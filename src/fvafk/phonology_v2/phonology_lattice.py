"""
FVAFK Phonology System - Syllable Lattice Builder
==================================================

Main algorithm for building a complete lattice of possible syllabifications.

This uses bidirectional negotiation between:
- Syllable structure constraints (CV patterns)
- VC classification (which letters are consonants vs vowels)

Author: Hussein (FVAFK Project)
Date: 2025-02-09
"""

from typing import List, Tuple, Dict, Optional

try:
    from .phonology_types import (
        Grapheme,
        Segment,
        SegKind,
        SyllableCandidate,
        SyllableLattice,
        SyllableType,
        SyllableWeight,
        VcTrace,
        CVRole,
        VCWitness,
        Diacritic,
    )
    from .phonology_vc_classify import vc_classify, has_shadda
except ImportError:  # pragma: no cover
    from phonology_types import (
        Grapheme,
        Segment,
        SegKind,
        SyllableCandidate,
        SyllableLattice,
        SyllableType,
        SyllableWeight,
        VcTrace,
        CVRole,
        VCWitness,
        Diacritic,
    )
    from phonology_vc_classify import vc_classify, has_shadda


# ============================================================================
# Segment Building with Context
# ============================================================================

def build_segments_with_context(
    graphemes: List[Grapheme],
    need_nucleus_map: Dict[int, bool],
    force_onset_map: Dict[int, bool]
) -> Tuple[List[Segment], List[VcTrace]]:
    """
    Convert graphemes to segments using context-aware VC classification.
    
    This is called during syllable candidate construction to determine
    what role each grapheme plays in the proposed syllable.
    
    Args:
        graphemes: Input graphemes (subset for this syllable)
        need_nucleus_map: {local_idx: True} if this position must be nucleus
        force_onset_map: {local_idx: True} if this position must stay consonant
    
    Returns:
        (segments, vc_traces)
    """
    segments: List[Segment] = []
    traces: List[VcTrace] = []
    
    for gi, g in enumerate(graphemes):
        need_nuc = need_nucleus_map.get(gi, False)
        force_c = force_onset_map.get(gi, False)
        
        # Classify this grapheme
        dec = vc_classify(g.base_char, g.diacs, need_nuc, force_c)
        
        # Record trace
        traces.append(VcTrace(
            grapheme_index=g.position,  # Use original position
            base=g.base_char,
            need_nucleus=need_nuc,
            force_onset_c=force_c,
            decided_role=dec.role,
            surface=dec.surface,
            witness=dec.witness
        ))
        
        # Handle SHADDA (gemination)
        shadda = has_shadda(g.diacs)
        
        # Convert role to segment(s)
        if dec.role == CVRole.V_SHORT:
            segments.append(Segment(
                kind=SegKind.V_SHORT,
                surface=dec.surface,
                span=(g.position, g.position + 1)
            ))
        
        elif dec.role == CVRole.V_LONG:
            segments.append(Segment(
                kind=SegKind.V_LONG,
                surface=dec.surface,
                span=(g.position, g.position + 1)
            ))
        
        else:  # Consonant-like (C, HAMZA_C, HAMZA_SEAT)
            seg = Segment(
                kind=SegKind.C,
                surface=g.base_char,
                span=(g.position, g.position + 1)
            )
            
            if shadda:
                # Gemination: insert consonant twice
                segments.append(seg)
                segments.append(seg)
            else:
                segments.append(seg)
    
    return segments, traces


# ============================================================================
# Syllable Type Classification
# ============================================================================

