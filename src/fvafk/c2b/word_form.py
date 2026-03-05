"""
WordForm (C2b → Syntax bridge).

This module defines a stable, syntax-ready representation of a token that
collects the outputs of the current C2b pipeline (Plan A) into one object.

Design goals:
- Keep it JSON-friendly (dataclasses with simple fields)
- Do not block the current pipeline (validation is best-effort)
- Provide a stable interface for the upcoming Syntax layer (ISNADI/TADMINI/TAQYIDI)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import unicodedata
from typing import Any, Dict, List, Optional, Tuple


def strip_diacritics(text: str) -> str:
    """Return NFC text without combining marks (harakat/tanwin/etc.)."""
    return "".join(
        ch for ch in unicodedata.normalize("NFC", text)
        if unicodedata.combining(ch) == 0
    ).replace("ـ", "").strip()


class PartOfSpeech(str, Enum):
    OPERATOR = "operator"
    PARTICLE = "particle"
    DEMONSTRATIVE = "demonstrative"
    NAME = "name"
    PRONOUN = "pronoun"
    NOUN = "noun"
    VERB = "verb"
    UNKNOWN = "unknown"


class Case(str, Enum):
    NOMINATIVE = "nominative"
    ACCUSATIVE = "accusative"
    GENITIVE = "genitive"
    ACCUSATIVE_OR_GENITIVE = "accusative_or_genitive"
    UNKNOWN = "unknown"


class Number(str, Enum):
    SINGULAR = "singular"
    DUAL = "dual"
    PLURAL = "plural"
    UNKNOWN = "unknown"


class Gender(str, Enum):
    MASCULINE = "masculine"
    FEMININE = "feminine"
    UNKNOWN = "unknown"


class SyntaxRole(str, Enum):
    # V1 placeholders; the syntax layer will assign these.
    MUBTADA = "mubtada"
    KHABAR = "khabar"
    FAEL = "fael"
    MAFUL = "maful"
    NAAT = "naat"
    MUDHAF_ILAYH = "mudhaf_ilayh"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Span:
    start: int
    end: int  # end-exclusive


@dataclass(frozen=True)
class RootInfo:
    letters: Tuple[str, ...]
    formatted: str
    root_type: str
    length: int


@dataclass(frozen=True)
class PatternInfo:
    template: Optional[str]
    pattern_type: str
    category: str
    stem: Optional[str] = None
    features: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Affixes:
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    normalized: Optional[str] = None
    stripped: Optional[str] = None


@dataclass(frozen=True)
class Dependency:
    """V1 placeholder for syntax relations (to be populated later)."""
    rel: str
    head_index: int
    dep_index: int


@dataclass(frozen=True)
class WordForm:
    """
    A syntax-ready representation of a single token.

    Fields are intentionally conservative: if C2b does not know something, the
    value is None/UNKNOWN rather than guessed aggressively.
    """

    surface: str
    bare: str
    kind: str
    pos: PartOfSpeech

    span: Optional[Span] = None

    root: Optional[RootInfo] = None
    pattern: Optional[PatternInfo] = None
    affixes: Optional[Affixes] = None

    # Raw C2b features dict (Plan A / V1 heuristics)
    features: Dict[str, Any] = field(default_factory=dict)

    # Closed-class payloads (when applicable)
    operator: Optional[Dict[str, Any]] = None
    particle: Optional[Dict[str, Any]] = None
    demonstrative: Optional[Dict[str, Any]] = None
    name: Optional[Dict[str, Any]] = None
    pronoun: Optional[Dict[str, Any]] = None

    # Syntax layer outputs (future)
    case: Optional[Case] = None
    definiteness: Optional[bool] = None
    number: Optional[Number] = None
    gender: Optional[Gender] = None
    syntax_role: Optional[SyntaxRole] = None
    dependencies: List[Dependency] = field(default_factory=list)

