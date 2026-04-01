#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VOCALOID6 Mac 資源提取工具
用途：從本機 VOCALOID6.app 提取資源文件，供繁體中文漢化研究使用
"""

import os
import argparse
import json
import shutil
from pathlib import Path
from typing import Optional

APP_CANDIDATES = [
    Path("/Applications/VOCALOID6.app"),
    Path.home() / "Applications/VOCALOID6.app",
    Path("/Applications/VOCALOID 6.app"),
    Path.home() / "Applications/VOCALOID 6.app",
    Path("/Applications/VOCALOID6 Editor.app"),
    Path.home() / "Applications/VOCALOID6 Editor.app",
]

# 需要提取的文件類型
RESOURCE_PATTERNS = [
    '*.json',
    '*.xml',
    '*.strings',
    '*.plist',
    '*.res',
    '*.dylib'
]


class VocaloidResourceExtractor:
    """VOCALOID6 Mac 資源提取器"""

    def __init__(self, app_path: Optional[str] = None, output_dir: str = "extracted_resources"):
        self.app_path = Path(app_path).expanduser() if app_path else None
        self.output_dir = Path(output_dir)

    def find_vocaloid_installation(self) -> Path:
        """查找 VOCALOID6.app 安裝路徑"""
        print("🔍 在 macOS 上查找 VOCALOID6...")

        if self.app_path:
            if self.app_path.exists():
                print(f"✅ 使用指定路徑: {self.app_path}")
                return self.app_path
            raise FileNotFoundError(f"指定的 app 路徑不存在：{self.app_path}")

        for path in APP_CANDIDATES:
            if path.exists() and (path / "Contents/Resources").exists():
                print(f"✅ 找到 VOCALOID6: {path}")
                return path

        raise FileNotFoundError(
            "未找到 VOCALOID6.app。請用 --app-path 指定，例如："
            " --app-path /Applications/VOCALOID6.app"
        )

    def extract_resources(self, app_bundle: Path, output: Optional[Path] = None):
        """提取資源文件"""
        if output is None:
            output = self.output_dir

        output.mkdir(parents=True, exist_ok=True)
        source = app_bundle / "Contents" / "Resources"

        if not source.exists():
            raise FileNotFoundError(f"找不到 Resources 目錄：{source}")

        print(f"\n📦 開始提取資源...")
        print(f"   App：{app_bundle}")
        print(f"   資源來源：{source}")
        print(f"   目標：{output}")

        extracted_count = 0

        # 遍歷資源目錄
        for root, dirs, files in os.walk(source):
            # 跳過無關目錄
            if any(skip in root for skip in ['.git', '__pycache__', 'node_modules']):
                continue
            
            for file in files:
                file_path = Path(root) / file
                
                # 檢查是否需要提取
                if self._should_extract(file_path):
                    # 計算相對路徑
                    try:
                        rel_path = file_path.relative_to(source)
                    except ValueError:
                        rel_path = file_path.name
                    
                    # 創建目標目錄
                    dest = output / rel_path
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    
                    # 複製文件
                    try:
                        shutil.copy2(file_path, dest)
                        extracted_count += 1
                        print(f"   ✅ {rel_path}")
                    except Exception as e:
                        print(f"   ⚠️ {rel_path}: {e}")
        
        print(f"\n✅ 提取完成！共 {extracted_count} 個文件")
        return extracted_count
    
    def _should_extract(self, file_path: Path) -> bool:
        """檢查文件是否需要提取"""
        # 跳過大文件 (>50MB)
        try:
            if file_path.stat().st_size > 50 * 1024 * 1024:
                return False
        except:
            pass
        
        # 檢查擴展名
        for pattern in RESOURCE_PATTERNS:
            if file_path.match(pattern):
                return True
        
        # 檢查是否為語言資源文件
        name = file_path.name.lower()
        if any(keyword in name for keyword in ['lang', 'locale', 'i18n', 'translation']):
            return True
        
        return False
    
    def generate_report(self, app_bundle: Path, output: Path):
        """生成提取報告"""
        report = {
            'platform': 'macOS',
            'app_bundle': str(app_bundle),
            'file_count': sum(1 for _ in output.rglob('*') if _.is_file()),
            'total_size_mb': sum(f.stat().st_size for f in output.rglob('*') if f.is_file()) / 1024 / 1024
        }
        
        report_file = output / 'extraction_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 提取報告已保存到：{report_file}")
        return report


def main():
    """主函數"""
    print("=" * 60)
    print("  VOCALOID6 資源提取工具 v1.0")
    print("  ⚠️ 僅供個人學習使用，請支持正版")
    print("=" * 60)
    print()
    
    parser = argparse.ArgumentParser(description='VOCALOID6 Mac 資源提取工具')
    parser.add_argument('--app-path', help='VOCALOID6.app 路徑')
    parser.add_argument('-o', '--output', default='extracted_resources', help='輸出目錄')
    args = parser.parse_args()

    extractor = VocaloidResourceExtractor(app_path=args.app_path, output_dir=args.output)
    
    try:
        # 1. 查找安裝
        app_bundle = extractor.find_vocaloid_installation()
        
        # 2. 提取資源
        extractor.extract_resources(app_bundle)
        
        # 3. 生成報告
        extractor.generate_report(app_bundle, extractor.output_dir)
        
        # 4. 下一步說明
        print("\n" + "=" * 60)
        print("  下一步：")
        print("  1. 檢查 extracted_resources/ 目錄")
        print("  2. 編輯翻譯文件 (data/translations/zh-TW.json)")
        print("  3. 運行安裝器 (install.sh)")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用戶中斷")
    except Exception as e:
        print(f"\n❌ 錯誤：{e}")
        print("\n請確保:")
        print("  1. VOCALOID6.app 已正確安裝")
        print("  2. 有權限訪問安裝目錄")
        print("  3. 關閉 VOCALOID6")


if __name__ == "__main__":
    main()
