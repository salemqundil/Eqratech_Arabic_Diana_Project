"""
I3rab Parser - Extract structured syntax data from I3rab text.

Uses a hybrid rule-based approach with regex patterns covering the
Top 5 I3rab types (Phase 1, ~70% coverage).

Author: Hussein Hiyassat
Date: 2026-02-21
Sprint: 4 - Task 4.1
"""

import re
from typing import Optional, Dict, List

from .i3rab_components import I3rabComponents
from .mappings import (
    I3RAB_TYPE_MAPPING,
    CASE_MAPPING,
    CASE_MARKER_MAPPING,
    MAHALL_MAPPING,
)


class I3rabParser:
    """
    Parse I3rab text using regex patterns.

    Phase 1 covers the Top 5 I3rab types:
      مبتدأ، خبر، فاعل، مفعول به، حرف

    Examples:
        >>> parser = I3rabParser()
        >>> comp = parser.parse("مُبْتَدَأٌ مَرْفُوعٌ وَعَلَامَةُ رَفْعِهِ الضَّمَّةُ")
        >>> comp.i3rab_type
        'مبتدأ'
        >>> comp.case
        'nominative'
        >>> comp.confidence > 0.5
        True
    """

    # ------------------------------------------------------------------
    # Core regex patterns (diacritic-insensitive matching via strip)
    # ------------------------------------------------------------------

    # I3rab type patterns ordered by priority (more specific first)
    _I3RAB_TYPE_PATTERNS: List[tuple] = [
        # Two-word types first
        ("مفعول به", r"مَفْعُولٌ\s*بِهِ|مفعول\s*به"),
        ("مضاف إليه", r"مُضَافٌ\s*إِلَيْهِ|مضاف\s*إليه|مُضَافٌ\s*إِلَيْه"),
        ("نائب فاعل", r"نَائِبُ\s*الْفَاعِلِ|نائب\s*فاعل"),
        ("اسم كان", r"اسْمُ\s*كَانَ|اسم\s*كان"),
        ("خبر كان", r"خَبَرُ\s*كَانَ|خبر\s*كان"),
        ("اسم إن", r"اسْمُ\s*إِنَّ|اسم\s*إن"),
        ("خبر إن", r"خَبَرُ\s*إِنَّ|خبر\s*إن"),
        # Single-word types
        ("مبتدأ", r"مُبْتَدَأٌ|مُبْتَدَأ|مبتدأ"),
        ("خبر", r"(?<!\S)خَبَرٌ|(?<!\S)خَبَرُ|(?<!\S)خبر(?!\s*كان|\s*إن)"),
        ("فاعل", r"فَاعِلٌ|فَاعِلُ|(?<!\S)فاعل"),
        ("حرف", r"حَرْفٌ|حَرْفُ|(?<!\S)حرف"),
        ("نعت", r"نَعْتٌ|نَعْتُ|(?<!\S)نعت"),
        ("حال", r"حَالٌ|حَالُ|(?<!\S)حال"),
        ("تمييز", r"تَمْيِيزٌ|(?<!\S)تمييز"),
        ("بدل", r"بَدَلٌ|(?<!\S)بدل"),
        ("توكيد", r"تَوْكِيدٌ|(?<!\S)توكيد"),
        ("مجرور", r"(?<!\S)مَجْرُورٌ(?!\s*وَ)|(?<!\S)مجرور"),
    ]

    # Case patterns
    _CASE_PATTERNS: Dict[str, List[str]] = {
        "nominative": [
            r"مَرْفُوعٌ",
            r"مَرْفُوع",
            r"رَفْعِهِ",
            r"عَلَامَةُ رَفْع",
            r"مرفوع",
        ],
        "accusative": [
            r"مَنْصُوبٌ",
            r"مَنْصُوب",
            r"نَصْبِهِ",
            r"عَلَامَةُ نَصْب",
            r"منصوب",
        ],
        "genitive": [
            r"مَجْرُورٌ",
            r"مَجْرُور",
            r"جَرِّهِ",
            r"عَلَامَةُ جَرّ",
            r"مجرور",
        ],
    }

    # Case marker patterns
    _CASE_MARKER_PATTERNS: Dict[str, List[str]] = {
        "الضمة": [r"الضَّمَّةُ", r"الضمة", r"ضَمَّة"],
        "الفتحة": [r"الْفَتْحَةُ", r"الفتحة", r"فَتْحَة"],
        "الكسرة": [r"الْكَسْرَةُ", r"الكسرة", r"كَسْرَة"],
        "الواو": [r"الْوَاوُ", r"الواو(?!\s*و)"],
        "الياء": [r"الْيَاءُ", r"الياء"],
        "الألف": [r"الْأَلِفُ", r"الألف"],
        "النون": [r"حَذْفِ النُّونِ", r"حذف النون"],
    }

    # Mahall patterns
    _MAHALL_PATTERNS: Dict[str, List[str]] = {
        "لا محل له من الإعراب": [
            r"لَا مَحَلَّ لَهُ مِنَ الْإِعْرَابِ",
            r"لا محل له من الإعراب",
            r"لَا مَحَلَّ لَهَا",
            r"لا محل لها",
        ],
        "في محل رفع": [r"فِي مَحَلِّ رَفْعٍ", r"في محل رفع"],
        "في محل نصب": [r"فِي مَحَلِّ نَصْبٍ", r"في محل نصب"],
        "في محل جر": [r"فِي مَحَلِّ جَرٍّ", r"في محل جر"],
    }

    def parse(self, i3rab_text: str) -> I3rabComponents:
        """
        Extract I3rab components from Arabic I3rab text.

        Args:
            i3rab_text: Full I3rab description in Arabic.

        Returns:
            I3rabComponents with extracted fields and confidence score.

        Examples:
            >>> parser = I3rabParser()
            >>> comp = parser.parse("فَاعِلٌ مَرْفُوعٌ وَعَلَامَةُ رَفْعِهِ الضَّمَّةُ")
            >>> comp.i3rab_type
            'فاعل'
            >>> comp.case
            'nominative'
        """
        if not i3rab_text or not i3rab_text.strip():
            return I3rabComponents(raw_text=i3rab_text or "")

        i3rab_type = self._extract_i3rab_type(i3rab_text)
        i3rab_type_en = I3RAB_TYPE_MAPPING.get(i3rab_type) if i3rab_type else None
        case = self._extract_case(i3rab_text)
        case_marker = self._extract_case_marker(i3rab_text)
        mahall = self._extract_mahall(i3rab_text)
        confidence = self._compute_confidence(i3rab_type, case, case_marker)

        return I3rabComponents(
            i3rab_type=i3rab_type,
            i3rab_type_en=i3rab_type_en,
            case=case,
            case_marker=case_marker,
            mahall=mahall,
            confidence=confidence,
            raw_text=i3rab_text,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _extract_i3rab_type(self, text: str) -> Optional[str]:
        """Extract the primary I3rab type from text."""
        for ar_type, pattern in self._I3RAB_TYPE_PATTERNS:
            if re.search(pattern, text):
                return ar_type
        return None

    def _extract_case(self, text: str) -> Optional[str]:
        """Extract grammatical case from text."""
        for case_en, patterns in self._CASE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return case_en
        return None

    def _extract_case_marker(self, text: str) -> Optional[str]:
        """Extract case marker (e.g. الضمة) from text."""
        for marker_ar, patterns in self._CASE_MARKER_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return marker_ar
        return None

    def _extract_mahall(self, text: str) -> Optional[str]:
        """Extract mahall (grammatical position clause) from text."""
        for mahall_ar, patterns in self._MAHALL_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return mahall_ar
        return None

    def _compute_confidence(
        self,
        i3rab_type: Optional[str],
        case: Optional[str],
        case_marker: Optional[str],
    ) -> float:
        """
        Compute parsing confidence based on matched fields.

        Confidence increases with the number of successfully extracted
        fields.
        """
        score = 0.0
        if i3rab_type:
            score += 0.5
        if case:
            score += 0.3
        if case_marker:
            score += 0.2
        return min(1.0, score)
