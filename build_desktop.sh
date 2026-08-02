#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_CACHE_DIR="$ROOT_DIR/.build-cache"

cd "$ROOT_DIR"
command rm -rf -- build dist
mkdir -p "$BUILD_CACHE_DIR/pyinstaller" "$BUILD_CACHE_DIR/matplotlib" "$BUILD_CACHE_DIR/fontconfig"
export PYINSTALLER_CONFIG_DIR="$BUILD_CACHE_DIR/pyinstaller"
export MPLCONFIGDIR="$BUILD_CACHE_DIR/matplotlib"
export XDG_CACHE_HOME="$BUILD_CACHE_DIR"
export FONTCONFIG_PATH="${FONTCONFIG_PATH:-}"
python3 -m PyInstaller --noconfirm ZaraStockChecker.spec
echo "Desktop app built at: $ROOT_DIR/dist/ZaraStockChecker.app"
