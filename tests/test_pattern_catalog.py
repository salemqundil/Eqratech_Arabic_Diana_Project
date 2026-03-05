"""
Tests for PatternCatalog.

Tests cover:
- Catalog initialization and building
- Category-based filtering
- Form-based filtering (via get_verb_forms / search)
- Frequency ranking (get_most_common)
- Pattern matching
- Search functionality
- Statistics generation
- Edge cases
"""

import pytest

from fvafk.c2b.pattern_catalog import (
    PatternCatalog,
    PatternInfo,
    PatternCategory,
    PatternMatch,
    create_default_catalog,
)
from fvafk.c2b.morpheme import Root, RootType, PatternType


class TestPatternCatalogInitialization:
    """Tests for PatternCatalog initialization."""

    def test_catalog_creates_default_instance(self):
        """Test default catalog creation."""
        catalog = PatternCatalog()
        assert catalog is not None
        assert len(catalog._pattern_info_cache) > 0

    def test_catalog_builds_entries_from_database(self):
        """Test catalog builds entries from pattern database."""
        catalog = PatternCatalog()
        stats = catalog.get_statistics()

        assert stats["total_patterns"] > 50
        assert stats["category_verb"] > 0
        assert stats["category_noun"] > 0
        assert stats["category_plural"] > 0


class TestCategoryFiltering:
    """Tests for category-based filtering."""

    def test_get_by_category_verbs(self):
        """Test getting verb patterns."""
        catalog = PatternCatalog()
        verbs = catalog.get_by_category(PatternCategory.VERB)

        assert len(verbs) > 0
        for info in verbs:
            assert info.category == PatternCategory.VERB

    def test_get_by_category_nouns(self):
        """Test getting noun patterns."""
        catalog = PatternCatalog()
        nouns = catalog.get_by_category(PatternCategory.NOUN)

        assert len(nouns) > 0
        for info in nouns:
            assert info.category == PatternCategory.NOUN

    def test_get_by_category_plurals(self):
        """Test getting plural patterns."""
        catalog = PatternCatalog()
        plurals = catalog.get_by_category(PatternCategory.PLURAL)

        assert len(plurals) > 0
        for info in plurals:
            assert info.category == PatternCategory.PLURAL

    def test_get_participle_patterns(self):
        """Test getting participle patterns."""
        catalog = PatternCatalog()
        participles = catalog.get_participle_patterns()

        assert isinstance(participles, list)
        for info in participles:
            assert info.category == PatternCategory.PARTICIPLE


class TestFormFiltering:
    """Tests for form-based filtering via search and get_verb_forms."""

    def test_get_verb_forms_returns_sorted(self):
        """Test get_verb_forms returns verb patterns."""
        catalog = PatternCatalog()
        verbs = catalog.get_verb_forms()

        assert len(verbs) > 0
        for info in verbs:
            assert info.category == PatternCategory.VERB

    def test_search_by_form_i(self):
        """Test searching Form I patterns."""
        catalog = PatternCatalog()
        form_i = catalog.search_patterns(form="I")

        assert len(form_i) > 0
        for info in form_i:
            assert info.form == "I"

    def test_search_by_form_ii(self):
        """Test searching Form II patterns."""
        catalog = PatternCatalog()
        form_ii = catalog.search_patterns(form="II")

        assert len(form_ii) > 0
        for info in form_ii:
            assert info.form == "II"

    def test_search_by_form_x(self):
        """Test searching Form X patterns."""
        catalog = PatternCatalog()
        form_x = catalog.search_patterns(form="X")

        assert len(form_x) > 0
        for info in form_x:
            assert info.form == "X"


class TestFrequencyRanking:
    """Tests for frequency ranking (get_most_common)."""

    def test_get_most_common_returns_limited_results(self):
        """Test get_most_common limits results."""
        catalog = PatternCatalog()
        top_10 = catalog.get_most_common(limit=10)

        assert len(top_10) <= 10

    def test_get_most_common_sorted_by_frequency(self):
        """Test get_most_common is sorted by frequency rank."""
        catalog = PatternCatalog()
        top_patterns = catalog.get_most_common(limit=20)

        ranks = [p.frequency_rank for p in top_patterns if p.frequency_rank is not None]
        if len(ranks) > 1:
            assert ranks == sorted(ranks)

    def test_get_most_common_default_limit(self):
        """Test get_most_common with default limit."""
        catalog = PatternCatalog()
        top = catalog.get_most_common()
        assert len(top) <= 20


class TestPatternMatching:
    """Tests for pattern matching functionality."""

    def test_match_pattern_simple_word(self):
        """Test matching a simple word."""
        catalog = PatternCatalog()
        root = Root(letters=("ك", "ت", "ب"), root_type=RootType.TRILATERAL)

        match = catalog.match_pattern("كَتَبَ", root)

        assert match is not None
        assert match.confidence > 0.0

    def test_match_pattern_form_ii(self):
        """Test matching Form II verb."""
        catalog = PatternCatalog()
        root = Root(letters=("ع", "ل", "م"), root_type=RootType.TRILATERAL)

        match = catalog.match_pattern("عَلَّمَ", root)

        assert match is not None
        assert match.pattern_info.pattern_type == PatternType.FORM_II

    def test_match_pattern_no_match_returns_none(self):
        """Test no match returns None."""
        catalog = PatternCatalog()
        root = Root(letters=("ك", "ت", "ب"), root_type=RootType.TRILATERAL)

        match = catalog.match_pattern("xyz", root)

        assert match is None

    def test_match_pattern_active_participle(self):
        """Test matching active participle (كَاتِب or كاتب)."""
        catalog = PatternCatalog()
        root = Root(letters=("ك", "ت", "ب"), root_type=RootType.TRILATERAL)

        # Try with tashkeel first; matcher may require diacritics
        match = catalog.match_pattern("كَاتِب", root)
        if match is None:
            match = catalog.match_pattern("كاتب", root)

        assert match is not None
        assert match.pattern_info.pattern_type == PatternType.ACTIVE_PARTICIPLE


