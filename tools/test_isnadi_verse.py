#!/usr/bin/env python3
"""
Test ISNADI Linker on Surah Al-Fath (48:29)

Simple test with manually created WordForms

Author: Hussein Hiyassat
Date: 2025-02-13
"""

import sys
sys.path.insert(0, 'src')

from fvafk.c2b.word_form import WordForm, Span, PartOfSpeech, Case, Number, Gender
from fvafk.syntax.linkers import find_isnadi_links

print("="*80)
print("🕌 Testing ISNADI Linker on Surah Al-Fath (48:29)")
print("="*80)
print()

# Create sample WordForms from the verse
print("📊 Creating sample WordForms...")
print()

# محمدٌ رسولُ الله
# والذين معه أشداءُ
sample_words = [
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

print(f"✅ Created {len(sample_words)} WordForm instances")
print()

# Display words
print("Words created:")
for i, wf in enumerate(sample_words):
    print(f"  {i}. {wf.surface:15} → {wf.pos.value:10} {wf.case.arabic:10} "
          f"{wf.number.arabic:8} ({'معرفة' if wf.is_definite else 'نكرة':5})")
print()

# Find ISNADI links
print("="*80)
print("🔗 Detecting ISNADI links...")
print("="*80)
print()

links = find_isnadi_links(sample_words)
print(f"Found {len(links)} ISNADI link(s)")
print()

# Display results
if len(links) == 0:
    print("⚠️  No ISNADI links detected")
    print()
    print("Let's check why:")
    print()
    
    # Analyze potential مبتدأ
    for i, wf in enumerate(sample_words):
        if wf.is_noun and wf.case == Case.NOMINATIVE:
            print(f"✓ Word {i} ({wf.surface}) could be مبتدأ:")
            print(f"  - Is noun: ✓")
            print(f"  - Is nominative: ✓")
            print(f"  - Looking for خبر after it...")
            
            # Look for potential خبر
            found_khabar = False
            for j in range(i+1, len(sample_words)):
                candidate = sample_words[j]
                if candidate.is_noun and candidate.case == Case.NOMINATIVE:
                    agrees = wf.agrees_with(candidate, ['number', 'gender'])
                    print(f"    → Candidate: {candidate.surface}")
                    print(f"       Number match: {wf.number == candidate.number}")
                    print(f"       Gender match: {wf.gender == candidate.gender}")
                    print(f"       Agrees: {agrees}")
                    if agrees:
                        found_khabar = True
                        break
            
            if not found_khabar:
                print(f"    ✗ No matching خبر found")
            print()
else:
    print("="*80)
    print("📋 DETECTED ISNADI RELATIONS")
    print("="*80)
    print()
    
    for i, link in enumerate(links, 1):
        mubtada = sample_words[link.head_id]
        khabar = sample_words[link.dependent_id]
        
        print(f"🔗 Link {i}")
        print()
        print(f"  مبتدأ: {mubtada.surface}")
        print(f"    Position: word #{link.head_id}")
        print(f"    Case: {mubtada.case.arabic}")
        print(f"    Number: {mubtada.number.arabic}")
        print(f"    Gender: {mubtada.gender.arabic}")
        print(f"    Type: {'معرفة' if mubtada.is_definite else 'نكرة'}")
        print()
        print(f"  خبر: {khabar.surface}")
        print(f"    Position: word #{link.dependent_id}")
        print(f"    Case: {khabar.case.arabic}")
        print(f"    Number: {khabar.number.arabic}")
        print(f"    Gender: {khabar.gender.arabic}")
        print(f"    Type: {'معرفة' if khabar.is_definite else 'نكرة'}")
        print()
        print(f"  ✅ Confidence: {link.confidence:.1%}")
        print(f"  📝 {link.reason}")
        print()
        print("-" * 80)
        print()

# Summary
print("="*80)
print("📊 SUMMARY")
print("="*80)
print()

from collections import Counter

nominative_nouns = [wf for wf in sample_words if wf.is_noun and wf.case == Case.NOMINATIVE]
print(f"Total words: {len(sample_words)}")
print(f"Nominative nouns (potential مبتدأ): {len(nominative_nouns)}")
for wf in nominative_nouns:
    print(f"  • {wf.surface} ({wf.number.arabic})")
print()
print(f"ISNADI links detected: {len(links)}")
print()

if len(links) > 0:
    print("✅ ISNADI Linker successfully detected nominal sentences!")
else:
    print("ℹ️  No complete ISNADI relations found in this sample")
    print("   (This could be due to agreement mismatches or sentence structure)")

print()
print("="*80)
print("✅ Test Complete!")
print("="*80)
