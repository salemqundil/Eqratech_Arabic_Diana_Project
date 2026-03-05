"""
Pydantic model for complete pipeline analysis result

Represents the complete output from FVAFK pipeline: C1 → C2a → C2b → C3.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

from .unit import Unit
from .syllable import Syllable
from .word_form import WordForm
from .link import Link
from .evidence import Evidence
from .proof_artifact import ProofArtifact


class C1Result(BaseModel):
    """C1 (Encoding) layer result"""
    num_units: int = Field(..., ge=0, description="Number of units")
    units: Optional[List[Unit]] = Field(default=None, description="List of units (if verbose)")


class C2aResult(BaseModel):
    """C2a (Phonology) layer result"""
    syllables: List[Syllable] = Field(default_factory=list, description="Syllables")
    gates: List[Dict[str, Any]] = Field(default_factory=list, description="Gate results")
    cv_pattern: Optional[str] = Field(default=None, description="Overall CV pattern")


class C2bResult(BaseModel):
    """C2b (Morphology) layer result"""
    words_count: int = Field(..., ge=0, description="Number of words analyzed")
    words: List[Dict[str, Any]] = Field(default_factory=list, description="Morphological analysis per word")


class SyntaxResult(BaseModel):
    """Syntax (C3) layer result"""
    word_forms: List[WordForm] = Field(default_factory=list, description="WordForm objects")
    links: Dict[str, List[Link]] = Field(default_factory=dict, description="Syntactic links by type")
    evidence: Optional[List[Evidence]] = Field(default=None, description="Evidence for links")


class Stats(BaseModel):
    """Performance statistics"""
    c1_time_ms: float = Field(..., ge=0, description="C1 execution time (ms)")
    c2a_time_ms: float = Field(..., ge=0, description="C2a execution time (ms)")
    c2b_time_ms: Optional[float] = Field(default=None, ge=0, description="C2b execution time (ms)")
    total_time_ms: float = Field(..., ge=0, description="Total pipeline time (ms)")
    gates_count: int = Field(..., ge=0, description="Number of gates executed")


class AnalysisResult(BaseModel):
    """
    Complete FVAFK pipeline analysis result
    
    Contains results from all layers: C1, C2a, C2b (optional), Syntax (optional),
    plus performance stats and optional proof artifacts.
    
    Attributes:
        input: Original input text
        c1: C1 (encoding) result
        c2a: C2a (phonology) result
        c2b: C2b (morphology) result (optional, requires --morphology)
        syntax: Syntax result (optional, requires --morphology)
        stats: Performance statistics
        proof_artifacts: Optional Coq proof artifacts (strict assurance mode)
        metadata: Additional metadata
    
    Examples:
        >>> result = AnalysisResult(
        ...     input="كِتَابٌ",
        ...     c1=C1Result(num_units=5),
        ...     c2a=C2aResult(syllables=[], gates=[]),
        ...     stats=Stats(
        ...         c1_time_ms=1.2,
        ...         c2a_time_ms=10.5,
        ...         total_time_ms=11.7,
        ...         gates_count=11
        ...     )
        ... )
        >>> result.input
        'كِتَابٌ'
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "input": "مُحَمَّدٌ رَسُولُ اللَّهِ",
                "c1": {"num_units": 23},
                "c2a": {
                    "syllables": [],
                    "gates": [],
                    "cv_pattern": "CV-CVC-CVC",
                },
                "c2b": {
                    "words_count": 3,
                    "words": [],
                },
                "syntax": {
                    "word_forms": [],
                    "links": {"isnadi": []},
                },
                "stats": {
                    "c1_time_ms": 3.5,
                    "c2a_time_ms": 18.2,
                    "c2b_time_ms": 12.8,
                    "total_time_ms": 34.5,
                    "gates_count": 11,
                },
            }
        }
    )

    input: str = Field(..., description="Original input text")
    c1: C1Result = Field(..., description="C1 encoding result")
    c2a: C2aResult = Field(..., description="C2a phonology result")
    c2b: Optional[C2bResult] = Field(default=None, description="C2b morphology result")
    syntax: Optional[SyntaxResult] = Field(default=None, description="Syntax result")
    stats: Stats = Field(..., description="Performance statistics")
    proof_artifacts: Optional[List[ProofArtifact]] = Field(default=None, description="Coq proof artifacts")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
