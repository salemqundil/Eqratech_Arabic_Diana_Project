"""
Pydantic Models for FVAFK/Bayan

Type-safe data models for the entire pipeline.

Models:
    - Unit: C1 encoding unit
    - Syllable: C2a syllable structure
    - WordForm: C2b→C3 morphology-syntax bridge
    - Link: Syntactic link between words
    - Evidence: Semantic evidence weights
    - ProofArtifact: Coq proof attachment
    - AnalysisResult: Complete pipeline output

Usage:
    >>> from app.models import WordForm, Link, AnalysisResult
    >>> wf = WordForm(word_id=0, surface="كتاب", bare="كتاب", pos="noun", span=...)
    >>> result = AnalysisResult(input="test", c1=..., c2a=..., stats=...)

Author: Hussein Hiyassat
Version: 0.1.0 (Sprint 1, Task 1.3)
"""

from .unit import Unit
from .syllable import Syllable
from .word_form import (
    WordForm,
    PartOfSpeech,
    Case,
    Number,
    Gender,
    Span,
    Root,
    Pattern,
)
from .link import Link, LinkType
from .evidence import Evidence, RealityLink
from .proof_artifact import ProofArtifact, ProofStatus
from .analysis_result import (
    AnalysisResult,
    C1Result,
    C2aResult,
    C2bResult,
    SyntaxResult,
    Stats,
)

__all__ = [
    # Core models
    "Unit",
    "Syllable",
    "WordForm",
    "Link",
    "Evidence",
    "ProofArtifact",
    "AnalysisResult",
    # WordForm components
    "PartOfSpeech",
    "Case",
    "Number",
    "Gender",
    "Span",
    "Root",
    "Pattern",
    # Link components
    "LinkType",
    # Evidence components
    "RealityLink",
    # Proof components
    "ProofStatus",
    # Result components
    "C1Result",
    "C2aResult",
    "C2bResult",
    "SyntaxResult",
    "Stats",
]

__version__ = "0.1.0"
