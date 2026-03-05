# -*- coding: utf-8 -*-
"""
قاعدة البيانات اللغوية - تُحمّل من data/linguistic/
Linguistic Data - Loaded from CSV/JSON; same API as the original constants module.
"""

from __future__ import annotations

from typing import Dict, List, Set, Tuple

from .loader import (
    load_allowed_target_tags,
    load_classification_lists,
    load_morph_tag_to_wasm,
    load_morph_type_to_naw3,
    load_morphology_lists,
    load_phonetic,
    load_special_compounds,
    load_wazn_lists,
)

# ---------------------------------------------------------------------------
# Phonetic constants
# ---------------------------------------------------------------------------

_ph = load_phonetic()

FATHA = _ph.get("FATHA", "\u064e")
DAMMA = _ph.get("DAMMA", "\u064f")
KASRA = _ph.get("KASRA", "\u0650")
SHORT_VOWELS: Set[str] = set(_ph.get("SHORT_VOWELS", []))

TANWEEN_FATH = _ph.get("TANWEEN_FATH", "\u064b")
TANWEEN_DAMM = _ph.get("TANWEEN_DAMM", "\u064c")
TANWEEN_KASR = _ph.get("TANWEEN_KASR", "\u064d")
TANWEEN: Set[str] = set(_ph.get("TANWEEN", []))

SHADDA = _ph.get("SHADDA", "\u0651")
SUKOON: Set[str] = set(_ph.get("SUKOON", []))
ALEF_WASLA = _ph.get("ALEF_WASLA", "\u0671")
HAMZA_QATA = _ph.get("HAMZA_QATA", "\u0623")

VALID_PATTERNS: Set[str] = set(_ph.get("VALID_PATTERNS", []))

# ---------------------------------------------------------------------------
# Morphology lists (sets for membership tests)
# ---------------------------------------------------------------------------

_ml = load_morphology_lists()


def _as_set(name: str) -> Set[str]:
    return set(_ml.get(name, []))


IMPERFECT_CHARS: Set[str] = _as_set("IMPERFECT_CHARS")
ISTAFAL_PATTERNS: Set[str] = _as_set("ISTAFAL_PATTERNS")
ISTAFAL_VERBS: Set[str] = _as_set("ISTAFAL_VERBS")
NOUN_EXCEPTIONS: Set[str] = _as_set("NOUN_EXCEPTIONS")
FULL_WORD_EXCEPTIONS: Set[str] = _as_set("FULL_WORD_EXCEPTIONS")

# ---------------------------------------------------------------------------
# Special compounds (word -> list of (text, tag))
# ---------------------------------------------------------------------------

SPECIAL_COMPOUNDS: Dict[str, List[Tuple[str, str]]] = load_special_compounds()

# ---------------------------------------------------------------------------
# Allowed target tags
# ---------------------------------------------------------------------------

ALLOWED_TARGET_TAGS: Set[str] = load_allowed_target_tags()

# ---------------------------------------------------------------------------
# Classification lists (order preserved for display/iteration)
# ---------------------------------------------------------------------------

_cl = load_classification_lists()


def _as_list(name: str) -> List[str]:
    return list(_cl.get(name, []))


DISJUNCTIVE_PRONOUNS: List[str] = _as_list("DISJUNCTIVE_PRONOUNS")
CONCRETE_NOUNS: List[str] = _as_list("CONCRETE_NOUNS")
PROPER_NOUNS: List[str] = _as_list("PROPER_NOUNS")
VERBAL_NOUNS_BASE: List[str] = _as_list("VERBAL_NOUNS_BASE")
ACTIVE_PARTICIPLES: List[str] = _as_list("ACTIVE_PARTICIPLES")
PASSIVE_PARTICIPLES: List[str] = _as_list("PASSIVE_PARTICIPLES")

# ---------------------------------------------------------------------------
# Wazn lists (order preserved)
# ---------------------------------------------------------------------------

_wl = load_wazn_lists()


def _wazn_list(name: str) -> List[str]:
    return list(_wl.get(name, []))


PAST_TENSE_WAZANS: List[str] = _wazn_list("PAST_TENSE_WAZANS")
IMPERATIVE_WAZANS: List[str] = _wazn_list("IMPERATIVE_WAZANS")
PRESENT_TENSE_WAZANS: List[str] = _wazn_list("PRESENT_TENSE_WAZANS")
VERBAL_NOUN_WAZANS: List[str] = _wazn_list("VERBAL_NOUN_WAZANS")
ACTIVE_PARTICIPLE_WAZANS: List[str] = _wazn_list("ACTIVE_PARTICIPLE_WAZANS")
PASSIVE_PARTICIPLE_WAZANS: List[str] = _wazn_list("PASSIVE_PARTICIPLE_WAZANS")

# ---------------------------------------------------------------------------
# Morph tag/type mappings
# ---------------------------------------------------------------------------

MORPH_TAG_TO_WASM: Dict[str, str] = load_morph_tag_to_wasm()
MORPH_TYPE_TO_NAW3: Dict[str, str] = load_morph_type_to_naw3()
