from typing import List

from ..gate_framework import GateResult, GateStatus, PhonologicalGate
from ..syllable import Segment, SegmentKind, VowelKind


class GateSukun(PhonologicalGate):
    def __init__(self):
        super().__init__(gate_id="G_SUKUN")
        self.SUKUN = VowelKind.SUKUN
        self.FATHA = VowelKind.FATHA

    def precondition(self, segments: List[Segment]) -> bool:
        return any(
            seg.kind == SegmentKind.VOWEL and seg.vk == self.SUKUN
            for seg in segments
        )

    def apply(self, segments: List[Segment]) -> GateResult:
        result = [Segment(seg.text, seg.kind, seg.vk) for seg in segments]
        for i in range(len(result) - 3):
            if self._is_consonant(result[i]) and self._is_sukun(result[i + 1]):
                for j in range(i + 2, min(len(result) - 1, i + 10)):
                    if self._is_consonant(result[j]) and self._is_sukun(result[j + 1]):
                        result[i + 1] = Segment(
                            text=result[i + 1].text,
                            kind=SegmentKind.VOWEL,
                            vk=self.FATHA,
                        )
                        return GateResult(
                            status=GateStatus.REPAIR,
                            output=result,
                            reason="double-sukun repaired",
                        )
        return GateResult(
            status=GateStatus.ACCEPT,
            output=result,
            reason="no double sukun detected",
        )

    def postcondition(
        self, segments_in: List[Segment], segments_out: List[Segment]
    ) -> bool:
        return not self._has_double_sukun(segments_out)

    def _is_consonant(self, seg: Segment) -> bool:
        return seg.kind == SegmentKind.CONSONANT

    def _is_sukun(self, seg: Segment) -> bool:
        return seg.kind == SegmentKind.VOWEL and seg.vk == self.SUKUN

    def _has_double_sukun(self, segments: List[Segment]) -> bool:
        for i in range(len(segments) - 3):
            if self._is_consonant(segments[i]) and self._is_sukun(segments[i + 1]):
                for j in range(i + 2, min(len(segments) - 1, i + 10)):
                    if self._is_consonant(segments[j]) and self._is_sukun(segments[j + 1]):
                        return True
        return False
