#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arabic Syllabifier - Reference Implementation (Sprint 2, Task 2.2.1)
=====================================================================

**Status:** REFERENCE IMPLEMENTATION - Single Source of Truth for syllabification

Converts Arabic words to syllable structures following Arabic phonological rules.
Implements the Unified Foundation Theorem: C1 → C2a → C2b (syllabification).

Syllable Types (CV/CVV/CVC Taxonomy):
--------------------------------------
- **CV**:   صَ    (short vowel) - Open syllable, light
- **CVV**:  صَا   (long vowel) - Open syllable, heavy
- **CVC**:  صَبْ   (closed syllable) - Closed, heavy
- **CVVC**: صَابْ  (long vowel + coda) - Superheavy
- **CVCC**: صَبْتْ  (double coda) - Superheavy
- **CVVCC**: صَابْتْ (long + double coda) - Superheavy

Integration:
------------
- **FormCodecV2**: Uses encoded units from C1 layer
- **Phonology V2**: Complementary VC classification (context-driven)
- **C2b Pipeline**: Used for morphology word boundary detection
- **Testing**: 39 comprehensive tests in tests/test_syllabifier.py

References:
-----------
- See: src/fvafk/phonology_v2/ for context-driven VC classification
- See: src/fvafk/c1/form_codec_v2.py for encoding
- See: docs/SPRINT2_PLAN.md for integration roadmap

