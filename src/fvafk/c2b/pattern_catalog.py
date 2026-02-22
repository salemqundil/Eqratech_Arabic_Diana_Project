"""
PatternCatalog: High-level API for Arabic morphological pattern access.

This module provides an organized, taxonomy-based interface to access
Arabic morphological patterns. It wraps PatternDatabase and PatternMatcher
to provide:
- Categorized pattern access (verbs, nouns, plurals)
- Confidence-scored pattern matching
- Pattern taxonomy and metadata
- Integration with Bayan's PatternUniverse

Classes:
    PatternCategory: Enum for pattern categories
    PatternInfo: Rich pattern information with metadata
    PatternCatalog: Main catalog interface
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional

from .morpheme import Pattern, PatternType, Root
from .pattern_matcher import PatternDatabase, PatternMatcher, PatternTemplate


class PatternCategory(Enum):
    """Categories of Arabic morphological patterns."""

    VERB = auto()           # Verb forms (I-X)
    NOUN = auto()           # Noun patterns
    PLURAL = auto()         # Plural patterns (sound & broken)
    PARTICIPLE = auto()     # Active & passive participles
    VERBAL_NOUN = auto()    # Masdar patterns
    ADJECTIVE = auto()      # Adjectival patterns
    OTHER = auto()          # Uncategorized patterns


@dataclass(frozen=True)
class PatternInfo:
    """Rich pattern information with metadata.

    Attributes:
        template: Pattern template string (e.g., "فَعَلَ")
        pattern_type: PatternType enum value
        category: PatternCategory
        form: Optional form designation (e.g., "I", "II")
        meaning: Optional semantic meaning
        cv_simple: Simple CV pattern
        cv_detailed: Detailed CV pattern
        cv_advanced: Advanced CV pattern
        notes: Additional notes
        frequency_rank: Estimated frequency rank (lower = more common)
    """
    template: str
    pattern_type: PatternType
    category: PatternCategory
    form: Optional[str] = None
    meaning: Optional[str] = None
    cv_simple: Optional[str] = None
    cv_detailed: Optional[str] = None
    cv_advanced: Optional[str] = None
    notes: Optional[str] = None
    frequency_rank: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "template": self.template,
            "pattern_type": self.pattern_type.name,
            "category": self.category.name,
            "form": self.form,
            "meaning": self.meaning,
            "cv_simple": self.cv_simple,
            "cv_detailed": self.cv_detailed,
            "cv_advanced": self.cv_advanced,
            "notes": self.notes,
            "frequency_rank": self.frequency_rank,
        }


@dataclass
class PatternMatch:
    """Result of pattern matching operation.

    Attributes:
        pattern_info: Matched pattern information
        confidence: Match confidence score [0.0, 1.0]
        matched_word: The word that was matched
        root: The root used for matching
    """
    pattern_info: PatternInfo
    confidence: float
    matched_word: str
    root: Root

    def __post_init__(self):
        """Validate confidence score."""
        assert 0.0 <= self.confidence <= 1.0, "Confidence must be in [0, 1]"


class PatternCatalog:
    """High-level catalog for Arabic morphological patterns.

    Provides organized access to pattern database with:
    - Taxonomic categorization
    - Confidence-scored matching
    - Pattern frequency information
    - Integration with existing PatternMatcher

    Attributes:
        database: PatternDatabase instance
        matcher: PatternMatcher instance
    """

    def __init__(
        self,
        database: Optional[PatternDatabase] = None,
        matcher: Optional[PatternMatcher] = None,
    ):
        """Initialize pattern catalog."""
        self.database = database or PatternDatabase()
        self.matcher = matcher or PatternMatcher(self.database)
        self._pattern_info_cache: Dict[str, PatternInfo] = {}
        self._build_catalog()

    def _build_catalog(self) -> None:
        """Build internal catalog from database."""
        for template in self.database.get_all():
            category = self._categorize_pattern(template)
            pattern_info = PatternInfo(
                template=template.template,
                pattern_type=template.pattern_type,
                category=category,
                form=template.form,
                meaning=template.meaning,
                cv_simple=template.cv_simple,
                cv_detailed=template.cv_detailed,
                cv_advanced=template.cv_advanced,
                notes=template.notes,
                frequency_rank=self._estimate_frequency(template),
            )
            self._pattern_info_cache[template.template] = pattern_info

    def _categorize_pattern(self, template: PatternTemplate) -> PatternCategory:
        """Categorize a pattern template."""
        category_str = template.category.lower()

        if category_str == "verb":
            return PatternCategory.VERB
        elif category_str == "plural":
            return PatternCategory.PLURAL
        elif category_str == "noun":
            pt = template.pattern_type
            if pt in (PatternType.ACTIVE_PARTICIPLE, PatternType.PASSIVE_PARTICIPLE):
                return PatternCategory.PARTICIPLE
            elif pt == PatternType.VERBAL_NOUN:
                return PatternCategory.VERBAL_NOUN
            elif pt in (PatternType.INTENSIVE, PatternType.ELATIVE):
                return PatternCategory.ADJECTIVE
            else:
                return PatternCategory.NOUN
        else:
            return PatternCategory.OTHER

    def _estimate_frequency(self, template: PatternTemplate) -> int:
        """Estimate frequency rank (lower = more common)."""
        high_frequency = {
            PatternType.FORM_I: 1,
            PatternType.FORM_II: 5,
            PatternType.FORM_III: 10,
            PatternType.ACTIVE_PARTICIPLE: 3,
            PatternType.PASSIVE_PARTICIPLE: 8,
            PatternType.SOUND_MASCULINE_PLURAL: 6,
            PatternType.SOUND_FEMININE_PLURAL: 7,
            PatternType.BROKEN_PLURAL_FUUL: 12,
        }
        return high_frequency.get(template.pattern_type, 50)

    def get_by_category(self, category: PatternCategory) -> List[PatternInfo]:
        """Get all patterns in a category."""
        return [
            info for info in self._pattern_info_cache.values()
            if info.category == category
        ]

    def get_verb_forms(self) -> List[PatternInfo]:
        """Get all verb form patterns (I-X)."""
        verbs = self.get_by_category(PatternCategory.VERB)
        return sorted(verbs, key=lambda x: x.form or "")

    def get_noun_patterns(self) -> List[PatternInfo]:
        """Get all noun patterns."""
        return self.get_by_category(PatternCategory.NOUN)

    def get_plural_patterns(self) -> List[PatternInfo]:
        """Get all plural patterns."""
        return self.get_by_category(PatternCategory.PLURAL)

    def get_participle_patterns(self) -> List[PatternInfo]:
        """Get all participle patterns."""
        return self.get_by_category(PatternCategory.PARTICIPLE)

    def get_most_common(self, limit: int = 20) -> List[PatternInfo]:
        """Get most common patterns by frequency rank."""
        all_patterns = list(self._pattern_info_cache.values())
        sorted_patterns = sorted(
            all_patterns,
            key=lambda x: x.frequency_rank or 999,
        )
        return sorted_patterns[:limit]

    def match_pattern(self, word: str, root: Root) -> Optional[PatternMatch]:
        """Match word against pattern catalog.

        Args:
            word: Arabic word to match
            root: Extracted root

        Returns:
            PatternMatch with confidence score, or None if no match
        """
        pattern = self.matcher.match(word, root)
        if not pattern:
            return None

        pattern_info = self._pattern_info_cache.get(pattern.template)
        if not pattern_info:
            pattern_info = PatternInfo(
                template=pattern.template,
                pattern_type=pattern.pattern_type,
                category=PatternCategory.OTHER,
            )

        confidence = 0.8
        if pattern.features and "confidence" in pattern.features:
            try:
                confidence = float(pattern.features["confidence"])
            except (ValueError, TypeError):
                pass

        return PatternMatch(
            pattern_info=pattern_info,
            confidence=confidence,
            matched_word=word,
            root=root,
        )

    def get_pattern_by_template(self, template: str) -> Optional[PatternInfo]:
        """Get pattern info by template string."""
        return self._pattern_info_cache.get(template)

    def search_patterns(
        self,
        category: Optional[PatternCategory] = None,
        form: Optional[str] = None,
        min_frequency_rank: Optional[int] = None,
    ) -> List[PatternInfo]:
        """Search patterns with filters.

        Args:
            category: Filter by category
            form: Filter by form (e.g., "I", "II")
            min_frequency_rank: Only patterns with rank <= this value

        Returns:
            List of matching PatternInfo objects
        """
        results = list(self._pattern_info_cache.values())

        if category:
            results = [p for p in results if p.category == category]

        if form:
            results = [p for p in results if p.form == form]

        if min_frequency_rank is not None:
            results = [
                p for p in results
                if p.frequency_rank is not None and p.frequency_rank <= min_frequency_rank
            ]

        return results

    def get_statistics(self) -> Dict[str, int]:
        """Get catalog statistics."""
        stats: Dict[str, int] = {
            "total_patterns": len(self._pattern_info_cache),
        }
        for category in PatternCategory:
            count = len(self.get_by_category(category))
            stats[f"category_{category.name.lower()}"] = count
        return stats


def create_default_catalog() -> PatternCatalog:
    """Create catalog with default database and matcher."""
    return PatternCatalog()
