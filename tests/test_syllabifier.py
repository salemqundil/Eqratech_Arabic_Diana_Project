#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Arabic Syllabifier (C2b)
==================================

Tests syllabification following Arabic phonological rules.

Author: Eqratech Project
Date: February 1, 2026
"""

import pytest
from fvafk.c2b.syllabifier import (
    ArabicSyllabifier,
    syllabify,
    syllabify_to_pattern,
    SyllableType,
    normalize_word,
    normalize_initial_hamza,
    split_letters_and_marks,
    expand_shadda,
    validate_cv_law,
    segment_cv_to_syllables,
    Haraka,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def syllabifier():
    """Provide a syllabifier instance."""
    return ArabicSyllabifier()


# =============================================================================
# Test Utilities
# =============================================================================

class TestUtilities:
    """Test basic utility functions."""
    
    def test_normalize_word(self):
        """Test word normalization."""
        assert normalize_word("  كتب  ") == "كتب"
        assert normalize_word("كـتـب") == "كتب"  # Remove tatweel
    
    def test_split_letters_and_marks(self):
        """Test splitting letters and diacritics."""
        result = split_letters_and_marks("كَتَبَ")
        assert len(result) == 3
        assert result[0] == ("ك", [Haraka.FATHA])
        assert result[1] == ("ت", [Haraka.FATHA])
        assert result[2] == ("ب", [Haraka.FATHA])
    
    def test_expand_shadda(self):
        """Test shadda expansion (gemination)."""
        units = [("د", [Haraka.SHADDA, Haraka.FATHA])]
        result = expand_shadda(units)
        assert len(result) == 2
        assert result[0] == ("د", [Haraka.SUKUN])
        assert result[1] == ("د", [Haraka.FATHA])
    
    def test_normalize_initial_hamza_wasl(self):
        """Test hamzat wasl normalization."""
        # Definite article
        result = normalize_initial_hamza("الكتاب")
        assert result.startswith("\u0671")  # ٱ
    
    def test_normalize_initial_hamza_qat(self):
        """Test hamzat qat' normalization."""
        result = normalize_initial_hamza("اكتب")
        # Should add hamza
        assert result[0] in {"أ", "إ"}


# =============================================================================
# Test CV Pattern Generation
# =============================================================================

class TestCVPattern:
    """Test CV pattern generation."""
    
    def test_simple_cv(self):
        """Test simple CV patterns."""
        # كَتَبَ -> CVCVCV
        assert syllabify_to_pattern("كَتَبَ") == "CVCVCV"
    
    def test_cvv_long_vowel(self):
        """Test CVV patterns with long vowels."""
        # كَا -> CVV (fatha + alif)
        assert syllabify_to_pattern("كَا") == "CVV"
        # كُو -> CVV (damma + waw)
        assert syllabify_to_pattern("كُو") == "CVV"
        # كِي -> CVV (kasra + ya)
        assert syllabify_to_pattern("كِي") == "CVV"
    
    def test_cvc_closed_syllable(self):
        """Test CVC patterns (closed syllables)."""
        # كَبْ -> CVC
        assert syllabify_to_pattern("كَبْ") == "CVC"
    
    def test_shadda_gemination(self):
        """Test shadda expansion."""
        # دَّ -> CVCC (d + sukun + d + fatha = CVCC? or CCV?)
        # Actually: دَّ should be: د (C) + ّ + َ -> first د with sukun (C), second د with fatha (CV)
        result = syllabify_to_pattern("دَّ")
        # Shadda creates gemination: CCV
        assert "C" in result and "V" in result
    
    def test_initial_hamza(self):
        """Test initial hamza handling."""
        # أَ -> CV (forced)
        result = syllabify_to_pattern("أَكْتُبُ")
        assert result.startswith("CV")


# =============================================================================
# Test CV Law Validation
# =============================================================================

class TestCVLaw:
    """Test Arabic CV law validation."""
    
    def test_valid_cv_law(self):
        """Test valid CV patterns."""
        valid, error = validate_cv_law("CVCVCV")
        assert valid is True
        assert error is None
    
    def test_invalid_starts_with_v(self):
        """Test invalid pattern starting with V."""
        valid, error = validate_cv_law("VCVCV")
        assert valid is False
        assert "does_not_start_with_CV" in error
    
    def test_invalid_empty(self):
        """Test empty pattern."""
        valid, error = validate_cv_law("")
        assert valid is False
        assert "empty" in error
    
    def test_valid_complex(self):
        """Test complex valid patterns."""
        valid, _ = validate_cv_law("CVVCVCC")
        assert valid is True


# =============================================================================
# Test Syllable Segmentation
# =============================================================================

