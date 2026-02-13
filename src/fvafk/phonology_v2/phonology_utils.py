"""
FVAFK Phonology System - Utilities
===================================

Utility functions for:
- Parsing Arabic text to graphemes
- Converting segments to CV patterns
- Debugging and visualization

Author: Hussein (FVAFK Project)
Date: 2025-02-09
"""

from typing import List, Set

try:
    from .phonology_types import (
        Grapheme,
        Segment,
        SegKind,
        Diacritic,
        SyllableCandidate,
        diacritic_from_char,
        is_diacritic,
    )
except ImportError:  # pragma: no cover
    from phonology_types import (
        Grapheme,
        Segment,
        SegKind,
        Diacritic,
        SyllableCandidate,
        diacritic_from_char,
        is_diacritic,
    )


# ============================================================================
# Arabic Character Constants
# ============================================================================

# Arabic letters (consonants)
ARABIC_LETTERS = set(
    "ابتثجحخدذرزسشصضطظعغفقكلمنهويءآأؤإئةى"
)

# Diacritic characters
DIACRITIC_CHARS = set("ًٌٍَُِّْٰٕٓٔ")

# Tatweel (kashida) - ignored
TATWEEL = "ـ"


# ============================================================================
# Text to Graphemes
# ============================================================================

def text_to_graphemes(text: str) -> List[Grapheme]:
    """
    Parse Arabic text into graphemes (base char + diacritics).
    
    A grapheme is a base letter plus all its diacritics.
    
    Args:
        text: Arabic text (may include diacritics)
    
    Returns:
        List of Grapheme objects
    
    Example:
        >>> text_to_graphemes("كِتَابٌ")
        [
            Grapheme('ك', {Diacritic.KASRA}, 0),
            Grapheme('ت', {Diacritic.FATHA}, 1),
            Grapheme('ا', set(), 2),
            Grapheme('ب', {Diacritic.TANWIN_DAMM}, 3),
        ]
    """
    
    graphemes: List[Grapheme] = []
    position = 0
    
    i = 0
    while i < len(text):
        char = text[i]
        
        # Skip tatweel
        if char == TATWEEL:
            i += 1
            continue
        
        # Skip spaces and punctuation (or handle as needed)
        if char.isspace() or char in ",.!؟،":
            i += 1
            continue
        
        # Must be a base letter
        if char in ARABIC_LETTERS or is_diacritic(char):
            base_char = char if char in ARABIC_LETTERS else ""
            diacs: Set[Diacritic] = set()
            
            # If it's a diacritic without base, skip it
            if not base_char:
                i += 1
                continue
            
            # Collect following diacritics
            j = i + 1
            while j < len(text) and is_diacritic(text[j]):
                diac = diacritic_from_char(text[j])
                if diac:
                    diacs.add(diac)
                j += 1
            
            # Create grapheme
            graphemes.append(Grapheme(
                base_char=base_char,
                diacs=diacs,
                position=position
            ))
            position += 1
            
            # Move past this grapheme
            i = j
        else:
            # Unknown character, skip
            i += 1
    
    return graphemes


# ============================================================================
# Segments to CV Pattern
# ============================================================================

def segments_to_cv(segments: List[Segment]) -> str:
    """
    Convert segment sequence to CV pattern string.
    
    Args:
        segments: List of segments
    
    Returns:
        CV pattern string (e.g., "CVCVVC")
    
    Example:
        >>> segs = [
        ...     Segment(SegKind.C, "ك", (0,1)),
        ...     Segment(SegKind.V_SHORT, "َ", (1,2)),
        ...     Segment(SegKind.C, "ت", (2,3)),
        ...     Segment(SegKind.V_LONG, "ا", (3,4)),
        ... ]
        >>> segments_to_cv(segs)
        "CVCV"
    """
    
    pattern: List[str] = []
    for seg in segments:
        if seg.kind == SegKind.C:
            pattern.append("C")
        elif seg.kind == SegKind.V_SHORT:
            pattern.append("V")
        elif seg.kind == SegKind.V_LONG:
            # Long vowel counts as two morae in CV templates: VV
            pattern.append("VV")

    return "".join(pattern)


