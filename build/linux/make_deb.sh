#!/usr/bin/env bash
# Build a minimal .deb from the PyInstaller one-file binary (amd64).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
STAGE="$ROOT/build/linux/deb-stage"
BIN="$ROOT/dist/md-generator-ui"
if [[ ! -f "$BIN" ]]; then
  echo "Missing $BIN — run build/linux/build.sh first." >&2
  exit 1
fi

rm -rf "$STAGE"
mkdir -p "$STAGE/DEBIAN" "$STAGE/usr/bin"
cp "$ROOT/build/linux/deb/DEBIAN/control" "$STAGE/DEBIAN/control"
cp "$BIN" "$STAGE/usr/bin/md-generator-ui"
chmod 755 "$STAGE/usr/bin/md-generator-ui"

dpkg-deb --build "$STAGE" "$ROOT/dist/md-generator-ui_amd64.deb"
echo "Created $ROOT/dist/md-generator-ui_amd64.deb"
