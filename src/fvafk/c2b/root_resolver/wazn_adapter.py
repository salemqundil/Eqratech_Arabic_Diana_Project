# -*- coding: utf-8 -*-
"""
WaznAdapter: bridges WaznMatcher with RootResolver.
Builds candidates (stripped, word_no_al if shadda, word_cleaned), tries patterns, extracts root on FULLMATCH only.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .wazn_matcher import (
    get_fal_indices,
    load_patterns,
    MatchHit,
    remove_al_and_shadda,
    split_units,
    try_match_pattern_to_word,
)

SHADDA = "\u0651"


def extract_root_from_hit(word_processed: str, hit: MatchHit) -> Optional[str]:
    """Extract root letters from word_processed using ف ع ل indices from the pattern."""
    units = split_units(word_processed)
    fal_indices = get_fal_indices(hit.pattern)
    if not fal_indices:
        return None
    letters = []
    for i in fal_indices:
        idx = hit.window_start + i
        if idx < len(units):
            letters.append(units[idx].base)
    return "".join(letters) if letters else None


@dataclass
class WaznResult:
    root: str
    wazn: str
    match_type: str
    window_start: int


class WaznAdapter:
    def __init__(self, patterns: List[str]) -> None:
        self._patterns = patterns

    @property
    def patterns_count(self) -> int:
        return len(self._patterns)

    @classmethod
    def load(cls, patterns_csv: str | Path) -> "WaznAdapter":
        path = Path(patterns_csv)
        patterns = load_patterns(str(path))
        return cls(patterns)

    def resolve(self, word: str, stripped: str = "") -> Optional[WaznResult]:
        candidates: List[str] = []
        if stripped and stripped.strip():
            candidates.append(stripped.strip())
        if SHADDA in word:
            word_no_al = re.sub(r"^[وفبكل]?ال", "", word).strip()
            if word_no_al and word_no_al not in candidates:
                candidates.append(word_no_al)
        word_cleaned = remove_al_and_shadda(word)
        if word_cleaned not in candidates:
            candidates.append(word_cleaned)

        for cand in candidates:
            result = self._try_resolve(cand, word)
            if result:
                return result
        return None

    def _try_resolve(self, word_processed: str, original_word: str) -> Optional[WaznResult]:
        hit: Optional[MatchHit] = None
        for pattern in self._patterns:
            hits = try_match_pattern_to_word(pattern, word_processed)
            if hits:
                hit = hits[0]
                break
        if hit is None:
            return None
        if hit.reason != "FULLMATCH":
            return None
        fal_indices = get_fal_indices(hit.pattern)
        if not fal_indices:
            return None
        root = extract_root_from_hit(word_processed, hit)
        if not root:
            return None
        return WaznResult(
            root=root,
            wazn=hit.pattern,
            match_type=hit.reason,
            window_start=hit.window_start,
        )
