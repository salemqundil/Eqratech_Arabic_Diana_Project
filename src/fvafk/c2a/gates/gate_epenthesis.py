"""
GateEpenthesis: insert kasra to break clusters.
"""

from __future__ import annotations

from typing import List, Set

from ..gate_framework import GateResult, GateStatus, PhonologicalGate
from ..syllable import Segment, SegmentKind, VowelKind


class GateEpenthesis(PhonologicalGate):
    CONSONANTS: Set[str] = {
        "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز",
        "س", "ش", "ص", "ض", "ط", "ظ", "ع", "غ", "ف", "ق",
        "ك", "ل", "م", "ن", "ه", "و", "ي",
    }

    SUKUN = VowelKind.SUKUN

    def __init__(self) -> None:
        super().__init__(gate_id="G_EPENTHESIS")

    def precondition(self, segments: List[Segment]) -> bool:
        count = 0
        for idx, seg in enumerate(segments):
            if seg.kind == SegmentKind.CONSONANT and seg.text in self.CONSONANTS:
                count += 1
                if idx + 1 < len(segments):
                    next_seg = segments[idx + 1]
                    if next_seg.kind == SegmentKind.VOWEL and next_seg.vk == self.SUKUN:
                        if count >= 2:
                            return True
            elif seg.kind == SegmentKind.VOWEL:
                count = 0
        return False

    def apply(self, segments: List[Segment]) -> GateResult:
        output = list(segments)
        deltas: List[str] = []
        idx = 0
        while idx < len(output) - 3:
            c1, v1, c2, v2 = output[idx], output[idx + 1], output[idx + 2], output[idx + 3]
            if (
                c1.kind == SegmentKind.CONSONANT
                and v1.kind == SegmentKind.VOWEL
                and v1.vk == self.SUKUN
                and c2.kind == SegmentKind.CONSONANT
                and v2.kind == SegmentKind.VOWEL
                and v2.vk == self.SUKUN
            ):
                kasra = Segment(text="ِ", kind=SegmentKind.VOWEL, vk=VowelKind.KASRA)
                output.insert(idx + 3, kasra)
                deltas.append(f"insert_kasra:{idx+3}")
                idx += 4
            else:
                idx += 1

        status = GateStatus.REPAIR if deltas else GateStatus.ACCEPT

        return GateResult(
            status=status,
            output=output,
            reason=f"epenthesis inserts: {len(deltas)}",
            deltas=deltas,
        )
