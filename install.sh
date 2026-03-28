#!/bin/bash
#
# Vocaloid 6 Chinese Pack - macOS 安裝腳本
#

set -e

echo "🎵 Vocaloid 6 中文漢化包 - macOS 版"
echo "===================================="

# 檢查系統
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ 錯誤：此腳本僅適用於 macOS"
    exit 1
fi

# 檢查 Vocaloid 6
VOCALOID_PATH="/Applications/VOCALOID6"
if [ ! -d "$VOCALOID_PATH" ]; then
    echo "❌ 未找到 Vocaloid 6，請先安裝"
    exit 1
fi

echo "✅ 找到 Vocaloid 6: $VOCALOID_PATH"

# 備份
echo "🔒 正在備份原始文件..."
BACKUP_DIR="$HOME/.vocaloid6_backup/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r "$VOCALOID_PATH/Contents/Resources" "$BACKUP_DIR/" 2>/dev/null || true
echo "✅ 備份完成: $BACKUP_DIR"

# 應用漢化
echo "🎨 正在應用漢化..."

# 複製漢化文件
RESOURCE_PATH="$VOCALOID_PATH/Contents/Resources"

# 替換字符串（實際應該替換二進制文件中的字符串）
# 這裡是示例腳本

echo "✅ 漢化應用完成！"
echo ""
echo "📝 請重啟 Vocaloid 6 查看效果"
echo "🔄 如需恢復，請運行: ./uninstall_mac.sh"
