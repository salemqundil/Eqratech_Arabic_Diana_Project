#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import csv
import os
import random
import time
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple


def _set_csv_field_limit():
    for limit in (10_000_000, 50_000_000, 200_000_000):
        try:
            csv.field_size_limit(limit)
            return
        except Exception:
            continue


_set_csv_field_limit()


@dataclass(frozen=True)
class I3rabRow:
    surah: int
    ayah: int
    word: str
    i3rab: str
    scope: str = ""


OUT_HEADER = ["surah", "ayah", "word", "i3rab", "scope"]


def _strip_bom(s: str) -> str:
    return (s or "").lstrip("\ufeff").strip()


def is_int_str(s: str) -> bool:
    s = _strip_bom(s)
    if s == "":
        return False
    if s[0] in "+-":
        s = s[1:]
    return s.isdigit()


def polite_sleep(base: float = 0.5, jitter: float = 1.0) -> None:
    time.sleep(base + random.random() * jitter)


def ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)


# ✅ KEY DOES NOT INCLUDE scope
def make_key(r: I3rabRow) -> str:
    return f"{r.surah}|{r.ayah}|{r.word}|{r.i3rab}"


def _parse_out_row(row: List[str]) -> Optional[I3rabRow]:
    if not row or len(row) < 4:
        return None

    c0 = _strip_bom(row[0]).lower()
    if c0 == "surah":
        return None

    try:
        surah = int(_strip_bom(row[0]))
        ayah = int(_strip_bom(row[1]))
        word = row[2] if len(row) > 2 else ""
        i3rab = row[3] if len(row) > 3 else ""
        scope = row[4] if len(row) > 4 else ""
        return I3rabRow(surah=surah, ayah=ayah, word=word, i3rab=i3rab, scope=scope)
    except Exception:
        return None


def load_existing_keys(out_csv: str) -> set[str]:
    keys: set[str] = set()
    if not out_csv or not os.path.exists(out_csv):
        return keys

    with open(out_csv, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        first = next(reader, None)
        if first is None:
            return keys

        is_headered = (len(first) >= 4 and _strip_bom(first[0]).lower() == "surah")
        if not is_headered:
            r0 = _parse_out_row(first)
            if r0:
                keys.add(make_key(r0))

        for row in reader:
            r = _parse_out_row(row)
            if r:
                keys.add(make_key(r))

    return keys


def append_rows(out_csv: str, rows: List[I3rabRow], write_header_if_new: bool = True) -> int:
    if not rows:
        return 0

    ensure_parent_dir(out_csv)
    file_exists = os.path.exists(out_csv)

    with open(out_csv, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)

        if write_header_if_new and (not file_exists or os.path.getsize(out_csv) == 0):
            writer.writerow(OUT_HEADER)

        for r in rows:
            writer.writerow([r.surah, r.ayah, r.word, r.i3rab, r.scope])

    return len(rows)


def detect_db_format(first_row: List[str]) -> Tuple[bool, Dict[str, int]]:
    if not first_row:
        raise ValueError("DB CSV is empty")

    first_cell = _strip_bom(first_row[0])
    is_headerless = is_int_str(first_cell)

    if is_headerless:
        col = {"surah": 0, "ayah": 1, "word": 2, "i3rab": 3}
        if len(first_row) >= 5:
            col["scope"] = 4
        return True, col

    header = [_strip_bom(c).lower() for c in first_row]
    aliases = {
        "surah": {"surah", "sura", "surah_no", "sura_no", "chapter", "chapter_no"},
        "ayah": {"ayah", "aya", "ayah_no", "verse", "verse_no"},
        "word": {"word", "token", "text", "term"},
        "i3rab": {"i3rab", "irab", "e3rab", "analysis", "parse"},
        "scope": {"scope", "level", "type", "kind", "source", "src"},
    }

    idx: Dict[str, int] = {}
    for need, names in aliases.items():
        for i, h in enumerate(header):
            if h in names:
                idx[need] = i
                break

    required = {"surah", "ayah", "word", "i3rab"}
    if required.issubset(idx.keys()):
        return False, idx

    # fallback: treat as headerless
    col = {"surah": 0, "ayah": 1, "word": 2, "i3rab": 3}
    if len(first_row) >= 5:
        col["scope"] = 4
    return True, col


def iter_db_rows_from_csv(db_csv: str) -> Iterable[I3rabRow]:
    abs_path = os.path.abspath(os.path.expanduser(db_csv))
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"DB CSV not found: {abs_path}")

    def ignorable(row: List[str]) -> bool:
        if not row:
            return True
        first = _strip_bom(row[0])
        return first == "" or first.startswith("#") or first.startswith("//")

    with open(abs_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)

        first: Optional[List[str]] = None
        for r in reader:
            if ignorable(r):
                continue
            first = r
            break

        if first is None:
            return

        is_headerless, col = detect_db_format(first)

        def parse_row(row: List[str]) -> Optional[I3rabRow]:
            if ignorable(row):
                return None
            try:
                s0 = _strip_bom(row[col["surah"]]) if col["surah"] < len(row) else ""
                a0 = _strip_bom(row[col["ayah"]]) if col["ayah"] < len(row) else ""
                if not is_int_str(s0) or not is_int_str(a0):
                    return None

                surah = int(s0)
                ayah = int(a0)
                word = row[col["word"]] if col["word"] < len(row) else ""
                i3rab = row[col["i3rab"]] if col["i3rab"] < len(row) else ""
                scope = ""
                if "scope" in col and col["scope"] < len(row):
                    scope = row[col["scope"]]
                return I3rabRow(surah=surah, ayah=ayah, word=word, i3rab=i3rab, scope=scope)
            except Exception:
                return None

        if is_headerless:
            r0 = parse_row(first)
            if r0:
                yield r0

        for r in reader:
            rr = parse_row(r)
            if rr:
                yield rr


