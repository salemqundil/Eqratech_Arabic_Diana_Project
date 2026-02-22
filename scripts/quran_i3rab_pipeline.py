#!/usr/bin/env python3
"""
Quran I3rab (Morphological Analysis) Data Pipeline
===================================================
Phase 1: Download raw HTML for all 114 surahs from surahquran.com
Phase 2: Parse + normalize + export to CSV

Usage:
  python quran_i3rab_pipeline.py download        # Phase 1: Download all surahs
  python quran_i3rab_pipeline.py parse           # Phase 2: Parse & export CSV
  python quran_i3rab_pipeline.py all             # Both phases
  python quran_i3rab_pipeline.py status          # Show download status
"""

import os
import sys
import json
import time
import re
import csv
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Try to import requests; install if missing
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing required packages...")
    os.system("pip install requests beautifulsoup4 lxml --break-system-packages -q")
    import requests
    from bs4 import BeautifulSoup

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
BASE_URL = "https://surahquran.com/i3rab-surah-{surah}.html"
PAGE_URL = "https://surahquran.com/i3rab-surah-{surah}.html?page={page}"
RAW_DIR = Path("quran_i3rab_raw")
OUTPUT_DIR = Path("quran_i3rab_output")
STATUS_FILE = RAW_DIR / "download_status.json"
CSV_OUTPUT = OUTPUT_DIR / "quran_i3rab.csv"
REPORT_FILE = OUTPUT_DIR / "coverage_report.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; QuranScraper/1.0; Educational)"
}
DELAY_BETWEEN_REQUESTS = 1.5  # seconds — be polite to the server
MAX_RETRIES = 3

# Expected ayah counts per surah (Hafs) — used to estimate page count
# 50 ayahs per page max observed
AYAHS_PER_PAGE = 50
SURAH_AYAH_COUNTS = [
    7,286,200,176,120,165,206,75,129,109,123,111,43,52,99,128,111,
    110,98,135,112,78,118,64,77,227,93,88,69,60,34,30,73,54,45,83,
    182,88,75,85,54,53,89,59,37,35,38,29,18,45,60,49,62,55,78,96,
    29,68,72,56,37,40,31,114,54,77,46,26,50,30,24,31,34,45,46,29,
    79,68,60,44,64,63,10,63,72,40,46,54,42,46,30,29,57,98,95,61,
    53,60,69,73,70,30,32,32,28,83,28,24,61,28,31,40,45,26,20,22,
    19,17,11,9
]

def get_page_count(surah_num: int) -> int:
    """Calculate how many pages a surah has based on ayah count."""
    import math
    ayahs = SURAH_AYAH_COUNTS[surah_num - 1]
    return math.ceil(ayahs / AYAHS_PER_PAGE)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pipeline.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# PHASE 1: DOWNLOADER
# ─────────────────────────────────────────────

def load_status() -> dict:
    """Load existing download status or return empty."""
    if STATUS_FILE.exists():
        with open(STATUS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_status(status: dict):
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False, indent=2)


def download_page(surah_num: int, page: int) -> tuple[bool, str, bytes]:
    """Download a single page of a surah. Returns (success, message, content)."""
    if page == 1:
        url = BASE_URL.format(surah=surah_num)
    else:
        url = PAGE_URL.format(surah=surah_num, page=page)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            return True, f"OK ({len(resp.content)} bytes)", resp.content
        except Exception as e:
            msg = str(e)
            if attempt < MAX_RETRIES:
                log.warning(f"Surah {surah_num} page {page} attempt {attempt} failed: {msg}. Retrying...")
                time.sleep(DELAY_BETWEEN_REQUESTS * 2)
            else:
                return False, msg, b""

    return False, "Max retries exceeded", b""


def download_surah(surah_num: int) -> tuple[bool, str]:
    """Download all pages of a surah and combine into one file."""
    num_pages = get_page_count(surah_num)
    raw_file = RAW_DIR / f"surah_{surah_num:03d}.html"
    combined_html = b""

    for page in range(1, num_pages + 1):
        success, msg, content = download_page(surah_num, page)
        if not success:
            return False, f"Page {page} failed: {msg}"
        combined_html += content
        log.info(f"    Page {page}/{num_pages}: {msg}")
        if page < num_pages:
            time.sleep(DELAY_BETWEEN_REQUESTS)

    raw_file.write_bytes(combined_html)
    return True, f"OK ({num_pages} pages, {len(combined_html)} bytes)"


