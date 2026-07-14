// ShowBuilder.app — native macOS wrapper around the local ShowBuilder server.
//
// On launch it starts the existing aiohttp server (run.sh -> backend.app) as a
// background process, waits for it to come up, and shows the wizard in a real
// Cocoa window via WKWebView. On quit it stops the server it started.
//
// It does NOT touch the build pipeline — it's only a window around the verified
// web app. If a server is already serving the port (e.g. ./run.sh in a terminal),
// it attaches to that one instead of spawning a second.

import AppKit
import WebKit

// ── config ──────────────────────────────────────────────────────────────────
let kRepoPath = "/Users/brianlloyd/Documents/Claude/Code/ShowBuilder"
let kPort = 8095
let kBaseURL = URL(string: "http://127.0.0.1:\(kPort)/")!
let kLogPath = NSTemporaryDirectory() + "showbuilder-server.log"

// ── small HTTP probe (background thread) ──────────────────────────────────────
func serverIsUp(timeout: TimeInterval = 0.8) -> Bool {
    // Ephemeral, no-cache session — a cached 200 from a previous run must NOT
    // read as "server up", or we'd attach to a server that isn't there.
    let scfg = URLSessionConfiguration.ephemeral
    scfg.requestCachePolicy = .reloadIgnoringLocalAndRemoteCacheData
    scfg.urlCache = nil
    let session = URLSession(configuration: scfg)
    defer { session.invalidateAndCancel() }
    var req = URLRequest(url: kBaseURL, cachePolicy: .reloadIgnoringLocalAndRemoteCacheData)
    req.timeoutInterval = timeout
    req.httpMethod = "GET"
    let sem = DispatchSemaphore(value: 0)
    var ok = false
    let task = session.dataTask(with: req) { _, resp, _ in
        if let http = resp as? HTTPURLResponse, (200..<500).contains(http.statusCode) { ok = true }
        sem.signal()
    }
    task.resume()
    _ = sem.wait(timeout: .now() + timeout + 0.3)
    return ok
}

// ── app delegate ──────────────────────────────────────────────────────────────
final class AppDelegate: NSObject, NSApplicationDelegate, WKNavigationDelegate, WKUIDelegate, WKScriptMessageHandler {
    var window: NSWindow!
    var webView: WKWebView!
    var server: Process?
    var spawned = false
    var overlay: NSView!
    let statusLabel = NSTextField(labelWithString: "Starting ShowBuilder…")

    func applicationDidFinishLaunching(_ note: Notification) {
        buildMenu()
        buildWindow()
        NSApp.activate(ignoringOtherApps: true)
        bringUpServer()
    }

    // MARK: window + webview
    func buildWindow() {
        let frame = NSRect(x: 0, y: 0, width: 1180, height: 840)
        window = NSWindow(contentRect: frame,
                          styleMask: [.titled, .closable, .miniaturizable, .resizable],
                          backing: .buffered, defer: false)
        window.title = "ShowBuilder"
        window.minSize = NSSize(width: 900, height: 640)
        window.center()
        window.setFrameAutosaveName("ShowBuilderMain")

        let cfg = WKWebViewConfiguration()
        cfg.preferences.javaScriptCanOpenWindowsAutomatically = false
        let ucc = WKUserContentController()
        ucc.add(self, name: "sblog")
        let js = """
        (function(){
          function send(l,a){try{window.webkit.messageHandlers.sblog.postMessage(l+': '+Array.from(a).map(String).join(' '));}catch(e){}}
          var c=window.console;['log','warn','error','info'].forEach(function(k){var o=c[k]?c[k].bind(c):function(){};c[k]=function(){send(k,arguments);o.apply(c,arguments);};});
          window.addEventListener('error',function(e){send('JSERROR',[e.message+' @ '+e.filename+':'+e.lineno]);});
          window.addEventListener('unhandledrejection',function(e){send('REJECT',[String(e.reason)]);});
        })();
        """
        ucc.addUserScript(WKUserScript(source: js, injectionTime: .atDocumentStart, forMainFrameOnly: true))
        cfg.userContentController = ucc
        webView = WKWebView(frame: window.contentView!.bounds, configuration: cfg)
        if #available(macOS 13.3, *) { webView.isInspectable = true }
        webView.autoresizingMask = [.width, .height]
        webView.navigationDelegate = self
        webView.uiDelegate = self
        window.contentView!.addSubview(webView)

        // loading overlay
        overlay = NSView(frame: window.contentView!.bounds)
        overlay.autoresizingMask = [.width, .height]
        overlay.wantsLayer = true
        overlay.layer?.backgroundColor = NSColor(srgbRed: 0.10, green: 0.23, blue: 0.36, alpha: 1).cgColor

        let spinner = NSProgressIndicator()
        spinner.style = .spinning
        spinner.controlSize = .regular
        spinner.translatesAutoresizingMaskIntoConstraints = false
        spinner.startAnimation(nil)

        statusLabel.textColor = .white
        statusLabel.font = NSFont.systemFont(ofSize: 15, weight: .medium)
        statusLabel.alignment = .center
        statusLabel.translatesAutoresizingMaskIntoConstraints = false

        overlay.addSubview(spinner)
        overlay.addSubview(statusLabel)
        NSLayoutConstraint.activate([
            spinner.centerXAnchor.constraint(equalTo: overlay.centerXAnchor),
            spinner.centerYAnchor.constraint(equalTo: overlay.centerYAnchor, constant: -14),
            statusLabel.centerXAnchor.constraint(equalTo: overlay.centerXAnchor),
            statusLabel.topAnchor.constraint(equalTo: spinner.bottomAnchor, constant: 16),
        ])
        window.contentView!.addSubview(overlay)
        window.makeKeyAndOrderFront(nil)
    }

