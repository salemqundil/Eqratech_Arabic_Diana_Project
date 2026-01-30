from typing import List

from ..gate_framework import GateResult, GateStatus, PhonologicalGate
from ..syllable import Segment, SegmentKind, VowelKind


class GateShadda(PhonologicalGate):
    def __init__(self):
        super().__init__(gate_id="G_SHADDA")

    def apply(self, segments: List[Segment]) -> GateResult:
        result: List[Segment] = []
        i = 0
        while i < len(segments):
            current = segments[i]
            if (
                i + 1 < len(segments)
                and current.kind == SegmentKind.CONSONANT
                and segments[i + 1].kind == SegmentKind.VOWEL
                and segments[i + 1].vk == VowelKind.SHADDA
            ):
                next_vowel = segments[i + 2] if i + 2 < len(segments) else None
                result.append(current)
                result.append(
                    Segment(text="", kind=SegmentKind.VOWEL, vk=VowelKind.SUKUN)
                )
                result.append(current)
                if next_vowel:
                    result.append(next_vowel)
                    i += 3
                else:
                    result.append(
                        Segment(text="", kind=SegmentKind.VOWEL, vk=VowelKind.FATHA)
                    )
                    i += 2
            else:
                result.append(current)
                i += 1

        status = GateStatus.ACCEPT
        reason = "shadda expanded"
        if result != segments:
            status = GateStatus.REPAIR
            reason = "shadda geminated"

        return GateResult(status=status, output=result, reason=reason)
