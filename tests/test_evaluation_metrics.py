"""
Tests for evaluation metrics.

Author: Hussein Hiyassat
Date: 2026-02-20
Sprint: 3 - Task 3.5
"""

import pytest
from fvafk.c2b.evaluation.metrics import (
    compute_precision,
    compute_recall,
    compute_f1_score,
    compute_accuracy,
    ConfusionMatrix,
)


class TestBasicMetrics:
    """Test basic metric calculations."""
    
    def test_perfect_precision(self):
        """Test precision with no false positives."""
        assert compute_precision(100, 0) == 1.0
    
    def test_perfect_recall(self):
        """Test recall with no false negatives."""
        assert compute_recall(100, 0) == 1.0
    
    def test_precision_with_errors(self):
        """Test precision with some false positives."""
        assert compute_precision(80, 20) == 0.8
    
    def test_recall_with_errors(self):
        """Test recall with some false negatives."""
        assert compute_recall(80, 20) == 0.8
    
    def test_f1_score_balanced(self):
        """Test F1 score when precision equals recall."""
        f1 = compute_f1_score(0.8, 0.8)
        assert abs(f1 - 0.8) < 0.001  # Use tolerance for floating point
    
    def test_f1_score_imbalanced(self):
        """Test F1 score with different precision and recall."""
        f1 = compute_f1_score(0.9, 0.7)
        assert abs(f1 - 0.7875) < 0.001
    
    def test_accuracy(self):
        """Test accuracy calculation."""
        assert compute_accuracy(80, 100) == 0.8
    
    def test_zero_division_handling(self):
        """Test that zero division returns 0.0."""
        assert compute_precision(0, 0) == 0.0
        assert compute_recall(0, 0) == 0.0
        assert compute_f1_score(0.0, 0.0) == 0.0
        assert compute_accuracy(0, 0) == 0.0


class TestConfusionMatrix:
    """Test confusion matrix."""
    
    def test_perfect_predictions(self):
        """Test confusion matrix with all correct predictions."""
        cm = ConfusionMatrix()
        cm.add_prediction('nominative', 'nominative')
        cm.add_prediction('accusative', 'accusative')
        cm.add_prediction('genitive', 'genitive')
        
        assert cm.precision('nominative') == 1.0
        assert cm.recall('nominative') == 1.0
        assert cm.f1_score('nominative') == 1.0
    
    def test_some_errors(self):
        """Test confusion matrix with some errors."""
        cm = ConfusionMatrix()
        # Correct
        cm.add_prediction('nominative', 'nominative')
        cm.add_prediction('nominative', 'nominative')
        # Wrong: predicted nominative, gold is accusative
        cm.add_prediction('nominative', 'accusative')
        # Wrong: predicted accusative, gold is nominative
        cm.add_prediction('accusative', 'nominative')
        
        # Nominative: 2 TP, 1 FP, 1 FN
        assert cm.true_positives['nominative'] == 2
        assert cm.false_positives['nominative'] == 1
        assert cm.false_negatives['nominative'] == 1
        
        # Precision: 2 / (2 + 1) = 0.666...
        assert abs(cm.precision('nominative') - 0.6666) < 0.01
        # Recall: 2 / (2 + 1) = 0.666...
        assert abs(cm.recall('nominative') - 0.6666) < 0.01
    
    def test_macro_averaging(self):
        """Test macro-averaged metrics."""
        cm = ConfusionMatrix()
        # Class A: perfect
        cm.add_prediction('A', 'A')
        cm.add_prediction('A', 'A')
        # Class B: 50% precision, 50% recall
        cm.add_prediction('B', 'B')
        cm.add_prediction('B', 'A')  # FP for B, FN for A
        
        # Macro precision = (1.0 + 0.5) / 2 = 0.75
        assert abs(cm.macro_precision() - 0.75) < 0.01
    
    def test_micro_averaging(self):
        """Test micro-averaged metrics."""
        cm = ConfusionMatrix()
        cm.add_prediction('A', 'A')  # TP
        cm.add_prediction('A', 'A')  # TP
        cm.add_prediction('B', 'A')  # FP for B, FN for A
        cm.add_prediction('A', 'B')  # FP for A, FN for B
        
        # Total TP = 2, FP = 2, FN = 2
        # Micro precision = 2 / (2 + 2) = 0.5
        assert cm.micro_precision() == 0.5
        # Micro recall = 2 / (2 + 2) = 0.5
        assert cm.micro_recall() == 0.5
    
    def test_none_handling(self):
        """Test handling of None values."""
        cm = ConfusionMatrix()
        # Both None - should not affect counts
        cm.add_prediction(None, None)
        # Predicted None, gold is A - FN for A
        cm.add_prediction(None, 'A')
        # Predicted A, gold is None - FP for A
        cm.add_prediction('A', None)
        
        assert cm.true_positives['A'] == 0
        assert cm.false_positives['A'] == 1
        assert cm.false_negatives['A'] == 1