def fetch_i3rab_for_surah_from_csv(db_csv: str, surah_no: int, ayah_from: int, ayah_to: int) -> List[I3rabRow]:
    rows: List[I3rabRow] = []
    for r in iter_db_rows_from_csv(db_csv):
        if r.surah != surah_no:
            continue
        if ayah_from and r.ayah < ayah_from:
            continue
        if ayah_to and r.ayah > ayah_to:
            continue
        rows.append(r)
    return rows


def fetch_i3rab_for_surah(surah_no: int) -> List[I3rabRow]:
    raise NotImplementedError("Plug your network fetcher here.")


def run_for_surah(
    *,
    mode: str,
    db_csv: Optional[str],
    surah_no: int,
    ayah_from: int,
    ayah_to: int,
    out_csv: str,
    dry_run: bool,
    print_each_ayah: bool,
    max_retries: int,
) -> int:
    known_keys = load_existing_keys(out_csv)
    print(f"[INFO] Output CSV: {out_csv}")
    print(f"[INFO] Starting surah: {surah_no}")
    print(f"[INFO] Mode: {mode}" + (f" (db={db_csv})" if mode == "from_csv" else ""))
    print(f"[INFO] Resume keys loaded: {len(known_keys)}")

    attempt = 0
    last_err: Optional[Exception] = None
    rows: List[I3rabRow] = []

    while attempt < max_retries:
        attempt += 1
        try:
            print(f"[FETCH] Surah {surah_no} (attempt {attempt}/{max_retries})")
            if mode == "from_csv":
                if not db_csv:
                    raise ValueError("--db is required in from_csv mode")
                rows = fetch_i3rab_for_surah_from_csv(db_csv, surah_no, ayah_from, ayah_to)
            else:
                rows = fetch_i3rab_for_surah(surah_no)
                if ayah_from or ayah_to:
                    rows = [
                        r for r in rows
                        if (not ayah_from or r.ayah >= ayah_from)
                        and (not ayah_to or r.ayah <= ayah_to)
                    ]
            last_err = None
            break
        except Exception as e:
            last_err = e
            print(f"[WARN] Fetch failed: {type(e).__name__}: {e}")
            polite_sleep(0.6, 1.2)

    if last_err is not None:
        print("[ERROR] Max retries reached. Aborting.")
        raise last_err

    if not rows:
        print(f"[DONE] No rows returned for surah {surah_no}.")
        return 0

    rows_sorted = sorted(rows, key=lambda r: (r.ayah, r.word))
    grouped: Dict[int, List[I3rabRow]] = {}
    for r in rows_sorted:
        grouped.setdefault(r.ayah, []).append(r)

    total_new = 0
    total_written = 0

    for ayah, ayah_rows in grouped.items():
        new_rows = [r for r in ayah_rows if make_key(r) not in known_keys]
        total_new += len(new_rows)

        if print_each_ayah:
            print(f"[AYAH] Surah {surah_no} | Ayah {ayah} | rows={len(ayah_rows)} | new={len(new_rows)}")

        if dry_run:
            continue

        if new_rows:
            written = append_rows(out_csv, new_rows)
            total_written += written
            for r in new_rows:
                known_keys.add(make_key(r))

    if dry_run:
        print(f"[DRY] Would append {total_new} new rows to {out_csv}")
        return total_new

    print(f"[OK] Appended {total_written} rows.")
    return total_written


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Download/Extract i3rab rows for a specific surah.")
    p.add_argument("--mode", choices=["fetch", "from_csv"], default="fetch")
    p.add_argument("--db", default=None)
    p.add_argument("--surah", type=int, required=True)
    p.add_argument("--out", default="i3rab_out.csv")
    p.add_argument("--ayah-from", type=int, default=0)
    p.add_argument("--ayah-to", type=int, default=0)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--print-each-ayah", action="store_true")
    p.add_argument("--max-retries", type=int, default=4)
    return p


def main() -> int:
    args = build_arg_parser().parse_args()

    if args.surah < 1 or args.surah > 114:
        print("[ERROR] --surah must be between 1 and 114")
        return 2

    if args.ayah_from and args.ayah_to and args.ayah_from > args.ayah_to:
        print("[ERROR] --ayah-from cannot be greater than --ayah-to")
        return 2

    return run_for_surah(
        mode=args.mode,
        db_csv=args.db,
        surah_no=args.surah,
        ayah_from=args.ayah_from,
        ayah_to=args.ayah_to,
        out_csv=args.out,
        dry_run=args.dry_run,
        print_each_ayah=args.print_each_ayah,
        max_retries=args.max_retries,
    )


if __name__ == "__main__":
    raise SystemExit(main())
