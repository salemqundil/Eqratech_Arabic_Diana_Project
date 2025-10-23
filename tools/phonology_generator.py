# -*- coding: utf-8 -*-
"""Phonology generator with gate sequences, OCP filtering, and (al) assimilation reports."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, List, Dict, Tuple, Optional
import csv
import argparse
import sys
import json
from pathlib import Path

A, I, U, S = "A", "I", "U", "S"
DIAC = {A: "َ", I: "ِ", U: "ُ", S: "ْ"}
DIAC_NAME = {A: "Fatha", I: "Kasra", U: "Damma", S: "Sukun"}
DEFAULT_C = list("فعل")
VERB_TRI_ALLOWED = [(A, A), (A, I), (A, U)]
NOUN_TRI_ALLOWED = [(A, S), (A, A), (U, S), (U, A), (I, S), (A, I), (A, U)]
NOUN_LABEL = {
    (A, S): "fa3l",
    (A, A): "fa3al",
    (U, S): "fu3l",
    (U, A): "fu3al",
    (I, S): "fi3l",
    (A, I): "fa3il",
    (A, U): "fa3ul",
}
SOLAR = tuple("تثدذرزسشصضطظلن")
LUNAR = tuple("أبجحخعغفقكمهوئيآوىةؤئ")
SHADDA = "ّ"
HARAKAT = {"a": "َ", "i": "ِ", "u": "ُ"}
SHORTS = set(DIAC.values()) - {DIAC[S]}
LONGS = set("اويآى")


def is_solar(ch: str) -> bool:
    return ch in SOLAR


def is_lunar(ch: str) -> bool:
    return (ch in LUNAR) and not is_solar(ch)


def is_cons(ch: str) -> bool:
    return bool(ch) and ch not in SHORTS and ch not in LONGS and ch != SHADDA


def is_short(ch: str) -> bool:
    return ch in SHORTS


def is_long(ch: str) -> bool:
    return ch in LONGS


def _graphemes(surface: str) -> List[str]:
    return list(surface)


def syllabify_segments(surface: str) -> Tuple[List[str], List[str]]:
    ch = _graphemes(surface)
    tokens: List[Tuple[str, int, int]] = []
    i = 0
    while i < len(ch):
        c = ch[i]
        if is_long(c):
            tokens.append(("V", i, i + 1))
            i += 1
            continue
        if is_cons(c):
            if i + 1 < len(ch) and is_short(ch[i + 1]):
                tokens.append(("CV", i, i + 2))
                i += 2
                continue
            tokens.append(("C", i, i + 1))
            i += 1
            continue
        i += 1

    gates: List[str] = []
    segs: List[str] = []
    j = 0
    n = len(tokens)

    def span(a, b):
        return surface[a:b]

    while j < n:
        t = tokens[j][0]
        if t == "V" and j + 1 < n and tokens[j + 1][0] == "C":
            gates.append("VC")
            segs.append(span(tokens[j][1], tokens[j + 1][2]))
            j += 2
            continue
        if t == "CV":
            if j + 1 < n and tokens[j + 1][0] == "V":
                if j + 2 < n and tokens[j + 2][0] == "C":
                    gates.append("CVVC")
                    segs.append(span(tokens[j][1], tokens[j + 2][2]))
                    j += 3
                    continue
                gates.append("CVV")
                segs.append(span(tokens[j][1], tokens[j + 1][2]))
                j += 2
                continue
            if j + 1 < n and tokens[j + 1][0] == "C":
                if j + 2 < n and tokens[j + 2][0] == "C":
                    gates.append("CVCC")
                    segs.append(span(tokens[j][1], tokens[j + 2][2]))
                    j += 3
                    continue
                gates.append("CVC")
                segs.append(span(tokens[j][1], tokens[j + 1][2]))
                j += 2
                continue
            gates.append("CV")
            segs.append(span(tokens[j][1], tokens[j][2]))
            j += 1
            continue
        if t == "C":
            if j + 1 < n and tokens[j + 1][0] == "V":
                if j + 2 < n and tokens[j + 2][0] == "C":
                    gates.append("CVVC")
                    segs.append(span(tokens[j][1], tokens[j + 2][2]))
                    j += 3
                    continue
                gates.append("CVV")
                segs.append(span(tokens[j][1], tokens[j + 1][2]))
                j += 2
                continue
            if j + 1 < n and tokens[j + 1][0] == "CV":
                gates.append("CVC")
                segs.append(span(tokens[j][1], tokens[j + 1][2]))
                j += 2
                continue
            if segs:
                prev = segs.pop()
                pg = gates.pop()
                segs.append(prev + span(tokens[j][1], tokens[j][2]))
                gates.append(pg if pg in ("CVC", "CVCC", "CVVC") else "CVC")
                j += 1
                continue
            gates.append("CV")
            segs.append(span(tokens[j][1], tokens[j][2]))
            j += 1
            continue
        gates.append("CV")
        segs.append(span(tokens[j][1], tokens[j][2]))
        j += 1

    cleaned = []
    for g in gates:
        if g in ("CV", "VC", "CVC", "CVV", "CVVC", "CVCC"):
            cleaned.append(g)
        elif g == "V":
            cleaned.append("VC")
        else:
            cleaned.append("CV")
    return cleaned, segs


def infer_gate_seq(surface: str) -> Tuple[str, int, str, str]:
    gates, segs = syllabify_segments(surface)
    if not gates:
        return "", 0, "", ""
    return ".".join(gates), len(gates), gates[0], "|".join(segs)


ARTIC_GROUPS_COARSE = [
    set("بمفو"),
    set("تثدذرزسصضطظنلر"),
    set("كقجش"),
    set("ءه"),
    set("عح"),
    set("غخ"),
]


def _same_artic_coarse(c1: str, c2: str) -> bool:
    for g in ARTIC_GROUPS_COARSE:
        if c1 in g and c2 in g:
            return True
    return False


def ocp_simple(surface: str) -> int:
    ch = list(surface)
    for i in range(len(ch) - 1):
        if is_cons(ch[i]) and ch[i] == ch[i + 1]:
            return 1
    for i in range(len(ch) - 1):
        if is_cons(ch[i]) and is_cons(ch[i + 1]) and _same_artic_coarse(ch[i], ch[i + 1]):
            return 1
    return 0


def load_phoneme_classes(path: Optional[Path]) -> Dict[str, str]:
    if not path or not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    mapping: Dict[str, str] = {}
    for cls, members in raw.get("classes", {}).items():
        for ch in members:
            mapping[ch] = cls
    return mapping


def load_ocp_rules(path: Optional[Path]) -> Dict[str, object]:
    if not path or not path.exists():
        return {
            "forbid_adjacent_same_class": False,
            "forbid_pairs": [],
            "forbid_same_short_vowel_in_same_class": False,
        }
    return json.loads(path.read_text(encoding="utf-8"))


def _short_on(surface: str, i: int) -> Tuple[Optional[str], Optional[str]]:
    va = surface[i + 1] if i + 1 < len(surface) and is_short(surface[i + 1]) else None
    vb = surface[i + 2] if i + 2 < len(surface) and is_short(surface[i + 2]) else None
    return va, vb


def ocp_artic(surface: str, ph2cls: Dict[str, str], rules: Dict[str, object]) -> int:
    if not ph2cls or not rules:
        return 0
    ch = list(surface)
    forbid_same_cls = bool(rules.get("forbid_adjacent_same_class", False))
    forbid_pairs = {tuple(p) for p in rules.get("forbid_pairs", []) if isinstance(p, list) and len(p) == 2}
    forbid_same_vowel_same_class = bool(rules.get("forbid_same_short_vowel_in_same_class", False))

    for i in range(len(ch) - 1):
        a, b = ch[i], ch[i + 1]
        if not (is_cons(a) and is_cons(b)):
            continue
        ca, cb = ph2cls.get(a), ph2cls.get(b)
        if not ca or not cb:
            continue
        if forbid_same_cls and ca == cb:
            return 1
        if (ca, cb) in forbid_pairs or (cb, ca) in forbid_pairs:
            return 1
        if forbid_same_vowel_same_class and ca == cb:
            va, vb = _short_on(surface, i)
            if va and vb and va == vb:
                return 1
    return 0


def apply_def_article(surface: str, vowel: str = "a") -> Dict[str, str]:
    if not surface:
        return {"with_def": "ال", "class": "other", "assimilated": "0"}
    first = surface[0]
    v = HARAKAT.get(vowel, "َ")
    if is_solar(first):
        first_shadda = first if SHADDA in first else first + SHADDA
        return {"with_def": "ا" + v + first_shadda + surface[1:], "class": "solar", "assimilated": "1"}
    return {
        "with_def": "ا" + v + "ل" + surface,
        "class": "lunar" if is_lunar(first) else "other",
        "assimilated": "0",
    }


def is_two_invalid(v1: str, v2: str) -> bool:
    return (v1, v2) in {(S, S), (S, I), (I, I)}


@dataclass
class Row:
    kind: str
    surface: str
    meta: Dict[str, str]


# TODO: Placeholder end-of-file implementation. Complete business logic if needed.
def main() -> None:
    parser = argparse.ArgumentParser(description="Phonology generator (placeholder)")
    parser.add_argument("--input", type=str, default=None, help="Optional input path")
    args = parser.parse_args()
    print("phonology_generator.py placeholder OK", "input=", args.input)


if __name__ == "__main__":
    main()
