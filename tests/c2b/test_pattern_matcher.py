"""Tests for PatternMatcher."""

import pytest

from fvafk.c2b.morpheme import PatternType, Root, RootType
from fvafk.c2b.pattern_matcher import PatternDatabase, PatternMatcher




@pytest.fixture(autouse=True)
def clear_pattern_cache():
    """Clear pattern cache before each test."""
    from fvafk.c2b.awzan_loader import AwzanPatternLoader
    AwzanPatternLoader._cache = None
    yield

class TestPatternDatabase:
    def test_database_has_patterns(self):
        db = PatternDatabase()
        patterns = db.get_all()
        assert len(patterns) >= 20

    def test_get_by_category(self):
        db = PatternDatabase()
        assert all(p.category == "verb" for p in db.get_by_category("verb"))
        assert all(p.category == "noun" for p in db.get_by_category("noun"))
        assert all(p.category == "plural" for p in db.get_by_category("plural"))


class TestPatternMatcherVerbForms:
    def test_form_i(self):
        matcher = PatternMatcher()
        root = Root(letters=("ك", "ت", "ب"), root_type=RootType.TRILATERAL)
        pattern = matcher.match("كَتَبَ", root)
        assert pattern
        assert pattern.pattern_type == PatternType.FORM_I

    def test_form_ii(self):
        matcher = PatternMatcher()
        root = Root(letters=("ع", "ل", "م"), root_type=RootType.TRILATERAL)
        pattern = matcher.match("عَلَّمَ", root)
        assert pattern
        assert pattern.pattern_type == PatternType.FORM_II

    def test_form_x(self):
        matcher = PatternMatcher()
        root = Root(letters=("ك", "ت", "ب"), root_type=RootType.TRILATERAL)
        pattern = matcher.match("اسْتَكْتَبَ", root)
        assert pattern
        assert pattern.pattern_type == PatternType.FORM_X

    def test_form_iv_hamza_normalized(self):
        matcher = PatternMatcher()
        root = Root(letters=("خ", "ر", "ج"), root_type=RootType.TRILATERAL)
        pattern = matcher.match("أَخْرَجَ", root)
        assert pattern
        assert pattern.pattern_type == PatternType.FORM_IV


class TestPatternMatcherNouns:
    def test_active_participle(self):
        matcher = PatternMatcher()
        root = Root(letters=("ك", "ت", "ب"), root_type=RootType.TRILATERAL)
        pattern = matcher.match("كَاتِب", root)
        assert pattern
        assert pattern.pattern_type == PatternType.ACTIVE_PARTICIPLE

    def test_passive_participle(self):
        matcher = PatternMatcher()
        root = Root(letters=("ك", "ت", "ب"), root_type=RootType.TRILATERAL)
        pattern = matcher.match("مَكْتُوب", root)
        assert pattern
        assert pattern.pattern_type == PatternType.PASSIVE_PARTICIPLE

    def test_place_noun(self):
        matcher = PatternMatcher()
        root = Root(letters=("ك", "ت", "ب"), root_type=RootType.TRILATERAL)
        pattern = matcher.match("مَكْتَب", root)
        assert pattern
        assert pattern.pattern_type == PatternType.PLACE_TIME_NOUN

    def test_verbal_noun(self):
        matcher = PatternMatcher()
        root = Root(letters=("ك", "ت", "ب"), root_type=RootType.TRILATERAL)
        pattern = matcher.match("كِتَاب", root)
        assert pattern
        assert pattern.pattern_type == PatternType.VERBAL_NOUN

    def test_fathatan_support_alif_does_not_break_matching(self):
        matcher = PatternMatcher()
        root = Root(letters=("ع", "ظ", "م"), root_type=RootType.TRILATERAL)
        pattern = matcher.match("عَظِيمًا", root)
        assert pattern
        assert pattern.template == "فَعِيل"


class TestPatternMatcherPlurals:
    def test_sound_masculine_plural(self):
        matcher = PatternMatcher()
        root = Root(letters=("ك", "ت", "ب"), root_type=RootType.TRILATERAL)
        pattern = matcher.match("كَاتِبُون", root)
        assert pattern
        assert pattern.pattern_type == PatternType.SOUND_MASCULINE_PLURAL

    def test_sound_feminine_plural(self):
        matcher = PatternMatcher()
        root = Root(letters=("ك", "ت", "ب"), root_type=RootType.TRILATERAL)
        pattern = matcher.match("كَاتِبَات", root)
        assert pattern
        assert pattern.pattern_type == PatternType.SOUND_FEMININE_PLURAL

    def test_broken_plural(self):
        matcher = PatternMatcher()
        root = Root(letters=("ك", "ت", "ب"), root_type=RootType.TRILATERAL)
        pattern = matcher.match("كُتُب", root)
        assert pattern
        assert pattern.pattern_type == PatternType.BROKEN_PLURAL_FUUL


class TestBestConfidenceSelection:
    """Verify that match() returns the highest-confidence match, not the first."""

    def test_active_participle_beats_form_iii(self):
        matcher = PatternMatcher()
        root = Root(letters=("ك", "ت", "ب"), root_type=RootType.TRILATERAL)
        pattern = matcher.match("كَاتِب", root)
        assert pattern is not None
        assert pattern.pattern_type == PatternType.ACTIVE_PARTICIPLE
        assert float(pattern.features["confidence"]) > 0.60

    def test_broken_plural_beats_form_i(self):
        matcher = PatternMatcher()
        root = Root(letters=("ك", "ت", "ب"), root_type=RootType.TRILATERAL)
        pattern = matcher.match("كُتُب", root)
        assert pattern is not None
        assert pattern.pattern_type == PatternType.BROKEN_PLURAL_FUUL
        assert float(pattern.features["confidence"]) >= 0.85

    def test_exact_match_short_circuits(self):
        matcher = PatternMatcher()
        root = Root(letters=("ك", "ت", "ب"), root_type=RootType.TRILATERAL)
        pattern = matcher.match("كَتَبَ", root)
        assert pattern is not None
        assert pattern.pattern_type == PatternType.FORM_I
        assert float(pattern.features["confidence"]) == 1.0


class TestPatternMatcherEdgeCases:
    def test_empty_word(self):
        matcher = PatternMatcher()
        root = Root(letters=("ك", "ت", "ب"), root_type=RootType.TRILATERAL)
        assert matcher.match("", root) is None

    def test_none_root(self):
        matcher = PatternMatcher()
        assert matcher.match("كاتب", None) is None

    def test_unrecognized(self):
        matcher = PatternMatcher()
        root = Root(letters=("ك", "ت", "ب"), root_type=RootType.TRILATERAL)
        assert matcher.match("كبتبكت", root) is None
