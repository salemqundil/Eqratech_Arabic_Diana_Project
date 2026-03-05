#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# 1) ضع مفتاحك هنا أو صدّره بالـ env
: "${BELQURAN_KEY:?Set BELQURAN_KEY first}"

# (اختياري)
export BELQURAN_BASE="${BELQURAN_BASE:-https://api.belquran.com/fa-ir/api/v1}"
export BELQURAN_ERAB_BOOK="${BELQURAN_ERAB_BOOK:-22}"

echo "[STEP 1] Download from source -> ayah_index.csv + raw_i3rab_ayah.csv"
python3 ./download_belquran_i3rab.py \
  --out-index ./ayah_index.csv \
  --out-raw   ./raw_i3rab_ayah.csv

echo "[STEP 2] Clean/normalize -> quran_i3rab_word_level.csv"
python3 ./clean_to_word_csv.py \
  --in-raw ./raw_i3rab_ayah.csv \
  --out    ./quran_i3rab_word_level.csv

echo "DONE ✅"