def classify_syllable(
    onset: List[Segment],
    nucleus: Segment,
    coda: List[Segment]
) -> Tuple[SyllableType, SyllableWeight]:
    """
    Classify syllable type and weight based on structure.
    
    Arabic syllable types:
    - CV:   قَ (light)
    - CVC:  قَدْ (heavy)
    - CVV:  قَا (heavy)
    - CVVC: قَالْ (superheavy)
    - CVCC: قَلْبْ (superheavy, rare)
    
    Args:
        onset: Onset consonants
        nucleus: Nucleus vowel
        coda: Coda consonants
    
    Returns:
        (syllable_type, weight)
    """
    
    coda_count = len(coda)
    is_long_nucleus = (nucleus.kind == SegKind.V_LONG)
    
    # Determine type
    if coda_count == 0:
        syl_type = SyllableType.CVV if is_long_nucleus else SyllableType.CV
    elif coda_count == 1:
        syl_type = SyllableType.CVVC if is_long_nucleus else SyllableType.CVC
    else:  # coda_count >= 2
        syl_type = SyllableType.CVCC
    
    # Determine weight
    if syl_type == SyllableType.CV:
        weight = SyllableWeight.LIGHT
    elif syl_type in {SyllableType.CVC, SyllableType.CVV}:
        weight = SyllableWeight.HEAVY
    else:  # CVVC, CVCC
        weight = SyllableWeight.SUPERHEAVY
    
    return syl_type, weight


# ============================================================================
# Syllable Scoring
# ============================================================================

def score_syllable(syl_type, weight, onset_count, is_word_final):
    """
    Preference scoring for syllable candidates.

    Higher is better. Scores are designed to:
    - Strongly discourage medial CVCC (superheavy clusters)
    - Mildly discourage CVVC compared to CVC/CVV
    - Discourage onset clusters (CC) in Arabic
    """
    score = 100.0

    # Onset clusters are rare in Arabic (except in borrowed words / sandhi)
    if onset_count >= 2:
        score -= 60.0

    # Prefer common syllable types
    if syl_type == SyllableType.CV:
        score += 5.0
    elif syl_type in {SyllableType.CVC, SyllableType.CVV}:
        score += 2.0
    elif syl_type == SyllableType.CVVC:
        score -= 8.0
    elif syl_type == SyllableType.CVCC:
        # Word-final CVCC can be acceptable; medial CVCC is extremely unlikely
        if is_word_final:
            score -= 5.0
        else:
            score -= 120.0

    # Weight sanity (tiny bias): superheavy slightly discouraged unless final
    if weight == SyllableWeight.SUPERHEAVY and not is_word_final:
        score -= 10.0

    return score
# ============================================================================
# Candidate Construction
# ============================================================================

def build_candidate(
    onset: List[Segment],
    nucleus: Segment,
    coda: List[Segment],
    span: Tuple[int, int],
    witnesses: List[VcTrace],
    is_word_final: bool = False
) -> SyllableCandidate:
    """
    Build a syllable candidate from components.
    """
    
    # Classify
    syl_type, weight = classify_syllable(onset, nucleus, coda)
    
    # Score
    onset_count = len(onset)
    score = score_syllable(syl_type, weight, onset_count, is_word_final)
    
    return SyllableCandidate(
        onset=onset,
        nucleus=nucleus,
        coda=coda,
        span=span,
        syl_type=syl_type,
        weight=weight,
        score=score,
        # Make a defensive copy: candidates must not share mutable witness lists.
        vc_witnesses=list(witnesses)
    )


# ============================================================================
# Pattern Trying Logic
# ============================================================================

