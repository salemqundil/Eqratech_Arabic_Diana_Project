"""
WordForm Builder: Convert C2B output to WordForm instances

This module provides the WordFormBuilder class that converts the output
from the C2B (morphology) pipeline into WordForm instances ready for
the Syntax Layer.

Author: Hussein Hiyassat
Date: 2025-02-12
Version: 1.0
"""

from typing import List, Dict, Any, Optional
from .word_form import (
    WordForm, Root, Pattern, Span, Affixes,
    PartOfSpeech, Case, Number, Gender
)


class WordFormBuilder:
    """
    Builds WordForm instances from C2B output
    
    The builder handles conversion from the C2B morphological analysis
    format to the unified WordForm representation.
    
    Examples:
        >>> builder = WordFormBuilder()
        >>> c2b_word = {
        ...     'word': 'الْكِتَابُ',
        ...     'span': {'start': 0, 'end': 10},
        ...     'kind': 'noun',
        ...     'root': {'letters': ['ك', 'ت', 'ب'], 'formatted': 'ك-ت-ب'},
        ...     'features': {'definite': True, 'case': 'nominative'}
        ... }
        >>> word_form = builder.from_c2b(c2b_word, word_id=0)
        >>> print(word_form.surface)
        الْكِتَابُ
    """
    
    def __init__(self):
        """Initialize the builder"""
        self._next_id = 0
    
    def from_c2b(self, c2b_word: Dict[str, Any], word_id: Optional[int] = None) -> WordForm:
        """
        Convert C2B output to WordForm
        
        Args:
            c2b_word: Dictionary containing C2B analysis
            word_id: Optional ID to assign (auto-increments if not provided)
        
        Returns:
            WordForm instance
        
        Examples:
            >>> builder = WordFormBuilder()
            >>> c2b = {'word': 'كِتَابٌ', 'kind': 'noun', 'span': {'start': 0, 'end': 6}}
            >>> wf = builder.from_c2b(c2b)
            >>> wf.is_noun
            True
        """
        if word_id is None:
            word_id = self._next_id
            self._next_id += 1
        
        return WordForm(
            word_id=word_id,
            surface=c2b_word['word'],
            span=self._extract_span(c2b_word),
            root=self._extract_root(c2b_word),
            pattern=self._extract_pattern(c2b_word),
            affixes=self._extract_affixes(c2b_word),
            pos=self._extract_pos(c2b_word),
            case=self._extract_case(c2b_word),
            definiteness=self._extract_definiteness(c2b_word),
            number=self._extract_number(c2b_word),
            gender=self._extract_gender(c2b_word),
            metadata=self._extract_metadata(c2b_word)
        )
    
    def from_c2b_batch(self, c2b_words: List[Dict[str, Any]]) -> List[WordForm]:
        """
        Convert multiple C2B outputs to WordForm instances
        
        Args:
            c2b_words: List of C2B word dictionaries
        
        Returns:
            List of WordForm instances
        
        Examples:
            >>> builder = WordFormBuilder()
            >>> c2b_list = [
            ...     {'word': 'الكتاب', 'kind': 'noun', 'span': {'start': 0, 'end': 6}},
            ...     {'word': 'جديد', 'kind': 'noun', 'span': {'start': 7, 'end': 11}}
            ... ]
            >>> word_forms = builder.from_c2b_batch(c2b_list)
            >>> len(word_forms)
            2
        """
        return [self.from_c2b(c2b_word, word_id=i) for i, c2b_word in enumerate(c2b_words)]
    
    def reset_id(self):
        """Reset the word ID counter"""
        self._next_id = 0
    
    # =========================================================================
    # Extraction Methods
    # =========================================================================
    
    def _extract_span(self, c2b_word: Dict[str, Any]) -> Span:
        """Extract span from C2B output"""
        span_dict = c2b_word.get('span', {})
        return Span(
            start=span_dict.get('start', 0),
            end=span_dict.get('end', 0)
        )
    
    def _extract_root(self, c2b_word: Dict[str, Any]) -> Optional[Root]:
        """Extract root from C2B output"""
        root_dict = c2b_word.get('root')
        if not root_dict:
            return None
        
        letters = root_dict.get('letters', [])
        if not letters:
            return None
        
        return Root(
            letters=tuple(letters),
            formatted=root_dict.get('formatted', '-'.join(letters)),
            type=root_dict.get('type', 'trilateral')
        )
    
    def _extract_pattern(self, c2b_word: Dict[str, Any]) -> Optional[Pattern]:
        """Extract pattern from C2B output"""
        pattern_dict = c2b_word.get('pattern')
        if not pattern_dict:
            return None
        
        template = pattern_dict.get('template')
        if not template:
            return None
        
        # Extract confidence from pattern features if available
        confidence = 1.0
        if 'features' in pattern_dict:
            conf_str = pattern_dict['features'].get('confidence', '1.0')
            try:
                confidence = float(conf_str)
            except (ValueError, TypeError):
                confidence = 1.0
        
        return Pattern(
            template=template,
            type=pattern_dict.get('type', 'unknown'),
            category=pattern_dict.get('category', 'unknown'),
            confidence=confidence
        )
    
    def _extract_affixes(self, c2b_word: Dict[str, Any]) -> Optional[Affixes]:
        """Extract affixes from C2B output"""
        affixes_dict = c2b_word.get('affixes')
        if not affixes_dict:
            return None
        
        prefix = affixes_dict.get('prefix')
        suffix = affixes_dict.get('suffix')
        
        if prefix is None and suffix is None:
            return None
        
        return Affixes(prefix=prefix, suffix=suffix)
    
    def _extract_pos(self, c2b_word: Dict[str, Any]) -> PartOfSpeech:
        """Extract part of speech from C2B output"""
        kind = c2b_word.get('kind', 'unknown')
        
        # Check for particle/name special cases
        if 'particle' in c2b_word:
            return PartOfSpeech.PARTICLE
        if 'name' in c2b_word:
            # Names are treated as nouns
            return PartOfSpeech.NOUN
        
        # Map from C2B kind to PartOfSpeech
        pos_mapping = {
            'noun': PartOfSpeech.NOUN,
            'verb': PartOfSpeech.VERB,
            'particle': PartOfSpeech.PARTICLE,
            'pronoun': PartOfSpeech.PRONOUN,
            'adjective': PartOfSpeech.ADJECTIVE,
            'adverb': PartOfSpeech.ADVERB,
        }
        
        return pos_mapping.get(kind, PartOfSpeech.UNKNOWN)
    
    def _extract_case(self, c2b_word: Dict[str, Any]) -> Case:
        """Extract grammatical case from C2B output"""
        features = c2b_word.get('features', {})
        case_str = features.get('case')
        
        if not case_str:
            return Case.UNKNOWN
        
        # Map from C2B case strings
        case_mapping = {
            'nominative': Case.NOMINATIVE,
            'accusative': Case.ACCUSATIVE,
            'genitive': Case.GENITIVE,
            'مرفوع': Case.NOMINATIVE,
            'منصوب': Case.ACCUSATIVE,
            'مجرور': Case.GENITIVE,
        }
        
        return case_mapping.get(case_str, Case.UNKNOWN)
    
    def _extract_definiteness(self, c2b_word: Dict[str, Any]) -> bool:
        """Extract definiteness from C2B output"""
        features = c2b_word.get('features', {})
        definite = features.get('definite')
        
        if definite is None:
            # Check if word starts with 'ال'
            word = c2b_word.get('word', '')
            return word.startswith('ال') or word.startswith('الـ')
        
        return bool(definite)
    
    def _extract_number(self, c2b_word: Dict[str, Any]) -> Number:
        """Extract grammatical number from C2B output"""
        features = c2b_word.get('features', {})
        number_str = features.get('number')
        
        if not number_str:
            return Number.UNKNOWN
        
        # Map from C2B number strings
        number_mapping = {
            'singular': Number.SINGULAR,
            'dual': Number.DUAL,
            'plural': Number.PLURAL,
            'مفرد': Number.SINGULAR,
            'مثنى': Number.DUAL,
            'جمع': Number.PLURAL,
        }
        
        return number_mapping.get(number_str, Number.UNKNOWN)
    
    def _extract_gender(self, c2b_word: Dict[str, Any]) -> Gender:
        """Extract grammatical gender from C2B output"""
        features = c2b_word.get('features', {})
        gender_str = features.get('gender')
        
        if not gender_str:
            return Gender.UNKNOWN
        
        # Map from C2B gender strings
        gender_mapping = {
            'masculine': Gender.MASCULINE,
            'feminine': Gender.FEMININE,
            'مذكر': Gender.MASCULINE,
            'مؤنث': Gender.FEMININE,
        }
        
        return gender_mapping.get(gender_str, Gender.UNKNOWN)
    
    def _extract_metadata(self, c2b_word: Dict[str, Any]) -> Dict[str, Any]:
        """Extract additional metadata from C2B output"""
        metadata = {}
        
        # Store original C2B kind
        if 'kind' in c2b_word:
            metadata['c2b_kind'] = c2b_word['kind']
        
        # Store pattern type if available
        if 'pattern' in c2b_word and 'type' in c2b_word['pattern']:
            metadata['pattern_type'] = c2b_word['pattern']['type']
        
        # Store confidence if available
        if 'features' in c2b_word and 'confidence' in c2b_word['features']:
            metadata['confidence'] = c2b_word['features']['confidence']
        
        # Store any special markers
        if 'name' in c2b_word:
            metadata['is_name'] = True
            metadata['name_status'] = c2b_word['name'].get('status')
        
        if 'particle' in c2b_word:
            metadata['particle_category'] = c2b_word['particle'].get('category')
        
        return metadata


# =============================================================================
# Convenience Functions
# =============================================================================

def build_word_form(c2b_word: Dict[str, Any], word_id: Optional[int] = None) -> WordForm:
    """
    Convenience function to build a single WordForm
    
    Args:
        c2b_word: C2B word dictionary
        word_id: Optional word ID
    
    Returns:
        WordForm instance
    """
    builder = WordFormBuilder()
    return builder.from_c2b(c2b_word, word_id=word_id)


def build_word_forms(c2b_words: List[Dict[str, Any]]) -> List[WordForm]:
    """
    Convenience function to build multiple WordForms
    
    Args:
        c2b_words: List of C2B word dictionaries
    
    Returns:
        List of WordForm instances
    """
    builder = WordFormBuilder()
    return builder.from_c2b_batch(c2b_words)