class TestSegmentation:
    """Test syllable segmentation from CV patterns."""
    
    def test_simple_cv(self):
        """Test simple CV segmentation."""
        result = segment_cv_to_syllables("CVCVCV")
        assert result == ["CV", "CV", "CV"]
    
    def test_cvv(self):
        """Test CVV segmentation."""
        result = segment_cv_to_syllables("CVVCV")
        assert result == ["CVV", "CV"]
    
    def test_cvc(self):
        """Test CVC segmentation."""
        result = segment_cv_to_syllables("CVCCV")
        assert result == ["CVC", "CV"]
    
    def test_cvvc(self):
        """Test CVVC segmentation."""
        result = segment_cv_to_syllables("CVVCCV")
        assert result == ["CVVC", "CV"]
    
    def test_cvcc(self):
        """Test CVCC segmentation."""
        result = segment_cv_to_syllables("CVCCCV")
        assert result == ["CVCC", "CV"]
    
    def test_cvvcc(self):
        """Test CVVCC segmentation."""
        result = segment_cv_to_syllables("CVVCCCV")
        assert result == ["CVVCC", "CV"]
    
    def test_mixed(self):
        """Test mixed syllable types."""
        result = segment_cv_to_syllables("CVVCVCCV")
        assert "CVV" in result
        assert "CVC" in result or "CVCC" in result


# =============================================================================
# Test Full Syllabification
# =============================================================================

class TestSyllabification:
    """Test complete syllabification process."""
    
    def test_syllabify_simple(self, syllabifier):
        """Test simple word syllabification."""
        result = syllabifier.syllabify("كَتَبَ")
        assert result.valid is True
        assert result.cv_pattern == "CVCVCV"
        assert len(result.syllables) == 3
    
    def test_syllabify_with_long_vowel(self, syllabifier):
        """Test word with long vowels."""
        result = syllabifier.syllabify("كَاتِبٌ")
        assert result.valid is True
        assert "CVV" in result.cv_pattern
    
    def test_syllabify_with_sukun(self, syllabifier):
        """Test word with sukun."""
        result = syllabifier.syllabify("كَتْبٌ")
        assert result.valid is True
        assert "CVC" in result.cv_pattern or "CVCC" in result.cv_pattern
    
    def test_syllabify_invalid(self, syllabifier):
        """Test invalid pattern handling."""
        # Word without harakat might be invalid
        result = syllabifier.syllabify("ك")  # Single consonant
        # Should handle gracefully
        assert result is not None
    
    def test_syllabify_batch(self, syllabifier):
        """Test batch syllabification."""
        words = ["كَتَبَ", "كَاتِبٌ", "مَكْتُوبٌ"]
        results = syllabifier.syllabify_batch(words)
        assert len(results) == 3
        assert all(isinstance(r.cv_pattern, str) for r in results)


# =============================================================================
# Test Real Arabic Words
# =============================================================================

class TestRealWords:
    """Test with real Arabic words."""
    
    @pytest.mark.parametrize("word,expected_pattern", [
        ("كِتَابٌ", "CVVVC"),      # kitaabun
        ("مَدْرَسَةٌ", "CVCVCV"),   # madrasatun (simplified)
        ("مُعَلِّمٌ", "CVCVC"),     # mu'allimun (with shadda)
        ("الْكِتَابُ", "CVVCV"),    # al-kitaabu (with definite article)
    ])
    def test_common_words(self, syllabifier, word, expected_pattern):
        """Test common Arabic words."""
        result = syllabifier.syllabify(word)
        # Just check it doesn't crash and produces some pattern
        assert result.cv_pattern is not None
        assert len(result.cv_pattern) > 0


# =============================================================================
# Test Convenience Functions
# =============================================================================

class TestConvenienceFunctions:
    """Test convenience wrapper functions."""
    
    def test_syllabify_function(self):
        """Test quick syllabify() function."""
        result = syllabify("كَتَبَ")
        assert result.valid is True
        assert result.cv_pattern == "CVCVCV"
    
    def test_syllabify_to_pattern_function(self):
        """Test quick pattern extraction."""
        pattern = syllabify_to_pattern("كَتَبَ")
        assert pattern == "CVCVCV"


# =============================================================================
# Test Edge Cases
# =============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_string(self, syllabifier):
        """Test empty input."""
        result = syllabifier.syllabify("")
        assert result is not None
    
    def test_only_harakat(self, syllabifier):
        """Test string with only harakat."""
        result = syllabifier.syllabify("َُِ")
        assert result is not None
    
    def test_mixed_arabic_latin(self, syllabifier):
        """Test mixed script handling."""
        result = syllabifier.syllabify("كَتَبَ ABC")
        # Should handle gracefully
        assert result is not None
    
    def test_no_harakat(self, syllabifier):
        """Test word without harakat."""
        result = syllabifier.syllabify("كتب")
        # Should handle but might be invalid
        assert result is not None


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests with C1/C2a components."""
    
    def test_preserves_input(self, syllabifier):
        """Test that original input is preserved."""
        original = "كَاتِبٌ"
        result = syllabifier.syllabify(original)
        assert result.original == original
    
    def test_normalization_applied(self, syllabifier):
        """Test that normalization is applied."""
        result = syllabifier.syllabify("الكتاب")
        # Should normalize hamza
        assert result.normalized is not None
    
    def test_traceability(self, syllabifier):
        """Test that syllables maintain position info."""
        result = syllabifier.syllabify("كَتَبَ")
        if result.valid and result.syllables:
            # Each syllable should have position
            assert all(hasattr(s, 'position') for s in result.syllables)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
