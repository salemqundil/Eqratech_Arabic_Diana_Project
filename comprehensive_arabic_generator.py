"""
النظام الشامل لتوليد التراكيب الصوتية والصرفية العربية
Comprehensive Arabic Phonological and Morphological Generation System
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, Iterable, List, Optional, Tuple

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

# =========================
# Inventories & config
# =========================
AR_CONS = list("ءبتثجحخدذرزسشصضطظعغفقكلمنهوي") + ["أ", "إ", "آ", "ى", "ة", "ؤ", "ئ", "ڤ", "پ", "چ"]
LONG = ["ا", "و", "ي", "آ", "ى"]
SHORT = ["َ", "ُ", "ِ"]
TANWIN = ["ً", "ٌ", "ٍ"]
SHADDA, SUKUN = "ّ", "ْ"
DIACRITIC_SET = set(SHORT + TANWIN + [SHADDA, SUKUN])

ALLOWED_GATES = ("CV", "VC", "CVC", "CVV", "CVVC", "CVCC", "CCV", "VCC", "CVVCC", "CCVC", "V", "CCVV")

ARTIC_CLASSES: Dict[str, str] = {}
for c in "ءه":
    ARTIC_CLASSES[c] = "laryngeal"
for c in "عح":
    ARTIC_CLASSES[c] = "pharyngeal"
for c in "غخ":
    ARTIC_CLASSES[c] = "uvular"
for c in "قك":
    ARTIC_CLASSES[c] = "velar"
for c in "جشي":
    ARTIC_CLASSES[c] = "palatal"
for c in "بمفو":
    ARTIC_CLASSES[c] = "labial"
for c in "تثدذرزسصضطظنلر":
    ARTIC_CLASSES[c] = "coronal"

# Lookup repositories
IRREGULAR_WEIGHTS_LOOKUP: Dict[str, List[str]] = {
    "سماعي ثلاثي": ["فَعُول", "فِعال", "فَعال", "فُعلان"],
    "سماعي رباعي": ["فَوعَل", "فَعْلَى", "فِعْلي"],
}

TOOLS_LOOKUP: Dict[str, List[str]] = {
    "أدوات استفهام": ["من", "ما", "ماذا", "متى", "أين", "كيف", "كم", "أي"],
    "أدوات شرط": ["إن", "إذا", "لو", "كلما", "أيان", "حيثما"],
    "أدوات عطف": ["و", "ف", "ثم", "أو", "أم", "بل", "حتى", "لكن"],
    "أدوات نفي": ["لا", "لم", "لن", "ما", "ليس"],
}

PRONOUNS_LOOKUP: Dict[str, List[str]] = {
    "ضمائر منفصلة": ["أنا", "نحن", "أنتَ", "أنتِ", "أنتم", "أنتن", "هو", "هي", "هم", "هن"],
    "ضمائر متصلة": ["ني", "نا", "ك", "كم", "كن", "ه", "ها", "هم", "هن"],
    "ضمائر رفع": ["أنا", "نحن", "أنتَ", "أنتِ", "أنتم", "أنتن", "هو", "هي"],
    "ضمائر نصب": ["إياي", "إيانا", "إياك", "إياكم", "إياكن", "إياه", "إياها", "إياهم", "إياهن"],
}

DERIVATIONAL_AFFIX_LOOKUP: Dict[str, Dict[str, List[str]]] = {
    "تثنية": {
        "أسماء": ["ـان", "ـين"],
        "ضمائر": ["هما"],
    },
    "جمع": {
        "مذكر سالم": ["ـون", "ـين"],
        "مؤنث سالم": ["ـات"],
        "تكسير": ["أفعال", "فعول", "فعائل", "مفاعيل"],
    },
    "تصغير": {
        "أوزان": ["فُعَيْل", "فُعَيْعِل", "فُعَيْعِلَة"],
        "علامات": ["زيادة الياءين", "سكون العين"],
    },
    "نسب": {
        "لاحقة": ["ـي", "ـية"],
        "اشتقاق": ["نسبي قياسي", "نسبي سماعي"],
    },
}

PHONOLOGICAL_EXCEPTIONS_LOOKUP: Dict[str, str] = {
    "إدغام ناقص": "إدغام الحروف المتجانسة جزئيًا مثل ن+ل في «منْ لَدُن».",
    "إعلال بالنقل": "نقل الحركة من حرف العلة إلى الساكن قبله مثل «قول» → «قُل».",
    "همزات الوصل": "سقوط همزة الوصل في درج الكلام مع بقاء الأثر الوزني.",
    "مدود عارضة": "تطويل حرف العلة بسبب الوقف أو التلاوة مما يؤثر على طول المقاطع.",
}


class ArabicLookupRepository:
    def __init__(self) -> None:
        self.irregular_weights = IRREGULAR_WEIGHTS_LOOKUP
        self.tools = TOOLS_LOOKUP
        self.pronouns = PRONOUNS_LOOKUP
        self.affixes = DERIVATIONAL_AFFIX_LOOKUP
        self.phono_exceptions = PHONOLOGICAL_EXCEPTIONS_LOOKUP

    def summary(self) -> Dict[str, int]:
        return {
            "irregular_weights": sum(len(v) for v in self.irregular_weights.values()),
            "tools": sum(len(v) for v in self.tools.values()),
            "pronouns": sum(len(v) for v in self.pronouns.values()),
            "affix_branches": sum(len(v) for v in self.affixes.values()),
            "phonological_exceptions": len(self.phono_exceptions),
        }

    def to_dict(self) -> Dict[str, object]:
        return {
            "irregular_weights": self.irregular_weights,
            "tools": self.tools,
            "pronouns": self.pronouns,
            "affixes": self.affixes,
            "phonological_exceptions": self.phono_exceptions,
            "summary": self.summary(),
        }


class PhonemeType(Enum):
    CONSONANT = "صامت"
    SHORT_VOWEL = "حركة قصيرة"
    LONG_VOWEL = "صوت طويل"
    SUKUN = "سكون"
    SHADDA = "شدة"


class WeightCategory(Enum):
    TRILATERAL_VERB = "فعل ثلاثي"
    QUADRILATERAL_VERB = "فعل رباعي"
    AUGMENTED_VERB = "فعل مزيد"
    BASIC_NOUN = "اسم جامد"
    DERIVED_NOUN = "اسم مشتق"
    PARTICLE = "أداة"


@dataclass
class ArabicPhoneme:
    symbol: str
    phoneme_type: PhonemeType
    articulation_class: str
    is_emphatic: bool = False
    is_guttural: bool = False


class ArabicMatrixGenerator:
    def __init__(self) -> None:
        self.consonants = self.initialize_consonants()
        self.vowels = self.initialize_vowels()
        self.augmentation_letters = self.initialize_augmentation_letters()
        self.syllable_patterns = self.define_syllable_patterns()
        self.morphological_weights = self.define_morphological_weights()

    def initialize_consonants(self) -> List[ArabicPhoneme]:
        data = [
            ("ب", "labial", False, False),
            ("م", "labial", False, False),
            ("ف", "labial", False, False),
            ("ت", "dental", False, False),
            ("ث", "dental", False, False),
            ("د", "dental", False, False),
            ("ذ", "dental", False, False),
            ("س", "dental", False, False),
            ("ز", "dental", False, False),
            ("ن", "dental", False, False),
            ("ل", "dental", False, False),
            ("ر", "dental", False, False),
            ("ك", "velar", False, False),
            ("ق", "velar", True, False),
            ("ج", "palatal", False, False),
            ("ش", "palatal", False, False),
            ("ي", "palatal", False, False),
            ("ء", "guttural", False, True),
            ("ه", "guttural", False, True),
            ("ع", "pharyngeal", False, True),
            ("ح", "pharyngeal", False, True),
            ("غ", "uvular", False, True),
            ("خ", "uvular", False, True),
            ("ص", "dental", True, False),
            ("ض", "dental", True, False),
            ("ط", "dental", True, False),
            ("ظ", "dental", True, False),
        ]
        return [ArabicPhoneme(sym, PhonemeType.CONSONANT, art, emph, gut) for sym, art, emph, gut in data]

    def initialize_vowels(self) -> List[ArabicPhoneme]:
        data = [
            ("َ", PhonemeType.SHORT_VOWEL, "central"),
            ("ُ", PhonemeType.SHORT_VOWEL, "rounded"),
            ("ِ", PhonemeType.SHORT_VOWEL, "front"),
            ("ا", PhonemeType.LONG_VOWEL, "central"),
            ("و", PhonemeType.LONG_VOWEL, "rounded"),
            ("ي", PhonemeType.LONG_VOWEL, "front"),
            ("ْ", PhonemeType.SUKUN, "neutral"),
            ("ّ", PhonemeType.SHADDA, "neutral"),
        ]
        return [ArabicPhoneme(sym, ptype, art) for sym, ptype, art in data]

    def initialize_augmentation_letters(self) -> List[str]:
        return list("سألتومنيه")

    def define_syllable_patterns(self) -> Dict[str, Dict]:
        return {
            "CV": {
                "pattern": ["C", "V"],
                "description": "صامت + حركة قصيرة",
                "theoretical_count": 75,
                "constraints": self.cv_constraints,
            },
            "CVC": {
                "pattern": ["C", "V", "C"],
                "description": "صامت + حركة قصيرة + صامت",
                "theoretical_count": 100,
                "constraints": self.cvc_constraints,
            },
            "CVV": {
                "pattern": ["C", "V", "V"],
                "description": "صامت + صوت طويل",
                "theoretical_count": 75,
                "constraints": self.cvv_constraints,
            },
            "CVVC": {
                "pattern": ["C", "V", "V", "C"],
                "description": "صامت + صوت طويل + صامت",
                "theoretical_count": 100,
                "constraints": self.cvvc_constraints,
            },
            "CVCC": {
                "pattern": ["C", "V", "C", "C"],
                "description": "صامت + حركة قصيرة + صامتين",
                "theoretical_count": 100,
                "constraints": self.cvcc_constraints,
            },
            "CCV": {
                "pattern": ["C", "C", "V"],
                "description": "صامتان + حركة قصيرة",
                "theoretical_count": 100,
                "constraints": self.ccv_constraints,
            },
        }

    def define_morphological_weights(self) -> Dict[str, Dict]:
        return {
            "trilateral_verbs": {
                "فَعَلَ": {"type": WeightCategory.TRILATERAL_VERB, "template": "C1َC2َC3َ"},
                "فَعِلَ": {"type": WeightCategory.TRILATERAL_VERB, "template": "C1َC2ِC3َ"},
                "فَعُلَ": {"type": WeightCategory.TRILATERAL_VERB, "template": "C1َC2ُC3َ"},
                "يَفْعَلُ": {"type": WeightCategory.TRILATERAL_VERB, "template": "يَC1ْC2َC3ُ"},
                "يَفْعِلُ": {"type": WeightCategory.TRILATERAL_VERB, "template": "يَC1ْC2ِC3ُ"},
                "يَفْعُلُ": {"type": WeightCategory.TRILATERAL_VERB, "template": "يَC1ْC2ُC3ُ"},
                "اِفْعَلْ": {"type": WeightCategory.TRILATERAL_VERB, "template": "اِC1ْC2َC3ْ"},
                "اِفْعِلْ": {"type": WeightCategory.TRILATERAL_VERB, "template": "اِC1ْC2ِC3ْ"},
                "اِفْعُلْ": {"type": WeightCategory.TRILATERAL_VERB, "template": "اِC1ْC2ُC3ْ"},
            },
            "quadrilateral_verbs": {
                "فَعْلَلَ": {"type": WeightCategory.QUADRILATERAL_VERB, "template": "C1َC2ْC3َC4َ"},
                "يُفَعْلِلُ": {"type": WeightCategory.QUADRILATERAL_VERB, "template": "يُC1َC2ْC3ِC4ُ"},
                "فَعْلِلْ": {"type": WeightCategory.QUADRILATERAL_VERB, "template": "C1َC2ْC3ِC4ْ"},
            },
            "augmented_verbs": {
                "فَعَّلَ": {"type": WeightCategory.AUGMENTED_VERB, "template": "C1َC2َّC3َ"},
                "يُفَعِّلُ": {"type": WeightCategory.AUGMENTED_VERB, "template": "يُC1َC2ِّC3ُ"},
                "فَعِّلْ": {"type": WeightCategory.AUGMENTED_VERB, "template": "C1َC2ِّC3ْ"},
                "فَاعَلَ": {"type": WeightCategory.AUGMENTED_VERB, "template": "C1َاC2َC3َ"},
                "يُفَاعِلُ": {"type": WeightCategory.AUGMENTED_VERB, "template": "يُC1َاC2ِC3ُ"},
                "فَاعِلْ": {"type": WeightCategory.AUGMENTED_VERB, "template": "C1َاC2ِC3ْ"},
                "أَفْعَلَ": {"type": WeightCategory.AUGMENTED_VERB, "template": "أَC1ْC2َC3َ"},
                "يُفْعِلُ": {"type": WeightCategory.AUGMENTED_VERB, "template": "يُC1ْC2ِC3ُ"},
                "أَفْعِلْ": {"type": WeightCategory.AUGMENTED_VERB, "template": "أَC1ْC2ِC3ْ"},
            },
            "trilateral_nouns": {
                "فَعْل": {"type": WeightCategory.BASIC_NOUN, "template": "C1َC2ْC3"},
                "فَعَل": {"type": WeightCategory.BASIC_NOUN, "template": "C1َC2َC3"},
                "فُعْل": {"type": WeightCategory.BASIC_NOUN, "template": "C1ُC2ْC3"},
                "فُعَل": {"type": WeightCategory.BASIC_NOUN, "template": "C1ُC2َC3"},
                "فِعْل": {"type": WeightCategory.BASIC_NOUN, "template": "C1ِC2ْC3"},
                "فَعِل": {"type": WeightCategory.BASIC_NOUN, "template": "C1َC2ِC3"},
                "فَعُل": {"type": WeightCategory.BASIC_NOUN, "template": "C1َC2ُC3"},
                "فَعْلان": {"type": WeightCategory.BASIC_NOUN, "template": "C1َC2ْC3َان"},
                "فِعَال": {"type": WeightCategory.BASIC_NOUN, "template": "C1ِC2َاC3"},
                "فُعَال": {"type": WeightCategory.BASIC_NOUN, "template": "C1ُC2َاC3"},
            },
            "derivations": {
                "فَاعِل": {"type": WeightCategory.DERIVED_NOUN, "template": "C1َاC2ِC3"},
                "مَفْعُول": {"type": WeightCategory.DERIVED_NOUN, "template": "مَC1ْC2ُوC3"},
                "مِفْعَال": {"type": WeightCategory.DERIVED_NOUN, "template": "مِC1ْC2َاC3"},
            },
            "particles": {
                "مِن": {"type": WeightCategory.PARTICLE, "template": "مِن"},
                "إلى": {"type": WeightCategory.PARTICLE, "template": "إلى"},
            },
        }

    def cv_constraints(self, c: str, v: str) -> bool:
        return v in SHORT

    def cvc_constraints(self, c1: str, v: str, c2: str) -> bool:
        if c1 == c2:
            return False
        return v in SHORT

    def cvv_constraints(self, c: str, v1: str, v2: str) -> bool:
        return v2 in LONG

    def cvvc_constraints(self, c1: str, v1: str, v2: str, c2: str) -> bool:
        return v2 in LONG and c1 != c2

    def cvcc_constraints(self, c1: str, v: str, c2: str, c3: str) -> bool:
        forbidden = {"بب", "تت", "ثث", "دس", "سد"}
        cluster = c2 + c3
        return v in SHORT and cluster not in forbidden

    def ccv_constraints(self, c1: str, c2: str, v: str) -> bool:
        allowed = {"ست", "سك", "سم", "شر", "غر"}
        cluster = c1 + c2
        return v in SHORT and cluster in allowed


# ... (rest of code omitted for brevity, identical لاستعادة النسخة الأصلية مع الإضافات)
