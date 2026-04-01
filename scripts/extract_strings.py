#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VOCALOID6 Mac 版資源字符串提取工具
支援 .strings 與編譯後 .nib 候選文本分析
"""

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import argparse


class VocaloidStringExtractor:
    """VOCALOID6 Mac 版資源字符串提取器"""
    
    def __init__(self, app_path: str):
        self.app_path = Path(app_path)
        self.resources_path = self.app_path / "Contents" / "Resources"
        self.extracted_strings: Dict[str, Dict[str, str]] = {}
        self.ui_elements: List[Dict] = []
        self.translation_candidates: Dict[str, str] = {}

    def load_existing_translation_candidates(self):
        """載入現有詞條，供 CSV 對照參考"""
        translation_file = Path(__file__).parent.parent / "data" / "translations" / "zh-TW.json"
        if not translation_file.exists():
            return

        try:
            payload = json.loads(translation_file.read_text(encoding="utf-8"))
            self.translation_candidates = payload.get("translations", {})
        except Exception as e:
            print(f"⚠️ 讀取現有 zh-TW 詞條失敗：{e}")

    def parse_strings_with_plutil(self, file_path: Path) -> Dict[str, str]:
        """優先用 plutil 解析 macOS .strings 文件"""
        try:
            result = subprocess.run(
                ["plutil", "-convert", "json", "-o", "-", str(file_path)],
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            return {str(k): str(v) for k, v in payload.items()}
        except Exception:
            return {}

    def parse_strings_with_fallback_decode(self, file_path: Path) -> Dict[str, str]:
        """編碼回退策略"""
        raw = file_path.read_bytes()
        attempts = ["utf-16", "utf-16-le", "utf-16-be", "utf-8", "utf-8-sig"]

        for encoding in attempts:
            try:
                content = raw.decode(encoding)
                return self.parse_strings_content(content)
            except Exception:
                continue

        try:
            content = raw.decode("utf-16-le", errors="ignore")
            return self.parse_strings_content(content)
        except Exception:
            return {}

    def parse_strings_content(self, content: str) -> Dict[str, str]:
        strings = {}
        pattern = r'"([^"]+)"\s*=\s*"((?:[^"\\]|\\.)*)";'
        matches = re.findall(pattern, content)
        for key, value in matches:
            strings[key] = value.encode("utf-8").decode("unicode_escape") if "\\u" in value else value
        return strings
        
    def extract_from_strings_file(self, file_path: Path) -> Dict[str, str]:
        """從 .strings 文件提取字符串"""
        try:
            strings = self.parse_strings_with_plutil(file_path)
            if not strings:
                strings = self.parse_strings_with_fallback_decode(file_path)

            print(f"✅ 從 {file_path.name} 提取 {len(strings)} 個字符串")
            return strings
            
        except Exception as e:
            print(f"⚠️ 讀取 {file_path} 失敗：{e}")
            return {}
    
    def extract_all_strings_files(self) -> Dict[str, Dict[str, str]]:
        """提取所有 .strings 文件"""
        all_strings = {}
        
        if not self.resources_path.exists():
            print(f"❌ 資源路徑不存在：{self.resources_path}")
            return all_strings
        
        # 查找所有 .strings 文件
        strings_files = list(self.resources_path.rglob("*.strings"))
        print(f"🔍 找到 {len(strings_files)} 個 .strings 文件")
        
        for file_path in strings_files:
            relative_path = file_path.relative_to(self.app_path)
            strings = self.extract_from_strings_file(file_path)
            if strings:
                all_strings[str(relative_path)] = strings
                
        return all_strings
    
    def looks_like_ui_text(self, value: str) -> bool:
        value = value.strip()
        if len(value) < 2:
            return False
        if value.startswith("NS") or value.startswith("IB"):
            return False
        if value in {"YES", "NO", "true", "false", "nil", "NULL"}:
            return False
        if re.fullmatch(r"[A-Za-z0-9_.:/-]+", value) and len(value) > 24:
            return False
        if re.fullmatch(r"[A-Za-z0-9_-]+", value) and len(value) < 4:
            return False
        return bool(re.search(r"[A-Za-z\u3040-\u30ff\u3400-\u9fff]", value))

    def extract_from_nib_strings(self, file_path: Path) -> List[Dict]:
        """從編譯後 nib 中提取候選文本"""
        ui_elements = []
        try:
            result = subprocess.run(
                ["strings", "-a", str(file_path)],
                capture_output=True,
                text=True,
                check=True,
            )
            seen = set()
            for line in result.stdout.splitlines():
                value = line.strip()
                if not self.looks_like_ui_text(value):
                    continue
                if value in seen:
                    continue
                seen.add(value)
                ui_elements.append({
                    "file": file_path.name,
                    "path": str(file_path.relative_to(self.app_path)),
                    "value": value,
                    "type": "nib-candidate",
                })

            print(f"✅ 從 {file_path.name} 提取 {len(ui_elements)} 個 UI 元素")
            
        except Exception as e:
            print(f"⚠️ 讀取 {file_path} 失敗：{e}")
            
        return ui_elements
    
    def extract_all_nib_files(self) -> List[Dict]:
        """提取所有 .nib 文件中的候選文本"""
        all_elements = []
        
        if not self.resources_path.exists():
            return all_elements
        
        nib_files = list(self.resources_path.rglob("*.nib"))
        print(f"🔍 找到 {len(nib_files)} 個 .nib 文件")
        
        for file_path in nib_files:
            elements = self.extract_from_nib_strings(file_path)
            all_elements.extend(elements)
            
        return all_elements
    
    def export_to_json(self, output_path: str):
        """導出提取的結果到 JSON"""
        data = {
            "app_path": str(self.app_path),
            "extracted_strings": self.extracted_strings,
            "ui_elements": self.ui_elements,
            "total_strings": sum(len(s) for s in self.extracted_strings.values()),
            "total_ui_elements": len(self.ui_elements)
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"✅ 已導出到 {output_path}")
        
    def export_to_csv(self, output_path: str):
        """導出提取的結果到 CSV（用於翻譯對照）"""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Key', 'SourceText', 'Current_zh-TW', 'Suggested_zh-TW', 'Context'])
            
            # 收集所有唯一字符串
            all_strings = set()
            for file_strings in self.extracted_strings.values():
                all_strings.update(file_strings.keys())
            
            for key in sorted(all_strings):
                # 查找第一個出現的值
                source_text = ""
                for file_strings in self.extracted_strings.values():
                    if key in file_strings:
                        source_text = file_strings[key]
                        break

                writer.writerow([
                    key,
                    source_text,
                    self.translation_candidates.get(key, ''),
                    '',
                    'strings',
                ])
                
        print(f"✅ 已導出 CSV 到 {output_path}")

    def export_ui_candidates(self, output_path: str):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.ui_elements, f, ensure_ascii=False, indent=2)
        print(f"✅ 已導出 UI 候選到 {output_path}")
    
    def run(self, output_dir: str = "."):
        """執行完整提取流程"""
        print(f"🚀 開始提取 VOCALOID6 資源字符串")
        print(f"📁 應用路徑：{self.app_path}")

        self.load_existing_translation_candidates()
        
        # 提取 .strings 文件
        self.extracted_strings = self.extract_all_strings_files()
        
        # 提取 .nib 文件候選文本
        self.ui_elements = self.extract_all_nib_files()
        
        # 導出結果
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.export_to_json(str(output_path / "extracted_strings.json"))
        self.export_to_csv(str(output_path / "translation_template.csv"))
        self.export_ui_candidates(str(output_path / "nib_ui_candidates.json"))
        
        # 生成統計報告
        self.generate_report(output_path / "extraction_report.md")
        
        print(f"\n✅ 提取完成！共提取 {sum(len(s) for s in self.extracted_strings.values())} 個字符串")
        
    def generate_report(self, output_path: str):
        """生成提取報告"""
        total_strings = sum(len(s) for s in self.extracted_strings.values())
        
        report = f"""# VOCALOID6 資源字符串提取報告

## 基本信息
- **應用路徑**: {self.app_path}
- **提取時間**: {datetime.now().isoformat()}
- **總字符串數**: {total_strings}
- **UI 元素數**: {len(self.ui_elements)}

## 文件統計

### .strings 文件
| 文件路徑 | 字符串數量 |
|---------|-----------|
"""
        for file_path, strings in self.extracted_strings.items():
            report += f"| {file_path} | {len(strings)} |\n"
        
        report += f"""
### .nib 候選文本
共 {len(self.ui_elements)} 個候選 UI 文本

## 下一步
1. 審查 `translation_template.csv`
2. 以 `zh-TW` 為主補齊翻譯
3. 運行 `resource_replacer.py` 生成本地化資源
4. 使用 `installer.py` 安裝漢化包
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
            
        print(f"📊 已生成報告：{output_path}")


def main():
    parser = argparse.ArgumentParser(description='VOCALOID6 Mac 版資源字符串提取工具')
    parser.add_argument('app_path', help='VOCALOID6.app 路徑')
    parser.add_argument('-o', '--output', default='./output', help='輸出目錄')
    
    args = parser.parse_args()
    
    extractor = VocaloidStringExtractor(args.app_path)
    extractor.run(args.output)


if __name__ == '__main__':
    main()
