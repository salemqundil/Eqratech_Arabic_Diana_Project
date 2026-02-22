"""Morphology Evaluator - Compare system predictions vs gold standard."""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from ..corpus.corpus_format import GoldAnnotation, CorpusEntry
from .metrics import ConfusionMatrix, compute_accuracy

@dataclass
class FeatureMetrics:
    feature_name: str
    confusion_matrix: ConfusionMatrix = field(default_factory=ConfusionMatrix)
    accuracy: float = 0.0
    total_predictions: int = 0
    correct_predictions: int = 0
    
    def compute_accuracy(self):
        self.accuracy = compute_accuracy(self.correct_predictions, self.total_predictions)
    
    def to_dict(self) -> Dict[str, Any]:
        cm_summary = self.confusion_matrix.summary()
        return {
            "feature": self.feature_name,
            "accuracy": self.accuracy,
            "total": self.total_predictions,
            "correct": self.correct_predictions,
            "macro_precision": cm_summary["macro_precision"],
            "macro_recall": cm_summary["macro_recall"],
            "macro_f1": cm_summary["macro_f1"],
            "micro_precision": cm_summary["micro_precision"],
            "micro_recall": cm_summary["micro_recall"],
            "micro_f1": cm_summary["micro_f1"],
            "per_class": cm_summary["per_class"],
        }

@dataclass
class EvaluationResult:
    case_metrics: FeatureMetrics = field(default_factory=lambda: FeatureMetrics("case"))
    number_metrics: FeatureMetrics = field(default_factory=lambda: FeatureMetrics("number"))
    gender_metrics: FeatureMetrics = field(default_factory=lambda: FeatureMetrics("gender"))
    definiteness_metrics: FeatureMetrics = field(default_factory=lambda: FeatureMetrics("definiteness"))
    pos_metrics: FeatureMetrics = field(default_factory=lambda: FeatureMetrics("pos"))
    root_metrics: FeatureMetrics = field(default_factory=lambda: FeatureMetrics("root"))
    pattern_metrics: FeatureMetrics = field(default_factory=lambda: FeatureMetrics("pattern"))
    total_words: int = 0
    words_evaluated: int = 0
    
    def overall_accuracy(self) -> float:
        all_metrics = [self.case_metrics, self.number_metrics, self.gender_metrics, self.definiteness_metrics, self.pos_metrics, self.root_metrics, self.pattern_metrics]
        total_correct = sum(m.correct_predictions for m in all_metrics)
        total_predictions = sum(m.total_predictions for m in all_metrics)
        return compute_accuracy(total_correct, total_predictions)
    
    def summary(self) -> Dict[str, Any]:
        return {
            "overall_accuracy": self.overall_accuracy(),
            "total_words": self.total_words,
            "words_evaluated": self.words_evaluated,
            "features": {
                "case": self.case_metrics.to_dict(),
                "number": self.number_metrics.to_dict(),
                "gender": self.gender_metrics.to_dict(),
                "definiteness": self.definiteness_metrics.to_dict(),
                "pos": self.pos_metrics.to_dict(),
                "root": self.root_metrics.to_dict(),
                "pattern": self.pattern_metrics.to_dict(),
            }
        }

class MorphologyEvaluator:
    def evaluate(self, predictions: List[GoldAnnotation], gold_standard: List[GoldAnnotation]) -> EvaluationResult:
        if len(predictions) != len(gold_standard):
            raise ValueError("Prediction and gold lists must have same length")
        result = EvaluationResult()
        result.total_words = len(predictions)
        result.words_evaluated = len(predictions)
        for pred, gold in zip(predictions, gold_standard):
            self._evaluate_word(pred, gold, result)
        result.case_metrics.compute_accuracy()
        result.number_metrics.compute_accuracy()
        result.gender_metrics.compute_accuracy()
        result.definiteness_metrics.compute_accuracy()
        result.pos_metrics.compute_accuracy()
        result.root_metrics.compute_accuracy()
        result.pattern_metrics.compute_accuracy()
        return result
    
    def _evaluate_word(self, pred: GoldAnnotation, gold: GoldAnnotation, result: EvaluationResult):
        self._evaluate_feature(pred.case, gold.case, result.case_metrics)
        self._evaluate_feature(pred.number, gold.number, result.number_metrics)
        self._evaluate_feature(pred.gender, gold.gender, result.gender_metrics)
        pred_def = str(pred.definiteness) if pred.definiteness is not None else None
        gold_def = str(gold.definiteness) if gold.definiteness is not None else None
        self._evaluate_feature(pred_def, gold_def, result.definiteness_metrics)
        self._evaluate_feature(pred.pos, gold.pos, result.pos_metrics)
        self._evaluate_feature(pred.root, gold.root, result.root_metrics)
        self._evaluate_feature(pred.pattern, gold.pattern, result.pattern_metrics)
    
    def _evaluate_feature(self, predicted: Optional[str], gold: Optional[str], metrics: FeatureMetrics):
        metrics.confusion_matrix.add_prediction(predicted, gold)
        metrics.total_predictions += 1
        if predicted == gold:
            metrics.correct_predictions += 1
    
    def evaluate_corpus_entries(self, pred_entries: List[CorpusEntry], gold_entries: List[CorpusEntry]) -> EvaluationResult:
        gold_index = {entry.entry_id: entry for entry in gold_entries}
        all_predictions = []
        all_gold = []
        for pred_entry in pred_entries:
            if pred_entry.entry_id not in gold_index:
                continue
            gold_entry = gold_index[pred_entry.entry_id]
            for i, pred_ann in enumerate(pred_entry.annotations):
                if i < len(gold_entry.annotations):
                    all_predictions.append(pred_ann)
                    all_gold.append(gold_entry.annotations[i])
        return self.evaluate(all_predictions, all_gold)
