"""
weight_engine.py — Extract prosodic weight units from syllable analysis.

Weight classification:
  حامل_وزن  — carries weight (core prosodic units: C, long V)
  محقق_وزن  — realizes weight (short vowels within syllable)
  دون_وزن   — below weight (functional/zero-weight elements)

Minimum weight threshold: 3 حاملة units (حامل_وزن).
"""
from __future__ import annotations

from typing import List

from .models import (
    Syllable, SyllableAnalysis, SLineGraph, WeightAnalysis, WeightUnit,
)

# Syllable patterns and their weight contribution
WEIGHT_BEARING_PATTERNS = {
    "CVC": 2,   # مغلق قصير → 2 وحدة
    "CVV": 2,   # طويل مفتوح → 2 وحدة
    "CVVC": 3,  # طويل مغلق → 3 وحدة
    "CV": 1,    # قصير مفتوح → 1 وحدة
}


def classify_weight_role(symbol: str, unit_type: str, syllable_pattern: str) -> tuple:
    """
    Determine weight role for a symbol within its syllable.
    Returns (weight_role, reason).
    """
    if unit_type == "صامت":
        return "حامل_وزن", f"صامت_في_قالب_{syllable_pattern}"
    if unit_type in ("صائت", "extension"):
        if syllable_pattern in ("CVV", "CVVC"):
            return "حامل_وزن", f"صائت_طويل_في_{syllable_pattern}"
        return "محقق_وزن", f"صائت_قصير_في_{syllable_pattern}"
    return "دون_وزن", "عنصر_وظيفي"


def extract_weight_units(
    syllable_analysis: SyllableAnalysis,
    sline_graph: SLineGraph,
) -> WeightAnalysis:
    """
    Extract weight units from SyllableAnalysis + SLineGraph.

    Returns WeightAnalysis with classification and trace.
    """
    weight_units: List[WeightUnit] = []
    trace: List[str] = []

    node_map = {n.node_id: n for n in sline_graph.nodes}

    for syl_idx, syl in enumerate(syllable_analysis.syllables):
        pattern = syl.pattern
        trace.append(f"syllable[{syl_idx}]={pattern}")

        # Assign weight roles to each unit in the syllable
        for unit_sym, nid in zip(syl.units, syl.node_ids):
            node = node_map.get(nid)
            unit_type = node.features.get("type", "صامت") if node else "صامت"
            role, reason = classify_weight_role(unit_sym, unit_type, pattern)
            wu = WeightUnit(
                node_id=nid,
                symbol=unit_sym,
                weight_role=role,
                reason=reason,
            )
            weight_units.append(wu)
            trace.append(f"  unit:{unit_sym} → {role} ({reason})")

    bearing_count = sum(1 for wu in weight_units if wu.weight_role == "حامل_وزن")
    trace.append(f"total_حامل_وزن={bearing_count}")

    return WeightAnalysis(
        weight_units=weight_units,
        weight_unit_count=bearing_count,
        below_weight=bearing_count < 3,
        valid_weight=bearing_count >= 3,
        trace=trace,
    )


def check_min_weight_threshold(weight_analysis: WeightAnalysis, threshold: int = 3) -> bool:
    """Check if weight meets minimum threshold."""
    return weight_analysis.weight_unit_count >= threshold


def map_weight_to_syllables(
    weight_analysis: WeightAnalysis,
    syllable_analysis: SyllableAnalysis,
) -> dict:
    """Map weight units back to syllable indices."""
    mapping: dict = {}
    for wu in weight_analysis.weight_units:
        for syl_idx, syl in enumerate(syllable_analysis.syllables):
            if wu.node_id in syl.node_ids:
                mapping[wu.node_id] = syl_idx
                break
    return mapping