def try_with_nucleus(
    graphemes: List[Grapheme],
    syl_start: int,
    onset_segs: List[Segment],
    onset_traces: List[VcTrace],
    nucleus_pos: int,
    is_long: bool,
    total: int,
    allow_superheavy: bool,
    is_word_final: bool
) -> List[SyllableCandidate]:
    """
    Try building syllable with given onset and nucleus type.
    
    Args:
        graphemes: Full grapheme sequence
        syl_start: Starting position of this syllable
        onset_segs: Already-built onset segments
        onset_traces: Traces for onset
        nucleus_pos: Position of nucleus grapheme
        is_long: Try to make nucleus a long vowel?
        total: Total grapheme count
        allow_superheavy: Allow CVVC/CVCC syllables?
        is_word_final: Is this at word end?
    
    Returns:
        List of valid syllable candidates
    """
    
    results: List[SyllableCandidate] = []
    
    if nucleus_pos >= total:
        return results
    
    g_nucleus = graphemes[nucleus_pos]
    
    # Classify nucleus with need_nucleus=True, force_onset_c=False
    nuc_dec = vc_classify(
        g_nucleus.base_char,
        g_nucleus.diacs,
        need_nucleus=True,
        force_onset_c=False
    )
    
    # Check if classification matches what we're trying
    if is_long:
        if nuc_dec.role != CVRole.V_LONG:
            return results  # Can't make this a long vowel
        nucleus_seg = Segment(
            kind=SegKind.V_LONG,
            surface=nuc_dec.surface,
            span=(nucleus_pos, nucleus_pos + 1)
        )
    else:
        if nuc_dec.role != CVRole.V_SHORT:
            return results  # Not a short vowel
        nucleus_seg = Segment(
            kind=SegKind.V_SHORT,
            surface=nuc_dec.surface,
            span=(nucleus_pos, nucleus_pos + 1)
        )
    
    nucleus_trace = VcTrace(
        grapheme_index=nucleus_pos,
        base=g_nucleus.base_char,
        need_nucleus=True,
        force_onset_c=False,
        decided_role=nuc_dec.role,
        surface=nuc_dec.surface,
        witness=nuc_dec.witness
    )
    
    # Try different coda lengths
    coda_start = nucleus_pos + 1
    
    # ========================================================================
    # No coda: CV or CVV
    # ========================================================================
    results.append(build_candidate(
        onset_segs,
        nucleus_seg,
        [],
        (syl_start, coda_start),
        onset_traces + [nucleus_trace],
        is_word_final=(coda_start >= total)
    ))
    
    # ========================================================================
    # Coda with 1 consonant: CVC or CVVC
    # ========================================================================
    if coda_start < total:
        coda_1_graphemes = [graphemes[coda_start]]
        coda_1_segs, coda_1_traces = build_segments_with_context(
            coda_1_graphemes,
            {0: False},  # Not nucleus
            {0: True}    # Force consonant
        )
        
        if len(coda_1_segs) > 0 and all(s.kind == SegKind.C for s in coda_1_segs):
            results.append(build_candidate(
                onset_segs,
                nucleus_seg,
                coda_1_segs,
                (syl_start, coda_start + 1),
                onset_traces + [nucleus_trace] + coda_1_traces,
                is_word_final=(coda_start + 1 >= total)
            ))
        
        # ====================================================================
        # Coda with 2 consonants: CVCC (superheavy, usually word-final)
        # ====================================================================
        if allow_superheavy and coda_start + 1 < total:
            coda_2_graphemes = graphemes[coda_start:coda_start + 2]
            coda_2_segs, coda_2_traces = build_segments_with_context(
                coda_2_graphemes,
                {0: False, 1: False},
                {0: True, 1: True}
            )
            
            if len(coda_2_segs) >= 2 and all(s.kind == SegKind.C for s in coda_2_segs):
                # Only allow CVCC word-finally (or override this check)
                if is_word_final or coda_start + 2 >= total:
                    results.append(build_candidate(
                        onset_segs,
                        nucleus_seg,
                        coda_2_segs[:2],
                        (syl_start, coda_start + 2),
                        onset_traces + [nucleus_trace] + coda_2_traces,
                        is_word_final=True
                    ))
    
    return results


