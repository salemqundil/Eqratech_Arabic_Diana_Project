"""
WordBoundaryDetector Plan B - Syllable-based word boundary detection.

This module provides sophisticated word boundary detection for Arabic text
using syllabification, morphological clues, and pattern matching.

Plan B (this implementation) uses:
- Syllable structure analysis
- Clitic detection (ال، و، ف، ب، ل، ك)
- Morpheme boundary markers
- Confidence scoring

Plan A (simple whitespace tokenization) is in word_boundary.py for comparison.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Set, Tuple
import re

from .syllabifier import syllabify, ArabicSyllabifier


@dataclass(frozen=True)
class WordBoundary:
    """
    Represents a detected word boundary with metadata.
    
    Attributes:
        text: The word text (including any attached clitics)
        start: Character offset start position in original text
        end: Character offset end position in original text
        confidence: Confidence score 0.0-1.0 for this boundary
        syllable_count: Number of syllables detected in this word
        has_prefix: Whether word has prefix clitic (e.g., ال، و، ف)
        has_suffix: Whether word has suffix clitic (e.g., ه، ها، هم)
    """
    text: str
    start: int
    end: int
    confidence: float
    syllable_count: int
    has_prefix: bool = False
    has_suffix: bool = False
    
    def __post_init__(self):
        assert 0.0 <= self.confidence <= 1.0, f"Confidence must be in [0,1], got {self.confidence}"
        assert self.start <= self.end, f"Invalid span: start={self.start}, end={self.end}"


class CliticDatabase:
    """Database of Arabic clitics (prefixes and suffixes)."""
    
    # Common prefixes (sorted by length, longest first for greedy matching)
    PREFIXES: List[str] = [
        'ال',      # definite article
        'و',       # conjunction 'and'
        'ف',       # conjunction 'then'
        'ب',       # preposition 'in/with'
        'ل',       # preposition 'to/for'
        'ك',       # preposition 'like'
    ]
    
    # Common suffixes (sorted by length, longest first)
    SUFFIXES: List[str] = [
        'كم',      # your (plural masculine)
        'كن',      # your (plural feminine)
        'هم',      # their/them (plural masculine)
        'هن',      # their/them (plural feminine)
        'نا',      # our/us
        'ه',       # his/him
        'ها',      # her
        'ك',       # your (singular)
        'ي',       # my
    ]
    
    # Compound prefixes (multiple clitics)
    COMPOUND_PREFIXES: List[str] = [
        'وال',     # و + ال
        'فال',     # ف + ال
        'بال',     # ب + ال
        'لل',      # ل + ال (with assimilation)
        'كال',     # ك + ال
    ]
    
    @classmethod
    def get_all_prefixes(cls) -> Set[str]:
        """Get all prefixes including compounds."""
        return set(cls.PREFIXES + cls.COMPOUND_PREFIXES)
    
    @classmethod
    def get_all_suffixes(cls) -> Set[str]:
        """Get all suffixes."""
        return set(cls.SUFFIXES)


class WordBoundaryDetectorPlanB:
    """Sophisticated word boundary detector using syllabification and morphological analysis.
    
    Algorithm:
    1. Split text on whitespace (initial boundaries)
    2. For each token:
       a. Use syllabifier to find syllable breaks
       b. Detect and separate clitics (prefixes/suffixes)
       c. Score boundary confidence based on features
    3. Return list of WordBoundary objects with metadata
    
    Examples:
        >>> detector = WordBoundaryDetectorPlanB()
        >>> boundaries = detector.detect_boundaries("الكتاب")
        >>> boundaries[0].text
        'الكتاب'
        >>> boundaries[0].has_prefix
        True
    """
    
    def __init__(self):
        """Initialize detector with clitic database."""
        self.clitics = CliticDatabase()
    
    def detect_boundaries(self, text: str) -> List[WordBoundary]:
        """Detect word boundaries in Arabic text.
        
        Args:
            text: Input Arabic text (may contain multiple words)
            
        Returns:
            List of WordBoundary objects with detected boundaries
            
        Examples:
            >>> detector = WordBoundaryDetectorPlanB()
            >>> boundaries = detector.detect_boundaries("الكتاب على الطاولة")
            >>> len(boundaries)
            3
            >>> boundaries[0].text
            'الكتاب'
        """
        if not text or not text.strip():
            return []
        
        # Initial tokenization on whitespace
        tokens = self._initial_tokenize(text)
        
        boundaries: List[WordBoundary] = []
        current_offset = 0
        
        for token_text, token_start, token_end in tokens:
            # Analyze this token
            boundary = self._analyze_token(token_text, token_start, token_end)
            boundaries.append(boundary)
            
            current_offset = token_end
        
        return boundaries
    
    def _initial_tokenize(self, text: str) -> List[Tuple[str, int, int]]:
        """Initial tokenization on whitespace.
        
        Returns:
            List of (token_text, start_offset, end_offset) tuples
        """
        tokens: List[Tuple[str, int, int]] = []
        
        # Split on whitespace but keep track of positions
        pattern = re.compile(r'\S+')
        for match in pattern.finditer(text):
            tokens.append((match.group(), match.start(), match.end()))
        
        return tokens
    
    def _analyze_token(self, text: str, start: int, end: int) -> WordBoundary:
        """Analyze a single token to create WordBoundary.
        
        Args:
            text: Token text
            start: Start offset in original text
            end: End offset in original text
            
        Returns:
            WordBoundary object with analysis results
        """
        # Remove diacritics for analysis (but keep original text)
        clean_text = self._remove_diacritics(text)
        
        # Detect prefixes and suffixes
        has_prefix, prefix_len = self._detect_prefix(clean_text)
        has_suffix, suffix_len = self._detect_suffix(clean_text)
        
        # Get syllable count (use clean text)
        try:
            result = syllabify(clean_text)
            syllable_count = len(result.syllables) if result and result.syllables else 0
        except Exception:
            syllable_count = 0
        
        # Always use estimate if syllabifier failed
        if syllable_count == 0:
            syllable_count = self._estimate_syllables(clean_text)
        
        # Compute confidence score
        confidence = self._compute_confidence(
            text=clean_text,
            has_prefix=has_prefix,
            has_suffix=has_suffix,
            syllable_count=syllable_count
        )
        
        return WordBoundary(
            text=text,
            start=start,
            end=end,
            confidence=confidence,
            syllable_count=syllable_count,
            has_prefix=has_prefix,
            has_suffix=has_suffix
        )
    
    def _detect_prefix(self, text: str) -> Tuple[bool, int]:
        """Detect if text starts with a clitic prefix.
        
        Returns:
            (has_prefix: bool, prefix_length: int)
        """
        # Try compound prefixes first (longest match)
        for prefix in sorted(self.clitics.COMPOUND_PREFIXES, key=len, reverse=True):
            if text.startswith(prefix) and len(text) - len(prefix) >= 3:
                return (True, len(prefix))
        
        # Try simple prefixes - be strict with single-letter prefixes
        for prefix in sorted(self.clitics.PREFIXES, key=len, reverse=True):
            remaining_length = len(text) - len(prefix)
            if text.startswith(prefix) and remaining_length >= 3:
                # Extra check: single-letter prefixes need longer stem
                if len(prefix) == 1 and remaining_length < 4:
                    continue
                return (True, len(prefix))
        
        return (False, 0)
    
    def _detect_suffix(self, text: str) -> Tuple[bool, int]:
        """Detect if text ends with a clitic suffix.
        
        Returns:
            (has_suffix: bool, suffix_length: int)
        """
        # Try suffixes (longest first)
        for suffix in sorted(self.clitics.SUFFIXES, key=len, reverse=True):
            if text.endswith(suffix) and len(text) - len(suffix) >= 3:
                return (True, len(suffix))
        
        return (False, 0)
    
    def _compute_confidence(
        self,
        text: str,
        has_prefix: bool,
        has_suffix: bool,
        syllable_count: int
    ) -> float:
        """Compute confidence score for this boundary.
        
        Higher confidence for:
        - Longer words (more information)
        - Words with recognized clitics
        - Words with 2-4 syllables (typical Arabic word length)
        
        Returns:
            Confidence score in [0.0, 1.0]
        """
        confidence = 0.5  # Base confidence
        
        # Length factor: longer words are more reliable
        if len(text) >= 5:
            confidence += 0.2
        elif len(text) >= 3:
            confidence += 0.1
        
        # Clitic factor: recognized clitics increase confidence
        if has_prefix:
            confidence += 0.1
        if has_suffix:
            confidence += 0.1
        
        # Syllable factor: typical words have 2-4 syllables
        if 2 <= syllable_count <= 4:
            confidence += 0.1
        
        # Clamp to [0, 1]
        return min(1.0, max(0.0, confidence))
    
    def _remove_diacritics(self, text: str) -> str:
        """Remove Arabic diacritics for analysis.
        
        Removes:
        - Short vowels (َ ُ ِ)
        - Tanwin (ً ٌ ٍ)
        - Sukun (ْ)
        - Shadda (ّ)
        """
        diacritics = [
            '\u064B',  # Fathatan
            '\u064C',  # Dammatan
            '\u064D',  # Kasratan
            '\u064E',  # Fatha
            '\u064F',  # Damma
            '\u0650',  # Kasra
            '\u0651',  # Shadda
            '\u0652',  # Sukun
        ]
        
        for diacritic in diacritics:
            text = text.replace(diacritic, '')
        
        return text
    
    def _estimate_syllables(self, text: str) -> int:
        """Estimate syllable count by counting vowels.
        
        Fallback method when syllabifier fails.
        """        
        vowels = {'ا', 'و', 'ي', 'ى'}  # Long vowels in Arabic
        count = sum(1 for c in text if c in vowels)
        
        # At least 1 syllable for any non-empty word
        return max(1, count)


# Convenience function for quick access
def detect_word_boundaries(text: str) -> List[WordBoundary]:
    """Convenience function to detect word boundaries.
    
    Args:
        text: Input Arabic text
        
    Returns:
        List of WordBoundary objects
        
    Examples:
        >>> boundaries = detect_word_boundaries("الكتاب على الطاولة")
        >>> [b.text for b in boundaries]
        ['الكتاب', 'على', 'الطاولة']
    """
    detector = WordBoundaryDetectorPlanB()
    return detector.detect_boundaries(text)