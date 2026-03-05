"""Syntax data models for I3rab representation.

This module defines the 3-layer architecture:
1. I3rabAnnotation - Raw data from corpus
2. I3rabComponents - Parsed structured data  
3. SyntaxFeatures - High-level features for analysis

Author: Hussein Hiyassat
Date: 2026-02-21
Sprint: 4 - Syntax Foundation
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class I3rabAnnotation:
    """Raw I3rab annotation from corpus.
    
    This is Layer 1: Direct representation of corpus data.
    """
    word: str
    i3rab_text: str  # Full Arabic I3rab description
    surah: int
    ayah: int
    word_index: int
    
    def __repr__(self) -> str:
        return f"I3rabAnnotation({self.word} [{self.surah}:{self.ayah}:{self.word_index}])"


@dataclass
class I3rabComponents:
    """Parsed I3rab components.
    
    This is Layer 2: Structured extraction from I3rab text.
    """
    i3rab_type: Optional[str] = None  # مبتدأ، خبر، فاعل، مفعول به، حرف
    case: Optional[str] = None  # nominative, accusative, genitive
    case_marker: Optional[str] = None  # الضمة، الفتحة، الكسرة
    mahall: Optional[str] = None  # في محل رفع / لا محل له من الإعراب
    confidence: float = 0.0  # 0.0-1.0 parsing confidence
    raw_text: str = ""  # Original I3rab text for reference
    
    def __repr__(self) -> str:
        return f"I3rabComponents(type={self.i3rab_type}, case={self.case}, conf={self.confidence:.2f})"


@dataclass
class SyntaxFeatures:
    """High-level syntax features.
    
    This is Layer 3: Final output for integration with WordForm.
    """
    syntactic_role: str  # "subject", "predicate", "object", "particle"
    case: str  # "nominative", "accusative", "genitive"
    i3rab_type_ar: str  # "مبتدأ"
    i3rab_type_en: str  # "mubtada"
    confidence: float  # 0.0-1.0
    warning: Optional[str] = None  # Warning message for low confidence
    
    def __post_init__(self):
        """Set warnings based on confidence."""
        if self.confidence < 0.5:
            self.warning = "Low confidence - verify manually"
        elif self.confidence < 0.7:
            self.warning = "Medium confidence"
    
    def __repr__(self) -> str:
        return f"SyntaxFeatures({self.i3rab_type_en}, {self.case}, conf={self.confidence:.2f})"