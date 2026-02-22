"""
Pydantic model for syntactic links

Represents a syntactic dependency or relation between words.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum


class LinkType(str, Enum):
    """Types of syntactic links"""
    ISNADI = "isnadi"          # مبتدأ-خبر (Subject-predicate)
    TADMINI = "tadmini"        # فعل متعدٍّ-مفعول (Transitive verb-object)
    TAQYIDI = "taqyidi"        # اسم-صفة أو إضافة (Noun-adjective/idafa)
    UNKNOWN = "unknown"


class Link(BaseModel):
    """
    Syntactic link between two words
    
    Attributes:
        link_type: Type of link (ISNADI, TADMINI, TAQYIDI)
        head_id: ID of head word (مبتدأ, فعل, موصوف)
        dependent_id: ID of dependent word (خبر, مفعول, صفة)
        confidence: Confidence score [0.0, 1.0]
        reason: Explanation for this link
        metadata: Additional link information
    
    Examples:
        >>> link = Link(
        ...     link_type=LinkType.ISNADI,
        ...     head_id=0,
        ...     dependent_id=1,
        ...     confidence=1.0,
        ...     reason="Case agreement, number agreement"
        ... )
        >>> link.link_type
        <LinkType.ISNADI: 'isnadi'>
    """
    
    link_type: LinkType = Field(..., description="Type of syntactic link")
    head_id: int = Field(..., ge=0, description="Head word ID")
    dependent_id: int = Field(..., ge=0, description="Dependent word ID")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    reason: Optional[str] = Field(default=None, description="Explanation for link")
    metadata: Optional[dict] = Field(default=None, description="Additional info")

    model_config = ConfigDict(
        use_enum_values=False,
        json_schema_extra={
            "example": {
                "link_type": "isnadi",
                "head_id": 0,
                "dependent_id": 1,
                "confidence": 1.0,
                "reason": "ISNADI: case agreement, number agreement",
                "metadata": {"checked_gender": True}
            }
        }
    )
