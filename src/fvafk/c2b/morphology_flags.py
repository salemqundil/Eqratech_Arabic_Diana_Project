"""
Morphology Flags Extractor - Extract grammatical features from Arabic words.

This module provides extractors for:
- Case (nominative, accusative, genitive)
- Number (singular, dual, plural)
- Gender (masculine, feminine)
- Definiteness (definite/indefinite)

The extractors analyze diacritics, suffixes, prefixes, and patterns.

Author: Hussein Hiyassat
Date: 2026-02-19
Sprint: 3 - Task 3.3
"""

from dataclasses import dataclass
from typing import Optional, Tuple
import re


@dataclass
class MorphologyFlags:
    """
    Container for morphological features.
    
    Attributes:
        case: Grammatical case (nominative, accusative, genitive)
        number: Grammatical number (singular, dual, plural)
        gender: Grammatical gender (masculine, feminine)
        definiteness: Whether word is definite (has ال)
        confidence: Confidence score for the extraction [0.0, 1.0]
    """
    case: Optional[str] = None
    number: Optional[str] = None
    gender: Optional[str] = None
    definiteness: bool = False
    confidence: float = 0.0


class MorphologyFlagsExtractor:
    """
    Extract morphological flags from Arabic words.
    
    The extractor analyzes:
    1. Diacritics (especially tanwin) for case
    2. Suffixes for number and gender
    3. Prefixes for definiteness
    4. Word endings for gender (ta marbuta)
    
    Examples:
        >>> extractor = MorphologyFlagsExtractor()
        >>> flags = extractor.extract("الْكِتَابُ")
        >>> flags.case
        'nominative'
        >>> flags.definiteness
        True
    """
    
    # Diacritics
    FATHATAN = '\u064B'  # ً (accusative tanwin)
    DAMMATAN = '\u064C'  # ٌ (nominative tanwin)
    KASRATAN = '\u064D'  # ٍ (genitive tanwin)
    FATHA = '\u064E'     # َ (fatha)
    DAMMA = '\u064F'     # ُ (damma)
    KASRA = '\u0650'     # ِ (kasra)
    SUKUN = '\u0652'     # ْ (sukun)
    
    # Special characters
    TA_MARBUTA = 'ة'      # Feminine marker
    ALIF = 'ا'
    WAW = 'و'
    YA = 'ي'
    NOON = 'ن'
    
    # Sound masculine plural suffixes
    MASCULINE_PLURAL_NOMINATIVE = ['ون', 'ُونَ', 'ُون']
    MASCULINE_PLURAL_ACCUSATIVE_GENITIVE = ['ين', 'ِينَ', 'ِين']
    
    # Dual suffixes
    DUAL_NOMINATIVE = ['ان', 'َانِ', 'َان']
    DUAL_ACCUSATIVE_GENITIVE = ['ين', 'َيْنِ', 'َيْن']
    
    # Sound feminine plural suffix
    FEMININE_PLURAL = ['ات', 'َاتٌ', 'َاتُ', 'َاتِ']
    
    def __init__(self):
        """Initialize the extractor."""
        pass
    
    def extract(self, word: str) -> MorphologyFlags:
        """
        Extract all morphological flags from a word.
        
        Args:
            word: Arabic word (with diacritics if available)
            
        Returns:
            MorphologyFlags object with extracted features
            
        Examples:
            >>> extractor = MorphologyFlagsExtractor()
            >>> flags = extractor.extract("كِتَابٌ")
            >>> flags.case
            'nominative'
            >>> flags.number
            'singular'
        """
        if not word or not word.strip():
            return MorphologyFlags()
        
        flags = MorphologyFlags()
        
        # Extract definiteness (must come first to strip ال)
        flags.definiteness = self._extract_definiteness(word)
        
        # Strip ال for further analysis
        word_without_al = self._strip_definite_article(word)
        
        # Extract case from diacritics
        flags.case = self._extract_case(word_without_al)
        
        # Extract number from suffixes and patterns
        flags.number = self._extract_number(word_without_al)
        
        # Extract gender from endings and patterns
        flags.gender = self._extract_gender(word_without_al)
        
        # Compute overall confidence
        flags.confidence = self._compute_confidence(flags, word_without_al)
        
        return flags
    
    def _extract_definiteness(self, word: str) -> bool:
        """
        Check if word has definite article ال.
        
        Args:
            word: Arabic word
            
        Returns:
            True if word starts with ال
            
        Examples:
            >>> extractor = MorphologyFlagsExtractor()
            >>> extractor._extract_definiteness("الكتاب")
            True
            >>> extractor._extract_definiteness("كتاب")
            False
        """
        # Remove diacritics for checking
        word_bare = self._remove_diacritics(word)
        
        # Check for ال at the beginning
        return word_bare.startswith('ال')
    
    def _extract_case(self, word: str) -> Optional[str]:
        """
        Extract grammatical case from word ending.
        
        Case is marked by:
        - Tanwin: ً (accusative), ٌ (nominative), ٍ (genitive)
        - Short vowels: َ (accusative), ُ (nominative), ِ (genitive)
        
        Args:
            word: Arabic word
            
        Returns:
            'nominative', 'accusative', 'genitive', or None
            
        Examples:
            >>> extractor = MorphologyFlagsExtractor()
            >>> extractor._extract_case("كِتَابٌ")
            'nominative'
            >>> extractor._extract_case("كِتَابًا")
            'accusative'
        """
        if not word:
            return None
        
        # Check last few characters for case markers
        last_chars = word[-3:] if len(word) >= 3 else word
        
        # Check for tanwin (strongest indicator)
        if self.DAMMATAN in last_chars:
            return 'nominative'
        elif self.FATHATAN in last_chars:
            return 'accusative'
        elif self.KASRATAN in last_chars:
            return 'genitive'
        
        # Check for short vowels (weaker indicator)
        if word.endswith(self.DAMMA):
            return 'nominative'
        elif word.endswith(self.FATHA):
            return 'accusative'
        elif word.endswith(self.KASRA):
            return 'genitive'
        
        return None
    
    def _extract_number(self, word: str) -> Optional[str]:
        """
        Extract grammatical number from word.
        
        Number is indicated by:
        - Dual suffixes: ان/ين
        - Masculine plural: ون/ين
        - Feminine plural: ات
        - Default: singular
        
        Args:
            word: Arabic word
            
        Returns:
            'singular', 'dual', or 'plural'
            
        Examples:
            >>> extractor = MorphologyFlagsExtractor()
            >>> extractor._extract_number("كِتَابَانِ")
            'dual'
            >>> extractor._extract_number("مُعَلِّمُونَ")
            'plural'
        """
        if not word:
            return 'singular'
        
        word_bare = self._remove_diacritics(word)
        
        # Check for dual suffixes (most specific)
        for suffix in self.DUAL_NOMINATIVE + self.DUAL_ACCUSATIVE_GENITIVE:
            suffix_bare = self._remove_diacritics(suffix)
            if word_bare.endswith(suffix_bare) and len(word_bare) > len(suffix_bare):
                # Make sure it's not just part of the root
                if suffix_bare == 'ان' or suffix_bare == 'ين':
                    return 'dual'
        
        # Check for sound masculine plural
        for suffix in self.MASCULINE_PLURAL_NOMINATIVE + self.MASCULINE_PLURAL_ACCUSATIVE_GENITIVE:
            suffix_bare = self._remove_diacritics(suffix)
            if word_bare.endswith(suffix_bare) and len(word_bare) > len(suffix_bare) + 1:
                return 'plural'
        
        # Check for sound feminine plural
        for suffix in self.FEMININE_PLURAL:
            suffix_bare = self._remove_diacritics(suffix)
            if word_bare.endswith(suffix_bare) and len(word_bare) > len(suffix_bare) + 1:
                return 'plural'
        
        # Default to singular
        return 'singular'
    
    def _extract_gender(self, word: str) -> Optional[str]:
        """
        Extract grammatical gender from word.
        
        Gender is indicated by:
        - Ta marbuta (ة): feminine
        - Feminine plural suffix (ات): feminine
        - Default: masculine
        
        Args:
            word: Arabic word
            
        Returns:
            'masculine' or 'feminine'
            
        Examples:
            >>> extractor = MorphologyFlagsExtractor()
            >>> extractor._extract_gender("مَدْرَسَةٌ")
            'feminine'
            >>> extractor._extract_gender("كِتَابٌ")
            'masculine'
        """
        if not word:
            return 'masculine'
        
        word_bare = self._remove_diacritics(word)
        
        # Check for ta marbuta (strongest feminine marker)
        if self.TA_MARBUTA in word_bare:
            return 'feminine'
        
        # Check for feminine plural suffix
        for suffix in self.FEMININE_PLURAL:
            suffix_bare = self._remove_diacritics(suffix)
            if word_bare.endswith(suffix_bare):
                return 'feminine'
        
        # Check for some known feminine patterns
        # Words ending in اء are often feminine
        if word_bare.endswith('اء'):
            return 'feminine'
        
        # Default to masculine
        return 'masculine'
    
    def _strip_definite_article(self, word: str) -> str:
        """
        Remove definite article ال from word.
        
        Args:
            word: Arabic word
            
        Returns:
            Word without ال prefix
        """
        word_bare = self._remove_diacritics(word)
        
        if word_bare.startswith('ال'):
            # Find where ال ends in the original word
            # Account for diacritics between ا and ل
            idx = 0
            if word[idx] in 'اأإآ':
                idx += 1
            # Skip diacritics
            while idx < len(word) and self._is_diacritic(word[idx]):
                idx += 1
            # Should be ل now
            if idx < len(word) and word[idx] == 'ل':
                idx += 1
            # Skip diacritics after ل
            while idx < len(word) and self._is_diacritic(word[idx]):
                idx += 1
            return word[idx:]
        
        return word
    
    def _compute_confidence(self, flags: MorphologyFlags, word: str) -> float:
        """
        Compute confidence score for the extraction.
        
        Higher confidence when:
        - Word has clear diacritics
        - Multiple features detected
        - Clear markers present
        
        Args:
            flags: Extracted flags
            word: Original word
            
        Returns:
            Confidence score [0.0, 1.0]
        """
        confidence = 0.0
        
        # Boost for each detected feature
        if flags.case:
            confidence += 0.3
        if flags.number:
            confidence += 0.2
        if flags.gender:
            confidence += 0.2
        if flags.definiteness:
            confidence += 0.2
        
        # Boost for diacritics present
        if self._has_diacritics(word):
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _remove_diacritics(self, text: str) -> str:
        """Remove all Arabic diacritics from text."""
        diacritics = re.compile(r'[\u064B-\u065F\u0670]')
        return diacritics.sub('', text)
    
    def _is_diacritic(self, char: str) -> bool:
        """Check if character is a diacritic."""
        return '\u064B' <= char <= '\u065F' or char == '\u0670'
    
    def _has_diacritics(self, text: str) -> bool:
        """Check if text contains any diacritics."""
        for char in text:
            if self._is_diacritic(char):
                return True
        return False


def extract_morphology_flags(word: str) -> MorphologyFlags:
    """
    Convenience function to extract morphology flags.
    
    Args:
        word: Arabic word
        
    Returns:
        MorphologyFlags object
        
    Examples:
        >>> flags = extract_morphology_flags("الْكِتَابُ")
        >>> flags.definiteness
        True
        >>> flags.case
        'nominative'
    """
    extractor = MorphologyFlagsExtractor()
    return extractor.extract(word)
