"""
models.py — Shared data models for arabic_xai_core pipeline.

All pipeline stages communicate via these typed structures,
each carrying a `trace` list for XAI explainability.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ── Sprint 1: Text ────────────────────────────────────────────────────────────

@dataclass
class NormalizedText:
    original_text: str
    normalized_text: str
    normalization_log: List[str] = field(default_factory=list)


@dataclass
class GraphemeCluster:
    base_char: str
    diacritics: List[str] = field(default_factory=list)
    position: int = 0          # index inside word
    word_index: int = 0        # word index inside text

    @property
    def full(self) -> str:
        return self.base_char + "".join(self.diacritics)


@dataclass
class ExpandedUnit:
    base_char: str
    role: str                  # e.g. "consonant", "vowel", "functional"
    value: str                 # phonemic value / mark
    expansion_trace: List[str] = field(default_factory=list)
    position: int = 0
    word_index: int = 0


# ── Sprint 2: Phonology / S-Line / Syllable ───────────────────────────────────

@dataclass
class PhonoUnit:
    symbol: str
    unit_type: str             # "صامت" | "صائت" | "شبه_صائت"
    makhraj: str = ""
    sifa: List[str] = field(default_factory=list)
    can_shift_role: bool = False
    position: int = 0
    word_index: int = 0
    trace: List[str] = field(default_factory=list)


@dataclass
class SLineNode:
    node_id: str
    symbol: str
    layer: str                 # "رسم" | "صوت" | "وظيفة" | "وزن"
    features: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SLineEdge:
    source_id: str
    target_id: str
    edge_type: str             # "داخلية" | "تحويلية" | "تركيبية"
    label: str = ""


@dataclass
class SLineGraph:
    nodes: List[SLineNode] = field(default_factory=list)
    edges: List[SLineEdge] = field(default_factory=list)
    word_ref_type: str = ""
    trace: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [{"id": n.node_id, "symbol": n.symbol, "layer": n.layer,
                        "features": n.features} for n in self.nodes],
            "edges": [{"src": e.source_id, "tgt": e.target_id,
                        "type": e.edge_type, "label": e.label} for e in self.edges],
            "word_ref_type": self.word_ref_type,
            "trace": self.trace,
        }


@dataclass
class Syllable:
    pattern: str               # e.g. "CV", "CVC", "CVV"
    units: List[str] = field(default_factory=list)
    node_ids: List[str] = field(default_factory=list)
    is_valid: bool = True
    validity_notes: List[str] = field(default_factory=list)


@dataclass
class SyllableAnalysis:
    syllables: List[Syllable] = field(default_factory=list)
    syllable_map: Dict[str, str] = field(default_factory=dict)  # node_id → syllable index
    trace: List[str] = field(default_factory=list)


# ── Sprint 3: Weight / Builtins / Morph ──────────────────────────────────────

@dataclass
class WeightUnit:
    node_id: str
    symbol: str
    weight_role: str           # "حامل_وزن" | "محقق_وزن" | "دون_وزن"
    reason: str = ""


@dataclass
class WeightAnalysis:
    weight_units: List[WeightUnit] = field(default_factory=list)
    weight_unit_count: int = 0
    below_weight: bool = False
    valid_weight: bool = False
    trace: List[str] = field(default_factory=list)


@dataclass
class BuiltinAnalysis:
    is_mabni: bool = False
    mabni_type: str = ""
    function: str = ""
    is_weight_bearing: bool = False
    sline_ref_class: str = ""
    trace: List[str] = field(default_factory=list)


@dataclass
class MorphAnalysis:
    root_candidate: str = ""
    pattern_candidate: str = ""
    tri_or_quad: str = ""      # "ثلاثي" | "رباعي" | ""
    mujarrad_or_mazid: str = "" # "مجرد" | "مزيد" | ""
    jamid_or_mushtaq: str = "" # "جامد" | "مشتق" | ""
    evidence_trace: List[str] = field(default_factory=list)


# ── Sprint 4: Proof ───────────────────────────────────────────────────────────

@dataclass
class Claim:
    claim_id: str
    text: str
    verdict: str               # "مثبت" | "منفي" | "غير_محدد"
    confidence: float = 1.0
    premises: List[str] = field(default_factory=list)
    reasoning_steps: List[str] = field(default_factory=list)
    trace_ids: List[str] = field(default_factory=list)


@dataclass
class ProofReport:
    word: str
    claims: List[Claim] = field(default_factory=list)
    overall_confidence: float = 1.0
    trace: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "word": self.word,
            "claims": [
                {
                    "id": c.claim_id,
                    "text": c.text,
                    "verdict": c.verdict,
                    "confidence": c.confidence,
                    "premises": c.premises,
                    "reasoning_steps": c.reasoning_steps,
                    "trace_ids": c.trace_ids,
                }
                for c in self.claims
            ],
            "overall_confidence": self.overall_confidence,
            "trace": self.trace,
        }
