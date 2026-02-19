"""
Test for ISNADI Linker V1.1 - Phrase skipping between مبتدأ and خبر

Author: Hussein Hiyassat
Date: 2025-02-13
"""

import pytest
import sys
sys.path.insert(0, 'src')

from fvafk.c2b.word_form import (
    WordForm, PartOfSpeech, Case, Number, Gender, Span
)
from fvafk.syntax.linkers.link import Link, LinkType

# Import V1.1
import importlib.util
spec = importlib.util.spec_from_file_location("isnadi_v1_1", "tools/isnadi_linker_v1_1.py")
isnadi_v1_1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(isnadi_v1_1)


class TestIsnadiV1_1:
    """Test ISNADI Linker V1.1 enhancements"""
    
    def test_isnadi_with_phrase_between(self):
        """Test: الذين معه أشداءُ (with particle between)"""
        words = [
            WordForm(
                word_id=0,
                surface='الذين',
                span=Span(0, 6),
                pos=PartOfSpeech.NOUN,
                case=Case.NOMINATIVE,
                definiteness=True,
                number=Number.PLURAL,
                gender=Gender.MASCULINE
            ),
            WordForm(
                word_id=1,
                surface='معه',
                span=Span(7, 10),
                pos=PartOfSpeech.PARTICLE,
                case=Case.UNKNOWN,
                number=Number.SINGULAR,
                gender=Gender.MASCULINE
            ),
            WordForm(
                word_id=2,
                surface='أشداء',
                span=Span(11, 17),
                pos=PartOfSpeech.NOUN,
                case=Case.NOMINATIVE,
                definiteness=False,
                number=Number.PLURAL,
                gender=Gender.MASCULINE
            ),
        ]
        
        links = isnadi_v1_1.find_isnadi_links(words)
        
        # Should detect the link despite particle in between
        assert len(links) == 1
        assert links[0].head_id == 0  # الذين
        assert links[0].dependent_id == 2  # أشداء
        assert links[0].confidence > 0.9
    
    def test_multiple_particles_skipped(self):
        """Test skipping multiple particles"""
        words = [
            WordForm(
                word_id=0,
                surface='الطالب',
                span=Span(0, 7),
                pos=PartOfSpeech.NOUN,
                case=Case.NOMINATIVE,
                definiteness=True,
                number=Number.SINGULAR,
                gender=Gender.MASCULINE
            ),
            WordForm(
                word_id=1,
                surface='في',
                span=Span(8, 10),
                pos=PartOfSpeech.PARTICLE,
                case=Case.UNKNOWN,
                number=Number.SINGULAR,
                gender=Gender.MASCULINE
            ),
            WordForm(
                word_id=2,
                surface='الفصل',
                span=Span(11, 17),
                pos=PartOfSpeech.NOUN,
                case=Case.GENITIVE,  # مجرور
                definiteness=True,
                number=Number.SINGULAR,
                gender=Gender.MASCULINE
            ),
            WordForm(
                word_id=3,
                surface='مجتهد',
                span=Span(18, 24),
                pos=PartOfSpeech.NOUN,
                case=Case.NOMINATIVE,
                definiteness=False,
                number=Number.SINGULAR,
                gender=Gender.MASCULINE
            ),
        ]
        
        links = isnadi_v1_1.find_isnadi_links(words)
        
        # Should skip both "في" and "الفصل" (genitive)
        assert len(links) == 1
        assert links[0].head_id == 0  # الطالب
        assert links[0].dependent_id == 3  # مجتهد
    
    def test_direct_link_still_works(self):
        """Ensure direct links still work (no regression)"""
        words = [
            WordForm(
                word_id=0,
                surface='الكتاب',
                span=Span(0, 7),
                pos=PartOfSpeech.NOUN,
                case=Case.NOMINATIVE,
                definiteness=True,
                number=Number.SINGULAR,
                gender=Gender.MASCULINE
            ),
            WordForm(
                word_id=1,
                surface='مفيد',
                span=Span(8, 12),
                pos=PartOfSpeech.NOUN,
                case=Case.NOMINATIVE,
                definiteness=False,
                number=Number.SINGULAR,
                gender=Gender.MASCULINE
            ),
        ]
        
        links = isnadi_v1_1.find_isnadi_links(words)
        
        assert len(links) == 1
        assert links[0].confidence == 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
