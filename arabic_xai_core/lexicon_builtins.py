"""
lexicon_builtins.py — Lookup and classify Arabic built-in (مبني) words.

Built-ins: particles, pronouns, demonstratives, relatives,
           interrogatives, conditional particles, built-in verbs.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from .models import BuiltinAnalysis, SLineGraph, WeightAnalysis

# Path to data file
_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
_LEXICON_PATH = os.path.join(_DATA_DIR, "mabni_lexicon.json")

# Built-in lexicon (loaded once)
_LEXICON: Optional[Dict[str, Any]] = None


def _load_lexicon() -> Dict[str, Any]:
    global _LEXICON
    if _LEXICON is None:
        if os.path.exists(_LEXICON_PATH):
            with open(_LEXICON_PATH, encoding="utf-8") as f:
                _LEXICON = json.load(f)
        else:
            _LEXICON = _get_default_lexicon()
    return _LEXICON


def _get_default_lexicon() -> Dict[str, Any]:
    """Minimal built-in lexicon (fallback if data file missing)."""
    return {
        "particles": {
            "في": {"type": "حرف_جر", "function": "ظرفية", "weight_bearing": False},
            "على": {"type": "حرف_جر", "function": "استعلاء", "weight_bearing": False},
            "من": {"type": "حرف_جر", "function": "ابتداء", "weight_bearing": False},
            "إلى": {"type": "حرف_جر", "function": "انتهاء", "weight_bearing": False},
            "الواو": {"type": "حرف_عطف", "function": "عطف", "weight_bearing": False},
            "ثم": {"type": "حرف_عطف", "function": "ترتيب", "weight_bearing": False},
            "لا": {"type": "حرف_نفي", "function": "نفي", "weight_bearing": False},
            "ما": {"type": "حرف_نفي", "function": "نفي", "weight_bearing": False},
            "لم": {"type": "حرف_جزم", "function": "نفي_جزم", "weight_bearing": False},
            "لن": {"type": "حرف_نصب", "function": "نفي_نصب", "weight_bearing": False},
            "أن": {"type": "حرف_مصدري", "function": "مصدرية", "weight_bearing": False},
            "إن": {"type": "حرف_شرط", "function": "شرط", "weight_bearing": False},
            "قد": {"type": "حرف_تحقيق", "function": "تحقيق", "weight_bearing": False},
        },
        "pronouns": {
            "هو": {"type": "ضمير_منفصل", "function": "مبتدأ", "weight_bearing": True},
            "هي": {"type": "ضمير_منفصل", "function": "مبتدأ", "weight_bearing": True},
            "هم": {"type": "ضمير_منفصل", "function": "مبتدأ", "weight_bearing": True},
            "هن": {"type": "ضمير_منفصل", "function": "مبتدأ", "weight_bearing": True},
            "أنا": {"type": "ضمير_منفصل", "function": "مبتدأ", "weight_bearing": True},
            "نحن": {"type": "ضمير_منفصل", "function": "مبتدأ", "weight_bearing": True},
            "أنت": {"type": "ضمير_منفصل", "function": "مبتدأ", "weight_bearing": True},
            "أنتم": {"type": "ضمير_منفصل", "function": "مبتدأ", "weight_bearing": True},
        },
        "demonstratives": {
            "هذا": {"type": "اسم_إشارة", "function": "إشارة_قريب", "weight_bearing": True},
            "هذه": {"type": "اسم_إشارة", "function": "إشارة_قريب", "weight_bearing": True},
            "ذلك": {"type": "اسم_إشارة", "function": "إشارة_بعيد", "weight_bearing": True},
            "تلك": {"type": "اسم_إشارة", "function": "إشارة_بعيد", "weight_bearing": True},
        },
        "relatives": {
            "الذي": {"type": "اسم_موصول", "function": "وصل", "weight_bearing": True},
            "التي": {"type": "اسم_موصول", "function": "وصل", "weight_bearing": True},
            "الذين": {"type": "اسم_موصول", "function": "وصل", "weight_bearing": True},
        },
        "interrogatives": {
            "من": {"type": "اسم_استفهام", "function": "استفهام_عاقل", "weight_bearing": True},
            "ما": {"type": "اسم_استفهام", "function": "استفهام_غير_عاقل", "weight_bearing": True},
            "متى": {"type": "اسم_استفهام", "function": "استفهام_زمان", "weight_bearing": True},
            "أين": {"type": "اسم_استفهام", "function": "استفهام_مكان", "weight_bearing": True},
            "كيف": {"type": "اسم_استفهام", "function": "استفهام_حال", "weight_bearing": True},
            "كم": {"type": "اسم_استفهام", "function": "استفهام_عدد", "weight_bearing": True},
        },
        "conditionals": {
            "إن": {"type": "أداة_شرط", "function": "شرط_جازم", "weight_bearing": False},
            "لو": {"type": "أداة_شرط", "function": "شرط_امتناعي", "weight_bearing": False},
            "كلما": {"type": "أداة_شرط", "function": "شرط_كلما", "weight_bearing": False},
            "من": {"type": "أداة_شرط", "function": "شرط_عاقل", "weight_bearing": False},
            "مهما": {"type": "أداة_شرط", "function": "شرط_غير_عاقل", "weight_bearing": False},
        },
        "mabni_verbs": {
            "كان": {"type": "فعل_مبني", "function": "كان_ناقص", "weight_bearing": True},
            "ليس": {"type": "فعل_مبني", "function": "نفي_حال", "weight_bearing": True},
        },
    }


def lookup_builtin(word: str) -> Optional[Dict[str, Any]]:
    """Look up a word in the built-in lexicon. Returns entry or None."""
    lexicon = _load_lexicon()
    # Strip diacritics for lookup
    bare = _strip_diacritics(word)
    for category, entries in lexicon.items():
        if bare in entries:
            entry = dict(entries[bare])
            entry["category"] = category
            return entry
    return None


def _strip_diacritics(text: str) -> str:
    """Remove Arabic diacritics for bare-form lookup."""
    diacritics = set("\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0653\u0654\u0655\u0670")
    return "".join(c for c in text if c not in diacritics)


def is_functional_builtin(word: str, entry: Optional[Dict[str, Any]] = None) -> bool:
    """Return True if word is a functional (non-eventive) built-in."""
    if entry is None:
        entry = lookup_builtin(word)
    if entry is None:
        return False
    return entry.get("category") in ("particles", "conditionals")


def is_eventive_builtin(word: str, entry: Optional[Dict[str, Any]] = None) -> bool:
    """Return True if word is an eventive (verb-like) built-in."""
    if entry is None:
        entry = lookup_builtin(word)
    if entry is None:
        return False
    return entry.get("category") == "mabni_verbs"


def classify_mabni(
    word: str,
    sline_graph: Optional[SLineGraph] = None,
    weight_analysis: Optional[WeightAnalysis] = None,
) -> BuiltinAnalysis:
    """
    Classify whether a word is مبني and determine its type/function.
    """
    trace: List[str] = []
    entry = lookup_builtin(word)

    if entry is None:
        trace.append(f"not_found_in_lexicon:{word}")
        return BuiltinAnalysis(is_mabni=False, trace=trace)

    mabni_type = entry.get("type", "")
    function = entry.get("function", "")
    is_weight_bearing = entry.get("weight_bearing", False)
    category = entry.get("category", "")

    # Override weight_bearing from actual weight_analysis if available
    if weight_analysis is not None:
        is_weight_bearing = weight_analysis.valid_weight
        trace.append(f"weight_override:{is_weight_bearing}")

    sline_ref_class = "وظيفي" if is_functional_builtin(word, entry) else "حدثي"

    trace.append(f"found_in:{category}")
    trace.append(f"type:{mabni_type}")
    trace.append(f"function:{function}")

    return BuiltinAnalysis(
        is_mabni=True,
        mabni_type=mabni_type,
        function=function,
        is_weight_bearing=is_weight_bearing,
        sline_ref_class=sline_ref_class,
        trace=trace,
    )