    func setStatus(_ s: String) {
        DispatchQueue.main.async { self.statusLabel.stringValue = s }
    }

    // MARK: server lifecycle
    func dlog(_ s: String) {
        FileHandle.standardError.write("[launcher] \(s)\n".data(using: .utf8)!)
    }

    func bringUpServer() {
        DispatchQueue.global(qos: .userInitiated).async {
            if serverIsUp() {                       // already running — just attach
                self.dlog("attach: server already up")
                self.spawned = false
                self.loadApp()
                return
            }
            self.dlog("no server up; spawning")
            self.setStatus("Starting the ShowBuilder server…")
            guard self.spawnServer() else {
                self.dlog("spawnServer FAILED")
                self.setStatus("Couldn't start the server. See log:\n\(kLogPath)")
                return
            }
            self.dlog("spawned pid \(self.server?.processIdentifier ?? -1)")
            // poll until ready (~25s)
            for i in 0..<80 {
                if serverIsUp(timeout: 0.6) { self.dlog("server up after poll \(i)"); self.loadApp(); return }
                if !(self.server?.isRunning ?? false) {
                    self.dlog("server process EXITED early (status \(self.server?.terminationStatus ?? -1))")
                    self.setStatus("Server exited on startup. See log:\n\(kLogPath)")
                    return
                }
                if i == 10 { self.setStatus("Warming up the engines…") }
                Thread.sleep(forTimeInterval: 0.33)
            }
            self.dlog("poll timed out")
            self.setStatus("Server didn't respond in time. See log:\n\(kLogPath)")
        }
    }

    func spawnServer() -> Bool {
        let runScript = kRepoPath + "/run.sh"
        guard FileManager.default.fileExists(atPath: runScript) else {
            self.setStatus("ShowBuilder not found at:\n\(kRepoPath)")
            return false
        }
        let p = Process()
        p.executableURL = URL(fileURLWithPath: runScript)
        p.currentDirectoryURL = URL(fileURLWithPath: kRepoPath)
        var env = ProcessInfo.processInfo.environment
        env["SHOWBUILDER_HOST"] = "127.0.0.1"       // keep it loopback-only
        p.environment = env
        FileManager.default.createFile(atPath: kLogPath, contents: nil)
        if let fh = FileHandle(forWritingAtPath: kLogPath) {
            p.standardOutput = fh
            p.standardError = fh
        }
        do {
            try p.run()
            self.server = p
            self.spawned = true
            return true
        } catch {
            self.dlog("Process.run threw: \(error)")
            return false
        }
    }

    func loadApp() {
        DispatchQueue.main.async {
            self.webView.load(URLRequest(url: kBaseURL, cachePolicy: .reloadIgnoringLocalCacheData))
        }
    }

