#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VOCALOID6 Mac 繁體中文安裝器
支持自動備份、安裝、還原、卸載
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Optional
import argparse
from datetime import datetime

from resource_replacer import ResourceReplacer


class VocaloidInstaller:
    """VOCALOID6 Mac 繁體中文安裝器"""
    
    def __init__(self, language: str = "zh-TW", app_path: Optional[str] = None, assume_yes: bool = False):
        self.language = language
        self.app_name = "VOCALOID6"
        self.explicit_app_path = Path(app_path).expanduser() if app_path else None
        self.assume_yes = assume_yes
        self.app_paths = self.find_vocaloid_installations()
        self.backup_base = Path.home() / ".vocaloid6-backup"
        self.script_dir = Path(__file__).parent
        self.data_dir = self.script_dir.parent / "data"
        
    def find_vocaloid_installations(self) -> list:
        """查找系統中所有 VOCALOID6 安裝"""
        if self.explicit_app_path:
            if self.explicit_app_path.exists() and (self.explicit_app_path / "Contents/MacOS").exists():
                return [self.explicit_app_path]
            raise FileNotFoundError(f"指定的 VOCALOID6 路徑不存在或不是有效 .app：{self.explicit_app_path}")

        possible_paths = [
            Path("/Applications/VOCALOID6.app"),
            Path.home() / "Applications/VOCALOID6.app",
            Path("/Applications/VOCALOID 6.app"),
            Path.home() / "Applications/VOCALOID 6.app",
            Path("/Applications/VOCALOID6 Editor.app"),
            Path.home() / "Applications/VOCALOID6 Editor.app",
        ]
        
        found = []
        for path in possible_paths:
            if path.exists() and (path / "Contents/MacOS").exists():
                found.append(path)
                
        # 使用 Spotlight 搜索
        try:
            result = subprocess.run(
                ['mdfind', 'kMDItemCFBundleIdentifier == "com.yamaha.vocaloid6"'],
                capture_output=True, text=True
            )
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    p = Path(line)
                    if p.exists() and p not in found:
                        found.append(p)
        except Exception as e:
            print(f"⚠️ Spotlight 搜索失敗：{e}")
            
        return found
    
    def detect_installation(self) -> Optional[Path]:
        """檢測 VOCALOID6 安裝路徑"""
        if not self.app_paths:
            return None
            
        if len(self.app_paths) == 1:
            return self.app_paths[0]
            
        # 多個安裝，讓用戶選擇
        print("\n📍 找到多個 VOCALOID6 安裝:")
        for i, path in enumerate(self.app_paths, 1):
            print(f"  {i}. {path}")
            
        while True:
            try:
                choice = input("\n請選擇 (輸入數字，或按 Enter 選擇第一個): ").strip()
                if not choice:
                    return self.app_paths[0]
                idx = int(choice) - 1
                if 0 <= idx < len(self.app_paths):
                    return self.app_paths[idx]
            except ValueError:
                pass
            print("❌ 無效輸入")
            
    def create_backup(self, app_path: Path) -> Path:
        """創建完整備份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_base / timestamp
        
        print(f"💾 創建備份：{backup_path}")
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # 備份整個應用（或至少 Resources）
        resources_path = app_path / "Contents/Resources"
        if resources_path.exists():
            backup_resources = backup_path / "Resources"
            subprocess.run(
                ["ditto", str(resources_path), str(backup_resources)],
                check=True,
            )
            
        # 保存元數據
        metadata = {
            "backup_time": datetime.now().isoformat(),
            "app_path": str(app_path),
            "language": self.language,
            "version": "1.0",
            "app_name": self.app_name
        }
        
        with open(backup_path / "backup_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
            
        print(f"✅ 備份完成")
        return backup_path
    
    def install_language_pack(self, app_path: Path):
        """安裝語言包"""
        print(f"\n📦 安裝 {self.language} 語言包...")
        
        resources_path = app_path / "Contents/Resources"
        lang_dir = resources_path / f"{self.language}.lproj"
        
        # 創建語言目錄
        lang_dir.mkdir(parents=True, exist_ok=True)

        replacer = ResourceReplacer(str(app_path), self.language)
        replacer.load_translations()
        replacer.load_terminology()
        translated_files = replacer.build_translated_strings_files()

        installed_count = 0
        for filename, entries in translated_files.items():
            destination = lang_dir / filename
            with open(destination, 'w', encoding='utf-16') as f:
                for key, value in entries.items():
                    f.write(f'"{key}" = "{value}";\n')
            installed_count += 1

        if installed_count == 0:
            self.generate_localizable_strings(lang_dir)
        else:
            print(f"✅ 安裝 {installed_count} 個本地化 strings 文件")
        
        # 創建 Info.plist 覆蓋（如果需要）
        self.patch_info_plist(app_path)
        self.resign_app(app_path)
        
        print(f"✅ 語言包安裝完成")
        
    def generate_localizable_strings(self, lang_dir: Path):
        """回退生成 Localizable.strings 文件"""
        translation_file = self.data_dir / "translations" / f"{self.language}.json"
        if not translation_file.exists():
            return
            
        with open(translation_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        translations = data.get('translations', {})
        
        strings_path = lang_dir / "Localizable.strings"
        with open(strings_path, 'w', encoding='utf-16') as f:
            for key, value in translations.items():
                f.write(f'"{key}" = "{value}";\n')
                
        print(f"✅ 生成 Localizable.strings")
        
    def patch_info_plist(self, app_path: Path):
        """修改 Info.plist 添加語言支持"""
        info_plist = app_path / "Contents/Info.plist"
        
        if not info_plist.exists():
            return
            
        try:
            import plistlib
            with open(info_plist, 'rb') as f:
                plist_data = plistlib.load(f)
                
            # 添加語言到 CFBundleLocalizations
            if 'CFBundleLocalizations' not in plist_data:
                plist_data['CFBundleLocalizations'] = []
                
            if self.language not in plist_data['CFBundleLocalizations']:
                plist_data['CFBundleLocalizations'].append(self.language)
                print(f"✅ 更新 Info.plist 語言列表")
                
            # 保存
            with open(info_plist, 'wb') as f:
                plistlib.dump(plist_data, f)
                
        except Exception as e:
            print(f"⚠️ 修改 Info.plist 失敗：{e}")

    def resign_app(self, app_path: Path):
        """對修改後的 .app 進行 ad-hoc 重簽名，避免因 bundle 被改動而無法啟動"""
        try:
            subprocess.run(
                ['codesign', '--force', '--deep', '--sign', '-', '--timestamp=none', str(app_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ['codesign', '--verify', '--deep', '--strict', str(app_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            print("✅ 已完成 app ad-hoc 重簽名")
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.strip() if e.stderr else str(e)
            print(f"⚠️ 重簽名失敗：{stderr}")
            
    def create_shortcut(self, app_path: Path):
        """創建桌面快捷方式（可選）"""
        # Mac 上通常不需要，因為 .app 本身就是可執行文件
        pass
        
    def install(self):
        """執行安裝流程"""
        print("🚀 VOCALOID6 Mac 繁體中文安裝器")
        print("=" * 50)
        
        # 檢測安裝
        app_path = self.detect_installation()
        if not app_path:
            print("❌ 未找到 VOCALOID6 安裝")
            print("\n請確保 VOCALOID6 已安裝到以下位置之一:")
            print("  - /Applications/VOCALOID6.app")
            print("  - ~/Applications/VOCALOID6.app")
            print("  - /Applications/VOCALOID 6.app")
            print("  - ~/Applications/VOCALOID 6.app")
            print("  - /Applications/VOCALOID6 Editor.app")
            print("  - ~/Applications/VOCALOID6 Editor.app")
            sys.exit(1)
            
        print(f"\n✅ 找到 VOCALOID6: {app_path}")
        
        # 確認
        print(f"\n⚠️ 即將安裝 {self.language} 語言包到:")
        print(f"   {app_path}")

        if not self.assume_yes:
            response = input("\n繼續？(y/N): ").strip().lower()
            if response != 'y':
                print("❌ 安裝已取消")
                sys.exit(0)
            
        # 備份
        print("\n📋 步驟 1/3: 備份原文件")
        backup_path = self.create_backup(app_path)
        
        # 安裝
        print("\n📋 步驟 2/3: 安裝語言包")
        self.install_language_pack(app_path)
        
        # 完成
        print("\n📋 步驟 3/3: 完成")
        print("=" * 50)
        print(f"✅ 安裝完成！")
        print(f"\n📁 備份位置：{backup_path}")
        print(f"🌍 語言：{self.language}")
        print(f"\n🔄 啟動 VOCALOID6 查看效果")
        print(f"\n💡 提示：如需還原，運行:")
        print(f"   python3 {self.script_dir}/installer.py --restore")
        
    def restore(self):
        """還原到原始狀態"""
        print("🔄 VOCALOID6 還原工具")
        print("=" * 50)
        
        if not self.backup_base.exists():
            print("❌ 找不到備份目錄")
            sys.exit(1)
            
        backups = sorted(self.backup_base.iterdir(), reverse=True)
        if not backups:
            print("❌ 找不到備份")
            sys.exit(1)
            
        print("\n📋 可用備份:")
        for i, backup in enumerate(backups[:10], 1):  # 只显示最近 10 個
            metadata_file = backup / "backup_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                print(f"  {i}. {backup.name} - {meta.get('backup_time', 'Unknown')}")
            else:
                print(f"  {i}. {backup.name}")
                
        while True:
            try:
                choice = input("\n請選擇要還原的備份 (輸入數字): ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(backups):
                    selected_backup = backups[idx]
                    break
            except ValueError:
                pass
            print("❌ 無效輸入")
            
        # 確認
        print(f"\n⚠️ 即將還原到:")
        print(f"   {selected_backup}")
        
        if not self.assume_yes:
            response = input("\n繼續？(y/N): ").strip().lower()
            if response != 'y':
                print("❌ 還原已取消")
                sys.exit(0)
            
        # 找到對應的應用路徑
        metadata_file = selected_backup / "backup_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            app_path = Path(meta.get('app_path', ''))
        else:
            app_path = self.detect_installation()
            
        if not app_path or not app_path.exists():
            print("❌ 找不到原應用路徑")
            sys.exit(1)
            
        # 執行還原
        resources_path = app_path / "Contents/Resources"
        backup_resources = selected_backup / "Resources"
        
        if not backup_resources.exists():
            print("❌ 備份中沒有 Resources 目錄")
            sys.exit(1)
            
        print(f"\n🔄 還原中...")
        
        # 刪除當前 Resources
        if resources_path.exists():
            shutil.rmtree(resources_path)
            
        # 複製備份
        shutil.copytree(backup_resources, resources_path)
        
        print(f"✅ 還原完成！")
        print(f"📁 應用已恢復到安裝漢化包前的狀態")
        
    def uninstall(self):
        """卸載語言包"""
        print("🗑️ 卸載 VOCALOID6 繁體中文語言包")
        
        app_path = self.detect_installation()
        if not app_path:
            print("❌ 未找到 VOCALOID6")
            sys.exit(1)
            
        resources_path = app_path / "Contents/Resources"
        lang_dir = resources_path / f"{self.language}.lproj"
        
        if lang_dir.exists():
            shutil.rmtree(lang_dir)
            print(f"✅ 已卸載 {self.language} 語言包")
        else:
            print(f"ℹ️  {self.language} 語言包未安裝")


def main():
    parser = argparse.ArgumentParser(description='VOCALOID6 Mac 繁體中文安裝器')
    parser.add_argument('-l', '--lang', default='zh-TW', 
                       help='目標語言 (default: zh-TW)')
    parser.add_argument('--app-path', help='指定要安裝/測試的 VOCALOID6 .app 路徑')
    parser.add_argument('-y', '--yes', action='store_true', help='自動確認，不再提示')
    parser.add_argument('--install', action='store_true', 
                       help='執行安裝（默認）')
    parser.add_argument('--restore', action='store_true', 
                       help='還原到原始狀態')
    parser.add_argument('--uninstall', action='store_true', 
                       help='卸載語言包')
    parser.add_argument('--list-backups', action='store_true', 
                       help='列出所有備份')
    
    args = parser.parse_args()
    
    installer = VocaloidInstaller(args.lang, app_path=args.app_path, assume_yes=args.yes)
    
    if args.restore:
        installer.restore()
    elif args.uninstall:
        installer.uninstall()
    elif args.list_backups:
        if installer.backup_base.exists():
            print("📋 備份列表:")
            for backup in sorted(installer.backup_base.iterdir(), reverse=True):
                print(f"  - {backup.name}")
        else:
            print("ℹ️  暫無備份")
    else:
        # 默認安裝
        installer.install()


if __name__ == '__main__':
    main()
