#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VOCALOID6 Mac 版資源替換工具
零侵入式動態本地化引擎
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import argparse
from datetime import datetime


class ResourceReplacer:
    """VOCALOID6 資源替換引擎 - 零侵入式"""
    
    def __init__(self, app_path: str, language: str = "zh-TW"):
        self.app_path = Path(app_path)
        self.language = language
        self.resources_path = self.app_path / "Contents" / "Resources"
        self.backup_path = Path.home() / ".vocaloid6-backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.translation_file = Path(__file__).parent.parent / "data" / "translations" / f"{language}.json"
        self.terminology_file = Path(__file__).parent.parent / "data" / "terminology" / "vocaloid_terms.yml"
        self.extracted_strings_file = Path(__file__).parent.parent / "output" / "extracted_strings.json"
        self.translations: Dict[str, str] = {}
        self.terminology: Dict = {}
        
    def load_translations(self):
        """載入翻譯文件"""
        if not self.translation_file.exists():
            raise FileNotFoundError(f"翻譯文件不存在：{self.translation_file}")
            
        with open(self.translation_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.translations = data.get('translations', {})
            
        print(f"✅ 載入 {len(self.translations)} 個翻譯條目 ({self.language})")
        
    def load_terminology(self):
        """載入術語庫"""
        try:
            import yaml
            if self.terminology_file.exists():
                with open(self.terminology_file, 'r', encoding='utf-8') as f:
                    self.terminology = yaml.safe_load(f)
                print(f"✅ 載入術語庫")
        except ImportError:
            print("⚠️ 未安裝 PyYAML，跳過術語庫載入")
            
    def create_backup(self):
        """創建備份"""
        print(f"💾 創建備份到：{self.backup_path}")
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        # 備份 Resources 目錄
        if self.resources_path.exists():
            backup_resources = self.backup_path / "Resources"
            shutil.copytree(self.resources_path, backup_resources, dirs_exist_ok=True)
            print(f"✅ 已備份 Resources 目錄")
            
        # 保存備份元數據
        metadata = {
            "backup_time": datetime.now().isoformat(),
            "app_path": str(self.app_path),
            "language": self.language,
            "version": "1.0"
        }
        
        with open(self.backup_path / "backup_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
            
    def read_strings_payload(self, file_path: Path) -> Tuple[str, Dict[str, str]]:
        raw = file_path.read_bytes()
        for encoding in ("utf-16", "utf-16-le", "utf-16-be", "utf-8", "utf-8-sig"):
            try:
                content = raw.decode(encoding)
                mapping = self.parse_strings_content(content)
                if mapping:
                    return encoding, mapping
            except Exception:
                continue
        content = raw.decode("utf-16-le", errors="ignore")
        return "utf-16", self.parse_strings_content(content)

    def parse_strings_content(self, content: str) -> Dict[str, str]:
        import re

        mapping: Dict[str, str] = {}
        pattern = r'"([^"]+)"\s*=\s*"((?:[^"\\]|\\.)*)";'
        matches = re.findall(pattern, content)
        for key, value in matches:
            mapping[key] = value.encode("utf-8").decode("unicode_escape") if "\\u" in value else value
        return mapping

    def replace_in_strings_file(self, file_path: Path):
        """替換 .strings 文件中的字符串"""
        try:
            encoding, parsed = self.read_strings_payload(file_path)
            replaced_count = 0

            for key in list(parsed.keys()):
                translation = self.translations.get(key)
                if translation and translation != parsed[key]:
                    parsed[key] = translation
                    replaced_count += 1

            if replaced_count > 0:
                with open(file_path, 'w', encoding=encoding if encoding.startswith("utf") else "utf-16") as f:
                    for key, value in parsed.items():
                        f.write(f'"{key}" = "{value}";\n')
                print(f"✅ 替換 {file_path.name}: {replaced_count} 個字符串")
                
        except Exception as e:
            print(f"⚠️ 處理 {file_path} 失敗：{e}")
            
    def replace_all_strings_files(self):
        """替換所有 .strings 文件"""
        if not self.resources_path.exists():
            print(f"❌ 資源路徑不存在：{self.resources_path}")
            return
            
        strings_files = list(self.resources_path.rglob("*.strings"))
        print(f"🔍 找到 {len(strings_files)} 個 .strings 文件")
        
        for file_path in strings_files:
            self.replace_in_strings_file(file_path)
            
    def load_extracted_strings(self) -> Dict[str, Dict[str, str]]:
        if not self.extracted_strings_file.exists():
            return {}

        with open(self.extracted_strings_file, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        return payload.get("extracted_strings", {})

    def build_translated_strings_files(self) -> Dict[str, Dict[str, str]]:
        translated_files: Dict[str, Dict[str, str]] = {}
        extracted_files = self.load_extracted_strings()

        for source_path, file_strings in extracted_files.items():
            target_name = Path(source_path).name
            translated_entries: Dict[str, str] = {}
            for key, source_value in file_strings.items():
                translated_value = self.translations.get(key)
                if translated_value and translated_value != source_value:
                    translated_entries[key] = translated_value
            if translated_entries:
                translated_files[target_name] = translated_entries

        return translated_files

    def generate_localization_bundle(self, output_path: str):
        """生成本地化資源包（不修改原文件）"""
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 創建語言特定的資源目錄
        lang_dir = output_dir / f"{self.language}.lproj"
        lang_dir.mkdir(parents=True, exist_ok=True)
        
        translated_files = self.build_translated_strings_files()

        for filename, entries in translated_files.items():
            destination = lang_dir / filename
            with open(destination, 'w', encoding='utf-16') as f:
                for key, value in entries.items():
                    f.write(f'"{key}" = "{value}";\n')

        if "Localizable.strings" not in translated_files:
            localizable_path = lang_dir / "Localizable.strings"
            with open(localizable_path, 'w', encoding='utf-16') as f:
                for key, value in self.translations.items():
                    f.write(f'"{key}" = "{value}";\n')

        print(f"✅ 生成本地化包：{output_path}")
        print(f"✅ 生成 {len(translated_files)} 個本地化 strings 文件")
        
        # 生成安裝說明
        readme_path = output_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"""# VOCALOID6 {self.language} 本地化包

## 安裝說明

### 方法 1: 自動安裝（推薦）
```bash
python3 installer.py --lang {self.language}
```

### 方法 2: 手動安裝
1. 備份原文件
2. 將 `{self.language}.lproj` 複製到 VOCALOID6.app/Contents/Resources/
3. 重啟 VOCALOID6

## 文件結構
```
{output_path}/
├── {self.language}.lproj/
│   └── Localizable.strings
└── README.md
```

## 還原
```bash
python3 installer.py --restore
```
""")
            
    def run(self, mode: str = "replace", output_path: str = None):
        """執行替換流程"""
        print(f"🚀 開始 VOCALOID6 資源替換")
        print(f"📁 應用路徑：{self.app_path}")
        print(f"🌍 目標語言：{self.language}")
        print(f"🔧 模式：{mode}")
        
        # 載入資源
        self.load_translations()
        self.load_terminology()
        
        if mode == "replace":
            # 直接替換模式（需要備份）
            self.create_backup()
            self.replace_all_strings_files()
            print(f"\n✅ 替換完成！備份位置：{self.backup_path}")
            
        elif mode == "bundle":
            # 生成資源包模式（不修改原文件）
            if not output_path:
                output_path = "./vocaloid6-localization"
            self.generate_localization_bundle(output_path)
            print(f"\n✅ 本地化包已生成：{output_path}")
            
        elif mode == "restore":
            # 還原模式
            self.restore_from_backup()
            
    def restore_from_backup(self):
        """從備份還原"""
        # 找到最新的備份
        backup_base = Path.home() / ".vocaloid6-backup"
        if not backup_base.exists():
            print("❌ 找不到備份目錄")
            return
            
        backups = sorted(backup_base.iterdir(), reverse=True)
        if not backups:
            print("❌ 找不到備份")
            return
            
        latest_backup = backups[0]
        backup_resources = latest_backup / "Resources"
        
        if not backup_resources.exists():
            print("❌ 備份中沒有 Resources 目錄")
            return
            
        print(f"🔄 從備份還原：{latest_backup}")
        
        # 刪除當前 Resources
        if self.resources_path.exists():
            shutil.rmtree(self.resources_path)
            
        # 複製備份
        shutil.copytree(backup_resources, self.resources_path)
        print(f"✅ 已還原到原始狀態")


def main():
    parser = argparse.ArgumentParser(description='VOCALOID6 Mac 版資源替換工具')
    parser.add_argument('app_path', help='VOCALOID6.app 路徑')
    parser.add_argument('-l', '--lang', default='zh-TW', help='目標語言 (default: zh-TW)')
    parser.add_argument('-m', '--mode', choices=['replace', 'bundle', 'restore'], 
                       default='bundle', help='操作模式')
    parser.add_argument('-o', '--output', help='輸出目錄（bundle 模式）')
    
    args = parser.parse_args()
    
    replacer = ResourceReplacer(args.app_path, args.lang)
    replacer.run(mode=args.mode, output_path=args.output)


if __name__ == '__main__':
    main()
