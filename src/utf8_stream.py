"""Deterministic UTF-8 separation for Arabic phoneme/diacritics vs. other symbols.

This module exposes helpers to:
- Classify a single Unicode char as C/DIAC/AUX/IGN
- Build an affix-to-base phoneme stream (PhonemeChar) and an ignored list
- Provide convenience functions for notebook use
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, TypedDict
import re
from collections import Counter

# Arabic base letters (ء..ي)
RE_AR_LETTER = re.compile(r"[\u0621-\u064A]")

# Core short diacritics we care about for learning: F/K/D/S
DIAC2LBL: Dict[str, str] = {
    "\u064E": "F",  # Fatha  َ
    "\u0650": "K",  # Kasra  ِ
    "\u064F": "D",  # Damma  ُ
    "\u0652": "S",  # Sukun  ْ
}

# Auxiliary diacritics (do not change dia label but may appear in raw)
AUX_DIAC = {
    "\u0651",  # Shadda  ّ
    "\u064B",  # Tanween Fath  ً
    "\u064C",  # Tanween Damm  ٌ
    "\u064D",  # Tanween Kasr  ٍ
    "\u0653",  # Maddah  ٓ
    "\u0670",  # Superscript Alef  ٰ
}

# Quranic annotation range (decorative/annotation marks) → ignore in phoneme analysis
RE_QURAN_ANNOT = re.compile(r"[\u06D6-\u06ED]")

# Tatweel (kashida) → ignore
TATWEEL = "\u0640"

# Long vowels considered as letters (phonemic): alif, waw, ya
LONG_VOWELS = {"ا", "و", "ي"}


def classify_char(ch: str) -> str:
    """Classify a single character.

    Returns one of:
      - 'C'    : Arabic base letter (phoneme/long vowel)
      - 'DIAC' : short diacritic (F/K/D/S)
      - 'AUX'  : auxiliary diacritic (shadda/tanween/maddah/superscript alef)
      - 'IGN'  : everything else (spaces, punctuation, Latin, digits, Quranic marks, tatweel)
    """
    if ch in DIAC2LBL:
        return "DIAC"
    if ch in AUX_DIAC:
        return "AUX"
    if ch == TATWEEL:
        return "IGN"
    if RE_QURAN_ANNOT.match(ch):
        return "IGN"
    if RE_AR_LETTER.match(ch):
        return "C"
    return "IGN"


@dataclass
class PhonemeChar:
    ch: str               # Arabic base letter
    dia: Optional[str]    # 'F'/'K'/'D'/'S' if present, else None
    raw: str              # raw glyph(s) seen (may include AUX)
    idx: int              # index in original text


def extract_streams(text: str, *, strict_aux: bool = False) -> Tuple[List[PhonemeChar], List[Tuple[int, str, str]]]:
    """Build the phoneme stream (with affix-to-base diacritics) and the ignored list.

    Returns:
      - stream: list of PhonemeChar (Arabic letters with an optional F/K/D/S)
      - ignored: list of (idx, char, class) for documentation/inspection
    """
    stream: List[PhonemeChar] = []
    ignored: List[Tuple[int, str, str]] = []
    last_idx_char: Optional[int] = None

    for i, ch in enumerate(text):
        cls = classify_char(ch)
        if cls == "C":
            stream.append(PhonemeChar(ch=ch, dia=None, raw=ch, idx=i))
            last_idx_char = len(stream) - 1
        elif cls == "DIAC":
            if last_idx_char is not None:
                stream[last_idx_char].dia = DIAC2LBL[ch]
                stream[last_idx_char].raw += ch
            else:
                ignored.append((i, ch, "DIAC_orphan"))
        elif cls == "AUX":
            if strict_aux:
                ignored.append((i, ch, "AUX" if last_idx_char is not None else "AUX_orphan"))
            else:
                if last_idx_char is not None:
                    stream[last_idx_char].raw += ch
                else:
                    ignored.append((i, ch, "AUX_orphan"))
        else:
            ignored.append((i, ch, "IGN"))
            last_idx_char = None

    return stream, ignored


def filter_to_phoneme_text(text: str, *, strict_aux: bool = False) -> str:
    """Return a text containing only the phoneme stream raw forms (letters + attached marks)."""
    stream, _ = extract_streams(text, strict_aux=strict_aux)
    return "".join(pc.raw for pc in stream)


def drop_non_phoneme(text: str, *, strict_aux: bool = False) -> List[PhonemeChar]:
    """Return only the stream of Arabic letters with optional F/K/D/S for downstream processing."""
    stream, _ = extract_streams(text, strict_aux=strict_aux)
    return stream


class IgnoredRow(TypedDict):
    char: str
    codepoint: str
    class_: str
    count: int


def summarize_ignored(ignored: List[Tuple[int, str, str]]) -> List[IgnoredRow]:
    """Summarize ignored characters by (char, class) with counts and codepoints.

    Returns list of dict rows suitable for DataFrame display in notebooks.
    """
    ctr = Counter((ch, cls) for _, ch, cls in ignored)
    rows: List[IgnoredRow] = []
    for (ch, cls), count in ctr.items():
        rows.append({  # type: ignore[typeddict-item]
            "char": ch,
            "codepoint": f"U+{ord(ch):04X}",
            "class_": cls,
            "count": int(count),
        })
    # sort by count desc
    rows.sort(key=lambda r: r["count"], reverse=True)
    return rows


def save_ignored_csv(path: str, ignored_rows: List[IgnoredRow]) -> None:
    """Save ignored summary to CSV (path can be relative)."""
    import csv

    fieldnames = ["char", "codepoint", "class_", "count"]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in ignored_rows:
            w.writerow(r)


__all__ = [
    "RE_AR_LETTER",
    "DIAC2LBL",
    "AUX_DIAC",
    "RE_QURAN_ANNOT",
    "TATWEEL",
    "LONG_VOWELS",
    "classify_char",
    "PhonemeChar",
    "extract_streams",
    "filter_to_phoneme_text",
    "drop_non_phoneme",
    "summarize_ignored",
    "save_ignored_csv",
]
