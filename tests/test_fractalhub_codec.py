"""
Comprehensive test suite for FractalHub Arabic Text Codec.

Tests the roundtrip theorem: decode(encode(text, mode), mode) == normalize(text, mode)
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from fractalhub.codec.fractalhub_codec import (
    encode_text_to_tokens,
    decode_tokens_to_text,
    normalize_text,
    verify_roundtrip,
    encode_token,
    decode_token,
    encode_position_token,
    decode_position_token,
    TokenTag,
)


class TestTokenEncoding:
    """Test token encoding/decoding primitives."""
    
    def test_encode_decode_token_space(self):
        """Test space token encoding."""
        token = encode_token(TokenTag.T_SPACE, 0)
        tag, payload = decode_token(token)
        assert tag == TokenTag.T_SPACE
        assert payload == 0
    
    def test_encode_decode_token_punct(self):
        """Test punctuation token encoding."""
        token = encode_token(TokenTag.T_PUNCT, 5)
        tag, payload = decode_token(token)
        assert tag == TokenTag.T_PUNCT
        assert payload == 5
    
    def test_position_token_basic(self):
        """Test basic PositionToken encoding."""
        # Encode: ب (ba) with FATHA
        token = encode_position_token(consonant_code=8, vowel_code=2, has_shadda=False, tanwin_type=0)
        
        # Decode
        consonant_code, vowel_code, has_shadda, tanwin_type = decode_position_token(token)
        
        assert consonant_code == 8
        assert vowel_code == 2
        assert has_shadda == False
        assert tanwin_type == 0
    
    def test_position_token_with_shadda(self):
        """Test PositionToken with shadda."""
        token = encode_position_token(consonant_code=30, vowel_code=3, has_shadda=True, tanwin_type=0)
        
        consonant_code, vowel_code, has_shadda, tanwin_type = decode_position_token(token)
        
        assert consonant_code == 30
        assert vowel_code == 3
        assert has_shadda == True
        assert tanwin_type == 0
    
    def test_position_token_with_tanwin(self):
        """Test PositionToken with tanwin."""
        token = encode_position_token(consonant_code=31, vowel_code=2, has_shadda=False, tanwin_type=1)
        
        consonant_code, vowel_code, has_shadda, tanwin_type = decode_position_token(token)
        
        assert consonant_code == 31
        assert vowel_code == 2
        assert has_shadda == False
        assert tanwin_type == 1


class TestNormalization:
    """Test text normalization."""
    
    def test_normalize_vowelled_no_change(self):
        """Test that vowelled text is preserved."""
        text = "السَّلامُ"
        normalized = normalize_text(text, mode='vowelled')
        assert normalized == text
    
    def test_normalize_unvowelled_removes_diacritics(self):
        """Test that unvowelled mode removes diacritics."""
        text = "السَّلامُ عَلَيْكُمْ"
        normalized = normalize_text(text, mode='unvowelled')
        assert normalized == "السلام عليكم"
        # Verify no diacritics remain
        assert '\u064E' not in normalized  # FATHA
        assert '\u064F' not in normalized  # DAMMA
        assert '\u0650' not in normalized  # KASRA
        assert '\u0651' not in normalized  # SHADDA
        assert '\u0652' not in normalized  # SUKUN
    
    def test_normalize_line_endings(self):
        """Test line ending normalization."""
        text_crlf = "مرحبا\r\nبك"
        text_cr = "مرحبا\rبك"
        
        normalized_crlf = normalize_text(text_crlf, mode='vowelled')
        normalized_cr = normalize_text(text_cr, mode='vowelled')
        
        assert normalized_crlf == "مرحبا\nبك"
        assert normalized_cr == "مرحبا\nبك"


class TestRoundtripVowelled:
    """Test roundtrip theorem in vowelled mode."""
    
    def test_roundtrip_simple_vowelled(self):
        """Test simple vowelled text."""
        text = "بَيْتٌ"
        assert verify_roundtrip(text, mode='vowelled')
    
    def test_roundtrip_greeting_vowelled(self):
        """Test vowelled greeting."""
        text = "السَّلامُ عَلَيْكُمْ"
        assert verify_roundtrip(text, mode='vowelled')
    
    def test_roundtrip_with_punctuation_vowelled(self):
        """Test vowelled text with punctuation."""
        text = "مَرْحَبًا بِكَ!"
        assert verify_roundtrip(text, mode='vowelled')
    
    def test_roundtrip_with_hamza_vowelled(self):
        """Test various hamza forms."""
        text = "أَإِؤُئِءْ"
        assert verify_roundtrip(text, mode='vowelled')
    
    def test_roundtrip_with_taa_marbuta_vowelled(self):
        """Test taa marbuta."""
        text = "مَدْرَسَةٌ"
        assert verify_roundtrip(text, mode='vowelled')
    
    def test_roundtrip_with_alif_maqsura_vowelled(self):
        """Test alif maqsura."""
        text = "مُوسَى"
        assert verify_roundtrip(text, mode='vowelled')
    
    def test_roundtrip_multiline_vowelled(self):
        """Test multiline vowelled text."""
        text = "السَّلامُ عَلَيْكُمْ\nمَرْحَبًا"
        assert verify_roundtrip(text, mode='vowelled')


class TestRoundtripUnvowelled:
    """Test roundtrip theorem in unvowelled mode."""
    
    def test_roundtrip_simple_unvowelled(self):
        """Test simple unvowelled text."""
        text = "بيت"
        assert verify_roundtrip(text, mode='unvowelled')
    
    def test_roundtrip_greeting_unvowelled(self):
        """Test unvowelled greeting."""
        text = "السلام عليكم"
        assert verify_roundtrip(text, mode='unvowelled')
    
    def test_roundtrip_with_punctuation_unvowelled(self):
        """Test unvowelled text with punctuation."""
        text = "مرحبا بك!"
        assert verify_roundtrip(text, mode='unvowelled')
    
    def test_roundtrip_vowelled_input_unvowelled_mode(self):
        """Test that vowelled input is stripped in unvowelled mode."""
        text_vowelled = "السَّلامُ عَلَيْكُمْ"
        text_unvowelled = "السلام عليكم"
        
        # Encode vowelled text in unvowelled mode
        tokens = encode_text_to_tokens(text_vowelled, mode='unvowelled')
        decoded = decode_tokens_to_text(tokens, mode='unvowelled')
        
        # Should match the unvowelled version
        assert decoded == text_unvowelled
    
    def test_roundtrip_multiline_unvowelled(self):
        """Test multiline unvowelled text."""
        text = "السلام عليكم\nمرحبا"
        assert verify_roundtrip(text, mode='unvowelled')


class TestSpecialCases:
    """Test special cases and edge conditions."""
    
    def test_empty_string(self):
        """Test empty string."""
        assert verify_roundtrip("", mode='vowelled')
        assert verify_roundtrip("", mode='unvowelled')
    
    def test_spaces_only(self):
        """Test spaces only."""
        text = "   "
        assert verify_roundtrip(text, mode='vowelled')
        assert verify_roundtrip(text, mode='unvowelled')
    
    def test_punctuation_only(self):
        """Test punctuation only."""
        text = ".,؟!:؛"
        assert verify_roundtrip(text, mode='vowelled')
        assert verify_roundtrip(text, mode='unvowelled')
    
    def test_mixed_arabic_punctuation(self):
        """Test mixed Arabic and punctuation."""
        text = "هل تتكلم العربية؟"
        assert verify_roundtrip(text, mode='unvowelled')
    
    def test_numbers(self):
        """Test numeric digits."""
        text = "العدد 123"
        assert verify_roundtrip(text, mode='unvowelled')
    
    def test_arabic_numbers(self):
        """Test Arabic numeric digits."""
        text = "العدد ١٢٣"
        tokens = encode_text_to_tokens(text, mode='unvowelled')
        decoded = decode_tokens_to_text(tokens, mode='unvowelled')
        # Arabic digits are converted to Western digits
        assert "العدد" in decoded
        assert any(c.isdigit() for c in decoded)


class TestComplexSentences:
    """Test complex real-world sentences."""
    
    def test_complex_sentence_vowelled(self):
        """Test complex vowelled sentence."""
        text = "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ"
        assert verify_roundtrip(text, mode='vowelled')
    
    def test_complex_sentence_unvowelled(self):
        """Test complex unvowelled sentence."""
        text = "الحمد لله رب العالمين"
        assert verify_roundtrip(text, mode='unvowelled')
    
    def test_question_sentence(self):
        """Test question sentence."""
        text = "كيف حالك؟"
        assert verify_roundtrip(text, mode='unvowelled')
    
    def test_quoted_text(self):
        """Test quoted text."""
        text = 'قال: "مرحبا"'
        assert verify_roundtrip(text, mode='unvowelled')
    
    def test_parenthetical_text(self):
        """Test text with parentheses."""
        text = "العربية (اللغة الجميلة)"
        assert verify_roundtrip(text, mode='unvowelled')


class TestEncodingConsistency:
    """Test that encoding is deterministic and consistent."""
    
    def test_encoding_deterministic(self):
        """Test that encoding is deterministic."""
        text = "مرحبا"
        tokens1 = encode_text_to_tokens(text, mode='unvowelled')
        tokens2 = encode_text_to_tokens(text, mode='unvowelled')
        assert tokens1 == tokens2
    
    def test_same_text_same_tokens_vowelled(self):
        """Test same vowelled text produces same tokens."""
        text1 = "بَيْتٌ"
        text2 = "بَيْتٌ"
        tokens1 = encode_text_to_tokens(text1, mode='vowelled')
        tokens2 = encode_text_to_tokens(text2, mode='vowelled')
        assert tokens1 == tokens2
    
    def test_different_vowelling_different_tokens(self):
        """Test different vowelling produces different tokens."""
        text1 = "بَيْتٌ"  # baytun
        text2 = "بِيْتُ"  # biytu
        tokens1 = encode_text_to_tokens(text1, mode='vowelled')
        tokens2 = encode_text_to_tokens(text2, mode='vowelled')
        assert tokens1 != tokens2


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
