#!/usr/bin/env python3
"""
將 nib 原始候選文本清洗成較像真實 UI 文案的集合，
並用現有 glossaries 自動匹配繁體中文翻譯，導出可維護模板。
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = text.replace("（", "(").replace("）", ")").replace("：", ":")
    text = re.sub(r"\s+", " ", text.strip())
    if text.endswith(";") and len(text) > 2:
        text = text[:-1] + ":"
    if text.endswith(("/", "+")) and len(text) > 2:
        text = text[:-1]
    if re.fullmatch(r".+[PQ]$", text) and " " in text:
        text = text[:-1]
    if re.fullmatch(r".+\d$", text) and " " in text:
        text = text[:-1]
    return text


def normalized_key(text: str) -> str:
    return normalize_text(text).casefold()


def looks_like_visible_text(text: str) -> bool:
    text = normalize_text(text)
    if not text or len(text) < 2 or len(text) > 120:
        return False
    if text.startswith("."):
        return False
    if text in {"YES", "NO", "true", "false", "nil", "NULL", "System"}:
        return False
    if "\ufffd" in text:
        return False
    if text.startswith("Copyright "):
        return False
    if "Encoding NSStackView requires" in text:
        return False
    if "pasteboard type" in text:
        return False
    if "IEC61966" in text or "sRGB" in text or "Gamma" in text:
        return False
    if any(token in text for token in ["assets-mainBundleID", "_TtC", "AutomaticTableColumnIdentifier", "headerTextColor"]):
        return False
    if re.fullmatch(r"\{[^}]+\}P?", text):
        return False
    if text.endswith("<"):
        return False
    if re.fullmatch(r"[A-Za-z0-9_./:-]+", text):
        return False
    if re.fullmatch(r"[{}\[\]()<>,;:'\"`~!@#$%^&*+=?|\\/-]+", text):
        return False

    letters = 0
    digits = 0
    spaces = 0
    punct = 0
    for ch in text:
        name = unicodedata.name(ch, "")
        if ch.isalpha() or "CJK" in name or "HIRAGANA" in name or "KATAKANA" in name:
            letters += 1
        elif ch.isdigit():
            digits += 1
        elif ch.isspace():
            spaces += 1
        else:
            punct += 1

    if letters + digits == 0:
        return False
    tokens = [tok for tok in re.split(r"\s+", text) if tok]
    if tokens and all(len(tok) <= 1 for tok in tokens):
        return False
    if spaces == 0 and punct > 0 and letters < 5:
        return False
    if punct > max(4, (letters + digits) * 1.5) and spaces == 0:
        return False
    if re.fullmatch(r"(?:.?[^\w\s]){3,}.?", text):
        return False
    if re.fullmatch(r"(?:[A-Za-z][^A-Za-z0-9\s]){3,}[A-Za-z]?", text):
        return False
    if re.fullmatch(r"[A-Za-z](?:\W[A-Za-z]){2,}", text):
        return False
    if re.search(r"[{}<>]{2,}", text):
        return False
    return True


def build_glossary(*payloads: dict[str, str]) -> dict[str, tuple[str, str]]:
    merged: dict[str, tuple[str, str]] = {}
    for payload in payloads:
        for source, translated in payload.items():
            merged[normalized_key(source)] = (source, translated)
    return merged


def lookup_translation(text: str, glossary: dict[str, tuple[str, str]]) -> tuple[str, str] | None:
    candidates = [text]

    if text.endswith(("@", ",", "]")) and len(text) > 2:
        candidates.append(text[:-1])

    if re.fullmatch(r".+[:@\],][A-Z]$", text):
        candidates.append(text[:-1])

    if re.fullmatch(r".+[A-Z]$", text) and " " in text:
        candidates.append(text[:-1])

    seen = set()
    for candidate in candidates:
        key = normalized_key(candidate)
        if key in seen:
            continue
        seen.add(key)
        hit = glossary.get(key)
        if hit:
            return hit
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap visible nib UI text translations")
    parser.add_argument("--input", default="output/nib_ui_candidates.json")
    parser.add_argument("--source-glossary", default="data/glossaries/source-text-zh-TW.json")
    parser.add_argument("--ui-glossary", default="data/glossaries/nib-visible-zh-TW.json")
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_items = load_json(input_path)
    source_glossary = load_json(Path(args.source_glossary))
    ui_glossary = load_json(Path(args.ui_glossary))
    glossary = build_glossary(source_glossary, ui_glossary)

    counts = Counter()
    files = defaultdict(set)
    ordered_unique: list[str] = []
    seen = set()

    for item in raw_items:
        value = normalize_text(str(item.get("value", "")))
        if not looks_like_visible_text(value):
            continue
        counts[value] += 1
        files[value].add(item.get("file", ""))
        if value not in seen:
            seen.add(value)
            ordered_unique.append(value)

    visible_entries = []
    matched = 0
    unmatched = 0
    for value in ordered_unique:
        hit = lookup_translation(value, glossary)
        translated = hit[1] if hit else ""
        source_match = hit[0] if hit else ""
        if hit:
            matched += 1
        else:
            unmatched += 1
        visible_entries.append(
            {
                "value": value,
                "translation": translated,
                "matched_source": source_match,
                "occurrences": counts[value],
                "file_count": len(files[value]),
                "files": sorted(files[value]),
            }
        )

    json_path = output_dir / "nib_visible_ui_texts.json"
    json_path.write_text(json.dumps(visible_entries, ensure_ascii=False, indent=2), encoding="utf-8")

    csv_path = output_dir / "nib_visible_ui_translation_template.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["SourceText", "Suggested_zh-TW", "MatchedSource", "Occurrences", "FileCount", "Files"])
        for item in visible_entries:
            writer.writerow(
                [
                    item["value"],
                    item["translation"],
                    item["matched_source"],
                    item["occurrences"],
                    item["file_count"],
                    "; ".join(item["files"]),
                ]
            )

    report_path = output_dir / "nib_visible_ui_report.md"
    top_unmatched = [item for item in visible_entries if not item["translation"]][:40]
    report_lines = [
        "# NIB Visible UI Text Bootstrap Report",
        "",
        f"- Raw candidate count: {len(raw_items)}",
        f"- Filtered visible unique candidates: {len(visible_entries)}",
        f"- Auto-matched translations: {matched}",
        f"- Remaining unmatched: {unmatched}",
        "",
        "## Top unmatched visible candidates",
        "",
        "| Text | Occurrences | Files |",
        "| --- | ---: | ---: |",
    ]
    for item in top_unmatched:
        report_lines.append(f"| {item['value'].replace('|', '\\|')} | {item['occurrences']} | {item['file_count']} |")
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"visible_unique={len(visible_entries)}")
    print(f"matched={matched}")
    print(f"unmatched={unmatched}")
    print(f"json={json_path}")
    print(f"csv={csv_path}")
    print(f"report={report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
