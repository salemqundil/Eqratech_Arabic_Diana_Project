"""
Tests for ISNADI Linker

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
from fvafk.syntax.linkers.isnadi_linker import IsnadiLinker, find_isnadi_links


class TestLink:
    """Test Link class"""
    
    def test_create_link(self):
        """Test basic link creation"""
        link = Link(
            link_type=LinkType.ISNADI,
            head_id=0,
            dependent_id=1,
            confidence=0.95
        )
        assert link.link_type == LinkType.ISNADI
        assert link.head_id == 0
        assert link.dependent_id == 1
        assert link.confidence == 0.95
    
    def test_link_arabic_name(self):
        """Test Arabic name for link type"""
        link = Link(
            link_type=LinkType.ISNADI,
            head_id=0,
            dependent_id=1
        )
        assert link.link_type.arabic == "إسنادي"
    
    def test_invalid_confidence(self):
        """Test that invalid confidence raises error"""
        with pytest.raises(ValueError):
            Link(
                link_type=LinkType.ISNADI,
                head_id=0,
                dependent_id=1,
                confidence=1.5  # Invalid
            )
    
    def test_same_head_dependent(self):
        """Test that head and dependent cannot be same"""
        with pytest.raises(ValueError):
            Link(
                link_type=LinkType.ISNADI,
                head_id=0,
                dependent_id=0  # Same as head
            )


class TestIsnadiLinker:
    """Test ISNADI Linker"""
    
    def test_simple_nominal_sentence(self):
        """Test: الكتابُ مفيدٌ"""
        words = [
            WordForm(
                word_id=0,
                surface='الْكِتَابُ',
                span=Span(0, 10),
                pos=PartOfSpeech.NOUN,
                case=Case.NOMINATIVE,
                definiteness=True,
                number=Number.SINGULAR,
                gender=Gender.MASCULINE
            ),
            WordForm(
                word_id=1,
                surface='مُفِيدٌ',
                span=Span(11, 17),
                pos=PartOfSpeech.NOUN,
                case=Case.NOMINATIVE,
                definiteness=False,
                number=Number.SINGULAR,
                gender=Gender.MASCULINE
            )
        ]
        
        linker = IsnadiLinker()
        links = linker.find_links(words)
        
        assert len(links) == 1
        assert links[0].link_type == LinkType.ISNADI
        assert links[0].head_id == 0  # الكتاب
        assert links[0].dependent_id == 1  # مفيد
        assert links[0].confidence > 0.9
    
    def test_feminine_agreement(self):
        """Test: الطالبةُ مجتهدةٌ"""
        words = [
            WordForm(
                word_id=0,
                surface='الطَّالِبَةُ',
                span=Span(0, 12),
                pos=PartOfSpeech.NOUN,
                case=Case.NOMINATIVE,
                definiteness=True,
                number=Number.SINGULAR,
                gender=Gender.FEMININE
            ),
            WordForm(
                word_id=1,
                surface='مُجْتَهِدَةٌ',
                span=Span(13, 25),
                pos=PartOfSpeech.NOUN,
                case=Case.NOMINATIVE,
                definiteness=False,
                number=Number.SINGULAR,
                gender=Gender.FEMININE
            )
        ]
        
        linker = IsnadiLinker()
        links = linker.find_links(words)
        
        assert len(links) == 1
        assert links[0].confidence > 0.9
    
    def test_dual_number(self):
        """Test: الطالبانِ مجتهدانِ"""
        words = [
            WordForm(
                word_id=0,
                surface='الطَّالِبَانِ',
                span=Span(0, 14),
                pos=PartOfSpeech.NOUN,
                case=Case.NOMINATIVE,
                definiteness=True,
                number=Number.DUAL,
                gender=Gender.MASCULINE
            ),
            WordForm(
                word_id=1,
                surface='مُجْتَهِدَانِ',
                span=Span(15, 29),
                pos=PartOfSpeech.NOUN,
                case=Case.NOMINATIVE,
                definiteness=False,
                number=Number.DUAL,
                gender=Gender.MASCULINE
            )
        ]
        
        linker = IsnadiLinker()
        links = linker.find_links(words)
        
        assert len(links) == 1
        assert links[0].confidence > 0.9
    
    def test_plural_number(self):
        """Test: الطلابُ مجتهدونَ"""
        words = [
            WordForm(
                word_id=0,
                surface='الطُّلَّابُ',
                span=Span(0, 12),
                pos=PartOfSpeech.NOUN,
                case=Case.NOMINATIVE,
                definiteness=True,
                number=Number.PLURAL,
                gender=Gender.MASCULINE
            ),
            WordForm(
                word_id=1,
                surface='مُجْتَهِدُونَ',
                span=Span(13, 27),
                pos=PartOfSpeech.NOUN,
                case=Case.NOMINATIVE,
                definiteness=False,
                number=Number.PLURAL,
                gender=Gender.MASCULINE
            )
        ]
        
        linker = IsnadiLinker()
        links = linker.find_links(words)
        
        assert len(links) == 1
        assert links[0].confidence > 0.9
    
    def test_no_link_when_case_mismatch(self):
        """Test that no link when case doesn't match"""
        words = [
            WordForm(
                word_id=0,
                surface='الكتابَ',  # منصوب
                span=Span(0, 8),
                pos=PartOfSpeech.NOUN,
                case=Case.ACCUSATIVE,  # Wrong case
                definiteness=True,
                number=Number.SINGULAR
            ),
            WordForm(
                word_id=1,
                surface='مفيدٌ',
                span=Span(9, 14),
                pos=PartOfSpeech.NOUN,
                case=Case.NOMINATIVE,
                number=Number.SINGULAR
            )
        ]
        
        linker = IsnadiLinker()
        links = linker.find_links(words)
        
        assert len(links) == 0
    
    def test_no_link_when_number_mismatch(self):
        """Test lower confidence when number doesn't match"""
        words = [
            WordForm(
                word_id=0,
                surface='الكتابُ',  # مفرد
                span=Span(0, 8),
                pos=PartOfSpeech.NOUN,
                case=Case.NOMINATIVE,
                definiteness=True,
                number=Number.SINGULAR
            ),
            WordForm(
                word_id=1,
                surface='مفيدونَ',  # جمع
                span=Span(9, 17),
                pos=PartOfSpeech.NOUN,
                case=Case.NOMINATIVE,
                number=Number.PLURAL  # Mismatch
            )
        ]
        
        linker = IsnadiLinker()
        links = linker.find_links(words)
        
        # Should not create link due to number mismatch
        assert len(links) == 0
    
    def test_indefinite_mubtada_allowed(self):
        """Test that indefinite مبتدأ is allowed by default"""
        words = [
            WordForm(
                word_id=0,
                surface='كتابٌ',  # نكرة
                span=Span(0, 6),
                pos=PartOfSpeech.NOUN,
                case=Case.NOMINATIVE,
                definiteness=False,  # Indefinite
                number=Number.SINGULAR
            ),
            WordForm(
                word_id=1,
                surface='مفيدٌ',
                span=Span(7, 12),
                pos=PartOfSpeech.NOUN,
                case=Case.NOMINATIVE,
                number=Number.SINGULAR
            )
        ]
        
        # Default: allow indefinite
        linker = IsnadiLinker(require_definiteness=False)
        links = linker.find_links(words)
        assert len(links) == 1
        
        # Strict: require definite
        strict_linker = IsnadiLinker(require_definiteness=True)
        strict_links = strict_linker.find_links(words)
        assert len(strict_links) == 0


class TestConvenienceFunction:
    """Test convenience function"""
    
    def test_find_isnadi_links(self):
        """Test convenience function"""
        words = [
            WordForm(
                word_id=0,
                surface='الكتابُ',
                span=Span(0, 8),
                pos=PartOfSpeech.NOUN,
                case=Case.NOMINATIVE,
                definiteness=True,
                number=Number.SINGULAR
            ),
            WordForm(
                word_id=1,
                surface='مفيدٌ',
                span=Span(9, 14),
                pos=PartOfSpeech.NOUN,
                case=Case.NOMINATIVE,
                number=Number.SINGULAR
            )
        ]
        
        links = find_isnadi_links(words)
        assert len(links) == 1
        assert links[0].link_type == LinkType.ISNADI


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
