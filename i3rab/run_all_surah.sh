#!/usr/bin/env bash
set -euo pipefail

# Work from the script directory (i3rab/)
cd "$(dirname "$0")"

PY="./i3rab_download_clean.py"
DB="./quran_i3rab_mushakkal_with_confirmed_fallback.csv"
OUT="./quran_i3rab_out.csv"

# sanity checks
[[ -f "$PY" ]] || { echo "[ERROR] Missing $PY"; exit 2; }
[[ -f "$DB" ]] || { echo "[ERROR] Missing $DB"; exit 2; }

# start fresh
rm -f "$OUT"

for s in $(seq 1 114); do
  echo "===== SURAH $s ====="
  python3 "$PY" \
    --mode from_csv \
    --db "$DB" \
    --surah "$s" \
    --out "$OUT" \
    --print-each-ayah
done

echo "DONE: all surah 1..114 -> $OUT"
