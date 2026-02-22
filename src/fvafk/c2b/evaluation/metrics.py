"""
Core evaluation metrics.

Provides functions to compute:
- Precision: TP / (TP + FP)
- Recall: TP / (TP + FN)
- F1 Score: 2 * (Precision * Recall) / (Precision + Recall)
- Accuracy: (TP + TN) / Total

Author: Hussein Hiyassat
Date: 2026-02-20
Sprint: 3 - Task 3.5
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from collections import defaultdict


def compute_precision(true_positives: int, false_positives: int) -> float:
    """
    Compute precision.
    
    Precision = TP / (TP + FP)
    
    Args:
        true_positives: Number of correct positive predictions
        false_positives: Number of incorrect positive predictions
        
    Returns:
        Precision score (0.0 to 1.0)
        
    Examples:
        >>> compute_precision(80, 20)
        0.8
        >>> compute_precision(0, 0)
        0.0
    """
    denominator = true_positives + false_positives
    if denominator == 0:
        return 0.0
    return true_positives / denominator


def compute_recall(true_positives: int, false_negatives: int) -> float:
    """
    Compute recall.
    
    Recall = TP / (TP + FN)
    
    Args:
        true_positives: Number of correct positive predictions
        false_negatives: Number of missed positive cases
        
    Returns:
        Recall score (0.0 to 1.0)
        
    Examples:
        >>> compute_recall(80, 20)
        0.8
        >>> compute_recall(0, 0)
        0.0
    """
    denominator = true_positives + false_negatives
    if denominator == 0:
        return 0.0
    return true_positives / denominator


def compute_f1_score(precision: float, recall: float) -> float:
    """
    Compute F1 score (harmonic mean of precision and recall).
    
    F1 = 2 * (Precision * Recall) / (Precision + Recall)
    
    Args:
        precision: Precision score
        recall: Recall score
        
    Returns:
        F1 score (0.0 to 1.0)
        
    Examples:
        >>> compute_f1_score(0.8, 0.8)
        0.8
        >>> compute_f1_score(0.9, 0.7)
        0.7875
        >>> compute_f1_score(0.0, 0.0)
        0.0
    """
    if precision + recall == 0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)


def compute_accuracy(correct: int, total: int) -> float:
    """
    Compute accuracy.
    
    Accuracy = Correct / Total
    
    Args:
        correct: Number of correct predictions
        total: Total number of predictions
        
    Returns:
        Accuracy score (0.0 to 1.0)
        
    Examples:
        >>> compute_accuracy(80, 100)
        0.8
        >>> compute_accuracy(0, 0)
        0.0
    """
    if total == 0:
        return 0.0
    return correct / total


@dataclass
class ConfusionMatrix:
    """
    Confusion matrix for a single feature.
    
    Tracks predictions vs gold standard for a categorical feature
    (e.g., case: nominative/accusative/genitive).
    
    Attributes:
        true_positives: Correct predictions per class
        false_positives: Incorrect predictions per class
        false_negatives: Missed predictions per class
        
    Examples:
        >>> cm = ConfusionMatrix()
        >>> cm.add_prediction('nominative', 'nominative')  # Correct
        >>> cm.add_prediction('nominative', 'accusative')  # Wrong
        >>> cm.precision('nominative')
        0.5
    """
    
    # Class -> count
    true_positives: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    false_positives: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    false_negatives: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    def add_prediction(self, predicted: Optional[str], gold: Optional[str]):
        """
        Add a prediction to the confusion matrix.
        
        Args:
            predicted: System's prediction (or None)
            gold: Gold standard label (or None)
        """
        if predicted is None and gold is None:
            # Both None - true negative (not tracked per class)
            return
        
        if predicted == gold:
            # Correct prediction
            if predicted is not None:
                self.true_positives[predicted] += 1
        else:
            # Incorrect prediction
            if predicted is not None:
                self.false_positives[predicted] += 1
            if gold is not None:
                self.false_negatives[gold] += 1
    
    def precision(self, class_label: str) -> float:
        """Compute precision for a specific class."""
        tp = self.true_positives[class_label]
        fp = self.false_positives[class_label]
        return compute_precision(tp, fp)
    
    def recall(self, class_label: str) -> float:
        """Compute recall for a specific class."""
        tp = self.true_positives[class_label]
        fn = self.false_negatives[class_label]
        return compute_recall(tp, fn)
    
    def f1_score(self, class_label: str) -> float:
        """Compute F1 score for a specific class."""
        p = self.precision(class_label)
        r = self.recall(class_label)
        return compute_f1_score(p, r)
    
    def macro_precision(self) -> float:
        """Compute macro-averaged precision (average across all classes)."""
        classes = set(list(self.true_positives.keys()) + 
                     list(self.false_positives.keys()) + 
                     list(self.false_negatives.keys()))
        if not classes:
            return 0.0
        return sum(self.precision(c) for c in classes) / len(classes)
    
    def macro_recall(self) -> float:
        """Compute macro-averaged recall."""
        classes = set(list(self.true_positives.keys()) + 
                     list(self.false_positives.keys()) + 
                     list(self.false_negatives.keys()))
        if not classes:
            return 0.0
        return sum(self.recall(c) for c in classes) / len(classes)
    
    def macro_f1_score(self) -> float:
        """Compute macro-averaged F1 score."""
        p = self.macro_precision()
        r = self.macro_recall()
        return compute_f1_score(p, r)
    
    def micro_precision(self) -> float:
        """Compute micro-averaged precision (total TP / total predictions)."""
        total_tp = sum(self.true_positives.values())
        total_fp = sum(self.false_positives.values())
        return compute_precision(total_tp, total_fp)
    
    def micro_recall(self) -> float:
        """Compute micro-averaged recall."""
        total_tp = sum(self.true_positives.values())
        total_fn = sum(self.false_negatives.values())
        return compute_recall(total_tp, total_fn)
    
    def micro_f1_score(self) -> float:
        """Compute micro-averaged F1 score."""
        p = self.micro_precision()
        r = self.micro_recall()
        return compute_f1_score(p, r)
    
    def summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        return {
            'macro_precision': self.macro_precision(),
            'macro_recall': self.macro_recall(),
            'macro_f1': self.macro_f1_score(),
            'micro_precision': self.micro_precision(),
            'micro_recall': self.micro_recall(),
            'micro_f1': self.micro_f1_score(),
            'per_class': {
                cls: {
                    'precision': self.precision(cls),
                    'recall': self.recall(cls),
                    'f1': self.f1_score(cls),
                    'tp': self.true_positives[cls],
                    'fp': self.false_positives[cls],
                    'fn': self.false_negatives[cls],
                }
                for cls in set(list(self.true_positives.keys()) + 
                              list(self.false_positives.keys()) + 
                              list(self.false_negatives.keys()))
            }
        }
