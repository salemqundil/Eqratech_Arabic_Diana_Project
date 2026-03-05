"""
Syntax Features - high-level syntax features for WordForm integration.

Author: Hussein Hiyassat
Date: 2026-02-21
Sprint: 4 - Task 4.2
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SyntaxFeatures:
    """
    High-level syntax features for WordForm integration.

    Attributes:
        syntactic_role: English syntactic role, e.g. "subject", "predicate".
        case: Grammatical case: "nominative", "accusative", "genitive".
        i3rab_type_ar: Arabic I3rab type label, e.g. "مبتدأ".
        i3rab_type_en: English I3rab type label, e.g. "mubtada".
        confidence: Confidence score [0.0, 1.0].
        warning: Optional warning message for low-confidence predictions.

    Examples:
        >>> feat = SyntaxFeatures(
        ...     syntactic_role="subject",
        ...     case="nominative",
        ...     i3rab_type_ar="مبتدأ",
        ...     i3rab_type_en="mubtada",
        ...     confidence=0.85,
        ... )
        >>> feat.syntactic_role
        'subject'
        >>> feat.warning is None
        True
    """

    syntactic_role: str
    case: str
    i3rab_type_ar: str
    i3rab_type_en: str
    confidence: float
    warning: Optional[str] = None

    def __post_init__(self):
        if self.confidence < 0.5 and self.warning is None:
            self.warning = "Low confidence - verify manually"
