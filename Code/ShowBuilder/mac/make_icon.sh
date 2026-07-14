#!/usr/bin/env bash
# Render AppIcon.icns from make_icon.swift.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ICONSET="$HERE/AppIcon.iconset"
rm -rf "$ICONSET"
mkdir -p "$ICONSET"
swift "$HERE/make_icon.swift" "$ICONSET"
iconutil -c icns "$ICONSET" -o "$HERE/AppIcon.icns"
rm -rf "$ICONSET"
echo "Built $HERE/AppIcon.icns"
