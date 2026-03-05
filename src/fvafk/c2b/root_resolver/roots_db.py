# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Set


_ARABIC_LETTER_MIN = "\u0621"
_ARABIC_LETTER_MAX = "\u064A"

# Denylist entries must be normalized (Arabic letters only, no dashes, no tashkeel)
_NON_ROOT_DENY = frozenset({
    "كنت", "قلت", "مني", "لذي",
    "علي", "عليه", "عليهم", "عليكما", "عليكم", "عليكن",
})


def _only_arabic_letters(s: str) -> str:
    return "".join(ch for ch in (s or "") if _ARABIC_LETTER_MIN <= ch <= _ARABIC_LETTER_MAX)


@dataclass(frozen=True)
class RootsDB:
    """
    Simple in-memory root database.

    Expected file format: CSV/TSV with the root in the FIRST column.
    """
    _roots: Set[str]

    @classmethod
    def load(cls, csv_path: str | Path) -> "RootsDB":
        path = Path(csv_path)

        # Determine delimiter (tab => TSV, otherwise CSV)
        first_line = ""
        with path.open("r", encoding="utf-8") as f:
            first_line = f.readline()
        delim = "\t" if "\t" in first_line else ","

        roots: Set[str] = set()
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                first_col = line.split(delim, 1)[0].strip()
                r = cls.normalize(first_col)
                if r:
                    roots.add(r)

        return cls(_roots=roots)

    @staticmethod
    def normalize(root: str) -> str:
        """
        Normalize a root representation:
        - remove dashes
        - keep Arabic letters only
        """
        r = (root or "").replace("-", "").strip()
        r = _only_arabic_letters(r)
        return r

    def is_valid(self, root: str) -> bool:
        r = self.normalize(root)
        return bool(r) and r in self._roots

    def is_rootlike(self, root: str) -> bool:
        """
        Stricter validity for *prediction*:
        - must exist in DB
        - must be 3 or 4 letters
        - must NOT be in denylist (even if present in DB)
        """
        r = self.normalize(root)
        if not r:
            return False
        if r in _NON_ROOT_DENY:
            return False
        if len(r) not in (3, 4):
            return False
        return self.is_valid(r)

    def canonicalize(self, root: str) -> str:
        """
        Canonicalize root encoding using DB-backed fixes.
        Prefer و/ي middle-letter variant when it is in DB (e.g. بون -> بين, شوء -> شيء).
        Works on roots with or without dashes.
        """
        r = self.normalize(root).replace("-", "").strip()
        if not r:
            return r

        # For 3-letter roots, try و<->ي middle variant first; prefer it when in DB
        if len(r) == 3:
            a, b, c = r[0], r[1], r[2]
            if b == "و":
                cand = a + "ي" + c
                if self.is_rootlike(cand):
                    return cand
            if b == "ي":
                cand = a + "و" + c
                if self.is_rootlike(cand):
                    return cand

        if self.is_rootlike(r):
            return r
        return r

    def __len__(self) -> int:
        return len(self._roots)

    def __contains__(self, root: str) -> bool:
        return self.is_valid(root)