def segments_to_detailed_cv(segments: List[Segment]) -> str:
    """
    Convert segments to detailed CV pattern (distinguish V_SHORT vs V_LONG).
    
    Returns:
        Pattern like "CVsCVl" (Vs=short, Vl=long)
    """
    
    pattern = []
    for seg in segments:
        if seg.kind == SegKind.C:
            pattern.append("C")
        elif seg.kind == SegKind.V_SHORT:
            pattern.append("Vs")
        elif seg.kind == SegKind.V_LONG:
            pattern.append("Vl")
    
    return "".join(pattern)


# ============================================================================
# Syllable Extraction
# ============================================================================

def extract_segments_from_syllables(
    syllables: List[SyllableCandidate]
) -> List[Segment]:
    """
    Extract all segments from a syllable sequence.
    
    Args:
        syllables: List of syllables (a complete syllabification)
    
    Returns:
        Flat list of segments
    """
    
    segments = []
    for syl in syllables:
        segments.extend(syl.onset)
        segments.append(syl.nucleus)
        segments.extend(syl.coda)
    
    return segments


def syllables_to_cv_pattern(syllables: List[SyllableCandidate]) -> str:
    """
    Convert syllable sequence to CV pattern.
    """
    segments = extract_segments_from_syllables(syllables)
    return segments_to_cv(segments)


# ============================================================================
# Visualization
# ============================================================================

def format_syllable(syl: SyllableCandidate) -> str:
    """
    Format syllable for display.
    
    Returns:
        String like "كِتَاب (CVVC)"
    """
    
    onset_str = "".join(s.surface for s in syl.onset)
    nucleus_str = syl.nucleus.surface
    coda_str = "".join(s.surface for s in syl.coda)
    
    syllable_text = f"{onset_str}{nucleus_str}{coda_str}"
    syl_type = syl.syl_type.name
    
    return f"{syllable_text} ({syl_type})"


def format_syllabification(syllables: List[SyllableCandidate]) -> str:
    """
    Format complete syllabification for display.
    
    Returns:
        String like "كِ.تَا.بٌ (CV.CVV.CVC)"
    """
    
    syllable_texts = []
    syllable_types = []
    
    for syl in syllables:
        onset_str = "".join(s.surface for s in syl.onset)
        nucleus_str = syl.nucleus.surface
        coda_str = "".join(s.surface for s in syl.coda)
        
        syllable_texts.append(f"{onset_str}{nucleus_str}{coda_str}")
        syllable_types.append(syl.syl_type.name)
    
    text = ".".join(syllable_texts)
    types = ".".join(syllable_types)
    
    return f"{text} ({types})"


def print_vc_witnesses(syllables: List[SyllableCandidate]) -> None:
    """
    Print all VC classification decisions with witnesses.
    """
    
    print("VC Classification Witnesses:")
    print("-" * 60)
    
    for i, syl in enumerate(syllables):
        print(f"\nSyllable {i}: {format_syllable(syl)}")
        
        for w in syl.vc_witnesses:
            print(f"  [{w.grapheme_index}] {w.base:2s} → "
                  f"{w.decided_role.name:12s} "
                  f"(need_nuc={str(w.need_nucleus):5s}, "
                  f"force_c={str(w.force_onset_c):5s}) "
                  f"witness: {w.witness.name}")


def print_lattice_summary(lattice) -> None:
    """
    Print summary of syllable lattice.
    """
    
    print(f"Syllable Lattice Summary:")
    print(f"  Total graphemes: {lattice.grapheme_count}")
    print(f"  Total candidates: {len(lattice.candidates)}")
    print(f"  Position spans: {len(lattice.position_map)}")
    
    # Count by type
    type_counts = {}
    for cand in lattice.candidates:
        t = cand.syl_type.name
        type_counts[t] = type_counts.get(t, 0) + 1
    
    print(f"  Candidates by type:")
    for syl_type, count in sorted(type_counts.items()):
        print(f"    {syl_type:6s}: {count:3d}")


