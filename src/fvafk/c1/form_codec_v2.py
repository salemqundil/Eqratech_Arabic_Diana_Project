#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FormCodecV2 (reversible):
- encode(text)  -> FormStream (list of GraphemeToken + metadata)
- decode(stream)-> original text EXACTLY (NFC)

Design goals:
1) Reversible by construction (decode(encode(w)) == w)
2) Extensible (flags/features can be added without breaking reversibility)
3) Trace-ready (tokens have stable ids/positions + optional spans)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
from typing import Dict, List, Optional, Tuple
import unicodedata


# -----------------------------
# Unicode categories / utilities
# -----------------------------
TATWEEL = "\u0640"

# Arabic diacritics / marks currently handled (extendable)
AR_MARKS = {
    "\u064b",
    "\u064c",
    "\u064d",  # tanwin
    "\u064e",
    "\u064f",
    "\u0650",  # fatha/damma/kasra
    "\u0651",
    "\u0652",  # shadda/sukun
    "\u0670",  # dagger alif
}


def is_mark(ch: str) -> bool:
    return unicodedata.combining(ch) != 0


def is_arabic_letter(ch: str) -> bool:
    return ("\u0600" <= ch <= "\u06FF") and unicodedata.category(ch).startswith("L")


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# -----------------------------
# Inventory (extensible)
# -----------------------------
class GraphemeClass(str, Enum):
    AR_LETTER = "AR_LETTER"
    AR_MARK = "AR_MARK"
    PUNCT = "PUNCT"
    SPACE = "SPACE"
    OTHER = "OTHER"


@dataclass(frozen=True)
class Inventory:
    """
    Minimal inventory:
    - inventory_id: a versioned identifier (e.g. 'inv_ar_v02')
    - allowed marks/letters can be extended (doesn't break decode)
    """

    inventory_id: str = "inv_ar_v02"
    allowed_marks: frozenset[str] = frozenset(AR_MARKS)

    def classify(self, ch: str) -> GraphemeClass:
        if ch == " ":
            return GraphemeClass.SPACE
        if is_mark(ch):
            return GraphemeClass.AR_MARK if ch in self.allowed_marks else GraphemeClass.OTHER
        if is_arabic_letter(ch):
            return GraphemeClass.AR_LETTER
        cat = unicodedata.category(ch)
        if cat.startswith("P"):
            return GraphemeClass.PUNCT
        return GraphemeClass.OTHER


# -----------------------------
# Core token types
# -----------------------------
@dataclass
class GraphemeToken:
    """
    A reversible token representing ONE base character plus its attached marks.
    - base: single unicode char (letter/punct/space/etc)
    - marks: list of combining marks attached to base (order preserved)
    - pos: position index in token stream (stable)
    - span: (start,end) indices in original string, optional (for trace)
    - flags: for future use BUT decode does NOT depend on them
    """

    base: str
    marks: List[str] = field(default_factory=list)
    pos: int = 0
    span: Optional[Tuple[int, int]] = None
    flags: Dict[str, str] = field(default_factory=dict)

    def to_text(self) -> str:
        return self.base + "".join(self.marks)


@dataclass(frozen=True)
class FormStream:
    """
    Reversible representation of a word/string.
    - tokens preserve full orthography
    - checksum can be used for trace / identity
    """

    inventory_id: str
    tokens: List[GraphemeToken]
    checksum: str  # hash of the exact decoded text (or canonical form)
    original_nfc: str  # exact NFC string we encoded

    def decode(self) -> str:
        return "".join(t.to_text() for t in self.tokens)


# -----------------------------
# Encoder/Decoder
# -----------------------------
class FormCodecV2:
    def __init__(self, inventory: Optional[Inventory] = None, keep_tatweel: bool = True):
        self.inv = inventory or Inventory()
        self.keep_tatweel = keep_tatweel

    def encode(self, text: str) -> FormStream:
        """
        Encode preserves exact NFC of the input by default.
        If you want to normalize (e.g., remove tatweel) do it OUTSIDE this codec
        as a *gate* so trace can record it. Keeping codec purely reversible is cleaner.
        """
        if text is None:
            text = ""
        original = nfc(str(text))
        # optionally keep/remove tatweel inside codec; recommended keep=True for strict reversibility
        if not self.keep_tatweel:
            original = original.replace(TATWEEL, "")

        tokens: List[GraphemeToken] = []
        current_base: Optional[str] = None
        current_marks: List[str] = []
        base_start: Optional[int] = None

        def flush(base_char: str, marks: List[str], start: int, end: int) -> None:
            pos = len(tokens)
            tokens.append(GraphemeToken(base=base_char, marks=list(marks), pos=pos, span=(start, end)))

        i = 0
        while i < len(original):
            ch = original[i]
            cls = self.inv.classify(ch)

            if cls == GraphemeClass.AR_MARK:
                # mark must attach to previous base; if none, attach to a synthetic base
                if current_base is None:
                    # attach to U+FEFF (ZERO WIDTH NO-BREAK SPACE) as synthetic base
                    current_base = "\ufeff"
                    current_marks = []
                    base_start = i
                current_marks.append(ch)
                i += 1
                continue

            # base char (letter/space/punct/other)
            if current_base is not None and base_start is not None:
                flush(current_base, current_marks, base_start, i)
            current_base = ch
            current_marks = []
            base_start = i
            i += 1

        if current_base is not None and base_start is not None:
            flush(current_base, current_marks, base_start, len(original))

        decoded = "".join(t.to_text() for t in tokens)
        # Strict reversibility check (can be disabled in production)
        if decoded != original:
            raise ValueError("FormCodecV2 internal error: decode(encode(text)) != text (NFC).")

        checksum = stable_hash(original)
        return FormStream(
            inventory_id=self.inv.inventory_id,
            tokens=tokens,
            checksum=checksum,
            original_nfc=original,
        )

    def decode(self, stream: FormStream) -> str:
        # Decode is independent of flags/inventory evolution
        return stream.decode()

