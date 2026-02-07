"""
Unit Tests for SyllabifyGate

Tests coverage:
- T-01: CV (Light) syllables
- T-02: CVC (Heavy) syllables
- T-03: CVV (Heavy) syllables
- T-04: CVVC/CVCC (Superheavy) syllables
- T-05: Forbidden patterns
- T-06: Transition evaluation
- Edge cases: empty input, invalid sequences
"""

import pytest
from gates.syllabify_gate import (
    SyllabifyGate,
    SyllabifyInput,
    SyllableType,
    SyllableWeight,
    GateStatus,
    TransitionDecision,
    syllabify_phoneme_stream
)


class TestSyllabifyGateBasic:
    """Basic syllabification tests (T-01 to T-04)"""
    
    def test_t01_cv_light_syllable(self):
        """T-01: CV → LIGHT (ma, bi)"""
        phoneme_stream = [{
            "token_id": 0,
            "surface": "ما",
            "phonemes": [
                {"type": "C", "sym": "m", "features": ["CF_PL_001"]},
                {"type": "V", "sym": "a", "features": ["VF_LN_001"]}
            ]
        }]
        
        result = syllabify_phoneme_stream(phoneme_stream)
        
        assert result.status == GateStatus.OK
        assert len(result.syllabification) == 1
        
        token_syll = result.syllabification[0]
        assert len(token_syll.syllables) == 1
        
        syll = token_syll.syllables[0]
        assert syll.type == SyllableType.CV
        assert syll.weight == SyllableWeight.LIGHT
        assert syll.onset == "m"
        assert syll.nucleus == "a"
        assert syll.coda is None
        assert syll.feature_id == "SY_TP_001"
    
    def test_t02_cvc_heavy_syllable(self):
        """T-02: CVC → HEAVY (man, bil)"""
        phoneme_stream = [{
            "token_id": 0,
            "surface": "من",
            "phonemes": [
                {"type": "C", "sym": "m", "features": ["CF_PL_001"]},
                {"type": "V", "sym": "a", "features": ["VF_LN_001"]},
                {"type": "C", "sym": "n", "features": ["CF_PL_004"]}
            ]
        }]
        
        result = syllabify_phoneme_stream(phoneme_stream)
        
        assert result.status == GateStatus.OK
        token_syll = result.syllabification[0]
        assert len(token_syll.syllables) == 1
        
        syll = token_syll.syllables[0]
        assert syll.type == SyllableType.CVC
        assert syll.weight == SyllableWeight.HEAVY
        assert syll.onset == "m"
        assert syll.nucleus == "a"
        assert syll.coda == "n"
        assert syll.feature_id == "SY_TP_002"
    
    def test_t03_cvv_heavy_syllable(self):
        """T-03: CVV → HEAVY (maa, bii)"""
        phoneme_stream = [{
            "token_id": 0,
            "surface": "ما",
            "phonemes": [
                {"type": "C", "sym": "m", "features": ["CF_PL_001"]},
                {"type": "V", "sym": "aa", "features": ["VF_LN_002"]}  # Long vowel
            ]
        }]
        
        result = syllabify_phoneme_stream(phoneme_stream)
        
        assert result.status == GateStatus.OK
        token_syll = result.syllabification[0]
        assert len(token_syll.syllables) == 1
        
        syll = token_syll.syllables[0]
        assert syll.type == SyllableType.CVV
        assert syll.weight == SyllableWeight.HEAVY
        assert syll.onset == "m"
        assert "aa" in syll.nucleus
        assert syll.coda is None
        assert syll.feature_id == "SY_TP_003"
    
    def test_t04_cvvc_superheavy_syllable(self):
        """T-04: CVVC → SUPERHEAVY (maan, biil)"""
        phoneme_stream = [{
            "token_id": 0,
            "surface": "مان",
            "phonemes": [
                {"type": "C", "sym": "m", "features": ["CF_PL_001"]},
                {"type": "V", "sym": "aa", "features": ["VF_LN_002"]},
                {"type": "C", "sym": "n", "features": ["CF_PL_004"]}
            ]
        }]
        
        result = syllabify_phoneme_stream(phoneme_stream)
        
        assert result.status == GateStatus.OK
        token_syll = result.syllabification[0]
        assert len(token_syll.syllables) == 1
        
        syll = token_syll.syllables[0]
        assert syll.type == SyllableType.CVVC
        assert syll.weight == SyllableWeight.SUPERHEAVY
        assert syll.onset == "m"
        assert "aa" in syll.nucleus
        assert syll.coda == "n"
        assert syll.feature_id == "SY_TP_004"
    
    def test_t04_cvcc_superheavy_syllable(self):
        """T-04: CVCC → SUPERHEAVY (bint, qalb)"""
        phoneme_stream = [{
            "token_id": 0,
            "surface": "بنت",
            "phonemes": [
                {"type": "C", "sym": "b", "features": ["CF_PL_001"]},
                {"type": "V", "sym": "i", "features": ["VF_LN_001"]},
                {"type": "C", "sym": "n", "features": ["CF_PL_004"]},
                {"type": "C", "sym": "t", "features": ["CF_PL_003"]}
            ]
        }]
        
        result = syllabify_phoneme_stream(phoneme_stream)
        
        assert result.status == GateStatus.OK
        token_syll = result.syllabification[0]
        assert len(token_syll.syllables) == 1
        
        syll = token_syll.syllables[0]
        assert syll.type == SyllableType.CVCC
        assert syll.weight == SyllableWeight.SUPERHEAVY
        assert syll.onset == "b"
        assert syll.nucleus == "i"
        assert syll.coda == "nt"
        assert syll.feature_id == "SY_TP_005"