def phase1_download(force: bool = False):
    """Download all 114 surahs (all pages) with resume support."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    status = load_status()

    pending = []
    for n in range(1, 115):
        key = str(n)
        raw_file = RAW_DIR / f"surah_{n:03d}.html"
        if force or key not in status or status[key]["success"] is False or not raw_file.exists():
            pending.append(n)

    log.info(f"Phase 1: {len(pending)} surahs to download (out of 114)")

    if not pending:
        log.info("All surahs already downloaded. Use --force to re-download.")
        return

    for i, surah_num in enumerate(pending, 1):
        num_pages = get_page_count(surah_num)
        log.info(f"[{i}/{len(pending)}] Downloading Surah {surah_num} ({num_pages} pages)...")
        success, msg = download_surah(surah_num)
        status[str(surah_num)] = {
            "success": success,
            "message": msg,
            "pages": num_pages,
            "timestamp": datetime.now().isoformat(),
        }
        if success:
            log.info(f"  ✓ Surah {surah_num}: {msg}")
        else:
            log.error(f"  ✗ Surah {surah_num}: {msg}")

        save_status(status)

        if i < len(pending):
            time.sleep(DELAY_BETWEEN_REQUESTS)

    # Summary
    total_ok = sum(1 for v in status.values() if v["success"])
    total_fail = sum(1 for v in status.values() if not v["success"])
    log.info(f"\nPhase 1 complete: {total_ok} success, {total_fail} failed")
    if total_fail:
        failed = [k for k, v in status.items() if not v["success"]]
        log.warning(f"Failed surahs: {failed}")


def show_status():
    """Show download status summary."""
    status = load_status()
    if not status:
        print("No download status found. Run: python quran_i3rab_pipeline.py download")
        return

    ok = [int(k) for k, v in status.items() if v["success"]]
    fail = [int(k) for k, v in status.items() if not v["success"]]
    missing = [n for n in range(1, 115) if str(n) not in status]

    print(f"\n{'='*50}")
    print(f"Download Status ({len(status)}/114 attempted)")
    print(f"{'='*50}")
    print(f"✓ Success : {len(ok)}/114")
    print(f"✗ Failed  : {len(fail)}")
    print(f"? Missing : {len(missing)}")
    if fail:
        print(f"\nFailed surahs: {sorted(fail)}")
    if missing:
        print(f"Not attempted: {sorted(missing)}")
    print()


# ─────────────────────────────────────────────
# PHASE 2: PARSER
# ─────────────────────────────────────────────

# Arabic curly brackets used to wrap words
WORD_OPEN = "﴿"
WORD_CLOSE = "﴾"

# Regex to find patterns like ﴿word﴾: i3rab_text
WORD_PATTERN = re.compile(
    rf"{re.escape(WORD_OPEN)}([^{re.escape(WORD_CLOSE)}]+){re.escape(WORD_CLOSE)}\s*[:：]\s*(.+?)(?=\s*{re.escape(WORD_OPEN)}|\s*$)",
    re.DOTALL,
)

# Ayah number: text like "(1)" or "( 1 )"
AYAH_NUM_PATTERN = re.compile(r"\(\s*(\d+)\s*\)")


def clean_text(text: str) -> str:
    """Normalize whitespace and remove unwanted chars."""
    if not text:
        return ""
    # Replace non-breaking spaces and other whitespace variants
    text = text.replace("\xa0", " ").replace("\u200c", "").replace("\u200d", "")
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_surah_html(surah_num: int, html_content: str) -> list[dict]:
    """
    Parse HTML of one surah page and extract word-level i3rab rows.
    Returns list of dicts: {surah, ayah, word, i3rab}
    """
    soup = BeautifulSoup(html_content, "lxml")
    rows = []

    # Find the main table containing ayahs
    # Each <tr><td> contains one ayah's text + i3rab
    table_cells = soup.find_all("td")

    for cell in table_cells:
        cell_text = cell.get_text(separator=" ")
        cell_text = clean_text(cell_text)

        if not cell_text:
            continue

        # Skip cells that don't contain Arabic brackets (not i3rab cells)
        if WORD_OPEN not in cell_text:
            continue

        # Extract ayah number from the cell
        ayah_match = AYAH_NUM_PATTERN.search(cell_text)
        if not ayah_match:
            # Try to find it in the link text or href
            link = cell.find("a")
            if link:
                link_text = link.get_text()
                ayah_match = AYAH_NUM_PATTERN.search(link_text)

        if not ayah_match:
            # Try to extract from URL
            link = cell.find("a")
            if link and link.get("href"):
                href = link.get("href", "")
                url_match = re.search(r"e3rab-aya-(\d+)-sora-\d+", href)
                if url_match:
                    ayah_num = int(url_match.group(1))
                else:
                    continue
            else:
                continue
        else:
            ayah_num = int(ayah_match.group(1))

        # Extract all ﴿word﴾: i3rab pairs
        word_matches = WORD_PATTERN.findall(cell_text)
        for word, i3rab in word_matches:
            word = clean_text(word)
            i3rab = clean_text(i3rab)
            if word and i3rab:
                rows.append({
                    "surah": surah_num,
                    "ayah": ayah_num,
                    "word": word,
                    "i3rab": i3rab,
                })

    return rows


def phase2_parse() -> list[dict]:
    """Parse all downloaded HTML files and return all rows."""
    status = load_status()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_rows = []
    surah_stats = {}  # surah_num -> {ayahs: set, words: int}

    for surah_num in range(1, 115):
        raw_file = RAW_DIR / f"surah_{surah_num:03d}.html"
        key = str(surah_num)

        if not raw_file.exists():
            log.warning(f"Surah {surah_num}: raw file not found, skipping")
            surah_stats[surah_num] = {"ayahs": set(), "words": 0, "status": "missing_file"}
            continue

        if key in status and not status[key]["success"]:
            log.warning(f"Surah {surah_num}: marked as failed download, skipping")
            surah_stats[surah_num] = {"ayahs": set(), "words": 0, "status": "failed_download"}
            continue

        html = raw_file.read_text(encoding="utf-8", errors="replace")
        rows = parse_surah_html(surah_num, html)

        if not rows:
            log.warning(f"Surah {surah_num}: no rows extracted!")
            surah_stats[surah_num] = {"ayahs": set(), "words": 0, "status": "parse_failed"}
            continue

        ayahs_found = {r["ayah"] for r in rows}
        surah_stats[surah_num] = {
            "ayahs": ayahs_found,
            "words": len(rows),
            "status": "ok",
        }
        all_rows.extend(rows)
        log.info(f"Surah {surah_num:3d}: {len(ayahs_found):3d} ayahs, {len(rows):4d} words")

    return all_rows, surah_stats


def write_csv(rows: list[dict]):
    """Write rows to CSV."""
    CSV_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(CSV_OUTPUT, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["surah", "ayah", "word", "i3rab"])
        writer.writeheader()
        writer.writerows(rows)
    log.info(f"CSV written: {CSV_OUTPUT} ({len(rows)} rows)")


def write_coverage_report(surah_stats: dict):
    """Generate a coverage report."""
    # Expected ayah counts per surah (standard Hafs)
    AYAH_COUNTS = [
        7,286,200,176,120,165,206,75,129,109,123,111,43,52,99,128,111,
        110,98,135,112,78,118,64,77,227,93,88,69,60,34,30,73,54,45,83,
        182,88,75,85,54,53,89,59,37,35,38,29,18,45,60,49,62,55,78,96,
        29,68,72,56,37,40,31,114,54,77,46,26,50,30,24,31,34,45,46,29,
        79,68,60,44,64,63,10,63,72,40,46,54,42,46,30,29,57,98,95,61,
        53,60,69,73,70,30,32,32,28,83,28,24,61,28,31,40,45,26,20,22,
        19,17,11,9,  # Fix below
    ]
    # Correct count (114 surahs)
    AYAH_COUNTS = [
        7,286,200,176,120,165,206,75,129,109,123,111,43,52,99,128,111,
        110,98,135,112,78,118,64,77,227,93,88,69,60,34,30,73,54,45,83,
        182,88,75,85,54,53,89,59,37,35,38,29,18,45,60,49,62,55,78,96,
        29,68,72,56,37,40,31,114,54,77,46,26,50,30,24,31,34,45,46,29,
        79,68,60,44,64,63,10,63,72,40,46,54,42,46,30,29,57,98,95,61,
        53,60,69,73,70,30,32,32,28,83,28,24,61,28,31,40,45,26,20,22,
        19,17,11,9
    ]

    lines = []
    lines.append("=" * 60)
    lines.append("QURAN I3RAB COVERAGE REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 60)

    ok_surahs = sum(1 for s in surah_stats.values() if s["status"] == "ok")
    total_words = sum(s["words"] for s in surah_stats.values())
    lines.append(f"\nSummary:")
    lines.append(f"  Surahs with data : {ok_surahs}/114")
    lines.append(f"  Total word rows  : {total_words:,}")

    lines.append("\nPer-Surah Details:")
    lines.append(f"{'Surah':>6} {'Expected':>9} {'Found':>7} {'Words':>7} {'Status'}")
    lines.append("-" * 55)

    problem_surahs = []
    for surah_num in range(1, 115):
        stats = surah_stats.get(surah_num, {"ayahs": set(), "words": 0, "status": "unknown"})
        expected = AYAH_COUNTS[surah_num - 1] if surah_num <= len(AYAH_COUNTS) else "?"
        found = len(stats["ayahs"])
        words = stats["words"]
        status = stats["status"]

        flag = ""
        if status != "ok":
            flag = " ⚠"
            problem_surahs.append(surah_num)
        elif isinstance(expected, int) and found < expected:
            flag = f" (missing {expected - found} ayahs)"
            problem_surahs.append(surah_num)

        lines.append(f"{surah_num:>6} {str(expected):>9} {found:>7} {words:>7}  {status}{flag}")

    if problem_surahs:
        lines.append(f"\n⚠ Problem surahs: {problem_surahs}")
    else:
        lines.append(f"\n✓ All surahs look complete!")

    report = "\n".join(lines)
    REPORT_FILE.write_text(report, encoding="utf-8")
    print(report)
    log.info(f"Coverage report saved: {REPORT_FILE}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Quran I3rab Data Pipeline")
    parser.add_argument("command", choices=["download", "parse", "all", "status"],
                        help="Command to run")
    parser.add_argument("--force", action="store_true",
                        help="Re-download even if already downloaded")
    parser.add_argument("--surah", type=int, default=None,
                        help="Process a single surah only (for testing)")
    args = parser.parse_args()

    if args.command == "status":
        show_status()

    elif args.command == "download":
        if args.surah:
            RAW_DIR.mkdir(parents=True, exist_ok=True)
            status = load_status()
            num_pages = get_page_count(args.surah)
            log.info(f"Downloading surah {args.surah} ({num_pages} pages)...")
            success, msg = download_surah(args.surah)
            status[str(args.surah)] = {"success": success, "message": msg,
                                        "pages": num_pages,
                                        "timestamp": datetime.now().isoformat()}
            save_status(status)
            print(f"{'✓' if success else '✗'} Surah {args.surah}: {msg}")
        else:
            phase1_download(force=args.force)

    elif args.command == "parse":
        all_rows, surah_stats = phase2_parse()
        if all_rows:
            write_csv(all_rows)
            write_coverage_report(surah_stats)
        else:
            log.error("No rows extracted! Check that Phase 1 (download) completed successfully.")

    elif args.command == "all":
        phase1_download(force=args.force)
        all_rows, surah_stats = phase2_parse()
        if all_rows:
            write_csv(all_rows)
            write_coverage_report(surah_stats)


if __name__ == "__main__":
    main()
