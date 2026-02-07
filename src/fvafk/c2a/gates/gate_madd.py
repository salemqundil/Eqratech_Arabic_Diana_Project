"""
GateMadd: Vowel lengthening detection.

Covers the main madd types (tabii, munfasil, muttasil, lazim, arid, lin)
by inspecting Arabic madd letters (ا، و، ي) and their context.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Set, Tuple

from ..gate_framework import GateResult, GateStatus, PhonologicalGate
from ..syllable import Segment, SegmentKind, VowelKind


class MaddType(Enum):
    TABII = "natural"
    MUNFASIL = "separate"
    MUTTASIL = "connected"
    LAZIM = "necessary"
    ARID = "accidental"
    LIN = "soft"


class GateMadd(PhonologicalGate):
    def __init__(self) -> None:
        super().__init__(gate_id="G_MADD")
        self.MADD_LETTERS: Set[str] = {"ا", "و", "ي"}
        self.HAMZA_LETTERS: Set[str] = {"ء", "أ", "إ", "ؤ", "ئ", "آ"}
        self.LIN_LETTERS: Set[str] = {"و", "ي"}

    def apply(self, segments: List[Segment]) -> GateResult:
        changes: List[str] = []
        result = list(segments)
        for i in range(len(segments)):
            madd_info = self._detect_madd(segments, i)
            if madd_info:
                madd_type, duration = madd_info
                changes.append(f"madd_{madd_type.value}_{duration}h")

        return GateResult(
            status=GateStatus.ACCEPT,
            output=result,
            reason=f"madd detected ({len(changes)} hits)",
            deltas=changes,
        )

    def _detect_madd(
        self, segments: List[Segment], index: int
    ) -> Optional[Tuple[MaddType, int]]:
        if index == 0 or index >= len(segments):
            return None

        seg = segments[index]
        prev = segments[index - 1]
        if seg.kind != SegmentKind.CONSONANT or seg.text not in self.MADD_LETTERS:
            return None
        if prev.kind != SegmentKind.VOWEL:
            return None

        if not self._is_valid_madd_context(prev.vk, seg.text):
            return None

        if self._is_madd_lazim(segments, index):
            return MaddType.LAZIM, 6
        if self._is_madd_muttasil(segments, index):
            return MaddType.MUTTASIL, 5
        if self._is_madd_munfasil(segments, index):
            return MaddType.MUNFASIL, 4
        if self._is_madd_arid(segments, index):
            return MaddType.ARID, 2
        if self._is_madd_lin(segments, index):
            return MaddType.LIN, 2

        return MaddType.TABII, 2

    def _is_valid_madd_context(self, prev_vk: Optional[VowelKind], madd_char: str) -> bool:
        if prev_vk is None:
            return False

        return (
            (madd_char == "ا" and prev_vk == VowelKind.FATHA)
            or (madd_char == "و" and prev_vk == VowelKind.DAMMA)
            or (madd_char == "ي" and prev_vk == VowelKind.KASRA)
        )

    def _is_madd_lazim(self, segments: List[Segment], index: int) -> bool:
        if index + 1 >= len(segments):
            return False
        next_seg = segments[index + 1]
        if next_seg.kind == SegmentKind.VOWEL and next_seg.vk == VowelKind.SHADDA:
            return True
        if index + 2 < len(segments):
            after_sukun = segments[index + 2]
            if (
                next_seg.kind == SegmentKind.VOWEL
                and next_seg.vk == VowelKind.SUKUN
                and after_sukun.kind == SegmentKind.CONSONANT
            ):
                return True
        return False

    def _is_madd_muttasil(self, segments: List[Segment], index: int) -> bool:
        for j in range(index + 1, min(len(segments), index + 5)):
            seg = segments[j]
            if seg.kind == SegmentKind.CONSONANT and seg.text in self.HAMZA_LETTERS:
                return True
        return False

    def _is_madd_munfasil(self, segments: List[Segment], index: int) -> bool:
        # Simplified: look beyond a short gap for hamza/word boundary
        for j in range(index + 2, min(len(segments), index + 7)):
            seg = segments[j]
            if seg.kind == SegmentKind.CONSONANT and seg.text in self.HAMZA_LETTERS:
                return True
        return False

    def _is_madd_arid(self, segments: List[Segment], index: int) -> bool:
        if index + 1 >= len(segments):
            return False
        next_seg = segments[index + 1]
        if next_seg.kind == SegmentKind.VOWEL and next_seg.vk == VowelKind.SUKUN:
            return True
        return False

    def _is_madd_lin(self, segments: List[Segment], index: int) -> bool:
        if index == 0 or index + 1 >= len(segments):
            return False
        seg = segments[index]
        if seg.text not in self.LIN_LETTERS:
            return False
        prev = segments[index - 1]
        next_seg = segments[index + 1]
        return (
            prev.kind == SegmentKind.VOWEL
            and prev.vk == VowelKind.FATHA
            and next_seg.kind == SegmentKind.VOWEL
            and next_seg.vk == VowelKind.SUKUN
        )
