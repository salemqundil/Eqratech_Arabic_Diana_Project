"""
syllable_engine.py — Build canonical syllable structure from S-Line graph.

Syllable types: CV (مفتوح قصير), CVC (مغلق قصير), CVV (مفتوح طويل), CVVC (مغلق طويل)
"""
from __future__ import annotations

from typing import Dict, List, Optional

from .models import PhonoUnit, Syllable, SyllableAnalysis, SLineGraph

# Syllable pattern constants
CV   = "CV"    # مقطع قصير مفتوح
CVC  = "CVC"   # مغلق قصير
CVV  = "CVV"   # مد / طويل مفتوح
CVVC = "CVVC"  # طويل مغلق


def _is_consonant(pu: PhonoUnit) -> bool:
    return pu.unit_type == "صامت"


def _is_vowel(pu: PhonoUnit) -> bool:
    return pu.unit_type in ("صائت", "شبه_صائت")


def classify_syllable(syllable: Syllable) -> Syllable:
    """Classify and validate syllable pattern."""
    valid_patterns = {CV, CVC, CVV, CVVC}
    if syllable.pattern not in valid_patterns:
        syllable.is_valid = False
        syllable.validity_notes.append(f"غير_معروف:{syllable.pattern}")
    else:
        syllable.is_valid = True
    return syllable


def validate_syllable(syllable: Syllable, phonology_hints: bool = True) -> Syllable:
    """Validate syllable structure."""
    classify_syllable(syllable)
    if phonology_hints and syllable.pattern == "V":
        syllable.is_valid = False
        syllable.validity_notes.append("صائت_بدون_صامت")
    return syllable


def _build_syllables_from_units(phono_units: List[PhonoUnit]) -> List[Syllable]:
    """
    Core syllable building algorithm.
    Scans phono_units left-to-right applying CV-based rules.
    """
    syllables: List[Syllable] = []
    i = 0
    n = len(phono_units)

    while i < n:
        pu = phono_units[i]

        if _is_consonant(pu):
            # Start potential syllable: C
            pattern_chars = [pu.symbol]
            pattern = "C"
            node_ids = [f"w{pu.word_index}_p{pu.position}_صوت"]
            i += 1

            if i < n and _is_vowel(phono_units[i]):
                # CV so far
                pattern_chars.append(phono_units[i].symbol)
                pattern += "V"
                node_ids.append(f"w{phono_units[i].word_index}_p{phono_units[i].position}_صوت")
                i += 1

                # Check for long vowel (second vowel extension)
                if i < n and phono_units[i].unit_type in ("صائت", "extension"):
                    pattern_chars.append(phono_units[i].symbol)
                    pattern += "V"
                    node_ids.append(f"w{phono_units[i].word_index}_p{phono_units[i].position}_صوت")
                    i += 1

                # Check for closing consonant
                if i < n and _is_consonant(phono_units[i]):
                    # Peek: if next is also consonant or end → close syllable
                    is_last = (i + 1 >= n)
                    next_is_c = (i + 1 < n and _is_consonant(phono_units[i + 1]))
                    if is_last or next_is_c:
                        pattern_chars.append(phono_units[i].symbol)
                        pattern += "C"
                        node_ids.append(f"w{phono_units[i].word_index}_p{phono_units[i].position}_صوت")
                        i += 1

                syl = Syllable(
                    pattern=pattern,
                    units=pattern_chars,
                    node_ids=node_ids,
                )
                validate_syllable(syl)
                syllables.append(syl)
            else:
                # Bare consonant — invalid syllable or word-final
                syl = Syllable(
                    pattern="C",
                    units=pattern_chars,
                    node_ids=node_ids,
                    is_valid=False,
                    validity_notes=["صامت_منفرد"],
                )
                syllables.append(syl)
        else:
            # Vowel without preceding consonant
            syl = Syllable(
                pattern="V",
                units=[pu.symbol],
                node_ids=[f"w{pu.word_index}_p{pu.position}_صوت"],
                is_valid=False,
                validity_notes=["صائت_بدون_صامت"],
            )
            syllables.append(syl)
            i += 1

    return syllables


def map_syllable_to_sline(syllable: Syllable, graph: SLineGraph) -> Dict[str, str]:
    """Return mapping of syllable node_ids to sline node symbols."""
    mapping: Dict[str, str] = {}
    node_map = {n.node_id: n.symbol for n in graph.nodes}
    for nid in syllable.node_ids:
        if nid in node_map:
            mapping[nid] = node_map[nid]
    return mapping


def build_syllables(
    sline_graph: Optional[SLineGraph] = None,
    phono_units: Optional[List[PhonoUnit]] = None,
) -> SyllableAnalysis:
    """
    Build SyllableAnalysis from either SLineGraph or PhonoUnit list.
    """
    if phono_units is None and sline_graph is not None:
        # Reconstruct PhonoUnit info from graph nodes (صوت layer)
        phono_units = []
        sound_nodes = [n for n in sline_graph.nodes if n.layer == "صوت"]
        for node in sound_nodes:
            # parse word_index and position from node_id: w{wi}_p{pos}_صوت
            parts = node.node_id.split("_")
            wi = int(parts[0][1:]) if parts[0].startswith("w") else 0
            pos = int(parts[1][1:]) if len(parts) > 1 and parts[1].startswith("p") else 0
            pu = PhonoUnit(
                symbol=node.symbol,
                unit_type=node.features.get("type", "صامت"),
                makhraj="",
                sifa=node.features.get("sifa", []),
                position=pos,
                word_index=wi,
            )
            phono_units.append(pu)

    if not phono_units:
        return SyllableAnalysis(trace=["no_phono_units"])

    syllables = _build_syllables_from_units(phono_units)

    syllable_map: Dict[str, str] = {}
    for idx, syl in enumerate(syllables):
        for nid in syl.node_ids:
            syllable_map[nid] = str(idx)

    trace = [f"built_{len(syllables)}_syllables"]
    for i, s in enumerate(syllables):
        trace.append(f"syl[{i}]={s.pattern}({'valid' if s.is_valid else 'invalid'})")

    return SyllableAnalysis(
        syllables=syllables,
        syllable_map=syllable_map,
        trace=trace,
    )
