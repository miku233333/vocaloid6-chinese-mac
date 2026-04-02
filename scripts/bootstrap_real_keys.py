#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根據真實提取結果，為 zh-TW.json 補上實際 app key 的種子翻譯。
"""

import argparse
import json
from pathlib import Path
from typing import Dict

from private_data import private_glossary_path, private_translation_path


def load_json(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: Dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap real VOCALOID6 keys into zh-TW translations")
    parser.add_argument(
        "--extracted",
        default="output/extracted_strings.json",
        help="提取腳本輸出的 extracted_strings.json 路徑",
    )
    parser.add_argument(
        "--glossary",
        default=str(private_glossary_path("source-text-zh-TW.json")),
        help="來源文本到繁中譯文的對照表",
    )
    parser.add_argument(
        "--translation",
        default=str(private_translation_path("zh-TW")),
        help="zh-TW 翻譯文件路徑",
    )
    args = parser.parse_args()

    extracted = load_json(Path(args.extracted))
    glossary = load_json(Path(args.glossary))
    translation_payload = load_json(Path(args.translation))
    translations = translation_payload.setdefault("translations", {})

    added = 0
    updated = 0
    unmatched = []
    seen_keys = {}

    for _, file_strings in extracted.get("extracted_strings", {}).items():
        for key, source_text in file_strings.items():
            candidate = glossary.get(source_text)
            if not candidate:
                if key not in translations:
                    unmatched.append((key, source_text))
                continue

            previous = translations.get(key)
            if previous is None:
                translations[key] = candidate
                added += 1
            elif previous != candidate:
                translations[key] = candidate
                updated += 1

            seen_keys[key] = source_text

    translation_payload["real_key_bootstrap"] = {
        "source_file_count": len(extracted.get("extracted_strings", {})),
        "matched_keys": len(seen_keys),
        "added": added,
        "updated": updated,
        "unmatched_count": len(unmatched),
    }

    save_json(Path(args.translation), translation_payload)

    print(f"matched_keys={len(seen_keys)}")
    print(f"added={added}")
    print(f"updated={updated}")
    print(f"unmatched={len(unmatched)}")
    print("sample_unmatched:")
    for key, source_text in unmatched[:40]:
        print(f"{key}\t{source_text}")


if __name__ == "__main__":
    main()
