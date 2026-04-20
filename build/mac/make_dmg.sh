#!/usr/bin/env bash
# Wrap the PyInstaller binary in a minimal .app bundle and create a DMG (macOS).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BIN="$ROOT/dist/md-generator-ui"
if [[ ! -f "$BIN" ]]; then
  echo "Missing $BIN — run build/mac/build.sh first." >&2
  exit 1
fi

APP="$ROOT/dist/md-generator-ui.app"
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp "$BIN" "$APP/Contents/MacOS/md-generator-ui"
chmod +x "$APP/Contents/MacOS/md-generator-ui"

cat >"$APP/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>
  <string>md-generator-ui</string>
  <key>CFBundleIdentifier</key>
  <string>com.mdgenerator.ui</string>
  <key>CFBundleName</key>
  <string>md-generator-ui</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleShortVersionString</key>
  <string>0.1.0</string>
</dict>
</plist>
PLIST

DMG="$ROOT/dist/md-generator-ui.dmg"
rm -f "$DMG"
if command -v create-dmg >/dev/null 2>&1; then
  create-dmg --volname "md-generator-ui" "$DMG" "$APP"
else
  hdiutil create -volname "md-generator-ui" -srcfolder "$APP" -ov -format UDZO "$DMG"
fi
echo "Created $DMG"
