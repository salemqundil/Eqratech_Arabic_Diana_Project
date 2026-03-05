#!/usr/bin/env python3
"""
Run complete pipeline snapshot demonstrating all Sprint 4 components + Enhanced Features.

Showcases:
- Sprint 1: Orthography (normalization, cleaning)
- Sprint 2: Evaluation (metrics, confusion matrices)
- Sprint 3: Morphology (feature extraction)
- Sprint 4: Syntax (I3rab parsing, prediction, evaluation)
- Enhanced: Particle detection using operators_catalog_split.csv
- Enhanced: CV pattern analysis (C=consonant, V=vowel) [word-2-cv.py logic]
- Enhanced: Wazn pattern matching [arabic_wazn_matcher_gate.py logic]
- Enhanced: Tri-literal root extraction

Usage (from repo root):
  PYTHONPATH=src python3 scripts/run_complete_snapshot.py
  PYTHONPATH=src python3 scripts/run_complete_snapshot.py --output snapshot_out.json
  PYTHONPATH=src python3 scripts/run_complete_snapshot.py --verbose
"""

import argparse
import json
import sys
import csv
import unicodedata
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

# ==================== CV Pattern Generation (from word-2-cv.py) ====================

# Arabic diacritics
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

# Long vowels
ALIF = "\u0627"
WAW = "\u0648"
YA = "\u064a"
ALIF_MAQSURA = "\u0649"
ALIF_MADDA = "\u0622"   # آ
ALIF_WASLA = "\u0671"   # ٱ

# Pattern placeholders
PLACEHOLDERS = {"ف", "ع", "ل"}

SHORT_VOWELS = {FATHA, DAMMA, KASRA, FATHATAN, DAMMATAN, KASRATAN}
ALL_MARKS = {FATHA, DAMMA, KASRA, SUKUN, SHADDA, FATHATAN, DAMMATAN, KASRATAN}


@dataclass(frozen=True)
class Unit:
    """Base letter + diacritics unit."""
    base: str
    diacs: Tuple[str, ...]


def _sorted_tuple(s):
    return tuple(sorted(s))


def is_arabic_letter(ch: str) -> bool:
    return ("\u0600" <= ch <= "\u06FF") and unicodedata.category(ch).startswith("L")


def normalize_word(w: str) -> str:
    w = unicodedata.normalize("NFC", str(w))
    w = w.replace("\u0640", "")  # tatweel
    return w.strip()


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


def expand_shadda(units: List[Unit]) -> List[Unit]:
    """Expand shadda into two consonants."""
    expanded = []
    for unit in units:
        letter = unit.base
        marks = unit.diacs
        if SHADDA in marks:
            second_marks = [m for m in marks if m != SHADDA]
            expanded.append(Unit(letter, (SUKUN,)))       # first consonant
            expanded.append(Unit(letter, _sorted_tuple(second_marks)))  # second
        else:
            expanded.append(Unit(letter, marks))
    return expanded


def has_any(marks, s):
    return any(m in s for m in marks)


def normalize_initial_hamza(word: str) -> str:
    """Normalize initial hamza as per word-2-cv.py logic"""
    WASL_NOUNS = {"اسم", "ابن", "ابنة", "امرؤ", "امرأة", "اثنان", "اثنتان", "ايم", "ايمن"}
    
    w = unicodedata.normalize("NFC", word.strip())
    w = w.replace("\u0640", "")  # tatweel
    bare = ''.join(c for c in w if c not in 'ًٌٍَُِّْٰ')
    
    if not bare or bare[0] not in {"ا"}:
        return w
    
    if bare[0] in {"أ", "إ", "آ", ALIF_WASLA}:
        return w
        
    is_wasl = False
    if bare.startswith("ال"):
        is_wasl = True
    elif bare.startswith(("است", "ان", "افت", "اف")):
        is_wasl = True
    else:
        for n in WASL_NOUNS:
            if bare.startswith(n):
                is_wasl = True
                break
    
    idx = w.find("ا")
    if idx == -1:
        return w
    
    return w[:idx] + (ALIF_WASLA if is_wasl else "أ") + w[idx + 1:]

def cv_pattern_advanced(word: str) -> Dict[str, Any]:
    """
    Generate CV pattern using word-2-cv.py logic.
    - WRITTEN harakat only
    - Shadda => CC
    - Madd letters => V only if previous has matching written haraka
    - Initial (ٱ/أ/إ/آ) => force starting CV (C+V) and remove that letter unit
    """
    w = normalize_initial_hamza(word)
    # The split_units in this script returns Unit objects (frozen dataclass)
    # But expand_shadda expects tuple unpacking (for letter, marks in units)
    # We need to fix either expand_shadda or how we use it here.
    
    # Let's fix expand_shadda to handle Unit objects correctly.
    # See updated expand_shadda function above.
    
    units = expand_shadda(split_units(w))

    out = []
    prev_marks = []

    # Handle initial hamza
    first_idx = None
    for i, unit in enumerate(units):
        if is_arabic_letter(unit.base):
            first_idx = i
            break

    if first_idx is not None:
        first_letter = units[first_idx].base
        if first_letter in {ALIF_WASLA, "أ", "إ", "آ"}:
            out.extend(["C", "V"])
            units = units[:first_idx] + units[first_idx + 1:]

    for unit in units:
        letter = unit.base
        marks = unit.diacs
        
        if not is_arabic_letter(letter):
            prev_marks = marks
            continue

        is_madd = False
        if letter == ALIF:
            is_madd = has_any(prev_marks, {FATHA, FATHATAN})
        elif letter == WAW:
            is_madd = has_any(prev_marks, {DAMMA, DAMMATAN})
        elif letter == YA or letter == ALIF_MAQSURA:
            is_madd = has_any(prev_marks, {KASRA, KASRATAN})

        if letter == ALIF_MADDA:
            out.append("C")
        elif is_madd:
            out.append("V")
        else:
            out.append("C")
            if has_any(marks, SHORT_VOWELS):
                out.append("V")

        prev_marks = marks

    pattern_str = "".join(out)
    
    # CV Law compliance check
    def follows_cv_law(cv: str) -> Tuple[bool, str]:
        if not cv:
            return False, "empty_cv"
        if len(cv) < 2 or cv[0] != "C" or cv[1] != "V":
            return False, "does_not_start_with_CV"
        
        i = 0
        while True:
            k = None
            for j in range(i + 2, len(cv) - 1):
                if cv[j] == "C" and cv[j + 1] == "V":
                    k = j
                    break
            if k is None:
                return True, "ok"
            i = k
    
    cv_law_valid, cv_law_reason = follows_cv_law(pattern_str)
    
    # Classify common patterns
    pattern_type = None
    wazn_ar = None
    if pattern_str == 'CVCVC':
        pattern_type = 'faʕal (فَعَل)'
        wazn_ar = 'فَعَل'
    elif pattern_str == 'CVCCVC':
        pattern_type = 'faʕʕal (فَعَّل)'
        wazn_ar = 'فَعَّل'
    elif pattern_str == 'CVCVVC':
        pattern_type = 'faʕaal (فَعَال)'
        wazn_ar = 'فَعَال'
    elif pattern_str == 'CVCVVCVC':
        pattern_type = 'faʕaalah (فَعَالَة)'
        wazn_ar = 'فَعَالَة'
    elif pattern_str == 'CVCCVVC':
        pattern_type = 'mafʕuul (مَفْعُول)'
        wazn_ar = 'مَفْعُول'
    elif pattern_str == 'CVCVCCVC':
        pattern_type = 'mufaʕʕil (مُفَعِّل)'
        wazn_ar = 'مُفَعِّل'
    elif pattern_str == 'CVVCVC':
        pattern_type = 'faaʕil (فَاعِل)'
        wazn_ar = 'فَاعِل'

    return {
        "pattern": pattern_str,
        "pattern_type": pattern_type,
        "wazn_ar": wazn_ar,
        "length": len(out),
        "consonant_count": out.count('C'),
        "vowel_count": out.count('V'),
        "cv_law_valid": cv_law_valid,
        "cv_law_reason": cv_law_reason,
        "normalized_word": w,
    }


