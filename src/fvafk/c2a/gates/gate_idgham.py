"""
GateIdgham: Tajwid idgham rules

Implements the six core idgham targets (ي، ن، م، و، ل، ر)
by collapsing a noon-sakin / tanwin + target letter into a geminated consonant.
"""

from typing import List, Set, Tuple

from ..gate_framework import GateResult, GateStatus, PhonologicalGate
from ..syllable import Segment, SegmentKind, VowelKind


class GateIdgham(PhonologicalGate):
    def __init__(self) -> None:
        super().__init__(gate_id="G_IDGHAM")
        self.NOON_CHAR = "ن"
        self.IDGHAM_GHUNNAH_LETTERS: Set[str] = {"ي", "ن", "م", "و"}
        self.IDGHAM_NO_GHUNNAH_LETTERS: Set[str] = {"ل", "ر"}
        self.ALL_IDGHAM_LETTERS: Set[str] = (
            self.IDGHAM_GHUNNAH_LETTERS | self.IDGHAM_NO_GHUNNAH_LETTERS
        )

    def apply(self, segments: List[Segment]) -> GateResult:
        result, changes = self._apply_noon_idgham(segments)
        status = GateStatus.ACCEPT
        reason = f"idgham applied ({len(changes)} changes)"
        return GateResult(
            status=status,
            output=result,
            reason=reason,
            deltas=changes,
        )

    def _apply_noon_idgham(
        self, segments: List[Segment]
    ) -> Tuple[List[Segment], List[str]]:
        result: List[Segment] = []
        changes: List[str] = []
        i = 0

        while i < len(segments):
            # ------------------------------------------------------------------
            # Boundary-idgham fix (Plan-aligned):
            # If a shadda appears on a word-initial consonant due to idgham across
            # word boundary (e.g., after tanwin / nun-sakin / identical consonant),
            # do NOT expand shadda inside the word. Instead, drop the shadda mark
            # and keep the written haraka.
            #
            # We approximate "word boundary" by patterns that commonly appear in
            # the continuous segment stream when spaces are removed by C1Encoder.
            # ------------------------------------------------------------------
            if self._is_boundary_tanwin_shadda(segments, i):
                # pattern: TANWIN + C(idgham_letter) + SHADDA
                result.append(segments[i])       # keep tanwin on previous word
                result.append(segments[i + 1])   # keep the consonant itself
                changes.append(f"idgham_boundary_drop_shadda_after_tanwin:{segments[i + 1].text}")
                i += 3
                continue

            if self._is_boundary_mutamathilayn_shadda(segments, i):
                # pattern: C(x) + SUKUN + C(x) + SHADDA  (e.g., ...مْ مُّ...)
                result.append(segments[i])
                result.append(segments[i + 1])
                result.append(segments[i + 2])
                changes.append(f"idgham_boundary_drop_shadda_mutamathilayn:{segments[i].text}")
                i += 4
                continue

            if self._is_boundary_double_consonant_shadda(segments, i):
                # pattern: C(x) + C(x) + SHADDA (e.g., ...م مُّ... when final sukun is not written)
                result.append(segments[i])
                result.append(segments[i + 1])
                changes.append(f"idgham_boundary_drop_shadda_double:{segments[i].text}")
                i += 3
                continue

            if self._is_noon_idgham_pattern(segments, i):
                idgham_letter = segments[i + 2]
                result.append(Segment(text=idgham_letter.text, kind=SegmentKind.CONSONANT))
                result.append(
                    Segment(
                        text="ّ",
                        kind=SegmentKind.VOWEL,
                        vk=VowelKind.SHADDA,
                    )
                )
                if idgham_letter.text in self.IDGHAM_GHUNNAH_LETTERS:
                    changes.append(f"idgham_ghunnah_{idgham_letter.text}")
                else:
                    changes.append(f"idgham_no_ghunnah_{idgham_letter.text}")
                i += 3
                continue
            result.append(segments[i])
            i += 1

        return result, changes

    def _is_boundary_tanwin_shadda(self, segments: List[Segment], offset: int) -> bool:
        """
        Detect: [TANWIN_*] [CONSONANT in idgham letters] [SHADDA]
        Example across boundary when tanwin remains written on previous word, and
        next word begins with a shadda-marked consonant.
        """
        if offset + 2 >= len(segments):
            return False
        t = segments[offset]
        c = segments[offset + 1]
        sh = segments[offset + 2]
        if t.kind != SegmentKind.VOWEL or t.vk not in {
            VowelKind.TANWIN_FATH,
            VowelKind.TANWIN_DAMM,
            VowelKind.TANWIN_KASR,
        }:
            return False
        if c.kind != SegmentKind.CONSONANT or c.text not in self.ALL_IDGHAM_LETTERS:
            return False
        if sh.kind != SegmentKind.VOWEL or sh.vk != VowelKind.SHADDA:
            return False
        return True

    def _is_boundary_mutamathilayn_shadda(self, segments: List[Segment], offset: int) -> bool:
        """
        Detect: [CONSONANT x] [SUKUN] [CONSONANT x] [SHADDA]
        Example: "...مْ مُّ..." where shadda represents boundary idgham.
        """
        if offset + 3 >= len(segments):
            return False
        c1 = segments[offset]
        s = segments[offset + 1]
        c2 = segments[offset + 2]
        sh = segments[offset + 3]
        if c1.kind != SegmentKind.CONSONANT or c2.kind != SegmentKind.CONSONANT:
            return False
        if c1.text != c2.text:
            return False
        if s.kind != SegmentKind.VOWEL or s.vk != VowelKind.SUKUN:
            return False
        if sh.kind != SegmentKind.VOWEL or sh.vk != VowelKind.SHADDA:
            return False
        return True

    def _is_boundary_double_consonant_shadda(self, segments: List[Segment], offset: int) -> bool:
        """
        Detect: [CONSONANT x] [CONSONANT x] [SHADDA]
        Covers boundary-idgham cases where the final sukun of the previous word is
        not explicitly written (common in non-fully-vocalized inputs).
        """
        if offset + 2 >= len(segments):
            return False
        c1 = segments[offset]
        c2 = segments[offset + 1]
        sh = segments[offset + 2]
        if c1.kind != SegmentKind.CONSONANT or c2.kind != SegmentKind.CONSONANT:
            return False
        if c1.text != c2.text:
            return False
        if sh.kind != SegmentKind.VOWEL or sh.vk != VowelKind.SHADDA:
            return False
        return True

    def _is_noon_idgham_pattern(self, segments: List[Segment], offset: int) -> bool:
        if offset + 2 >= len(segments):
            return False

        noon = segments[offset]
        sukun = segments[offset + 1]
        letter = segments[offset + 2]

        if noon.kind != SegmentKind.CONSONANT:
            return False
        if noon.text != self.NOON_CHAR:
            return False
        if sukun.kind != SegmentKind.VOWEL or sukun.vk != VowelKind.SUKUN:
            return False
        if letter.kind != SegmentKind.CONSONANT:
            return False
        if letter.text not in self.ALL_IDGHAM_LETTERS:
            return False

        return True
