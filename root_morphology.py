"""
Interactive root dictionary and derivation generator.

This module loads Arabic roots from a spreadsheet (or fallback sample),
builds a searchable repository, and provides utilities to generate
derivations while tracking vowels and augmentation letters.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import numpy as np
import pandas as pd

from comprehensive_arabic_generator import ArabicMatrixGenerator, MorphologicalGenerator
from src.syllables import syllabify


DEFAULT_ROOT_DATA = [
    {
        "root": "كتب",
        "category": "ثلاثي",
        "gloss": "to write",
        "patterns": "فَعَلَ;مَفْعُول;تَفْعِيل",
        "sample_derivations": "كَتَبَ;كُتِبَ;كَاتِب;مَكْتُوب;تَكْتِيب",
        "notes": "جذر قياسي متعدد الاشتقاقات",
    },
    {
        "root": "علم",
        "category": "ثلاثي",
        "gloss": "to know / to learn",
        "patterns": "فَعِلَ;فَعْل;مُفَاعَلَة",
        "sample_derivations": "عَلِمَ;عِلم;عَالِم;مَعْلُوم;مُعَالَمَة",
        "notes": "يتداخل مع باب التعليم والمعرفة",
    },
    {
        "root": "دحرج",
        "category": "رباعي",
        "gloss": "to roll",
        "patterns": "فَعْلَلَ;تَفَعْلَلَ",
        "sample_derivations": "دَحْرَجَ;تَدَحْرَجَ;مُدَحْرِج",
        "notes": "جذر رباعي مزيد",
    },
]

HARAKAT_MAP = {"َ": "F", "ُ": "D", "ِ": "K"}
IGNORED_SIGNS = {"ْ", "ّ"}
LONG_VOWELS = {"ا", "و", "ي", "آ", "ى"}
GATE_DURATION = {
    "CV": 1.0,
    "CVC": 1.5,
    "CVV": 2.0,
    "CVVC": 2.5,
    "CVCC": 2.5,
    "VC": 1.0,
    "CCV": 1.5,
    "V": 1.0,
}


def _split_field(value: object) -> List[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    if isinstance(value, (list, tuple)):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value)
    if ";" in text:
        parts = text.split(";")
    elif "," in text:
        parts = text.split(",")
    else:
        parts = [text]
    return [p.strip() for p in parts if p.strip()]


@dataclass
class RootEntry:
    root: str
    category: str
    gloss: str
    patterns: List[str]
    sample_derivations: List[str]
    notes: str

    def to_record(self) -> Dict[str, object]:
        return {
            "root": self.root,
            "category": self.category,
            "gloss": self.gloss,
            "patterns": "; ".join(self.patterns),
            "sample_derivations": "; ".join(self.sample_derivations),
            "notes": self.notes,
        }


class RootMorphologyDictionary:
    """Smart look-up dictionary for Arabic roots."""

    REQUIRED_COLUMNS = ("root", "category", "gloss", "patterns", "sample_derivations", "notes")

    def __init__(self, dataframe: pd.DataFrame) -> None:
        self._df = self._normalize_dataframe(dataframe.copy())
        self._entries: Dict[str, RootEntry] = {}
        for _, row in self._df.iterrows():
            entry = RootEntry(
                root=row["root"],
                category=row["category"],
                gloss=row["gloss"],
                patterns=_split_field(row["patterns"]),
                sample_derivations=_split_field(row["sample_derivations"]),
                notes=row["notes"],
            )
            self._entries[entry.root] = entry

    @classmethod
    def from_excel(cls, path: str | Path, use_fallback: bool = True) -> "RootMorphologyDictionary":
        path = Path(path)
        df: Optional[pd.DataFrame] = None
        if path.exists():
            try:
                df = pd.read_excel(path, engine="openpyxl")
            except Exception:
                if not use_fallback:
                    raise
        if df is None:
            if not use_fallback:
                raise FileNotFoundError(f"Unable to load root data from {path}")
            df = pd.DataFrame(DEFAULT_ROOT_DATA)
        return cls(df)

    @staticmethod
    def _normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        for col in RootMorphologyDictionary.REQUIRED_COLUMNS:
            if col not in df.columns:
                df[col] = ""
        df = df[list(RootMorphologyDictionary.REQUIRED_COLUMNS)]
        df["root"] = df["root"].astype(str).str.strip()
        df["category"] = df["category"].astype(str).str.strip()
        df["gloss"] = df["gloss"].astype(str).str.strip()
        df["notes"] = df["notes"].astype(str).str.strip()
        df = df.dropna(subset=["root"])
        df = df[df["root"] != ""]
        return df.drop_duplicates(subset=["root"]).reset_index(drop=True)

    def lookup(self, root: str) -> Optional[RootEntry]:
        return self._entries.get(root)

    def search(self, substring: str) -> pd.DataFrame:
        substring = substring.strip()
        if not substring:
            return self._df.copy()
        mask = self._df["root"].str.contains(substring) | self._df["gloss"].str.contains(substring)
        return self._df[mask].reset_index(drop=True)

    def to_dataframe(self) -> pd.DataFrame:
        return self._df.copy()

    def roots(self) -> List[str]:
        return list(self._entries.keys())


class RootDerivationGenerator:
    """Generate derivations from roots while tracking vowels and augmentation letters."""

    def __init__(self, matrix: Optional[ArabicMatrixGenerator] = None) -> None:
        self.matrix = matrix or ArabicMatrixGenerator()
        self.morph_gen = MorphologicalGenerator(self.matrix)
        self.canonical_gates: Dict[str, List[str]] = self._build_canonical_gates()

    def generate(
        self,
        root: str,
        weight_names: Optional[Iterable[str]] = None,
        include_augmented: bool = True,
    ) -> pd.DataFrame:
        weight_filter = set(weight_names) if weight_names else None
        records: List[Dict[str, object]] = []

        for category, weights in self.matrix.morphological_weights.items():
            for weight_name, weight_info in weights.items():
                if weight_filter and weight_name not in weight_filter:
                    continue
                form = self.morph_gen.apply_weight_to_root(root, weight_info["template"])
                if not form:
                    continue
                records.append(
                    self._build_record(
                        root=root,
                        form=form,
                        weight=weight_name,
                        category=category,
                    )
                )

        if include_augmented:
            base_forms = [rec["form"] for rec in records]
            augmented_records = []
            for form in base_forms:
                for letter in self.matrix.augmentation_letters:
                    augmented_form = f"{letter}{form}"
                    augmented_records.append(
                        self._build_record(
                            root=root,
                            form=augmented_form,
                            weight="augmented",
                            category="augmentation",
                        )
                    )
            records.extend(augmented_records)

        return pd.DataFrame(records).drop_duplicates(subset=["form"]).reset_index(drop=True)

    def _build_record(self, root: str, form: str, weight: str, category: str) -> Dict[str, object]:
        vowels = [ch for ch in form if ch in LONG_VOWELS or ch in HARAKAT_MAP]
        augmentations = [ch for ch in form if ch in self.matrix.augmentation_letters]
        gates = self._extract_gates(form)
        canonical = self.canonical_gates.get(weight)
        dtw_cost = self._dtw_cost(gates, canonical) if canonical else None
        return {
            "root": root,
            "form": form,
            "weight": weight,
            "category": category,
            "vowels": "".join(vowels),
            "augmentation_letters": "".join(augmentations),
            "length": len(form),
            "gates": " ".join(gates),
            "dtw_cost": dtw_cost,
            "phoneme_tokens": " ".join(self._phoneme_tokens(form)),
            "byte_tokens": " ".join(str(b) for b in form.encode("utf-8")),
        }

    def _extract_gates(self, form: str) -> List[str]:
        seq = self._split_form(form)
        try:
            return syllabify(seq)
        except Exception:
            return []

    def _split_form(self, form: str) -> List[tuple[str, str]]:
        out: List[tuple[str, str]] = []
        for ch in form:
            if ch in HARAKAT_MAP and out:
                base, _ = out[-1]
                out[-1] = (base, HARAKAT_MAP[ch])
            elif ch in IGNORED_SIGNS:
                continue
            else:
                out.append((ch, ""))
        return out

    def _phoneme_tokens(self, form: str) -> List[str]:
        tokens: List[str] = []
        for ch in form:
            if ch in HARAKAT_MAP:
                tokens.append(HARAKAT_MAP[ch])
            elif ch in IGNORED_SIGNS:
                tokens.append(ch)
            else:
                tokens.append(ch)
        return tokens

    def _build_canonical_gates(self) -> Dict[str, List[str]]:
        canonical: Dict[str, List[str]] = {}
        sample_root_tri = "فعل"
        sample_root_quad = "فعلل"
        for weights in self.matrix.morphological_weights.values():
            for weight_name, weight_info in weights.items():
                template = weight_info["template"]
                if "C4" in template:
                    sample = self.morph_gen.apply_weight_to_root(sample_root_quad, template)
                else:
                    sample = self.morph_gen.apply_weight_to_root(sample_root_tri, template)
                if not sample:
                    continue
                gates = self._extract_gates(sample)
                if gates:
                    canonical[weight_name] = gates
        return canonical

    def _dtw_cost(self, gates: List[str], canonical: Optional[List[str]]) -> Optional[float]:
        if not gates or not canonical:
            return None
        a = np.array([GATE_DURATION.get(g, 1.0) for g in gates], dtype=float)
        b = np.array([GATE_DURATION.get(g, 1.0) for g in canonical], dtype=float)
        n, m = len(a), len(b)
        dp = np.full((n + 1, m + 1), np.inf)
        dp[0, 0] = 0.0
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                cost = abs(a[i - 1] - b[j - 1])
                dp[i, j] = cost + min(dp[i - 1, j], dp[i, j - 1], dp[i - 1, j - 1])
        return float(dp[n, m])


def build_root_dictionary(path: str | Path) -> RootMorphologyDictionary:
    return RootMorphologyDictionary.from_excel(path)


__all__ = [
    "RootEntry",
    "RootMorphologyDictionary",
    "RootDerivationGenerator",
    "build_root_dictionary",
]
