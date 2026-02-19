#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import time
import argparse
import requests

BASE_DEFAULT = "https://api.belquran.com/fa-ir/api/v1"

def post_json(url: str, payload: dict, headers: dict, timeout=60):
    r = requests.post(url, json=payload, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.json()

def download_index(base: str, headers: dict, out_index_csv: str):
    """
    Creates ayah index with: surah, ayah, ayehId, text
    Uses:
      - /Quran/ListSurah
      - /Quran/QuranFromSurahId  (AyehNumber=1 to get full surah)
    """
    list_surah_url = f"{base}/Quran/ListSurah"
    quran_from_surah_url = f"{base}/Quran/QuranFromSurahId"

    surahs = post_json(list_surah_url, {}, headers=headers)

    # Be tolerant: sometimes response is {"surah":[...]} or direct list
    if isinstance(surahs, dict):
        surah_list = surahs.get("surah") or surahs.get("surahs") or surahs.get("data") or []
    else:
        surah_list = surahs

    if not surah_list:
        raise RuntimeError("ListSurah returned empty result. Check API key/header.")

    rows = []
    for s in surah_list:
        surah_id = s.get("surahId") or s.get("sorehId") or s.get("id")
        if not surah_id:
            continue

        data = post_json(
            quran_from_surah_url,
            {"Soreh": int(surah_id), "AyehNumber": 1},
            headers=headers,
        )

        qlist = data.get("quran") if isinstance(data, dict) else data
        if not qlist:
            continue

        for a in qlist:
            ayeh_id = a.get("ayehId")
            ayah_no = a.get("ayehNumber")
            surah_no = a.get("surahId") or int(surah_id)
            text = (a.get("content") or "").strip()

            if ayeh_id and ayah_no and surah_no:
                rows.append([int(surah_no), int(ayah_no), int(ayeh_id), text])

        # be nice to API
        time.sleep(0.2)

    rows.sort(key=lambda x: (x[0], x[1]))

    with open(out_index_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["surah", "ayah", "ayehId", "text"])
        w.writerows(rows)

    return len(rows)

def download_i3rab(base: str, headers: dict, index_csv: str, out_raw_csv: str, erab_book_id: int, sleep_s=0.2):
    """
    Downloads i3rab for each ayahId -> saves ayah-level i3rab (tafsir text).
    Uses: /Erabs/ErabAyeh with {"AyehId":..., "ModeErabBook":...}
    """
    erab_url = f"{base}/Erabs/ErabAyeh"

    with open(index_csv, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        idx = list(r)

    with open(out_raw_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["surah", "ayah", "ayehId", "text", "i3rab"])
        ok = 0

        for row in idx:
            surah = int(row["surah"])
            ayah = int(row["ayah"])
            ayeh_id = int(row["ayehId"])
            text = row["text"]

            data = post_json(erab_url, {"AyehId": ayeh_id, "ModeErabBook": erab_book_id}, headers=headers)
            # docs: output has "tafsir" as string
            i3rab = ""
            if isinstance(data, dict):
                i3rab = (data.get("tafsir") or data.get("erab") or "").strip()
            else:
                i3rab = str(data)

            w.writerow([surah, ayah, ayeh_id, text, i3rab])
            ok += 1

            if ok % 50 == 0:
                print(f"[DL] downloaded {ok}/{len(idx)}")

            time.sleep(sleep_s)

    return ok

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api-key", default=os.getenv("BELQURAN_KEY", "").strip(), help="BelQuran API key (or env BELQURAN_KEY)")
    ap.add_argument("--base", default=os.getenv("BELQURAN_BASE", BASE_DEFAULT), help="API base URL")
    ap.add_argument("--erab-book-id", type=int, default=int(os.getenv("BELQURAN_ERAB_BOOK", "22")), help="ModeErabBook id (default 22)")
    ap.add_argument("--out-index", default="ayah_index.csv")
    ap.add_argument("--out-raw", default="raw_i3rab_ayah.csv")
    ap.add_argument("--sleep", type=float, default=0.2)
    args = ap.parse_args()

    if not args.api_key:
        raise SystemExit("ERROR: missing API key. Provide --api-key or set BELQURAN_KEY env var.")

    # docs show header key used as 'key'
    headers = {"key": args.api_key}

    print("[1] Downloading ayah index...")
    n = download_index(args.base, headers, args.out_index)
    print(f"[OK] ayah_index rows = {n} -> {args.out_index}")

    print("[2] Downloading i3rab (ayah-level)...")
    m = download_i3rab(args.base, headers, args.out_index, args.out_raw, args.erab_book_id, args.sleep)
    print(f"[OK] raw_i3rab_ayah rows = {m} -> {args.out_raw}")

if __name__ == "__main__":
    main()
