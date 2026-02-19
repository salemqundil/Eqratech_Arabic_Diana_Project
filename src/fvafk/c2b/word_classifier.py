"""
Word classification layer (Plan A).

This module provides a small, explicit classifier for:
- operators/particles (closed class) via OperatorsCatalog
- detached pronouns via a small lexicon
- verb vs noun heuristics using PatternType when available

It is intentionally minimal and testable. Plan B can later refine classification
using syllable-derived evidence.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Tuple

from .morpheme import PatternType
from .operators_catalog import OperatorsCatalog, get_operators_catalog
from .special_words_catalog import SpecialWordsCatalog, get_special_words_catalog


def _strip_diacritics(text: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFC", text)
        if unicodedata.combining(ch) == 0
    ).replace("ـ", "").strip()


class WordKind(str, Enum):
    OPERATOR = "operator"
    DEMONSTRATIVE = "demonstrative"
    NAME = "name"
    PARTICLE = "particle"
    PRONOUN = "pronoun"
    VERB = "verb"
    NOUN = "noun"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Classification:
    kind: WordKind
    operator: Optional[Dict[str, Any]] = None
    special: Optional[Dict[str, Any]] = None
    pronoun: Optional[Dict[str, Any]] = None


_DETACHED_PRONOUNS: Dict[str, Dict[str, Any]] = {
    # 1st person
    "انا": {"person": 1, "number": "singular"},
    "نحن": {"person": 1, "number": "plural"},
    # 2nd person (gender may be ambiguous after diacritics stripping)
    "انت": {"person": 2, "number": "singular"},
    "انتما": {"person": 2, "number": "dual"},
    "انتم": {"person": 2, "number": "plural", "gender": "masculine"},
    "انتن": {"person": 2, "number": "plural", "gender": "feminine"},
    # 3rd person
    "هو": {"person": 3, "number": "singular", "gender": "masculine"},
    "هي": {"person": 3, "number": "singular", "gender": "feminine"},
    "هما": {"person": 3, "number": "dual"},
    "هم": {"person": 3, "number": "plural", "gender": "masculine"},
    "هن": {"person": 3, "number": "plural", "gender": "feminine"},
}


_ATTACHED_PRONOUN_SUFFIXES: Dict[str, Dict[str, Any]] = {
    "ه": {"person": 3, "number": "singular", "gender": "masculine"},
    "ها": {"person": 3, "number": "singular", "gender": "feminine"},
    "هما": {"person": 3, "number": "dual"},
    "هم": {"person": 3, "number": "plural", "gender": "masculine"},
    "هن": {"person": 3, "number": "plural", "gender": "feminine"},
    "ك": {"person": 2, "number": "singular"},
    "كم": {"person": 2, "number": "plural", "gender": "masculine"},
    "كن": {"person": 2, "number": "plural", "gender": "feminine"},
    "كما": {"person": 2, "number": "dual"},
    "نا": {"person": 1, "number": "plural"},
    "ني": {"person": 1, "number": "singular"},
    "ي": {"person": 1, "number": "singular"},
}


_VERB_FORMS = {
    PatternType.FORM_I,
    PatternType.FORM_II,
    PatternType.FORM_III,
    PatternType.FORM_IV,
    PatternType.FORM_V,
    PatternType.FORM_VI,
    PatternType.FORM_VII,
    PatternType.FORM_VIII,
    PatternType.FORM_IX,
    PatternType.FORM_X,
}


class WordClassifier:
    def __init__(
        self,
        operators: Optional[OperatorsCatalog] = None,
        special: Optional[SpecialWordsCatalog] = None,
    ) -> None:
        self._operators = operators or get_operators_catalog()
        self._special = special or get_special_words_catalog()

    def classify(
        self,
        token: str,
        *,
        pattern_type: Optional[PatternType] = None,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
    ) -> Classification:
        if not token:
            return Classification(kind=WordKind.UNKNOWN)

        # 1) operators/particles (closed class)
        op = self._operators.classify(token)
        if op:
            return Classification(kind=WordKind.OPERATOR, operator=op)

        # 2) special closed-class / excluded names / demonstratives from external lexicons
        sp = self._special.classify(token)
        if sp:
            sp_kind = (sp.get("kind") or "").lower()
            if sp_kind == "demonstrative":
                return Classification(kind=WordKind.DEMONSTRATIVE, special=sp)
            if sp_kind == "excluded_name":
                return Classification(kind=WordKind.NAME, special=sp)
            if sp_kind in {"particle", "special"}:
                return Classification(kind=WordKind.PARTICLE, special=sp)

        bare = _strip_diacritics(token)
        if not bare:
            return Classification(kind=WordKind.UNKNOWN)

        # 3) preposition/particle + attached pronoun clitics (generic closed pattern)
        # Examples: بهم، به، معه، عليهم، منهم ...
        clitic = self.detect_attached_pronoun_suffix(bare)
        if clitic:
            suf, suf_feats = clitic
            base = bare[: -len(suf)]
            # Common prepositions/particles that take a clitic object
            prep_bases = {
                "ب",
                "ك",
                "ل",
                "في",
                "من",
                "عن",
                "على",
                "إلى",
                "الي",
                "مع",
                "لدى",
                "عند",
                "بين",
            }
            if base in prep_bases:
                return Classification(
                    kind=WordKind.PARTICLE,
                    special={
                        "token_bare": bare,
                        "kind": "particle",
                        "category": "PREP_CLITIC",
                        "base": base,
                        "attached_pronoun": {"suffix": suf, **suf_feats},
                        "source_path": "builtin",
                    },
                )
            # If token begins with an imperfect marker and ends with an attached pronoun,
            # it is very likely a verb (e.g., تراهم، يراهم...).
            if bare and bare[0] in {"ي", "ت", "ن", "أ"} and len(bare) >= 3:
                return Classification(kind=WordKind.VERB)

        # 3) detached pronouns
        pron = _DETACHED_PRONOUNS.get(bare)
        if pron:
            return Classification(kind=WordKind.PRONOUN, pronoun={"surface": token, "bare": bare, **pron})

        # 4) content word: verb vs noun via pattern_type when available
        if pattern_type and pattern_type in _VERB_FORMS:
            return Classification(kind=WordKind.VERB)

        # 5) verb heuristics from affixes when no pattern matched
        # Past plural: ...وا (e.g., آمنوا، عملوا)
        suf_tail = (suffix or "").split("+")[-1] if suffix else ""
        if suf_tail == "وا":
            return Classification(kind=WordKind.VERB)
        # Present plural: ي...ون / ت...ون / ن...ون / أ...ون (e.g., يبتغون)
        if suf_tail in {"ون", "ين"} and prefix:
            parts = set(prefix.split("+"))
            if parts & {"ي", "ت", "ن", "أ"}:
                return Classification(kind=WordKind.VERB)
        # Present singular: imperfect marker appears in extracted prefix
        # Examples: (ف+س+ي)+... , (ي)+...
        if prefix:
            parts = set(prefix.split("+"))
            if parts & {"ي", "ت", "ن", "أ"}:
                return Classification(kind=WordKind.VERB)

        # Default noun for normal-length tokens.
        if len(bare) >= 2:
            return Classification(kind=WordKind.NOUN)

        return Classification(kind=WordKind.UNKNOWN)

    def detect_attached_pronoun_suffix(self, token: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Return (suffix, features) if token ends with an attached pronoun suffix.
        This does not classify the whole token as a pronoun; it only detects clitics.
        """
        bare = _strip_diacritics(token)
        if len(bare) < 2:
            return None

        # Prefer longest suffix match.
        for suf in sorted(_ATTACHED_PRONOUN_SUFFIXES.keys(), key=len, reverse=True):
            if bare.endswith(suf) and len(bare) > len(suf):
                return suf, dict(_ATTACHED_PRONOUN_SUFFIXES[suf])
        return None

