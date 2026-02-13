"""
Basic morphological dataclasses and helpers.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


class RootType(Enum):
    TRILATERAL = auto()
    QUADRILATERAL = auto()


class PatternType(Enum):
    """Types of morphological patterns."""
    UNKNOWN = "unknown"

    # Verb Forms
    FORM_I = "form_i"
    FORM_II = "form_ii"
    FORM_III = "form_iii"
    FORM_IV = "form_iv"
    FORM_V = "form_v"
    FORM_VI = "form_vi"
    FORM_VII = "form_vii"
    FORM_VIII = "form_viii"
    FORM_IX = "form_ix"
    FORM_X = "form_x"

    # Noun Patterns
    ACTIVE_PARTICIPLE = "active_participle"
    PASSIVE_PARTICIPLE = "passive_participle"
    PLACE_TIME_NOUN = "place_time_noun"
    VERBAL_NOUN = "verbal_noun"
    INTENSIVE = "intensive"
    ABSTRACT_NOUN = "abstract_noun"
    INSTRUMENT = "instrument"
    ELATIVE = "elative"

    # Plural Patterns
    SOUND_MASCULINE_PLURAL = "sound_masc_plural"
    SOUND_FEMININE_PLURAL = "sound_fem_plural"
    BROKEN_PLURAL_FUUL = "broken_plural_fuul"
    BROKEN_PLURAL_FIAAL = "broken_plural_fiaal"
    BROKEN_PLURAL_AFAAL = "broken_plural_afaal"
    BROKEN_PLURAL_FIUL = "broken_plural_fiul"
    BROKEN_PLURAL_FU33AL = "broken_plural_fu33al"
    BROKEN_PLURAL_FU3ALAA = "broken_plural_fu3alaa"


class AffixType(Enum):
    PREFIX = auto()
    SUFFIX = auto()
    INFIX = auto()


@dataclass(frozen=True)
class Root:
    letters: Tuple[str, ...]
    root_type: RootType
    weak_positions: Tuple[int, ...] = ()
    has_hamza: bool = False

    def __post_init__(self) -> None:
        if any(len(letter) != 1 for letter in self.letters):
            raise ValueError("Root letters must be single characters")
        if self.root_type == RootType.TRILATERAL and len(self.letters) != 3:
            raise ValueError("Trilateral root must have 3 letters")
        if self.root_type == RootType.QUADRILATERAL and len(self.letters) != 4:
            raise ValueError("Quadrilateral root must have 4 letters")

    @property
    def trilateral(self) -> bool:
        return len(self.letters) == 3

    @property
    def quadrilateral(self) -> bool:
        return len(self.letters) == 4


@dataclass(frozen=True)
class Pattern:
    name: str
    template: str
    pattern_type: PatternType = PatternType.UNKNOWN
    stem: Optional[str] = None
    description: Optional[str] = None
    weight: int = 1
    features: Dict[str, str] = field(default_factory=dict)

    def matches(self, stem: str) -> bool:
        consonants = [ch for ch in stem if ch.isalpha()]
        return len(consonants) >= len([c for c in self.template if c.isalpha()])


@dataclass(frozen=True)
class Affix:
    text: str
    position: str  # "prefix", "suffix", "infix"
    name: Optional[str] = None


@dataclass
class Morpheme:
    root: Root
    pattern: Pattern
    stem: str
    affixes: List[Affix] = field(default_factory=list)
    gloss: Optional[str] = None

    def describe(self) -> str:
        parts = [f"Root: {''.join(self.root.letters)}", f"Pattern: {self.pattern.name}"]
        if self.gloss:
            parts.append(f"Gloss: {self.gloss}")
        if self.affixes:
            parts.append(f"Affixes: {[a.text for a in self.affixes]}")
        return " | ".join(parts)


@dataclass
class MorphologicalAnalysis:
    morpheme: Morpheme
    affix_sequence: List[Affix] = field(default_factory=list)
    meaning_category: Optional[str] = None
    notes: List[str] = field(default_factory=list)

    def summary(self) -> str:
        affixes = "+".join(affix.text for affix in self.affix_sequence)
        return f"{self.morpheme.describe()} | AffixSeq: {affixes or 'none'}"
