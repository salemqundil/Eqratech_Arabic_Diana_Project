from __future__ import annotations

import re
from typing import List, Tuple, Dict

# Arabic diacritics of interest
FATHA = "\u064E"  # F
DAMMA = "\u064F"  # D
KASRA = "\u0650"  # K
SUKUN = "\u0652"  # S
TANWEEN_FATH = "\u064B"
TANWEEN_DAMM = "\u064C"
TANWEEN_KASR = "\u064D"

DIAC_TO_CODE = {
    FATHA: "F",
    DAMMA: "D",
    KASRA: "K",
    SUKUN: "S",
    TANWEEN_FATH: "F",  # collapse tanween to base vowel for counting
    TANWEEN_DAMM: "D",
    TANWEEN_KASR: "K",
}

ARABIC_LETTER_RE = re.compile(r"[\u0621-\u064A\u0660-\u0669\u0670\u0671-\u06D3]")
ARABIC_DIAC_RE = re.compile(r"[\u064B-\u0652]")
SPACE_SPLIT_RE = re.compile(r"\s+")

ALEF_VARIANTS = str.maketrans({
    "أ": "ا",
    "إ": "ا",
    "آ": "ا",
    "ى": "ي",  # alif maqsurah to ya
})


def normalize_word(word: str) -> str:
    """Normalize Arabic word by unifying alef variants and removing tatweel.
    Keep base Arabic letters and punctuation/marks as-is.
    """
    if not isinstance(word, str):
        return ""
    w = word.replace("\u0640", "")  # tatweel
    w = w.translate(ALEF_VARIANTS)
    return w


def attach_diacritics(word: str) -> Tuple[List[Tuple[str, str]], List[str]]:
    """Affix-to-Base: assign diacritics to the nearest previous Arabic base letter.

    Returns:
      - chars_with_diac: list of (char, diac_code or "")
      - diac_sequence: list of diac_code in order (skipping blanks)
    """
    word = normalize_word(word)
    chars_with_diac: List[Tuple[str, str]] = []
    diac_seq: List[str] = []

    for ch in word:
        if ARABIC_DIAC_RE.match(ch):
            code = DIAC_TO_CODE.get(ch, "")
            if chars_with_diac:
                base_ch, _ = chars_with_diac[-1]
                chars_with_diac[-1] = (base_ch, code)
                if code:
                    diac_seq.append(code)
            # if no base char yet, ignore leading diacritic safely
        else:
            chars_with_diac.append((ch, ""))

    return chars_with_diac, diac_seq


def tokenize_text(text: str) -> List[str]:
    """Tokenize on whitespace and simple punctuation while preserving Arabic words.
    This is a light tokenizer for educational stats, not a full Arabic segmenter.
    """
    if not text:
        return []
    # Replace common punctuation with space
    cleaned = re.sub(r"[\.,;:\-\!\?\(\)\[\]{}\"'،؛؟ـ]", " ", text)
    tokens = [t for t in SPACE_SPLIT_RE.split(cleaned) if t]
    return tokens


def strip_diacritics(text: str) -> str:
    """Remove Arabic diacritics, keep letters only."""
    return ARABIC_DIAC_RE.sub("", text)


def diac_counts_from_sequence(seq: List[str]) -> Dict[str, int]:
    d = {"F": 0, "D": 0, "K": 0, "S": 0}
    for s in seq:
        if s in d:
            d[s] += 1
    return d
