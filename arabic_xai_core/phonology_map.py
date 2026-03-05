"""
phonology_map.py — Classify each ExpandedUnit as consonant/vowel/glide,
assign makhraj (articulation place) and sifat (phonetic properties).
"""
from __future__ import annotations

from typing import List, Optional

from .models import ExpandedUnit, PhonoUnit

# Arabic diacritics
FATHA  = "\u064E"
KASRA  = "\u0650"
DAMMA  = "\u064F"
SUKUN  = "\u0652"
SHADDA = "\u0651"

SHORT_VOWEL_MARKS = {FATHA, KASRA, DAMMA, SUKUN}

# Long vowel carriers
ALEF = "\u0627"
WAW  = "\u0648"
YEH  = "\u064A"
LONG_VOWEL_CARRIERS = {ALEF, WAW, YEH}

HAMZA = "\u0621"

# --- Makhraj table (simplified) ---
MAKHRAJ_TABLE: dict = {
    # Throat (حلق)
    "\u0621": "حلق_أقصى",    # ء
    "\u0647": "حلق_أوسط",    # ه
    "\u0639": "حلق_أوسط",    # ع
    "\u062D": "حلق_أوسط",    # ح
    "\u063A": "حلق_أدنى",    # غ
    "\u062E": "حلق_أدنى",    # خ
    # Tongue back (لسان_أقصى)
    "\u0642": "لسان_أقصى",   # ق
    "\u0643": "لسان_أقصى",   # ك
    # Tongue middle
    "\u062C": "لسان_وسط",    # ج
    "\u0634": "لسان_وسط",    # ش
    "\u064A": "لسان_وسط",    # ي (consonant role; also acts as long-vowel carrier)
    # Tongue tip (لسان_طرف)
    "\u0636": "لسان_طرف_أعلى", # ض
    "\u0644": "لسان_طرف",    # ل
    "\u0646": "لسان_طرف",    # ن
    "\u0631": "لسان_طرف",    # ر
    # Dental (أسنان)
    "\u062F": "أسناني",       # د
    "\u062A": "أسناني",       # ت
    "\u0637": "أسناني",       # ط
    "\u0630": "أسناني",       # ذ
    "\u062B": "أسناني",       # ث
    "\u0638": "أسناني",       # ظ
    "\u0632": "أسناني",       # ز
    "\u0633": "أسناني",       # س
    "\u0635": "أسناني",       # ص
    # Labio-dental
    "\u0641": "شفوي_أسناني",  # ف
    # Labial (شفوي)
    "\u0628": "شفوي",         # ب
    "\u0645": "شفوي",         # م
    "\u0648": "شفوي",         # و (consonant role; also acts as long-vowel carrier)
    # Alef
    "\u0627": "جوف",          # ا
    # Short vowel diacritics (treated as phonological vowels)
    "\u064E": "جوف",          # فتحة
    "\u0650": "جوف",          # كسرة
    "\u064F": "جوف",          # ضمة
}

# --- Sifat table (simplified) ---
SIFAT_TABLE: dict = {
    "\u0628": ["مجهور", "شديد", "مطبق_لا"],
    "\u062A": ["مهموس", "شديد"],
    "\u062B": ["مهموس", "رخو"],
    "\u062C": ["مجهور", "شديد", "رخو"],
    "\u062D": ["مهموس", "رخو"],
    "\u062E": ["مهموس", "رخو"],
    "\u062F": ["مجهور", "شديد"],
    "\u0630": ["مجهور", "رخو"],
    "\u0631": ["مجهور", "رخو", "منحرف", "تكرار"],
    "\u0632": ["مجهور", "رخو"],
    "\u0633": ["مهموس", "رخو"],
    "\u0634": ["مهموس", "رخو"],
    "\u0635": ["مهموس", "رخو", "مطبق"],
    "\u0636": ["مجهور", "رخو", "مطبق"],
    "\u0637": ["مجهور", "شديد", "مطبق"],
    "\u0638": ["مجهور", "رخو", "مطبق"],
    "\u0639": ["مجهور", "رخو"],
    "\u063A": ["مجهور", "رخو"],
    "\u0641": ["مهموس", "رخو"],
    "\u0642": ["مجهور", "شديد"],
    "\u0643": ["مهموس", "شديد"],
    "\u0644": ["مجهور", "رخو", "منحرف"],
    "\u0645": ["مجهور", "شديد", "أنفي"],
    "\u0646": ["مجهور", "رخو", "أنفي"],
    "\u0647": ["مهموس", "رخو"],
    "\u0648": ["مجهور", "رخو"],   # consonant
    "\u064A": ["مجهور", "رخو"],   # consonant
    "\u0621": ["مهموس", "شديد"],
    "\u0627": ["صائت_طويل"],
}


def assign_makhraj(unit: ExpandedUnit) -> str:
    return MAKHRAJ_TABLE.get(unit.base_char, "غير_محدد")


def assign_sifat(unit: ExpandedUnit) -> List[str]:
    return SIFAT_TABLE.get(unit.base_char, [])


def resolve_glide_role(unit: ExpandedUnit, context: Optional[List[ExpandedUnit]] = None) -> str:
    """
    Determine if و or ي is acting as glide (شبه_صائت) or long vowel (صائت).
    Heuristic: if preceded by matching short vowel in previous unit → vowel role.
    """
    char = unit.base_char
    if char not in (WAW, YEH):
        return "صامت"

    # If the unit has explicit vowel role from expansion
    if unit.role == "vowel":
        return "صائت"
    if unit.role == "extension":
        return "صائت"

    # Context-based: if no diacritics after, treat as glide
    diacritics_in_value = set(unit.value) & SHORT_VOWEL_MARKS
    if diacritics_in_value:
        return "شبه_صائت"  # has its own movement → consonant/glide

    return "شبه_صائت"


def classify_phonounit(unit: ExpandedUnit, context: Optional[List[ExpandedUnit]] = None) -> PhonoUnit:
    """Classify a single ExpandedUnit into a PhonoUnit."""
    char = unit.base_char
    trace = []

    # Determine type
    if unit.role in ("vowel", "extension"):
        unit_type = "صائت"
        trace.append(f"role_is_{unit.role}")
    elif char in LONG_VOWEL_CARRIERS:
        unit_type = resolve_glide_role(unit, context)
        trace.append(f"glide_resolved:{unit_type}")
    else:
        unit_type = "صامت"
        trace.append("consonant")

    makhraj = assign_makhraj(unit)
    sifa = assign_sifat(unit)
    can_shift = char in LONG_VOWEL_CARRIERS

    return PhonoUnit(
        symbol=char,
        unit_type=unit_type,
        makhraj=makhraj,
        sifa=sifa,
        can_shift_role=can_shift,
        position=unit.position,
        word_index=unit.word_index,
        trace=trace,
    )


def classify_phonounits(
    units: List[ExpandedUnit],
    context: Optional[List[ExpandedUnit]] = None
) -> List[PhonoUnit]:
    """Classify all ExpandedUnit items into PhonoUnit list."""
    return [classify_phonounit(u, context or units) for u in units]
