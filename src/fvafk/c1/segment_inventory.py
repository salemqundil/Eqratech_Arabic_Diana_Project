from dataclasses import dataclass
from typing import ClassVar, Dict, FrozenSet


@dataclass(frozen=True)
class ConsonantInventory:
    """30 consonants with phonetic attributes for Phase 1."""

    CONSONANTS: ClassVar[Dict[str, Dict[str, object]]] = {
        # Bilabial
        "ب": {"cid": 1, "manner": "stop", "place": "bilabial", "voice": "voiced"},
        "م": {"cid": 2, "manner": "nasal", "place": "bilabial", "voice": "voiced"},
        "ف": {"cid": 3, "manner": "fricative", "place": "labiodental", "voice": "voiceless"},
        "و": {"cid": 4, "manner": "approximant", "place": "labial-velar", "voice": "voiced"},
        # Dental/Alveolar
        "ت": {"cid": 5, "manner": "stop", "place": "dental", "voice": "voiceless"},
        "د": {"cid": 6, "manner": "stop", "place": "dental", "voice": "voiced"},
        "ط": {"cid": 7, "manner": "stop", "place": "dental", "voice": "voiceless", "emphatic": True},
        "ض": {"cid": 8, "manner": "stop", "place": "dental", "voice": "voiced", "emphatic": True},
        "ث": {"cid": 9, "manner": "fricative", "place": "dental", "voice": "voiceless"},
        "ذ": {"cid": 10, "manner": "fricative", "place": "dental", "voice": "voiced"},
        "ظ": {"cid": 11, "manner": "fricative", "place": "dental", "voice": "voiced", "emphatic": True},
        "ن": {"cid": 12, "manner": "nasal", "place": "alveolar", "voice": "voiced"},
        "ل": {"cid": 13, "manner": "lateral", "place": "alveolar", "voice": "voiced"},
        "ر": {"cid": 14, "manner": "trill", "place": "alveolar", "voice": "voiced"},
        # Post-alveolar
        "س": {"cid": 15, "manner": "fricative", "place": "alveolar", "voice": "voiceless"},
        "ز": {"cid": 16, "manner": "fricative", "place": "alveolar", "voice": "voiced"},
        "ص": {"cid": 17, "manner": "fricative", "place": "alveolar", "voice": "voiceless", "emphatic": True},
        "ش": {"cid": 18, "manner": "fricative", "place": "post-alveolar", "voice": "voiceless"},
        "ج": {"cid": 19, "manner": "affricate", "place": "post-alveolar", "voice": "voiced"},
        # Palatal/Velar
        "ي": {"cid": 20, "manner": "approximant", "place": "palatal", "voice": "voiced"},
        "ك": {"cid": 21, "manner": "stop", "place": "velar", "voice": "voiceless"},
        "غ": {"cid": 22, "manner": "fricative", "place": "velar", "voice": "voiced"},
        "خ": {"cid": 23, "manner": "fricative", "place": "velar", "voice": "voiceless"},
        # Uvular/Pharyngeal/Glottal
        "ق": {"cid": 24, "manner": "stop", "place": "uvular", "voice": "voiceless"},
        "ح": {"cid": 25, "manner": "fricative", "place": "pharyngeal", "voice": "voiceless"},
        "ع": {"cid": 26, "manner": "fricative", "place": "pharyngeal", "voice": "voiced"},
        "ء": {"cid": 27, "manner": "stop", "place": "glottal", "voice": "voiceless"},
        "ه": {"cid": 28, "manner": "fricative", "place": "glottal", "voice": "voiceless"},
        # Additional markers
        "ة": {"cid": 29, "manner": "marker", "place": "none", "voice": "none"},
        "ى": {"cid": 30, "manner": "marker", "place": "none", "voice": "none"},
    }

    @classmethod
    def get_features(cls, consonant: str) -> FrozenSet[str]:
        info = cls.CONSONANTS.get(consonant, {})
        features = set()
        for key, value in info.items():
            if key == "cid":
                continue
            if isinstance(value, bool) and value:
                features.add(key)
            elif isinstance(value, str):
                features.add(f"{key}:{value}")
        return frozenset(features)
