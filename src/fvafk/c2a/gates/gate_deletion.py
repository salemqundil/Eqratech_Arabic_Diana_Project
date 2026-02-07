"""
GateDeletion: deletion of predictable segments (alif, hamza) in connected speech.
"""

from __future__ import annotations

from typing import Dict, List, Set

from ..gate_framework import GateResult, GateStatus, PhonologicalGate
from ..syllable import Segment, SegmentKind, VowelKind


class GateDeletion(PhonologicalGate):
    ALIF = "ا"
    LAM = "ل"
    HAMZA_WASL = "إ"

    VOWEL_SET = {
        VowelKind.FATHA,
        VowelKind.DAMMA,
        VowelKind.KASRA,
    }

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
        super().__init__(gate_id="G_DELETION")

    def precondition(self, segments: List[Segment]) -> bool:
        for idx, seg in enumerate(segments[:-1]):
            if seg.kind == SegmentKind.CONSONANT and seg.text == self.ALIF:
                next_seg = segments[idx + 1]
                if next_seg.kind == SegmentKind.CONSONANT and next_seg.text == self.LAM:
                    return True
        return any(
            seg.kind == SegmentKind.CONSONANT and seg.text == self.HAMZA_WASL
            for seg in segments
        )

    def apply(self, segments: List[Segment]) -> GateResult:
        output = list(segments)
        deltas: List[str] = []

        for idx in range(1, len(output)):
            prev = output[idx - 1]
            curr = output[idx]
            if (
                prev.kind == SegmentKind.VOWEL and prev.vk in self.VOWEL_SET
                and curr.kind == SegmentKind.CONSONANT
                and curr.text == self.ALIF
                and idx + 1 < len(output)
                and output[idx + 1].text == self.LAM
            ):
                output[idx] = Segment(
                    text=curr.text,
                    kind=curr.kind,
                    vk=curr.vk,
                    deleted=True,
                )
                deltas.append(f"delete_alif:{idx}")
            if (
                curr.kind == SegmentKind.CONSONANT
                and curr.text == self.HAMZA_WASL
                and prev.kind == SegmentKind.VOWEL
                and prev.vk in self.VOWEL_SET
            ):
                output[idx] = Segment(
                    text=curr.text,
                    kind=curr.kind,
                    vk=curr.vk,
                    deleted=True,
                )
                deltas.append(f"delete_hamza:{idx}")

        status = GateStatus.REPAIR if deltas else GateStatus.ACCEPT

        return GateResult(
            status=status,
            output=output,
            reason=f"deletions: {len(deltas)}",
            deltas=deltas,
        )
