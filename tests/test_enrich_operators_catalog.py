"""
tests/test_enrich_operators_catalog.py
=======================================
Unit tests for scripts/enrich_operators_catalog.py.
"""

import sys
import os
import importlib.util

import pytest

# ---------------------------------------------------------------------------
# Import the script module without executing main()
# ---------------------------------------------------------------------------
_SCRIPT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "scripts", "enrich_operators_catalog.py"
)

spec = importlib.util.spec_from_file_location("enrich_operators_catalog", _SCRIPT_PATH)
_mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
spec.loader.exec_module(_mod)  # type: ignore[union-attr]

get_effect_signature = _mod.get_effect_signature
get_usage_universal_ar = _mod.get_usage_universal_ar
get_i3rab_template = _mod.get_i3rab_template
load_quran_i3rab_phrases = _mod.load_quran_i3rab_phrases
strip_diacritics = _mod.strip_diacritics
enrich_row = _mod.enrich_row
_PHRASE_SEP = _mod._PHRASE_SEP
MAX_EVIDENCE_PHRASES = _mod.MAX_EVIDENCE_PHRASES

# Path to the quran i3rab CSV (used in integration tests)
_QURAN_I3RAB_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "i3rab", "quran_i3rab.csv"
)


# ---------------------------------------------------------------------------
# Helper rows
# ---------------------------------------------------------------------------
_PREP_ROW = {
    "Group Number": "1",
    "Arabic Group Name": "الجر فقط الدلالية",
    "English Group Name": "Prepositions Only (Semantic)",
    "Operator": "بِ",
    "Purpose/Usage": "للدلالة على المرور أو القرب",
    "Example": "مررت بزيد",
    "Note": "الباء: حرف جر، زيد: اسم مجرور",
}

_OATH_ROW = {
    "Group Number": "1",
    "Arabic Group Name": "الجر فقط الدلالية",
    "English Group Name": "Prepositions Only (Semantic)",
    "Operator": "وَ",
    "Purpose/Usage": "للدلالة على القسم",
    "Example": "والله لأشربن",
    "Note": "واو: حرف قسم، الله: اسم مجرور",
}

_OTHER_ROW = {
    "Group Number": "2",
    "Arabic Group Name": "التوكيد",
    "English Group Name": "Emphasis",
    "Operator": "إِنَّ",
    "Purpose/Usage": "للتوكيد",
    "Example": "إن زيدا قائم",
    "Note": "إنَّ: حرف توكيد، زيدا: اسم منصوب",
}


# ---------------------------------------------------------------------------
# 1. Test: diacritics preserved in project_usage_universal_ar
# ---------------------------------------------------------------------------
class TestUsageUniversalArDiacritics:
    """Diacritics must NOT be stripped from project_usage_universal_ar."""

    def test_gen_signature_contains_tashkil(self):
        text = get_usage_universal_ar("GEN")
        # The text must contain Arabic diacritics (fatha, kasra, shadda, sukun…)
        has_diacritic = any(
            "\u064b" <= ch <= "\u065f" or ch == "\u0670"
            for ch in text
        )
        assert has_diacritic, (
            f"Expected diacritics in GEN usage text but got: {text!r}"
        )

    def test_oath_gen_signature_contains_tashkil(self):
        text = get_usage_universal_ar("OATH_GEN")
        has_diacritic = any(
            "\u064b" <= ch <= "\u065f" or ch == "\u0670"
            for ch in text
        )
        assert has_diacritic, (
            f"Expected diacritics in OATH_GEN usage text but got: {text!r}"
        )

    def test_strip_diacritics_differs_from_original(self):
        text = get_usage_universal_ar("GEN")
        stripped = strip_diacritics(text)
        assert stripped != text, (
            "strip_diacritics() should remove diacritics but text was unchanged"
        )


# ---------------------------------------------------------------------------
# 2. Test: diacritics preserved in project_i3rab_template
# ---------------------------------------------------------------------------
class TestI3rabTemplateDiacritics:
    """Diacritics must NOT be stripped from project_i3rab_template."""

    def test_gen_template_contains_tashkil(self):
        tmpl = get_i3rab_template("GEN")
        has_diacritic = any(
            "\u064b" <= ch <= "\u065f" or ch == "\u0670"
            for ch in tmpl
        )
        assert has_diacritic, f"Expected tashkil in GEN template: {tmpl!r}"

    def test_oath_gen_template_contains_tashkil(self):
        tmpl = get_i3rab_template("OATH_GEN")
        has_diacritic = any(
            "\u064b" <= ch <= "\u065f" or ch == "\u0670"
            for ch in tmpl
        )
        assert has_diacritic, f"Expected tashkil in OATH_GEN template: {tmpl!r}"

    def test_gen_template_contains_noun_placeholder(self):
        tmpl = get_i3rab_template("GEN")
        assert "{NOUN}" in tmpl, f"GEN template missing {{NOUN}} placeholder: {tmpl!r}"


