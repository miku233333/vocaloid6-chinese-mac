#!/usr/bin/env python3
"""
分析 compiled nib 目錄中的 keyedobjects-*.nib，
輸出可見字符串的偏移、長度前綴與原始字節，供未來定向 patch 參考。
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def collect_ascii_runs(blob: bytes, min_len: int = 3):
    pattern = re.compile(rb"[ -~]{%d,}" % min_len)
    for match in pattern.finditer(blob):
        yield match.start(), match.group().decode("ascii", errors="ignore")


def inspect_file(path: Path):
    blob = path.read_bytes()
    results = []
    for offset, text in collect_ascii_runs(blob):
        if text.startswith("IB.") or text.startswith("NS"):
            continue
        if len(text) > 120:
            continue
        prefix = blob[max(0, offset - 8):offset]
        results.append(
            {
                "offset": offset,
                "text": text,
                "prefix_hex": prefix.hex(),
                "length_marker": blob[offset - 1] if offset > 0 else None,
                "file": path.name,
            }
        )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze compiled nib keyedobjects files")
    parser.add_argument("nib_dir", help="compiled .nib directory path")
    parser.add_argument("-o", "--output", help="output JSON path")
    parser.add_argument("--contains", help="only keep strings containing this substring")
    args = parser.parse_args()

    nib_dir = Path(args.nib_dir).expanduser().resolve()
    if not nib_dir.exists() or not nib_dir.is_dir():
        raise SystemExit(f"not a nib directory: {nib_dir}")

    payload = {
        "nib_dir": str(nib_dir),
        "results": [],
    }

    for keyed in sorted(nib_dir.glob("keyedobjects-*.nib")):
        rows = inspect_file(keyed)
        if args.contains:
            rows = [row for row in rows if args.contains in row["text"]]
        payload["results"].extend(rows)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
