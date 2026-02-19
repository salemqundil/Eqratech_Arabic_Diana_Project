from __future__ import annotations

import csv
import os
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional, Tuple


def _strip_diacritics(text: str) -> str:
    # Remove harakat/tanwin/sukun/shadda etc. Keep letters (including hamza letters).
    return "".join(
        ch for ch in unicodedata.normalize("NFC", text)
        if unicodedata.combining(ch) == 0
    ).replace("ـ", "").strip()


@dataclass(frozen=True)
class SpecialEntry:
    kind: str  # excluded_name | demonstrative | particle | prep_combo | special
    category: Optional[str] = None
    root_hint: Optional[str] = None
    status: Optional[str] = None
    source_path: Optional[str] = None


class SpecialWordsCatalog:
    """
    Loads external lexicons to prevent false-positive morphology:
    - golden_name_base.csv: excluded names (no root extraction)
    - no_root_jawamed-new.csv: jawamed/no-root words (no root extraction)
    - additional_excludes.csv: categories (DEMONSTRATIVE/PARTICLE/PREP_*) with root hints
    """

    DEFAULT_GOLDEN_NAMES = Path(
        "/Users/husseinhiyassat/clean_code__morphology_pipeline/data/golden_name_base.csv"
    )
    DEFAULT_ADDITIONAL_EXCLUDES = Path(
        "/Users/husseinhiyassat/clean_code__morphology_pipeline/data/additional_excludes.csv"
    )
    DEFAULT_NO_ROOT_JAWAMED = Path(
        "/Users/husseinhiyassat/clean_code__morphology_pipeline/data/no_root_jawamed-new.csv"
    )

    def __init__(
        self,
        *,
        golden_names_csv: Optional[Path] = None,
        additional_excludes_csv: Optional[Path] = None,
        no_root_jawamed_csv: Optional[Path] = None,
    ) -> None:
        self._map: Dict[str, SpecialEntry] = {}

        golden = golden_names_csv or self._resolve_env("FVAFK_GOLDEN_NAMES_CSV") or self.DEFAULT_GOLDEN_NAMES
        additional = additional_excludes_csv or self._resolve_env("FVAFK_ADDITIONAL_EXCLUDES_CSV") or self.DEFAULT_ADDITIONAL_EXCLUDES
        jawamed = no_root_jawamed_csv or self._resolve_env("FVAFK_NO_ROOT_JAWAMED_CSV") or self.DEFAULT_NO_ROOT_JAWAMED

        self._load_golden_names(golden)
        self._load_no_root_jawamed(jawamed)
        self._load_additional_excludes(additional)

        # Built-in minimal demonstratives (fallback even if CSV absent)
        for demo in ("ذلك", "هذه", "هذا", "هؤلاء", "تلك", "أولئك", "هنالك", "هناك", "كذا"):
            self._map.setdefault(
                demo,
                SpecialEntry(kind="demonstrative", category="DEMONSTRATIVE", source_path="builtin"),
            )

        # Built-in relatives / closed-class pronouns (prevent false morphology)
        for rel in (
            "الذي",
            "التي",
            "اللذين",
            "الذين",
            "اللتين",
            "اللاتي",
            "اللائي",
            "اللواتي",
            "من",
            "ما",
        ):
            self._map.setdefault(
                rel,
                SpecialEntry(kind="particle", category="RELATIVE", source_path="builtin"),
            )

    def _resolve_env(self, key: str) -> Optional[Path]:
        val = os.environ.get(key)
        if not val:
            return None
        p = Path(val).expanduser()
        return p if p.exists() else None

    def classify(self, token: str) -> Optional[Dict[str, object]]:
        bare = _strip_diacritics(token)
        if not bare:
            return None
        entry = self._map.get(bare)
        prefixes = ""
        # Peel conjunction-like prefixes (و/ف) and retry for closed-class words.
        # This helps cases like: والذين / فذلك / وذلك ...
        if not entry and len(bare) > 2 and bare[0] in {"و", "ف"}:
            prefixes, remainder = self._peel_prefixes(bare)
            if remainder and remainder != bare:
                entry = self._map.get(remainder)
        if not entry:
            return None
        return {
            "token_bare": bare,
            "kind": entry.kind,
            "category": entry.category,
            "root_hint": entry.root_hint,
            "status": entry.status,
            "prefixes": prefixes or None,
            "source_path": entry.source_path,
        }

    def _peel_prefixes(self, bare: str) -> Tuple[str, str]:
        prefixes = ""
        remainder = bare
        for _ in range(2):
            if remainder and remainder[0] in {"و", "ف"} and len(remainder) > 1:
                prefixes += remainder[0]
                remainder = remainder[1:]
            else:
                break
        return prefixes, remainder

    def _load_additional_excludes(self, path: Path) -> None:
        if not path.exists():
            return
        try:
            with open(path, encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    word = (row.get("Word_Clean") or "").strip()
                    if not word:
                        continue
                    bare = _strip_diacritics(word)
                    category = (row.get("Category") or "").strip() or None
                    root_hint = (row.get("Root") or "").strip() or None
                    kind = "special"
                    if category == "DEMONSTRATIVE":
                        kind = "demonstrative"
                    elif category and (category.startswith("PREP_") or category == "PARTICLE" or category == "ALLAH_COMBO"):
                        kind = "particle"
                    self._map[bare] = SpecialEntry(
                        kind=kind,
                        category=category,
                        root_hint=root_hint,
                        source_path=str(path),
                    )
        except Exception:
            # best-effort: ignore file errors
            return

    def _load_no_root_jawamed(self, path: Path) -> None:
        if not path.exists():
            return
        try:
            with open(path, encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    word = (row.get("Word_Clean") or "").strip()
                    status = (row.get("Status") or "").strip() or None
                    if not word:
                        continue
                    bare = _strip_diacritics(word)
                    self._map.setdefault(
                        bare,
                        SpecialEntry(
                            kind="excluded_name",
                            status=status or "NO_ROOT",
                            source_path=str(path),
                        ),
                    )
        except Exception:
            return

    def _load_golden_names(self, path: Path) -> None:
        if not path.exists():
            return
        try:
            # This file is not a clean CSV; parse lines defensively.
            with open(path, encoding="utf-8-sig") as f:
                for raw in f:
                    line = raw.strip()
                    if not line:
                        continue
                    # skip obvious header lines
                    if line.lower().startswith("word"):
                        continue
                    if "Word_Clean" in line and "Status" in line:
                        continue
                    # likely tab-separated: WORD <TAB> STATUS <TAB> COUNT
                    parts = [p.strip() for p in line.split("\t") if p.strip()]
                    if len(parts) < 2:
                        # fallback: comma-separated
                        parts = [p.strip() for p in line.split(",") if p.strip()]
                    if len(parts) < 2:
                        continue
                    word, status = parts[0], parts[1]
                    if not word:
                        continue
                    bare = _strip_diacritics(word)
                    if not bare:
                        continue
                    self._map.setdefault(
                        bare,
                        SpecialEntry(
                            kind="excluded_name",
                            status=status or "EXCLUDED",
                            source_path=str(path),
                        ),
                    )
        except Exception:
            return


@lru_cache(maxsize=1)
def get_special_words_catalog() -> SpecialWordsCatalog:
    return SpecialWordsCatalog()