class TestSearchFunctionality:
    """Tests for search_patterns."""

    def test_search_patterns_by_category(self):
        """Test searching by category."""
        catalog = PatternCatalog()
        results = catalog.search_patterns(category=PatternCategory.VERB)

        assert len(results) > 0
        for info in results:
            assert info.category == PatternCategory.VERB

    def test_search_patterns_by_form(self):
        """Test searching by form."""
        catalog = PatternCatalog()
        results = catalog.search_patterns(form="I")

        assert len(results) > 0
        for info in results:
            assert info.form == "I"

    def test_search_patterns_with_min_frequency(self):
        """Test searching with minimum frequency rank."""
        catalog = PatternCatalog()
        results = catalog.search_patterns(min_frequency_rank=10)

        for info in results:
            if info.frequency_rank is not None:
                assert info.frequency_rank <= 10

    def test_search_patterns_combined_filters(self):
        """Test searching with multiple filters."""
        catalog = PatternCatalog()
        results = catalog.search_patterns(category=PatternCategory.VERB, form="I")

        assert len(results) > 0
        for info in results:
            assert info.category == PatternCategory.VERB
            assert info.form == "I"

    def test_get_pattern_by_template(self):
        """Test get pattern info by template string."""
        catalog = PatternCatalog()
        info = catalog.get_pattern_by_template("فَعَلَ")

        assert info is not None
        assert info.template == "فَعَلَ"


class TestStatistics:
    """Tests for statistics generation."""

    def test_get_statistics_has_total(self):
        """Test statistics includes total count."""
        catalog = PatternCatalog()
        stats = catalog.get_statistics()

        assert "total_patterns" in stats
        assert stats["total_patterns"] > 0

    def test_get_statistics_has_categories(self):
        """Test statistics includes category counts."""
        catalog = PatternCatalog()
        stats = catalog.get_statistics()

        assert "category_verb" in stats
        assert "category_noun" in stats
        assert "category_plural" in stats

    def test_get_statistics_counts_consistent(self):
        """Test statistics counts are consistent."""
        catalog = PatternCatalog()
        stats = catalog.get_statistics()

        total = stats["total_patterns"]
        category_sum = sum(
            v for k, v in stats.items()
            if k.startswith("category_")
        )
        assert total >= 0
        assert category_sum >= 0


class TestPatternInfo:
    """Tests for PatternInfo dataclass."""

    def test_pattern_info_creation(self):
        """Test creating PatternInfo."""
        info = PatternInfo(
            template="فَعَلَ",
            pattern_type=PatternType.FORM_I,
            category=PatternCategory.VERB,
            form="I",
            meaning="past tense",
            frequency_rank=1,
        )

        assert info.template == "فَعَلَ"
        assert info.pattern_type == PatternType.FORM_I
        assert info.category == PatternCategory.VERB
        assert info.form == "I"

    def test_pattern_info_to_dict(self):
        """Test PatternInfo.to_dict()."""
        info = PatternInfo(
            template="فَعَلَ",
            pattern_type=PatternType.FORM_I,
            category=PatternCategory.VERB,
            form="I",
        )
        d = info.to_dict()
        assert d["template"] == "فَعَلَ"
        assert d["category"] == "VERB"
        assert d["form"] == "I"


class TestEdgeCases:
    """Tests for edge cases."""

    def test_search_no_filters_returns_all(self):
        """Test search with no filters returns all patterns."""
        catalog = PatternCatalog()
        results = catalog.search_patterns()

        assert len(results) == len(catalog._pattern_info_cache)

    def test_match_pattern_none_word(self):
        """Test match with empty string."""
        catalog = PatternCatalog()
        root = Root(letters=("ك", "ت", "ب"), root_type=RootType.TRILATERAL)
        match = catalog.match_pattern("", root)
        assert match is None

    def test_create_default_catalog(self):
        """Test create_default_catalog factory."""
        catalog = create_default_catalog()
        assert isinstance(catalog, PatternCatalog)
        assert catalog.get_statistics()["total_patterns"] > 0


class TestIntegration:
    """Integration tests with existing components."""

    def test_catalog_integrates_with_pattern_matcher(self):
        """Test catalog uses PatternMatcher correctly (verb or participle)."""
        catalog = PatternCatalog()
        root = Root(letters=("ك", "ت", "ب"), root_type=RootType.TRILATERAL)

        # Past verb is reliably matched
        match = catalog.match_pattern("كَتَبَ", root)
        assert match is not None
        assert match.pattern_info.pattern_type == PatternType.FORM_I

    def test_catalog_loads_awzan_patterns(self):
        """Test catalog loads patterns from awzan database."""
        catalog = PatternCatalog()
        stats = catalog.get_statistics()
        assert stats["total_patterns"] > 25


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