Author: Eqratech Project
Date: February 1, 2026
Updated: February 15, 2026 (Sprint 2 - marked as reference)
"""

import re
import unicodedata
from typing import List, Tuple, Optional, NamedTuple
from dataclasses import dataclass
from enum import Enum

__all__ = [
    "segment_cv_strict",
    "segment_cv_to_syllables",
    "validate_cv_law",
    "ArabicSyllabifier",
    "SyllabificationResult",
    "SyllableType",
    "Syllable",
    "Haraka",
    "MaddLetter",
    "normalize_word",
    "normalize_initial_hamza",
    "split_letters_and_marks",
    "expand_shadda",
    "syllabify",
    "syllabify_to_pattern",
]


# =============================================================================
# Unicode Constants - Harakat (Diacritics)
# =============================================================================

class Haraka:
    """Arabic diacritical marks"""
    FATHA = "\u064e"        # َ
    DAMMA = "\u064f"        # ُ
    KASRA = "\u0650"        # ِ
    SUKUN = "\u0652"        # ْ
    SHADDA = "\u0651"       # ّ
    TANWIN_FATH = "\u064b"  # ً
    TANWIN_DAMM = "\u064c"  # ٌ
    TANWIN_KASR = "\u064d"  # ٍ

    SHORT_VOWELS = {FATHA, DAMMA, KASRA, TANWIN_FATH, TANWIN_DAMM, TANWIN_KASR}
    ALL_MARKS = {FATHA, DAMMA, KASRA, SUKUN, SHADDA, TANWIN_FATH, TANWIN_DAMM, TANWIN_KASR}


class MaddLetter:
    """Arabic long vowel letters"""
    ALIF = "\u0627"         # ا
    WAW = "\u0648"          # و
    YA = "\u064a"           # ي
    ALIF_MAQSURA = "\u0649" # ى
    ALIF_MADDA = "\u0622"   # آ
    ALIF_WASLA = "\u0671"   # ٱ


# =============================================================================
# Data Structures
# =============================================================================

class SyllableType(Enum):
    """Arabic syllable patterns"""
    CV = "CV"           # صَ
    CVV = "CVV"         # صَا
    CVC = "CVC"         # صَبْ
    CVVC = "CVVC"       # صَابْ
    CVCC = "CVCC"       # صَبْتْ
    CVVCC = "CVVCC"     # صَابْتْ


@dataclass(frozen=True)
class Syllable:
    """
    Represents a single Arabic syllable.
    
    Attributes:
        text: Original Arabic text
        pattern: CV pattern (e.g., "CVC")
        syllable_type: Enum type
        onset: Consonant(s) before vowel
        nucleus: Vowel (short or long)
        coda: Optional consonant(s) after vowel
        position: Character position in original word
    """
    text: str
    pattern: str
    syllable_type: SyllableType
    onset: str
    nucleus: str
    coda: str
    position: int

    def __str__(self):
        return f"{self.text} [{self.pattern}]"


@dataclass
class SyllabificationResult:
    """
    Result of syllabifying a word.
    
    Attributes:
        original: Input word
        normalized: Normalized version
        syllables: List of Syllable objects
        cv_pattern: Full CV pattern string
        valid: Whether follows Arabic CV law
        error: Error message if invalid
    """
    original: str
    normalized: str
    syllables: List[Syllable]
    cv_pattern: str
    valid: bool
    error: Optional[str] = None

    def __str__(self):
        if not self.valid:
            return f"❌ {self.original} -> {self.error}"
        sylls = " - ".join(str(s) for s in self.syllables)
        return f"✅ {self.original} -> {sylls} [{self.cv_pattern}]"


# =============================================================================
# Core Utilities
# =============================================================================

def is_arabic_letter(ch: str) -> bool:
    """Check if character is an Arabic letter."""
    return ("\u0600" <= ch <= "\u06FF") and unicodedata.category(ch).startswith("L")


def normalize_word(word: str) -> str:
    """
    Normalize Arabic word:
    - NFC Unicode normalization
    - Remove tatweel (ـ)
    - Strip whitespace
    """
    word = unicodedata.normalize("NFC", str(word))
    word = word.replace("\u0640", "")  # Remove tatweel
    return word.strip()


def split_letters_and_marks(text: str) -> List[Tuple[str, List[str]]]:
    """
    Split text into (base_letter, [marks]) pairs.
    
    Example:
        "كَتَبَ" -> [('ك', ['َ']), ('ت', ['َ']), ('ب', ['َ'])]
    """
    units = []
    base = None
    marks = []
    
    for ch in text:
        is_mark = unicodedata.combining(ch) != 0 and ch in Haraka.ALL_MARKS
        
        if is_mark:
            if base is not None:
                marks.append(ch)
            continue
        
        # Save previous unit
        if base is not None:
            units.append((base, marks))
        
        base = ch
        marks = []
    
    # Save last unit
    if base is not None:
        units.append((base, marks))
    
    return units


def expand_shadda(units: List[Tuple[str, List[str]]]) -> List[Tuple[str, List[str]]]:
    """
    Expand shadda (gemination) into two consonants.
    
    Example:
        ('د', ['ّ', 'َ']) -> [('د', ['ْ']), ('د', ['َ'])]
    """
    expanded = []
    for letter, marks in units:
        if Haraka.SHADDA in marks:
            # First consonant with sukun
            expanded.append((letter, [Haraka.SUKUN]))
            # Second consonant with remaining marks
            second_marks = [m for m in marks if m != Haraka.SHADDA]
            expanded.append((letter, second_marks))
        else:
            expanded.append((letter, marks))
    return expanded


def has_any(marks: List[str], mark_set: set) -> bool:
    """Check if any mark in list is in the given set."""
    return any(m in mark_set for m in marks)


# =============================================================================
# Hamza Normalization
# =============================================================================

# Words that start with hamzat wasl (connecting hamza)
WASL_NOUNS = {"اسم", "ابن", "ابنة", "امرؤ", "امرأة", "اثنان", "اثنتان", "ايم", "ايمن"}


def normalize_initial_hamza(word: str) -> str:
    """
    Normalize initial hamza:
    - Bare alif (ا) with no hamza -> convert to wasl (ٱ) or qat' (أ)
    - Already has hamza -> keep as is
    """
    word = normalize_word(word)
    
    # Remove all marks to check first letter
    bare = "".join(ch for ch in word if ch not in Haraka.ALL_MARKS)
    if not bare:
        return word
    
    # Already has hamza - keep as is
    if bare[0] in {"أ", "إ", "آ", MaddLetter.ALIF_WASLA}:
        return word
    
    # Not starting with alif
    if bare[0] != MaddLetter.ALIF:
        return word
    
    # Determine if hamzat wasl or qat'
    is_wasl = False
    
    # Definite article "ال"
    if bare.startswith("ال"):
        is_wasl = True
    # Verbs: استفعل، انفعل، افتعل
    elif bare.startswith(("است", "ان", "افت")):
        is_wasl = True
    # Known wasl nouns
    else:
        for noun in WASL_NOUNS:
            if bare.startswith(noun):
                is_wasl = True
                break
    
    # Replace first alif
    idx = word.find(MaddLetter.ALIF)
    if idx == -1:
        return word
    
    replacement = MaddLetter.ALIF_WASLA if is_wasl else "أ"
    return word[:idx] + replacement + word[idx + 1:]


# =============================================================================
# CV Pattern Generation
# =============================================================================

def word_to_cv_pattern(word: str) -> str:
    """
    Convert Arabic word to CV pattern (WRITTEN harakat only).
    
    Rules:
    1. Shadda -> CC (gemination)
    2. Madd letters (ا، و، ي) -> V only if previous has matching haraka
    3. Initial hamza (ٱ/أ/إ/آ) -> force CV and remove
    4. Regular consonant with haraka -> CV
    5. Regular consonant with sukun -> C only
    
    Example:
        "كَتَبَ" -> "CVCVCV"
        "كَاتِب" -> "CVVCVC"
    """
    word = normalize_word(word)
    units = expand_shadda(split_letters_and_marks(word))
    
    cv = []
    prev_marks = []
    
    # Handle initial hamza
    first_idx = None
    for i, (ch, _) in enumerate(units):
        if is_arabic_letter(ch):
            first_idx = i
            break
    
    if first_idx is not None:
        first_letter = units[first_idx][0]
        if first_letter in {MaddLetter.ALIF_WASLA, "أ", "إ", "آ"}:
            # Force initial CV
            cv.extend(["C", "V"])
            units = units[:first_idx] + units[first_idx + 1:]
    
    # Process remaining units
    for letter, marks in units:
        if not is_arabic_letter(letter):
            prev_marks = marks
            continue
        
        # Check if this is a madd letter
        is_madd = False
        if letter == MaddLetter.ALIF:
            is_madd = has_any(prev_marks, {Haraka.FATHA, Haraka.TANWIN_FATH})
        elif letter == MaddLetter.WAW:
            is_madd = has_any(prev_marks, {Haraka.DAMMA, Haraka.TANWIN_DAMM})
        elif letter in {MaddLetter.YA, MaddLetter.ALIF_MAQSURA}:
            is_madd = has_any(prev_marks, {Haraka.KASRA, Haraka.TANWIN_KASR})
        
        # Special case: alif madda (آ)
        if letter == MaddLetter.ALIF_MADDA:
            cv.append("C")
        elif is_madd:
            cv.append("V")
        else:
            cv.append("C")
            if has_any(marks, Haraka.SHORT_VOWELS):
                cv.append("V")
        
        prev_marks = marks
    
    return "".join(cv)


# =============================================================================
# CV Law Validation
# =============================================================================

def validate_cv_law(cv: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Arabic CV law: must start with CV and maintain syllable structure.
    
    Returns:
        (is_valid, error_message)
    """
    if not cv:
        return False, "empty_cv_pattern"
    
    if len(cv) < 2 or cv[0] != "C" or cv[1] != "V":
        return False, "does_not_start_with_CV"
    
    # Check for valid syllable sequences
    i = 0
    while True:
        # Find next CV sequence
        k = None
        for j in range(i + 2, len(cv) - 1):
            if cv[j] == "C" and cv[j + 1] == "V":
                k = j
                break
        
        if k is None:
            return True, None
        
        i = k


