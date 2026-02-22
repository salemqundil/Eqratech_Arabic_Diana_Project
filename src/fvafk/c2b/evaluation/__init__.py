"""Evaluation package - metrics and corpus loaders."""

from .metrics import (
    compute_precision,
    compute_recall,
    compute_f1_score,
    compute_accuracy,
    ConfusionMatrix,
)

from .evaluator import (
    FeatureMetrics,
    EvaluationResult,
    MorphologyEvaluator,
)

from .i3rab_loader import (
    I3rabParser,
    I3rabParseResult,
    I3rabLoader,
)

__all__ = [
    "compute_precision",
    "compute_recall",
    "compute_f1_score",
    "compute_accuracy",
    "ConfusionMatrix",
    "FeatureMetrics",
    "EvaluationResult",
    "MorphologyEvaluator",
    "I3rabParser",
    "I3rabParseResult",
    "I3rabLoader",
]
