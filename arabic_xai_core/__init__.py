"""
arabic_xai_core — Explainable Arabic NLP Pipeline
10-module XAI pipeline: normalizer → grapheme_parser → composite_expander →
phonology_map → sline_core → syllable_engine → weight_engine →
lexicon_builtins → morph_gate → prover
"""

from .models import (
    NormalizedText, GraphemeCluster, ExpandedUnit, PhonoUnit,
    SLineNode, SLineEdge, SLineGraph,
    Syllable, SyllableAnalysis,
    WeightAnalysis, BuiltinAnalysis, MorphAnalysis, ProofReport,
)
from .normalizer import normalize_text
from .grapheme_parser import parse_graphemes
from .composite_expander import expand_units
from .phonology_map import classify_phonounits
from .sline_core import build_sline_for_word
from .syllable_engine import build_syllables
from .weight_engine import extract_weight_units
from .lexicon_builtins import classify_mabni
from .morph_gate import analyze_morphology
from .prover import build_proof_report

__all__ = [
    "NormalizedText", "GraphemeCluster", "ExpandedUnit", "PhonoUnit",
    "SLineNode", "SLineEdge", "SLineGraph",
    "Syllable", "SyllableAnalysis", "WeightAnalysis", "BuiltinAnalysis",
    "MorphAnalysis", "ProofReport",
    "normalize_text", "parse_graphemes", "expand_units",
    "classify_phonounits", "build_sline_for_word", "build_syllables",
    "extract_weight_units", "classify_mabni", "analyze_morphology",
    "build_proof_report",
]
