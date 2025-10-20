from __future__ import annotations

from typing import Dict, Optional, Tuple

from .normalize import strip_diacritics


# Detached personal pronouns (normalized, no diacritics)
DETACHED_PRONOUNS = {
    "انا", "نحن", "انت", "انتما", "انتم", "انتن", "هو", "هي", "هما", "هم", "هن",
}

# Attached pronoun suffixes (longest first)
ATTACHED_SUFFIXES = [
    "كما", "كم", "كن", "نا", "ني", "هم", "هن", "ها", "ه", "ي",
]

# Common particles (subset)
PARTICLES = {
    "و", "ف", "ثم", "بل", "لكن", "او", "ام", "على", "من", "الى", "عن", "في", "ب", "ك", "ل", "حتى", "كي", "لان", "اذن",
}


def is_detached_pronoun(token: str) -> bool:
    base = strip_diacritics(token)
    return base in DETACHED_PRONOUNS


def match_attached_pronoun(token: str) -> Optional[str]:
    """Return the matched suffix if the token ends with an attached pronoun and has a stem before it."""
    base = strip_diacritics(token)
    for suf in ATTACHED_SUFFIXES:
        if base.endswith(suf) and len(base) > len(suf):
            return suf
    return None


def is_particle(token: str) -> bool:
    base = strip_diacritics(token)
    return base in PARTICLES


# Built noun categories (demonstratives/relatives/interrogatives) — quick filters
_TATWEEL = "\u0640"

def _norm_core(token: str) -> str:
    base = strip_diacritics(token)
    base = base.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ٱ", "ا").replace("ى", "ي").replace(_TATWEEL, "")
    return base

DEMONSTRATIVES = {
    "هذا", "هذه", "هذان", "هاتان", "هؤلاء", "ذلك", "تلك", "اولئك",
}
RELATIVES = {
    "الذي", "التي", "الذين", "اللاتي", "اللائي", "من", "ما",
}
INTERROGATIVES = {
    "من", "ما", "اين", "متى", "كيف", "كم", "اي",
}


def is_built_noun_other(token: str) -> bool:
    w = _norm_core(token)
    return (w in DEMONSTRATIVES) or (w in RELATIVES) or (w in INTERROGATIVES)


def detect_built_verb(token: str) -> Tuple[str, Optional[str]]:
    """Detect verb form and built type.

    Returns (verb_form, built_type) where built_type in {past, imperative, present_tawkid, present_niswa, None}
    and verb_form in {past, imperative, present, unknown}.
    """
    base = strip_diacritics(token)
    if not base:
        return "unknown", None

    # Past (approximate) by endings common in Arabic (educational heuristic)
    PAST_ENDINGS = ("ت", "ت", "تم", "تن", "نا", "وا", "ن")
    if base.endswith(PAST_ENDINGS):
        return "past", "past"

    # Imperative: does not start with present prefixes and has imperative endings (~)
    PRESENT_PREFIXES = ("ي", "ت", "ن", "ا")
    if not base.startswith(PRESENT_PREFIXES):
        if base.endswith(("", "ي", "ا", "وا", "ن")):
            return "imperative", "imperative"

    # Present: starts with present prefixes
    if base.startswith(PRESENT_PREFIXES):
        if base.endswith(("ن", "نّ", "نَّ")):  # nun al-niswa or emphasized forms (simplified)
            return "present", "present_niswa"
        if base.endswith(("ن", "نْ", "نَّ", "نً")) or base.endswith(("ن",)):
            # rough match for emphatic nuns; educational
            return "present", "present_tawkid"
        return "present", None

    return "unknown", None


def tag_token(token: str) -> Dict[str, Optional[str]]:
    """Return rule-based tags for a single token."""
    out: Dict[str, Optional[str]] = {
        "pos": None,
        "i3rab": None,
        "pron_type": None,
        "pron_form": None,
        "verb_form": None,
        "verb_built_type": None,
    }

    if is_detached_pronoun(token):
        out.update({"pos": "pronoun", "i3rab": "مبني", "pron_type": "detached"})
        return out

    suf = match_attached_pronoun(token)
    if suf is not None:
        out.update({"pos": "pronoun", "i3rab": "مبني", "pron_type": "attached", "pron_form": suf})
        return out

    if is_particle(token):
        out.update({"pos": "particle", "i3rab": "مبني"})
        return out

    vform, vbuilt = detect_built_verb(token)
    if vform != "unknown":
        out.update({"pos": "verb", "verb_form": vform, "verb_built_type": vbuilt, "i3rab": "مبني" if vbuilt else "معرب"})
        return out

    out.update({"pos": "none", "i3rab": None})
    return out
