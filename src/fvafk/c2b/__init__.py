"""
Morphology (C2b) package.
"""

from .morpheme import (
    Affix,
    AffixType,
    Morpheme,
    MorphologicalAnalysis,
    Pattern,
    PatternType,
    Root,
    RootType,
)
from .pattern_matcher import PatternDatabase, PatternMatcher, PatternTemplate
from .root_extractor import RootExtractionResult, RootExtractor
from .mabni_rules import MabniResult, classify_mabni, should_skip_root_extraction as mabni_should_skip_root
from .word_form import (
    WordForm,
    PartOfSpeech,
    Case,
    Number,
    Gender,
    SyntaxRole,
    Span,
)
from .word_form import WordFormBuilder

__all__ = [
    "Affix",
    "AffixType",
    "Morpheme",
    "MorphologicalAnalysis",
    "Pattern",
    "PatternType",
    "Root",
    "RootType",
    "RootExtractionResult",
    "RootExtractor",
    "MabniResult",
    "classify_mabni",
    "mabni_should_skip_root",
    "PatternMatcher",
    "PatternTemplate",
    "PatternDatabase",
    "WordForm",
    "PartOfSpeech",
    "Case",
    "Number",
    "Gender",
    "SyntaxRole",
    "Span",
    "WordFormBuilder",
]
