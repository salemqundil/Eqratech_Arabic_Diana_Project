"""
Tests for MorphologyEvaluator.

Author: Hussein Hiyassat
Date: 2026-02-21
Sprint: 3 - Task 3.5
"""

import pytest
from fvafk.c2b.evaluation import MorphologyEvaluator, EvaluationResult, FeatureMetrics
from fvafk.c2b.corpus import GoldAnnotation, CorpusEntry


class TestMorphologyEvaluator:
    """Test morphology evaluator."""
    
    def test_perfect_predictions(self):
        """Test evaluation with perfect predictions."""
        evaluator = MorphologyEvaluator()
        
        predictions = [
            GoldAnnotation(word="الحمد", case="nominative", pos="noun", number="singular"),
            GoldAnnotation(word="لله", case="genitive", pos="noun", number="singular"),
        ]
        
        gold = [
            GoldAnnotation(word="الحمد", case="nominative", pos="noun", number="singular"),
            GoldAnnotation(word="لله", case="genitive", pos="noun", number="singular"),
        ]
        
        result = evaluator.evaluate(predictions, gold)
        
        assert result.total_words == 2
        assert result.words_evaluated == 2
        assert result.case_metrics.accuracy == 1.0
        assert result.pos_metrics.accuracy == 1.0
        assert result.number_metrics.accuracy == 1.0
        assert result.overall_accuracy() == 1.0
    
    def test_some_errors(self):
        """Test evaluation with some errors."""
        evaluator = MorphologyEvaluator()
        
        predictions = [
            GoldAnnotation(word="الحمد", case="nominative", pos="noun"),
            GoldAnnotation(word="لله", case="accusative", pos="verb"),
        ]
        
        gold = [
            GoldAnnotation(word="الحمد", case="nominative", pos="noun"),
            GoldAnnotation(word="لله", case="genitive", pos="noun"),
        ]
        
        result = evaluator.evaluate(predictions, gold)
        
        assert result.total_words == 2
        assert result.case_metrics.accuracy == 0.5
        assert result.pos_metrics.accuracy == 0.5
    
    def test_mismatched_lengths(self):
        """Test that mismatched lengths raise error."""
        evaluator = MorphologyEvaluator()
        
        predictions = [GoldAnnotation(word="test", case="nominative")]
        gold = [
            GoldAnnotation(word="test", case="nominative"),
            GoldAnnotation(word="test2", case="genitive"),
        ]
        
        with pytest.raises(ValueError, match="same length"):
            evaluator.evaluate(predictions, gold)
    
    def test_none_handling(self):
        """Test handling of None values."""
        evaluator = MorphologyEvaluator()
        
        predictions = [
            GoldAnnotation(word="test", case=None, pos="noun"),
        ]
        
        gold = [
            GoldAnnotation(word="test", case="nominative", pos="noun"),
        ]
        
        result = evaluator.evaluate(predictions, gold)
        
        assert result.case_metrics.accuracy == 0.0
        assert result.pos_metrics.accuracy == 1.0
    
    def test_evaluate_corpus_entries(self):
        """Test evaluating corpus entries."""
        evaluator = MorphologyEvaluator()
        
        pred_entries = [
            CorpusEntry(
                entry_id="test:1",
                annotations=[
                    GoldAnnotation(word="w1", case="nominative"),
                    GoldAnnotation(word="w2", case="accusative"),
                ]
            )
        ]
        
        gold_entries = [
            CorpusEntry(
                entry_id="test:1",
                annotations=[
                    GoldAnnotation(word="w1", case="nominative"),
                    GoldAnnotation(word="w2", case="genitive"),
                ]
            )
        ]
        
        result = evaluator.evaluate_corpus_entries(pred_entries, gold_entries)
        
        assert result.total_words == 2
        assert result.case_metrics.accuracy == 0.5


class TestFeatureMetrics:
    """Test FeatureMetrics class."""
    
    def test_initialization(self):
        """Test FeatureMetrics initialization."""
        metrics = FeatureMetrics("test_feature")
        assert metrics.feature_name == "test_feature"
        assert metrics.accuracy == 0.0
        assert metrics.total_predictions == 0
        assert metrics.correct_predictions == 0
    
    def test_compute_accuracy(self):
        """Test accuracy computation."""
        metrics = FeatureMetrics("test")
        metrics.total_predictions = 10
        metrics.correct_predictions = 7
        metrics.compute_accuracy()
        assert metrics.accuracy == 0.7