# =============================================================================
# Syllable Segmentation
# =============================================================================

def segment_cv_to_syllables(cv: str) -> List[str]:
    """
    Segment CV pattern into syllable patterns.
    
    Algorithm:
    1. Start from beginning
    2. Match longest valid syllable (CVVCC > CVVC > CVCC > CVC > CVV > CV)
    3. Repeat until end
    
    Example:
        "CVVCVCC" -> ["CVV", "CVC", "C"] or ["CVV", "CVCC"]
    """
    if not cv:
        return []
    
    syllables: List[str] = []
    i = 0

    while i < len(cv):
        if i + 1 >= len(cv) or cv[i] != "C" or cv[i + 1] != "V":
            i += 1
            continue

        syll = "CV"
        i += 2

        if i < len(cv) and cv[i] == "V":
            syll = "CVV"
            i += 1

        c_start = i
        while i < len(cv) and cv[i] == "C":
            i += 1
        c_count = i - c_start

        if i >= len(cv):
            coda = min(2, c_count)
            if coda == 1:
                syll += "C"
            elif coda == 2:
                syll += "CC"
            syllables.append(syll)
            break

        coda = min(2, max(0, c_count - 1))
        if coda == 1:
            syll += "C"
        elif coda == 2:
            syll += "CC"

        i = c_start + coda
        syllables.append(syll)

    return syllables


def segment_cv_strict(cv: str) -> Tuple[Optional[List[str]], Optional[str]]:
    """
    Strict CV segmentation.  Returns ``(syllable_patterns, error)``.

    Unlike :func:`segment_cv_to_syllables`, this routine fails immediately
    whenever it encounters a position that cannot start a valid syllable
    (i.e. ``cv[i:i+2] != "CV"``) and also fails if the CV string is not
    **fully consumed** by the produced syllable list.

    Error codes returned in the ``error`` slot:
    - ``illegal_cv_sequence_at:<index>`` – position *i* is not the start of CV
    - ``cv_not_fully_consumed:<leftover>`` – trailing characters remain after
      last syllable

    Returns ``([], None)`` for an empty string (consistent with
    :func:`segment_cv_to_syllables`).
    """
    if not cv:
        return [], None

    syllables: List[str] = []
    i = 0

    while i < len(cv):
        if i + 1 >= len(cv) or cv[i] != "C" or cv[i + 1] != "V":
            return None, f"illegal_cv_sequence_at:{i}"

        syll = "CV"
        i += 2

        if i < len(cv) and cv[i] == "V":
            syll = "CVV"
            i += 1

        c_start = i
        while i < len(cv) and cv[i] == "C":
            i += 1
        c_count = i - c_start

        if i >= len(cv):
            coda = min(2, c_count)
            if coda == 1:
                syll += "C"
            elif coda == 2:
                syll += "CC"
            syllables.append(syll)
            break

        coda = min(2, max(0, c_count - 1))
        if coda == 1:
            syll += "C"
        elif coda == 2:
            syll += "CC"

        i = c_start + coda
        syllables.append(syll)

    # Full-consumption check
    consumed = "".join(syllables)
    if consumed != cv:
        leftover = cv[len(consumed):]
        return None, f"cv_not_fully_consumed:{leftover}"

    return syllables, None