class TestSyllabifyGateMultiSyllable:
    """Multi-syllable word tests"""
    
    def test_two_syllable_cvc_cvc(self):
        """كتب → kat-ab (CVC-CVC)"""
        phoneme_stream = [{
            "token_id": 0,
            "surface": "كتب",
            "phonemes": [
                {"type": "C", "sym": "k", "features": ["CF_PL_007"]},
                {"type": "V", "sym": "a", "features": ["VF_LN_001"]},
                {"type": "C", "sym": "t", "features": ["CF_PL_003"]},
                {"type": "V", "sym": "a", "features": ["VF_LN_001"]},
                {"type": "C", "sym": "b", "features": ["CF_PL_001"]}
            ]
        }]
        
        result = syllabify_phoneme_stream(phoneme_stream)
        
        assert result.status == GateStatus.OK
        token_syll = result.syllabification[0]
        assert len(token_syll.syllables) == 2
        
        # First syllable: CVC (kat)
        syll1 = token_syll.syllables[0]
        assert syll1.type == SyllableType.CVC
        assert syll1.onset == "k"
        assert syll1.coda == "t"
        
        # Second syllable: CVC (ab)
        syll2 = token_syll.syllables[1]
        assert syll2.type == SyllableType.CVC
        assert syll2.onset is None or syll2.onset == ""  # No onset after coda
        assert syll2.coda == "b"
    
    def test_three_syllable_cv_cv_cv(self):
        """كتبَ → ka-ta-ba (CV-CV-CV)"""
        phoneme_stream = [{
            "token_id": 0,
            "surface": "كتب",
            "phonemes": [
                {"type": "C", "sym": "k", "features": ["CF_PL_007"]},
                {"type": "V", "sym": "a", "features": ["VF_LN_001"]},
                {"type": "C", "sym": "t", "features": ["CF_PL_003"]},
                {"type": "V", "sym": "a", "features": ["VF_LN_001"]},
                {"type": "C", "sym": "b", "features": ["CF_PL_001"]},
                {"type": "V", "sym": "a", "features": ["VF_LN_001"]}
            ]
        }]
        
        result = syllabify_phoneme_stream(phoneme_stream)
        
        assert result.status == GateStatus.OK
        token_syll = result.syllabification[0]
        assert len(token_syll.syllables) == 3
        
        # All syllables should be CV (LIGHT)
        for syll in token_syll.syllables:
            assert syll.type == SyllableType.CV
            assert syll.weight == SyllableWeight.LIGHT
            assert syll.coda is None


