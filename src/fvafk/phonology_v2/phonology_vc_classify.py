"""
FVAFK Phonology System - VC Classification
===========================================

Core algorithm for classifying graphemes as consonants or vowels.

Key Innovation: و/ي/ا are CONSONANTS by default (assumption A).
They only become LONG VOWELS when the syllable structure PROVES they must be nuclei.

This solves the fundamental ambiguity problem in Arabic phonology.

Author: Hussein (FVAFK Project)
Date: 2025-02-09
"""

from typing import Set, Optional

try:
    # Package import (recommended): `python -m fvafk.phonology.test_examples`
    from .phonology_types import CVRole, VCWitness, VCDecision, Diacritic
except ImportError:  # pragma: no cover
    # Local script import: `cd src/fvafk/phonology && python test_examples.py`
    from phonology_types import CVRole, VCWitness, VCDecision, Diacritic


# ============================================================================
# Constants
# ============================================================================

# Hamza forms (all are consonants)
AR_HAMZA_FORMS = {"ء", "أ", "إ", "ؤ", "ئ", "ٱ"}

# Hamza seats (carriers) - these are special
HAMZA_SEATS = {"أ", "إ", "ؤ", "ئ"}

# Letters that can be long vowels (when context allows)
LONG_LETTERS = {"ا", "و", "ي"}

# Alif variants
ALIF_VARIANTS = {"ا", "ٱ", "آ", "أ", "إ"}


# ============================================================================
# Helper Functions
# ============================================================================

def has_short_vowel(diacs: Set[Diacritic]) -> Optional[str]:
    """
    Check if grapheme has a short vowel diacritic.
    
    Returns:
        The vowel character if present, None otherwise.
    """
    if Diacritic.FATHA in diacs:
        return "َ"
    if Diacritic.DAMMA in diacs:
        return "ُ"
    if Diacritic.KASRA in diacs:
        return "ِ"
    return None


def has_sukun(diacs: Set[Diacritic]) -> bool:
    """
    Check if grapheme has sukun (no vowel).
    """
    return Diacritic.SUKUN in diacs


def has_shadda(diacs: Set[Diacritic]) -> bool:
    """
    Check if grapheme has shadda (gemination marker).
    """
    return Diacritic.SHADDA in diacs


def has_tanwin(diacs: Set[Diacritic]) -> bool:
    """
    Check if grapheme has tanwin (nunation).
    """
    return any(d in diacs for d in [
        Diacritic.TANWIN_FATH,
        Diacritic.TANWIN_DAMM,
        Diacritic.TANWIN_KASR
    ])


def is_pure_hamza(base_char: str) -> bool:
    """
    Check if character is pure hamza (ء) vs seat forms.
    """
    return base_char == "ء"


def is_hamza_seat(base_char: str) -> bool:
    """
    Check if character is a hamza seat (أإؤئ).
    """
    return base_char in HAMZA_SEATS


def is_long_letter(base_char: str) -> bool:
    """
    Check if character can be a long vowel (ا و ي).
    """
    return base_char in LONG_LETTERS


# ============================================================================
# Core VC Classification Algorithm
# ============================================================================

