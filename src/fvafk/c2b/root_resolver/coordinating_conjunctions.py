#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Arabic Wazn Matcher (Gate / Window Matching)
-------------------------------------------
الموقع: src/fvafk/c2b/root_resolver/wazn_matcher.py
منقول من: data/arabic_wazn_matcher_gate.py

الاستخدام كموديول (للـ root_resolver):
    from fvafk.c2b.root_resolver.wazn_matcher import (
        try_match_pattern_to_word,
        best_hit,
        load_patterns,
        split_units,
        MatchHit,
    )

الاستخدام كـ CLI للتقييم (من جذر المشروع):
    python -m fvafk.c2b.root_resolver.wazn_matcher \\
        --patterns data/awzan_enhanced-atwah.csv \\
        --pairs    data/awzan_claude.csv \\
        --out_csv  out/awzan_results.csv \\
        --out_txt  out/awzan_analysis.txt

Key rule:
- Do NOT accept a pattern unless it contains placeholders ف ثم ع ثم ل in order.
- Matching supports:
  * FULLMATCH if pattern_units == word_units
  * WINDOW if pattern_units < word_units (substring sliding window)
- Placeholders (ف/ع/ل) match any base letter, but diacritics still checked.

Ranking (to pick predicted Top-1 from matches):
1) FULLMATCH preferred over WINDOW
2) Longer effective length preferred
3) More fixed letters preferred (non placeholders)
4) More diacritics specified preferred (vowels + shadda)
"""

import csv
import os
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


# -----------------------------
# Config (adjust if you want)
# -----------------------------
REQUIRE_FAL_ORDER_IN_PATTERN = True  # enforce ف ثم ع ثم ل inside pattern
MIN_PATTERN_UNITS = 3               # drop tiny patterns
SUBSTRING_MATCHING = True           # allow window matching
ALLOW_MISSING_WORD_VOWELS = True    # if word lacks vowel where pattern has one, allow
IGNORE_LAST_VOWEL = False
IGNORE_TANWIN = False


# -----------------------------
# Arabic diacritics
# -----------------------------
FATHATAN = "\u064B"
DAMMATAN = "\u064C"
KASRATAN = "\u064D"
FATHA = "\u064E"
DAMMA = "\u064F"
KASRA = "\u0650"
SHADDA = "\u0651"
SUKUN = "\u0652"
DAGGER_ALIF = "\u0670"

TANWIN = {FATHATAN, DAMMATAN, KASRATAN}
VOWELS = {FATHA, DAMMA, KASRA, SUKUN}
DIACRITICS = set().union(TANWIN, VOWELS, {SHADDA, DAGGER_ALIF})

PLACEHOLDERS = {"ف", "ع", "ل"}


@dataclass(frozen=True)
class Unit:
    base: str
    diacs: Tuple[str, ...]  # sorted, deterministic


def _sorted_tuple(s):
    return tuple(sorted(s))


def remove_al_and_shadda(word: str) -> str:
    """
    إزالة 'ال' التعريف والشدة من الكلمة.
    إذا كانت الكلمة تبدأ بـ 'ال'، نزيل 'ال' وإذا كان الحرف التالي مشدد، نزيل الشدة.
    """
    if word.startswith('ال'):
        # إزالة 'ال'
        remaining = word[2:]
        # البحث عن الشدة بعد 'ال'
        # في "السُّفَهَاءُ": بعد 'ال' يأتي 'س' ثم حركة ثم 'ّ' (شدة)
        chars = list(remaining)
        if len(chars) >= 2:
            # البحث عن الشدة في المواضع 1 أو 2 بعد الحرف الأول
            for i in range(1, min(3, len(chars))):
                if chars[i] == SHADDA:
                    # إزالة الشدة
                    new_chars = chars[:i] + chars[i+1:]
                    remaining = ''.join(new_chars)
                    break
        return remaining
    return word


def split_units(text: str) -> List[Unit]:
    """
    Split Arabic text into (base_letter + diacritics) units.
    Example: 'كَتَبَ' -> [ك+َ, ت+َ, ب+َ]
    """
    units: List[Unit] = []
    cur_base: Optional[str] = None
    cur_diacs = []

    for ch in text:
        if ch in DIACRITICS:
            if cur_base is None:
                # leading diacritic: ignore
                continue
            cur_diacs.append(ch)
        else:
            # flush previous
            if cur_base is not None:
                units.append(Unit(cur_base, _sorted_tuple(cur_diacs)))
            cur_base = ch
            cur_diacs = []

    if cur_base is not None:
        units.append(Unit(cur_base, _sorted_tuple(cur_diacs)))

    return units


def has_fal_order_in_pattern(pattern: str) -> bool:
    """Require ف then ع then ل in order inside pattern text (by base letters)."""
    bases = [u.base for u in split_units(pattern)]
    try:
        i_f = bases.index("ف")
        i_a = bases.index("ع", i_f + 1)
        i_l = bases.index("ل", i_a + 1)
        return True
    except ValueError:
        return False


def pattern_effective_len(units: List[Unit]) -> int:
    """
    "Effective length" to reward shadda complexity a bit:
    length + count(shadda in any unit)
    """
    shadda_count = sum(1 for u in units if SHADDA in u.diacs)
    return len(units) + shadda_count


def count_fixed_letters(units: List[Unit]) -> int:
    return sum(1 for u in units if u.base not in PLACEHOLDERS)


def count_specified_diacritics(units: List[Unit]) -> int:
    # count vowels + tanwin + shadda occurrences (excluding dagger_alif if you prefer)
    c = 0
    for u in units:
        for d in u.diacs:
            if d in VOWELS or d in TANWIN or d == SHADDA:
                c += 1
    return c


def unit_vowel(diacs: Tuple[str, ...]) -> Optional[str]:
    for d in diacs:
        if d in VOWELS:
            return d
    return None


def unit_tanwin(diacs: Tuple[str, ...]) -> Optional[str]:
    for d in diacs:
        if d in TANWIN:
            return d
    return None


def unit_has_shadda(diacs: Tuple[str, ...]) -> bool:
    return SHADDA in diacs


def normalize_units_for_options(units: List[Unit], ignore_last_vowel: bool, ignore_tanwin: bool) -> List[Unit]:
    if not units:
        return units
    out = []
    for idx, u in enumerate(units):
        diacs = set(u.diacs)
        if ignore_tanwin:
            diacs -= TANWIN
        if ignore_last_vowel and idx == len(units) - 1:
            diacs -= VOWELS
            diacs -= TANWIN  # optional: last tanwin often i3rab too
        out.append(Unit(u.base, _sorted_tuple(diacs)))
    return out


def units_match(p: Unit, w: Unit, allow_missing_word_vowels: bool) -> bool:
    # base letter
    if p.base in PLACEHOLDERS:
        base_ok = True
    else:
        base_ok = (p.base == w.base)
    if not base_ok:
        return False

    # shadda must match if specified in pattern
    p_sh = unit_has_shadda(p.diacs)
    w_sh = unit_has_shadda(w.diacs)
    if p_sh != w_sh:
        return False

    # vowel match (if pattern specifies)
    pv = unit_vowel(p.diacs)
    wv = unit_vowel(w.diacs)
    if pv is not None:
        if wv is None and allow_missing_word_vowels:
            pass
        else:
            if pv != wv:
                return False

    # tanwin match (if pattern specifies and not ignored)
    pt = unit_tanwin(p.diacs)
    wt = unit_tanwin(w.diacs)
    if pt is not None:
        if wt is None and allow_missing_word_vowels:
            pass
        else:
            if pt != wt:
                return False

    return True


@dataclass
class MatchHit:
    pattern: str
    reason: str            # FULLMATCH or WINDOW
    window_start: int      # 0 for fullmatch; otherwise index
    score_key: Tuple[int, int, int, int]  # for ranking


def try_match_pattern_to_word(pattern: str, word: str) -> List[MatchHit]:
    """
    Returns all hits (normally 0 or 1 hit per pattern).
    If WINDOW is enabled and multiple windows match, we keep the best window (earliest).
    """
    # معالجة 'ال' التعريف والشدة قبل المقارنة
    word_processed = remove_al_and_shadda(word)
    
    p_units = split_units(pattern)
    w_units = split_units(word_processed)

    # options normalization
    p_units = normalize_units_for_options(p_units, IGNORE_LAST_VOWEL, IGNORE_TANWIN)
    w_units = normalize_units_for_options(w_units, IGNORE_LAST_VOWEL, IGNORE_TANWIN)

    # gates
    if len(p_units) < MIN_PATTERN_UNITS:
        return []
    if REQUIRE_FAL_ORDER_IN_PATTERN and not has_fal_order_in_pattern(pattern):
        return []

    lp = len(p_units)
    lw = len(w_units)

    fixed = count_fixed_letters(p_units)
    diac_spec = count_specified_diacritics(p_units)
    eff_len = pattern_effective_len(p_units)

    def make_score(reason: str) -> Tuple[int, int, int, int]:
        # FULLMATCH higher than WINDOW
        reason_rank = 2 if reason == "FULLMATCH" else 1
        return (reason_rank, eff_len, fixed, diac_spec)

    # longer than word -> reject
    if lp > lw:
        return []

    # equal -> fullmatch only
    if lp == lw:
        ok = True
        for i in range(lp):
            if not units_match(p_units[i], w_units[i], ALLOW_MISSING_WORD_VOWELS):
                ok = False
                break
        if ok:
            return [MatchHit(pattern, "FULLMATCH", 0, make_score("FULLMATCH"))]
        return []

    # shorter -> window matching if enabled
    if not SUBSTRING_MATCHING:
        return []

    best_start = None
    for start in range(0, lw - lp + 1):
        ok = True
        for i in range(lp):
            if not units_match(p_units[i], w_units[start + i], ALLOW_MISSING_WORD_VOWELS):
                ok = False
                break
        if ok:
            best_start = start
            break

    if best_start is None:
        return []

    return [MatchHit(pattern, "WINDOW", best_start, make_score("WINDOW"))]


def sniff_delimiter(path: str) -> str:
    with open(path, "r", encoding="utf-8", newline="") as f:
        sample = f.read(4096)
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=[",", "\t", ";", "|"])
        return dialect.delimiter
    except Exception:
        # fallback: detect tab in header
        if "\t" in sample.splitlines()[0]:
            return "\t"
        return ","


def read_rows(path: str) -> List[Dict[str, str]]:
    delim = sniff_delimiter(path)
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=delim)
        rows = [dict(r) for r in reader]

    # handle the "single column containing tabs" issue
    if rows and len(rows[0].keys()) == 1:
        only_key = next(iter(rows[0].keys()))
        if "\t" in only_key:
            headers = only_key.split("\t")
            fixed_rows = []
            with open(path, "r", encoding="utf-8", newline="") as f2:
                all_lines = f2.read().splitlines()
            for line in all_lines[1:]:
                parts = line.split("\t")
                parts += [""] * (len(headers) - len(parts))
                fixed_rows.append({headers[i]: parts[i] for i in range(len(headers))})
            return fixed_rows

    return rows


def pick_column(row: Dict[str, str], candidates: List[str]) -> Optional[str]:
    for c in candidates:
        if c in row and row[c] is not None and str(row[c]).strip() != "":
            return str(row[c]).strip()
    return None


def load_patterns(patterns_csv: str) -> List[str]:
    rows = read_rows(patterns_csv)
    patterns = []
    for r in rows:
        p = pick_column(r, ["الوزن", "wazn", "pattern", "Pattern"])
        if p:
            patterns.append(p)
    # de-dup preserve order
    seen = set()
    out = []
    for p in patterns:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def load_pairs(pairs_csv: str) -> List[Tuple[str, str]]:
    rows = read_rows(pairs_csv)
    pairs = []
    for r in rows:
        gold = pick_column(r, ["الوزن", "gold", "Gold", "wazn"])
        word = pick_column(r, ["مثال", "word", "Word", "example"])
        if gold and word:
            pairs.append((word, gold))
    return pairs


def best_hit(hits: List[MatchHit]) -> Optional[MatchHit]:
    if not hits:
        return None
    # max by score_key, tie -> longer raw pattern string, then lexical
    hits_sorted = sorted(
        hits,
        key=lambda h: (h.score_key, len(h.pattern), h.pattern),
        reverse=True
    )
    return hits_sorted[0]


def main():
    # Defaults: relative to project root (run with PYTHONPATH=src from repo root)
    import pathlib as _pathlib
    _project_root = _pathlib.Path(__file__).parent.parent.parent.parent.parent
    patterns_csv = str(_project_root / "data" / "awzan_enhanced-atwah.csv")
    pairs_csv    = str(_project_root / "data" / "awzan_claude.csv")
    out_csv      = str(_project_root / "out"  / "awzan_match_results.csv")
    out_txt      = str(_project_root / "out"  / "awzan_match_analysis.txt")

    # allow CLI overrides
    argv = sys.argv[1:]
    for i, a in enumerate(argv):
        if a == "--patterns" and i + 1 < len(argv):
            patterns_csv = argv[i + 1]
        if a == "--pairs" and i + 1 < len(argv):
            pairs_csv = argv[i + 1]
        if a == "--out_csv" and i + 1 < len(argv):
            out_csv = argv[i + 1]
        if a == "--out_txt" and i + 1 < len(argv):
            out_txt = argv[i + 1]

    patterns = load_patterns(patterns_csv)
    pairs = load_pairs(pairs_csv)

    # Evaluate
    results_rows = []
    match_count_hist = Counter()
    accept_reasons = Counter()
    matched_patterns_freq = Counter()
    confusion = Counter()

    total = 0
    no_match = 0
    ambiguous = 0
    top1_correct = 0
    coverage_correct = 0

    valid_total = 0
    valid_no_match = 0
    valid_ambiguous = 0
    valid_top1_correct = 0
    valid_coverage_correct = 0

    invalid_gold_rows = []

    def gold_is_valid(g: str) -> bool:
        if len(split_units(g)) < MIN_PATTERN_UNITS:
            return False
        if REQUIRE_FAL_ORDER_IN_PATTERN and not has_fal_order_in_pattern(g):
            return False
        return True

    for word, gold in pairs:
        total += 1
        gold_valid = gold_is_valid(gold)
        if gold_valid:
            valid_total += 1
        else:
            invalid_gold_rows.append((word, gold))

        hits_all: List[MatchHit] = []
        matches_set = []
        reasons_map = {}

        for p in patterns:
            hits = try_match_pattern_to_word(p, word)
            if hits:
                hit = hits[0]
                hits_all.append(hit)
                matches_set.append(p)
                reasons_map[p] = hit.reason
                accept_reasons[hit.reason] += 1
                matched_patterns_freq[p] += 1

        matches_count = len(matches_set)
        match_count_hist[matches_count] += 1

        if matches_count == 0:
            no_match += 1
            if gold_valid:
                valid_no_match += 1
        elif matches_count > 1:
            ambiguous += 1
            if gold_valid:
                valid_ambiguous += 1

        gold_in = "YES" if gold in matches_set else "NO"
        if gold in matches_set:
            coverage_correct += 1
            if gold_valid:
                valid_coverage_correct += 1

        best = best_hit(hits_all)
        predicted = best.pattern if best else ""
        pred_reason = best.reason if best else ""
        pred_score = best.score_key if best else None

        is_top1 = (predicted == gold) and (predicted != "")
        if is_top1:
            top1_correct += 1
            if gold_valid:
                valid_top1_correct += 1
        if best and gold in matches_set:
            confusion[(gold, predicted)] += 1

        # store sorted matches by ranking to help you see "longest wins" effect
        ranked = sorted(
            hits_all,
            key=lambda h: (h.score_key, len(h.pattern), h.pattern),
            reverse=True
        )
        ranked_patterns = [h.pattern for h in ranked]

        results_rows.append({
            "word": word,
            "gold": gold,
            "matches_count": str(matches_count),
            "matches": " | ".join(ranked_patterns),
            "gold_in_matches": gold_in,
            "predicted": predicted,
            "predicted_reason": pred_reason,
            "predicted_score": str(pred_score),
            "top1_correct": "YES" if is_top1 else "NO",
            "gold_valid": "YES" if gold_valid else "NO",
        })

    # Write results CSV
    fieldnames = [
        "word", "gold", "gold_valid",
        "matches_count", "matches", "gold_in_matches",
        "predicted", "predicted_reason", "predicted_score",
        "top1_correct"
    ]
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in results_rows:
            w.writerow(r)

    # Build analysis report
    def pct(a: int, b: int) -> float:
        return (a / b) if b else 0.0

    lines = []
    lines.append("تحليل نتائج مطابقة الأوزان (بوابات الوزن داخل الكلمة)")
    lines.append("=" * 78)
    lines.append(f"patterns_csv: {patterns_csv}")
    lines.append(f"pairs_csv:    {pairs_csv}")
    lines.append(f"Total rows:   {total}")
    lines.append(f"Total patterns loaded: {len(patterns)}")
    lines.append("")
    lines.append("--- Gates / Options ---")
    lines.append(f"- REQUIRE_FAL_ORDER_IN_PATTERN: {REQUIRE_FAL_ORDER_IN_PATTERN}")
    lines.append(f"- MIN_PATTERN_UNITS: {MIN_PATTERN_UNITS}")
    lines.append(f"- SUBSTRING_MATCHING: {SUBSTRING_MATCHING}")
    lines.append(f"- ALLOW_MISSING_WORD_VOWELS: {ALLOW_MISSING_WORD_VOWELS}")
    lines.append(f"- IGNORE_LAST_VOWEL: {IGNORE_LAST_VOWEL}")
    lines.append(f"- IGNORE_TANWIN: {IGNORE_TANWIN}")
    lines.append("")
    lines.append("-" * 78)
    lines.append("OVERALL METRICS")
    lines.append(f"- No match: {no_match}")
    lines.append(f"- Ambiguous (>1 match): {ambiguous}")
    lines.append(f"- Top-1 Accuracy: {pct(top1_correct, total):.4f} ({top1_correct}/{total})")
    lines.append(f"- Coverage Accuracy (gold in matches): {pct(coverage_correct, total):.4f} ({coverage_correct}/{total})")
    lines.append("")
    lines.append("-" * 78)
    lines.append("VALID-ONLY METRICS (rows where gold passes FAL+min_units)")
    lines.append(f"- Valid rows: {valid_total}")
    lines.append(f"- No match: {valid_no_match}")
    lines.append(f"- Ambiguous (>1 match): {valid_ambiguous}")
    lines.append(f"- Top-1 Accuracy: {pct(valid_top1_correct, valid_total):.4f} ({valid_top1_correct}/{valid_total})")
    lines.append(f"- Coverage Accuracy: {pct(valid_coverage_correct, valid_total):.4f} ({valid_coverage_correct}/{valid_total})")
    lines.append("")
    lines.append("-" * 78)
    lines.append("MATCH COUNT HISTOGRAM")
    for k in sorted(match_count_hist.keys()):
        lines.append(f"- {k}: {match_count_hist[k]}")
    lines.append("")
    lines.append("-" * 78)
    lines.append("ACCEPT REASONS COUNTS")
    for k, v in accept_reasons.most_common():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("-" * 78)
    lines.append("TOP MATCHED PATTERNS (ambiguity drivers) - top 30")
    for p, v in matched_patterns_freq.most_common(30):
        lines.append(f"- {p}: {v}")
    lines.append("")
    lines.append("-" * 78)
    lines.append("TOP CONFUSIONS (gold -> predicted) - top 30")
    for (g, pr), v in confusion.most_common(30):
        if g != pr:
            lines.append(f"- {g} -> {pr}: {v}")
    lines.append("")
    lines.append("-" * 78)
    lines.append("ROWS WITH INVALID GOLD (gold does NOT pass FAL+min_units) - sample")
    for word, gold in invalid_gold_rows[:80]:
        lines.append(f"- {word} | gold={gold}")
    lines.append("")

    with open(out_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # Minimal terminal output (as you requested)
    print(f"[OK] Wrote results: {out_csv}")
    print(f"[OK] Wrote analysis: {out_txt}")


if __name__ == "__main__":
    main()