class TestSyllabifyGateTransitions:
    """T-06: Transition evaluation tests"""
    
    def test_transition_between_tokens(self):
        """Test transition detection between two tokens"""
        phoneme_stream = [
            {
                "token_id": 0,
                "surface": "من",
                "phonemes": [
                    {"type": "C", "sym": "m", "features": []},
                    {"type": "V", "sym": "a", "features": ["VF_LN_001"]},
                    {"type": "C", "sym": "n", "features": []}
                ]
            },
            {
                "token_id": 1,
                "surface": "ما",
                "phonemes": [
                    {"type": "C", "sym": "m", "features": []},
                    {"type": "V", "sym": "aa", "features": ["VF_LN_002"]}
                ]
            }
        ]
        
        result = syllabify_phoneme_stream(phoneme_stream)
        
        assert result.status == GateStatus.OK
        assert len(result.transitions) == 1
        
        trans = result.transitions[0]
        assert trans.between["from_token"] == 0
        assert trans.between["to_token"] == 1
        assert trans.pattern["left"] == "CVC"
        assert trans.pattern["right"] == "CVV"
        assert trans.decision == TransitionDecision.KEEP
        assert "boundary_ok" in trans.notes
    
    def test_superheavy_clustering_warning(self):
        """T-06: SUPERHEAVY-SUPERHEAVY should be marked"""
        phoneme_stream = [
            {
                "token_id": 0,
                "surface": "بنت",
                "phonemes": [
                    {"type": "C", "sym": "b", "features": []},
                    {"type": "V", "sym": "i", "features": ["VF_LN_001"]},
                    {"type": "C", "sym": "n", "features": []},
                    {"type": "C", "sym": "t", "features": []}
                ]
            },
            {
                "token_id": 1,
                "surface": "قلب",
                "phonemes": [
                    {"type": "C", "sym": "q", "features": []},
                    {"type": "V", "sym": "a", "features": ["VF_LN_001"]},
                    {"type": "C", "sym": "l", "features": []},
                    {"type": "C", "sym": "b", "features": []}
                ]
            }
        ]
        
        result = syllabify_phoneme_stream(phoneme_stream)
        
        assert result.status == GateStatus.OK
        assert len(result.transitions) == 1
        
        trans = result.transitions[0]
        assert trans.pattern["left"] == "CVCC"
        assert trans.pattern["right"] == "CVCC"
        assert "heavy_clustering" in trans.notes


class TestSyllabifyGateEdgeCases:
    """Edge cases and error handling"""
    
    def test_empty_phoneme_stream(self):
        """Empty input should return empty output"""
        phoneme_stream = []
        result = syllabify_phoneme_stream(phoneme_stream)
        
        assert result.status == GateStatus.OK
        assert len(result.syllabification) == 0
        assert len(result.transitions) == 0
    
    def test_token_with_no_nucleus(self):
        """Token with only consonants should produce warning"""
        phoneme_stream = [{
            "token_id": 0,
            "surface": "invalid",
            "phonemes": [
                {"type": "C", "sym": "k", "features": []},
                {"type": "C", "sym": "t", "features": []}
            ]
        }]
        
        result = syllabify_phoneme_stream(phoneme_stream)
        
        assert result.status == GateStatus.WARNING
        assert len(result.warnings) > 0
        assert "Token 0" in result.warnings[0]
    
    def test_only_vowels_invalid(self):
        """T-05: Only vowels without onset is invalid"""
        phoneme_stream = [{
            "token_id": 0,
            "surface": "invalid",
            "phonemes": [
                {"type": "V", "sym": "a", "features": ["VF_LN_001"]},
                {"type": "V", "sym": "i", "features": ["VF_LN_001"]}
            ]
        }]
        
        result = syllabify_phoneme_stream(phoneme_stream)
        
        # Should produce warning about invalid structure
        assert result.status == GateStatus.WARNING
        assert len(result.warnings) > 0


