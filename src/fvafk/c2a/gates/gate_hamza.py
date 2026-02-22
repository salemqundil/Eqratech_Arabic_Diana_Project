"""
GateHamza: Hamza placement rules for Arabic.

Adapts letter placement based on initial/medial/final context and vowel strength.
"""

from __future__ import annotations

import time
from typing import Dict, List, Optional, Set

from ..gate_framework import GateResult, GateStatus, PhonologicalGate
from ..syllable import Segment, SegmentKind, VowelKind


class GateHamza(PhonologicalGate):
    LONG_VOWEL_LETTERS: Set[str] = {"ا", "و", "ي"}

    ALL_HAMZA_FORMS: Set[str] = {"ء", "أ", "إ", "ؤ", "ئ"}

    VOWEL_STRENGTH: Dict[VowelKind, int] = {
        VowelKind.KASRA: 3,
        VowelKind.TANWIN_KASR: 3,
        VowelKind.DAMMA: 2,
        VowelKind.TANWIN_DAMM: 2,
        VowelKind.FATHA: 1,
        VowelKind.TANWIN_FATH: 1,
        VowelKind.SUKUN: 0,
    }

    def __init__(self) -> None:
        super().__init__(gate_id="G_HAMZA")
        self.initial_strength_map = {
            "kasra": "إ",
            "fatha": "أ",
            "damma": "أ",
        }

    def precondition(self, segments: List[Segment]) -> bool:
        return any(
            seg.kind == SegmentKind.CONSONANT and seg.text in self.ALL_HAMZA_FORMS
            for seg in segments
        )

    def apply(self, segments: List[Segment]) -> GateResult:
        start = time.time()
        output: List[Segment] = list(segments)
        deltas: List[str] = []

        for idx, seg in enumerate(output):
            if seg.kind != SegmentKind.CONSONANT or seg.text not in self.ALL_HAMZA_FORMS:
                continue

            position_type = self._get_position_type(output, idx)
            new_form = None

            if position_type == "initial":
                new_form = self._apply_initial_rule(output, idx)
            elif position_type == "medial":
                new_form = self._apply_medial_rule(output, idx)
            else:
                new_form = self._apply_final_rule(output, idx)

            if new_form and new_form != seg.text:
                output[idx] = Segment(text=new_form, kind=seg.kind, vk=seg.vk)
                deltas.append(f"{position_type}_hamza:{idx}")

        duration = (time.time() - start) * 1000
        status = GateStatus.REPAIR if deltas else GateStatus.ACCEPT
        reason = f"hamza placements: {len(deltas)}"

        return GateResult(
            status=status,
            output=output,
            reason=reason,
            deltas=deltas,
            latency_ms=duration,
        )

    def _get_position_type(self, segments: List[Segment], index: int) -> str:
        prev_letter = self._find_prev_consonant(segments, index)
        next_letter = self._find_next_consonant(segments, index)
        if prev_letter is None:
            return "initial"
        if next_letter is None:
            return "final"
        return "medial"

    def _find_prev_consonant(
        self, segments: List[Segment], index: int
    ) -> Optional[int]:
        for i in range(index - 1, -1, -1):
            if segments[i].kind == SegmentKind.CONSONANT:
                return i
        return None

    def _find_next_consonant(
        self, segments: List[Segment], index: int
    ) -> Optional[int]:
        for i in range(index + 1, len(segments)):
            if segments[i].kind == SegmentKind.CONSONANT:
                return i
        return None

    def _find_neighbor_vowel_strength(
        self, segments: List[Segment], index: int
    ) -> int:
        if 0 <= index < len(segments):
            seg = segments[index]
            if seg.kind == SegmentKind.VOWEL and seg.vk in self.VOWEL_STRENGTH:
                return self.VOWEL_STRENGTH[seg.vk]
        if 0 <= index + 1 < len(segments):
            seg = segments[index + 1]
            if seg.kind == SegmentKind.VOWEL and seg.vk in self.VOWEL_STRENGTH:
                return self.VOWEL_STRENGTH[seg.vk]
        return 0

    def _apply_initial_rule(self, segments: List[Segment], index: int) -> str:
        next_vowel_strength = self._find_neighbor_vowel_strength(segments, index)
        if next_vowel_strength == 3:
            return "إ"
        if next_vowel_strength >= 2:
            return "أ"
        return "أ"

    def _apply_medial_rule(self, segments: List[Segment], index: int) -> str:
        prev_strength = self._find_neighbor_vowel_strength(segments, index - 1)
        next_strength = self._find_neighbor_vowel_strength(segments, index + 1)
        strength = max(prev_strength, next_strength)
        if strength >= 3:
            return "ئ"
        if strength == 2:
            return "ؤ"
        if strength == 1:
            return "أ"

        prev_letter_idx = self._find_prev_consonant(segments, index)
        if prev_letter_idx is not None:
            prev_letter = segments[prev_letter_idx].text
            if prev_letter in self.LONG_VOWEL_LETTERS:
                return "ء"

        return "أ"

    def _apply_final_rule(self, segments: List[Segment], index: int) -> str:
        prev_letter_idx = self._find_prev_consonant(segments, index)
        if prev_letter_idx is not None:
            prev_letter = segments[prev_letter_idx]
            if prev_letter.text in self.LONG_VOWEL_LETTERS:
                return "ء"
            strength = self._find_neighbor_vowel_strength(segments, prev_letter_idx)
            if strength >= 3:
                return "ئ"
            if strength == 2:
                return "ؤ"
            if strength == 1:
                return "أ"
        return "ء"
