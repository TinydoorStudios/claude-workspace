#!/usr/bin/env bash
# Build ShowBuilder.app — compiles main.swift and assembles the bundle.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
APP="$HERE/ShowBuilder.app"

echo "› Building icon…"
if [ ! -f "$HERE/AppIcon.icns" ]; then
  "$HERE/make_icon.sh"
fi

echo "› Assembling bundle…"
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp "$HERE/Info.plist" "$APP/Contents/Info.plist"
cp "$HERE/AppIcon.icns" "$APP/Contents/Resources/AppIcon.icns"

echo "› Compiling…"
swiftc -O -o "$APP/Contents/MacOS/ShowBuilder" "$HERE/main.swift" \
  -framework AppKit -framework WebKit
chmod +x "$APP/Contents/MacOS/ShowBuilder"

echo "› Signing (ad-hoc)…"
codesign --force --deep --sign - "$APP" >/dev/null 2>&1 || \
  echo "  (codesign skipped — Gatekeeper may prompt on first launch)"

echo "✓ Built $APP"
echo "  Drag it to /Applications or the Dock, or just double-click it."
