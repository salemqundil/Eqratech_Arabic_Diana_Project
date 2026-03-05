"""
Pattern Catalog - Arabic Morphological Patterns
Comprehensive collection of verb forms, noun patterns, and broken plurals
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class PatternCategory(Enum):
    """High-level category for a morphological pattern."""
    VERB = "verb"
    NOUN = "noun"
    PARTICIPLE = "participle"
    PLURAL = "plural"
    ADJECTIVE = "adjective"
    OTHER = "other"


@dataclass
class PatternInfo:
    """Rich metadata about a single pattern."""
    template: str
    pattern_type: Any  # fvafk.c2b.morpheme.PatternType (kept as Any to avoid circular import)
    category: PatternCategory
    form: Optional[str] = None
    meaning: Optional[str] = None
    frequency_rank: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "template": self.template,
            "pattern_type": self.pattern_type.name if hasattr(self.pattern_type, "name") else str(self.pattern_type),
            "category": self.category.name,
            "form": self.form,
            "meaning": self.meaning,
            "frequency_rank": self.frequency_rank,
        }


@dataclass
class PatternMatch:
    """Result of matching a word against the catalog."""
    pattern_info: PatternInfo
    confidence: float


# ---------------------------------------------------------------------------
# Legacy "simple template" type kept for backward-compat with load_full_catalog
# ---------------------------------------------------------------------------

class _LegacyPatternType(Enum):
    """Pattern types (legacy – used only by load_full_catalog)."""
    VERB_FORM_I = "verb_form_i"
    VERB_FORM_II = "verb_form_ii"
    VERB_FORM_III = "verb_form_iii"
    VERB_FORM_IV = "verb_form_iv"
    VERB_FORM_V = "verb_form_v"
    VERB_FORM_VI = "verb_form_vi"
    VERB_FORM_VII = "verb_form_vii"
    VERB_FORM_VIII = "verb_form_viii"
    VERB_FORM_IX = "verb_form_ix"
    VERB_FORM_X = "verb_form_x"
    NOUN_MASDAR = "noun_masdar"
    NOUN_ACTIVE_PARTICIPLE = "noun_active_participle"
    NOUN_PASSIVE_PARTICIPLE = "noun_passive_participle"
    NOUN_INSTRUMENT = "noun_instrument"
    NOUN_PLACE_TIME = "noun_place_time"
    BROKEN_PLURAL = "broken_plural"
    ADJECTIVE = "adjective"


@dataclass
class PatternTemplate:
    """Simple pattern template (used by load_full_catalog)."""
    name: str
    template: str
    description: str
    pattern_type: str = "unknown"
    examples: Optional[List[str]] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _morpheme_pattern_type_to_category(pt: Any) -> PatternCategory:
    """Map fvafk.c2b.morpheme.PatternType → PatternCategory."""
    name = pt.name if hasattr(pt, "name") else str(pt)
    if name.startswith("FORM_"):
        return PatternCategory.VERB
    if name in ("ACTIVE_PARTICIPLE", "PASSIVE_PARTICIPLE"):
        return PatternCategory.PARTICIPLE
    if name.startswith("BROKEN_PLURAL") or name.startswith("SOUND_"):
        return PatternCategory.PLURAL
    if name in ("INTENSIVE", "ELATIVE", "COLOUR"):
        return PatternCategory.ADJECTIVE
    return PatternCategory.NOUN


_FORM_ROMAN: Dict[str, str] = {
    "FORM_I": "I", "FORM_II": "II", "FORM_III": "III",
    "FORM_IV": "IV", "FORM_V": "V", "FORM_VI": "VI",
    "FORM_VII": "VII", "FORM_VIII": "VIII", "FORM_IX": "IX",
    "FORM_X": "X",
}

_CATEGORY_STR_MAP: Dict[str, PatternCategory] = {
    "verb": PatternCategory.VERB,
    "noun": PatternCategory.NOUN,
    "broken_plural": PatternCategory.PLURAL,
    "adjective": PatternCategory.ADJECTIVE,
    "participle": PatternCategory.PARTICIPLE,
}

# Frequency rank: most common forms first (lower = more frequent)
_FREQUENCY_RANK: Dict[str, int] = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5,
    "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10,
}


class PatternCatalog:
    """Catalog of Arabic morphological patterns.

    Supports both:
    - Legacy class-method API: ``PatternCatalog.load_full_catalog()``
    - New instance API: ``catalog = PatternCatalog()``
    """

    def __init__(self) -> None:
        self._pattern_info_cache: List[PatternInfo] = self._build_cache()

    # ------------------------------------------------------------------
    # New instance API
    # ------------------------------------------------------------------

    def _build_cache(self) -> List[PatternInfo]:
        """Build PatternInfo list from PatternDatabase."""
        from .pattern_matcher import PatternDatabase  # avoid circular at module level
        db = PatternDatabase()
        cache: List[PatternInfo] = []
        rank_counter: Dict[str, int] = {}
        for tmpl in db.get_all():
            pt = tmpl.pattern_type
            cat_str: str = tmpl.category if isinstance(tmpl.category, str) else ""
            # Determine category
            if cat_str in _CATEGORY_STR_MAP:
                category = _CATEGORY_STR_MAP[cat_str]
            else:
                category = _morpheme_pattern_type_to_category(pt)
            # Override noun → participle for participle pattern types
            if pt.name in ("ACTIVE_PARTICIPLE", "PASSIVE_PARTICIPLE"):
                category = PatternCategory.PARTICIPLE
            # Determine form
            form: Optional[str] = tmpl.form if hasattr(tmpl, "form") else None
            if form is None:
                form = _FORM_ROMAN.get(pt.name)
            # Frequency rank
            freq: Optional[int] = None
            if form is not None and form in _FREQUENCY_RANK:
                freq = _FREQUENCY_RANK[form]
            else:
                # Use a global counter for non-verb patterns so they still get a rank
                key = pt.name
                rank_counter.setdefault(key, len(rank_counter) + 11)
                freq = rank_counter[key]
            cache.append(PatternInfo(
                template=tmpl.template,
                pattern_type=pt,
                category=category,
                form=form,
                meaning=tmpl.meaning if hasattr(tmpl, "meaning") else None,
                frequency_rank=freq,
            ))
        return cache

    def get_by_category(self, category: PatternCategory) -> List[PatternInfo]:
        """Return all patterns in a given category."""
        return [p for p in self._pattern_info_cache if p.category == category]

    def get_participle_patterns(self) -> List[PatternInfo]:
        """Return active and passive participle patterns."""
        return self.get_by_category(PatternCategory.PARTICIPLE)

    def get_verb_forms(self) -> List[PatternInfo]:
        """Return all verb-form patterns."""
        return self.get_by_category(PatternCategory.VERB)

    def search_patterns(
        self,
        category: Optional[PatternCategory] = None,
        form: Optional[str] = None,
        min_frequency_rank: Optional[int] = None,
    ) -> List[PatternInfo]:
        """Search patterns with optional filters."""
        results = self._pattern_info_cache
        if category is not None:
            results = [p for p in results if p.category == category]
        if form is not None:
            results = [p for p in results if p.form == form]
        if min_frequency_rank is not None:
            results = [
                p for p in results
                if p.frequency_rank is not None and p.frequency_rank <= min_frequency_rank
            ]
        return results

    def get_most_common(self, limit: int = 20) -> List[PatternInfo]:
        """Return patterns sorted by frequency rank (lowest rank = most common)."""
        ranked = [p for p in self._pattern_info_cache if p.frequency_rank is not None]
        ranked.sort(key=lambda p: p.frequency_rank)  # type: ignore[arg-type]
        return ranked[:limit]

    def match_pattern(self, word: str, root: Any) -> Optional[PatternMatch]:
        """Match *word* against the catalog, returning the best PatternMatch or None."""
        if not word:
            return None
        from .pattern_matcher import PatternMatcher  # avoid circular at module level
        matcher = PatternMatcher()
        pattern = matcher.match(word, root)
        if pattern is None:
            return None
        pt = pattern.pattern_type
        confidence = float(pattern.features.get("confidence", "0.5"))
        category = _morpheme_pattern_type_to_category(pt)
        if pt.name in ("ACTIVE_PARTICIPLE", "PASSIVE_PARTICIPLE"):
            category = PatternCategory.PARTICIPLE
        form_str = pattern.features.get("form") or _FORM_ROMAN.get(pt.name)
        info = PatternInfo(
            template=pattern.template,
            pattern_type=pt,
            category=category,
            form=form_str,
            meaning=pattern.features.get("meaning"),
            frequency_rank=_FREQUENCY_RANK.get(form_str) if form_str else None,
        )
        return PatternMatch(pattern_info=info, confidence=confidence)

    def get_pattern_by_template(self, template: str) -> Optional[PatternInfo]:
        """Return the first PatternInfo whose template matches."""
        for p in self._pattern_info_cache:
            if p.template == template:
                return p
        return None

    def get_statistics(self) -> Dict[str, int]:
        """Return summary statistics."""
        stats: Dict[str, int] = {"total_patterns": len(self._pattern_info_cache)}
        for cat in PatternCategory:
            key = f"category_{cat.name.lower()}"
            stats[key] = sum(1 for p in self._pattern_info_cache if p.category == cat)
        return stats

    # ------------------------------------------------------------------
    # Legacy class-method API (backward compatibility)
    # ------------------------------------------------------------------

    @classmethod
    def load_full_catalog(cls) -> Dict[str, List[PatternTemplate]]:
        """Load complete pattern catalog"""
        return {
            "verb_forms": cls._load_verb_patterns(),
            "noun_patterns": cls._load_noun_patterns(),
            "broken_plurals": cls._load_broken_plural_patterns(),
            "adjectives": cls._load_adjective_patterns(),
        }
    
    @classmethod
    def _load_verb_patterns(cls) -> List[PatternTemplate]:
        """Load verb form patterns (Forms I-X)"""
        return [
            # Form I (فَعَلَ)
            PatternTemplate(
                name="FORM_I_FATHA",
                template="فَعَلَ",
                description="Form I - فَتَحَ pattern",
                pattern_type="verb_form_i",
                examples=["كَتَبَ", "ذَهَبَ", "فَعَلَ"]
            ),
            PatternTemplate(
                name="FORM_I_KASRA",
                template="فَعِلَ",
                description="Form I - فَهِمَ pattern",
                pattern_type="verb_form_i",
                examples=["شَرِبَ", "عَلِمَ", "فَهِمَ"]
            ),
            PatternTemplate(
                name="FORM_I_DAMMA",
                template="فَعُلَ",
                description="Form I - حَسُنَ pattern",
                pattern_type="verb_form_i",
                examples=["حَسُنَ", "كَرُمَ", "عَظُمَ"]
            ),
            
            # Form II (فَعَّلَ)
            PatternTemplate(
                name="FORM_II",
                template="فَعَّلَ",
                description="Form II - causative/intensive",
                pattern_type="verb_form_ii",
                examples=["عَلَّمَ", "كَسَّرَ", "فَهَّمَ"]
            ),
            
            # Form III (فَاعَلَ)
            PatternTemplate(
                name="FORM_III",
                template="فَاعَلَ",
                description="Form III - mutual action",
                pattern_type="verb_form_iii",
                examples=["قَاتَلَ", "جَاهَدَ", "سَافَرَ"]
            ),
            
            # Form IV (أَفْعَلَ)
            PatternTemplate(
                name="FORM_IV",
                template="أَفْعَلَ",
                description="Form IV - causative",
                pattern_type="verb_form_iv",
                examples=["أَكْرَمَ", "أَخْرَجَ", "أَسْلَمَ"]
            ),
            
            # Form V (تَفَعَّلَ)
            PatternTemplate(
                name="FORM_V",
                template="تَفَعَّلَ",
                description="Form V - reflexive of Form II",
                pattern_type="verb_form_v",
                examples=["تَعَلَّمَ", "تَكَلَّمَ", "تَقَدَّمَ"]
            ),
            
            # Form VI (تَفَاعَلَ)
            PatternTemplate(
                name="FORM_VI",
                template="تَفَاعَلَ",
                description="Form VI - reflexive of Form III",
                pattern_type="verb_form_vi",
                examples=["تَقَاتَلَ", "تَعَاوَنَ", "تَبَادَلَ"]
            ),
            
            # Form VII (اِنْفَعَلَ)
            PatternTemplate(
                name="FORM_VII",
                template="اِنْفَعَلَ",
                description="Form VII - passive/reflexive",
                pattern_type="verb_form_vii",
                examples=["اِنْكَسَرَ", "اِنْفَتَحَ", "اِنْقَطَعَ"]
            ),
            
            # Form VIII (اِفْتَعَلَ)
            PatternTemplate(
                name="FORM_VIII",
                template="اِفْتَعَلَ",
                description="Form VIII - reflexive",
                pattern_type="verb_form_viii",
                examples=["اِجْتَمَعَ", "اِخْتَارَ", "اِشْتَغَلَ"]
            ),
            
            # Form IX (اِفْعَلَّ)
            PatternTemplate(
                name="FORM_IX",
                template="اِفْعَلَّ",
                description="Form IX - colors/defects",
                pattern_type="verb_form_ix",
                examples=["اِحْمَرَّ", "اِخْضَرَّ", "اِصْفَرَّ"]
            ),
            
            # Form X (اِسْتَفْعَلَ)
            PatternTemplate(
                name="FORM_X",
                template="اِسْتَفْعَلَ",
                description="Form X - seeking/requesting",
                pattern_type="verb_form_x",
                examples=["اِسْتَخْرَجَ", "اِسْتَقْبَلَ", "اِسْتَغْفَرَ"]
            ),
        ]
    
    @classmethod
    def _load_noun_patterns(cls) -> List[PatternTemplate]:
        """Load noun patterns"""
        return [
            # Masdar patterns
            PatternTemplate(
                name="MASDAR_FACL",
                template="فَعْل",
                description="Masdar Form I pattern",
                pattern_type="noun_masdar",
                examples=["ضَرْب", "أَكْل", "فَتْح"]
            ),
            PatternTemplate(
                name="MASDAR_FICAAL",
                template="فِعَال",
                description="Masdar Form I pattern",
                pattern_type="noun_masdar",
                examples=["جِهَاد", "قِتَال", "نِزَال"]
            ),
            PatternTemplate(
                name="MASDAR_TAFCEEL",
                template="تَفْعِيل",
                description="Masdar Form II",
                pattern_type="noun_masdar",
                examples=["تَعْلِيم", "تَكْسِير", "تَفْهِيم"]
            ),
            
            # Active participle
            PatternTemplate(
                name="ACTIVE_PARTICIPLE_FAACIL",
                template="فَاعِل",
                description="Active participle Form I",
                pattern_type="noun_active_participle",
                examples=["كَاتِب", "ذَاهِب", "قَارِئ"]
            ),
            PatternTemplate(
                name="ACTIVE_PARTICIPLE_MUFACCIL",
                template="مُفَعِّل",
                description="Active participle Form II",
                pattern_type="noun_active_participle",
                examples=["مُعَلِّم", "مُكَسِّر", "مُفَهِّم"]
            ),
            
            # Passive participle
            PatternTemplate(
                name="PASSIVE_PARTICIPLE_MAFCOOL",
                template="مَفْعُول",
                description="Passive participle Form I",
                pattern_type="noun_passive_participle",
                examples=["مَكْتُوب", "مَقْرُوء", "مَفْهُوم"]
            ),
            
            # Instrument nouns
            PatternTemplate(
                name="INSTRUMENT_MIFCAAL",
                template="مِفْعَال",
                description="Instrument noun",
                pattern_type="noun_instrument",
                examples=["مِفْتَاح", "مِقْيَاس", "مِنْشَار"]
            ),
            
            # Place/Time nouns
            PatternTemplate(
                name="PLACE_MAFCAL",
                template="مَفْعَل",
                description="Place/time noun",
                pattern_type="noun_place_time",
                examples=["مَكْتَب", "مَدْرَسَة", "مَطْبَخ"]
            ),
        ]
    
    @classmethod
    def _load_broken_plural_patterns(cls) -> List[PatternTemplate]:
        """Load broken plural patterns"""
        return [
            PatternTemplate(
                name="PLURAL_AFCAAL",
                template="أَفْعَال",
                description="Broken plural pattern",
                pattern_type="broken_plural",
                examples=["أَقْلَام", "أَبْوَاب", "أَيَّام"]
            ),
            PatternTemplate(
                name="PLURAL_FUCOOL",
                template="فُعُول",
                description="Broken plural pattern",
                pattern_type="broken_plural",
                examples=["بُيُوت", "عُيُون", "قُلُوب"]
            ),
            PatternTemplate(
                name="PLURAL_FACAALIL",
                template="فَعَائِل",
                description="Broken plural pattern",
                pattern_type="broken_plural",
                examples=["رَسَائِل", "مَسَائِل", "وَسَائِل"]
            ),
            PatternTemplate(
                name="PLURAL_FUCALAA",
                template="فُعَلَاء",
                description="Broken plural pattern",
                pattern_type="broken_plural",
                examples=["عُلَمَاء", "شُعَرَاء", "فُقَهَاء"]
            ),
        ]
    
    @classmethod
    def _load_adjective_patterns(cls) -> List[PatternTemplate]:
        """Load adjective patterns"""
        return [
            PatternTemplate(
                name="ADJECTIVE_FACEEL",
                template="فَعِيل",
                description="Intensive adjective",
                pattern_type="adjective",
                examples=["كَرِيم", "رَحِيم", "عَظِيم"]
            ),
            PatternTemplate(
                name="ADJECTIVE_AFCAL",
                template="أَفْعَل",
                description="Comparative/superlative",
                pattern_type="adjective",
                examples=["أَكْبَر", "أَصْغَر", "أَحْسَن"]
            ),
        ]


def create_default_catalog() -> PatternCatalog:
    """Factory function – create a default PatternCatalog instance."""
    return PatternCatalog()

