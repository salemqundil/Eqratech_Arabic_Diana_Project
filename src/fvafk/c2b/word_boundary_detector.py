"""
Word Boundary Detector - Plan B (Syllable-Based)

This module provides syllable-based word boundary detection for Arabic text.
Plan B uses syllable structure analysis combined with clitic detection to
identify word boundaries more accurately than character-pattern-based approaches.

Classes:
    WordBoundary: Represents a detected word boundary with metadata
    CliticDatabase: Database of Arabic clitics (prefixes and suffixes)
    WordBoundaryDetectorPlanB: Main detector class using syllable analysis
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple
import re


@dataclass
class WordBoundary:
    """
    Represents a detected word boundary.

    Attributes:
        text: The word text
        start: Start position in original text
        end: End position in original text
        confidence: Confidence score [0.0, 1.0]
        syllable_count: Number of syllables in the word
        has_prefix: Whether word has clitic prefix
        has_suffix: Whether word has clitic suffix
        prefix: Detected prefix clitic (if any)
        suffix: Detected suffix clitic (if any)
    """
    text: str
    start: int
    end: int
    confidence: float
    syllable_count: int
    has_prefix: bool = False
    has_suffix: bool = False
    prefix: Optional[str] = None
    suffix: Optional[str] = None

    def __post_init__(self):
        """Validate boundary constraints."""
        assert 0.0 <= self.confidence <= 1.0, "Confidence must be in [0, 1]"
        assert self.start <= self.end, "Start must be <= end"


class CliticDatabase:
    """
    Database of Arabic clitic morphemes (prefixes and suffixes).

    Clitics are function words that attach to content words.
    Examples: ال (the), و (and), ب (with), ه (his)
    """

    # Simple prefixes
    SIMPLE_PREFIXES = [
        'ال',  # definite article (al-)
        'و',   # conjunction (and)
        'ف',   # conjunction (then)
        'ب',   # preposition (with/in)
        'ل',   # preposition (to/for)
        'ك',   # preposition (like)
        'س',   # future marker
    ]

    # Compound prefixes (combinations)
    COMPOUND_PREFIXES = [
        'وال',  # و + ال
        'فال',  # ف + ال
        'بال',  # ب + ال
        'لل',   # ل + ال
        'كال',  # ك + ال
        'ولل',  # و + لل
        'فلل',  # ف + لل
    ]

    # Attached pronoun suffixes
    PRONOUN_SUFFIXES = [
        'ه',    # he/his/him
        'ها',   # she/her
        'هم',   # they/their/them (masc)
        'هن',   # they/their/them (fem)
        'ك',    # you/your (masc sing)
        'كم',   # you/your (masc plural)
        'كن',   # you/your (fem plural)
        'ي',    # me/my
        'نا',   # we/our/us
    ]

    @classmethod
    def get_all_prefixes(cls) -> List[str]:
        """Get all prefix clitics (simple + compound)."""
        return cls.SIMPLE_PREFIXES + cls.COMPOUND_PREFIXES

    @classmethod
    def get_all_suffixes(cls) -> List[str]:
        """Get all suffix clitics."""
        return cls.PRONOUN_SUFFIXES


class WordBoundaryDetectorPlanB:
    """
    Syllable-based word boundary detector for Arabic text.

    Plan B uses syllable structure analysis to detect word boundaries,
    combined with clitic detection for improved accuracy.

    Algorithm:
        1. Split text on whitespace to get candidate words
        2. Analyze syllable structure of each candidate
        3. Detect and strip clitic prefixes/suffixes
        4. Compute confidence based on syllable count and clitic presence
        5. Return word boundaries with metadata

    Attributes:
        syllabifier: Reference to syllabification engine (optional)
        clitics: Clitic database instance
    """

    def __init__(self, syllabifier=None):
        """Initialize detector.

        Args:
            syllabifier: Optional syllabifier instance for advanced analysis
        """
        self.syllabifier = syllabifier
        self.clitics = CliticDatabase()

    def detect_boundaries(self, text: str) -> List[WordBoundary]:
        """Detect word boundaries in Arabic text.

        Args:
            text: Arabic text to analyze

        Returns:
            List of WordBoundary objects with metadata
        """
        if not text or not text.strip():
            return []

        boundaries = []

        # Split on whitespace to get candidate words
        words = text.split()
        current_pos = 0

        for word in words:
            # Find actual position in original text
            start = text.find(word, current_pos)
            end = start + len(word)
            current_pos = end

            # Analyze word
            boundary = self._analyze_word(word, start, end)
            boundaries.append(boundary)

        return boundaries

    def _analyze_word(self, word: str, start: int, end: int) -> WordBoundary:
        """Analyze a single word to detect boundaries and clitics.

        Args:
            word: Word text
            start: Start position in original text
            end: End position in original text

        Returns:
            WordBoundary object with analysis results
        """
        # Detect prefixes
        prefix, has_prefix = self._detect_prefix(word)

        # Detect suffixes
        suffix, has_suffix = self._detect_suffix(word)

        # Count syllables (approximate)
        syllable_count = self._count_syllables(word)

        # Compute confidence
        confidence = self._compute_confidence(
            word, has_prefix, has_suffix, syllable_count
        )

        return WordBoundary(
            text=word,
            start=start,
            end=end,
            confidence=confidence,
            syllable_count=syllable_count,
            has_prefix=has_prefix,
            has_suffix=has_suffix,
            prefix=prefix,
            suffix=suffix,
        )

    def _detect_prefix(self, word: str) -> Tuple[Optional[str], bool]:
        """Detect clitic prefix in word.

        Args:
            word: Word text

        Returns:
            Tuple of (prefix_text, has_prefix)
        """
        word_bare = self._remove_diacritics(word)

        # Check compound prefixes first (longer matches)
        for prefix in sorted(self.clitics.COMPOUND_PREFIXES, key=len, reverse=True):
            if word_bare.startswith(prefix) and len(word_bare) - len(prefix) >= 3:
                return prefix, True

        # Check simple prefixes; require minimum stem length to avoid false positives
        # (e.g. "كتاب" should not be split as ك + تاب; ك is root letter)
        for prefix in sorted(self.clitics.SIMPLE_PREFIXES, key=len, reverse=True):
            remaining = len(word_bare) - len(prefix)
            if word_bare.startswith(prefix) and remaining >= 3:
                if len(prefix) == 1 and remaining < 4:
                    continue  # single-char prefix needs longer stem
                return prefix, True

        return None, False

    def _detect_suffix(self, word: str) -> Tuple[Optional[str], bool]:
        """Detect clitic suffix in word.

        Args:
            word: Word text

        Returns:
            Tuple of (suffix_text, has_suffix)
        """
        # Remove diacritics for suffix detection
        word_bare = self._remove_diacritics(word)

        # Check suffixes (longest first for better matching)
        for suffix in sorted(self.clitics.PRONOUN_SUFFIXES, key=len, reverse=True):
            if word_bare.endswith(suffix) and len(word_bare) > len(suffix):
                return suffix, True

        return None, False

    def _count_syllables(self, word: str) -> int:
        """Approximate syllable count for Arabic word.

        Uses syllabifier when available; otherwise a simplified heuristic
        based on vowel counting.

        Args:
            word: Word text

        Returns:
            Estimated syllable count
        """
        if self.syllabifier:
            try:
                result = self.syllabifier.syllabify(word)
                n = len(result.syllables) if result.syllables else 0
                return max(1, n)
            except Exception:
                pass

        try:
            from .syllabifier import syllabify
            result = syllabify(word)
            n = len(result.syllables) if result.syllables else 0
            return max(1, n)
        except Exception:
            pass

        # Fallback: count short vowels as syllable markers
        vowel_marks = ['َ', 'ِ', 'ُ']  # fatha, kasra, damma
        count = sum(1 for char in word if char in vowel_marks)

        # Minimum 1 syllable per word
        return max(1, count)

    def _compute_confidence(
        self,
        word: str,
        has_prefix: bool,
        has_suffix: bool,
        syllable_count: int,
    ) -> float:
        """Compute confidence score for word boundary detection.

        Confidence is higher when:
        - Word has clear clitics
        - Word has reasonable syllable count
        - Word length is reasonable

        Args:
            word: Word text
            has_prefix: Whether prefix detected
            has_suffix: Whether suffix detected
            syllable_count: Number of syllables

        Returns:
            Confidence score [0.0, 1.0]
        """
        confidence = 0.5  # Base confidence

        # Boost for clitic presence
        if has_prefix:
            confidence += 0.2
        if has_suffix:
            confidence += 0.1

        # Boost for reasonable syllable count (1-4 syllables)
        if 1 <= syllable_count <= 4:
            confidence += 0.1

        # Slight boost for reasonable word length
        word_length = len(self._remove_diacritics(word))
        if 3 <= word_length <= 12:
            confidence += 0.1

        # Cap at 1.0
        return min(1.0, confidence)

    def _remove_diacritics(self, text: str) -> str:
        """Remove Arabic diacritics from text.

        Args:
            text: Text with diacritics

        Returns:
            Text without diacritics
        """
        # Arabic diacritics Unicode range
        diacritics = re.compile(r'[\u064B-\u065F\u0670]')
        return diacritics.sub('', text)


def detect_word_boundaries(text: str) -> List[WordBoundary]:
    """Convenience function to detect word boundaries using Plan B.

    Args:
        text: Arabic text to analyze

    Returns:
        List of WordBoundary objects
    """
    detector = WordBoundaryDetectorPlanB()
    return detector.detect_boundaries(text)
