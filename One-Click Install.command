#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3)}"

if [[ -z "${PYTHON_BIN}" ]]; then
  osascript -e 'display alert "找不到 Python 3" message "請先安裝 Python 3 再重試。"'
  exit 1
fi

cd "${SCRIPT_DIR}"
"${PYTHON_BIN}" "${SCRIPT_DIR}/scripts/one_click_install.py"

echo
read -r -p "按 Enter 結束..."
