#!/usr/bin/env python3
"""
Compare ISNADI Linker V1 vs V2 on Surah Al-Fath

Shows the improvement in V2 with modifier skipping

Author: Hussein Hiyassat
Date: 2025-02-13
"""

import sys
sys.path.insert(0, 'src')

from fvafk.c2b.word_form import WordForm, Span, PartOfSpeech, Case, Number, Gender
from fvafk.syntax.linkers import find_isnadi_links  # V1
# Import V2 from the new file
import importlib.util
spec = importlib.util.spec_from_file_location("isnadi_v2", "tools/isnadi_linker_v2.py")
isnadi_v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(isnadi_v2)

print("="*80)
print("🕌 ISNADI Linker V1 vs V2 Comparison")
print("   Surah Al-Fath (48:29)")
print("="*80)
print()

# Sample words from the verse
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

print("Words:")
for i, wf in enumerate(sample_words):
    marker = "  "
    if wf.is_noun and wf.case == Case.NOMINATIVE:
        marker = "→ "
    elif wf.is_particle:
        marker = "⊗ "
    
    print(f"{marker}{i}. {wf.surface:15} {wf.pos.value:10} {wf.case.arabic:10} "
          f"{wf.number.arabic:8}")
print()
print("Legend: → = nominative noun, ⊗ = particle")
print()

# Test V1
print("="*80)
print("📊 V1: Original ISNADI Linker")
print("="*80)
print()

links_v1 = find_isnadi_links(sample_words)
print(f"Found: {len(links_v1)} link(s)")
print()

if links_v1:
    for i, link in enumerate(links_v1, 1):
        mubtada = sample_words[link.head_id]
        khabar = sample_words[link.dependent_id]
        print(f"Link {i}: {mubtada.surface} ← {khabar.surface}")
        print(f"  Confidence: {link.confidence:.1%}")
        print()

# Test V2
print("="*80)
print("🚀 V2: Enhanced ISNADI Linker (with modifier skipping)")
print("="*80)
print()

links_v2 = isnadi_v2.find_isnadi_links_v2(sample_words)
print(f"Found: {len(links_v2)} link(s)")
print()

if links_v2:
    for i, link in enumerate(links_v2, 1):
        mubtada = sample_words[link.head_id]
        khabar = sample_words[link.dependent_id]
        print(f"Link {i}: {mubtada.surface} ← {khabar.surface}")
        print(f"  Confidence: {link.confidence:.1%}")
        print(f"  Reason: {link.reason}")
        print()

# Compare
print("="*80)
print("📈 COMPARISON")
print("="*80)
print()

print(f"V1 detected: {len(links_v1)} link(s)")
print(f"V2 detected: {len(links_v2)} link(s)")
print()

if len(links_v2) > len(links_v1):
    print(f"✅ V2 found {len(links_v2) - len(links_v1)} additional link(s)!")
    print()
    
    # Show what V2 found that V1 didn't
    v1_pairs = set((l.head_id, l.dependent_id) for l in links_v1)
    v2_pairs = set((l.head_id, l.dependent_id) for l in links_v2)
    new_pairs = v2_pairs - v1_pairs
    
    if new_pairs:
        print("New detections in V2:")
        for head_id, dep_id in new_pairs:
            mubtada = sample_words[head_id]
            khabar = sample_words[dep_id]
            print(f"  • {mubtada.surface} ← {khabar.surface}")
            
            # Show what was skipped
            between = []
            for i in range(head_id + 1, dep_id):
                between.append(sample_words[i].surface)
            if between:
                print(f"    (skipped: {', '.join(between)})")
        print()

print("="*80)
print("💡 Analysis")
print("="*80)
print()

print("Expected ISNADI relations in this text:")
print("  1. مُّحَمَّدٌ ← رَّسُولُ (direct)")
print("  2. وَالَّذِينَ ← أَشِدَّاءُ (with 'معه' between)")
print()

detected_1 = any(l.head_id == 0 and l.dependent_id == 1 for l in links_v1)
detected_2_v1 = any(l.head_id == 3 and l.dependent_id == 5 for l in links_v1)
detected_2_v2 = any(l.head_id == 3 and l.dependent_id == 5 for l in links_v2)

print("V1 Results:")
print(f"  1. محمد ← رسول:        {'✅ Detected' if detected_1 else '❌ Missed'}")
print(f"  2. الذين ← أشداء:      {'✅ Detected' if detected_2_v1 else '❌ Missed (particle in between)'}")
print()

print("V2 Results:")
print(f"  1. محمد ← رسول:        {'✅ Detected' if detected_1 else '❌ Missed'}")
print(f"  2. الذين ← أشداء:      {'✅ Detected' if detected_2_v2 else '❌ Missed'}")
print()

if detected_2_v2 and not detected_2_v1:
    print("🎉 Success! V2 can now skip particles between مبتدأ and خبر!")
    print()

print("="*80)
print("✅ Comparison Complete")
print("="*80)
