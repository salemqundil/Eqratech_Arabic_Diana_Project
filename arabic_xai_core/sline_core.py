"""
sline_core.py — Build the S-Line (س.خط) graph representation.

Each node represents رسم/صوت/وظيفة/وزن layers.
Edges represent internal, transformational, or syntactic references.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from .models import PhonoUnit, SLineEdge, SLineGraph, SLineNode


def _make_node_id(word_index: int, position: int, layer: str) -> str:
    return f"w{word_index}_p{position}_{layer}"


def build_sline_for_word(
    phono_units: List[PhonoUnit],
    word_index: int = 0,
) -> SLineGraph:
    """
    Build S-Line graph for a single word from its PhonoUnit list.

    Layers created per unit:
      - رسم  (grapheme / script)
      - صوت  (phoneme / sound)
      - وظيفة (function)
      - وزن  (prosodic weight)
    """
    nodes: List[SLineNode] = []
    edges: List[SLineEdge] = []
    trace: List[str] = []

    prev_sound_id: Optional[str] = None

    for pu in phono_units:
        pos = pu.position

        # ── رسم node ─────────────────────────────────────────────────
        rasm_id = _make_node_id(word_index, pos, "رسم")
        nodes.append(SLineNode(
            node_id=rasm_id,
            symbol=pu.symbol,
            layer="رسم",
            features={"makhraj": pu.makhraj},
        ))

        # ── صوت node ─────────────────────────────────────────────────
        sound_id = _make_node_id(word_index, pos, "صوت")
        nodes.append(SLineNode(
            node_id=sound_id,
            symbol=pu.symbol,
            layer="صوت",
            features={"type": pu.unit_type, "sifa": pu.sifa},
        ))

        # ── وظيفة node ───────────────────────────────────────────────
        func_id = _make_node_id(word_index, pos, "وظيفة")
        nodes.append(SLineNode(
            node_id=func_id,
            symbol=pu.symbol,
            layer="وظيفة",
            features={"can_shift_role": pu.can_shift_role},
        ))

        # ── وزن node ─────────────────────────────────────────────────
        weight_id = _make_node_id(word_index, pos, "وزن")
        nodes.append(SLineNode(
            node_id=weight_id,
            symbol=pu.symbol,
            layer="وزن",
            features={"unit_type": pu.unit_type},
        ))

        # Internal edges: رسم → صوت → وظيفة → وزن
        edges.append(SLineEdge(rasm_id, sound_id, "داخلية", "رسم→صوت"))
        edges.append(SLineEdge(sound_id, func_id, "داخلية", "صوت→وظيفة"))
        edges.append(SLineEdge(func_id, weight_id, "داخلية", "وظيفة→وزن"))

        # Sequential sound edge
        if prev_sound_id:
            edges.append(SLineEdge(prev_sound_id, sound_id, "تحويلية", "تسلسل"))
        prev_sound_id = sound_id

        trace.append(f"node_built:{rasm_id}")

    return SLineGraph(
        nodes=nodes,
        edges=edges,
        word_ref_type="داخلي",
        trace=trace,
    )


def link_internal_refs(graph: SLineGraph) -> SLineGraph:
    """Add internal cross-layer reference edges (already done in build)."""
    return graph


def link_transform_refs(graph: SLineGraph, transform_map: Optional[Dict[str, str]] = None) -> SLineGraph:
    """
    Add transformational reference edges based on phonological alternations.
    transform_map: {source_node_id: target_node_id}
    """
    if transform_map:
        for src, tgt in transform_map.items():
            graph.edges.append(SLineEdge(src, tgt, "تحويلية", "تبادل_صوتي"))
            graph.trace.append(f"transform_edge:{src}→{tgt}")
    return graph


def to_dict(graph: SLineGraph) -> dict:
    """Serialize SLineGraph to dict."""
    return graph.to_dict()