class TestSyllabifyGateRealExamples:
    """Real Arabic word examples from trace system"""
    
    def test_example_man_who_lies(self):
        """من يكذب - from example_traces.json"""
        phoneme_stream = [
            {
                "token_id": 0,
                "surface": "من",
                "phonemes": [
                    {"type": "C", "sym": "m", "features": ["CF_PL_001", "CF_MN_004"]},
                    {"type": "V", "sym": "a", "features": ["VF_LN_001", "VF_QL_001"]},
                    {"type": "C", "sym": "n", "features": ["CF_PL_004", "CF_MN_004"]}
                ]
            }
        ]
        
        result = syllabify_phoneme_stream(phoneme_stream)
        
        assert result.status == GateStatus.OK
        token_syll = result.syllabification[0]
        assert len(token_syll.syllables) == 1
        
        syll = token_syll.syllables[0]
        assert syll.type == SyllableType.CVC
        assert syll.weight == SyllableWeight.HEAVY
        assert str(syll) == "C(m)V(a)C(n)"
    
    def test_example_yakadhib(self):
        """يكذب → ya-kdhi-b"""
        phoneme_stream = [{
            "token_id": 1,
            "surface": "يكذب",
            "phonemes": [
                {"type": "C", "sym": "y", "features": ["CF_RR_002"]},
                {"type": "V", "sym": "a", "features": ["VF_LN_001"]},
                {"type": "C", "sym": "k", "features": ["CF_RR_001"]},
                {"type": "V", "sym": "dh", "features": ["VF_LN_001"]},
                {"type": "C", "sym": "dh", "features": ["CF_RR_001"]},
                {"type": "V", "sym": "i", "features": ["VF_LN_001"]},
                {"type": "C", "sym": "b", "features": ["CF_RR_001"]}
            ]
        }]
        
        result = syllabify_phoneme_stream(phoneme_stream)
        
        assert result.status == GateStatus.OK
        token_syll = result.syllabification[0]
        
        # Should have multiple syllables
        assert len(token_syll.syllables) >= 2
        
        # All syllables should be valid types
        for syll in token_syll.syllables:
            assert syll.type in [
                SyllableType.CV, SyllableType.CVC,
                SyllableType.CVV, SyllableType.CVVC, SyllableType.CVCC
            ]


class TestSyllabifyGateWeightCalculation:
    """Weight calculation tests"""
    
    def test_total_weight_light(self):
        """Single CV syllable → weight = 1"""
        phoneme_stream = [{
            "token_id": 0,
            "surface": "ما",
            "phonemes": [
                {"type": "C", "sym": "m", "features": []},
                {"type": "V", "sym": "a", "features": ["VF_LN_001"]}
            ]
        }]
        
        result = syllabify_phoneme_stream(phoneme_stream)
        token_syll = result.syllabification[0]
        
        assert token_syll.total_weight == 1  # 1 LIGHT
    
    def test_total_weight_heavy(self):
        """Single CVC syllable → weight = 2"""
        phoneme_stream = [{
            "token_id": 0,
            "surface": "من",
            "phonemes": [
                {"type": "C", "sym": "m", "features": []},
                {"type": "V", "sym": "a", "features": ["VF_LN_001"]},
                {"type": "C", "sym": "n", "features": []}
            ]
        }]
        
        result = syllabify_phoneme_stream(phoneme_stream)
        token_syll = result.syllabification[0]
        
        assert token_syll.total_weight == 2  # 1 HEAVY
    
    def test_total_weight_superheavy(self):
        """Single CVCC syllable → weight = 3"""
        phoneme_stream = [{
            "token_id": 0,
            "surface": "بنت",
            "phonemes": [
                {"type": "C", "sym": "b", "features": []},
                {"type": "V", "sym": "i", "features": ["VF_LN_001"]},
                {"type": "C", "sym": "n", "features": []},
                {"type": "C", "sym": "t", "features": []}
            ]
        }]
        
        result = syllabify_phoneme_stream(phoneme_stream)
        token_syll = result.syllabification[0]
        
        assert token_syll.total_weight == 3  # 1 SUPERHEAVY


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
