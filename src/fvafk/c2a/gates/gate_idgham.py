"""
GateIdgham: Tajwid idgham rules

Implements the six core idgham targets (ي، ن، م، و، ل، ر)
by collapsing a noon-sakin / tanwin + target letter into a geminated consonant.
"""

from typing import List, Set, Tuple

from ..gate_framework import GateResult, GateStatus, PhonologicalGate
from ..syllable import Segment, SegmentKind, VowelKind


class GateIdgham(PhonologicalGate):
    def __init__(self) -> None:
        super().__init__(gate_id="G_IDGHAM")
        self.NOON_CHAR = "ن"
        self.IDGHAM_GHUNNAH_LETTERS: Set[str] = {"ي", "ن", "م", "و"}
        self.IDGHAM_NO_GHUNNAH_LETTERS: Set[str] = {"ل", "ر"}
        self.ALL_IDGHAM_LETTERS: Set[str] = (
            self.IDGHAM_GHUNNAH_LETTERS | self.IDGHAM_NO_GHUNNAH_LETTERS
        )

    def apply(self, segments: List[Segment]) -> GateResult:
        result, changes = self._apply_noon_idgham(segments)
        status = GateStatus.ACCEPT
        reason = f"idgham applied ({len(changes)} changes)"
        return GateResult(
            status=status,
            output=result,
            reason=reason,
            deltas=changes,
        )

    def _apply_noon_idgham(
        self, segments: List[Segment]
    ) -> Tuple[List[Segment], List[str]]:
        result: List[Segment] = []
        changes: List[str] = []
        i = 0

        while i < len(segments):
            if self._is_noon_idgham_pattern(segments, i):
                idgham_letter = segments[i + 2]
                result.append(Segment(text=idgham_letter.text, kind=SegmentKind.CONSONANT))
                result.append(
                    Segment(
                        text="ّ",
                        kind=SegmentKind.VOWEL,
                        vk=VowelKind.SHADDA,
                    )
                )
                if idgham_letter.text in self.IDGHAM_GHUNNAH_LETTERS:
                    changes.append(f"idgham_ghunnah_{idgham_letter.text}")
                else:
                    changes.append(f"idgham_no_ghunnah_{idgham_letter.text}")
                i += 3
                continue
            result.append(segments[i])
            i += 1

        return result, changes

    def _is_noon_idgham_pattern(self, segments: List[Segment], offset: int) -> bool:
        if offset + 2 >= len(segments):
            return False

        noon = segments[offset]
        sukun = segments[offset + 1]
        letter = segments[offset + 2]

        if noon.kind != SegmentKind.CONSONANT:
            return False
        if noon.text != self.NOON_CHAR:
            return False
        if sukun.kind != SegmentKind.VOWEL or sukun.vk != VowelKind.SUKUN:
            return False
        if letter.kind != SegmentKind.CONSONANT:
            return False
        if letter.text not in self.ALL_IDGHAM_LETTERS:
            return False

        return True
