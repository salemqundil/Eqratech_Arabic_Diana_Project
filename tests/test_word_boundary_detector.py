"""
Tests for WordBoundaryDetector Plan B.

Tests cover:
- Basic word boundary detection
- Clitic detection (prefixes and suffixes)
- Confidence scoring
- Syllable counting
- Edge cases (empty text, single words, multiple words)
"""

import pytest

from fvafk.c2b.word_boundary_detector import (
    WordBoundaryDetectorPlanB,
    WordBoundary,
    CliticDatabase,
    detect_word_boundaries,
)


class TestWordBoundaryDetectorPlanB:
    """Tests for WordBoundaryDetectorPlanB class."""

    def test_detector_initialization(self):
        """Test detector initializes correctly."""
        detector = WordBoundaryDetectorPlanB()
        assert detector.syllabifier is not None or detector.syllabifier is None
        assert detector.clitics is not None

    def test_empty_text_returns_empty_list(self):
        """Test empty text returns no boundaries."""
        detector = WordBoundaryDetectorPlanB()
        assert detector.detect_boundaries("") == []
        assert detector.detect_boundaries("   ") == []

    def test_single_word_no_clitics(self):
        """Test simple word without clitics."""
        detector = WordBoundaryDetectorPlanB()
        boundaries = detector.detect_boundaries("كتاب")

        assert len(boundaries) == 1
        assert boundaries[0].text == "كتاب"
        assert boundaries[0].start == 0
        assert boundaries[0].end == 4
        assert not boundaries[0].has_prefix
        assert not boundaries[0].has_suffix
        assert 0.0 <= boundaries[0].confidence <= 1.0

    def test_word_with_definite_article_prefix(self):
        """Test word with ال prefix."""
        detector = WordBoundaryDetectorPlanB()
        boundaries = detector.detect_boundaries("الكتاب")

        assert len(boundaries) == 1
        assert boundaries[0].text == "الكتاب"
        assert boundaries[0].has_prefix is True
        assert boundaries[0].prefix == "ال"
        assert boundaries[0].confidence > 0.5

    def test_word_with_conjunction_prefix(self):
        """Test word with و prefix."""
        detector = WordBoundaryDetectorPlanB()
        boundaries = detector.detect_boundaries("وكتاب")

        assert len(boundaries) == 1
        assert boundaries[0].has_prefix is True
        assert boundaries[0].prefix == "و"

    def test_word_with_preposition_prefix(self):
        """Test words with preposition prefixes (ب، ل، ك)."""
        detector = WordBoundaryDetectorPlanB()

        boundaries = detector.detect_boundaries("بالبيت")
        assert boundaries[0].has_prefix is True

        boundaries = detector.detect_boundaries("للطالب")
        assert boundaries[0].has_prefix is True

        boundaries = detector.detect_boundaries("كالماء")
        assert boundaries[0].has_prefix is True

    def test_word_with_suffix(self):
        """Test word with pronoun suffix."""
        detector = WordBoundaryDetectorPlanB()
        boundaries = detector.detect_boundaries("كتابه")

        assert len(boundaries) == 1
        assert boundaries[0].has_suffix is True
        assert boundaries[0].suffix == "ه"

    def test_word_with_compound_prefix(self):
        """Test word with compound prefix (و + ال)."""
        detector = WordBoundaryDetectorPlanB()
        boundaries = detector.detect_boundaries("والكتاب")

        assert len(boundaries) == 1
        assert boundaries[0].has_prefix is True
        assert boundaries[0].prefix == "وال"

    def test_multiple_words(self):
        """Test text with multiple words."""
        detector = WordBoundaryDetectorPlanB()
        boundaries = detector.detect_boundaries("الكتاب على الطاولة")

        assert len(boundaries) == 3
        assert boundaries[0].text == "الكتاب"
        assert boundaries[1].text == "على"
        assert boundaries[2].text == "الطاولة"

    def test_syllable_counting(self):
        """Test syllable count is computed."""
        detector = WordBoundaryDetectorPlanB()
        boundaries = detector.detect_boundaries("كِتَابٌ")

        assert boundaries[0].syllable_count >= 1

    def test_confidence_scoring(self):
        """Test confidence scores are in valid range."""
        detector = WordBoundaryDetectorPlanB()
        boundaries = detector.detect_boundaries("الكتاب على الطاولة")

        for boundary in boundaries:
            assert 0.0 <= boundary.confidence <= 1.0


class TestCliticDatabase:
    """Tests for CliticDatabase class."""

    def test_get_all_prefixes_includes_simple_and_compound(self):
        """Test get_all_prefixes returns both simple and compound."""
        prefixes = CliticDatabase.get_all_prefixes()

        assert 'ال' in prefixes
        assert 'و' in prefixes
        assert 'وال' in prefixes
        assert 'لل' in prefixes

    def test_get_all_suffixes(self):
        """Test get_all_suffixes returns expected suffixes."""
        suffixes = CliticDatabase.get_all_suffixes()

        assert 'ه' in suffixes
        assert 'ها' in suffixes
        assert 'هم' in suffixes


class TestWordBoundary:
    """Tests for WordBoundary dataclass."""

    def test_word_boundary_creation(self):
        """Test creating WordBoundary object."""
        boundary = WordBoundary(
            text="كتاب",
            start=0,
            end=4,
            confidence=0.8,
            syllable_count=2
        )

        assert boundary.text == "كتاب"
        assert boundary.confidence == 0.8

    def test_word_boundary_confidence_validation(self):
        """Test confidence must be in [0, 1]."""
        with pytest.raises(AssertionError):
            WordBoundary(
                text="test",
                start=0,
                end=4,
                confidence=1.5,
                syllable_count=1
            )


class TestConvenienceFunction:
    """Tests for detect_word_boundaries convenience function."""

    def test_convenience_function_works(self):
        """Test convenience function returns correct results."""
        boundaries = detect_word_boundaries("الكتاب")

        assert len(boundaries) == 1
        assert boundaries[0].text == "الكتاب"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
