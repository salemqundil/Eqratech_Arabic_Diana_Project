"""
Arabic Wazn Matcher (Gate / Window Matching) — core only for root_resolver.
Exports: try_match_pattern_to_word, best_hit, split_units, load_patterns, MatchHit,
         remove_al_and_shadda, normalize_units_for_options, get_fal_indices.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Config
REQUIRE_FAL_ORDER_IN_PATTERN = True
MIN_PATTERN_UNITS = 3
SUBSTRING_MATCHING = True
ALLOW_MISSING_WORD_VOWELS = True
IGNORE_LAST_VOWEL = False
IGNORE_TANWIN = False

# Diacritics
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
    diacs: Tuple[str, ...]


def _sorted_tuple(s):
    return tuple(sorted(s))


def remove_al_and_shadda(word: str) -> str:
    if word.startswith("ال"):
        remaining = word[2:]
        chars = list(remaining)
        if len(chars) >= 2:
            for i in range(1, min(3, len(chars))):
                if chars[i] == SHADDA:
                    new_chars = chars[:i] + chars[i + 1 :]
                    remaining = "".join(new_chars)
                    break
        return remaining
    return word


def split_units(text: str) -> List[Unit]:
    units: List[Unit] = []
    cur_base: Optional[str] = None
    cur_diacs: List[str] = []

    for ch in text:
        if ch in DIACRITICS:
            if cur_base is None:
                continue
            cur_diacs.append(ch)
        else:
            if cur_base is not None:
                units.append(Unit(cur_base, _sorted_tuple(cur_diacs)))
            cur_base = ch
            cur_diacs = []

    if cur_base is not None:
        units.append(Unit(cur_base, _sorted_tuple(cur_diacs)))
    return units


def get_fal_indices(pattern: str) -> Optional[List[int]]:
    """
    Return indices of ف, ع, ل (and second ل if quadrilateral) in pattern units.
    Returns None if pattern does not have ف then ع then ل in order.
    """
    units = split_units(pattern)
    bases = [u.base for u in units]
    try:
        i_f = bases.index("ف")
        i_a = bases.index("ع", i_f + 1)
        i_l = bases.index("ل", i_a + 1)
        indices = [i_f, i_a, i_l]
        # Optional second ل for quadrilateral (فَعْلَلَ etc.)
        try:
            i_l2 = bases.index("ل", i_l + 1)
            indices.append(i_l2)
        except ValueError:
            pass
        return indices
    except ValueError:
        return None


def has_fal_order_in_pattern(pattern: str) -> bool:
    return get_fal_indices(pattern) is not None


def pattern_effective_len(units: List[Unit]) -> int:
    shadda_count = sum(1 for u in units if SHADDA in u.diacs)
    return len(units) + shadda_count


def count_fixed_letters(units: List[Unit]) -> int:
    return sum(1 for u in units if u.base not in PLACEHOLDERS)


def count_specified_diacritics(units: List[Unit]) -> int:
    c = 0
    for u in units:
        for d in u.diacs:
            if d in VOWELS or d in TANWIN or d == SHADDA:
                c += 1
    return c


def unit_has_shadda(diacs: Tuple[str, ...]) -> bool:
    return SHADDA in diacs


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


def normalize_units_for_options(
    units: List[Unit], ignore_last_vowel: bool, ignore_tanwin: bool
) -> List[Unit]:
    if not units:
        return units
    out = []
    for idx, u in enumerate(units):
        diacs = set(u.diacs)
        if ignore_tanwin:
            diacs -= TANWIN
        if ignore_last_vowel and idx == len(units) - 1:
            diacs -= VOWELS
            diacs -= TANWIN
        out.append(Unit(u.base, _sorted_tuple(diacs)))
    return out


def units_match(p: Unit, w: Unit, allow_missing_word_vowels: bool) -> bool:
    if p.base in PLACEHOLDERS:
        base_ok = True
    else:
        base_ok = p.base == w.base
    if not base_ok:
        return False
    if unit_has_shadda(p.diacs) != unit_has_shadda(w.diacs):
        return False
    pv, wv = unit_vowel(p.diacs), unit_vowel(w.diacs)
    if pv is not None and not (wv is None and allow_missing_word_vowels) and pv != wv:
        return False
    pt, wt = unit_tanwin(p.diacs), unit_tanwin(w.diacs)
    if pt is not None and not (wt is None and allow_missing_word_vowels) and pt != wt:
        return False
    return True


@dataclass
class MatchHit:
    pattern: str
    reason: str
    window_start: int
    score_key: Tuple[int, int, int, int]


def try_match_pattern_to_word(pattern: str, word: str) -> List[MatchHit]:
    word_processed = remove_al_and_shadda(word)
    p_units = split_units(pattern)
    w_units = split_units(word_processed)
    p_units = normalize_units_for_options(p_units, IGNORE_LAST_VOWEL, IGNORE_TANWIN)
    w_units = normalize_units_for_options(w_units, IGNORE_LAST_VOWEL, IGNORE_TANWIN)

    if len(p_units) < MIN_PATTERN_UNITS:
        return []
    if REQUIRE_FAL_ORDER_IN_PATTERN and not has_fal_order_in_pattern(pattern):
        return []

    lp, lw = len(p_units), len(w_units)
    fixed = count_fixed_letters(p_units)
    diac_spec = count_specified_diacritics(p_units)
    eff_len = pattern_effective_len(p_units)

    def make_score(reason: str) -> Tuple[int, int, int, int]:
        reason_rank = 2 if reason == "FULLMATCH" else 1
        return (reason_rank, eff_len, fixed, diac_spec)

    if lp > lw:
        return []
    if lp == lw:
        if all(
            units_match(p_units[i], w_units[i], ALLOW_MISSING_WORD_VOWELS)
            for i in range(lp)
        ):
            return [MatchHit(pattern, "FULLMATCH", 0, make_score("FULLMATCH"))]
        return []
    if not SUBSTRING_MATCHING:
        return []

    for start in range(0, lw - lp + 1):
        if all(
            units_match(p_units[i], w_units[start + i], ALLOW_MISSING_WORD_VOWELS)
            for i in range(lp)
        ):
            return [MatchHit(pattern, "WINDOW", start, make_score("WINDOW"))]
    return []


def best_hit(hits: List[MatchHit]) -> Optional[MatchHit]:
    if not hits:
        return None
    return max(
        hits,
        key=lambda h: (h.score_key, len(h.pattern), h.pattern),
    )


def _sniff_delimiter(path: str) -> str:
    with open(path, "r", encoding="utf-8", newline="") as f:
        sample = f.read(4096)
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=[",", "\t", ";", "|"])
        return dialect.delimiter
    except Exception:
        if "\t" in sample.splitlines()[0]:
            return "\t"
        return ","


def _pick_column(row: Dict[str, str], candidates: List[str]) -> Optional[str]:
    for c in candidates:
        if c in row and row.get(c) and str(row[c]).strip():
            return str(row[c]).strip()
    return None


def load_patterns(patterns_csv: str) -> List[str]:
    path = Path(patterns_csv)
    if not path.exists():
        return []
    delim = _sniff_delimiter(str(path))
    patterns: List[str] = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=delim)
        for row in reader:
            p = _pick_column(dict(row), ["الوزن", "wazn", "pattern", "Pattern"])
            if p:
                patterns.append(p)
    seen = set()
    out = []
    for p in patterns:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out
