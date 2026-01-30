from dataclasses import dataclass
from typing import List, Tuple

ORTHOGRAPHY_RULES: List[Tuple[str, str]] = [
    ("ٱ", "ا"),
    ("أ", "ا"),
    ("إ", "ا"),
    ("ة", "ت"),
    ("ى", "ي"),
    ("ء", "ء"),
]

TANWIN_MAP = {
    "ً": "ن",
    "ٌ": "ن",
    "ٍ": "ن",
}
HARAKAT = {
    "َ",
    "ُ",
    "ِ",
    "ْ",
    "ً",
    "ٌ",
    "ٍ",
    "ّ",
    "ٓ",
    "ٰ",
    "ٖ",
    "ٗ",
}


@dataclass
class OrthographyAdapter:
    """Simplified written→spoken transformer."""

    def normalize(self, text: str) -> str:
        result = text
        for source, target in ORTHOGRAPHY_RULES:
            result = result.replace(source, target)
        result = self._collapse_tanwin(result)
        result = self._strip_diacritics(result)
        return result

    def _strip_diacritics(self, text: str) -> str:
        return "".join(ch for ch in text if ch not in HARAKAT)

    def _collapse_tanwin(self, text: str) -> str:
        for symbol, replacement in TANWIN_MAP.items():
            text = text.replace(symbol, replacement)
        return text
