"""
Integration tests for morphology evaluation.

Author: Hussein Hiyassat
Date: 2026-02-21
Sprint: 3 - Task 3.7
"""

import pytest
from pathlib import Path
from fvafk.c2b.evaluation import I3rabLoader, MorphologyEvaluator, FeatureMetrics, ConfusionMatrix
from fvafk.c2b.corpus import GoldAnnotation, CorpusEntry


class TestI3rabIntegration:
    """Integration tests using I3rab corpus."""
    
    @pytest.fixture
    def csv_path(self):
        """Path to I3rab CSV."""
        return Path("data/i3rab/quran_i3rab.csv")
    
    @pytest.fixture
    def loader(self, csv_path):
        """I3rab loader instance."""
        if not csv_path.exists():
            pytest.skip("I3rab CSV not found")
        return I3rabLoader(csv_path)
    
    def test_load_fatiha(self, loader):
        """Test loading Al-Fatiha."""
        entries = loader.load_surah(1)
        
        assert len(entries) == 7
        assert all(isinstance(e, CorpusEntry) for e in entries)
        
        # Check first ayah (Bismillah)
        first = entries[0]
        assert first.entry_id == "quran:1:1"
        assert len(first.annotations) == 4
    
    def test_parser_extracts_case(self, loader):
        """Test that parser extracts case information."""
        # 1:2 - الْحَمْدُ (nominative)
        entry = loader.load_ayah(1, 2)
        
        # First word should be nominative
        assert entry.annotations[0].case == "nominative"
    
    def test_parser_extracts_pos(self, loader):
        """Test that parser extracts POS information."""
        # 1:1 - All words should be nouns or particles
        entry = loader.load_ayah(1, 1)
        
        for ann in entry.annotations:
            assert ann.pos in ["noun", "particle", None]
    
    def test_evaluation_with_perfect_predictions(self, loader):
        """Test evaluation with perfect predictions."""
        # Load gold standard
        gold_entry = loader.load_ayah(1, 1)
        
        # Create perfect predictions (copy gold)
        pred_entry = CorpusEntry(
            entry_id="quran:1:1",
            annotations=[
                GoldAnnotation(
                    word=ann.word,
                    case=ann.case,
                    pos=ann.pos,
                    number=ann.number,
                    gender=ann.gender,
                )
                for ann in gold_entry.annotations
            ]
        )
        
        # Evaluate
        evaluator = MorphologyEvaluator()
        result = evaluator.evaluate_corpus_entries([pred_entry], [gold_entry])
        
        # Should have perfect accuracy
        assert result.case_metrics.accuracy == 1.0
        assert result.pos_metrics.accuracy == 1.0
    
    def test_evaluation_with_errors(self, loader):
        """Test evaluation with some errors."""
        # Load gold standard
        gold_entry = loader.load_ayah(1, 1)
        
        # Create predictions with errors
        pred_entry = CorpusEntry(
            entry_id="quran:1:1",
            annotations=[
                GoldAnnotation(
                    word=ann.word,
                    case="nominative" if i == 0 else ann.case,  # Wrong case for first word
                    pos=ann.pos,
                    number=ann.number,
                    gender=ann.gender,
                )
                for i, ann in enumerate(gold_entry.annotations)
            ]
        )
        
        # Evaluate
        evaluator = MorphologyEvaluator()
        result = evaluator.evaluate_corpus_entries([pred_entry], [gold_entry])
        
        # Should have less than perfect accuracy
        assert result.case_metrics.accuracy < 1.0
    
    def test_corpus_statistics(self, loader):
        """Test corpus statistics."""
        entries = loader.load_surah(1)
        
        total_words = sum(len(e.annotations) for e in entries)
        
        # Al-Fatiha has 29 words
        assert total_words == 29
        
        # Count case distribution
        cases = {}
        for entry in entries:
            for ann in entry.annotations:
                if ann.case:
                    cases[ann.case] = cases.get(ann.case, 0) + 1
        
        # Should have nominative, genitive, etc.
        assert "nominative" in cases
        assert "genitive" in cases
        
        print(f"\nCase distribution in Al-Fatiha:")
        for case, count in sorted(cases.items()):
            print(f"  {case}: {count}")


class TestEvaluationReport:
    """Test evaluation report generation."""
    
    def test_feature_metrics_structure(self):
        """Test FeatureMetrics structure."""
        cm = ConfusionMatrix()
        cm.add_prediction("nominative", "nominative")
        cm.add_prediction("genitive", "genitive")
        cm.add_prediction("accusative", "nominative")  # Error
        
        metrics = FeatureMetrics(
            feature_name="case",
            confusion_matrix=cm,
            total_predictions=3,
            correct_predictions=2,
        )
        metrics.compute_accuracy()
        
        assert metrics.feature_name == "case"
        assert metrics.accuracy == pytest.approx(2/3, rel=0.01)
        assert metrics.total_predictions == 3
        assert metrics.correct_predictions == 2
        
        # Check dict conversion
        metrics_dict = metrics.to_dict()
        assert "feature" in metrics_dict
        assert "accuracy" in metrics_dict
        assert metrics_dict["feature"] == "case"
    
    def test_evaluation_result_summary(self):
        """Test EvaluationResult summary."""
        from fvafk.c2b.evaluation import EvaluationResult
        
        # Create metrics with some data
        case_cm = ConfusionMatrix()
        case_cm.add_prediction("nominative", "nominative")
        case_cm.add_prediction("genitive", "genitive")
        
        case_metrics = FeatureMetrics(
            feature_name="case",
            confusion_matrix=case_cm,
            total_predictions=2,
            correct_predictions=2,
        )
        case_metrics.compute_accuracy()
        
        pos_cm = ConfusionMatrix()
        pos_cm.add_prediction("noun", "noun")
        pos_cm.add_prediction("verb", "verb")
        
        pos_metrics = FeatureMetrics(
            feature_name="pos",
            confusion_matrix=pos_cm,
            total_predictions=2,
            correct_predictions=2,
        )
        pos_metrics.compute_accuracy()
        
        result = EvaluationResult(
            case_metrics=case_metrics,
            pos_metrics=pos_metrics,
        )
        
        # Generate summary
        summary = result.summary()
        
        assert "features" in summary
        assert "case" in summary["features"]
        assert "pos" in summary["features"]
        
        assert summary["features"]["case"]["accuracy"] == 1.0
        assert summary["features"]["pos"]["accuracy"] == 1.0
