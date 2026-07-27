// Patchbay.app — native macOS wrapper around the local Patchbay server.
//
// Launch it and you get the patch sheets in a real Cocoa window: it spawns the
// aiohttp server (run.sh -> backend.app) in the background, waits for it, shows
// the page in a WKWebView, and stops the server it started when you quit. If a
// server is already serving the port (./run.sh in a terminal), it attaches to
// that one and leaves it running.
//
// Exports are handed to the system rather than the web view: the PDF opens in
// the default browser (where Cmd-P → Save as PDF works), xlsx/JSON download to
// ~/Downloads and get revealed in Finder.

import AppKit
import WebKit

// ── config ──────────────────────────────────────────────────────────────────
let kRepoPath = "/Users/brianlloyd/Documents/Claude/Code/Patchbay"
let kPort = 8096
let kBaseURL = URL(string: "http://127.0.0.1:\(kPort)/")!
let kLogPath = NSTemporaryDirectory() + "patchbay-server.log"

// ── small HTTP probe (background thread) ────────────────────────────────────
func serverIsUp(timeout: TimeInterval = 0.8) -> Bool {
    let scfg = URLSessionConfiguration.ephemeral
    scfg.requestCachePolicy = .reloadIgnoringLocalAndRemoteCacheData
    scfg.urlCache = nil
    let session = URLSession(configuration: scfg)
    defer { session.invalidateAndCancel() }
    var req = URLRequest(url: kBaseURL.appendingPathComponent("health"),
                         cachePolicy: .reloadIgnoringLocalAndRemoteCacheData)
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

// ── app delegate ────────────────────────────────────────────────────────────
final class AppDelegate: NSObject, NSApplicationDelegate, WKNavigationDelegate, WKUIDelegate,
                         WKScriptMessageHandler, WKDownloadDelegate {
    var window: NSWindow!
    var webView: WKWebView!
    var server: Process?
    var spawned = false
    var overlay: NSView!
    let statusLabel = NSTextField(labelWithString: "Starting Patchbay…")
    var downloadDestinations: [ObjectIdentifier: URL] = [:]

    func applicationDidFinishLaunching(_ note: Notification) {
        buildMenu()
        buildWindow()
        NSApp.activate(ignoringOtherApps: true)
        bringUpServer()
    }

    // MARK: window + webview
    func buildWindow() {
        let frame = NSRect(x: 0, y: 0, width: 1320, height: 880)
        window = NSWindow(contentRect: frame,
                          styleMask: [.titled, .closable, .miniaturizable, .resizable],
                          backing: .buffered, defer: false)
        window.title = "Patchbay"
        window.minSize = NSSize(width: 980, height: 620)
        window.center()
        window.setFrameAutosaveName("PatchbayMain")
        window.appearance = NSAppearance(named: .darkAqua)   // matches the app's dark theme
        window.backgroundColor = NSColor(srgbRed: 0.07, green: 0.08, blue: 0.10, alpha: 1)

        let cfg = WKWebViewConfiguration()
        cfg.preferences.javaScriptCanOpenWindowsAutomatically = false
        let ucc = WKUserContentController()
        ucc.add(self, name: "pblog")
        let js = """
        (function(){
          function send(l,a){try{window.webkit.messageHandlers.pblog.postMessage(l+': '+Array.from(a).map(String).join(' '));}catch(e){}}
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
        webView.setValue(false, forKey: "drawsBackground")
        window.contentView!.addSubview(webView)

        // loading overlay
        overlay = NSView(frame: window.contentView!.bounds)
        overlay.autoresizingMask = [.width, .height]
        overlay.wantsLayer = true
        overlay.layer?.backgroundColor = NSColor(srgbRed: 0.07, green: 0.08, blue: 0.10, alpha: 1).cgColor

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
            self.setStatus("Starting the Patchbay server…")
            guard self.spawnServer() else {
                self.dlog("spawnServer FAILED")
                self.setStatus("Couldn't start the server. See log:\n\(kLogPath)")
                return
            }
            for i in 0..<80 {
                if serverIsUp(timeout: 0.6) { self.dlog("server up after poll \(i)"); self.loadApp(); return }
                if !(self.server?.isRunning ?? false) {
                    self.dlog("server process EXITED early (status \(self.server?.terminationStatus ?? -1))")
                    self.setStatus("Server exited on startup. See log:\n\(kLogPath)")
                    return
                }
                Thread.sleep(forTimeInterval: 0.33)
            }
            self.setStatus("Server didn't respond in time. See log:\n\(kLogPath)")
        }
    }

    func spawnServer() -> Bool {
        let runScript = kRepoPath + "/run.sh"
        guard FileManager.default.fileExists(atPath: runScript) else {
            self.setStatus("Patchbay not found at:\n\(kRepoPath)")
            return false
        }
        let p = Process()
        p.executableURL = URL(fileURLWithPath: runScript)
        p.currentDirectoryURL = URL(fileURLWithPath: kRepoPath)
        var env = ProcessInfo.processInfo.environment
        env["PATCHBAY_HOST"] = "127.0.0.1"          // keep it loopback-only
        env["PATCHBAY_PORT"] = String(kPort)
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

    // MARK: exports — hand them to the system, not the web view
    func isExport(_ url: URL?) -> Bool {
        guard let p = url?.path else { return false }
        return p.contains("/export.")
    }

    func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction,
                 decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        guard let url = navigationAction.request.url else { return decisionHandler(.allow) }
        if isExport(url) {
            // .html goes to the browser so Cmd-P → Save as PDF works;
            // xlsx/json download to ~/Downloads.
            if url.path.hasSuffix("export.html") || url.path.hasSuffix("export.pdf") {
                NSWorkspace.shared.open(url)
                return decisionHandler(.cancel)
            }
            if #available(macOS 11.3, *) { return decisionHandler(.download) }
            NSWorkspace.shared.open(url)
            return decisionHandler(.cancel)
        }
        if navigationAction.navigationType == .linkActivated,
           let host = url.host, host != "127.0.0.1", host != "localhost" {
            NSWorkspace.shared.open(url)              // real links open outside
            return decisionHandler(.cancel)
        }
        decisionHandler(.allow)
    }

    // window.open (the PDF path) → default browser
    func webView(_ webView: WKWebView, createWebViewWith cfg: WKWebViewConfiguration,
                 for navigationAction: WKNavigationAction,
                 windowFeatures: WKWindowFeatures) -> WKWebView? {
        if let url = navigationAction.request.url { NSWorkspace.shared.open(url) }
        return nil
    }

    @available(macOS 11.3, *)
    func webView(_ webView: WKWebView, navigationAction: WKNavigationAction,
                 didBecome download: WKDownload) {
        download.delegate = self
    }

    @available(macOS 11.3, *)
    func download(_ download: WKDownload, decideDestinationUsing response: URLResponse,
                  suggestedFilename: String, completionHandler: @escaping (URL?) -> Void) {
        let dir = FileManager.default.urls(for: .downloadsDirectory, in: .userDomainMask).first
            ?? URL(fileURLWithPath: NSHomeDirectory() + "/Downloads")
        var dest = dir.appendingPathComponent(suggestedFilename)
        var n = 2
        while FileManager.default.fileExists(atPath: dest.path) {
            let base = (suggestedFilename as NSString).deletingPathExtension
            let ext = (suggestedFilename as NSString).pathExtension
            dest = dir.appendingPathComponent("\(base) \(n).\(ext)")
            n += 1
        }
        downloadDestinations[ObjectIdentifier(download)] = dest
        completionHandler(dest)
    }

    @available(macOS 11.3, *)
    func downloadDidFinish(_ download: WKDownload) {
        if let url = downloadDestinations.removeValue(forKey: ObjectIdentifier(download)) {
            NSWorkspace.shared.activateFileViewerSelecting([url])
        }
    }

    @available(macOS 11.3, *)
    func download(_ download: WKDownload, didFailWithError error: Error, resumeData: Data?) {
        downloadDestinations.removeValue(forKey: ObjectIdentifier(download))
        setStatus("Download failed: \(error.localizedDescription)")
    }

    // MARK: WKNavigationDelegate
    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        overlay.isHidden = true
    }
    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        setStatus("Failed to load Patchbay:\n\(error.localizedDescription)")
        overlay.isHidden = false
    }

    // MARK: WKUIDelegate — file picker for the two Import buttons
    func webView(_ webView: WKWebView, runOpenPanelWith parameters: WKOpenPanelParameters,
                 initiatedByFrame frame: WKFrameInfo,
                 completionHandler: @escaping ([URL]?) -> Void) {
        let panel = NSOpenPanel()
        panel.canChooseFiles = true
        panel.canChooseDirectories = false
        panel.allowsMultipleSelection = parameters.allowsMultipleSelection
        panel.begin { resp in completionHandler(resp == .OK ? panel.urls : nil) }
    }

    // JS confirm()/alert() need native panels inside a WKWebView
    func webView(_ webView: WKWebView, runJavaScriptAlertPanelWithMessage message: String,
                 initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping () -> Void) {
        let a = NSAlert(); a.messageText = "Patchbay"; a.informativeText = message
        a.addButton(withTitle: "OK"); a.beginSheetModal(for: window) { _ in completionHandler() }
    }
    func webView(_ webView: WKWebView, runJavaScriptConfirmPanelWithMessage message: String,
                 initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping (Bool) -> Void) {
        let a = NSAlert(); a.messageText = "Patchbay"; a.informativeText = message
        a.addButton(withTitle: "OK"); a.addButton(withTitle: "Cancel")
        a.beginSheetModal(for: window) { r in completionHandler(r == .alertFirstButtonReturn) }
    }
    func webView(_ webView: WKWebView, runJavaScriptTextInputPanelWithPrompt prompt: String,
                 defaultText: String?, initiatedByFrame frame: WKFrameInfo,
                 completionHandler: @escaping (String?) -> Void) {
        let a = NSAlert(); a.messageText = "Patchbay"; a.informativeText = prompt
        let field = NSTextField(frame: NSRect(x: 0, y: 0, width: 280, height: 24))
        field.stringValue = defaultText ?? ""
        a.accessoryView = field
        a.addButton(withTitle: "OK"); a.addButton(withTitle: "Cancel")
        a.beginSheetModal(for: window) { r in
            completionHandler(r == .alertFirstButtonReturn ? field.stringValue : nil)
        }
    }

    // MARK: console capture (diagnostic)
    func userContentController(_ ucc: WKUserContentController, didReceive message: WKScriptMessage) {
        let line = "[webview] \(message.body)\n"
        if let fh = FileHandle(forWritingAtPath: kLogPath) {
            fh.seekToEndOfFile(); fh.write(line.data(using: .utf8)!); fh.closeFile()
        }
    }

    // MARK: actions
    @objc func reload(_ sender: Any?) { webView.reload() }
    @objc func openLog(_ sender: Any?) { NSWorkspace.shared.open(URL(fileURLWithPath: kLogPath)) }
    @objc func openInBrowser(_ sender: Any?) { NSWorkspace.shared.open(kBaseURL) }
    @objc func openDataFolder(_ sender: Any?) {
        NSWorkspace.shared.open(URL(fileURLWithPath: kRepoPath + "/data/sheets"))
    }

    // MARK: shutdown
    func applicationShouldTerminateAfterLastWindowClosed(_ app: NSApplication) -> Bool { true }
    func applicationWillTerminate(_ note: Notification) {
        if spawned, let s = server, s.isRunning {
            s.terminate()
            for _ in 0..<10 { if !s.isRunning { break }; Thread.sleep(forTimeInterval: 0.1) }
        }
    }

    // MARK: menu
    func buildMenu() {
        let main = NSMenu()

        let appItem = NSMenuItem(); main.addItem(appItem)
        let appMenu = NSMenu(); appItem.submenu = appMenu
        appMenu.addItem(withTitle: "About Patchbay", action: #selector(NSApplication.orderFrontStandardAboutPanel(_:)), keyEquivalent: "")
        appMenu.addItem(.separator())
        appMenu.addItem(withTitle: "Open Sheets Folder", action: #selector(openDataFolder(_:)), keyEquivalent: "")
        appMenu.addItem(withTitle: "Open in Browser", action: #selector(openInBrowser(_:)), keyEquivalent: "b")
        appMenu.addItem(withTitle: "Open Server Log", action: #selector(openLog(_:)), keyEquivalent: "l")
        appMenu.addItem(.separator())
        appMenu.addItem(withTitle: "Hide Patchbay", action: #selector(NSApplication.hide(_:)), keyEquivalent: "h")
        appMenu.addItem(withTitle: "Quit Patchbay", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")

        let editItem = NSMenuItem(); main.addItem(editItem)
        let edit = NSMenu(title: "Edit"); editItem.submenu = edit
        edit.addItem(withTitle: "Undo", action: Selector(("undo:")), keyEquivalent: "z")
        edit.addItem(withTitle: "Redo", action: Selector(("redo:")), keyEquivalent: "Z")
        edit.addItem(.separator())
        edit.addItem(withTitle: "Cut", action: #selector(NSText.cut(_:)), keyEquivalent: "x")
        edit.addItem(withTitle: "Copy", action: #selector(NSText.copy(_:)), keyEquivalent: "c")
        edit.addItem(withTitle: "Paste", action: #selector(NSText.paste(_:)), keyEquivalent: "v")
        edit.addItem(withTitle: "Select All", action: #selector(NSText.selectAll(_:)), keyEquivalent: "a")

        let viewItem = NSMenuItem(); main.addItem(viewItem)
        let view = NSMenu(title: "View"); viewItem.submenu = view
        view.addItem(withTitle: "Reload", action: #selector(reload(_:)), keyEquivalent: "r")

        let winItem = NSMenuItem(); main.addItem(winItem)
        let win = NSMenu(title: "Window"); winItem.submenu = win
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
