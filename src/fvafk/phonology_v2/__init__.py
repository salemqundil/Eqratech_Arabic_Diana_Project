"""
FVAFK Phonology V2
==================

Context-driven VC classification for Arabic syllabification (Assumption A):
و/ي/ا are consonants by default and only become V_LONG when syllable structure
proves they must be nuclei.

This package was copied from the external phonology prototype and integrated
under `fvafk.phonology_v2`.
"""

__version__ = "2.0.0"

# Core types
from .phonology_types import (  # noqa: F401
    Grapheme,
    Segment,
    SegKind,
    Diacritic,
    CVRole,
    VCWitness,
    VCDecision,
    VcTrace,
    SyllableType,
    SyllableWeight,
    SyllableCandidate,
    SyllableLattice,
    WordAnalysis,
    MatchTrace,
)

# VC classification
from .phonology_vc_classify import (  # noqa: F401
    vc_classify,
    vc_classify_sequence,
    validate_vc_decision,
    explain_vc_decision,
)

# Lattice building
from .phonology_lattice import (  # noqa: F401
    build_syllable_lattice_v2,
    find_best_syllabification,
)

# Utilities
from .phonology_utils import (  # noqa: F401
    text_to_graphemes,
    segments_to_cv,
    segments_to_detailed_cv,
    syllables_to_cv_pattern,
    format_syllable,
    format_syllabification,
    print_vc_witnesses,
    print_lattice_summary,
    debug_graphemes,
    debug_segments,
    debug_syllable_candidate,
    validate_syllabification,
    compute_syllabification_stats,
)

__all__ = [
    "Grapheme",
    "Segment",
    "SegKind",
    "Diacritic",
    "CVRole",
    "VCWitness",
    "VCDecision",
    "VcTrace",
    "SyllableType",
    "SyllableWeight",
    "SyllableCandidate",
    "SyllableLattice",
    "WordAnalysis",
    "MatchTrace",
    "vc_classify",
    "vc_classify_sequence",
    "build_syllable_lattice_v2",
    "find_best_syllabification",
    "text_to_graphemes",
    "syllables_to_cv_pattern",
    "segments_to_cv",
    "segments_to_detailed_cv",
    "format_syllabification",
    "print_vc_witnesses",
    "validate_syllabification",
    "analyze_word",
    "PhonologyV2Adapter",
]


def analyze_word(text: str, verbose: bool = False) -> WordAnalysis:
    """
    High-level API: analyze a single (diacritized) Arabic word with Phonology V2.

    Returns a `WordAnalysis` object containing:
    - parsed `graphemes`
    - a `SyllableLattice` of candidates
    - `best_syllabification` (best path), if any
    - `cv_pattern` (e.g. `CVCVVC`)
    - `all_vc_traces` (witnesses/decision traces for VC classification)

    When `verbose=True`, additional debugging summaries are printed to stdout.
    """
    graphemes = text_to_graphemes(text)
    if verbose:
        debug_graphemes(graphemes)

    lattice = build_syllable_lattice_v2(graphemes)
    if verbose:
        print_lattice_summary(lattice)

    best_path = find_best_syllabification(lattice)
    if not best_path:
        return WordAnalysis(
            original_text=text,
            graphemes=graphemes,
            lattice=lattice,
            best_syllabification=None,
            cv_pattern=None,
            segments=[],
            all_vc_traces=[],
        )

    cv_pattern = syllables_to_cv_pattern(best_path)
    segments = []
    all_traces = []
    for syl in best_path:
        segments.extend(syl.onset)
        segments.append(syl.nucleus)
        segments.extend(syl.coda)
        all_traces.extend(syl.vc_witnesses)

    if verbose:
        print(f"\nSyllabification: {format_syllabification(best_path)}")
        print(f"CV Pattern: {cv_pattern}")
        print_vc_witnesses(best_path)

    return WordAnalysis(
        original_text=text,
        graphemes=graphemes,
        lattice=lattice,
        best_syllabification=best_path,
        cv_pattern=cv_pattern,
        segments=segments,
        all_vc_traces=all_traces,
    )


# Adapter imported last to avoid circular imports:
# phonology_adapter.py imports analyze_word from this module.
from .phonology_adapter import PhonologyV2Adapter  # noqa: F401

