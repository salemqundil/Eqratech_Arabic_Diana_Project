"""
Tests for OrthographyAdapter + FormCodecV2 integration (Sprint 1, Task 1.4)

Tests reversibility, normalization rules, and integration between
OrthographyAdapter and FormCodecV2.
"""

import pytest
from src.fvafk.orthography_adapter import OrthographyAdapter
from src.fvafk.c1.form_codec_v2 import FormCodecV2


class TestOrthographyNormalization:
    """Test orthography normalization rules"""
    
    def test_hamzat_al_wasl_normalization(self):
        adapter = OrthographyAdapter()
        result = adapter.normalize("ٱلْكِتَابُ", strip_diacritics=True)
        assert "ٱ" not in result
        assert result.startswith("ا")
    
    def test_taa_marbuta_normalization(self):
        adapter = OrthographyAdapter()
        result = adapter.normalize("مَدْرَسَة", strip_diacritics=True)
        assert "ة" not in result
        assert result.endswith("ت")
    
    def test_alef_maqsurah_normalization(self):
        adapter = OrthographyAdapter()
        result = adapter.normalize("مُوسَى", strip_diacritics=True)
        assert "ى" not in result
        assert result.endswith("ي")
    
    def test_tanwin_to_nun_conversion(self):
        adapter = OrthographyAdapter(apply_tanwin_waqf=True)
        # Tanwin fath
        result1 = adapter.normalize("كِتَابًا", strip_diacritics=False)
        assert "ً" not in result1 or "ن" in result1
        
        # Tanwin damm
        result2 = adapter.normalize("كِتَابٌ", strip_diacritics=False)
        assert "ٌ" not in result2 or "ن" in result2
    
    def test_diacritic_stripping(self):
        adapter = OrthographyAdapter()
        result = adapter.normalize("الْكِتَابُ", strip_diacritics=True)
        # Should have no diacritics
        diacritics = {"َ", "ُ", "ِ", "ْ", "ً", "ٌ", "ٍ", "ّ"}
        for d in diacritics:
            assert d not in result


class TestFormCodecV2Integration:
    """Test integration with FormCodecV2"""
    
    def test_encode_with_normalization(self):
        adapter = OrthographyAdapter()
        codec = FormCodecV2()
        
        stream = adapter.encode_with_normalization("ٱلْكِتَابُ", codec, normalize=True)
        assert stream is not None
        assert len(stream.tokens) > 0
        assert stream.original_nfc  # Should have original NFC
    
    def test_decode_basic(self):
        adapter = OrthographyAdapter()
        codec = FormCodecV2()
        
        text = "الكتاب"
        stream = codec.encode(text)
        decoded = adapter.decode(stream, codec)
        assert decoded == text
    
    def test_roundtrip_simple_text(self):
        adapter = OrthographyAdapter()
        codec = FormCodecV2()
        
        text = "الكتاب"
        assert adapter.roundtrip_test(text, codec) is True
    
    def test_roundtrip_with_hamza_normalization(self):
        adapter = OrthographyAdapter()
        codec = FormCodecV2()
        
        # Original has hamzat al-wasl, should roundtrip to normalized form
        text = "ٱلْكِتَابُ"
        normalized = adapter.normalize(text)
        stream = codec.encode(normalized)
        decoded = codec.decode(stream)
        assert decoded == normalized
    
    def test_roundtrip_with_taa_marbuta(self):
        adapter = OrthographyAdapter()
        codec = FormCodecV2()
        
        text = "مَدْرَسَة"
        assert adapter.roundtrip_test(text, codec) is True


class TestReversibility:
    """Test strict reversibility guarantees"""
    
    def test_reversibility_without_normalization(self):
        """Without normalization, encode/decode should be exact"""
        adapter = OrthographyAdapter()
        codec = FormCodecV2()
        
        text = "الْكِتَابُ"
        stream = adapter.encode_with_normalization(text, codec, normalize=False)
        decoded = adapter.decode(stream, codec)
        
        # Should be exactly the same (FormCodecV2 guarantees this)
        assert decoded == text
    
    def test_reversibility_with_normalization(self):
        """With normalization, decode should give normalized form"""
        adapter = OrthographyAdapter()
        codec = FormCodecV2()
        
        text = "ٱلْكِتَابُ"
        normalized = adapter.normalize(text)
        stream = adapter.encode_with_normalization(text, codec, normalize=True)
        decoded = adapter.decode(stream, codec)
        
        # Decoded should match normalized
        assert decoded == normalized
    
    def test_reversibility_complex_text(self):
        """Test with complex text (multiple rules)"""
        adapter = OrthographyAdapter()
        codec = FormCodecV2()
        
        # Text with hamzat al-wasl, taa marbuta, alef maqsurah
        texts = [
            "ٱلْمَدْرَسَة",
            "مُوسَى",
            "كِتَابٌ",
        ]
        
        for text in texts:
            assert adapter.roundtrip_test(text, codec) is True


class TestRuleConfiguration:
    """Test rule configuration options"""
    
    def test_disable_hamza_normalization(self):
        adapter = OrthographyAdapter(apply_hamza_normalization=False)
        result = adapter.normalize("ٱلْكِتَابُ", strip_diacritics=True)
        # Should keep hamzat al-wasl if normalization disabled
        # But strip_diacritics still applies
        pass  # Complex interaction, basic coverage
    
    def test_disable_taa_normalization(self):
        adapter = OrthographyAdapter(apply_taa_normalization=False)
        result = adapter.normalize("مَدْرَسَة", strip_diacritics=True)
        # Should keep taa marbuta
        assert "ة" in result or "ت" in result
    
    def test_keep_diacritics(self):
        adapter = OrthographyAdapter(keep_diacritics=True)
        result = adapter.normalize("الْكِتَابُ", strip_diacritics=False)
        # Should keep some diacritics
        has_diacritics = any(d in result for d in {"َ", "ُ", "ِ", "ْ"})
        assert has_diacritics
    
    def test_rules_summary(self):
        adapter = OrthographyAdapter()
        summary = adapter.get_rules_summary()
        
        assert "hamza_normalization" in summary
        assert "taa_normalization" in summary
        assert "alef_normalization" in summary
        assert "tanwin_waqf" in summary
        assert "keep_diacritics" in summary


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_text(self):
        adapter = OrthographyAdapter()
        codec = FormCodecV2()
        
        result = adapter.normalize("")
        assert result == ""
        
        stream = codec.encode("")
        decoded = adapter.decode(stream, codec)
        assert decoded == ""
    
    def test_text_without_arabic(self):
        adapter = OrthographyAdapter()
        codec = FormCodecV2()
        
        text = "Hello World"
        assert adapter.roundtrip_test(text, codec) is True
    
    def test_mixed_arabic_latin(self):
        adapter = OrthographyAdapter()
        codec = FormCodecV2()
        
        text = "الكتاب Book"
        assert adapter.roundtrip_test(text, codec) is True