# ---------------------------------------------------------------------------
# 3. Test: evidence phrases extraction (requires quran_i3rab.csv)
# ---------------------------------------------------------------------------
@pytest.mark.skipif(
    not os.path.isfile(_QURAN_I3RAB_PATH),
    reason=f"quran_i3rab.csv not found at {_QURAN_I3RAB_PATH}",
)
class TestEvidencePhrases:
    """Validate phrase extraction from quran_i3rab.csv."""

    def test_gen_returns_at_most_5_phrases(self):
        phrases = load_quran_i3rab_phrases(_QURAN_I3RAB_PATH, "GEN")
        assert len(phrases) <= MAX_EVIDENCE_PHRASES, (
            f"Expected ≤{MAX_EVIDENCE_PHRASES} phrases, got {len(phrases)}"
        )

    def test_gen_phrases_contain_genitive_cue(self):
        """At least one phrase for GEN must contain a genitive cue word."""
        phrases = load_quran_i3rab_phrases(_QURAN_I3RAB_PATH, "GEN")
        genitive_cues = ("مَجْرُورٌ", "جَرِّهِ", "الْكَسْرَةُ", "حَرْفُ جَرٍّ")
        found = any(
            any(cue in phrase for cue in genitive_cues)
            for phrase in phrases
        )
        assert found, (
            "Expected at least one GEN phrase to contain a genitive cue word. "
            f"Got: {phrases}"
        )

    def test_phrases_preserve_diacritics(self):
        phrases = load_quran_i3rab_phrases(_QURAN_I3RAB_PATH, "GEN")
        for phrase in phrases:
            has_diacritic = any(
                "\u064b" <= ch <= "\u065f" or ch == "\u0670"
                for ch in phrase
            )
            assert has_diacritic, (
                f"Phrase appears to have stripped diacritics: {phrase!r}"
            )

    def test_phrases_are_deduplicated(self):
        phrases = load_quran_i3rab_phrases(_QURAN_I3RAB_PATH, "GEN")
        assert len(phrases) == len(set(phrases)), "Phrases contain duplicates"


# ---------------------------------------------------------------------------
# 4. Test: effect signature computation
# ---------------------------------------------------------------------------
class TestEffectSignature:
    def test_prep_group_gives_gen(self):
        assert get_effect_signature(_PREP_ROW) == "GEN"

    def test_oath_note_gives_oath_gen(self):
        assert get_effect_signature(_OATH_ROW) == "OATH_GEN"

    def test_other_group_gives_empty(self):
        assert get_effect_signature(_OTHER_ROW) == ""


# ---------------------------------------------------------------------------
# 5. Test: enrich_row returns correct field names and types
# ---------------------------------------------------------------------------
class TestEnrichRow:
    def _cache(self):
        return {"GEN": [], "OATH_GEN": [], "": []}

    def test_all_new_fields_present(self):
        result = enrich_row(_PREP_ROW, self._cache())
        for field in (
            "project_usage_universal_ar",
            "project_i3rab_template",
            "project_effect_signature",
            "project_quran_evidence_phrases",
            "project_modules",
        ):
            assert field in result, f"Missing field: {field}"

    def test_phrases_is_list(self):
        result = enrich_row(_PREP_ROW, self._cache())
        assert isinstance(result["project_quran_evidence_phrases"], list)

    def test_modules_is_list(self):
        result = enrich_row(_PREP_ROW, self._cache())
        assert isinstance(result["project_modules"], list)

    def test_original_fields_preserved(self):
        result = enrich_row(_PREP_ROW, self._cache())
        for key, val in _PREP_ROW.items():
            assert result[key] == val, f"Original field {key!r} was modified"

    def test_empty_sig_gives_empty_usage(self):
        result = enrich_row(_OTHER_ROW, self._cache())
        assert result["project_usage_universal_ar"] == ""
        assert result["project_i3rab_template"] == ""
