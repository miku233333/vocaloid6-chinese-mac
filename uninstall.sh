#!/bin/bash
#
# Vocaloid 6 Chinese Pack - macOS 卸載腳本
#

echo "🔄 正在恢復原始文件..."

# 找到最新備份
BACKUP_DIR=$(ls -td ~/.vocaloid6_backup/*/ 2>/dev/null | head -1)

if [ -z "$BACKUP_DIR" ]; then
    echo "❌ 找不到備份文件"
    exit 1
fi

echo "📁 使用備份: $BACKUP_DIR"

# 恢復文件
VOCALOID_PATH="/Applications/VOCALOID6"
cp -r "$BACKUP_DIR/Resources" "$VOCALOID_PATH/Contents/" 2>/dev/null || true

echo "✅ 恢復完成！"
echo "📝 請重啟 Vocaloid 6"
