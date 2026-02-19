#!/usr/bin/env bash
set -e

PY="/Users/husseinhiyassat/fractal/Eqratech_Hussein_Hiyassat_Project/i3rab_download_clean.py"
DB="/Users/husseinhiyassat/clean_code__morphology_pipeline/quran_i3rab_mushakkal_with_confirmed_fallback.csv"
OUT="quran_i3rab_out.csv"

# استخرج السور الموجودة فعلاً داخل DB (فقط أرقام)
SURAH_LIST=$(python3 - <<'PY'
import csv, sys
db = "/Users/husseinhiyassat/clean_code__morphology_pipeline/quran_i3rab_mushakkal_with_confirmed_fallback.csv"

# رفع حد حجم الحقل لتجنب field larger than limit
for lim in (10_000_000, 50_000_000, 200_000_000, sys.maxsize):
    try:
        csv.field_size_limit(lim); break
    except OverflowError:
        pass

surahs=set()
with open(db, "r", encoding="utf-8", newline="") as f:
    r=csv.reader(f)
    for row in r:
        if not row: 
            continue
        try:
            s=int(row[0].strip().lstrip("\ufeff"))
        except:
            continue
        surahs.add(s)

print(" ".join(map(str, sorted(surahs))))
PY
)

echo "Surahs found in DB:"
echo "$SURAH_LIST"
echo

for s in $SURAH_LIST; do
  echo "===== SURAH $s ====="
  python3 "$PY" \
    --mode from_csv \
    --db "$DB" \
    --surah "$s" \
    --out "$OUT" \
    --print-each-ayah
done

echo "DONE: processed existing surahs only."
