#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import argparse

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-raw", default="raw_i3rab_ayah.csv")
    ap.add_argument("--out", default="quran_i3rab_word_level.csv")
    args = ap.parse_args()

    with open(args.in_raw, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        rows = list(r)

    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["surah", "ayah", "word", "i3rab"])

        out_n = 0
        for row in rows:
            surah = int(row["surah"])
            ayah = int(row["ayah"])
            text = (row.get("text") or "").strip()
            i3rab = (row.get("i3rab") or "").strip()

            # basic tokenization (you can replace with your MASAQ tokenizer later)
            words = [x for x in text.split() if x]
            for wd in words:
                w.writerow([surah, ayah, wd, i3rab])
                out_n += 1

    print(f"[OK] wrote {out_n} rows -> {args.out}")

if __name__ == "__main__":
    main()
