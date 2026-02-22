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