def extract_syllable_text(word: str, cv_pattern: str, syll_pattern: str, start_pos: int) -> Tuple[str, str, str]:
    """
    Extract actual text for a syllable from the word.
    
    Returns:
        (syllable_text, onset, nucleus, coda)
    """
    # This is a simplified version - full implementation would track character positions
    # For now, return pattern as placeholder
    return syll_pattern, "C", "V", ""


# =============================================================================
# Main Syllabifier
# =============================================================================

class ArabicSyllabifier:
    """
    Arabic syllabifier implementing C2b phonological analysis.
    
    Usage:
        syllabifier = ArabicSyllabifier()
        result = syllabifier.syllabify("كَاتِبٌ")
        print(result)
    """
    
    def __init__(self):
        pass
    
    def syllabify(self, word: str) -> SyllabificationResult:
        """
        Main syllabification method.
        
        Args:
            word: Arabic word (with or without harakat)
        
        Returns:
            SyllabificationResult object
        """
        original = word
        
        # Step 1: Normalize
        normalized = normalize_initial_hamza(normalize_word(word))
        
        # Step 2: Generate CV pattern
        cv_pattern = word_to_cv_pattern(normalized)
        
        # Step 3: Validate
        valid, error = validate_cv_law(cv_pattern)
        if not valid:
            return SyllabificationResult(
                original=original,
                normalized=normalized,
                syllables=[],
                cv_pattern=cv_pattern,
                valid=False,
                error=error
            )
        
        # Step 4: Strict segmentation into syllables
        syll_patterns, seg_error = segment_cv_strict(cv_pattern)
        if seg_error is not None:
            return SyllabificationResult(
                original=original,
                normalized=normalized,
                syllables=[],
                cv_pattern=cv_pattern,
                valid=False,
                error=seg_error,
            )

        # Step 5: Create Syllable objects
        syllables = []
        pos = 0
        for i, pattern in enumerate(syll_patterns):
            syll_type = self._pattern_to_type(pattern)
            if syll_type is None:
                return SyllabificationResult(
                    original=original,
                    normalized=normalized,
                    syllables=[],
                    cv_pattern=cv_pattern,
                    valid=False,
                    error=f"unrecognized_syllable_pattern:{pattern}",
                )
            text, onset, nucleus, coda = extract_syllable_text(normalized, cv_pattern, pattern, pos)
            
            syll = Syllable(
                text=text,
                pattern=pattern,
                syllable_type=syll_type,
                onset=onset,
                nucleus=nucleus,
                coda=coda,
                position=pos
            )
            syllables.append(syll)
            pos += len(pattern)
        
        return SyllabificationResult(
            original=original,
            normalized=normalized,
            syllables=syllables,
            cv_pattern=cv_pattern,
            valid=True,
            error=None
        )
    
    def _pattern_to_type(self, pattern: str) -> Optional[SyllableType]:
        """Map pattern string to SyllableType enum. Returns None for unrecognized patterns."""
        try:
            return SyllableType(pattern)
        except ValueError:
            return None
    
    def syllabify_batch(self, words: List[str]) -> List[SyllabificationResult]:
        """Syllabify multiple words."""
        return [self.syllabify(w) for w in words]


# =============================================================================
# Convenience Functions
# =============================================================================

def syllabify(word: str) -> SyllabificationResult:
    """Quick syllabification of a single word."""
    syllabifier = ArabicSyllabifier()
    return syllabifier.syllabify(word)


def syllabify_to_pattern(word: str) -> str:
    """Quick conversion to CV pattern string."""
    normalized = normalize_initial_hamza(normalize_word(word))
    return word_to_cv_pattern(normalized)


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    """CLI for testing syllabification."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m fvafk.c2b.syllabifier <word1> <word2> ...")
        print("\nExample:")
        print("  python -m fvafk.c2b.syllabifier كَاتِبٌ كِتَابٌ مَكْتُوبٌ")
        sys.exit(1)
    
    syllabifier = ArabicSyllabifier()
    
    for word in sys.argv[1:]:
        result = syllabifier.syllabify(word)
        print(result)
        print()


if __name__ == "__main__":
    main()
