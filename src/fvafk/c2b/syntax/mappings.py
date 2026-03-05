"""
Arabic-English mappings for I3rab (grammatical annotation) terms.

Author: Hussein Hiyassat
Date: 2026-02-21
Sprint: 4 - Task 4.2
"""

# I3rab type mappings (Arabic -> English)
I3RAB_TYPE_MAPPING = {
    "مبتدأ": "mubtada",
    "خبر": "khabar",
    "فاعل": "fa'il",
    "مفعول به": "maf'ul_bihi",
    "حرف": "harf",
    # Extended types
    "مضاف إليه": "mudaf_ilayhi",
    "نعت": "na't",
    "مفعول مطلق": "maf'ul_mutlaq",
    "مفعول لأجله": "maf'ul_lajlih",
    "حال": "hal",
    "تمييز": "tamyeez",
    "بدل": "badal",
    "عطف": "atf",
    "توكيد": "tawkid",
    "نائب فاعل": "na'ib_fa'il",
    "اسم كان": "ism_kana",
    "خبر كان": "khabar_kana",
    "اسم إن": "ism_inna",
    "خبر إن": "khabar_inna",
    "مجرور": "majrur",
}

# Reverse mapping (English -> Arabic)
I3RAB_TYPE_MAPPING_REVERSE = {v: k for k, v in I3RAB_TYPE_MAPPING.items()}

# Syntactic role mappings (I3rab type -> syntactic role)
SYNTACTIC_ROLE_MAPPING = {
    "mubtada": "subject",
    "khabar": "predicate",
    "fa'il": "agent",
    "maf'ul_bihi": "object",
    "harf": "particle",
    "mudaf_ilayhi": "genitive_complement",
    "na't": "adjunct",
    "maf'ul_mutlaq": "cognate_object",
    "maf'ul_lajlih": "purpose",
    "hal": "circumstantial",
    "tamyeez": "specifier",
    "badal": "appositive",
    "atf": "conjunction",
    "tawkid": "emphasis",
    "na'ib_fa'il": "passive_subject",
    "ism_kana": "subject",
    "khabar_kana": "predicate",
    "ism_inna": "subject",
    "khabar_inna": "predicate",
    "majrur": "oblique",
}

# Case mappings (Arabic -> English)
CASE_MAPPING = {
    "مرفوع": "nominative",
    "منصوب": "accusative",
    "مجرور": "genitive",
}

# Reverse case mapping
CASE_MAPPING_REVERSE = {v: k for k, v in CASE_MAPPING.items()}

# Case marker mappings
CASE_MARKER_MAPPING = {
    "الضمة": "damma",
    "الفتحة": "fatha",
    "الكسرة": "kasra",
    "الواو": "waw",
    "الياء": "ya",
    "الألف": "alif",
    "النون": "nun",
    "الحركات": "short_vowels",
}

# Mahall (محل) mappings
MAHALL_MAPPING = {
    "في محل رفع": "in_nominative_position",
    "في محل نصب": "in_accusative_position",
    "في محل جر": "in_genitive_position",
    "لا محل له من الإعراب": "no_grammatical_position",
    "لا محل له": "no_grammatical_position",
}

# Top 5 I3rab types (Phase 1 - Sprint 4)
TOP5_I3RAB_TYPES = {
    "مبتدأ",
    "خبر",
    "فاعل",
    "مفعول به",
    "حرف",
}