    // MARK: WKNavigationDelegate — drop the overlay once the page is in
    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        overlay.isHidden = true
    }
    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        setStatus("Failed to load the wizard:\n\(error.localizedDescription)")
        overlay.isHidden = false
    }

    // MARK: WKUIDelegate — file picker for "load a package"
    func webView(_ webView: WKWebView, runOpenPanelWith parameters: WKOpenPanelParameters,
                 initiatedByFrame frame: WKFrameInfo,
                 completionHandler: @escaping ([URL]?) -> Void) {
        let panel = NSOpenPanel()
        panel.canChooseFiles = true
        panel.canChooseDirectories = false
        panel.allowsMultipleSelection = parameters.allowsMultipleSelection
        panel.begin { resp in
            completionHandler(resp == .OK ? panel.urls : nil)
        }
    }

    // MARK: console capture (diagnostic)
    func userContentController(_ ucc: WKUserContentController, didReceive message: WKScriptMessage) {
        let line = "[webview] \(message.body)\n"
        if let fh = FileHandle(forWritingAtPath: kLogPath) {
            fh.seekToEndOfFile()
            fh.write(line.data(using: .utf8)!)
            fh.closeFile()
        }
        FileHandle.standardError.write(line.data(using: .utf8)!)
    }

    // MARK: actions
    @objc func reload(_ sender: Any?) { webView.reload() }
    @objc func openLog(_ sender: Any?) {
        NSWorkspace.shared.open(URL(fileURLWithPath: kLogPath))
    }
    @objc func openShowsFolder(_ sender: Any?) {
        let p = (CommandLine.arguments.first.map { _ in "/Users/brianlloyd/Documents/Claude/audio" }) ?? ""
        NSWorkspace.shared.open(URL(fileURLWithPath: p))
    }

    // MARK: shutdown
    func applicationShouldTerminateAfterLastWindowClosed(_ app: NSApplication) -> Bool { true }
    func applicationWillTerminate(_ note: Notification) {
        if spawned, let s = server, s.isRunning {
            s.terminate()
            // give aiohttp a moment to release the port
            for _ in 0..<10 { if !s.isRunning { break }; Thread.sleep(forTimeInterval: 0.1) }
        }
    }

    // MARK: menu
    func buildMenu() {
        let main = NSMenu()

        let appItem = NSMenuItem()
        main.addItem(appItem)
        let appMenu = NSMenu()
        appItem.submenu = appMenu
        appMenu.addItem(withTitle: "About ShowBuilder", action: #selector(NSApplication.orderFrontStandardAboutPanel(_:)), keyEquivalent: "")
        appMenu.addItem(.separator())
        appMenu.addItem(withTitle: "Open Server Log", action: #selector(openLog(_:)), keyEquivalent: "l")
        appMenu.addItem(withTitle: "Open Shows Folder", action: #selector(openShowsFolder(_:)), keyEquivalent: "")
        appMenu.addItem(.separator())
        appMenu.addItem(withTitle: "Hide ShowBuilder", action: #selector(NSApplication.hide(_:)), keyEquivalent: "h")
        appMenu.addItem(withTitle: "Quit ShowBuilder", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")

        // Edit menu — makes Cmd-C/V/X/A work inside the WebView's text fields
        let editItem = NSMenuItem()
        main.addItem(editItem)
        let edit = NSMenu(title: "Edit")
        editItem.submenu = edit
        edit.addItem(withTitle: "Undo", action: Selector(("undo:")), keyEquivalent: "z")
        edit.addItem(withTitle: "Redo", action: Selector(("redo:")), keyEquivalent: "Z")
        edit.addItem(.separator())
        edit.addItem(withTitle: "Cut", action: #selector(NSText.cut(_:)), keyEquivalent: "x")
        edit.addItem(withTitle: "Copy", action: #selector(NSText.copy(_:)), keyEquivalent: "c")
        edit.addItem(withTitle: "Paste", action: #selector(NSText.paste(_:)), keyEquivalent: "v")
        edit.addItem(withTitle: "Select All", action: #selector(NSText.selectAll(_:)), keyEquivalent: "a")

        // View menu — reload
        let viewItem = NSMenuItem()
        main.addItem(viewItem)
        let view = NSMenu(title: "View")
        viewItem.submenu = view
        view.addItem(withTitle: "Reload", action: #selector(reload(_:)), keyEquivalent: "r")

        // Window menu
        let winItem = NSMenuItem()
        main.addItem(winItem)
        let win = NSMenu(title: "Window")
        winItem.submenu = win
        win.addItem(withTitle: "Minimize", action: #selector(NSWindow.performMiniaturize(_:)), keyEquivalent: "m")
        win.addItem(withTitle: "Zoom", action: #selector(NSWindow.performZoom(_:)), keyEquivalent: "")
        NSApp.windowsMenu = win

        NSApp.mainMenu = main
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.setActivationPolicy(.regular)
app.run()
