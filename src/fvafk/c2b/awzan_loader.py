from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .morpheme import PatternType


class AwzanPatternLoader:
    # Preferred awzan file (new default)
    # 1) Package-local copy (when you want it under src/fvafk/phonology/)
    #    This is the primary awzan source for the project.
    CSV_PATH_PHONOLOGY_CLEAN = (
        Path(__file__).resolve().parents[1] / "phonology" / "awzan_merged_final_clean.csv"
    )
    # 2) Optional full table (kept as fallback)
    CSV_PATH_PHONOLOGY_FULL = (
        Path(__file__).resolve().parents[1] / "phonology" / "awzan_merged_final.csv"
    )
    # 2) Project-level data/ (default for this repo)
    CSV_PATH = Path(__file__).resolve().parents[3] / "data" / "awzan_merged_final.csv"
    # Legacy fallback (kept for compatibility)
    CSV_PATH_LEGACY = Path(__file__).resolve().parents[3] / "awzan-claude-atwah.csv"

    _cache: Optional[List[dict]] = None

    PATTERN_TYPE_MAP: Dict[str, PatternType] = {
        "فَعَلَ": PatternType.FORM_I,
        "فَعِلَ": PatternType.FORM_I,
        "فَعُلَ": PatternType.FORM_I,
        "فَعَّلَ": PatternType.FORM_II,
        "فَاعَلَ": PatternType.FORM_III,
        "أَفْعَلَ": PatternType.FORM_IV,
        "تَفَعَّلَ": PatternType.FORM_V,
        "تَفَاعَلَ": PatternType.FORM_VI,
        "انْفَعَلَ": PatternType.FORM_VII,
        "افْتَعَلَ": PatternType.FORM_VIII,
        "اسْتَفْعَلَ": PatternType.FORM_X,
        "مَفْعُول": PatternType.PASSIVE_PARTICIPLE,
        "فَاعِل": PatternType.ACTIVE_PARTICIPLE,
        "مَفْعَل": PatternType.PLACE_TIME_NOUN,
        "فِعَال": PatternType.VERBAL_NOUN,
        "فَعِيل": PatternType.INTENSIVE,
        "أَفْعَل": PatternType.ELATIVE,
        "فَاعِلُون": PatternType.SOUND_MASCULINE_PLURAL,
        "فَاعِلِين": PatternType.SOUND_MASCULINE_PLURAL,
        "فَاعِلَات": PatternType.SOUND_FEMININE_PLURAL,
        "فُعُول": PatternType.BROKEN_PLURAL_FUUL,
        # Broken plural on فُعُل (e.g., كُتُب)
        "فُعُل": PatternType.BROKEN_PLURAL_FUUL,
        # High-impact broken plurals (Qur'anic frequent)
        "فُعَّل": PatternType.BROKEN_PLURAL_FU33AL,  # رُكَّع، سُجَّد
        "فُعَلَاء": PatternType.BROKEN_PLURAL_FU3ALAA,  # عُلَمَاء
        "فُعَلَاءُ": PatternType.BROKEN_PLURAL_FU3ALAA,  # رُحَمَاءُ
        "فِعَال": PatternType.BROKEN_PLURAL_FIAAL,
        "أَفْعَال": PatternType.BROKEN_PLURAL_AFAAL,
        "فِعَل": PatternType.BROKEN_PLURAL_FIUL,
        "فَعِيْلَة": PatternType.INTENSIVE,
        "فَعِيل": PatternType.INTENSIVE,
        "مَفْعَلَة": PatternType.PLACE_TIME_NOUN,
        "مِفْعَال": PatternType.PLACE_TIME_NOUN,
        # Present plural for Form VIII (افتعل) – keep as FORM_VIII type
        "يَفْتَعِلُونَ": PatternType.FORM_VIII,
        # Present tense templates (Qur'anic frequent)
        "يُفْعِلُ": PatternType.FORM_IV,      # يُعْجِبُ
        "يُفْعِلُون": PatternType.FORM_IV,
        "يُفْعِلُونَ": PatternType.FORM_IV,
    }

    _VERB_FORM_LABELS: Dict[PatternType, str] = {
        PatternType.FORM_I: "I",
        PatternType.FORM_II: "II",
        PatternType.FORM_III: "III",
        PatternType.FORM_IV: "IV",
        PatternType.FORM_V: "V",
        PatternType.FORM_VI: "VI",
        PatternType.FORM_VII: "VII",
        PatternType.FORM_VIII: "VIII",
        PatternType.FORM_IX: "IX",
        PatternType.FORM_X: "X",
    }

    @classmethod
    def _form_from_pattern_type(cls, pattern_type: PatternType) -> Optional[str]:
        """Derive form label (e.g. 'I', 'II') from pattern type when CSV has no الاسم."""
        return cls._VERB_FORM_LABELS.get(pattern_type)

    @classmethod
    def load(cls) -> List[dict]:
        if cls._cache is not None:
            return cls._cache
        patterns: List[dict] = []
        # FORCE: Use only data/awzan_merged_final.csv
        csv_path = cls.CSV_PATH
        if not csv_path.exists():
            cls._cache = patterns
            return cls._cache
        with open(csv_path, encoding="utf-8-sig", newline="") as handle:
            sample = handle.read(2048)
            handle.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",\t")
                delimiter = dialect.delimiter
            except Exception:
                # Default to comma for the merged file shape.
                delimiter = ","
            reader = csv.DictReader(handle, delimiter=delimiter)
            seen: Set[str] = set()
            for row in reader:
                template = (row.get("الوزن") or "").strip()
                if not template or template in seen:
                    continue
                seen.add(template)
                pattern_type = cls.PATTERN_TYPE_MAP.get(template, PatternType.UNKNOWN)
                category = cls._infer_category(row, pattern_type)
                raw_form = (row.get("الاسم") or "").strip()
                form = raw_form or cls._form_from_pattern_type(pattern_type) or "unknown"
                entry = {
                    "template": template,
                    "pattern_type": pattern_type,
                    "category": category,
                    "form": form,
                    "meaning": row.get("الوصف", "unknown"),
                    "cv_simple": row.get("CV") or None,
                    "cv_detailed": row.get("Detailed_CV", "unknown"),
                    "cv_advanced": row.get("Advanced_CV", "unknown"),
                    "notes": row.get("ملاحظات", "unknown"),
                }
                patterns.append(entry)
                # فِعَال is both verbal noun (مصدر) and broken plural; add noun entry so كِتَاب matches as verbal noun first
                if template == "فِعَال":
                    patterns.append({
                        **entry,
                        "pattern_type": PatternType.VERBAL_NOUN,
                        "category": "noun",
                    })
        cls._cache = patterns
        return cls._cache

    @staticmethod
    def _infer_category(row: Dict[str, str], pattern_type: PatternType) -> str:
        label = (row.get("الاسم") or "").strip()
        description = (row.get("الوصف") or "").strip()
        if "جمع" in label or "جمع" in description:
            return "plural"
        if description.startswith("اسم") or label.startswith("اسم") or "صفة" in description:
            return "noun"
        if pattern_type in {
            PatternType.SOUND_MASCULINE_PLURAL,
            PatternType.SOUND_FEMININE_PLURAL,
            PatternType.BROKEN_PLURAL_AFAAL,
            PatternType.BROKEN_PLURAL_FIAAL,
            PatternType.BROKEN_PLURAL_FUUL,
            PatternType.BROKEN_PLURAL_FIUL,
        }:
            return "plural"
        if pattern_type in {
            PatternType.ACTIVE_PARTICIPLE,
            PatternType.PASSIVE_PARTICIPLE,
            PatternType.VERBAL_NOUN,
            PatternType.INTENSIVE,
            PatternType.ELATIVE,
            PatternType.PLACE_TIME_NOUN,
        }:
            return "noun"
        if pattern_type != PatternType.UNKNOWN:
            return "verb"
        return "noun"
