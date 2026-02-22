#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Find awzan rows that contain example words.

Why:
  Some awzan CSVs only contain templates + CV columns and no example words, so
  benchmarks that require examples cannot run. This tool reports coverage and
  prints/export rows that include examples.

Usage:
  python3 tools/find_awzan_with_examples.py src/fvafk/phonology/awzan_merged_final_clean.csv
  python3 tools/find_awzan_with_examples.py src/fvafk/phonology/awzan_merged_final_clean.csv --limit 50
  python3 tools/find_awzan_with_examples.py src/fvafk/phonology/awzan_merged_final_clean.csv --write-csv awzan_with_examples.csv
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def _sniff_delimiter(path: Path) -> str:
    sample = path.read_text(encoding="utf-8-sig", errors="replace")[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t")
        return dialect.delimiter
    except Exception:
        return ","


def _norm(s: str | None) -> str:
    return (s or "").strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path", type=str, help="Path to awzan CSV")
    ap.add_argument("--limit", type=int, default=30, help="Max rows to print")
    ap.add_argument("--write-csv", type=str, default="", help="Write rows with examples to CSV path")
    args = ap.parse_args()

    path = Path(args.csv_path).expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"CSV not found: {path}")

    delimiter = _sniff_delimiter(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        cols = reader.fieldnames or []
        want_cols = {
            "الوزن",
            "source",
            "CV",
            "Detailed_CV",
            "Advanced_CV",
            "الاسم",
            "الوصف",
            "ملاحظات",
            "مثال",
            "Matched_Example",
            "الجذر",
            "نمط_الحركات",
        }
        missing = [c for c in ("الوزن",) if c not in cols]
        if missing:
            raise SystemExit(f"CSV missing required columns: {missing}. Found: {cols}")

        rows = list(reader)

    total = len(rows)
    with_example: list[dict[str, str]] = []
    for r in rows:
        ex1 = _norm(r.get("مثال"))
        ex2 = _norm(r.get("Matched_Example"))
        if ex1 or ex2:
            with_example.append(r)

    print(f"CSV: {path}")
    print(f"Total patterns: {total}")
    print(f"With ANY example: {len(with_example)} ({(len(with_example)/total*100 if total else 0):.1f}%)")
    print("Columns:", ", ".join(cols))

    print("\nFirst rows WITH examples:\n" + "-" * 72)
    for r in with_example[: max(0, args.limit)]:
        tpl = _norm(r.get("الوزن"))
        src = _norm(r.get("source"))
        ex1 = _norm(r.get("مثال"))
        ex2 = _norm(r.get("Matched_Example"))
        root = _norm(r.get("الجذر"))
        print(f"- {tpl}  (source={src}, root={root or 'MISSING'})")
        if ex1:
            print(f"  مثال: {ex1}")
        if ex2:
            print(f"  Matched_Example: {ex2}")

    out_csv = _norm(args.write_csv)
    if out_csv:
        out_path = Path(out_csv).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # Keep stable subset of columns (only those that exist)
        fieldnames = [c for c in [
            "الوزن",
            "source",
            "CV",
            "Detailed_CV",
            "Advanced_CV",
            "الاسم",
            "الوصف",
            "ملاحظات",
            "مثال",
            "Matched_Example",
            "الجذر",
            "نمط_الحركات",
        ] if c in (cols or [])]
        with out_path.open("w", encoding="utf-8", newline="") as h:
            w = csv.DictWriter(h, fieldnames=fieldnames, delimiter=",")
            w.writeheader()
            for r in with_example:
                w.writerow({k: r.get(k, "") for k in fieldnames})
        print(f"\nWrote {len(with_example)} rows to: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

