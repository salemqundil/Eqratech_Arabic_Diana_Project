from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional


class SegmentKind(Enum):
    CONSONANT = auto()
    VOWEL = auto()


class VowelKind(Enum):
    FATHA = auto()
    DAMMA = auto()
    KASRA = auto()
    SUKUN = auto()
    SHADDA = auto()
    TANWIN_FATH = auto()
    TANWIN_DAMM = auto()
    TANWIN_KASR = auto()
    NONE = auto()


class SyllableType(Enum):
    CV = auto()
    CVV = auto()
    CVC = auto()
    CVVC = auto()
    CVCC = auto()
    CVVCC = auto()


@dataclass(frozen=True)
class Segment:
    text: str
    kind: SegmentKind
    vk: Optional[VowelKind] = None
    deleted: bool = False


@dataclass
class Syllable:
    onset: List[Segment]
    nucleus: Segment
    coda: List[Segment]
    type: SyllableType
    stress: bool = False

    def __post_init__(self):
        if self.nucleus.kind != SegmentKind.VOWEL:
            raise ValueError("Nucleus must be vowel")
        consonants = self.onset + self.coda
        for seg in consonants:
            if seg.kind != SegmentKind.CONSONANT:
                raise ValueError("Onset/coda must be consonants")

    def is_open(self) -> bool:
        return len(self.coda) == 0

    def is_closed(self) -> bool:
        return len(self.coda) > 0

    def is_heavy(self) -> bool:
        return self.type in {
            SyllableType.CVV,
            SyllableType.CVC,
            SyllableType.CVVC,
            SyllableType.CVCC,
            SyllableType.CVVCC,
        }