# ============================================================================
# Debugging Helpers
# ============================================================================

def debug_graphemes(graphemes: List[Grapheme]) -> None:
    """
    Print graphemes in readable format.
    """
    
    print("Graphemes:")
    for g in graphemes:
        diacs_str = "".join(d.value for d in g.diacs) if g.diacs else "(none)"
        print(f"  [{g.position}] {g.base_char} + {diacs_str}")


def debug_segments(segments: List[Segment]) -> None:
    """
    Print segments in readable format.
    """
    
    print("Segments:")
    for i, seg in enumerate(segments):
        print(f"  [{i}] {seg.kind.name:8s} '{seg.surface}' span={seg.span}")


def debug_syllable_candidate(cand: SyllableCandidate, index: int) -> None:
    """
    Print detailed information about a syllable candidate.
    """
    
    print(f"\nCandidate {index}:")
    print(f"  Span: {cand.span}")
    print(f"  Type: {cand.syl_type.name}")
    print(f"  Weight: {cand.weight.name}")
    print(f"  Score: {cand.score:.1f}")
    
    onset_str = "".join(s.surface for s in cand.onset) or "(none)"
    nucleus_str = cand.nucleus.surface
    coda_str = "".join(s.surface for s in cand.coda) or "(none)"
    
    print(f"  Structure:")
    print(f"    Onset:   {onset_str} ({len(cand.onset)} segments)")
    print(f"    Nucleus: {nucleus_str} ({cand.nucleus.kind.name})")
    print(f"    Coda:    {coda_str} ({len(cand.coda)} segments)")
    
    print(f"  VC Witnesses:")
    for w in cand.vc_witnesses:
        print(f"    [{w.grapheme_index}] {w.base} → {w.decided_role.name} "
              f"({w.witness.name})")


# ============================================================================
# Validation
# ============================================================================

def validate_syllabification(
    syllables: List[SyllableCandidate],
    expected_grapheme_count: int
) -> bool:
    """
    Validate that syllabification is complete and non-overlapping.
    
    Returns:
        True if valid, False otherwise
    """
    
    if not syllables:
        return expected_grapheme_count == 0
    
    # Check coverage
    covered = set()
    for syl in syllables:
        for i in range(syl.span[0], syl.span[1]):
            if i in covered:
                print(f"ERROR: Position {i} covered by multiple syllables")
                return False
            covered.add(i)
    
    # Check completeness
    if len(covered) != expected_grapheme_count:
        print(f"ERROR: Expected {expected_grapheme_count} positions, "
              f"got {len(covered)}")
        return False
    
    # Check continuity
    if covered != set(range(expected_grapheme_count)):
        print(f"ERROR: Coverage gaps in syllabification")
        return False
    
    return True


# ============================================================================
# Stats
# ============================================================================

def compute_syllabification_stats(syllables: List[SyllableCandidate]) -> dict:
    """
    Compute statistics about a syllabification.
    """
    
    stats = {
        'syllable_count': len(syllables),
        'total_score': sum(s.score for s in syllables),
        'avg_score': sum(s.score for s in syllables) / len(syllables) if syllables else 0,
        'syllable_types': {},
        'weights': {},
        'onset_lengths': {},
        'coda_lengths': {},
    }
    
    for syl in syllables:
        # Type counts
        t = syl.syl_type.name
        stats['syllable_types'][t] = stats['syllable_types'].get(t, 0) + 1
        
        # Weight counts
        w = syl.weight.name
        stats['weights'][w] = stats['weights'].get(w, 0) + 1
        
        # Onset lengths
        onset_len = len(syl.onset)
        stats['onset_lengths'][onset_len] = stats['onset_lengths'].get(onset_len, 0) + 1
        
        # Coda lengths
        coda_len = len(syl.coda)
        stats['coda_lengths'][coda_len] = stats['coda_lengths'].get(coda_len, 0) + 1
    
    return stats
