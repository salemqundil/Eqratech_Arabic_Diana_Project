"""
composite_expander.py — Expand composite graphemes into explicit ExpandedUnit list.

Handles: shadda (شدة), tanween, madd, hamza carrier separation.
Each expansion records a trace explaining what was done.
"""
from __future__ import annotations

from typing import List, Optional

from .models import GraphemeCluster, ExpandedUnit

# Diacritic code points
SHADDA    = "\u0651"
FATHA     = "\u064E"
KASRA     = "\u0650"
DAMMA     = "\u064F"
SUKUN     = "\u0652"
TANWIN_F  = "\u064B"   # fathatan
TANWIN_K  = "\u064D"   # kasratan
TANWIN_D  = "\u064C"   # dammatan
MADD      = "\u0653"   # maddah
ALEF      = "\u0627"
WAW       = "\u0648"
YEH       = "\u064A"
HAMZA     = "\u0621"

VOWEL_MARKS = {FATHA, KASRA, DAMMA, SUKUN}
TANWEEN_MARKS = {TANWIN_F, TANWIN_K, TANWIN_D}

LONG_VOWEL_CARRIERS = {ALEF: FATHA, WAW: DAMMA, YEH: KASRA}


def expand_shadda(cluster: GraphemeCluster) -> List[ExpandedUnit]:
    """
    Expand shadda: ب + شدة → ب (silent) + ب (active consonant).
    Returns two ExpandedUnit items when shadda present, else one.
    """
    units: List[ExpandedUnit] = []
    has_shadda = SHADDA in cluster.diacritics
    other_diacritics = [d for d in cluster.diacritics if d != SHADDA]

    if has_shadda:
        # First: silent (assimilated) copy
        units.append(ExpandedUnit(
            base_char=cluster.base_char,
            role="consonant",
            value=cluster.base_char,
            expansion_trace=[f"shadda_first_copy:{cluster.base_char}"],
            position=cluster.position,
            word_index=cluster.word_index,
        ))
        # Second: active copy with remaining diacritics
        units.append(ExpandedUnit(
            base_char=cluster.base_char,
            role="consonant",
            value=cluster.base_char + "".join(other_diacritics),
            expansion_trace=[f"shadda_second_copy:{cluster.base_char}", "shadda_expanded"],
            position=cluster.position,
            word_index=cluster.word_index,
        ))
    else:
        units.append(ExpandedUnit(
            base_char=cluster.base_char,
            role="consonant",
            value=cluster.full,
            expansion_trace=["no_shadda"],
            position=cluster.position,
            word_index=cluster.word_index,
        ))
    return units


def expand_tanween(cluster: GraphemeCluster, stop_mode: bool = False) -> List[ExpandedUnit]:
    """
    Expand tanween: فتحتان → حركة (فتحة) + نون وظيفية.
    If stop_mode=True (waqf), tanween is dropped.
    """
    units: List[ExpandedUnit] = []
    tanween_mark = next((d for d in cluster.diacritics if d in TANWEEN_MARKS), None)
    other_diacritics = [d for d in cluster.diacritics if d not in TANWEEN_MARKS]

    if tanween_mark is None:
        # No tanween – just pass through
        units.append(ExpandedUnit(
            base_char=cluster.base_char,
            role="consonant",
            value=cluster.full,
            expansion_trace=["no_tanween"],
            position=cluster.position,
            word_index=cluster.word_index,
        ))
        return units

    vowel_equiv = {TANWIN_F: FATHA, TANWIN_K: KASRA, TANWIN_D: DAMMA}[tanween_mark]

    # The base character with its vowel equivalent
    units.append(ExpandedUnit(
        base_char=cluster.base_char,
        role="consonant",
        value=cluster.base_char + vowel_equiv + "".join(other_diacritics),
        expansion_trace=[f"tanween_vowel:{tanween_mark}→{vowel_equiv}"],
        position=cluster.position,
        word_index=cluster.word_index,
    ))

    if not stop_mode:
        # Functional nun
        units.append(ExpandedUnit(
            base_char="ن",
            role="functional",
            value="ن" + SUKUN,
            expansion_trace=["tanween_functional_nun"],
            position=cluster.position,
            word_index=cluster.word_index,
        ))

    return units


