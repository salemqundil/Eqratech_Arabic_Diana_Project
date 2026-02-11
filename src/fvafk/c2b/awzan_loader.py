from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Optional

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

    @classmethod
    def load(cls) -> List[PatternTemplate]:
        patterns: List[dict] = []
        if cls.CSV_PATH_PHONOLOGY_CLEAN.exists():
            csv_path = cls.CSV_PATH_PHONOLOGY_CLEAN
        elif cls.CSV_PATH_PHONOLOGY_FULL.exists():
            csv_path = cls.CSV_PATH_PHONOLOGY_FULL
        elif cls.CSV_PATH.exists():
            csv_path = cls.CSV_PATH
        else:
            csv_path = cls.CSV_PATH_LEGACY
        if not csv_path.exists():
            return patterns
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
            seen = set()
            for row in reader:
                template = (row.get("الوزن") or "").strip()
                if not template or template in seen:
                    continue
                seen.add(template)
                pattern_type = cls.PATTERN_TYPE_MAP.get(template, PatternType.UNKNOWN)
                category = cls._infer_category(row, pattern_type)
                patterns.append(
                    {
                        "template": template,
                        "pattern_type": pattern_type,
                        "category": category,
                        "form": row.get("الاسم") or None,
                        "meaning": row.get("الوصف") or None,
                        "cv_simple": row.get("CV") or None,
                        "cv_detailed": row.get("Detailed_CV") or None,
                        "cv_advanced": row.get("Advanced_CV") or None,
                        "notes": row.get("ملاحظات") or None,
                    }
                )
        return patterns

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
        if pattern_type != PatternType.UNKNOWN:
            return "verb"
        return "noun"
