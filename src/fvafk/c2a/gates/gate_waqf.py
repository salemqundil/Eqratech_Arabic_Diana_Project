"""
GateWaqf: Pause (وقف) rules for Arabic phonology.

Enforces tanwin → sukun and ة → ه at pauses.
"""

from __future__ import annotations

from typing import List, Set

from ..gate_framework import GateResult, GateStatus, PhonologicalGate
from ..syllable import Segment, SegmentKind, VowelKind


class GateWaqf(PhonologicalGate):
    TANWIN_FATH = "\u064b"
    TANWIN_DAMM = "\u064c"
    TANWIN_KASR = "\u064d"
    ALL_TANWIN: Set[str] = {TANWIN_FATH, TANWIN_DAMM, TANWIN_KASR}
    TA_MARBUTA = "\u0629"
    HA = "\u0647"
    SUKUN = "\u0652"
    SPACE = " "

    def __init__(self) -> None:
        super().__init__(gate_id="G_WAQF")

    def precondition(self, segments: List[Segment]) -> bool:
        return any(
            (seg.kind == SegmentKind.VOWEL and seg.text in self.ALL_TANWIN)
            or (seg.kind == SegmentKind.CONSONANT and seg.text == self.TA_MARBUTA)
            for seg in segments
        )

    def apply(self, segments: List[Segment]) -> GateResult:
        output: List[Segment] = list(segments)
        deltas: List[str] = []

        pause_positions = self._find_pause_boundaries(output)
        for pause_pos in pause_positions:
            deltas.extend(self._apply_tanwin_rule(output, pause_pos))
            deltas.extend(self._apply_ta_marbuta_rule(output, pause_pos))

        status = GateStatus.REPAIR if deltas else GateStatus.ACCEPT
        reason = f"waqf adjustments: {len(deltas)}"

        return GateResult(
            status=status,
            output=output,
            reason=reason,
            deltas=deltas,
        )

    def _find_pause_boundaries(self, segments: List[Segment]) -> List[int]:
        boundaries: List[int] = []
        for idx, seg in enumerate(segments):
            is_space = seg.kind == SegmentKind.CONSONANT and seg.text == self.SPACE
            is_end = idx == len(segments) - 1
            if is_space:
                if idx - 1 >= 0:
                    boundaries.append(idx - 1)
            elif is_end:
                boundaries.append(idx)
        # Remove duplicates
        return sorted(set(boundaries))

    def _apply_tanwin_rule(self, segments: List[Segment], pause_pos: int) -> List[str]:
        changes: List[str] = []
        if 0 <= pause_pos < len(segments):
            seg = segments[pause_pos]
            if seg.kind == SegmentKind.VOWEL and seg.text in self.ALL_TANWIN:
                segments[pause_pos] = Segment(
                    text=self.SUKUN,
                    kind=SegmentKind.VOWEL,
                    vk=VowelKind.SUKUN,
                )
                changes.append(f"tanwin_to_sukun:{pause_pos}")

        if pause_pos - 1 >= 0:
            prev = segments[pause_pos - 1]
            if prev.kind == SegmentKind.VOWEL and prev.text in self.ALL_TANWIN:
                segments[pause_pos - 1] = Segment(
                    text=self.SUKUN,
                    kind=SegmentKind.VOWEL,
                    vk=VowelKind.SUKUN,
                )
                changes.append(f"tanwin_to_sukun:{pause_pos - 1}")

        return changes

    def _apply_ta_marbuta_rule(self, segments: List[Segment], pause_pos: int) -> List[str]:
        changes: List[str] = []
        search_range = min(3, pause_pos + 1)
        for idx in range(pause_pos, max(pause_pos - search_range, -1), -1):
            seg = segments[idx]
            if seg.kind == SegmentKind.CONSONANT and seg.text == self.TA_MARBUTA:
                segments[idx] = Segment(
                    text=self.HA,
                    kind=SegmentKind.CONSONANT,
                    vk=seg.vk,
                )
                changes.append(f"ta_marbuta_to_ha:{idx}")
                break
        return changes
