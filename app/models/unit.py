"""
Pydantic model for encoding unit (C1 layer)

Represents a single unit in the encoded form, typically a character or character sequence.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class Unit(BaseModel):
    """
    Encoding unit from C1 layer
    
    Attributes:
        text: The Unicode text of the unit
        category: Category classification (LETTER, DIACRITIC, SPACE, etc.)
        index: Position in the original input
        metadata: Optional additional information
    
    Examples:
        >>> unit = Unit(text="ك", category="LETTER", index=0)
        >>> unit.text
        'ك'
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "ك",
                "category": "LETTER",
                "index": 0,
                "metadata": {"normalized": True},
            }
        }
    )

    text: str = Field(..., description="Unicode text of the unit")
    category: str = Field(..., description="Category: LETTER, DIACRITIC, SPACE, etc.")
    index: int = Field(..., ge=0, description="Position in original input (0-indexed)")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata")
