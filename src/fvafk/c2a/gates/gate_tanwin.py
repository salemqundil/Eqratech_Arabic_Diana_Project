from typing import List

from ..gate_framework import GateResult, GateStatus, PhonologicalGate
from ..syllable import Segment, SegmentKind, VowelKind


class GateTanwin(PhonologicalGate):
    def __init__(self):
        super().__init__(gate_id="G_TANWIN")
        self.TANWIN_KINDS = {
            VowelKind.TANWIN_FATH,
            VowelKind.TANWIN_DAMM,
            VowelKind.TANWIN_KASR,
        }
        self.TANWIN_TO_VOWEL = {
            VowelKind.TANWIN_FATH: VowelKind.FATHA,
            VowelKind.TANWIN_DAMM: VowelKind.DAMMA,
            VowelKind.TANWIN_KASR: VowelKind.KASRA,
        }
        self.NOON_CID = 12

    def apply(self, segments: List[Segment]) -> GateResult:
        result: List[Segment] = []
        count = 0

        for seg in segments:
            if seg.kind == SegmentKind.VOWEL and seg.vk in self.TANWIN_KINDS:
                count += 1
                vowel = self.TANWIN_TO_VOWEL[seg.vk]
                result.append(Segment(text=self._vowel_mark(vowel), kind=SegmentKind.VOWEL, vk=vowel))
                result.append(Segment(text="ن", kind=SegmentKind.CONSONANT, cid=self.NOON_CID))
                result.append(Segment(text="ْ", kind=SegmentKind.VOWEL, vk=VowelKind.SUKUN))
            else:
                result.append(seg)

        status = GateStatus.ACCEPT
        reason = f"Tanwin converted ({count} instances)"
        if count > 0:
            status = GateStatus.REPAIR

        return GateResult(
            status=status,
            output=result,
            reason=reason,
            deltas=[f"tanwin_expanded_{i}" for i in range(count)],
        )

    def _vowel_mark(self, vk: VowelKind) -> str:
        return {
            VowelKind.FATHA: "َ",
            VowelKind.DAMMA: "ُ",
            VowelKind.KASRA: "ِ",
        }.get(vk, "")
