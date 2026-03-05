"""
normalizer.py — Strict Unicode normalization for diacritized Arabic text.

Inputs:  text: str, mode: str
Outputs: NormalizedText (with normalization_log trace)
"""
from __future__ import annotations

import unicodedata
import re
from typing import List

from .models import NormalizedText

# Arabic Unicode ranges
TATWEEL = "\u0640"
ARABIC_DIACRITICS = set("\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0653\u0654\u0655\u0670")

# Hamza forms
HAMZA_FORMS = {
    "\u0622": "\u0627",  # آ → ا (alef with madda)
    "\u0623": "\u0627",  # أ → ا (alef with hamza above)
    "\u0625": "\u0627",  # إ → ا (alef with hamza below)
    "\u0671": "\u0627",  # ٱ → ا (alef wasla)
    "\u0624": "\u0648",  # ؤ → و (waw with hamza)
    "\u0626": "\u064A",  # ئ → ي (yeh with hamza)
}

# Alef forms (orthographic normalization)
ALEF_FORMS = {
    "\u0622": "\u0627",
    "\u0623": "\u0627",
    "\u0625": "\u0627",
    "\u0671": "\u0627",
}

# Yeh forms
YEH_FORMS = {
    "\u0649": "\u064A",  # alef maqsura → ya
}


def strip_tatweel(text: str) -> tuple:
    """Remove tatweel (kashida) characters."""
    log = []
    if TATWEEL in text:
        text = text.replace(TATWEEL, "")
        log.append("stripped_tatweel")
    return text, log


def normalize_diacritic_order(text: str) -> tuple:
    """Reorder diacritics to canonical NFC order."""
    log = []
    normalized = unicodedata.normalize("NFC", text)
    if normalized != text:
        log.append("nfc_normalization_applied")
    return normalized, log


def normalize_hamza_forms(text: str, mode: str) -> tuple:
    """Normalize hamza/alef variants according to mode."""
    log = []
    if mode == "phonetic":
        # In phonetic mode, preserve carrier distinction
        return text, log
    if mode in ("orthographic", "weight"):
        for src, tgt in ALEF_FORMS.items():
            if src in text:
                text = text.replace(src, tgt)
                log.append(f"alef_normalized: {src!r}→{tgt!r}")
    return text, log


def normalize_alef_maqsura(text: str, mode: str) -> tuple:
    """Normalize alef maqsura (ى → ي) in non-phonetic mode."""
    log = []
    if mode != "phonetic":
        for src, tgt in YEH_FORMS.items():
            if src in text:
                text = text.replace(src, tgt)
                log.append(f"alef_maqsura_normalized: {src!r}→{tgt!r}")
    return text, log


def normalize_text(text: str, mode: str = "orthographic") -> NormalizedText:
    """
    Normalize Arabic text for analysis.

    Args:
        text: Raw Arabic text (may be diacritized).
        mode: "orthographic" | "phonetic" | "weight"

    Returns:
        NormalizedText with original, normalized, and log.
    """
    original = text
    log: List[str] = []

    text, step_log = strip_tatweel(text)
    log.extend(step_log)

    text, step_log = normalize_diacritic_order(text)
    log.extend(step_log)

    text, step_log = normalize_hamza_forms(text, mode)
    log.extend(step_log)

    text, step_log = normalize_alef_maqsura(text, mode)
    log.extend(step_log)

    if not log:
        log.append("no_changes")

    return NormalizedText(
        original_text=original,
        normalized_text=text,
        normalization_log=log,
    )