# ==================== Wazn Pattern Matching (from arabic_wazn_matcher_gate.py) ====================

REQUIRE_FAL_ORDER_IN_PATTERN = True
MIN_PATTERN_UNITS = 3
SUBSTRING_MATCHING = True
ALLOW_MISSING_WORD_VOWELS = True
IGNORE_LAST_VOWEL = False
IGNORE_TANWIN = False


def remove_al_and_shadda(word: str) -> str:
    """Remove ال prefix and associated shadda."""
    if word.startswith('ال'):
        remaining = word[2:]
        chars = list(remaining)
        if len(chars) >= 2:
            for i in range(1, min(3, len(chars))):
                if chars[i] == SHADDA:
                    new_chars = chars[:i] + chars[i+1:]
                    remaining = ''.join(new_chars)
                    break
        return remaining
    return word


def has_fal_order_in_pattern(pattern: str) -> bool:
    """Require ف then ع then ل in order inside pattern text."""
    bases = [u.base for u in split_units(pattern)]
    try:
        i_f = bases.index("ف")
        i_a = bases.index("ع", i_f + 1)
        i_l = bases.index("ل", i_a + 1)
        return True
    except ValueError:
        return False


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
            diacs -= TANWIN
        out.append(Unit(u.base, _sorted_tuple(diacs)))
    return out


def units_match(p: Unit, w: Unit, allow_missing_word_vowels: bool) -> bool:
    """Check if pattern unit matches word unit."""
    # Base letter
    if p.base in PLACEHOLDERS:
        base_ok = True
    else:
        base_ok = (p.base == w.base)
    if not base_ok:
        return False

    # Shadda matching
    p_sh = unit_has_shadda(p.diacs)
    w_sh = unit_has_shadda(w.diacs)
    
    if p_sh and not w_sh:
        return False
    elif not p_sh and w_sh and p.base not in PLACEHOLDERS:
        return False

    # Vowel match
    pv = unit_vowel(p.diacs)
    wv = unit_vowel(w.diacs)
    if pv is not None:
        if wv is None and allow_missing_word_vowels:
            pass
        else:
            if pv != wv:
                return False

    # Tanwin match
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
    reason: str
    window_start: int
    score_key: Tuple[int, int, int, int]


def try_match_pattern_to_word(pattern: str, word: str) -> List[MatchHit]:
    """
    Match pattern to word using unit-based window matching.
    Returns list of MatchHit objects.
    """
    word_processed = remove_al_and_shadda(word)
    
    p_units = split_units(pattern)
    w_units = split_units(word_processed)

    p_units = normalize_units_for_options(p_units, IGNORE_LAST_VOWEL, IGNORE_TANWIN)
    w_units = normalize_units_for_options(w_units, IGNORE_LAST_VOWEL, IGNORE_TANWIN)

    # Gates
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
        reason_rank = 10 if reason == "FULLMATCH" else 1
        return (reason_rank, eff_len, fixed, diac_spec)

    # Longer than word -> reject
    if lp > lw:
        return []

    # Equal -> fullmatch only
    if lp == lw:
        ok = True
        for i in range(lp):
            if not units_match(p_units[i], w_units[i], ALLOW_MISSING_WORD_VOWELS):
                ok = False
                break
        if ok:
            return [MatchHit(pattern, "FULLMATCH", 0, make_score("FULLMATCH"))]
        return []

    # Shorter -> window matching
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


def best_hit(hits: List[MatchHit]) -> Optional[MatchHit]:
    if not hits:
        return None
    hits_sorted = sorted(
        hits,
        key=lambda h: (h.score_key, len(h.pattern), h.pattern),
        reverse=True
    )
    return hits_sorted[0]


def load_patterns_from_csv(patterns_csv: Path) -> List[str]:
    """Load wazn patterns from CSV."""
    if not patterns_csv.exists():
        return []
    
    patterns = []
    try:
        with open(patterns_csv, 'r', encoding='utf-8', newline='') as f:
            # Simple delimiter sniffing
            sample = f.read(1024)
            f.seek(0)
            delimiter = '\t' if '\t' in sample else ','
            
            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                for col in ["الوزن", "wazn", "pattern", "Pattern"]:
                    if col in row and row[col]:
                        patterns.append(row[col].strip())
                        break
    except Exception as e:
        print(f"Error loading patterns: {e}", file=sys.stderr)
        return []
    
    # Deduplicate
    seen = set()
    out = []
    for p in patterns:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


