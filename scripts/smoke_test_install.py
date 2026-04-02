#!/usr/bin/env python3
"""
VOCALOID6 Mac 繁體中文安裝冒煙測試

驗證流程：
1. 複製原始 app 到測試副本
2. 執行 installer.py 安裝語言包
3. 檢查 zh-TW.lproj 與 .strings 文件
4. 驗證 codesign
5. 嘗試啟動副本 app
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="VOCALOID6 Mac 安裝冒煙測試")
    parser.add_argument(
        "--source-app",
        default="/Applications/VOCALOID6 Editor.app",
        help="原始 VOCALOID6 .app 路徑",
    )
    parser.add_argument(
        "--test-app",
        default="./tmp/VOCALOID6 Editor Test.app",
        help="測試副本 .app 路徑",
    )
    parser.add_argument("--lang", default="zh-TW", help="安裝語言")
    parser.add_argument(
        "--launch-wait",
        type=int,
        default=8,
        help="啟動後等待秒數",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    installer = repo_root / "scripts" / "installer.py"
    source_app = Path(args.source_app).expanduser().resolve()
    test_app = Path(args.test_app).expanduser()
    if not test_app.is_absolute():
        test_app = (repo_root / test_app).resolve()

    if not source_app.exists():
        print(f"❌ 找不到原始 app：{source_app}")
        return 1

    print(f"📦 原始 app：{source_app}")
    print(f"🧪 測試副本：{test_app}")

    run(["pkill", "-f", test_app.name], check=False)
    run(["rm", "-rf", str(test_app)], check=False)
    test_app.parent.mkdir(parents=True, exist_ok=True)

    print("1. 複製測試副本")
    run(["ditto", str(source_app), str(test_app)])

    print("2. 安裝繁體中文語言包")
    result = run(
        [
            sys.executable,
            str(installer),
            "--app-path",
            str(test_app),
            "--lang",
            args.lang,
            "-y",
            "--install",
        ]
    )
    print(result.stdout.strip())

    resources = test_app / "Contents" / "Resources"
    locale_dir = resources / f"{args.lang}.lproj"
    strings_files = list(locale_dir.glob("*.strings"))
    if not locale_dir.exists() or not strings_files:
        print(f"❌ 缺少本地化輸出：{locale_dir}")
        return 1
    print(f"3. 本地化輸出存在：{len(strings_files)} 個 .strings 文件")

    compiled_nib = resources / "VEHomeWC.nib" / "keyedobjects-110000.nib"
    if not compiled_nib.exists():
        print(f"❌ 缺少首頁 compiled nib：{compiled_nib}")
        return 1
    compiled_blob = compiled_nib.read_bytes()
    for marker in ("開啟", "新增專案", "最近開啟", "新聞欄"):
        if marker.encode("utf-8") not in compiled_blob:
            print(f"❌ 缺少首頁 nib 補丁字串：{marker}")
            return 1
    print("3b. 首頁 compiled nib 補丁存在")

    print("4. 驗證 codesign")
    run(["codesign", "--verify", "--deep", "--strict", str(test_app)])
    print("✅ codesign 驗證通過")

    print("5. 啟動測試副本")
    run(["open", "-n", str(test_app)])
    time.sleep(args.launch_wait)
    proc = None
    process_patterns = [test_app.stem, "VOCALOID6 Editor"]
    for pattern in process_patterns:
        proc = run(["pgrep", "-af", pattern], check=False)
        if proc.returncode == 0 and proc.stdout.strip():
            break

    if proc is None or proc.returncode != 0 or not proc.stdout.strip():
        print("❌ 未檢測到測試副本進程")
        return 1
    print("✅ 啟動成功")
    print(proc.stdout.strip())

    run(["pkill", "-f", test_app.name], check=False)
    print("\n🎉 冒煙測試完成：安裝、重簽名、codesign 驗證、啟動均成功")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
