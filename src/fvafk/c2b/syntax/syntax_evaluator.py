"""
Syntax Evaluator - Metrics for I3rab type, case, and overall accuracy.

Author: Hussein Hiyassat
Date: 2026-02-21
Sprint: 4 - Task 4.4
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..evaluation.metrics import (
    ConfusionMatrix,
    compute_accuracy,
    compute_f1_score,
)
from .i3rab_components import I3rabComponents
from .syntax_features import SyntaxFeatures


@dataclass
class SyntaxMetrics:
    """
    Aggregated metrics for syntax evaluation.

    Attributes:
        i3rab_type_accuracy: Fraction of words with correct I3rab type.
        case_accuracy: Fraction of words with correct case.
        coverage: Fraction of words for which a prediction was made.
        overall_f1: Macro F1 across I3rab-type labels.
        per_class_precision: Precision per I3rab type.
        per_class_recall: Recall per I3rab type.
        i3rab_confusion_matrix: Full confusion matrix for I3rab types.
        case_confusion_matrix: Full confusion matrix for cases.
        total_words: Total number of word pairs evaluated.

    Examples:
        >>> m = SyntaxMetrics(
        ...     i3rab_type_accuracy=0.75,
        ...     case_accuracy=0.88,
        ...     coverage=0.92,
        ...     overall_f1=0.76,
        ... )
        >>> m.i3rab_type_accuracy
        0.75
    """

    i3rab_type_accuracy: float = 0.0
    case_accuracy: float = 0.0
    coverage: float = 0.0
    overall_f1: float = 0.0
    per_class_precision: Dict[str, float] = field(default_factory=dict)
    per_class_recall: Dict[str, float] = field(default_factory=dict)
    i3rab_confusion_matrix: ConfusionMatrix = field(
        default_factory=ConfusionMatrix
    )
    case_confusion_matrix: ConfusionMatrix = field(
        default_factory=ConfusionMatrix
    )
    total_words: int = 0

    def to_dict(self) -> Dict:
        """Return a JSON-serialisable summary."""
        return {
            "i3rab_type_accuracy": self.i3rab_type_accuracy,
            "case_accuracy": self.case_accuracy,
            "coverage": self.coverage,
            "overall_f1": self.overall_f1,
            "total_words": self.total_words,
            "per_class_precision": self.per_class_precision,
            "per_class_recall": self.per_class_recall,
        }

    def meets_targets(self) -> bool:
        """Return True when all Sprint-4 target metrics are met."""
        return (
            self.i3rab_type_accuracy >= 0.70
            and self.case_accuracy >= 0.85
            and self.coverage >= 0.90
            and self.overall_f1 >= 0.75
        )


class SyntaxEvaluator:
    """
    Evaluate syntax predictions against gold-standard I3rab annotations.

    The evaluator compares:
    - I3rab type (Arabic label) from predictions vs gold
    - Case from predictions vs gold

    Examples:
        >>> evaluator = SyntaxEvaluator()
        >>> from fvafk.c2b.syntax.i3rab_components import I3rabComponents
        >>> from fvafk.c2b.syntax.syntax_features import SyntaxFeatures
        >>> gold = [I3rabComponents(i3rab_type="مبتدأ", case="nominative", confidence=1.0)]
        >>> preds = [SyntaxFeatures(
        ...     syntactic_role="subject", case="nominative",
        ...     i3rab_type_ar="مبتدأ", i3rab_type_en="mubtada", confidence=0.8
        ... )]
        >>> metrics = evaluator.evaluate(preds, gold)
        >>> metrics.i3rab_type_accuracy
        1.0
    """

    def evaluate(
        self,
        predictions: List[SyntaxFeatures],
        gold: List[I3rabComponents],
    ) -> SyntaxMetrics:
        """
        Evaluate syntax predictions against gold standard.

        Args:
            predictions: List of SyntaxFeatures produced by the system.
            gold: List of I3rabComponents from the corpus.

        Returns:
            SyntaxMetrics with all evaluation scores.

        Raises:
            ValueError: If predictions and gold lists have different lengths.
        """
        if len(predictions) != len(gold):
            raise ValueError(
                f"Predictions ({len(predictions)}) and gold ({len(gold)}) "
                "must have the same length."
            )

        metrics = SyntaxMetrics(total_words=len(predictions))
        i3rab_cm = ConfusionMatrix()
        case_cm = ConfusionMatrix()

        i3rab_correct = 0
        case_correct = 0
        covered = 0

        for pred, g in zip(predictions, gold):
            # Coverage: prediction made (non-unknown i3rab type)
            if pred.i3rab_type_en != "unknown":
                covered += 1

            # I3rab type comparison (use Arabic label)
            pred_type = pred.i3rab_type_ar
            gold_type = g.i3rab_type
            i3rab_cm.add_prediction(pred_type, gold_type)
            if pred_type == gold_type:
                i3rab_correct += 1

            # Case comparison
            pred_case = pred.case if pred.case != "unknown" else None
            gold_case = g.case
            case_cm.add_prediction(pred_case, gold_case)
            if pred_case == gold_case:
                case_correct += 1

        n = len(predictions)
        metrics.i3rab_type_accuracy = compute_accuracy(i3rab_correct, n)
        metrics.case_accuracy = compute_accuracy(case_correct, n)
        metrics.coverage = compute_accuracy(covered, n)

        # Overall F1: macro-F1 over I3rab types
        metrics.overall_f1 = i3rab_cm.macro_f1_score()

        # Per-class metrics
        cm_summary = i3rab_cm.summary()
        metrics.per_class_precision = {
            cls: info["precision"]
            for cls, info in cm_summary.get("per_class", {}).items()
        }
        metrics.per_class_recall = {
            cls: info["recall"]
            for cls, info in cm_summary.get("per_class", {}).items()
        }

        metrics.i3rab_confusion_matrix = i3rab_cm
        metrics.case_confusion_matrix = case_cm

        return metrics
