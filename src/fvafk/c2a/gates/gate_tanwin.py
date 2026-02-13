"""
GateTanwin: expand tanwin into short vowel + nunation.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from ..gate_framework import GateResult, GateStatus, PhonologicalGate
from ..syllable import Segment, SegmentKind, VowelKind


class GateTanwin(PhonologicalGate):
    def __init__(self) -> None:
        super().__init__(gate_id="G_TANWIN")
        self._tanwin_map = {
            VowelKind.TANWIN_FATH: VowelKind.FATHA,
            VowelKind.TANWIN_DAMM: VowelKind.DAMMA,
            VowelKind.TANWIN_KASR: VowelKind.KASRA,
        }

    def apply(self, segments: List[Segment]) -> GateResult:
        output: List[Segment] = []
        deltas: List[str] = []

        for idx, seg in enumerate(segments):
            if seg.kind == SegmentKind.VOWEL and seg.vk in self._tanwin_map:
                short_vk = self._tanwin_map[seg.vk]
                output.append(Segment(text=seg.text, kind=SegmentKind.VOWEL, vk=short_vk))
                output.append(Segment(text="ن", kind=SegmentKind.CONSONANT))
                output.append(Segment(text="ْ", kind=SegmentKind.VOWEL, vk=VowelKind.SUKUN))
                deltas.append(f"tanwin_expanded:{idx}")
            else:
                output.append(seg)

        status = GateStatus.REPAIR if deltas else GateStatus.ACCEPT

        return GateResult(
            status=status,
            output=output,
            reason=f"tanwin expanded: {len(deltas)}",
            deltas=deltas,
        )
