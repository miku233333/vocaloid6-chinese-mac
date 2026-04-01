#!/bin/bash
#
# VOCALOID6 Mac 繁體中文安裝入口
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🎵 VOCALOID6 Mac 繁體中文安裝入口"
echo "===================================="
echo "這會呼叫 Python 安裝器，並以 zh-TW 為預設語言。"
echo

if [[ "${OSTYPE}" != darwin* ]]; then
  echo "❌ 錯誤：此腳本僅適用於 macOS"
  exit 1
fi

python3 "${SCRIPT_DIR}/scripts/installer.py" --lang zh-TW