def try_cv_patterns(
    graphemes: List[Grapheme],
    start: int,
    total: int,
    max_onset: int,
    allow_superheavy: bool
) -> List[SyllableCandidate]:
    """
    Try all valid syllables starting at grapheme index `start`.

    IMPORTANT: Arabic short vowels are diacritics on the SAME consonant grapheme.
    So the nucleus for short vowels comes from `graphemes[start]` itself.

    This function builds candidates using a grapheme-level model:
    - onset = consonant at start
    - nucleus = short vowel diacritic on that consonant (if present)
    - optionally extend nucleus with a following long-letter (ا/و/ي) when it
      forms a true long vowel (e.g., تَ + ا → تَا)
    - coda = following consonant graphemes without short vowels
    """

    def short_vowel_char(diacs: set) -> Optional[str]:
        if Diacritic.FATHA in diacs:
            return "َ"
        if Diacritic.DAMMA in diacs:
            return "ُ"
        if Diacritic.KASRA in diacs:
            return "ِ"
        return None

    def matches_long_extension(vowel: str, long_letter: str) -> bool:
        return (
            (vowel == "َ" and long_letter == "ا")
            or (vowel == "ُ" and long_letter == "و")
            or (vowel == "ِ" and long_letter == "ي")
        )

    results: List[SyllableCandidate] = []
    if start >= total:
        return results

    g0 = graphemes[start]
    v0 = short_vowel_char(g0.diacs)
    if v0 is None:
        # Without a short vowel on the consonant, we can't form a syllable nucleus
        # in this simplified diacritized model.
        return results

    # Onset consonant (handle shadda by doubling onset consonant)
    onset: List[Segment] = [Segment(kind=SegKind.C, surface=g0.base_char, span=(start, start + 1))]
    # Witness traces:
    # - one trace for the consonantal base (onset)
    # - one trace for the short vowel nucleus on the same grapheme
    traces: List[VcTrace] = [
        VcTrace(
            grapheme_index=start,
            base=g0.base_char,
            need_nucleus=False,
            force_onset_c=True,
            decided_role=CVRole.C,
            surface=g0.base_char,
            witness=VCWitness.DEFAULT_CONSONANT,
        ),
        VcTrace(
            grapheme_index=start,
            base=g0.base_char,
            need_nucleus=True,
            force_onset_c=False,
            decided_role=CVRole.V_SHORT,
            surface=v0,
            witness=VCWitness.SHORT_ON_SELF,
        ),
    ]
    if has_shadda(g0.diacs):
        onset.append(Segment(kind=SegKind.C, surface=g0.base_char, span=(start, start + 1)))

    # Nucleus short vowel is on the same grapheme
    nucleus = Segment(kind=SegKind.V_SHORT, surface=v0, span=(start, start + 1))
    pos_after_nucleus = start + 1

    # Optional long vowel extension: next grapheme is long letter matching v0
    if pos_after_nucleus < total:
        g1 = graphemes[pos_after_nucleus]
        if (
            g1.base_char in {"ا", "و", "ي"}
            and short_vowel_char(g1.diacs) is None
            and Diacritic.SUKUN not in g1.diacs
            and matches_long_extension(v0, g1.base_char)
        ):
            nucleus = Segment(kind=SegKind.V_LONG, surface=g1.base_char, span=(pos_after_nucleus, pos_after_nucleus + 1))
            traces.append(
                VcTrace(
                    grapheme_index=pos_after_nucleus,
                    base=g1.base_char,
                    need_nucleus=True,
                    force_onset_c=False,
                    decided_role=CVRole.V_LONG,
                    surface=g1.base_char,
                    witness=VCWitness.LONG_BY_NUCLEUS_NEED,
                )
            )
            pos_after_nucleus += 1

    # Candidate with no coda (CV / CVV)
    results.append(
        build_candidate(
            onset=onset,
            nucleus=nucleus,
            coda=[],
            span=(start, pos_after_nucleus),
            witnesses=traces,
            is_word_final=(pos_after_nucleus >= total),
        )
    )

    # Coda with 1 consonant grapheme (must have no short vowel)
    if pos_after_nucleus < total:
        g_c1 = graphemes[pos_after_nucleus]
        if short_vowel_char(g_c1.diacs) is None:
            coda1 = [Segment(kind=SegKind.C, surface=g_c1.base_char, span=(pos_after_nucleus, pos_after_nucleus + 1))]
            end1 = pos_after_nucleus + 1
            coda1_trace = VcTrace(
                grapheme_index=pos_after_nucleus,
                base=g_c1.base_char,
                need_nucleus=False,
                force_onset_c=False,
                decided_role=CVRole.C,
                surface=g_c1.base_char,
                witness=VCWitness.DEFAULT_CONSONANT,
            )
            results.append(
                build_candidate(
                    onset=onset,
                    nucleus=nucleus,
                    coda=coda1,
                    span=(start, end1),
                    witnesses=traces + [coda1_trace],
                    is_word_final=(end1 >= total),
                )
            )

            # Coda with 2 consonants (CVCC): allow only at word-final
            if allow_superheavy and end1 < total:
                g_c2 = graphemes[end1]
                if short_vowel_char(g_c2.diacs) is None and end1 + 1 >= total:
                    coda2 = coda1 + [Segment(kind=SegKind.C, surface=g_c2.base_char, span=(end1, end1 + 1))]
                    coda2_trace = VcTrace(
                        grapheme_index=end1,
                        base=g_c2.base_char,
                        need_nucleus=False,
                        force_onset_c=False,
                        decided_role=CVRole.C,
                        surface=g_c2.base_char,
                        witness=VCWitness.DEFAULT_CONSONANT,
                    )
                    results.append(
                        build_candidate(
                            onset=onset,
                            nucleus=nucleus,
                            coda=coda2,
                            span=(start, end1 + 1),
                            witnesses=traces + [coda1_trace, coda2_trace],
                            is_word_final=True,
                        )
                    )

    return results


