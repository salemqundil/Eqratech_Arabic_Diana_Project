"""
GateWasl: repair illegal initial sukun by inserting a prothetic kasra.

Arabic syllables cannot start with a consonant carrying sukun (Cْ) in isolation.
In connected speech, this is typically repaired via hamzat-wasl / prothesis.

We implement a conservative rule:
- If the token begins with: CONSONANT + SUKUN, change that SUKUN into KASRA.

This turns an initial cluster like: لْيَ... into لِـيَ...
and helps remove leading CC/CCC artifacts in CV computed after phonology.
"""

from __future__ import annotations

from typing import List

from ..gate_framework import GateResult, GateStatus, PhonologicalGate
from ..syllable import Segment, SegmentKind, VowelKind


class GateWasl(PhonologicalGate):
    def __init__(self) -> None:
        super().__init__(gate_id="G_WASL")

    def apply(self, segments: List[Segment]) -> GateResult:
        if len(segments) < 2:
            return GateResult(
                status=GateStatus.ACCEPT,
                output=list(segments),
                reason="wasl: too short",
                deltas=[],
            )

        # Case 1: initial consonant + explicit sukun -> convert to kasra (prothesis)
        first, second = segments[0], segments[1]
        if first.kind == SegmentKind.CONSONANT and second.kind == SegmentKind.VOWEL and second.vk == VowelKind.SUKUN:
            output = list(segments)
            output[1] = Segment(text="ِ", kind=SegmentKind.VOWEL, vk=VowelKind.KASRA)
            return GateResult(
                status=GateStatus.REPAIR,
                output=output,
                reason="wasl: initial sukun repaired to kasra",
                deltas=["initial_sukun_to_kasra:1"],
            )

        # Case 2: illegal initial consonant cluster (CC...) with no vowel yet -> insert kasra
        if first.kind == SegmentKind.CONSONANT and second.kind == SegmentKind.CONSONANT:
            output = list(segments)
            output.insert(1, Segment(text="ِ", kind=SegmentKind.VOWEL, vk=VowelKind.KASRA))
            return GateResult(
                status=GateStatus.REPAIR,
                output=output,
                reason="wasl: initial consonant cluster repaired by kasra",
                deltas=["initial_cluster_insert_kasra:1"],
            )

        return GateResult(
            status=GateStatus.ACCEPT,
            output=list(segments),
            reason="wasl: ok",
            deltas=[],
        )

