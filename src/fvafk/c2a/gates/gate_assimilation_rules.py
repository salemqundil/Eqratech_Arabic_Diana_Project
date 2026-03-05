from typing import Dict, List, Set

SUN_LETTERS: Set[str] = {
    "ت", "ث", "د", "ذ", "ر", "ز",
    "س", "ش", "ص", "ض", "ط", "ظ",
    "ل", "ن",
}

MOON_LETTERS: Set[str] = {
    "ا", "ب", "ج", "ح", "خ", "ع",
    "غ", "ف", "ق", "ك", "م", "ه",
    "و", "ي",
}

BILABIALS: Set[str] = {"ب", "م", "و"}

EXAMPLES: List[Dict[str, str]] = [
    {
        "rule": "sun_letters",
        "input": "الشَّمْس",
        "output": "اَشَّمْس",
        "description": "al-shams becomes ash-shams (lam assimilates to sheen)",
    },
    {
        "rule": "sun_letters",
        "input": "النَّهَار",
        "output": "اَنَّهَار",
        "description": "al-nahaar with noon assimilation",
    },
    {
        "rule": "moon_letters",
        "input": "القَمَر",
        "output": "اَلْقَمَر",
        "description": "lam persists before moon letter",
    },
    {
        "rule": "nasal",
        "input": "مِنْ بَعْد",
        "output": "مِمْ بَعْد",
        "description": "noon saakin assimilates to meem before ba",
    },
]

RULE_DESCRIPTIONS: Dict[str, str] = {
    "sun_letters": """
Sun Letters Assimilation (ال + حرف شمسي)
Pattern: [ا، ل، ْ، letter] -> [ا، َ، letter، ّ]
Lam is replaced by the following solar consonant, which receives shadda.
""",
    "moon_letters": """
Moon Letters (no assimilation)
Lam is preserved before moon letters.
""",
    "nasal": """
Nasal Assimilation
Noon saakin before bilabials (ب، م، و) becomes the bilabial consonant itself.
""",
}

def get_assimilation_type(letter: str) -> str:
    if letter in SUN_LETTERS:
        return "sun"
    if letter in MOON_LETTERS:
        return "moon"
    return "unknown"

def is_bilabial(letter: str) -> bool:
    return letter in BILABIALS

def expected_sun_output(letter: str) -> str:
    return f"اَ{letter}ّ"  # simplified, lam disappears
