"""
ISNADI Linker V1.1: Enhanced with modifier/phrase skipping

This version can skip over modifiers and phrases between مبتدأ and خبر

Author: Hussein Hiyassat  
Date: 2025-02-13
Version: 1.1
"""

from typing import List, Optional
import sys
sys.path.insert(0, 'src')

from fvafk.c2b.word_form import (
    WordForm, PartOfSpeech, Case, Number, Gender
)
from fvafk.syntax.linkers.link import Link, LinkType


class IsnadiLinkerV2:
    """
    Enhanced ISNADI Linker that can skip modifiers
    
    Improvements over V1:
    - Skips particles between مبتدأ and خبر
    - Skips adjectives/attributes
    - Looks ahead up to N words for potential خبر
    - Handles complex noun phrases
    
    Examples:
        >>> # والذين معه أشداءُ
        >>> # Can now detect: والذين (مبتدأ) ← أشداءُ (خبر)
        >>> # Skipping: معه (particle)
    """
    
    def __init__(self, 
                 require_definiteness: bool = False,
                 max_lookahead: int = 5):
        """
        Initialize enhanced ISNADI linker
        
        Args:
            require_definiteness: If True, require مبتدأ to be definite
            max_lookahead: Maximum words to look ahead for خبر
        """
        self.require_definiteness = require_definiteness
        self.max_lookahead = max_lookahead
    
    def find_links(self, words: List[WordForm]) -> List[Link]:
        """
        Find all ISNADI links with modifier skipping
        
        Args:
            words: List of WordForm instances
        
        Returns:
            List of Link instances
        """
        links = []
        
        # Scan for potential مبتدأ
        for i, word in enumerate(words):
            if self._is_mubtada(word, position=i):
                # Look for خبر, skipping modifiers
                khabar = self._find_khabar_with_skip(words, mubtada_idx=i)
                
                if khabar is not None:
                    khabar_idx, confidence, reason = khabar
                    
                    # Create ISNADI link
                    link = Link(
                        link_type=LinkType.ISNADI,
                        head_id=word.word_id,
                        dependent_id=words[khabar_idx].word_id,
                        confidence=confidence,
                        reason=reason
                    )
                    links.append(link)
        
        return links
    
    def _is_mubtada(self, word: WordForm, position: int) -> bool:
        """Check if a word can be مبتدأ"""
        # Must be noun
        if not word.is_noun:
            return False
        
        # Must be nominative
        if word.case != Case.NOMINATIVE:
            return False
        
        # Optionally check definiteness
        if self.require_definiteness and not word.is_definite:
            return False
        
        # Usually at beginning (be more lenient)
        if position > 3:
            return False
        
        return True
    
    def _find_khabar_with_skip(self, 
                               words: List[WordForm], 
                               mubtada_idx: int) -> Optional[tuple]:
        """
        Find خبر, skipping over modifiers/particles
        
        Args:
            words: List of all words
            mubtada_idx: Index of the مبتدأ
        
        Returns:
            Tuple of (khabar_index, confidence, reason) or None
        """
        mubtada = words[mubtada_idx]
        
        # Look ahead with skipping
        end_idx = min(len(words), mubtada_idx + self.max_lookahead + 1)
        
        for i in range(mubtada_idx + 1, end_idx):
            candidate = words[i]
            
            # Skip particles (like معه، في، على، etc.)
            if candidate.is_particle:
                continue
            
            # Skip genitive nouns (مضاف إليه)
            if candidate.case == Case.GENITIVE:
                continue
            
            # Skip accusative nouns (مفعول به)
            if candidate.case == Case.ACCUSATIVE:
                continue
            
            # Check if this could be خبر
            if self._is_valid_khabar(mubtada, candidate):
                confidence, reason = self._calculate_confidence(
                    mubtada, candidate, 
                    words_between=i - mubtada_idx - 1
                )
                return (i, confidence, reason)
        
        return None
    
    def _is_valid_khabar(self, mubtada: WordForm, candidate: WordForm) -> bool:
        """Check if candidate can be خبر"""
        # Must be noun or adjective
        if not (candidate.is_noun or candidate.pos == PartOfSpeech.ADJECTIVE):
            return False
        
        # Must be nominative
        if candidate.case != Case.NOMINATIVE:
            return False
        
        # Should agree in number and gender
        if not mubtada.agrees_with(candidate, ['number', 'gender']):
            return False
        
        return True
    
    def _calculate_confidence(self, 
                              mubtada: WordForm, 
                              khabar: WordForm,
                              words_between: int = 0) -> tuple:
        """
        Calculate confidence with penalty for words between
        
        Args:
            mubtada: The مبتدأ
            khabar: The خبر
            words_between: Number of words skipped
        
        Returns:
            Tuple of (confidence_score, reason_string)
        """
        confidence = 1.0
        reasons = []
        
        # Check case agreement
        if mubtada.case == khabar.case == Case.NOMINATIVE:
            reasons.append("case agreement")
        else:
            confidence *= 0.8
        
        # Check number agreement
        if mubtada.number == khabar.number:
            reasons.append("number agreement")
        else:
            confidence *= 0.7
        
        # Check gender agreement
        if mubtada.gender == khabar.gender:
            reasons.append("gender agreement")
        else:
            confidence *= 0.7
        
        # Bonus for definite مبتدأ
        if mubtada.is_definite:
            reasons.append("definite mubtada")
            confidence = min(1.0, confidence * 1.1)
        
        # Small penalty for words between (reduces confidence slightly)
        if words_between > 0:
            penalty = 1.0 - (words_between * 0.05)  # 5% per word
            confidence *= max(0.7, penalty)  # Don't go below 70%
            reasons.append(f"skipped {words_between} word(s)")
        
        reason = "ISNADI: " + ", ".join(reasons)
        return (confidence, reason)


def find_isnadi_links_v2(words: List[WordForm]) -> List[Link]:
    """
    Enhanced convenience function with modifier skipping
    
    Args:
        words: List of WordForm instances
    
    Returns:
        List of Link instances
    """
    linker = IsnadiLinkerV2()
    return linker.find_links(words)
