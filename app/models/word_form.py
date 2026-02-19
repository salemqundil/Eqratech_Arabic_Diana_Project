"""
Pydantic model for WordForm (C2b→C3 bridge)

Represents a word with all its morphological and syntactic features.
"""

from typing import Optional, Tuple
from pydantic import BaseModel, Field
from enum import Enum


class PartOfSpeech(str, Enum):
    """Part of speech tags"""
    NOUN = "noun"
    VERB = "verb"
    PARTICLE = "particle"
    PRONOUN = "pronoun"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    UNKNOWN = "unknown"


class Case(str, Enum):
    """Grammatical case (إعراب)"""
    NOMINATIVE = "nominative"  # مرفوع
    ACCUSATIVE = "accusative"  # منصوب
    GENITIVE = "genitive"      # مجرور
    UNKNOWN = "unknown"


class Number(str, Enum):
    """Grammatical number"""
    SINGULAR = "singular"  # مفرد
    DUAL = "dual"          # مثنى
    PLURAL = "plural"      # جمع
    UNKNOWN = "unknown"


class Gender(str, Enum):
    """Grammatical gender"""
    MASCULINE = "masculine"  # مذكر
    FEMININE = "feminine"    # مؤنث
    UNKNOWN = "unknown"


class Span(BaseModel):
    """Text span"""
    start: int = Field(..., ge=0)
    end: int = Field(..., ge=0)


class Root(BaseModel):
    """Morphological root"""
    letters: Tuple[str, ...] = Field(..., description="Root letters")
    formatted: str = Field(..., description="Formatted root (e.g., 'ك ت ب')")
    type: str = Field(default="triliteral", description="Root type")


class Pattern(BaseModel):
    """Morphological pattern"""
    template: str = Field(..., description="Pattern template (e.g., 'فِعَال')")
    type: str = Field(..., description="Pattern type")
    category: str = Field(default="unknown", description="Pattern category")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class WordForm(BaseModel):
    """
    WordForm: Bridge between morphology (C2b) and syntax (C3)
    
    Attributes:
        word_id: Unique identifier in sentence
        surface: Surface form as it appears
        bare: Bare form (without diacritics)
        pos: Part of speech
        span: Text span (start, end)
        case: Grammatical case
        number: Grammatical number
        gender: Grammatical gender
        definiteness: Whether word is definite
        root: Morphological root
        pattern: Morphological pattern
        metadata: Additional features
    
    Examples:
        >>> wf = WordForm(
        ...     word_id=0,
        ...     surface="الْكِتَابُ",
        ...     bare="الكتاب",
        ...     pos=PartOfSpeech.NOUN,
        ...     span=Span(start=0, end=10),
        ...     case=Case.NOMINATIVE,
        ...     number=Number.SINGULAR,
        ...     gender=Gender.MASCULINE,
        ...     definiteness=True
        ... )
        >>> wf.pos
        <PartOfSpeech.NOUN: 'noun'>
    """
    
    word_id: int = Field(..., ge=0, description="Unique word ID in sentence")
    surface: str = Field(..., description="Surface form with diacritics")
    bare: str = Field(..., description="Bare form (no diacritics)")
    pos: PartOfSpeech = Field(..., description="Part of speech")
    span: Span = Field(..., description="Text span")
    case: Optional[Case] = Field(default=None, description="Grammatical case")
    number: Optional[Number] = Field(default=None, description="Grammatical number")
    gender: Optional[Gender] = Field(default=None, description="Grammatical gender")
    definiteness: bool = Field(default=False, description="Is definite (has ال)")
    root: Optional[Root] = Field(default=None, description="Morphological root")
    pattern: Optional[Pattern] = Field(default=None, description="Morphological pattern")
    metadata: Optional[dict] = Field(default=None, description="Additional features")
    
    class Config:
        use_enum_values = False  # Keep enum objects
        json_schema_extra = {
            "example": {
                "word_id": 0,
                "surface": "الْكِتَابُ",
                "bare": "الكتاب",
                "pos": "noun",
                "span": {"start": 0, "end": 10},
                "case": "nominative",
                "number": "singular",
                "gender": "masculine",
                "definiteness": True,
                "root": {
                    "letters": ["ك", "ت", "ب"],
                    "formatted": "ك ت ب",
                    "type": "triliteral"
                },
                "pattern": {
                    "template": "فِعَال",
                    "type": "form_i",
                    "category": "noun",
                    "confidence": 1.0
                }
            }
        }
