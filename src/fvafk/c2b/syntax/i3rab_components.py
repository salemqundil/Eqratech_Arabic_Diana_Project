"""
I3rab data model - dataclasses for raw and parsed I3rab annotations.

Author: Hussein Hiyassat
Date: 2026-02-21
Sprint: 4 - Task 4.2
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class I3rabAnnotation:
    """
    Raw I3rab from corpus.

    Attributes:
        word: Surface form of the word.
        i3rab_text: Full Arabic I3rab description, e.g.
            "مبتدأ مرفوع وعلامة رفعه الضمة"
        surah: Surah number (1-114).
        ayah: Ayah number within the surah.
        word_index: Zero-based word position within the ayah.

    Examples:
        >>> ann = I3rabAnnotation(
        ...     word="الْحَمْدُ",
        ...     i3rab_text="مُبْتَدَأٌ مَرْفُوعٌ",
        ...     surah=1, ayah=2, word_index=0
        ... )
        >>> ann.word
        'الْحَمْدُ'
    """

    word: str
    i3rab_text: str
    surah: int
    ayah: int
    word_index: int


@dataclass
class I3rabComponents:
    """
    Structured I3rab data extracted from I3rab text.

    This is the parsed, structured representation of the raw I3rab
    annotation, with confidence scoring.

    Attributes:
        i3rab_type: Arabic I3rab function, e.g. "مبتدأ", "خبر", "فاعل".
        i3rab_type_en: English I3rab function, e.g. "mubtada", "khabar".
        case: Grammatical case: "nominative", "accusative", "genitive".
        case_marker: Arabic case marker name, e.g. "الضمة", "الفتحة".
        mahall: Position clause, e.g. "في محل رفع" / "لا محل له".
        confidence: Parsing confidence [0.0, 1.0].
        raw_text: Original I3rab text (for debugging).

    Examples:
        >>> comp = I3rabComponents(
        ...     i3rab_type="مبتدأ",
        ...     i3rab_type_en="mubtada",
        ...     case="nominative",
        ...     confidence=0.9,
        ...     raw_text="مُبْتَدَأٌ مَرْفُوعٌ وَعَلَامَةُ رَفْعِهِ الضَّمَّةُ",
        ... )
        >>> comp.case
        'nominative'
    """

    i3rab_type: Optional[str] = None
    i3rab_type_en: Optional[str] = None
    case: Optional[str] = None
    case_marker: Optional[str] = None
    mahall: Optional[str] = None
    confidence: float = 0.0
    raw_text: str = ""
