# -*- coding: utf-8 -*-
"""
Load linguistic data from data/linguistic/ (CSV/JSON).
Cached so files are read once. Graceful fallbacks when files are missing.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# Project root: src/fvafk/linguistic_data/loader.py -> 4 parents
_DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "linguistic"


def _path(name: str) -> Path:
    return _DATA_DIR / name


# ---------------------------------------------------------------------------
# Phonetic
# ---------------------------------------------------------------------------

_phonetic_cache: Dict[str, Any] | None = None


def load_phonetic() -> Dict[str, Any]:
    """Load phonetic.json; return dict with str and list values. Build sets in __init__."""
    global _phonetic_cache
    if _phonetic_cache is not None:
        return _phonetic_cache
    p = _path("phonetic.json")
    if not p.exists():
        _phonetic_cache = {}
        return _phonetic_cache
    with open(p, encoding="utf-8") as f:
        _phonetic_cache = json.load(f)
    return _phonetic_cache


# ---------------------------------------------------------------------------
# CSV list files (list_name, value [, notes])
# ---------------------------------------------------------------------------

def _load_csv_lists(filename: str, value_col: str = "value", list_col: str = "list_name") -> Dict[str, List[str]]:
    """Return dict mapping list_name -> [value, ...] (order preserved)."""
    out: Dict[str, List[str]] = {}
    p = _path(filename)
    if not p.exists():
        return out
    with open(p, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            list_name = (row.get(list_col) or "").strip()
            val = (row.get(value_col) or "").strip()
            if not list_name:
                continue
            if list_name not in out:
                out[list_name] = []
            if val:
                out[list_name].append(val)
    return out


_morphology_lists_cache: Dict[str, List[str]] | None = None


def load_morphology_lists() -> Dict[str, List[str]]:
    """Morphology lists: IMPERFECT_CHARS, ISTAFAL_PATTERNS, ISTAFAL_VERBS, NOUN_EXCEPTIONS, FULL_WORD_EXCEPTIONS."""
    global _morphology_lists_cache
    if _morphology_lists_cache is not None:
        return _morphology_lists_cache
    _morphology_lists_cache = _load_csv_lists("morphology_lists.csv")
    return _morphology_lists_cache


_classification_lists_cache: Dict[str, List[str]] | None = None


def load_classification_lists() -> Dict[str, List[str]]:
    """Classification lists: DISJUNCTIVE_PRONOUNS, CONCRETE_NOUNS, PROPER_NOUNS, etc."""
    global _classification_lists_cache
    if _classification_lists_cache is not None:
        return _classification_lists_cache
    _classification_lists_cache = _load_csv_lists("classification_lists.csv")
    return _classification_lists_cache


_wazn_lists_cache: Dict[str, List[str]] | None = None


def load_wazn_lists() -> Dict[str, List[str]]:
    """Wazn lists: PAST_TENSE_WAZANS, IMPERATIVE_WAZANS, etc."""
    global _wazn_lists_cache
    if _wazn_lists_cache is not None:
        return _wazn_lists_cache
    _wazn_lists_cache = _load_csv_lists("wazn_lists.csv", value_col="wazn")
    return _wazn_lists_cache


# ---------------------------------------------------------------------------
# Allowed target tags (single column)
# ---------------------------------------------------------------------------

_allowed_target_tags_cache: Set[str] | None = None


def load_allowed_target_tags() -> Set[str]:
    """Set of allowed morph tags for matching."""
    global _allowed_target_tags_cache
    if _allowed_target_tags_cache is not None:
        return _allowed_target_tags_cache
    out: Set[str] = set()
    p = _path("allowed_target_tags.csv")
    if not p.exists():
        _allowed_target_tags_cache = out
        return out
    with open(p, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        tag_col = "tag"
        for row in reader:
            t = (row.get(tag_col) or "").strip()
            if t:
                out.add(t)
    _allowed_target_tags_cache = out
    return out


# ---------------------------------------------------------------------------
# Special compounds: word -> list of (text, tag)
# ---------------------------------------------------------------------------

_special_compounds_cache: Dict[str, List[Tuple[str, str]]] | None = None


def load_special_compounds() -> Dict[str, List[Tuple[str, str]]]:
    """Word -> list of (segment_text, tag). Tuples for compatibility with segmenter."""
    global _special_compounds_cache
    if _special_compounds_cache is not None:
        return _special_compounds_cache
    p = _path("special_compounds.json")
    if not p.exists():
        _special_compounds_cache = {}
        return _special_compounds_cache
    with open(p, encoding="utf-8") as f:
        raw = json.load(f)
    result: Dict[str, List[Tuple[str, str]]] = {}
    for word, pairs in raw.items():
        result[word] = [tuple(p) for p in pairs]
    _special_compounds_cache = result
    return result


# ---------------------------------------------------------------------------
# Morph tag/style mappings (CSV -> dict)
# ---------------------------------------------------------------------------

def _load_csv_mapping(filename: str, key_col: str, val_col: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    p = _path(filename)
    if not p.exists():
        return out
    with open(p, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            k = (row.get(key_col) or "").strip()
            v = (row.get(val_col) or "").strip()
            if k:
                out[k] = v
    return out


_morph_tag_to_wasm_cache: Dict[str, str] | None = None


def load_morph_tag_to_wasm() -> Dict[str, str]:
    """MORPH_TAG -> Arabic wasm."""
    global _morph_tag_to_wasm_cache
    if _morph_tag_to_wasm_cache is not None:
        return _morph_tag_to_wasm_cache
    _morph_tag_to_wasm_cache = _load_csv_mapping("morph_tag_to_wasm.csv", "morph_tag", "wasm_ar")
    return _morph_tag_to_wasm_cache


_morph_type_to_naw3_cache: Dict[str, str] | None = None


def load_morph_type_to_naw3() -> Dict[str, str]:
    """MORPH_TYPE -> Arabic naw3."""
    global _morph_type_to_naw3_cache
    if _morph_type_to_naw3_cache is not None:
        return _morph_type_to_naw3_cache
    _morph_type_to_naw3_cache = _load_csv_mapping("morph_type_to_naw3.csv", "morph_type", "naw3_ar")
    return _morph_type_to_naw3_cache
