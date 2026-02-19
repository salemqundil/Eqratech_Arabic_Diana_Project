"""
Pydantic model for syllable structure (C2a layer)

Represents a syllable in Arabic phonology with CV pattern.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class Syllable(BaseModel):
    """
    Syllable structure from C2a phonology layer
    
    Attributes:
        pattern: CV pattern (CV, CVV, CVC)
        units: List of unit indices comprising this syllable
        start: Starting position in text
        end: Ending position in text
        weight: Syllable weight (light, heavy, superheavy)
        stress: Whether this syllable carries stress
        metadata: Optional phonological features
    
    Examples:
        >>> syll = Syllable(
        ...     pattern="CVC",
        ...     units=[0, 1, 2],
        ...     start=0,
        ...     end=3,
        ...     weight="heavy"
        ... )
        >>> syll.pattern
        'CVC'
    """
    
    pattern: str = Field(..., description="CV pattern: CV, CVV, or CVC")
    units: List[int] = Field(..., description="Unit indices in this syllable")
    start: int = Field(..., ge=0, description="Start position in text")
    end: int = Field(..., ge=0, description="End position in text")
    weight: str = Field(default="light", description="Syllable weight: light, heavy, superheavy")
    stress: bool = Field(default=False, description="Whether syllable is stressed")
    metadata: Optional[dict] = Field(default=None, description="Phonological features")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pattern": "CVC",
                "units": [0, 1, 2],
                "start": 0,
                "end": 3,
                "weight": "heavy",
                "stress": False,
                "metadata": {"open": False}
            }
        }