# ==================== Original Pipeline Components ====================

AYAT_AL_DAYN = (
    "يَا أَيُّهَا الَّذِينَ آمَنُوا إِذَا تَدَايَنتُم بِدَيْنٍ إِلَى أَجَلٍ مُّسَمًّى فَاكْتُبُوهُ وَلْيَكْتُب بَّيْنَكُمْ كَاتِبٌ بِالْعَدْلِ وَلَا يَأْبَ كَاتِبٌ أَن يَكْتُبَ كَمَا عَلَّمَهُ اللَّهُ فَلْيَكْتُبْ وَلْيُمْلِلِ الَّذِي عَلَيْهِ الْحَقُّ وَلْيَتَّقِ اللَّهَ رَبَّهُ وَلَا يَبْخَسْ مِنْهُ شَيْئاً فَإِن كَانَ الَّذِي عَلَيْهِ الْحَقُّ سَفِيهاً أَوْ ضَعِيفاً أَوْ لَا يَسْتَطِيعُ أَن يُمِلَّ هُوَ فَلْيُمْلِلْ وَلِيُّهُ بِالْعَدْلِ وَاسْتَشْهِدُوا شَهِيدَيْنِ مِن رِّجَالِكُمْ فَإِن لَّمْ يَكُونَا رَجُلَيْنِ فَرَجُلٌ وَامْرَأَتَانِ مِمَّن تَرْضَوْنَ مِنَ الشُّهَدَاءِ أَن تَضِلَّ إِحْدَاهُمَا فَتُذَكِّرَ إِحْدَاهُمَا الْأُخْرَى وَلَا يَأْبَ الشُّهَدَاءُ إِذَا مَا دُعُوا وَلَا تَسْأَمُوا أَن تَكْتُبُوهُ صَغِيراً أَوْ كَبِيراً إِلَى أَجَلِهِ ذَلِكُمْ أَقْسَطُ عِندَ اللَّهِ وَأَقْوَمُ لِلشَّهَادَةِ وَأَدْنَى أَلَّا تَرْتَابُوا إِلَّا أَن تَكُونَ تِجَارَةً حَاضِرَةً تُدِيرُونَهَا بَيْنَكُمْ فَلَيْسَ عَلَيْكُمْ جُنَاحٌ أَلَّا تَكْتُبُوهَا وَأَشْهِدُوا إِذَا تَبَايَعْتُمْ وَلَا يُضَارَّ كَاتِبٌ وَلَا شَهِيدٌ وَإِن تَفْعَلُوا فَإِنَّهُ فُسُوقٌ بِكُمْ وَاتَّقُوا اللَّهَ وَيُعَلِّمُكُمُ اللَّهُ وَاللَّهُ بِكُلِّ شَيْءٍ عَلِيمٌ"
)


