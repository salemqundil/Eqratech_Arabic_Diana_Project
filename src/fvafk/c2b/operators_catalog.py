from __future__ import annotations

import csv
import os
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def _strip_diacritics(text: str) -> str:
    # Remove Arabic harakat/tanwin/sukun/shadda etc. Keep letters (including hamza letters).
    return "".join(
        ch for ch in unicodedata.normalize("NFC", text)
        if unicodedata.combining(ch) == 0
    ).replace("ـ", "").strip()


@dataclass(frozen=True)
class OperatorEntry:
    group_number: str
    arabic_group_name: str
    english_group_name: str
    operator: str
    purpose: str
    example: str
    note: str

    @property
    def operator_bare(self) -> str:
        return _strip_diacritics(self.operator)


class OperatorsCatalog:
    """
    Catalog of Arabic operators/particles (حروف/أدوات) loaded from a CSV.
    Used to short-circuit morphology (root/pattern) for tokens that are operators.
    """

    DEFAULT_CANDIDATE_PATHS = [
        # User-provided external dataset path (optional).
        Path("/Users/husseinhiyassat/clean_code__morphology_pipeline/data/operators_catalog_split.csv"),
        # Common local locations (optional).
        Path.cwd() / "operators_catalog_split.csv",
        Path.cwd() / "data" / "operators_catalog_split.csv",
    ]

    PREFIX_CHARS = ("و", "ف", "ب", "ك", "ل", "س")

    def __init__(self, csv_path: Optional[Path] = None) -> None:
        self.csv_path = csv_path or self._resolve_path()
        self._by_bare: Dict[str, List[OperatorEntry]] = {}
        if self.csv_path and self.csv_path.exists():
            self._load(self.csv_path)

    def _resolve_path(self) -> Optional[Path]:
        env = os.environ.get("FVAFK_OPERATORS_CSV")
        if env:
            p = Path(env).expanduser()
            if p.exists():
                return p
        for p in self.DEFAULT_CANDIDATE_PATHS:
            if p.exists():
                return p
        return None

    def _load(self, path: Path) -> None:
        with open(path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                op = (row.get("Operator") or "").strip()
                if not op:
                    continue
                entry = OperatorEntry(
                    group_number=(row.get("Group Number") or "").strip(),
                    arabic_group_name=(row.get("Arabic Group Name") or "").strip(),
                    english_group_name=(row.get("English Group Name") or "").strip(),
                    operator=op,
                    purpose=(row.get("Purpose/Usage") or "").strip(),
                    example=(row.get("Example") or "").strip(),
                    note=(row.get("Note") or "").strip(),
                )
                bare = entry.operator_bare
                self._by_bare.setdefault(bare, []).append(entry)

    def classify(self, token: str) -> Optional[Dict[str, object]]:
        """
        Return operator metadata if token is an operator (possibly prefixed by conjunctions),
        else None.
        """
        bare = _strip_diacritics(token)
        if not bare:
            return None

        # First: direct match
        direct = self._best_entry(bare)
        if direct:
            return self._format_result(token_bare=bare, prefixes="", parts=[direct])

        # Second: peel single-letter prefixes (و/ف/ب/ك/ل/س) and retry
        prefixes, remainder = self._peel_prefixes(bare)
        if remainder != bare:
            # direct remainder
            rem_entry = self._best_entry(remainder)
            if rem_entry:
                return self._format_result(token_bare=bare, prefixes=prefixes, parts=[rem_entry])

            # compound: e.g., "إنما" = "إن" + "ما" if both exist
            compound = self._compound_match(remainder)
            if compound:
                return self._format_result(token_bare=bare, prefixes=prefixes, parts=compound)

        return None

    def _best_entry(self, bare: str) -> Optional[OperatorEntry]:
        entries = self._by_bare.get(bare)
        if not entries:
            return None
        # prefer the first; CSV ordering is curated
        return entries[0]

    def _peel_prefixes(self, bare: str) -> Tuple[str, str]:
        prefixes = ""
        remainder = bare
        for _ in range(3):  # avoid stripping too much
            if remainder and remainder[0] in self.PREFIX_CHARS and len(remainder) > 1:
                prefixes += remainder[0]
                remainder = remainder[1:]
            else:
                break
        return prefixes, remainder

    def _compound_match(self, bare: str) -> Optional[List[OperatorEntry]]:
        # find a decomposition bare = op1 + op2 where both ops exist; prefer longest op1
        candidates = sorted(self._by_bare.keys(), key=len, reverse=True)
        for op1 in candidates:
            if bare.startswith(op1) and len(op1) < len(bare):
                rest = bare[len(op1):]
                if rest in self._by_bare:
                    return [self._best_entry(op1), self._best_entry(rest)]  # type: ignore[list-item]
        return None

    def _format_result(self, token_bare: str, prefixes: str, parts: List[OperatorEntry]) -> Dict[str, object]:
        primary = parts[0]
        return {
            "token_bare": token_bare,
            "prefixes": prefixes or None,
            "operator": primary.operator_bare,
            "group": {
                "number": primary.group_number or None,
                "arabic": primary.arabic_group_name or None,
                "english": primary.english_group_name or None,
            },
            "purpose": primary.purpose or None,
            "example": primary.example or None,
            "note": primary.note or None,
            "compound": [p.operator_bare for p in parts] if len(parts) > 1 else None,
            "source_path": str(self.csv_path) if self.csv_path else None,
        }


@lru_cache(maxsize=1)
def get_operators_catalog() -> OperatorsCatalog:
    return OperatorsCatalog()

