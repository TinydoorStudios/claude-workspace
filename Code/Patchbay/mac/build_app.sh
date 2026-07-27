#!/usr/bin/env bash
# Build Patchbay.app — compiles main.swift and assembles the bundle.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
APP="$HERE/Patchbay.app"

if [ ! -f "$HERE/AppIcon.icns" ]; then
  "$HERE/make_icon.sh"
fi

rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp "$HERE/Info.plist" "$APP/Contents/Info.plist"
cp "$HERE/AppIcon.icns" "$APP/Contents/Resources/AppIcon.icns"

swiftc -O -o "$APP/Contents/MacOS/Patchbay" "$HERE/main.swift" \
  -framework AppKit -framework WebKit
chmod +x "$APP/Contents/MacOS/Patchbay"

codesign --force --deep --sign - "$APP" >/dev/null 2>&1 || \
  echo "  (codesign skipped — Gatekeeper may prompt on first launch)"

echo "✓ Built $APP"

# Install to /Applications so it's launchable from Spotlight / Launchpad.
if [ -w /Applications ]; then
  rm -rf /Applications/Patchbay.app
  ditto "$APP" /Applications/Patchbay.app
  echo "✓ Installed /Applications/Patchbay.app"
else
  echo "  (/Applications not writable — drag $APP there yourself)"
fi
