"""
Tests for Syntax Data Models (Sprint 4 - Task 4.2).

Author: Hussein Hiyassat
Date: 2026-02-21
Sprint: 4
"""

import pytest
from fvafk.c2b.syntax import (
    I3rabAnnotation,
    I3rabComponents,
    SyntaxFeatures,
    I3RAB_TYPE_MAPPING,
    CASE_MAPPING,
    TOP5_I3RAB_TYPES,
)


class TestI3rabAnnotation:
    """Test I3rabAnnotation dataclass."""

    def test_create_annotation(self):
        ann = I3rabAnnotation(
            word="الْحَمْدُ",
            i3rab_text="مُبْتَدَأٌ مَرْفُوعٌ",
            surah=1,
            ayah=2,
            word_index=0,
        )
        assert ann.word == "الْحَمْدُ"
        assert ann.surah == 1
        assert ann.ayah == 2
        assert ann.word_index == 0

    def test_annotation_fields(self):
        ann = I3rabAnnotation(
            word="لِلَّهِ",
            i3rab_text="مَجْرُورٌ",
            surah=1,
            ayah=2,
            word_index=1,
        )
        assert ann.i3rab_text == "مَجْرُورٌ"


class TestI3rabComponents:
    """Test I3rabComponents dataclass."""

    def test_default_values(self):
        comp = I3rabComponents()
        assert comp.i3rab_type is None
        assert comp.case is None
        assert comp.confidence == 0.0
        assert comp.raw_text == ""

    def test_full_construction(self):
        comp = I3rabComponents(
            i3rab_type="مبتدأ",
            i3rab_type_en="mubtada",
            case="nominative",
            case_marker="الضمة",
            mahall=None,
            confidence=0.9,
            raw_text="مُبْتَدَأٌ مَرْفُوعٌ",
        )
        assert comp.i3rab_type == "مبتدأ"
        assert comp.i3rab_type_en == "mubtada"
        assert comp.case == "nominative"
        assert comp.case_marker == "الضمة"
        assert comp.confidence == 0.9

    def test_all_top5_types_have_english_mapping(self):
        """Every Top-5 Arabic type must have an English mapping."""
        for ar_type in TOP5_I3RAB_TYPES:
            assert ar_type in I3RAB_TYPE_MAPPING, (
                f"'{ar_type}' missing from I3RAB_TYPE_MAPPING"
            )


class TestSyntaxFeatures:
    """Test SyntaxFeatures dataclass."""

    def test_create_features(self):
        feat = SyntaxFeatures(
            syntactic_role="subject",
            case="nominative",
            i3rab_type_ar="مبتدأ",
            i3rab_type_en="mubtada",
            confidence=0.85,
        )
        assert feat.syntactic_role == "subject"
        assert feat.case == "nominative"
        assert feat.warning is None  # high confidence → no warning

    def test_low_confidence_auto_warning(self):
        feat = SyntaxFeatures(
            syntactic_role="unknown",
            case="unknown",
            i3rab_type_ar="غير معروف",
            i3rab_type_en="unknown",
            confidence=0.3,
        )
        assert feat.warning is not None
        assert "Low confidence" in feat.warning

    def test_explicit_warning_not_overwritten(self):
        feat = SyntaxFeatures(
            syntactic_role="subject",
            case="nominative",
            i3rab_type_ar="مبتدأ",
            i3rab_type_en="mubtada",
            confidence=0.3,
            warning="Custom warning",
        )
        assert feat.warning == "Custom warning"


class TestMappings:
    """Test mapping dictionaries."""

    def test_i3rab_type_mapping_completeness(self):
        """All top-5 types are in the mapping."""
        for ar in ["مبتدأ", "خبر", "فاعل", "مفعول به", "حرف"]:
            assert ar in I3RAB_TYPE_MAPPING

    def test_case_mapping(self):
        assert CASE_MAPPING["مرفوع"] == "nominative"
        assert CASE_MAPPING["منصوب"] == "accusative"
        assert CASE_MAPPING["مجرور"] == "genitive"

    def test_top5_set_contents(self):
        assert TOP5_I3RAB_TYPES == {"مبتدأ", "خبر", "فاعل", "مفعول به", "حرف"}
