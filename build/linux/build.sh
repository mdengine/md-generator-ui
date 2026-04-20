#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

if ! command -v pyinstaller >/dev/null 2>&1; then
  python3 -m pip install -r requirements-dev.txt
fi

pyinstaller --noconfirm md-generator-ui.spec
echo "Done. Output: $ROOT/dist/md-generator-ui"
