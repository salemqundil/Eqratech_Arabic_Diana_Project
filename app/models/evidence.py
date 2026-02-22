"""
Pydantic model for evidence weights

Represents evidence supporting an analysis decision, with semantic gates integration.
"""

from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class RealityLink(BaseModel):
    """Link to reality/corpus evidence"""
    reference: str = Field(..., description="Reference to source (corpus, lexicon, etc.)")
    weight: float = Field(..., ge=0.0, le=1.0, description="Evidence weight")
    verified: bool = Field(default=False, description="Whether verified")


class Evidence(BaseModel):
    """
    Evidence for an analysis decision
    
    Used by semantic gates to evaluate truth, scope, and falsifiability.
    
    Attributes:
        score: Overall evidence score [0.0, 1.0]
        scope_ok: Whether scope constraints are satisfied
        truth_ok: Whether truth conditions are met
        reference_ok: Whether references are valid
        reality_links: Links to corpus/lexicon evidence
        notes: Explanation of evidence
        metadata: Additional evidence data
    
    Examples:
        >>> evidence = Evidence(
        ...     score=0.85,
        ...     scope_ok=True,
        ...     truth_ok=True,
        ...     reference_ok=True,
        ...     reality_links=[
        ...         RealityLink(reference="Quran 1:1", weight=1.0, verified=True)
        ...     ],
        ...     notes="Strong corpus evidence"
        ... )
        >>> evidence.score
        0.85
    """
    
    score: float = Field(..., ge=0.0, le=1.0, description="Overall evidence score")
    scope_ok: bool = Field(default=True, description="Scope constraints satisfied")
    truth_ok: bool = Field(default=True, description="Truth conditions met")
    reference_ok: bool = Field(default=True, description="References valid")
    reality_links: List[RealityLink] = Field(default_factory=list, description="Corpus/lexicon links")
    notes: Optional[str] = Field(default=None, description="Evidence explanation")
    metadata: Optional[dict] = Field(default=None, description="Additional data")

    def is_acceptable(self, threshold: float = 0.5) -> bool:
        """Check if evidence meets acceptance criteria"""
        return (
            self.score >= threshold
            and self.scope_ok
            and self.truth_ok
            and self.reference_ok
        )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "score": 0.85,
                "scope_ok": True,
                "truth_ok": True,
                "reference_ok": True,
                "reality_links": [
                    {
                        "reference": "Quran 1:1",
                        "weight": 1.0,
                        "verified": True
                    }
                ],
                "notes": "Strong corpus evidence from classical texts"
            }
        }
    )