# ============================================================================
# Main Lattice Builder
# ============================================================================

def build_syllable_lattice_v2(
    graphemes: List[Grapheme],
    max_onset: int = 1,
    allow_superheavy: bool = True
) -> SyllableLattice:
    """
    Build complete syllable lattice using bidirectional VC classification.
    
    Algorithm:
    1. For each position, try to build syllable candidates
    2. For each candidate, determine which graphemes need to be nucleus
    3. Re-classify ا/و/ي based on syllable needs
    4. Accept/reject candidates based on phonotactic constraints
    5. Score candidates by preference
    
    Args:
        graphemes: Input graphemes
        max_onset: Maximum consonants in onset (default 1, Arabic rarely has 2)
        allow_superheavy: Allow CVVC/CVCC (usually only word-final)
    
    Returns:
        SyllableLattice with all valid candidates
    """
    
    n = len(graphemes)
    candidates: List[SyllableCandidate] = []
    
    # Try building syllables starting at each position
    for start in range(n):
        # Try different syllable patterns
        new_candidates = try_cv_patterns(
            graphemes, start, n, max_onset, allow_superheavy
        )
        candidates.extend(new_candidates)
    
    # Build position map for efficient lookup
    position_map: Dict[Tuple[int, int], List[int]] = {}
    for idx, cand in enumerate(candidates):
        key = cand.span
        if key not in position_map:
            position_map[key] = []
        position_map[key].append(idx)
    
    return SyllableLattice(
        candidates=candidates,
        grapheme_count=n,
        position_map=position_map
    )


# ============================================================================
# Best Path Finding (Dynamic Programming)
# ============================================================================

def find_best_syllabification(
    lattice: SyllableLattice
) -> Optional[List[SyllableCandidate]]:
    """
    Find the best complete path through the syllable lattice.
    
    Uses dynamic programming to find the highest-scoring complete
    syllabification that covers all graphemes exactly once.
    
    Args:
        lattice: Complete syllable lattice
    
    Returns:
        List of syllable candidates forming best path, or None if impossible
    """
    
    n = lattice.grapheme_count
    
    # dp[i] = (best_score, path_to_position_i)
    dp: Dict[int, Tuple[float, List[SyllableCandidate]]] = {0: (0.0, [])}
    
    # For each position
    for pos in range(n + 1):
        if pos not in dp:
            continue
        
        current_score, current_path = dp[pos]
        
        # Try all candidates starting at this position
        for cand in lattice.candidates:
            if cand.span[0] != pos:
                continue
            
            next_pos = cand.span[1]
            new_score = current_score + cand.score
            new_path = current_path + [cand]
            
            # Update if better
            if next_pos not in dp or new_score > dp[next_pos][0]:
                dp[next_pos] = (new_score, new_path)
    
    # Check if we reached the end
    if n in dp:
        return dp[n][1]
    else:
        return None