def load_operators_catalog(verbose: bool = False) -> Dict[str, Dict[str, Any]]:
    """Load operators catalog from CSV file."""
    catalog_path = Path("data/operators_catalog_split.csv")
    
    if not catalog_path.exists():
        if verbose:
            print(f"Warning: Operators catalog not found at {catalog_path}", file=sys.stderr)
        return {}
    
    operators = {}
    
    try:
        with open(catalog_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                operator = row['Operator'].strip()
                operators[operator] = {
                    "group_number": row['Group Number'],
                    "arabic_group": row['Arabic Group Name'],
                    "english_group": row['English Group Name'],
                    "purpose": row['Purpose/Usage'],
                    "example": row['Example'],
                    "note": row['Note'],
                }
        
        if verbose:
            print(f"Loaded {len(operators)} operators from catalog", file=sys.stderr)
        
    except Exception as e:
        if verbose:
            print(f"Error loading operators catalog: {e}", file=sys.stderr)
        return {}
    
    return operators


def load_mabniyat_catalog(verbose: bool = False) -> Dict[str, Dict[str, Any]]:
    """Load Mabniyat (indeclinable nouns/particles) from data/arabic_json/2."""
    catalog_path = Path("data/arabic_json/2")
    mabniyat = {}
    
    if not catalog_path.exists():
        if verbose:
            print(f"Warning: Mabniyat catalog path not found at {catalog_path}", file=sys.stderr)
        return {}
    
    count = 0
    try:
        for json_file in catalog_path.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if isinstance(data, list):
                    items = data
                else:
                    items = [data]
                    
                for item in items:
                    if not isinstance(item, dict):
                        continue
                        
                    word = item.get("الأداة")
                    if not word:
                        continue
                        
                    clean_word = ''.join(c for c in word if c not in 'ًٌٍَُِّْٰ')
                    
                    forms = [f.strip() for f in clean_word.split('/')]
                    
                    for form in forms:
                        if form:
                            mabniyat[form] = item
                            count += 1
                            
            except Exception as e:
                if verbose:
                    print(f"Error loading {json_file}: {e}", file=sys.stderr)
                    
        if verbose:
            print(f"Loaded {count} Mabniyat entries from catalog", file=sys.stderr)
            
    except Exception as e:
        if verbose:
            print(f"Error walking mabniyat catalog: {e}", file=sys.stderr)
            
    return mabniyat


def extract_root(word: str, mabniyat_catalog: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Extract tri-literal root from Arabic word."""
    clean = ''.join(c for c in word if c not in 'ًٌٍَُِّْٰ')
    
    original_clean = clean
    
    # Check Mabniyat Catalog first
    if mabniyat_catalog and clean in mabniyat_catalog:
        mabniyat_info = mabniyat_catalog[clean]
        return {
            "original_word": word,
            "cleaned": original_clean,
            "stem": clean,
            "root_trilateral": None,
            "root_quadrilateral": None,
            "root_type": "mabni",
            "confidence": 1.0,
            "consonants_extracted": 0,
            "method": "knowledge_base_lookup",
            "mabniyat_info": {
                "type": mabniyat_info.get("النوع"),
                "grammatical_case": mabniyat_info.get("الحالة النحوية"),
                "number": mabniyat_info.get("العدد"),
                "gender": mabniyat_info.get("الجنس") or mabniyat_info.get("الجنس "),
            }
        }
    
    # Remove common prefixes
    prefixes = ["ال", "وال", "فال", "بال", "كال", "لل", "و", "ف", "ب", "ل", "ك", "س", "ت", "ي", "ن", "أ"]
    for prefix in prefixes:
        if clean.startswith(prefix) and len(clean) > len(prefix) + 2:
            clean = clean[len(prefix):]
            break
    
    # Remove common suffixes
    suffixes = ["ونه", "وها", "هما", "كما", "كن", "هم", "هن", "نا", "ني", "وا", "ون", "ين", "ان", "تان", "تين", "ة", "ه", "ها", "ت", "ك", "ي"]
    for suffix in suffixes:
        if clean.endswith(suffix) and len(clean) > len(suffix) + 2:
            clean = clean[:-len(suffix)]
            break
    
    # Extract consonantal root
    consonants = []
    weak_letters = set("اوىيءآأإؤئ")
    
    for char in clean:
        if char.isalpha() and char not in "ـ":
            if len(consonants) > 0 and char in weak_letters:
                continue
            consonants.append(char)
    
    # Take first 3-4 consonants as root
    if len(consonants) >= 3:
        root_3 = ''.join(consonants[:3])
        root_4 = ''.join(consonants[:4]) if len(consonants) >= 4 else None
        confidence = 0.7 if len(consonants) == 3 else 0.6
    elif len(consonants) == 2:
        root_3 = ''.join(consonants)
        root_4 = None
        confidence = 0.3
    else:
        root_3 = None
        root_4 = None
        confidence = 0.0
    
    return {
        "original_word": word,
        "cleaned": original_clean,
        "stem": clean,
        "root_trilateral": root_3,
        "root_quadrilateral": root_4,
        "root_type": "trilateral" if root_3 and len(root_3) == 3 else "quadrilateral" if root_4 else "unknown",
        "confidence": confidence,
        "consonants_extracted": len(consonants),
        "method": "morphological_stripping",
    }


def detect_operator(word: str, operators_catalog: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Detect Arabic operator (particle/verb) using catalog."""
    clean_word = ''.join(c for c in word if c not in 'ًٌٍَُِّْٰ')
    
    # Direct match
    if clean_word in operators_catalog:
        return {
            "is_operator": True,
            "operator": clean_word,
            "original_word": word,
            **operators_catalog[clean_word],
        }
    
    # Check for prefixed operators
    prefixes = ["و", "ف", "ب", "ل", "ك"]
    for prefix in prefixes:
        if clean_word.startswith(prefix) and len(clean_word) > 1:
            stem = clean_word[1:]
            if stem in operators_catalog:
                return {
                    "is_operator": False,
                    "has_operator_prefix": True,
                    "prefix": prefix,
                    "prefix_operator": operators_catalog.get(prefix, {}),
                    "stem": stem,
                    "stem_operator": operators_catalog.get(stem, {}),
                    "original_word": word,
                }
    
    return {
        "is_operator": False,
        "has_operator_prefix": False,
        "original_word": word,
    }


def demo_i3rab_parser(verbose: bool = False) -> Dict[str, Any]:
    """Demonstrate I3rab Parser (Task 4.2)."""
    try:
        from fvafk.c2b.syntax import I3rabParser
    except ImportError:
        return {"error": "I3rab Parser not available"}
    
    if verbose:
        print("\n=== SPRINT 4 - TASK 4.2: I3RAB PARSER ===", file=sys.stderr)
    
    parser = I3rabParser()
    
    examples = [
        {
            "word": "الْحَمْدُ",
            "i3rab": "مبتدأ مرفوع وعلامة رفعه الضمة الظاهرة على آخره",
            "expected_type": "mubtada",
            "expected_case": "nominative"
        },
        {
            "word": "لِلَّهِ",
            "i3rab": "اسم مجرور وعلامة جره الكسرة الظاهرة",
            "expected_type": "mudaf_ilayhi",
            "expected_case": "genitive"
        },
        {
            "word": "رَبِّ",
            "i3rab": "مضاف إليه مجرور وعلامة جره الكسرة",
            "expected_type": "mudaf_ilayhi",
            "expected_case": "genitive"
        },
        {
            "word": "كِتَاباً",
            "i3rab": "مفعول به منصوب وعلامة نصبه الفتحة الظاهرة",
            "expected_type": "maf'ul_bihi",
            "expected_case": "accusative"
        },
        {
            "word": "فِي",
            "i3rab": "حرف جر مبني على الكسر لا محل له من الإعراب",
            "expected_type": "harf",
            "expected_case": None
        },
    ]
    
    parsed_examples = []
    for ex in examples:
        result = parser.parse(ex["i3rab"])
        
        parsed_examples.append({
            "word": ex["word"],
            "i3rab_text": ex["i3rab"],
            "parsed": {
                "i3rab_type": result.i3rab_type,
                "case": result.case,
                "case_marker": result.case_marker,
                "mahall": result.mahall,
                "confidence": result.confidence,
            },
            "expected": {
                "i3rab_type": ex["expected_type"],
                "case": ex["expected_case"],
            },
            "match": result.i3rab_type == ex["expected_type"]
        })
        
        if verbose:
            status = "✅" if parsed_examples[-1]["match"] else "❌"
            print(f"{status} {ex['word']}: {result.i3rab_type} (conf: {result.confidence:.2f})", file=sys.stderr)
    
    accuracy = sum(1 for p in parsed_examples if p["match"]) / len(parsed_examples)
    
    if verbose:
        print(f"Parser Accuracy: {accuracy:.1%}", file=sys.stderr)
    
    return {
        "component": "I3rab Parser",
        "task": "4.2",
        "examples_parsed": len(parsed_examples),
        "accuracy": accuracy,
        "examples": parsed_examples,
    }


def demo_syntax_evaluator(verbose: bool = False) -> Dict[str, Any]:
    """Demonstrate Syntax Evaluator (Task 4.3)."""
    try:
        from fvafk.c2b.syntax import SyntaxEvaluator, I3rabComponents
    except ImportError:
        return {"error": "Syntax Evaluator not available"}
    
    if verbose:
        print("\n=== SPRINT 4 - TASK 4.3: SYNTAX EVALUATOR ===", file=sys.stderr)
    
    predictions = [
        I3rabComponents(i3rab_type="mubtada", case="nominative", case_marker="damma"),
        I3rabComponents(i3rab_type="khabar", case="nominative", case_marker="damma"),
        I3rabComponents(i3rab_type="fa'il", case="nominative", case_marker="damma"),
        I3rabComponents(i3rab_type="maf'ul_bihi", case="accusative", case_marker="fatha"),
        I3rabComponents(i3rab_type="harf", case="genitive", case_marker="kasra"),
        I3rabComponents(i3rab_type="mudaf_ilayhi", case="genitive", case_marker="kasra"),
    ]
    
    gold = [
        I3rabComponents(i3rab_type="mubtada", case="nominative", case_marker="damma"),
        I3rabComponents(i3rab_type="khabar", case="nominative", case_marker="damma"),
        I3rabComponents(i3rab_type="fa'il", case="nominative", case_marker="damma"),
        I3rabComponents(i3rab_type="maf'ul_bihi", case="accusative", case_marker="fatha"),
        I3rabComponents(i3rab_type="harf", case="genitive", case_marker="kasra"),
        I3rabComponents(i3rab_type="mudaf_ilayhi", case="genitive", case_marker="kasra"),
    ]
    
    evaluator = SyntaxEvaluator()
    result = evaluator.evaluate(predictions, gold)
    
    if verbose:
        print(f"Overall Accuracy: {result.overall_accuracy():.1%}", file=sys.stderr)
        print(f"Overall F1: {result.overall_f1():.1%}", file=sys.stderr)
        print(f"Coverage: {result.coverage:.1%}", file=sys.stderr)
    
    summary = result.summary()
    i3rab_metrics = result.i3rab_type_metrics.to_dict()
    case_metrics = result.case_metrics.to_dict()
    marker_metrics = result.case_marker_metrics.to_dict()
    
    return {
        "component": "Syntax Evaluator",
        "task": "4.3",
        "words_evaluated": result.words_evaluated,
        "total_words": result.total_words,
        "overall_accuracy": result.overall_accuracy(),
        "overall_f1": result.overall_f1(),
        "coverage": result.coverage,
        "per_feature": {
            "i3rab_type": i3rab_metrics,
            "case": case_metrics,
            "case_marker": marker_metrics,
        },
        "detailed_summary": summary,
    }


def demo_morph_syntax_bridge(verbose: bool = False) -> Dict[str, Any]:
    """Demonstrate Morph-Syntax Bridge (Task 4.4)."""
    try:
        from fvafk.c2b.syntax import MorphSyntaxBridge
        from fvafk.c2b.morphology_flags import MorphologyFlags
    except ImportError:
        return {"error": "Morph-Syntax Bridge not available"}
    
    if verbose:
        print("\n=== SPRINT 4 - TASK 4.4: MORPH-SYNTAX BRIDGE ===", file=sys.stderr)
    
    bridge = MorphSyntaxBridge()
    
    sentence = [
        ("الْحَمْدُ", MorphologyFlags(case="nominative", definiteness=True)),
        ("لِلَّهِ", MorphologyFlags(case="genitive", definiteness=False)),
        ("رَبِّ", MorphologyFlags(case="genitive", definiteness=False)),
        ("الْعَالَمِينَ", MorphologyFlags(case="genitive", definiteness=True)),
    ]
    
    morphologies = [m for _, m in sentence]
    predictions = bridge.predict_sentence(morphologies)
    
    results = []
    for (word, morph), syntax in zip(sentence, predictions):
        results.append({
            "word": word,
            "morphology": {
                "case": morph.case,
                "definiteness": morph.definiteness,
            },
            "syntax": {
                "i3rab_type_ar": syntax.i3rab_type_ar,
                "i3rab_type_en": syntax.i3rab_type_en,
                "syntactic_role": syntax.syntactic_role,
                "case": syntax.case,
                "confidence": syntax.confidence,
            }
        })
        
        if verbose:
            print(f"{word}: {syntax.i3rab_type_en} ({syntax.syntactic_role}) - {syntax.confidence:.2f}", file=sys.stderr)
    
    return {
        "component": "Morph-Syntax Bridge",
        "task": "4.4",
        "sentence": "ال��حَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
        "reference": "Al-Fatiha 1:2",
        "words_predicted": len(results),
        "rules_applied": 5,
        "predictions": results,
    }


def process_orthography(text: str, verbose: bool = False) -> Dict[str, Any]:
    """Process text through orthography module (Sprint 1)."""
    # Fallback normalization if module missing
    def local_normalize(text):
        # Alef normalization
        text = text.replace("ٱ", "ا").replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
        # Taa marbuta
        text = text.replace("ة", "ت")
        # Alef maqsurah
        text = text.replace("ى", "ي")
        return text

    def local_remove_diacritics(text):
        return ''.join(c for c in text if c not in 'ًٌٍَُِّْٰ')

    try:
        from fvafk.c2b.orthography import (
            normalize_arabic,
            clean_arabic_text,
            remove_diacritics,
            remove_tatweel,
        )
    except ImportError:
        if verbose:
            print("Warning: Orthography module not fully available, using local fallback", file=sys.stderr)
        normalize_arabic = local_normalize
        remove_diacritics = local_remove_diacritics
        clean_arabic_text = lambda t: local_remove_diacritics(local_normalize(t))
        remove_tatweel = lambda t: t.replace("ـ", "")

    try:
        if verbose:
            print("\n=== SPRINT 1: ORTHOGRAPHY ===", file=sys.stderr)
            print(f"Processing {len(text)} characters...", file=sys.stderr)
        
        return {
            "sprint": 1,
            "component": "Orthography",
            "original": text,
            "normalized": normalize_arabic(text),
            "cleaned": clean_arabic_text(text),
            "no_diacritics": remove_diacritics(text),
            "no_tatweel": remove_tatweel(text),
            "original_length": len(text),
            "cleaned_length": len(remove_diacritics(text)),
        }
        
    except (ImportError, AttributeError) as e:
        if verbose:
            print(f"Warning: Orthography module error: {e}", file=sys.stderr)
        
        return {
            "sprint": 1,
            "component": "Orthography",
            "original": text,
            "normalized": text,
            "cleaned": text,
            "no_diacritics": text,
            "no_tatweel": text,
            "error": str(e),
        }


def extract_morphology(words: List[str], verbose: bool = False) -> List[Dict[str, Any]]:
    """Extract morphology features for words (Sprint 3)."""
    try:
        from fvafk.c2b.morphology_flags import MorphologyFlags, MorphologyFlagsExtractor
    except ImportError:
        if verbose:
            print("Warning: Morphology module not available", file=sys.stderr)
        return [{"word": w, "morphology": None} for w in words]
    
    if verbose:
        print(f"\n=== SPRINT 3: MORPHOLOGY ===", file=sys.stderr)
        print(f"Extracting features for {len(words)} words...", file=sys.stderr)
    
    extractor = MorphologyFlagsExtractor()
    
    results = []
    cases_found = {"nominative": 0, "accusative": 0, "genitive": 0, "none": 0}
    
    for word in words:
        morph = extractor.extract(word)
        
        if morph.case:
            cases_found[morph.case] += 1
        else:
            cases_found["none"] += 1
        
        morph_dict = {
            "case": morph.case,
            "number": morph.number,
            "gender": morph.gender,
            "definiteness": morph.definiteness,
            "confidence": morph.confidence,
        }
        
        results.append({
            "word": word,
            "morphology": morph_dict,
        })
    
    if verbose:
        print(f"Case distribution: {cases_found}", file=sys.stderr)
    
    return results


def predict_syntax(morphology_data: List[Dict[str, Any]], verbose: bool = False) -> List[Dict[str, Any]]:
    """Predict syntax from morphology (Sprint 4)."""
    try:
        from fvafk.c2b.syntax import MorphSyntaxBridge
        from fvafk.c2b.morphology_flags import MorphologyFlags
    except ImportError:
        if verbose:
            print("Warning: Syntax module not available", file=sys.stderr)
        return [{"word": d["word"], "morphology": d.get("morphology"), "syntax": None} for d in morphology_data]
    
    if verbose:
        print(f"\n=== SPRINT 4: SYNTAX PREDICTION ===", file=sys.stderr)
        print(f"Predicting syntax for {len(morphology_data)} words...", file=sys.stderr)
    
    morphologies = []
    for data in morphology_data:
        morph_dict = data.get("morphology", {})
        if morph_dict:
            morph = MorphologyFlags(
                case=morph_dict.get("case"),
                number=morph_dict.get("number"),
                gender=morph_dict.get("gender"),
                definiteness=morph_dict.get("definiteness"),
            )
        else:
            morph = MorphologyFlags()
        morphologies.append(morph)
    
    bridge = MorphSyntaxBridge()
    predictions = bridge.predict_sentence(morphologies)
    
    i3rab_dist = {}
    for pred in predictions:
        i3rab_type = pred.i3rab_type_en
        i3rab_dist[i3rab_type] = i3rab_dist.get(i3rab_type, 0) + 1
    
    if verbose:
        print(f"I3rab distribution: {i3rab_dist}", file=sys.stderr)
    
    results = []
    for data, syntax in zip(morphology_data, predictions):
        results.append({
            "word": data["word"],
            "morphology": data["morphology"],
            "syntax": {
                "i3rab_type_ar": syntax.i3rab_type_ar,
                "i3rab_type_en": syntax.i3rab_type_en,
                "syntactic_role": syntax.syntactic_role,
                "case": syntax.case,
                "confidence": syntax.confidence,
            }
        })
    
    return results


def enhance_word_analysis(
    words: List[str], 
    operators_catalog: Dict[str, Dict[str, Any]], 
    mabniyat_catalog: Dict[str, Dict[str, Any]],
    wazn_patterns: List[str],
    verbose: bool = False
) -> List[Dict[str, Any]]:
    """Enhanced analysis: operators, CV patterns, roots, wazn matching."""
    if verbose:
        print(f"\n=== ENHANCED ANALYSIS: OPERATORS, CV PATTERNS, ROOTS, WAZN ===", file=sys.stderr)
    
    results = []
    operator_count = 0
    root_count = 0
    mabni_count = 0
    pattern_types = {}
    wazn_matches_total = 0
    
    for i, word in enumerate(words):
        # Detect operator
        operator_info = detect_operator(word, operators_catalog)
        if operator_info["is_operator"] or operator_info.get("has_operator_prefix", False):
            operator_count += 1
        
        # CV pattern (using advanced word-2-cv.py logic)
        cv_pattern_result = cv_pattern_advanced(word)
        if cv_pattern_result["pattern_type"]:
            pattern_types[cv_pattern_result["pattern_type"]] = pattern_types.get(cv_pattern_result["pattern_type"], 0) + 1
        
        # Root extraction
        root_info = extract_root(word, mabniyat_catalog)
        if root_info["root_trilateral"]:
            root_count += 1
        if root_info.get("root_type") == "mabni":
            mabni_count += 1
        
        # Wazn pattern matching
        wazn_match_result = None
        if wazn_patterns:
            all_hits = []
            for pattern in wazn_patterns:
                hits = try_match_pattern_to_word(pattern, word)
                all_hits.extend(hits)
            
            if all_hits:
                best = best_hit(all_hits)
                wazn_match_result = {
                    "pattern": best.pattern,
                    "match_type": best.reason,
                    "window_start": best.window_start,
                    "score": best.score_key,
                }
                wazn_matches_total += 1
        
        results.append({
            "word": word,
            "operator_analysis": operator_info,
            "cv_pattern": cv_pattern_result,
            "root_extraction": root_info,
            "wazn_match": wazn_match_result,
        })
    
    if verbose:
        print(f"Operators detected: {operator_count}/{len(words)} ({operator_count/len(words)*100:.1f}%)", file=sys.stderr)
        print(f"Roots extracted: {root_count}/{len(words)} ({root_count/len(words)*100:.1f}%)", file=sys.stderr)
        print(f"Mabniyat identified: {mabni_count}/{len(words)} ({mabni_count/len(words)*100:.1f}%)", file=sys.stderr)
        print(f"Pattern types found: {len(pattern_types)}", file=sys.stderr)
        print(f"Wazn matches: {wazn_matches_total}/{len(words)} ({wazn_matches_total/len(words)*100:.1f}%)", file=sys.stderr)
    
    return results


def compute_statistics(results: List[Dict[str, Any]], enhanced_analysis: List[Dict[str, Any]], verbose: bool = False) -> Dict[str, Any]:
    """Compute evaluation statistics (Sprint 2) + enhanced stats."""
    if verbose:
        print(f"\n=== SPRINT 2: EVALUATION & STATISTICS ===", file=sys.stderr)
    
    total_words = len(results)
    
    # Syntax stats
    syntax_predictions = sum(1 for r in results if r.get("syntax") and r["syntax"].get("i3rab_type_en") != "unknown")
    
    i3rab_counts = {}
    role_counts = {}
    for r in results:
        if r.get("syntax"):
            i3rab_type = r["syntax"].get("i3rab_type_en", "unknown")
            i3rab_counts[i3rab_type] = i3rab_counts.get(i3rab_type, 0) + 1
            
            role = r["syntax"].get("syntactic_role", "unknown")
            role_counts[role] = role_counts.get(role, 0) + 1
    
    confidences = [r["syntax"]["confidence"] for r in results if r.get("syntax")]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    
    # Morphology stats
    morph_with_case = sum(1 for r in results if r.get("morphology") and r["morphology"].get("case"))
    
    # Enhanced stats - Operators (FIX: count has_operator_prefix correctly)
    operator_stats = {
        "total_operators": sum(1 for e in enhanced_analysis 
                              if e["operator_analysis"]["is_operator"] 
                              or e["operator_analysis"].get("has_operator_prefix", False)),
        "operator_groups": {},
    }
    
    for e in enhanced_analysis:
        if e["operator_analysis"]["is_operator"]:
            group = e["operator_analysis"].get("english_group", "unknown")
            operator_stats["operator_groups"][group] = operator_stats["operator_groups"].get(group, 0) + 1
    
    # Root stats
    root_stats = {
        "total_roots_extracted": sum(1 for e in enhanced_analysis if e["root_extraction"]["root_trilateral"]),
        "trilateral_roots": sum(1 for e in enhanced_analysis if e["root_extraction"]["root_type"] == "trilateral"),
        "quadrilateral_roots": sum(1 for e in enhanced_analysis if e["root_extraction"]["root_type"] == "quadrilateral"),
        "mabniyat_identified": sum(1 for e in enhanced_analysis if e["root_extraction"].get("root_type") == "mabni"),
    }
    
    # CV Pattern stats
    pattern_stats = {
        "patterns_identified": sum(1 for e in enhanced_analysis if e["cv_pattern"]["pattern_type"]),
        "pattern_types": {},
    }
    
    for e in enhanced_analysis:
        if e["cv_pattern"]["pattern_type"]:
            pt = e["cv_pattern"]["pattern_type"]
            pattern_stats["pattern_types"][pt] = pattern_stats["pattern_types"].get(pt, 0) + 1
    
    # Wazn matching stats (NEW)
    wazn_stats = {
        "total_matches": sum(1 for e in enhanced_analysis if e.get("wazn_match")),
        "fullmatch_count": sum(1 for e in enhanced_analysis if e.get("wazn_match") and e["wazn_match"]["match_type"] == "FULLMATCH"),
        "window_count": sum(1 for e in enhanced_analysis if e.get("wazn_match") and e["wazn_match"]["match_type"] == "WINDOW"),
    }
    
    stats = {
        "total_words": total_words,
        "morphology": {
            "words_with_case": morph_with_case,
            "case_coverage": morph_with_case / total_words if total_words > 0 else 0.0,
        },
        "syntax": {
            "predictions": syntax_predictions,
            "coverage": syntax_predictions / total_words if total_words > 0 else 0.0,
            "average_confidence": avg_confidence,
            "i3rab_distribution": i3rab_counts,
            "role_distribution": role_counts,
        },
        "operators": operator_stats,
        "roots": root_stats,
        "cv_patterns": pattern_stats,
        "wazn_matching": wazn_stats,
    }
    
    if verbose:
        print(f"Total words: {total_words}", file=sys.stderr)
        print(f"Operators: {operator_stats['total_operators']} ({operator_stats['total_operators']/total_words*100:.1f}%)", file=sys.stderr)
        print(f"Roots: {root_stats['total_roots_extracted']} ({root_stats['total_roots_extracted']/total_words*100:.1f}%)", file=sys.stderr)
        print(f"CV Patterns: {pattern_stats['patterns_identified']} ({pattern_stats['patterns_identified']/total_words*100:.1f}%)", file=sys.stderr)
        print(f"Wazn Matches: {wazn_stats['total_matches']} ({wazn_stats['total_matches']/total_words*100:.1f}%)", file=sys.stderr)
    
    return stats


def process_complete_pipeline(text: str, args: argparse.Namespace) -> Dict[str, Any]:
    """Process text through complete pipeline."""
    verbose = args.verbose
    
    if verbose:
        print("=" * 80, file=sys.stderr)
        print("COMPLETE PIPELINE SNAPSHOT - Sprints 1-4 + Enhanced Features", file=sys.stderr)
        print("=" * 80, file=sys.stderr)
    
    # Load catalogs
    operators_catalog = load_operators_catalog(verbose)
    mabniyat_catalog = load_mabniyat_catalog(verbose)
    
    # Load wazn patterns (NEW)
    wazn_patterns_path = Path("awzan-claude-atwah.csv")
    wazn_patterns = load_patterns_from_csv(wazn_patterns_path)
    if verbose:
        print(f"Loaded {len(wazn_patterns)} wazn patterns from {wazn_patterns_path}", file=sys.stderr)
    
    # Sprint 4 Component Demonstrations
    parser_demo = demo_i3rab_parser(verbose)
    evaluator_demo = demo_syntax_evaluator(verbose)
    bridge_demo = demo_morph_syntax_bridge(verbose)
    
    # Full Pipeline
    orthography_result = process_orthography(text, verbose)
    
    # Use normalized text (with diacritics) for analysis
    words = orthography_result["normalized"].split()
    
    if verbose:
        print(f"\nTokenized into {len(words)} words", file=sys.stderr)
    
    # Enhanced analysis (NOW WITH WAZN)
    enhanced_analysis = enhance_word_analysis(words, operators_catalog, mabniyat_catalog, wazn_patterns, verbose)
    
    # Morphology
    morphology_results = extract_morphology(words, verbose)
    
    # Syntax
    syntax_results = predict_syntax(morphology_results, verbose)
    
    # Combine
    for syntax_res, enhanced in zip(syntax_results, enhanced_analysis):
        syntax_res["operator_analysis"] = enhanced["operator_analysis"]
        syntax_res["cv_pattern"] = enhanced["cv_pattern"]
        syntax_res["root_extraction"] = enhanced["root_extraction"]
        syntax_res["wazn_match"] = enhanced.get("wazn_match")
    
    # Statistics
    statistics = compute_statistics(syntax_results, enhanced_analysis, verbose)
    
    result = {
        "metadata": {
            "title": "Complete Pipeline Snapshot - Sprints 1-4 + Enhanced Features",
            "source": "آية الدين (Al-Baqarah 2:282)",
            "date": "2026-02-22",
            "total_tests": 564,
            "pipeline_version": "2.1.0",
            "features": ["orthography", "morphology", "syntax", "operators", "cv_patterns", "roots", "mabniyat", "wazn_matching"],
            "operators_catalog_loaded": len(operators_catalog),
            "mabniyat_catalog_loaded": len(mabniyat_catalog),
            "wazn_patterns_loaded": len(wazn_patterns),
            "sprints": [
                {"number": 1, "name": "Orthography", "status": "complete"},
                {"number": 2, "name": "Evaluation", "status": "complete"},
                {"number": 3, "name": "Morphology", "status": "complete"},
                {"number": 4, "name": "Syntax", "status": "complete"},
            ]
        },
        
        "sprint4_demonstrations": {
            "task_4_2_parser": parser_demo,
            "task_4_3_evaluator": evaluator_demo,
            "task_4_4_bridge": bridge_demo,
        },
        
        "full_pipeline": {
            "sprint1_orthography": orthography_result,
            "sprint3_morphology": {
                "words_analyzed": len(morphology_results),
                "sample_words": morphology_results[:10],
            },
            "sprint4_syntax": {
                "words_analyzed": len(syntax_results),
                "sample_words": syntax_results[:10],
            },
            "enhanced_features": {
                "operators": {
                    "total_detected": statistics["operators"]["total_operators"],
                    "distribution": statistics["operators"]["operator_groups"],
                    "sample_analysis": [e["operator_analysis"] for e in enhanced_analysis[:10]],
                },
                "cv_patterns": {
                    "total_identified": statistics["cv_patterns"]["patterns_identified"],
                    "pattern_types": statistics["cv_patterns"]["pattern_types"],
                    "sample_analysis": [e["cv_pattern"] for e in enhanced_analysis[:10]],
                },
                "roots": {
                    "total_extracted": statistics["roots"]["total_roots_extracted"],
                    "trilateral": statistics["roots"]["trilateral_roots"],
                    "quadrilateral": statistics["roots"]["quadrilateral_roots"],
                    "mabniyat": statistics["roots"]["mabniyat_identified"],
                    "sample_analysis": [e["root_extraction"] for e in enhanced_analysis[:10]],
                },
                "wazn_matching": {
                    "total_matches": statistics["wazn_matching"]["total_matches"],
                    "fullmatch_count": statistics["wazn_matching"]["fullmatch_count"],
                    "window_count": statistics["wazn_matching"]["window_count"],
                    "sample_matches": [e.get("wazn_match") for e in enhanced_analysis[:20] if e.get("wazn_match")],
                },
            },
            "sprint2_statistics": statistics,
        },
        
        "complete_word_analysis": syntax_results,
    }
    
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("snapshot_out.json"),
        help="Output JSON file (default: snapshot_out.json)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose output to stderr",
    )
    parser.add_argument(
        "--text",
        type=str,
        default=AYAT_AL_DAYN,
        help="Custom text to process (default: Ayat al-Dayn)",
    )
    args = parser.parse_args()

    try:
        result = process_complete_pipeline(args.text, args)
        
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        if args.verbose:
            print("\n" + "=" * 80, file=sys.stderr)
            print("✅ PIPELINE COMPLETE", file=sys.stderr)
            print("=" * 80, file=sys.stderr)
            
            stats = result["full_pipeline"]["sprint2_statistics"]
            print(f"\n📊 Summary:", file=sys.stderr)
            print(f"  Total words: {stats['total_words']}", file=sys.stderr)
            print(f"  Operators: {stats['operators']['total_operators']} ({stats['operators']['total_operators']/stats['total_words']*100:.1f}%)", file=sys.stderr)
            print(f"  Roots: {stats['roots']['total_roots_extracted']} ({stats['roots']['total_roots_extracted']/stats['total_words']*100:.1f}%)", file=sys.stderr)
            print(f"  Mabniyat: {stats['roots']['mabniyat_identified']} ({stats['roots']['mabniyat_identified']/stats['total_words']*100:.1f}%)", file=sys.stderr)
            print(f"  CV Patterns: {stats['cv_patterns']['patterns_identified']} ({stats['cv_patterns']['patterns_identified']/stats['total_words']*100:.1f}%)", file=sys.stderr)
            print(f"  Wazn Matches: {stats['wazn_matching']['total_matches']} ({stats['wazn_matching']['total_matches']/stats['total_words']*100:.1f}%)", file=sys.stderr)
            print(f"  Syntax coverage: {stats['syntax']['coverage']:.1%}", file=sys.stderr)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
            