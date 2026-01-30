from typing import List, Set, Tuple

from ..gate_framework import GateResult, GateStatus, PhonologicalGate
from ..syllable import Segment, SegmentKind, VowelKind


class GateAssimilation(PhonologicalGate):
    def __init__(self):
        super().__init__(gate_id="G_ASSIMILATION")
        self.SUN_LETTERS: Set[str] = {
            "ت", "ث", "د", "ذ", "ر", "ز",
            "س", "ش", "ص", "ض", "ط", "ظ",
            "ل", "ن",
        }
        self.BILABIALS: Set[str] = {"ب", "م", "و"}
        self.LAM_CID = 11
        self.NOON_CID = 12
        self.MEEM_CID = 13

    def apply(self, segments: List[Segment]) -> GateResult:
        working = list(segments)
        changes = []
        working, sun_changes = self._apply_sun_letters(working)
        working, nasal_changes = self._apply_nasal_assimilation(working)
        changes.extend(sun_changes)
        changes.extend(nasal_changes)
        status = GateStatus.ACCEPT if not changes else GateStatus.REPAIR
        reason = f"Assimilation changes: {len(changes)}"
        return GateResult(status=status, output=working, reason=reason, deltas=changes)

    def _apply_sun_letters(
        self, segments: List[Segment]
    ) -> Tuple[List[Segment], List[str]]:
        result: List[Segment] = []
        changes: List[str] = []
        i = 0
        while i < len(segments):
            if self._matches_al_sun(segments, i):
                result.append(segments[i])  # alif
                result.append(Segment(text="َ", kind=SegmentKind.VOWEL, vk=VowelKind.FATHA))
                sun_letter = segments[i + 3]
                result.append(sun_letter)
                result.append(Segment(text="ّ", kind=SegmentKind.VOWEL, vk=VowelKind.SHADDA))
                result.append(segments[i + 4])
                changes.append(f"sun_letter_{sun_letter.text}")
                i += 5
            else:
                result.append(segments[i])
                i += 1
        return result, changes

    def _matches_al_sun(self, segments: List[Segment], idx: int) -> bool:
        if idx + 4 >= len(segments):
            return False
        if segments[idx].text != "ا":
            return False
        lam = segments[idx + 1]
        if lam.cid != self.LAM_CID:
            return False
        if segments[idx + 2].vk != VowelKind.SUKUN:
            return False
        if segments[idx + 3].text not in self.SUN_LETTERS:
            return False
        return segments[idx + 4].kind == SegmentKind.VOWEL

    def _apply_nasal_assimilation(
        self, segments: List[Segment]
    ) -> Tuple[List[Segment], List[str]]:
        result: List[Segment] = []
        changes: List[str] = []
        i = 0
        while i < len(segments):
            if self._matches_nasal_pattern(segments, i):
                bilabial = segments[i + 2]
                replacement = "م" if bilabial.text == "ب" else bilabial.text
                result.append(Segment(text=replacement, kind=SegmentKind.CONSONANT, cid=self.MEEM_CID))
                result.append(segments[i + 1])  # sukun
                result.append(bilabial)
                changes.append(f"nasal_to_{replacement}")
                i += 3
            else:
                result.append(segments[i])
                i += 1
        return result, changes

    def _matches_nasal_pattern(self, segments: List[Segment], idx: int) -> bool:
        if idx + 2 >= len(segments):
            return False
        seg = segments[idx]
        if seg.cid != self.NOON_CID:
            return False
        if segments[idx + 1].vk != VowelKind.SUKUN:
            return False
        return segments[idx + 2].text in self.BILABIALS
