#!/usr/bin/env bash
# Build GudoSnake.app for macOS (double-click to run).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This script must run on macOS."
  echo "PyInstaller cannot cross-compile a Mac .app from Windows or Linux."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required."
  exit 1
fi

VENV="$ROOT/.venv-mac"
if [[ ! -d "$VENV" ]]; then
  python3 -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"

python -m pip install --upgrade pip
python -m pip install pyinstaller pygame-ce pyyaml

ICON_PNG="$ROOT/assets/icon.png"
ICON_ICNS="$ROOT/assets/icon.icns"
if [[ -f "$ICON_PNG" && ! -f "$ICON_ICNS" ]]; then
  echo "Generating assets/icon.icns from assets/icon.png ..."
  ICONSET="$ROOT/assets/icon.iconset"
  rm -rf "$ICONSET"
  mkdir -p "$ICONSET"
  sips -z 16 16 "$ICON_PNG" --out "$ICONSET/icon_16x16.png" >/dev/null
  sips -z 32 32 "$ICON_PNG" --out "$ICONSET/icon_16x16@2x.png" >/dev/null
  sips -z 32 32 "$ICON_PNG" --out "$ICONSET/icon_32x32.png" >/dev/null
  sips -z 64 64 "$ICON_PNG" --out "$ICONSET/icon_32x32@2x.png" >/dev/null
  sips -z 128 128 "$ICON_PNG" --out "$ICONSET/icon_128x128.png" >/dev/null
  sips -z 256 256 "$ICON_PNG" --out "$ICONSET/icon_128x128@2x.png" >/dev/null
  sips -z 256 256 "$ICON_PNG" --out "$ICONSET/icon_256x256.png" >/dev/null
  sips -z 512 512 "$ICON_PNG" --out "$ICONSET/icon_256x256@2x.png" >/dev/null
  sips -z 512 512 "$ICON_PNG" --out "$ICONSET/icon_512x512.png" >/dev/null
  cp "$ICONSET/icon_512x512.png" "$ICONSET/icon_512x512@2x.png"
  iconutil -c icns "$ICONSET" -o "$ICON_ICNS"
  rm -rf "$ICONSET"
fi

pyinstaller --noconfirm --clean GudoSnake-mac.spec

ZIP="$ROOT/dist/GudoSnake-mac.zip"
if [[ -d "$ROOT/dist/GudoSnake.app" ]]; then
  rm -f "$ZIP"
  ditto -c -k --sequesterRsrc --keepParent "$ROOT/dist/GudoSnake.app" "$ZIP"
fi

echo ""
echo "Build complete:"
echo "  App: $ROOT/dist/GudoSnake.app"
if [[ -f "$ZIP" ]]; then
  echo "  Zip: $ZIP"
fi
echo ""
echo "Run: open dist/GudoSnake.app"
echo "If macOS blocks the app, right-click -> Open once, or run:"
echo "  xattr -cr dist/GudoSnake.app"