def vc_classify(
    base_char: str,
    diacs: Set[Diacritic],
    need_nucleus: bool,
    force_onset_c: bool
) -> VCDecision:
    """
    Classify a grapheme as consonant or vowel based on context.
    
    This is the CORE algorithm that solves the و/ي/ا ambiguity problem.
    
    Algorithm:
    1. Hamza (ء أ إ ؤ ئ) → always CONSONANT
    2. Has short vowel (َ ُ ِ) → V_SHORT
    3. Hamza seat without nucleus need → HAMZA_SEAT
    4. و/ي/ا with nucleus need and no onset constraint → V_LONG
    5. Everything else → CONSONANT (default)
    
    Args:
        base_char: The base Arabic character
        diacs: Set of diacritics on this character
        need_nucleus: Does the syllable structure require a nucleus here?
        force_onset_c: Must this position be consonant due to onset constraints?
    
    Returns:
        VCDecision with role and witness (proof)
    
    Examples:
        >>> # يوم - و is consonant
        >>> vc_classify("و", set(), need_nucleus=False, force_onset_c=False)
        VCDecision(role=CVRole.C, surface="و", witness=VCWitness.DEFAULT_CONSONANT)
        
        >>> # قول - و is long vowel (syllable needs nucleus)
        >>> vc_classify("و", set(), need_nucleus=True, force_onset_c=False)
        VCDecision(role=CVRole.V_LONG, surface="و", witness=VCWitness.LONG_BY_NUCLEUS_NEED)
        
        >>> # كَتَب - ت with fatha is short vowel
        >>> vc_classify("ت", {Diacritic.FATHA}, need_nucleus=False, force_onset_c=False)
        VCDecision(role=CVRole.V_SHORT, surface="َ", witness=VCWitness.SHORT_ON_SELF)
    """
    
    # ========================================================================
    # Rule 1: Hamza is always a consonant (sound)
    # ========================================================================
    if base_char in AR_HAMZA_FORMS:
        return VCDecision(
            role=CVRole.HAMZA_C,
            surface="ء",
            witness=VCWitness.HAMZA_ALWAYS_CONSONANT
        )
    
    # ========================================================================
    # Rule 2: Short vowel on self → V_SHORT
    # ========================================================================
    # If the grapheme has a short vowel diacritic (َ ُ ِ), it represents
    # that short vowel regardless of the base character.
    sv = has_short_vowel(diacs)
    if sv is not None:
        return VCDecision(
            role=CVRole.V_SHORT,
            surface=sv,
            witness=VCWitness.SHORT_ON_SELF
        )
    
    # ========================================================================
    # Rule 3: Hamza seat-only
    # ========================================================================
    # Letters like أ إ ؤ ئ when they're NOT serving as nucleus
    # are just seat carriers, not vowels themselves.
    if is_hamza_seat(base_char):
        return VCDecision(
            role=CVRole.HAMZA_SEAT,
            surface=base_char,
            witness=VCWitness.HAMZA_SEAT_ONLY
        )
    
    # ========================================================================
    # Rule 4: ا/و/ي - context-dependent classification
    # ========================================================================
    # This is the KEY innovation: these letters are consonants by default,
    # and only become long vowels when the syllable structure PROVES
    # they must be nuclei.
    
    if is_long_letter(base_char):
        # Case A: Syllable needs nucleus AND onset not forced
        # → This letter MUST be the nucleus → V_LONG
        if need_nucleus and not force_onset_c:
            return VCDecision(
                role=CVRole.V_LONG,
                surface=base_char,
                witness=VCWitness.LONG_BY_NUCLEUS_NEED
            )
        
        # Case B: Onset constraint forces consonant
        # Even if nucleus is needed, onset constraint overrides
        elif force_onset_c:
            return VCDecision(
                role=CVRole.C,
                surface=base_char,
                witness=VCWitness.FORCED_CONSONANT_BY_ONSET
            )
    
    # ========================================================================
    # Rule 5: Everything else → CONSONANT (default)
    # ========================================================================
    # This includes:
    # - All regular consonants (ب ت ث ج ...)
    # - و/ي/ا when not needed as nucleus
    # - Any character we haven't classified above
    
    return VCDecision(
        role=CVRole.C,
        surface=base_char,
        witness=VCWitness.DEFAULT_CONSONANT
    )


# ============================================================================
# Batch Classification
# ============================================================================

def vc_classify_sequence(
    graphemes,
    need_nucleus_map: dict,
    force_onset_map: dict
) -> list:
    """
    Classify a sequence of graphemes.
    
    Args:
        graphemes: List of Grapheme objects
        need_nucleus_map: Dict[int, bool] - which positions need to be nuclei
        force_onset_map: Dict[int, bool] - which positions must be consonants
    
    Returns:
        List of VCDecision objects
    """
    decisions = []
    
    for i, g in enumerate(graphemes):
        need_nuc = need_nucleus_map.get(i, False)
        force_c = force_onset_map.get(i, False)
        
        dec = vc_classify(g.base_char, g.diacs, need_nuc, force_c)
        decisions.append(dec)
    
    return decisions


# ============================================================================
# Validation Functions
# ============================================================================

def validate_vc_decision(decision: VCDecision) -> bool:
    """
    Validate that a VC decision is consistent.
    
    Checks:
    - Role matches witness
    - Surface form is appropriate for role
    """
    
    # Short vowel should have vowel surface
    if decision.role == CVRole.V_SHORT:
        if decision.surface not in {"َ", "ُ", "ِ"}:
            return False
        if decision.witness != VCWitness.SHORT_ON_SELF:
            return False
    
    # Long vowel should have long letter surface
    if decision.role == CVRole.V_LONG:
        if decision.surface not in LONG_LETTERS:
            return False
        if decision.witness != VCWitness.LONG_BY_NUCLEUS_NEED:
            return False
    
    # Hamza should have hamza witness
    if decision.role == CVRole.HAMZA_C:
        if decision.witness != VCWitness.HAMZA_ALWAYS_CONSONANT:
            return False
    
    return True


# ============================================================================
# Debug/Trace Functions
# ============================================================================

def explain_vc_decision(decision: VCDecision) -> str:
    """
    Generate human-readable explanation of a VC decision.
    """
    explanations = {
        VCWitness.SHORT_ON_SELF: 
            f"Has short vowel diacritic → {decision.surface}",
        VCWitness.LONG_BY_NUCLEUS_NEED: 
            f"Syllable requires nucleus here → {decision.surface} is long vowel",
        VCWitness.FORCED_CONSONANT_BY_ONSET: 
            f"Onset constraint forces consonant → {decision.surface}",
        VCWitness.HAMZA_ALWAYS_CONSONANT: 
            f"Hamza is always consonant → ء",
        VCWitness.HAMZA_SEAT_ONLY: 
            f"Hamza seat (not nucleus) → {decision.surface}",
        VCWitness.DEFAULT_CONSONANT: 
            f"Default classification → {decision.surface} is consonant"
    }
    
    return explanations.get(
        decision.witness,
        f"Unknown witness: {decision.witness}"
    )
