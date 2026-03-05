"""
Tests for SyntaxEvaluator (Sprint 4 - Task 4.4).

Author: Hussein Hiyassat
Date: 2026-02-21
Sprint: 4
"""

import pytest
from fvafk.c2b.syntax import (
    SyntaxEvaluator,
    SyntaxMetrics,
    SyntaxFeatures,
    I3rabComponents,
)


def _make_gold(i3rab_type: str, case: str) -> I3rabComponents:
    return I3rabComponents(i3rab_type=i3rab_type, case=case, confidence=1.0)


def _make_pred(i3rab_type_ar: str, i3rab_type_en: str, case: str, conf: float = 0.8) -> SyntaxFeatures:
    from fvafk.c2b.syntax.mappings import SYNTACTIC_ROLE_MAPPING
    role = SYNTACTIC_ROLE_MAPPING.get(i3rab_type_en, "unknown")
    return SyntaxFeatures(
        syntactic_role=role,
        case=case,
        i3rab_type_ar=i3rab_type_ar,
        i3rab_type_en=i3rab_type_en,
        confidence=conf,
    )


class TestSyntaxEvaluatorPerfect:
    """Test evaluator with perfect predictions."""

    def setup_method(self):
        self.evaluator = SyntaxEvaluator()

    def test_perfect_i3rab_type_accuracy(self):
        gold = [_make_gold("مبتدأ", "nominative")]
        preds = [_make_pred("مبتدأ", "mubtada", "nominative")]
        metrics = self.evaluator.evaluate(preds, gold)
        assert metrics.i3rab_type_accuracy == 1.0

    def test_perfect_case_accuracy(self):
        gold = [_make_gold("مبتدأ", "nominative")]
        preds = [_make_pred("مبتدأ", "mubtada", "nominative")]
        metrics = self.evaluator.evaluate(preds, gold)
        assert metrics.case_accuracy == 1.0

    def test_coverage_for_known_type(self):
        gold = [_make_gold("فاعل", "nominative")]
        preds = [_make_pred("فاعل", "fa'il", "nominative")]
        metrics = self.evaluator.evaluate(preds, gold)
        assert metrics.coverage == 1.0


class TestSyntaxEvaluatorErrors:
    """Test evaluator with wrong predictions."""

    def setup_method(self):
        self.evaluator = SyntaxEvaluator()

    def test_wrong_i3rab_type(self):
        gold = [_make_gold("مبتدأ", "nominative")]
        preds = [_make_pred("خبر", "khabar", "nominative")]
        metrics = self.evaluator.evaluate(preds, gold)
        assert metrics.i3rab_type_accuracy == 0.0

    def test_wrong_case(self):
        gold = [_make_gold("مبتدأ", "nominative")]
        preds = [_make_pred("مبتدأ", "mubtada", "accusative")]
        metrics = self.evaluator.evaluate(preds, gold)
        assert metrics.case_accuracy == 0.0

    def test_partial_accuracy(self):
        gold = [
            _make_gold("مبتدأ", "nominative"),
            _make_gold("خبر", "nominative"),
            _make_gold("فاعل", "nominative"),
        ]
        preds = [
            _make_pred("مبتدأ", "mubtada", "nominative"),   # correct
            _make_pred("مبتدأ", "mubtada", "nominative"),   # wrong type
            _make_pred("فاعل", "fa'il", "nominative"),      # correct
        ]
        metrics = self.evaluator.evaluate(preds, gold)
        assert metrics.i3rab_type_accuracy == pytest.approx(2 / 3)


class TestSyntaxEvaluatorCoverage:
    """Test coverage computation."""

    def setup_method(self):
        self.evaluator = SyntaxEvaluator()

    def test_unknown_prediction_reduces_coverage(self):
        gold = [
            _make_gold("مبتدأ", "nominative"),
            _make_gold("خبر", "nominative"),
        ]
        preds = [
            _make_pred("مبتدأ", "mubtada", "nominative"),
            _make_pred("غير معروف", "unknown", "unknown", conf=0.0),
        ]
        metrics = self.evaluator.evaluate(preds, gold)
        assert metrics.coverage == 0.5

    def test_full_coverage(self):
        gold = [_make_gold("فاعل", "nominative") for _ in range(5)]
        preds = [_make_pred("فاعل", "fa'il", "nominative") for _ in range(5)]
        metrics = self.evaluator.evaluate(preds, gold)
        assert metrics.coverage == 1.0


class TestSyntaxEvaluatorValidation:
    """Test input validation."""

    def setup_method(self):
        self.evaluator = SyntaxEvaluator()

    def test_mismatched_lengths_raises(self):
        gold = [_make_gold("مبتدأ", "nominative")]
        preds = []
        with pytest.raises(ValueError):
            self.evaluator.evaluate(preds, gold)

    def test_empty_lists(self):
        metrics = self.evaluator.evaluate([], [])
        assert metrics.total_words == 0
        assert metrics.i3rab_type_accuracy == 0.0


class TestSyntaxMetricsToDict:
    """Test SyntaxMetrics serialisation."""

    def test_to_dict_keys(self):
        metrics = SyntaxMetrics(
            i3rab_type_accuracy=0.75,
            case_accuracy=0.88,
            coverage=0.92,
            overall_f1=0.76,
            total_words=100,
        )
        d = metrics.to_dict()
        assert "i3rab_type_accuracy" in d
        assert "case_accuracy" in d
        assert "coverage" in d
        assert "overall_f1" in d
        assert "total_words" in d