def expand_madd(cluster: GraphemeCluster, context: Optional[str] = None) -> List[ExpandedUnit]:
    """
    Expand madd (long vowel): حرف مد = حركة قصيرة + امتداد.
    """
    units: List[ExpandedUnit] = []
    char = cluster.base_char

    if char in LONG_VOWEL_CARRIERS:
        short_vowel = LONG_VOWEL_CARRIERS[char]
        units.append(ExpandedUnit(
            base_char=char,
            role="vowel",
            value=short_vowel,
            expansion_trace=[f"madd_short_vowel:{short_vowel}"],
            position=cluster.position,
            word_index=cluster.word_index,
        ))
        units.append(ExpandedUnit(
            base_char=char,
            role="extension",
            value=char,
            expansion_trace=["madd_extension"],
            position=cluster.position,
            word_index=cluster.word_index,
        ))
    else:
        units.append(ExpandedUnit(
            base_char=char,
            role="consonant",
            value=cluster.full,
            expansion_trace=["no_madd"],
            position=cluster.position,
            word_index=cluster.word_index,
        ))
    return units


def separate_hamza_carrier(cluster: GraphemeCluster) -> List[ExpandedUnit]:
    """
    Separate hamza (ء) as phoneme from its graphical carrier (أ/إ/ؤ/ئ).
    """
    carriers = {"\u0623": ALEF, "\u0625": ALEF, "\u0624": WAW, "\u0626": YEH}
    char = cluster.base_char
    if char in carriers:
        carrier = carriers[char]
        units = [
            ExpandedUnit(
                base_char=HAMZA,
                role="consonant",
                value=HAMZA,
                expansion_trace=[f"hamza_separated_from:{char}"],
                position=cluster.position,
                word_index=cluster.word_index,
            ),
            ExpandedUnit(
                base_char=carrier,
                role="carrier",
                value=carrier + "".join(cluster.diacritics),
                expansion_trace=[f"hamza_carrier:{carrier}"],
                position=cluster.position,
                word_index=cluster.word_index,
            ),
        ]
        return units
    # Not a hamza carrier
    return [ExpandedUnit(
        base_char=char,
        role="consonant",
        value=cluster.full,
        expansion_trace=["no_hamza_carrier"],
        position=cluster.position,
        word_index=cluster.word_index,
    )]


def _is_long_vowel_without_diacritics(cluster: GraphemeCluster) -> bool:
    """Return True if cluster is a bare long-vowel carrier (madd context)."""
    return (
        cluster.base_char in LONG_VOWEL_CARRIERS
        and not any(d in VOWEL_MARKS for d in cluster.diacritics)
    )


def _expand_cluster(cluster: GraphemeCluster) -> List[ExpandedUnit]:
    """Apply all expansions to a single GraphemeCluster."""
    diacritics = set(cluster.diacritics)

    # Priority: shadda > tanween > madd carrier > hamza carrier > plain
    if SHADDA in diacritics:
        return expand_shadda(cluster)
    if diacritics & TANWEEN_MARKS:
        return expand_tanween(cluster)
    if _is_long_vowel_without_diacritics(cluster):
        return expand_madd(cluster)
    if cluster.base_char in {"\u0623", "\u0625", "\u0624", "\u0626"}:
        return separate_hamza_carrier(cluster)

    # Plain cluster
    if not cluster.base_char.strip():
        return []

    units: List[ExpandedUnit] = []
    role = "vowel" if cluster.base_char in LONG_VOWEL_CARRIERS else "consonant"
    # Consonant (or long-vowel carrier) unit
    units.append(ExpandedUnit(
        base_char=cluster.base_char,
        role=role,
        value=cluster.base_char,
        expansion_trace=["plain"],
        position=cluster.position,
        word_index=cluster.word_index,
    ))
    # Extract short-vowel diacritics as separate vowel units
    for d in cluster.diacritics:
        if d in VOWEL_MARKS and d != SUKUN:
            units.append(ExpandedUnit(
                base_char=d,
                role="vowel",
                value=d,
                expansion_trace=[f"short_vowel:{d}"],
                position=cluster.position,
                word_index=cluster.word_index,
            ))
    return units


def expand_units(clusters: List[GraphemeCluster]) -> List[ExpandedUnit]:
    """
    Expand all GraphemeCluster items into ExpandedUnit list.

    Re-numbers positions sequentially so every ExpandedUnit has a unique
    (word_index, position) pair, enabling collision-free S-Line node IDs.
    """
    result: List[ExpandedUnit] = []
    for cluster in clusters:
        result.extend(_expand_cluster(cluster))
    # Reassign sequential positions within each word
    word_counters: dict = {}
    for unit in result:
        wi = unit.word_index
        unit.position = word_counters.get(wi, 0)
        word_counters[wi] = unit.position + 1
    return result
