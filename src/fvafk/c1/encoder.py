"""
C1Encoder: Simplified Phase 1 text encoder.
"""

from __future__ import annotations

from typing import Dict, List

from ..orthography_adapter import OrthographyAdapter
from ..c2a.syllable import Segment, SegmentKind, VowelKind
from .unit import UnitCategory


HARAKAT_MAP: Dict[str, VowelKind] = {
    "َ": VowelKind.FATHA,
    "ُ": VowelKind.DAMMA,
    "ِ": VowelKind.KASRA,
    "ْ": VowelKind.SUKUN,
    "ّ": VowelKind.SHADDA,
    "ً": VowelKind.TANWIN_FATH,
    "ٌ": VowelKind.TANWIN_DAMM,
    "ٍ": VowelKind.TANWIN_KASR,
}


class C1Encoder:
    """Simple encoder that converts Arabic text into C1 segments."""

    def __init__(self) -> None:
        self.adapter = OrthographyAdapter()

    def encode(self, text: str) -> List[Unit]:
        segments: List = []
        for char in text:
            if char.isspace():
                continue
            category = HARAKAT_MAP.get(char)
            if category is not None:
                segments.append(
                    Segment(text=char, kind=SegmentKind.VOWEL, vk=HARAKAT_MAP[char])
                )
            else:
                normalized = self.adapter.normalize(char)
                if not normalized:
                    continue
                segments.append(Segment(text=normalized, kind=SegmentKind.CONSONANT))
        return segments
