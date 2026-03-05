"""
grapheme_parser.py — Split normalized Arabic text into GraphemeCluster units.

Each cluster = one base character + its attached diacritics.
"""
from __future__ import annotations

import re
import unicodedata
from typing import List

from .models import GraphemeCluster

# Arabic diacritics (harakat + shadda + tanween variants)
ARABIC_DIACRITICS = frozenset(
    "\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0653\u0654\u0655\u0670"
)

# Arabic letter range: U+0600–U+06FF (approximate)
def _is_arabic_letter(ch: str) -> bool:
    cp = ord(ch)
    return (0x0600 <= cp <= 0x06FF) or (0x0750 <= cp <= 0x077F)


def cluster_diacritics(word: str) -> List[GraphemeCluster]:
    """
    Parse a single word into GraphemeCluster list.
    Each base Arabic letter gathers following diacritics.
    """
    clusters: List[GraphemeCluster] = []
    i = 0
    pos = 0
    while i < len(word):
        ch = word[i]
        if ch in ARABIC_DIACRITICS:
            # orphan diacritic (shouldn't happen in well-formed text)
            i += 1
            continue
        # Base character
        diacritics: List[str] = []
        i += 1
        while i < len(word) and word[i] in ARABIC_DIACRITICS:
            diacritics.append(word[i])
            i += 1
        clusters.append(GraphemeCluster(
            base_char=ch,
            diacritics=diacritics,
            position=pos,
        ))
        pos += 1
    return clusters


def split_words(text: str) -> List[str]:
    """Split text on whitespace/punctuation into word tokens."""
    return [w for w in re.split(r"[\s\u060C\u061B\u061F\u06D4.,;:!?()\[\]]+", text) if w]


def parse_graphemes(text: str) -> List[GraphemeCluster]:
    """
    Parse normalized text into a flat list of GraphemeCluster objects.

    Each cluster records its word_index and position within the word.
    """
    words = split_words(text)
    result: List[GraphemeCluster] = []
    for word_idx, word in enumerate(words):
        clusters = cluster_diacritics(word)
        for c in clusters:
            c.word_index = word_idx
        result.extend(clusters)
    return result
