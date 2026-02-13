"""
GateAssimilation: handles lam assimilation (al- + sun letters).
"""

from __future__ import annotations

from typing import List, Set

from ..gate_framework import GateResult, GateStatus, PhonologicalGate
from ..syllable import Segment, SegmentKind, VowelKind


class GateAssimilation(PhonologicalGate):
    ALIF = "ا"
    LAM = "ل"
    SUN_LETTERS: Set[str] = {
        "ت",
        "ث",
        "د",
        "ذ",
        "ر",
        "ز",
        "س",
        "ش",
        "ص",
        "ض",
        "ط",
        "ظ",
        "ل",
        "ن",
    }

    def __init__(self) -> None:
        super().__init__(gate_id="G_ASSIMILATION")

    def apply(self, segments: List[Segment]) -> GateResult:
        output: List[Segment] = []
        deltas: List[str] = []
        i = 0

        while i < len(segments):
            if self._is_sun_assimilation_pattern(segments, i):
                alif = segments[i]
                lam = segments[i + 1]
                sun = segments[i + 2]

                output.append(alif)
                output.append(
                    Segment(
                        text=lam.text,
                        kind=lam.kind,
                        vk=lam.vk,
                        deleted=True,
                    )
                )
                output.append(sun)

                next_is_shadda = (
                    i + 3 < len(segments)
                    and segments[i + 3].kind == SegmentKind.VOWEL
                    and segments[i + 3].vk == VowelKind.SHADDA
                )
                if not next_is_shadda:
                    output.append(
                        Segment(text="ّ", kind=SegmentKind.VOWEL, vk=VowelKind.SHADDA)
                    )
                deltas.append(f"lam_assimilated:{i+2}")
                i += 3
                continue

            output.append(segments[i])
            i += 1

        status = GateStatus.REPAIR if deltas else GateStatus.ACCEPT

        return GateResult(
            status=status,
            output=output,
            reason=f"assimilation: {len(deltas)}",
            deltas=deltas,
        )

    def _is_sun_assimilation_pattern(self, segments: List[Segment], index: int) -> bool:
        if index + 2 >= len(segments):
            return False
        alif = segments[index]
        lam = segments[index + 1]
        sun = segments[index + 2]
        if alif.kind != SegmentKind.CONSONANT or alif.text != self.ALIF:
            return False
        if lam.kind != SegmentKind.CONSONANT or lam.text != self.LAM:
            return False
        if sun.kind != SegmentKind.CONSONANT or sun.text not in self.SUN_LETTERS:
            return False
        return True
