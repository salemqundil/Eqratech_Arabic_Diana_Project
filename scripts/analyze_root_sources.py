#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze root source distribution in CSV produced by run_ayat_full_quran.py (with --show-root-source).
Optionally compare unique predicted roots to Tanzil's root list.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


def _norm_root(r: str) -> str:
    return (r or "").replace("-", "").strip()


def canonical_root(r: str) -> str:
    """Normalize root for set-level comparison (alef variants, alef maqsura)."""
    r = _norm_root(r)
    if not r:
        return r
    r = r.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    r = r.replace("ى", "ي")
    if len(r) == 3 and r[0] == "ا":
        r = "ء" + r[1:]
    return r


def _load_tanzil_root_set(path: str) -> set:
    roots = set()
    with open(path, encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rt = _norm_root(row.get("root", ""))
            if rt:
                roots.add(rt)
    return roots


def _pct(n: int, d: int) -> int:
    return int(round((n / d) * 100)) if d else 0


def _bar(pct: int, width: int = 12) -> str:
    filled = int(round((pct / 100) * width))
    return "█" * filled


@dataclass
class Sample:
    word: str
    sura: str
    aya: str
    root: str
    stripped: str
    kind: str
    source: str
    confidence: float
    reason: str


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="out_with_sources.csv", help="CSV from run_ayat_full_quran.py --show-root-source")
    ap.add_argument("--samples", type=int, default=5, help="Sample rows per source bucket")
    ap.add_argument("--tanzil", default="data/tanzil_roots.csv", help="Tanzil roots CSV for set comparison")
    ap.add_argument("--no-tanzil-normalize", action="store_true", help="Disable canonicalization when comparing to Tanzil")
    ap.add_argument("--top-missing", type=int, default=30, help="Top N predicted roots missing in Tanzil to show")
    args = ap.parse_args()

    path = Path(args.input)
    if not path.exists():
        print(f"Input file not found: {path.resolve()}", flush=True)
        return 1

    total = 0
    with_root = 0
    no_root = 0
    by_source = Counter()
    by_kind = Counter()
    samples_by_source = defaultdict(list)
    low_conf = []
    pred_root_counter = Counter()

    with open(path, encoding="utf-8") as f:
        r = csv.DictReader(f)
        cols = r.fieldnames or []
        if "root" not in cols:
            print(f"{path} must contain column 'root'. Found: {cols}")
            return 1
        for row in r:
            total += 1
            sura = row.get("sura", "")
            aya = row.get("aya", "")
            word = row.get("word", "")
            stripped = row.get("stripped", row.get("normalized", ""))
            kind = row.get("kind", row.get("type", "unknown"))
            source = row.get("root_source", "unknown")
            reason = row.get("isnadi_reason", row.get("root_reason", ""))
            root_raw = row.get("root", "")
            root = _norm_root(root_raw)
            try:
                confidence = float(row.get("root_confidence", "") or "0")
            except ValueError:
                confidence = 0.0
            by_kind[kind] += 1
            by_source[source] += 1
            if root:
                with_root += 1
                pred_root_counter[root] += 1
            else:
                no_root += 1
            s = Sample(word=word, sura=sura, aya=aya, root=root_raw if root_raw else "—", stripped=stripped, kind=kind, source=source, confidence=confidence, reason=reason)
            if len(samples_by_source[source]) < args.samples:
                samples_by_source[source].append(s)
            if 0 < confidence < 0.3 and len(low_conf) < 200:
                low_conf.append(s)

    print("=" * 65)
    print("  تقرير مصادر الجذر — Root Source Report")
    print("=" * 65)
    print()
    print(f"  المجموع الكلي : {total} كلمة")
    print(f"  عندها جذر    : {with_root}  ({_pct(with_root, total)}%)")
    print(f"  بدون جذر     : {no_root}  ({_pct(no_root, total)}%)")
    print()
    print("  توزيع المصادر:")
    for src, cnt in by_source.most_common():
        pct = _pct(cnt, total)
        print(f"    {src:18s} {cnt:6d}  ({pct:3d}%)  {_bar(pct)}")
    print()
    print("  توزيع الأنواع:")
    for k, cnt in by_kind.most_common():
        print(f"    {k:20s} {cnt:6d}")

    for src, cnt in by_source.most_common():
        print(f"\n  المصدر: {src}  ({cnt} كلمة)")
        for i, s in enumerate(samples_by_source.get(src, [])[: args.samples], start=1):
            print(f"  [{i}] الكلمة : {s.word}  ({s.sura}:{s.aya})")
            print(f"       الجذر   : {s.root}")
            print(f"       المصدر  : {s.source}  (conf={s.confidence:.2f})")
            if s.stripped:
                print(f"       stripped: {s.stripped}")
            if s.kind:
                print(f"       النوع   : {s.kind}")
        print()

    if low_conf:
        print("─" * 65)
        print(f"  ⚠️  حالات بـ confidence منخفض (< 0.3) — {len(low_conf)} كلمة")
        for i, s in enumerate(low_conf[: args.samples], start=1):
            print(f"  [{i}] الكلمة : {s.word}  ({s.sura}:{s.aya})  الجذر: {s.root}  {s.source} (conf={s.confidence:.2f})")
        print()

    tanzil_path = Path(args.tanzil)
    if tanzil_path.exists():
        tanzil_root_set = _load_tanzil_root_set(str(tanzil_path))
        pred_root_set = set(pred_root_counter.keys())
        both = pred_root_set & tanzil_root_set
        pred_only = pred_root_set - tanzil_root_set
        tanzil_only = tanzil_root_set - pred_root_set
        print("=" * 65)
        print("  Unique Roots vs Tanzil (set-level)")
        print("=" * 65)
        print(f"  Tanzil roots file : {args.tanzil}")
        print(f"  Unique predicted roots (non-empty): {len(pred_root_set)}")
        print(f"  Unique tanzil roots:               {len(tanzil_root_set)}")
        print(f"  Intersection (in both):            {len(both)}")
        print(f"  Pred-only (missing in tanzil):     {len(pred_only)}")
        print(f"  Tanzil-only (missing in ours):     {len(tanzil_only)}")
        if not args.no_tanzil_normalize:
            pred_canonical = {canonical_root(r) for r in pred_root_set if r}
            tanzil_canonical = {canonical_root(r) for r in tanzil_root_set if r}
            both_c = pred_canonical & tanzil_canonical
            pred_only_c = pred_canonical - tanzil_canonical
            tanzil_only_c = tanzil_canonical - pred_canonical
            print("\n  Overlap after canonicalization:")
            print(f"  Intersection (canonical):       {len(both_c)}")
            print(f"  Pred-only (canonical):          {len(pred_only_c)}")
            print(f"  Tanzil-only (canonical):        {len(tanzil_only_c)}")
        if args.top_missing and pred_only:
            print("\n  Top predicted roots missing in Tanzil (by frequency):")
            for root, cnt in pred_root_counter.most_common():
                if root in pred_only:
                    print(f"    {root:10s}  count={cnt}")
                    args.top_missing -= 1
                    if args.top_missing <= 0:
                        break
        print("\n" + "=" * 65)
    else:
        print(f"\n  (Tanzil file not found: {tanzil_path}; skipping set comparison)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
