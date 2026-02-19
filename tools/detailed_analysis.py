#!/usr/bin/env python3
"""
ISNADI Linker with Detailed Grammatical Analysis Output

Shows complete syntactic breakdown like traditional Arabic grammar books

Author: Hussein Hiyassat
Date: 2025-02-13
"""

import sys
sys.path.insert(0, 'src')

from fvafk.c2b.word_form import WordForm, Span, PartOfSpeech, Case, Number, Gender
# Import V2
import importlib.util
spec = importlib.util.spec_from_file_location("isnadi_v2", "tools/isnadi_linker_v2.py")
isnadi_v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(isnadi_v2)

print("="*80)
print("🕌 ISNADI Linker - Detailed Grammatical Analysis")
print("   Surah Al-Fath (48:29)")
print("="*80)
print()

# Sample words
sample_words = [
    # محمدٌ رسولُ الله
    WordForm(
        word_id=0,
        surface='مُّحَمَّدٌ',
        span=Span(0, 10),
        pos=PartOfSpeech.NOUN,
        case=Case.NOMINATIVE,
        definiteness=False,
        number=Number.SINGULAR,
        gender=Gender.MASCULINE
    ),
    WordForm(
        word_id=1,
        surface='رَّسُولُ',
        span=Span(11, 19),
        pos=PartOfSpeech.NOUN,
        case=Case.NOMINATIVE,
        definiteness=False,
        number=Number.SINGULAR,
        gender=Gender.MASCULINE
    ),
    WordForm(
        word_id=2,
        surface='اللَّهِ',
        span=Span(20, 26),
        pos=PartOfSpeech.NOUN,
        case=Case.GENITIVE,
        definiteness=True,
        number=Number.SINGULAR,
        gender=Gender.MASCULINE
    ),
    # والذين معه أشداءُ
    WordForm(
        word_id=3,
        surface='وَالَّذِينَ',
        span=Span(27, 37),
        pos=PartOfSpeech.NOUN,
        case=Case.NOMINATIVE,
        definiteness=True,
        number=Number.PLURAL,
        gender=Gender.MASCULINE
    ),
    WordForm(
        word_id=4,
        surface='مَعَهُ',
        span=Span(38, 43),
        pos=PartOfSpeech.PARTICLE,
        case=Case.UNKNOWN,
        number=Number.SINGULAR,
        gender=Gender.MASCULINE
    ),
    WordForm(
        word_id=5,
        surface='أَشِدَّاءُ',
        span=Span(44, 53),
        pos=PartOfSpeech.NOUN,
        case=Case.NOMINATIVE,
        definiteness=False,
        number=Number.PLURAL,
        gender=Gender.MASCULINE
    ),
]

# Detect links
links = isnadi_v2.find_isnadi_links_v2(sample_words)

print(f"✅ Detected {len(links)} ISNADI relation(s)")
print()

# Display with detailed analysis
print("="*80)
print("📋 DETAILED GRAMMATICAL ANALYSIS")
print("="*80)
print()

for link_num, link in enumerate(links, 1):
    mubtada = sample_words[link.head_id]
    khabar = sample_words[link.dependent_id]
    
    print(f"الجملة {link_num}: ", end="")
    
    # Construct the sentence from mubtada to khabar
    sentence_parts = []
    for i in range(link.head_id, link.dependent_id + 1):
        sentence_parts.append(sample_words[i].surface)
    print(" ".join(sentence_parts))
    print()
    
    # Detailed breakdown
    print("```")
    
    # مبتدأ
    def_str = "معرفة" if mubtada.is_definite else "نكرة"
    print(f"{mubtada.surface:15} → مبتدأ ({def_str}، {mubtada.case.arabic}، {mubtada.number.arabic})")
    
    # Words between (if any)
    for i in range(link.head_id + 1, link.dependent_id):
        word = sample_words[i]
        
        # Determine grammatical role
        if word.is_particle:
            role = "شبه جملة (ظرفية)"
            marker = "← SKIPPED!"
        elif word.case == Case.GENITIVE:
            role = "مضاف إليه"
            marker = ""
        elif word.case == Case.ACCUSATIVE:
            role = "مفعول به"
            marker = ""
        else:
            role = "متمم"
            marker = ""
        
        def_str = "معرفة" if word.is_definite else "نكرة"
        case_str = word.case.arabic if word.case != Case.UNKNOWN else ""
        
        if case_str:
            print(f"{word.surface:15} → {role} ({def_str}، {case_str}) {marker}")
        else:
            print(f"{word.surface:15} → {role} {marker}")
    
    # خبر
    def_str = "معرفة" if khabar.is_definite else "نكرة"
    print(f"{khabar.surface:15} → خبر ({def_str}، {khabar.case.arabic}، {khabar.number.arabic})")
    
    print("```")
    print()
    
    # Agreement analysis
    print("التوافق:")
    print(f"  ✓ الإعراب: {mubtada.case.arabic} = {khabar.case.arabic}")
    print(f"  ✓ العدد: {mubtada.number.arabic} = {khabar.number.arabic}")
    print(f"  ✓ الجنس: {mubtada.gender.arabic} = {khabar.gender.arabic}")
    print()
    
    print(f"الثقة: {link.confidence:.0%}")
    print(f"السبب: {link.reason}")
    print()
    print("-" * 80)
    print()

# Summary
print("="*80)
print("📊 الملخص")
print("="*80)
print()

print(f"عدد الجمل المكتشفة: {len(links)}")
print()

print("أنواع الجمل:")
for i, link in enumerate(links, 1):
    mubtada = sample_words[link.head_id]
    khabar = sample_words[link.dependent_id]
    
    # Determine sentence type
    if link.dependent_id - link.head_id == 1:
        sentence_type = "جملة اسمية بسيطة"
    else:
        sentence_type = "جملة اسمية مع متممات"
    
    print(f"  {i}. {sentence_type}")
    print(f"     {mubtada.surface} ← {khabar.surface}")

print()
print("="*80)
print("✅ التحليل النحوي اكتمل!")
print("="*80)
