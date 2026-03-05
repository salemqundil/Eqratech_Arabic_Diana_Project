"""
morph_gate.py — Initial morphological gate: jamid/mushtaq, mujarrad/mazid, 3-letter/4-letter.

This is the morphological analysis entrypoint that uses weight/s-line/builtin analysis.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

from .models import (
    BuiltinAnalysis, MorphAnalysis, SLineGraph, WeightAnalysis,
)

_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
_PATTERNS_PATH = os.path.join(_DATA_DIR, "past_mujarrad_patterns.json")

# Arabic diacritics
FATHA  = "\u064E"
KASRA  = "\u0650"
DAMMA  = "\u064F"
SUKUN  = "\u0652"

# حروف الزيادة (augmentative letters) — traditional Arabic mnemonic: أسألتمنوي
# (ا، س، أ، ل، ت، م، ن، و، ي) — these 9 letters can appear as additions in derived forms
EXTRA_LETTERS = set("أسألتمنوي")

# Long vowel carriers (potential ziyada)
LONG_VOWEL_CHARS = set("\u0627\u0648\u064A")  # ا و ي


def _strip_diacritics(text: str) -> str:
    """Remove Arabic diacritics."""
    diacritics = set("\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0653\u0654\u0655\u0670")
    return "".join(c for c in text if c not in diacritics)


def _load_patterns() -> List[Dict[str, Any]]:
    """Load past mujarrad patterns from data file."""
    if os.path.exists(_PATTERNS_PATH):
        with open(_PATTERNS_PATH, encoding="utf-8") as f:
            return json.load(f)
    return _get_default_patterns()


def _get_default_patterns() -> List[Dict[str, Any]]:
    """Default past mujarrad patterns (ماضي مجرد)."""
    return [
        # Trilateral
        {"pattern": "فَعَلَ", "vowel_seq": [FATHA, FATHA, FATHA], "tri_quad": "ثلاثي", "mujarrad": True},
        {"pattern": "فَعِلَ", "vowel_seq": [FATHA, KASRA, FATHA], "tri_quad": "ثلاثي", "mujarrad": True},
        {"pattern": "فَعُلَ", "vowel_seq": [FATHA, DAMMA, FATHA], "tri_quad": "ثلاثي", "mujarrad": True},
        # Quadrilateral
        {"pattern": "فَعْلَلَ", "vowel_seq": [FATHA, SUKUN, FATHA, FATHA], "tri_quad": "رباعي", "mujarrad": True},
    ]


def detect_root_skeleton(
    normalized_text: str,
    sline_graph: Optional[SLineGraph] = None,
) -> Tuple[str, List[str]]:
    """
    Extract the root skeleton (consonants) from normalized text.
    Returns (root_skeleton, trace).
    """
    trace: List[str] = []
    bare = _strip_diacritics(normalized_text)
    # Remove alef wasla/lam (definite article)
    if bare.startswith("ال"):
        bare = bare[2:]
        trace.append("removed_definite_article")

    # Identify root consonants (exclude long vowel carriers if they appear to be ziyada)
    root_chars: List[str] = []
    for ch in bare:
        if ch not in LONG_VOWEL_CHARS:
            root_chars.append(ch)
        else:
            trace.append(f"skipped_possible_ziyada:{ch}")

    root = "".join(root_chars)
    trace.append(f"root_skeleton:{root}")
    return root, trace


def mark_original_extra_transform(
    normalized_text: str,
) -> Tuple[Dict[str, List[str]], List[str]]:
    """
    Mark each character in the word as:
    - أصلي (original/root consonant)
    - زائد (extra/augmentative)
    - تحويلي (transformational)
    Returns (classification_dict, trace).
    """
    trace: List[str] = []
    bare = _strip_diacritics(normalized_text)
    classification: Dict[str, List[str]] = {"أصلي": [], "زائد": [], "تحويلي": []}

    for i, ch in enumerate(bare):
        if ch in LONG_VOWEL_CHARS:
            classification["زائد"].append(f"{i}:{ch}")
            trace.append(f"char[{i}]={ch}→زائد")
        else:
            classification["أصلي"].append(f"{i}:{ch}")
            trace.append(f"char[{i}]={ch}→أصلي")

    return classification, trace


def match_past_mujarrad_patterns(
    normalized_text: str,
) -> Tuple[Optional[str], Optional[str], List[str]]:
    """
    Match normalized text against known past mujarrad patterns.
    Returns (matched_pattern, tri_or_quad, trace).
    """
    trace: List[str] = []
    patterns = _load_patterns()

    # Extract vowel sequence from normalized text
    diacritics_in_text = [ch for ch in normalized_text
                          if ch in {FATHA, KASRA, DAMMA, SUKUN}]
    root, _ = detect_root_skeleton(normalized_text)
    root_len = len(root)

    trace.append(f"root_length:{root_len}")
    trace.append(f"vowel_seq:{diacritics_in_text}")

    for pat in patterns:
        pat_vowels = pat["vowel_seq"]
        pat_tri = pat["tri_quad"]
        pat_len = 3 if pat_tri == "ثلاثي" else 4

        if root_len == pat_len and diacritics_in_text[:len(pat_vowels)] == pat_vowels:
            trace.append(f"matched_pattern:{pat['pattern']}")
            return pat["pattern"], pat_tri, trace

    trace.append("no_pattern_matched")
    return None, None, trace


def classify_mujarrad_vs_mazid(
    normalized_text: str,
    tri_or_quad: Optional[str],
    sline_graph: Optional[SLineGraph] = None,
) -> Tuple[str, List[str]]:
    """
    Determine if word is مجرد (simple) or مزيد (augmented).
    Returns (mujarrad_or_mazid, trace).
    """
    trace: List[str] = []
    classification, mark_trace = mark_original_extra_transform(normalized_text)
    trace.extend(mark_trace)

    extra_count = len(classification["زائد"])
    original_count = len(classification["أصلي"])

    trace.append(f"أصلي_count:{original_count}")
    trace.append(f"زائد_count:{extra_count}")

    if extra_count == 0:
        trace.append("verdict:مجرد (no_extra_letters)")
        return "مجرد", trace
    else:
        trace.append(f"verdict:مزيد (extra_letters={extra_count})")
        return "مزيد", trace


def classify_tri_quad(root: str) -> Tuple[str, List[str]]:
    """Classify root as trilateral or quadrilateral."""
    trace: List[str] = []
    length = len(root)
    if length <= 3:
        trace.append(f"root_len={length}→ثلاثي")
        return "ثلاثي", trace
    elif length == 4:
        trace.append(f"root_len={length}→رباعي")
        return "رباعي", trace
    else:
        trace.append(f"root_len={length}→غير_محدد")
        return "غير_محدد", trace


def analyze_morphology(
    normalized_text: str,
    sline_graph: Optional[SLineGraph] = None,
    weight_analysis: Optional[WeightAnalysis] = None,
    builtin_analysis: Optional[BuiltinAnalysis] = None,
) -> MorphAnalysis:
    """
    Run the morphological gate: detect root, pattern, tri/quad, mujarrad/mazid.

    Returns MorphAnalysis with full evidence trace.
    """
    evidence: List[str] = []

    # If it's a built-in (مبني), skip morphological analysis
    if builtin_analysis and builtin_analysis.is_mabni:
        evidence.append("مبني_skipped_morph")
        return MorphAnalysis(
            evidence_trace=evidence,
            jamid_or_mushtaq="جامد",
        )

    root, root_trace = detect_root_skeleton(normalized_text, sline_graph)
    evidence.extend(root_trace)

    matched_pattern, tri_quad_from_pattern, pattern_trace = match_past_mujarrad_patterns(normalized_text)
    evidence.extend(pattern_trace)

    tri_quad, tq_trace = classify_tri_quad(root)
    evidence.extend(tq_trace)
    if tri_quad_from_pattern:
        tri_quad = tri_quad_from_pattern
        evidence.append(f"tri_quad_from_pattern:{tri_quad}")

    mujarrad_or_mazid, mm_trace = classify_mujarrad_vs_mazid(normalized_text, tri_quad, sline_graph)
    evidence.extend(mm_trace)

    # Jamid vs mushtaq: heuristic (مبدئي)
    jamid_or_mushtaq = "غير_محدد"
    if matched_pattern:
        jamid_or_mushtaq = "جامد" if mujarrad_or_mazid == "مجرد" else "مشتق"
        evidence.append(f"jamid_heuristic:{jamid_or_mushtaq}")

    return MorphAnalysis(
        root_candidate=root,
        pattern_candidate=matched_pattern or "",
        tri_or_quad=tri_quad,
        mujarrad_or_mazid=mujarrad_or_mazid,
        jamid_or_mushtaq=jamid_or_mushtaq,
        evidence_trace=evidence,
    )
