"""
ISNADI Linker V1.1: Enhanced with phrase skipping between مبتدأ and خبر

Allows skipping particles and prepositional phrases between subject and predicate

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


def _is_skippable_between_mubtada_khabar(wf: WordForm) -> bool:
    """
    Words that can be skipped between مبتدأ and خبر in nominal sentences.
    
    Example: (الذين معه أشداء) => "معه" should be skipped.
    
    Args:
        wf: WordForm to check
    
    Returns:
        True if this word can be skipped (particle, PP, adverb)
    """
    # Skip particles
    if wf.pos == PartOfSpeech.PARTICLE:
        return True
    
    # Heuristic: words like معه/عليه/فيه/لديه (prep + pronoun)
    s = wf.surface
    if s.endswith("هُ") or s.endswith("هِ") or s.endswith("ها") or s.endswith("هم"):
        # Small guard: skip only if it's short and looks like prep + pronoun
        if len(s) <= 5:
            return True
    
    return False


class IsnadiLinker:
    """
    Identifies ISNADI (إسنادي) relations in nominal sentences
    
    V1.1 Enhancement: Can skip particles/phrases between مبتدأ and خبر
    
    The ISNADI linker detects مبتدأ (subject) and خبر (predicate) pairs
    in nominal sentences, even when separated by particles or phrases.
    
    Rules:
    1. مبتدأ must be:
       - Noun (اسم)
       - Nominative case (مرفوع)
       - Usually definite (معرفة)
       - At beginning of sentence
    
    2. خبر must be:
       - Noun or adjective
       - Nominative case (مرفوع)
       - Agrees with مبتدأ in number and gender
    
    3. Can skip between them:
       - Particles (معه، فيه، عليه)
       - Prepositional phrases
    
    Examples:
        >>> # الكتابُ مفيدٌ (direct)
        >>> # الذين معه أشداءُ (with particle between)
    """
    
    def __init__(self, require_definiteness: bool = False):
        """
        Initialize ISNADI linker
        
        Args:
            require_definiteness: If True, require مبتدأ to be definite
        """
        self.require_definiteness = require_definiteness
    
    def find_links(self, words: List[WordForm]) -> List[Link]:
        """
        Find all ISNADI links in the given words
        
        Args:
            words: List of WordForm instances representing a sentence
        
        Returns:
            List of Link instances for detected مبتدأ/خبر pairs
        """
        links = []
        
        # Scan for potential مبتدأ
        for i, word in enumerate(words):
            if self._is_mubtada(word, position=i):
                # Look for خبر after it (with skipping)
                khabar = self._find_khabar(words, mubtada_idx=i)
                
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
        """
        Check if a word can be مبتدأ
        
        Args:
            word: WordForm to check
            position: Position in sentence (0-indexed)
        
        Returns:
            True if word can be مبتدأ
        """
        # Must be noun
        if not word.is_noun:
            return False
        
        # Must be nominative
        if word.case != Case.NOMINATIVE:
            return False
        
        # Optionally check definiteness
        if self.require_definiteness and not word.is_definite:
            return False
        
        # Usually at beginning (be lenient for coordinated clauses)
        # Allow position up to 5 to catch coordinated مبتدأ like "والذين"
        if position > 5:
            return False
        
        return True
    
    def _find_khabar(self, words: List[WordForm], mubtada_idx: int) -> Optional[tuple]:
        """
        Find خبر for a given مبتدأ (V1.1: with skipping)
        
        Args:
            words: List of all words
            mubtada_idx: Index of the مبتدأ
        
        Returns:
            Tuple of (khabar_index, confidence, reason) or None
        """
        mubtada = words[mubtada_idx]
        
        # ✅ V1.1 ENHANCEMENT: Loop with skipping
        j = mubtada_idx + 1
        while j < len(words):
            candidate = words[j]
            
            # ✅ NEW: Skip phrases/particles between mubtada and khabar
            if _is_skippable_between_mubtada_khabar(candidate):
                j += 1
                continue
            
            # If not skippable, this is a real candidate for خبر
            if self._is_valid_khabar(mubtada, candidate):
                confidence, reason = self._calculate_confidence(mubtada, candidate)
                return (j, confidence, reason)
            
            # Stop early if we hit something that breaks nominal clause
            # (e.g., a verb, or accusative noun indicating new clause)
            if candidate.is_verb:
                break
            if candidate.case == Case.ACCUSATIVE and candidate.is_noun:
                break
            
            j += 1
        
        return None
    
    def _is_valid_khabar(self, mubtada: WordForm, candidate: WordForm) -> bool:
        """
        Check if candidate can be خبر for the given مبتدأ
        
        Args:
            mubtada: The مبتدأ
            candidate: Candidate for خبر
        
        Returns:
            True if candidate is valid خبر
        """
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
    
    def _calculate_confidence(self, mubtada: WordForm, khabar: WordForm) -> tuple:
        """
        Calculate confidence score for a مبتدأ/خبر pair
        
        Args:
            mubtada: The مبتدأ
            khabar: The خبر
        
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
        
        reason = "ISNADI: " + ", ".join(reasons)
        return (confidence, reason)


def find_isnadi_links(words: List[WordForm]) -> List[Link]:
    """
    Convenience function to find ISNADI links
    
    Args:
        words: List of WordForm instances
    
    Returns:
        List of Link instances
    
    Examples:
        >>> links = find_isnadi_links(words)
        >>> for link in links:
        ...     print(link)
    """
    linker = IsnadiLinker()
    return linker.find_links(words)
