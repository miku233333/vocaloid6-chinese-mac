#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VOCALOID6 Mac 繁體中文一鍵安裝器

優先嘗試安裝到現有 app；若原 app 不可寫，則自動安裝到使用者副本。
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from installer import VocaloidInstaller
from private_data import private_translation_path


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def is_bundle_writable(app_path: Path) -> bool:
    resources = app_path / "Contents" / "Resources"
    return os.access(resources, os.W_OK)


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def clone_app(source: Path, target: Path) -> None:
    ensure_parent_dir(target)
    if target.exists():
        shutil.rmtree(target)
    run(["ditto", str(source), str(target)])


def resolve_source_app(explicit_source: str | None, language: str) -> Path:
    installer = VocaloidInstaller(language, app_path=explicit_source, assume_yes=True)
    app_path = installer.detect_installation()
    if not app_path:
        raise FileNotFoundError("找不到可用的 VOCALOID6 Editor.app")
    return app_path


def install_to_target(target_app: Path, language: str) -> None:
    installer = VocaloidInstaller(language, app_path=str(target_app), assume_yes=True)
    installer.install()


def main() -> int:
    parser = argparse.ArgumentParser(description="VOCALOID6 Mac 一鍵安裝器")
    parser.add_argument("--lang", default="zh-TW", help="安裝語言，預設 zh-TW")
    parser.add_argument("--source-app", help="指定來源 VOCALOID6 .app 路徑")
    parser.add_argument(
        "--mode",
        choices=["auto", "inplace", "copy"],
        default="auto",
        help="auto=自動判斷；inplace=強制裝原 app；copy=強制裝使用者副本",
    )
    parser.add_argument(
        "--copy-target",
        default=str(Path.home() / "Applications" / "VOCALOID6 Editor zh-TW.app"),
        help="副本安裝目標路徑，預設 ~/Applications/VOCALOID6 Editor zh-TW.app",
    )
    parser.add_argument("--no-open", action="store_true", help="安裝後不自動打開 app")
    args = parser.parse_args()

    source_app = resolve_source_app(args.source_app, args.lang)
    copy_target = Path(args.copy_target).expanduser()
    translation_file = private_translation_path(args.lang)

    if not translation_file.exists():
        print("❌ 找不到本機私有翻譯資料")
        print(f"   需要：{translation_file}")
        print("   公開倉庫不再附帶 VOCALOID6 專用翻譯資料，請先在本機私有目錄生成或放入對應文件。")
        return 1

    print("🎵 VOCALOID6 Mac 繁體中文一鍵安裝")
    print("=" * 50)
    print(f"📦 來源 app：{source_app}")
    print(f"🌍 語言：{args.lang}")

    if args.mode == "copy":
        final_target = copy_target
        print(f"🪄 模式：使用者副本安裝 -> {final_target}")
        clone_app(source_app, final_target)
    elif args.mode == "inplace":
        final_target = source_app
        print(f"🪄 模式：直接安裝原 app -> {final_target}")
    else:
        if is_bundle_writable(source_app):
            final_target = source_app
            print(f"🪄 模式：原 app 可寫，直接安裝 -> {final_target}")
        else:
            final_target = copy_target
            print("🪄 模式：原 app 不可寫，自動切換到使用者副本")
            print(f"📁 副本目標：{final_target}")
            clone_app(source_app, final_target)

    install_to_target(final_target, args.lang)

    if not args.no_open:
        run(["open", "-n", str(final_target)], check=False)

    print("\n✅ 一鍵安裝完成")
    print(f"📍 最終安裝目標：{final_target}")
    if final_target != source_app:
        print("ℹ️ 這次是安裝到使用者副本，不會直接改動 /Applications 下的原始 app。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
