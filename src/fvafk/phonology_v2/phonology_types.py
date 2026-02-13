"""
FVAFK Phonology System - Type Definitions
==========================================

All core types for VC classification and syllable lattice building.
Author: Hussein (FVAFK Project)
Date: 2025-02-09
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, List, Set, Dict, Tuple


# ============================================================================
# VC Classification Types
# ============================================================================

class VCWitness(Enum):
    """
    Witness/proof for why a grapheme was classified as consonant or vowel.
    Each classification decision must be justified.
    """
    SHORT_ON_SELF = auto()              # Has short vowel diacritic (َ ُ ِ)
    LONG_BY_NUCLEUS_NEED = auto()       # Syllable proves it needs this as nucleus
    FORCED_CONSONANT_BY_ONSET = auto()  # Onset constraint prevents vowel interpretation
    HAMZA_ALWAYS_CONSONANT = auto()     # Hamza is always consonant sound
    HAMZA_SEAT_ONLY = auto()            # Seat carrier (أإؤئ) without being nucleus
    DEFAULT_CONSONANT = auto()          # Default: و/ي/ا are consonants (assumption A)


class CVRole(Enum):
    """
    The role a grapheme plays in syllable structure.
    """
    C = auto()           # Consonant
    V_SHORT = auto()     # Short vowel (fatha/damma/kasra)
    V_LONG = auto()      # Long vowel (alif/waw/yaa as nucleus)
    HAMZA_C = auto()     # Hamza as consonant
    HAMZA_SEAT = auto()  # Hamza seat carrier (أإؤئ)


class SegKind(Enum):
    """
    Segment kind in the output sequence.
    """
    C = auto()           # Consonant
    V_SHORT = auto()     # Short vowel
    V_LONG = auto()      # Long vowel


class Diacritic(Enum):
    """
    Arabic diacritical marks (harakat and tanwin).
    """
    FATHA = "َ"          # Fatha (a)
    DAMMA = "ُ"          # Damma (u)
    KASRA = "ِ"          # Kasra (i)
    SUKUN = "ْ"          # Sukun (no vowel)
    SHADDA = "ّ"         # Shadda (gemination)
    TANWIN_FATH = "ً"    # Tanwin fath (an)
    TANWIN_DAMM = "ٌ"    # Tanwin damm (un)
    TANWIN_KASR = "ٍ"    # Tanwin kasr (in)
    MADDA = "ٓ"          # Madda (over alif)
    HAMZA_ABOVE = "ٔ"    # Hamza above
    HAMZA_BELOW = "ٕ"    # Hamza below


# ============================================================================
# Input/Output Types
# ============================================================================

@dataclass(frozen=True)
class Grapheme:
    """
    A single Arabic grapheme (base character + diacritics).
    """
    base_char: str                           # Base character (ك، ت، ا، etc.)
    diacs: Set[Diacritic] = field(default_factory=set)  # Diacritics on this grapheme
    position: int = 0                        # Position in word


@dataclass(frozen=True)
class Segment:
    """
    A segment in the phonological representation (C or V).
    """
    kind: SegKind                            # C, V_SHORT, or V_LONG
    surface: str                             # Surface form (character)
    span: Tuple[int, int]                    # (start_grapheme_idx, end_grapheme_idx)


@dataclass(frozen=True)
class VCDecision:
    """
    Result of VC classification for a single grapheme.
    """
    role: CVRole                             # What role this grapheme plays
    surface: str                             # Surface representation
    witness: VCWitness                       # Proof/justification for this decision


@dataclass
class VcTrace:
    """
    Trace record for VC classification decision (for debugging).
    """
    grapheme_index: int                      # Index in grapheme sequence
    base: str                                # Base character
    need_nucleus: bool                       # Was nucleus needed at this position?
    force_onset_c: bool                      # Was consonant forced by onset constraint?
    decided_role: CVRole                     # Final decision
    surface: str                             # Surface form
    witness: VCWitness                       # Witness/proof


# ============================================================================
# Syllable Types
# ============================================================================

class SyllableType(Enum):
    """
    Arabic syllable types (CV patterns).
    """
    CV = auto()      # قَ (qa)
    CVC = auto()     # قَدْ (qad)
    CVV = auto()     # قَا (qaa)
    CVVC = auto()    # قَالْ (qaal)
    CVCC = auto()    # قَلْبْ (qalb) - rare, usually word-final


class SyllableWeight(Enum):
    """
    Syllable weight (for prosody/metrics).
    """
    LIGHT = auto()       # CV
    HEAVY = auto()       # CVC, CVV
    SUPERHEAVY = auto()  # CVVC, CVCC


@dataclass
class SyllableCandidate:
    """
    A potential syllable in the lattice.
    """
    onset: List[Segment]                     # C or CC (rare in Arabic)
    nucleus: Segment                         # V_SHORT or V_LONG
    coda: List[Segment]                      # [], [C], or [C,C]
    span: Tuple[int, int]                    # Grapheme indices (start, end)
    syl_type: SyllableType                   # CV, CVC, CVV, CVVC, CVCC
    weight: SyllableWeight                   # LIGHT, HEAVY, SUPERHEAVY
    score: float = 0.0                       # Preference score
    vc_witnesses: List[VcTrace] = field(default_factory=list)  # VC decisions for this syllable


@dataclass
class SyllableLattice:
    """
    Complete lattice of all possible syllabifications for a word.
    """
    candidates: List[SyllableCandidate]      # All syllable candidates
    grapheme_count: int                      # Total graphemes in input
    # Map: (start_pos, end_pos) -> [candidate_indices]
    position_map: Dict[Tuple[int, int], List[int]] = field(default_factory=dict)


# ============================================================================
# Analysis Results
# ============================================================================

@dataclass
class WordAnalysis:
    """
    Complete phonological analysis of a word.
    """
    original_text: str                       # Original Arabic text
    graphemes: List[Grapheme]                # Parsed graphemes
    lattice: SyllableLattice                 # Full syllable lattice
    best_syllabification: Optional[List[SyllableCandidate]]  # Best path through lattice
    cv_pattern: Optional[str]                # Final CV pattern string
    segments: List[Segment]                  # Final segment sequence
    all_vc_traces: List[VcTrace]             # All VC classification decisions


@dataclass
class MatchTrace:
    """
    Trace for pattern matching (debugging).
    """
    word: str
    graphemes: List[Grapheme]
    lattice: SyllableLattice
    best_path: Optional[List[SyllableCandidate]]
    cv_pattern: Optional[str]
    match_result: bool
    failure_reason: Optional[str] = None


# ============================================================================
# Phonological Operation Types (for future expansion)
# ============================================================================

class PhonoOp(Enum):
    """
    Phonological operations that can be applied.
    """
    RESOLVE_TWO_SUKUN = auto()   # التقاء ساكنين
    ASSIMILATE = auto()          # إدغام
    WAQF_END = auto()            # Pause form
    CASE_LETTER_END = auto()     # Case endings


class WordPosition(Enum):
    """
    Position of word in utterance (affects phonological rules).
    """
    INITIAL = auto()
    MEDIAL = auto()
    FINAL = auto()
    ISOLATED = auto()


# ============================================================================
# Utility Functions
# ============================================================================

def diacritic_from_char(char: str) -> Optional[Diacritic]:
    """
    Convert a character to Diacritic enum if it's a diacritic.
    """
    diac_map = {
        "َ": Diacritic.FATHA,
        "ُ": Diacritic.DAMMA,
        "ِ": Diacritic.KASRA,
        "ْ": Diacritic.SUKUN,
        "ّ": Diacritic.SHADDA,
        "ً": Diacritic.TANWIN_FATH,
        "ٌ": Diacritic.TANWIN_DAMM,
        "ٍ": Diacritic.TANWIN_KASR,
        "ٓ": Diacritic.MADDA,
        "ٔ": Diacritic.HAMZA_ABOVE,
        "ٕ": Diacritic.HAMZA_BELOW,
    }
    return diac_map.get(char)


def is_diacritic(char: str) -> bool:
    """
    Check if a character is a diacritic.
    """
    return diacritic_from_char(char) is not None
