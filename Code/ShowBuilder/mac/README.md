# ShowBuilder.app — native Mac wrapper

A real macOS `.app` around the local ShowBuilder web app. Double-click it and you
get the wizard in its own Cocoa window with a Dock icon — no terminal, no browser
tab. It starts the existing `run.sh` server in the background, waits for it, shows
the page in a `WKWebView`, and stops the server when you quit.

It is **only a window**. It does not touch the build pipeline — same engines, same
verified `.ses`/paperwork output as `./run.sh` + browser.

## Build

```bash
cd ~/Documents/Claude/Code/ShowBuilder/mac
./build_app.sh          # compiles main.swift, draws the icon, assembles the bundle
```

Output: `mac/ShowBuilder.app`. Drag it to `/Applications` or the Dock, or just
double-click. First launch may need a right-click → Open (ad-hoc signed, no
Developer ID).

## How it behaves

- If nothing is serving port 8095, it spawns `run.sh` (forced to `127.0.0.1`).
- If a server is already up (e.g. you ran `./run.sh` in a terminal), it attaches to
  that one and leaves it running on quit.
- App menu has **Open Server Log** (`~/.../T/showbuilder-server.log`) and **Open
  Shows Folder**; View → **Reload** (⌘R). The file picker for "load a package" works.

## Files

| File | Role |
|---|---|
| `main.swift` | the app — server lifecycle + WKWebView window |
| `Info.plist` | bundle metadata (id `com.tinydoor.showbuilder`, loopback ATS) |
| `make_icon.swift` / `make_icon.sh` | renders `AppIcon.icns` (EQ curve on DiGiCo navy) |
| `build_app.sh` | one-shot build |

## Notes

- The repo path is hardcoded in `main.swift` (`kRepoPath`). If ShowBuilder ever
  moves, update that constant and rebuild.
- macOS / Swift toolchain required (`swiftc`, ships with the Command Line Tools).
