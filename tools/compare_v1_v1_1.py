#!/usr/bin/env python3
"""
Compare ISNADI Linker V1 vs V1.1

Shows the improvement with phrase skipping

Author: Hussein Hiyassat
Date: 2025-02-13
"""

import sys
sys.path.insert(0, 'src')

from fvafk.c2b.word_form import WordForm, Span, PartOfSpeech, Case, Number, Gender

# Import V1 (original)
from fvafk.syntax.linkers import find_isnadi_links as find_isnadi_links_v1

# Import V1.1
import importlib.util
spec = importlib.util.spec_from_file_location("isnadi_v1_1", "tools/isnadi_linker_v1_1.py")
isnadi_v1_1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(isnadi_v1_1)

print("="*80)
print("🕌 ISNADI Linker V1 vs V1.1 Comparison")
print("="*80)
print()

# Test case: والذين معه أشداءُ
words = [
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

print("Sample text: محمدٌ رسولُ الله والذين معه أشداءُ")
print()

# Test V1
print("="*80)
print("📊 V1 (Original)")
print("="*80)
print()

links_v1 = find_isnadi_links_v1(words)
print(f"Detected: {len(links_v1)} link(s)")
print()

for link in links_v1:
    mubtada = words[link.head_id]
    khabar = words[link.dependent_id]
    print(f"  {mubtada.surface} ← {khabar.surface}")
    print(f"  Confidence: {link.confidence:.0%}")
print()

# Test V1.1
print("="*80)
print("🚀 V1.1 (With phrase skipping)")
print("="*80)
print()

links_v1_1 = isnadi_v1_1.find_isnadi_links(words)
print(f"Detected: {len(links_v1_1)} link(s)")
print()

for link in links_v1_1:
    mubtada = words[link.head_id]
    khabar = words[link.dependent_id]
    print(f"  {mubtada.surface} ← {khabar.surface}")
    print(f"  Confidence: {link.confidence:.0%}")
print()

# Compare
print("="*80)
print("📈 COMPARISON")
print("="*80)
print()

print(f"V1 detected:   {len(links_v1)} link(s)")
print(f"V1.1 detected: {len(links_v1_1)} link(s)")
print()

if len(links_v1_1) > len(links_v1):
    print(f"✅ V1.1 found {len(links_v1_1) - len(links_v1)} additional link(s)!")
    
    # Show what V1.1 found that V1 didn't
    v1_pairs = set((l.head_id, l.dependent_id) for l in links_v1)
    v1_1_pairs = set((l.head_id, l.dependent_id) for l in links_v1_1)
    new_pairs = v1_1_pairs - v1_pairs
    
    if new_pairs:
        print()
        print("New detections in V1.1:")
        for head_id, dep_id in new_pairs:
            mubtada = words[head_id]
            khabar = words[dep_id]
            print(f"  • {mubtada.surface} ← {khabar.surface}")
            
            # Show what was skipped
            between = []
            for i in range(head_id + 1, dep_id):
                between.append(words[i].surface)
            if between:
                print(f"    (skipped: {', '.join(between)})")
elif len(links_v1_1) == len(links_v1):
    print("Both versions detected the same number of links")
print()

print("="*80)
print("💡 V1.1 Enhancement")
print("="*80)
print()

print("Key improvement: Can skip particles/phrases between مبتدأ and خبر")
print()
print("Skippable items:")
print("  • Particles (PARTICLE pos)")
print("  • Prep + pronoun (معه، فيه، عليه، etc.)")
print("  • Short phrases (≤5 chars ending in ه/ها/هم)")
print()

print("="*80)
print("✅ Comparison Complete")
print("="*80)
