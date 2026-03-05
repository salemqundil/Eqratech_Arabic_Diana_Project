"""
Tests for MorphSyntaxBridge (Sprint 4 - Task 4.3).

Author: Hussein Hiyassat
Date: 2026-02-21
Sprint: 4
"""

import pytest
from fvafk.c2b.morphology_flags import MorphologyFlags
from fvafk.c2b.syntax import MorphSyntaxBridge, SyntaxFeatures


class SimpleWord:
    """Minimal context object that exposes a .pos attribute."""

    def __init__(self, pos: str):
        self.pos = pos


class TestInferI3rabType:
    """Unit tests for MorphSyntaxBridge.infer_i3rab_type."""

    def setup_method(self):
        self.bridge = MorphSyntaxBridge()

    def test_mubtada_rule(self):
        """Definite nominative at position 0 → mubtada."""
        morph = MorphologyFlags(case="nominative", definiteness=True, confidence=0.9)
        i3rab, conf = self.bridge.infer_i3rab_type(morph, [], 0)
        assert i3rab == "mubtada"
        assert conf == 0.8

    def test_fa_il_after_verb(self):
        """Nominative after verb → fa'il."""
        morph = MorphologyFlags(case="nominative", definiteness=False, confidence=0.9)
        context = [SimpleWord("verb")]
        i3rab, conf = self.bridge.infer_i3rab_type(morph, context, 1)
        assert i3rab == "fa'il"
        assert conf == 0.75

    def test_maf_ul_bihi_after_verb(self):
        """Indefinite accusative after verb → maf'ul_bihi."""
        morph = MorphologyFlags(case="accusative", definiteness=False, confidence=0.9)
        context = [SimpleWord("verb")]
        i3rab, conf = self.bridge.infer_i3rab_type(morph, context, 1)
        assert i3rab == "maf'ul_bihi"
        assert conf == 0.7

    def test_majrur_after_preposition(self):
        """Genitive after preposition → majrur."""
        morph = MorphologyFlags(case="genitive", definiteness=False, confidence=0.9)
        context = [SimpleWord("noun"), SimpleWord("particle")]
        i3rab, conf = self.bridge.infer_i3rab_type(morph, context, 2)
        assert i3rab == "majrur"
        assert conf == 0.9

    def test_khabar_fallback(self):
        """Nominative at non-zero position with no preceding verb → khabar."""
        morph = MorphologyFlags(case="nominative", definiteness=False, confidence=0.9)
        context = [SimpleWord("noun")]
        i3rab, conf = self.bridge.infer_i3rab_type(morph, context, 1)
        assert i3rab == "khabar"
        assert conf == 0.5

    def test_none_morph_returns_none(self):
        """None morph input → (None, 0.0)."""
        i3rab, conf = self.bridge.infer_i3rab_type(None, [], 0)
        assert i3rab is None
        assert conf == 0.0

    def test_unknown_case_returns_none(self):
        """Word with no case and no matching rule → (None, 0.0)."""
        morph = MorphologyFlags(case=None, definiteness=False, confidence=0.3)
        i3rab, conf = self.bridge.infer_i3rab_type(morph, [], 0)
        assert i3rab is None
        assert conf == 0.0


class TestPredictSyntax:
    """Unit tests for MorphSyntaxBridge.predict_syntax."""

    def setup_method(self):
        self.bridge = MorphSyntaxBridge()

    def test_predict_returns_syntax_features(self):
        morph = MorphologyFlags(case="nominative", definiteness=True, confidence=0.9)
        result = self.bridge.predict_syntax(morph, [], 0)
        assert isinstance(result, SyntaxFeatures)

    def test_predict_mubtada(self):
        morph = MorphologyFlags(case="nominative", definiteness=True, confidence=0.9)
        result = self.bridge.predict_syntax(morph, [], 0)
        assert result.i3rab_type_en == "mubtada"
        assert result.i3rab_type_ar == "مبتدأ"
        assert result.case == "nominative"
        assert result.syntactic_role == "subject"

    def test_predict_sets_warning_on_low_confidence(self):
        """Low confidence prediction should trigger a warning."""
        morph = MorphologyFlags(case=None, definiteness=False, confidence=0.1)
        result = self.bridge.predict_syntax(morph, [], 5)
        assert result.confidence < 0.5
        assert result.warning is not None
