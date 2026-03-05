"""
GateEpenthesis: insert kasra to break clusters.
"""

from __future__ import annotations

from typing import List, Set

from ..gate_framework import GateResult, GateStatus, PhonologicalGate
from ..syllable import Segment, SegmentKind, VowelKind


class GateEpenthesis(PhonologicalGate):
    CONSONANTS: Set[str] = {
        "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز",
        "س", "ش", "ص", "ض", "ط", "ظ", "ع", "غ", "ف", "ق",
        "ك", "ل", "م", "ن", "ه", "و", "ي",
    }

    SUKUN = VowelKind.SUKUN

    def __init__(self) -> None:
        super().__init__(gate_id="G_EPENTHESIS")

    def precondition(self, segments: List[Segment]) -> bool:
        count = 0
        for idx, seg in enumerate(segments):
            if seg.kind == SegmentKind.CONSONANT and seg.text in self.CONSONANTS:
                count += 1
                if idx + 1 < len(segments):
                    next_seg = segments[idx + 1]
                    if next_seg.kind == SegmentKind.VOWEL and next_seg.vk == self.SUKUN:
                        if count >= 2:
                            return True
            elif seg.kind == SegmentKind.VOWEL:
                count = 0
        return False

    def apply(self, segments: List[Segment]) -> GateResult:
        output = list(segments)
        deltas: List[str] = []

        # Repair illegal initial consonant clusters (CC/CCC/CCCC...) by inserting kasra
        # between the first two consonants. Apply at most twice to avoid runaway inserts.
        inserted = 0
        while (
            len(output) >= 2
            and output[0].kind == SegmentKind.CONSONANT
            and output[1].kind == SegmentKind.CONSONANT
            and inserted < 2
        ):
            output.insert(1, Segment(text="ِ", kind=SegmentKind.VOWEL, vk=VowelKind.KASRA))
            deltas.append("initial_cluster_insert_kasra:1")
            inserted += 1

        idx = 0
        while idx < len(output) - 3:
            c1, v1, c2, v2 = output[idx], output[idx + 1], output[idx + 2], output[idx + 3]
            if (
                c1.kind == SegmentKind.CONSONANT
                and v1.kind == SegmentKind.VOWEL
                and v1.vk == self.SUKUN
                and c2.kind == SegmentKind.CONSONANT
                and v2.kind == SegmentKind.VOWEL
                and v2.vk == self.SUKUN
            ):
                kasra = Segment(text="ِ", kind=SegmentKind.VOWEL, vk=VowelKind.KASRA)
                output.insert(idx + 3, kasra)
                deltas.append(f"insert_kasra:{idx+3}")
                idx += 4
            else:
                idx += 1

        # Repair any triple-consonant clusters (CCC) by inserting kasra between 2nd and 3rd.
        # This targets sequences that still survive after other gates and commonly produce
        # CV patterns like CVCCC... which are not allowed in Arabic syllabification.
        idx = 0
        repairs = 0
        while idx < len(output) - 2 and repairs < 20:
            a, b, c = output[idx], output[idx + 1], output[idx + 2]
            if (
                a.kind == SegmentKind.CONSONANT
                and b.kind == SegmentKind.CONSONANT
                and c.kind == SegmentKind.CONSONANT
            ):
                output.insert(idx + 2, Segment(text="ِ", kind=SegmentKind.VOWEL, vk=VowelKind.KASRA))
                deltas.append(f"ccc_break_kasra:{idx+2}")
                repairs += 1
                idx += 3
                continue
            idx += 1

        # Break "CV-sense" CCC clusters where consonants are separated only by sukun/shadda.
        # These clusters still surface in CV output because sukun is ignored as a nucleus.
        repairs = 0
        idx = 0
        run_len = 0
        while idx < len(output) and repairs < 30:
            seg = output[idx]
            if seg.kind == SegmentKind.VOWEL:
                # Short/long vowels break consonant runs; sukun does not.
                if seg.vk not in {VowelKind.SUKUN, VowelKind.SHADDA, VowelKind.NONE, None}:
                    run_len = 0
                idx += 1
                continue
            if seg.kind == SegmentKind.CONSONANT:
                run_len += 1
                if run_len >= 3:
                    output.insert(idx, Segment(text="ِ", kind=SegmentKind.VOWEL, vk=VowelKind.KASRA))
                    deltas.append(f"cv_cluster_break_kasra:{idx}")
                    repairs += 1
                    # Keep current consonant as start of a new run after insertion.
                    run_len = 1
                    idx += 2
                    continue
            idx += 1

        status = GateStatus.REPAIR if deltas else GateStatus.ACCEPT

        return GateResult(
            status=status,
            output=output,
            reason=f"epenthesis inserts: {len(deltas)}",
            deltas=deltas,
        )
