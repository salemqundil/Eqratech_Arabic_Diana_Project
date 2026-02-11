"""
Word boundary detection (Plan A).

Plan A approach:
- Detect Arabic tokens from raw text and return their character spans.
- This is a stable interface we can later upgrade (Plan B) to derive boundaries
  from a syllable/segment stream once spaces/punctuation boundaries are carried
  through C1/C2a.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable, Iterator, List, Optional, Sequence


@dataclass(frozen=True)
class TokenSpan:
    token: str
    start: int
    end: int  # end-exclusive


_ARABIC_RUN_RE = re.compile(r"[\u0600-\u06FF]+", re.UNICODE)


def _has_arabic_letter(token: str) -> bool:
    """
    Keep runs that contain at least one Arabic letter (category L).
    This filters Quranic annotation marks and punctuation that also live in the
    Arabic block.
    """
    for ch in token:
        if "\u0600" <= ch <= "\u06FF" and unicodedata.category(ch).startswith("L"):
            return True
    return False


class WordBoundaryDetector:
    def detect(self, text: str) -> List[TokenSpan]:
        spans: List[TokenSpan] = []
        if not text:
            return spans

        for m in _ARABIC_RUN_RE.finditer(text):
            token = m.group(0)
            if not token:
                continue
            if not _has_arabic_letter(token):
                continue
            spans.append(TokenSpan(token=token, start=m.start(), end=m.end()))
        return spans

    def iter_tokens(self, text: str) -> Iterator[str]:
        for span in self.detect(text):
            yield span.token

    # -------------------------
    # Plan B hook (not used yet)
    # -------------------------
    def detect_from_segments(
        self,
        segments: Sequence[object],
        *,
        syllables: Optional[Sequence[object]] = None,
    ) -> List[TokenSpan]:
        """
        Plan B hook: derive word boundaries from a segments/syllables stream.

        This requires carrying boundary markers (spaces/punct) or offsets through C1/C2a.
        Not implemented in Plan A.
        """
        return []

