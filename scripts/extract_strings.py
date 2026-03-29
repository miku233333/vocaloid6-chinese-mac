#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VOCALOID6 Mac 版資源字符串提取工具
支援 .strings, .nib, .xib 文件分析
"""

import os
import sys
import plistlib
import json
import re
from pathlib import Path
from typing import Dict, List, Set
import argparse


class VocaloidStringExtractor:
    """VOCALOID6 Mac 版資源字符串提取器"""
    
    def __init__(self, app_path: str):
        self.app_path = Path(app_path)
        self.resources_path = self.app_path / "Contents" / "Resources"
        self.extracted_strings: Dict[str, str] = {}
        self.ui_elements: List[Dict] = []
        
    def extract_from_strings_file(self, file_path: Path) -> Dict[str, str]:
        """從 .strings 文件提取字符串"""
        strings = {}
        try:
            with open(file_path, 'r', encoding='utf-16') as f:
                content = f.read()
            
            # 正則表達式匹配 "key" = "value"; 格式
            pattern = r'"([^"]+)"\s*=\s*"([^"]*)";'
            matches = re.findall(pattern, content)
            
            for key, value in matches:
                strings[key] = value
                
            print(f"✅ 從 {file_path.name} 提取 {len(strings)} 個字符串")
            
        except Exception as e:
            print(f"⚠️ 讀取 {file_path} 失敗：{e}")
            
        return strings
    
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
    
    def extract_from_xib(self, file_path: Path) -> List[Dict]:
        """從 .xib 文件提取 UI 元素"""
        ui_elements = []
        try:
            with open(file_path, 'rb') as f:
                plist_data = plistlib.load(f)
            
            # 遍歷 plist 結構查找 UI 元素
            def traverse(obj, path=""):
                if isinstance(obj, dict):
                    # 查找常見的 UI 屬性
                    if 'string' in obj:
                        ui_elements.append({
                            'file': file_path.name,
                            'path': path,
                            'value': obj['string'],
                            'type': 'string'
                        })
                    
                    for key, value in obj.items():
                        traverse(value, f"{path}.{key}")
                        
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        traverse(item, f"{path}[{i}]")
            
            traverse(plist_data)
            print(f"✅ 從 {file_path.name} 提取 {len(ui_elements)} 個 UI 元素")
            
        except Exception as e:
            print(f"⚠️ 讀取 {file_path} 失敗：{e}")
            
        return ui_elements
    
    def extract_all_xib_files(self) -> List[Dict]:
        """提取所有 .xib 文件"""
        all_elements = []
        
        if not self.resources_path.exists():
            return all_elements
        
        xib_files = list(self.resources_path.rglob("*.xib"))
        print(f"🔍 找到 {len(xib_files)} 個 .xib 文件")
        
        for file_path in xib_files:
            elements = self.extract_from_xib(file_path)
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
            writer.writerow(['Key', 'English', 'zh-CN', 'zh-TW', 'ja-JP', 'Context'])
            
            # 收集所有唯一字符串
            all_strings = set()
            for file_strings in self.extracted_strings.values():
                all_strings.update(file_strings.keys())
            
            for key in sorted(all_strings):
                # 查找第一個出現的值
                english = ""
                for file_strings in self.extracted_strings.values():
                    if key in file_strings:
                        english = file_strings[key]
                        break
                
                writer.writerow([key, english, '', '', '', ''])
                
        print(f"✅ 已導出 CSV 到 {output_path}")
    
    def run(self, output_dir: str = "."):
        """執行完整提取流程"""
        print(f"🚀 開始提取 VOCALOID6 資源字符串")
        print(f"📁 應用路徑：{self.app_path}")
        
        # 提取 .strings 文件
        self.extracted_strings = self.extract_all_strings_files()
        
        # 提取 .xib 文件
        self.ui_elements = self.extract_all_xib_files()
        
        # 導出結果
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.export_to_json(str(output_path / "extracted_strings.json"))
        self.export_to_csv(str(output_path / "translation_template.csv"))
        
        # 生成統計報告
        self.generate_report(output_path / "extraction_report.md")
        
        print(f"\n✅ 提取完成！共提取 {sum(len(s) for s in self.extracted_strings.values())} 個字符串")
        
    def generate_report(self, output_path: str):
        """生成提取報告"""
        total_strings = sum(len(s) for s in self.extracted_strings.values())
        
        report = f"""# VOCALOID6 資源字符串提取報告

## 基本信息
- **應用路徑**: {self.app_path}
- **提取時間**: {Path(output_path).stat().st_mtime}
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
### .xib 文件
共 {len(self.ui_elements)} 個 UI 元素

## 下一步
1. 審查 `translation_template.csv`
2. 填寫翻譯（zh-CN, zh-TW, ja-JP）
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
