"""
Syntactic Link: Represents syntactic relations between words

This module defines the Link class which represents directed syntactic
relations between WordForm instances.

Author: Hussein Hiyassat
Date: 2025-02-13
Version: 1.0
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class LinkType(Enum):
    """Types of syntactic links"""
    ISNADI = "isnadi"              # إسنادي: مبتدأ ← خبر
    TADMINI = "tadmini"            # تضميني: فعل ← فاعل/مفعول
    TAQYIDI = "taqyidi"            # تقييدي: موصوف ← صفة
    IDAFA = "idafa"                # إضافة: مضاف ← مضاف إليه
    UNKNOWN = "unknown"
    
    def __str__(self):
        return self.value
    
    @property
    def arabic(self) -> str:
        """Get Arabic name"""
        mapping = {
            LinkType.ISNADI: "إسنادي",
            LinkType.TADMINI: "تضميني",
            LinkType.TAQYIDI: "تقييدي",
            LinkType.IDAFA: "إضافة",
            LinkType.UNKNOWN: "غير معروف"
        }
        return mapping[self]


@dataclass
class Link:
    """
    Represents a directed syntactic link between two words
    
    A Link connects a head (governor) to a dependent, with a specific
    syntactic relation type.
    
    Attributes:
        link_type: Type of syntactic relation
        head_id: ID of the head/governor word
        dependent_id: ID of the dependent word
        confidence: Confidence score (0.0 to 1.0)
        reason: Human-readable explanation
    
    Examples:
        >>> # المبتدأ (head) ← الخبر (dependent)
        >>> link = Link(
        ...     link_type=LinkType.ISNADI,
        ...     head_id=0,  # الكتاب
        ...     dependent_id=1,  # مفيد
        ...     confidence=0.95,
        ...     reason="مبتدأ + خبر with case agreement"
        ... )
        >>> print(link.link_type.arabic)
        إسنادي
    """
    
    link_type: LinkType
    head_id: int
    dependent_id: int
    confidence: float = 1.0
    reason: Optional[str] = None
    
    def __post_init__(self):
        """Validate after initialization"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        
        if self.head_id == self.dependent_id:
            raise ValueError("Head and dependent cannot be the same word")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'link_type': str(self.link_type),
            'link_type_arabic': self.link_type.arabic,
            'head_id': self.head_id,
            'dependent_id': self.dependent_id,
            'confidence': self.confidence,
            'reason': self.reason
        }
    
    def __str__(self):
        return f"Link({self.link_type.arabic}: {self.head_id} ← {self.dependent_id})"
    
    def __repr__(self):
        return f"Link(type={self.link_type}, head={self.head_id}, dep={self.dependent_id}, conf={self.confidence:.2f})"
