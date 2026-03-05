"""
Unit model for C1 encoding.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class UnitCategory(Enum):
    LETTER = auto()
    DIAC = auto()


@dataclass
class Unit:
    text: str
    category: Optional[UnitCategory] = None
