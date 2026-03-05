"""
Integration Tests for Syntax Layer (Sprint 4 - Task 4.5).

Tests the end-to-end pipeline using real Quranic examples
from the I3rab corpus.

Author: Hussein Hiyassat
Date: 2026-02-21
Sprint: 4
"""

import pytest
from pathlib import Path
from fvafk.c2b.syntax import (
    I3rabParser,
    I3rabComponents,
    SyntaxFeatures,
    SyntaxEvaluator,
    SyntaxMetrics,
    MorphSyntaxBridge,
    I3RAB_TYPE_MAPPING,
)
from fvafk.c2b.morphology_flags import MorphologyFlags, MorphologyFlagsExtractor


# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------

I3RAB_CSV = Path(__file__).parent.parent / "data" / "i3rab" / "quran_i3rab.csv"


def _load_ayah_rows(surah: int, ayah: int):
    """Load raw rows for a given surah:ayah from the CSV."""
    import csv
    rows = []
    with open(I3RAB_CSV, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Handle BOM and alternate column names
            surah_val = row.get("surah") or row.get("\ufeffsurah", "")
            if int(surah_val) == surah and int(row["ayah"]) == ayah:
                rows.append(row)
    return rows


# -------------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------------


class TestParserOnRealCorpus:
    """Integration: run I3rabParser on real Quranic rows."""

    def setup_method(self):
        self.parser = I3rabParser()

    @pytest.mark.skipif(not I3RAB_CSV.exists(), reason="I3rab CSV not available")
    def test_al_fatiha_ayah_1_parse_count(self):
        """Al-Fatiha 1:1 (Basmala) has 4 words; all should parse without crashing."""
        rows = _load_ayah_rows(1, 1)
        assert len(rows) == 4
        for row in rows:
            comp = self.parser.parse(row["i3rab"])
            assert comp.raw_text == row["i3rab"]

    @pytest.mark.skipif(not I3RAB_CSV.exists(), reason="I3rab CSV not available")
    def test_al_fatiha_ayah_2_types(self):
        """Al-Fatiha 1:2 - الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ."""
        rows = _load_ayah_rows(1, 2)
        assert len(rows) >= 2
        parsed = [self.parser.parse(row["i3rab"]) for row in rows]
        # At least one word should have a detected I3rab type
        detected = [p for p in parsed if p.i3rab_type is not None]
        assert len(detected) >= 1

    @pytest.mark.skipif(not I3RAB_CSV.exists(), reason="I3rab CSV not available")
    def test_genitive_case_in_basmala(self):
        """First word of Basmala is genitive (بِسْمِ)."""
        rows = _load_ayah_rows(1, 1)
        first = self.parser.parse(rows[0]["i3rab"])
        assert first.case == "genitive"

    @pytest.mark.skipif(not I3RAB_CSV.exists(), reason="I3rab CSV not available")
    def test_parser_coverage_on_fatiha(self):
        """At least 60% of Al-Fatiha words should get an I3rab type."""
        all_rows = []
        for ayah in range(1, 8):
            all_rows.extend(_load_ayah_rows(1, ayah))
        parsed = [self.parser.parse(row["i3rab"]) for row in all_rows]
        typed = [p for p in parsed if p.i3rab_type is not None]
        coverage = len(typed) / len(parsed) if parsed else 0.0
        assert coverage >= 0.60, f"Coverage only {coverage:.1%}"


class TestEvaluatorOnRealCorpus:
    """Integration: end-to-end evaluator on real I3rab data."""

    def setup_method(self):
        self.parser = I3rabParser()
        self.evaluator = SyntaxEvaluator()
        self.extractor = MorphologyFlagsExtractor()
        self.bridge = MorphSyntaxBridge()

    @pytest.mark.skipif(not I3RAB_CSV.exists(), reason="I3rab CSV not available")
    def test_evaluate_fatiha_case_accuracy(self):
        """Case accuracy on Al-Fatiha should be reasonable."""
        all_rows = []
        for ayah in range(1, 8):
            all_rows.extend(_load_ayah_rows(1, ayah))

        gold_components = [self.parser.parse(row["i3rab"]) for row in all_rows]

        # Build predictions via morph→syntax bridge
        preds = []
        for i, row in enumerate(all_rows):
            morph = self.extractor.extract(row["word"])
            feat = self.bridge.predict_syntax(morph, [], i)
            preds.append(feat)

        metrics = self.evaluator.evaluate(preds, gold_components)
        # Basic sanity: coverage > 0
        assert metrics.total_words > 0

    @pytest.mark.skipif(not I3RAB_CSV.exists(), reason="I3rab CSV not available")
    def test_evaluate_returns_syntax_metrics(self):
        """evaluate() must always return a SyntaxMetrics object."""
        rows = _load_ayah_rows(1, 1)
        gold = [self.parser.parse(r["i3rab"]) for r in rows]
        preds = []
        for i, row in enumerate(rows):
            morph = self.extractor.extract(row["word"])
            preds.append(self.bridge.predict_syntax(morph, [], i))
        metrics = self.evaluator.evaluate(preds, gold)
        assert isinstance(metrics, SyntaxMetrics)


class TestPipelineSmoke:
    """Smoke tests that don't require the CSV to be present."""

    def test_parser_harf_text(self):
        parser = I3rabParser()
        comp = parser.parse("حَرْفُ جَرٍّ مَبْنِيٌّ عَلَى الْكَسْرِ")
        assert comp.i3rab_type == "حرف"

    def test_evaluator_perfect_pair(self):
        evaluator = SyntaxEvaluator()
        gold = [I3rabComponents(i3rab_type="مبتدأ", case="nominative", confidence=1.0)]
        pred = [SyntaxFeatures(
            syntactic_role="subject",
            case="nominative",
            i3rab_type_ar="مبتدأ",
            i3rab_type_en="mubtada",
            confidence=0.9,
        )]
        metrics = evaluator.evaluate(pred, gold)
        assert metrics.i3rab_type_accuracy == 1.0
        assert metrics.case_accuracy == 1.0

    def test_all_top5_types_parseable(self):
        """Each Top-5 type string should be detectable in a simple sentence."""
        parser = I3rabParser()
        test_cases = [
            ("مُبْتَدَأٌ مَرْفُوعٌ", "مبتدأ"),
            ("خَبَرٌ مَرْفُوعٌ", "خبر"),
            ("فَاعِلٌ مَرْفُوعٌ", "فاعل"),
            ("مَفْعُولٌ بِهِ مَنْصُوبٌ", "مفعول به"),
            ("حَرْفُ جَرٍّ", "حرف"),
        ]
        for text, expected_type in test_cases:
            comp = parser.parse(text)
            assert comp.i3rab_type == expected_type, (
                f"Expected '{expected_type}' for '{text}', got '{comp.i3rab_type}'"
            )

    def test_bridge_subject_prediction(self):
        bridge = MorphSyntaxBridge()
        morph = MorphologyFlags(case="nominative", definiteness=True, confidence=0.9)
        result = bridge.predict_syntax(morph, [], 0)
        assert result.syntactic_role == "subject"
        assert result.i3rab_type_en == "mubtada"

    def test_i3rab_type_mapping_covers_top5(self):
        for ar in ["مبتدأ", "خبر", "فاعل", "مفعول به", "حرف"]:
            assert ar in I3RAB_TYPE_MAPPING, f"'{ar}' not in I3RAB_TYPE_MAPPING"

    def test_evaluator_empty_lists(self):
        evaluator = SyntaxEvaluator()
        metrics = evaluator.evaluate([], [])
        assert metrics.total_words == 0

    def test_evaluator_mismatched_raises(self):
        evaluator = SyntaxEvaluator()
        gold = [I3rabComponents(i3rab_type="مبتدأ", case="nominative")]
        with pytest.raises(ValueError):
            evaluator.evaluate([], gold)
