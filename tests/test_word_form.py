"""
Tests for WordForm and WordFormBuilder

Author: Hussein Hiyassat
Date: 2025-02-12
"""

import pytest
import sys
sys.path.insert(0, 'src')

from fvafk.c2b.word_form.word_form import (
    WordForm, Root, Pattern, Span, Affixes,
    PartOfSpeech, Case, Number, Gender, SyntaxRole
)
from fvafk.c2b.word_form.word_form_builder import (
    WordFormBuilder, build_word_form, build_word_forms
)


# =============================================================================
# Test Basic Functionality
# =============================================================================

class TestBasicWordForm:
    """Test basic WordForm functionality"""
    
    def test_creation(self):
        """Test basic WordForm creation"""
        word = WordForm(
            surface='كِتَابٌ',
            span=Span(0, 6),
            pos=PartOfSpeech.NOUN
        )
        assert word.surface == 'كِتَابٌ'
        assert word.is_noun
    
    def test_case_arabic(self):
        """Test Case enum with Arabic"""
        word = WordForm(
            surface='كتاب',
            span=Span(0, 4),
            case=Case.NOMINATIVE
        )
        assert word.case.arabic == "مرفوع"
    
    def test_agreement(self):
        """Test agreement checking"""
        word1 = WordForm(
            surface='الكتاب',
            span=Span(0, 6),
            number=Number.SINGULAR,
            gender=Gender.MASCULINE
        )
        word2 = WordForm(
            surface='الجديد',
            span=Span(7, 13),
            number=Number.SINGULAR,
            gender=Gender.MASCULINE
        )
        assert word1.agrees_with(word2, ['number', 'gender'])


class TestWordFormBuilder:
    """Test WordFormBuilder"""
    
    def test_basic_conversion(self):
        """Test C2B to WordForm conversion"""
        c2b_word = {
            'word': 'كِتَابٌ',
            'span': {'start': 0, 'end': 6},
            'kind': 'noun',
            'features': {
                'case': 'nominative',
                'number': 'singular'
            }
        }
        
        word = build_word_form(c2b_word)
        assert word.surface == 'كِتَابٌ'
        assert word.is_noun
        assert word.case == Case.NOMINATIVE
    
    def test_with_root(self):
        """Test conversion with root"""
        c2b_word = {
            'word': 'كِتَابٌ',
            'span': {'start': 0, 'end': 6},
            'kind': 'noun',
            'root': {
                'letters': ['ك', 'ت', 'ب'],
                'formatted': 'ك-ت-ب'
            },
            'features': {}
        }
        
        word = build_word_form(c2b_word)
        assert word.has_root
        assert word.root.formatted == 'ك-ت-ب'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
