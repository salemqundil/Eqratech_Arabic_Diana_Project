#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Normalize RAW i3rab DB to a stable CSV format for the pipeline.

Output columns:
- surah
- ayah
- word
- i3rab

For now:
- We output ONE row per ayah with word="__AYAH__" and i3rab = full erab text.
Then we can upgrade to true word-level once you show me 5-10 sample lines of erab text.
"""

import argparse
import csv
import os
import re


def normalize_ws(s: str) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-db", required=True, help="Input RAW DB CSV (from downloader)")
    ap.add_argument("--out", required=True, help="Output normalized CSV")
    args = ap.parse_args()

    with open(args.in_db, "r", encoding="utf-8", newline="") as fin, \
         open(args.out, "w", encoding="utf-8", newline="") as fout:

        r = csv.DictReader(fin)
        w = csv.writer(fout)
        w.writerow(["surah", "ayah", "word", "i3rab"])

        for row in r:
            surah = (row.get("surah") or "").strip()
            ayah = (row.get("ayah") or "").strip()
            erab_text = normalize_ws(row.get("erab_text") or "")

            if not surah or not ayah or not erab_text:
                continue

            # Ayah-level row (always valid)
            w.writerow([surah, ayah, "__AYAH__", erab_text])

    print(f"[DONE] Normalized CSV -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
