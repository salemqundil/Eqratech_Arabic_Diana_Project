#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export_discovered_roots_table.py

يستخرج من مخرجات الـ pipeline جدولاً بالجذور المكتشفة مع أول كلمة طابقها والوزن،
ومقارنتها مع data/arabic_roots.csv.

الاستخدام:
  PYTHONPATH=src python3 scripts/export_discovered_roots_table.py
  PYTHONPATH=src python3 scripts/export_discovered_roots_table.py --input out.csv --roots data/arabic_roots.csv --output discovered_roots_table.csv
"""

import argparse
import csv
import sys
from pathlib import Path


def load_arabic_roots(path: Path) -> set:
    """يحمّل مجموعة الجذور من ملف CSV (عمود root)."""
    roots = set()
    if not path.exists():
        return roots
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        col = "root" if "root" in (reader.fieldnames or []) else (reader.fieldnames or [None])[0]
        for row in reader:
            r = (row.get(col) or "").strip()
            if r:
                roots.add(r)
    return roots


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("out.csv"),
        help="ملف CSV مخرجات الـ pipeline (يجب أن يحتوي root ويفضل root_wazn)",
    )
    parser.add_argument(
        "--roots",
        type=Path,
        default=Path("data/arabic_roots.csv"),
        help="ملف الجذور المرجعي للمقارنة",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("discovered_roots_table.csv"),
        help="ملف الجدول الناتج",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"❌ الملف غير موجود: {args.input}", file=sys.stderr)
        return 1

    ref_roots = load_arabic_roots(args.roots)
    # أول ظهور لكل جذر: (كلمة، وزن)
    first_word_by_root: dict[str, tuple[str, str]] = {}

    with open(args.input, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fn = reader.fieldnames or []
        if "root" not in fn:
            print("❌ الملف لا يحتوي عمود 'root'", file=sys.stderr)
            return 1
        has_wazn = "root_wazn" in fn
        for row in reader:
            root = (row.get("root") or "").strip()
            if not root or root in first_word_by_root:
                continue
            word = (row.get("word") or "").strip()
            wazn = (row.get("root_wazn") or "").strip() if has_wazn else ""
            first_word_by_root[root] = (word, wazn)

    # ترتيب الجذور — المقارنة مع المرجع بعد إزالة الشرطات (الـ pipeline يخرج كـ أ-ك-ل والمرجع كتب)
    def norm(r: str) -> str:
        return (r or "").replace("-", "").strip()

    ordered_roots = sorted(first_word_by_root.keys())
    ref_norm = {norm(r) for r in ref_roots}

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["root", "first_word", "wazn", "in_arabic_roots"])
        for root in ordered_roots:
            word, wazn = first_word_by_root[root]
            in_ref = "نعم" if norm(root) in ref_norm else "لا"
            writer.writerow([root, word, wazn, in_ref])

    in_ref_count = sum(1 for r in ordered_roots if r in ref_roots)
    print(f"✅ كُتب {len(ordered_roots)} جذراً إلى {args.output}", file=sys.stderr)
    print(f"   موجود في arabic_roots: {in_ref_count} ، غير موجود: {len(ordered_roots) - in_ref_count}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
