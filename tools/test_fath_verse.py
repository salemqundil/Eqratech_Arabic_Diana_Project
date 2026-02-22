#!/usr/bin/env python3
"""
Test ISNADI Linker on Surah Al-Fath (48:29)

This script tests the complete pipeline:
1. C2B morphological analysis
2. WordForm conversion
3. ISNADI link detection

Author: Hussein Hiyassat
Date: 2025-02-13
"""

import sys
import json
sys.path.insert(0, 'src')

from fvafk.cli.main import main as cli_main
from fvafk.c2b.word_form.word_form_builder import build_word_forms
from fvafk.syntax.linkers import find_isnadi_links
import subprocess

# The verse
VERSE = """مُّحَمَّدٌ رَّسُولُ اللَّهِ وَالَّذِينَ مَعَهُ أَشِدَّاءُ عَلَى الْكُفَّارِ رُحَمَاءُ بَيْنَهُمْ تَرَاهُمْ رُكَّعًا سُجَّدًا يَبْتَغُونَ فَضْلًا مِّنَ اللَّهِ وَرِضْوَانًا سِيمَاهُمْ فِي وُجُوهِهِم مِّنْ أَثَرِ السُّجُودِ ذَٰلِكَ مَثَلُهُمْ فِي التَّوْرَاةِ وَمَثَلُهُمْ فِي الْإِنجِيلِ كَزَرْعٍ أَخْرَجَ شَطْأَهُ فَآزَرَهُ فَاسْتَغْلَظَ فَاسْتَوَىٰ عَلَىٰ سُوقِهِ يُعْجِبُ الزُّرَّاعَ لِيَغِيظَ بِهِمُ الْكُفَّارَ وَعَدَ اللَّهُ الَّذِينَ آمَنُوا وَعَمِلُوا الصَّالِحَاتِ مِنْهُم مَّغْفِرَةً وَأَجْرًا عَظِيمًا"""

print("="*80)
print("🕌 Testing ISNADI Linker on Surah Al-Fath (48:29)")
print("="*80)
print()

# Step 1: Run C2B pipeline
print("📊 Step 1: Running C2B morphological analysis...")
print()

result = subprocess.run(
    ['python3', '-m', 'fvafk.cli', VERSE],
    capture_output=True,
    text=True,
    cwd='.'
)

if result.returncode != 0:
    print("❌ Error running CLI:")
    print(result.stderr)
    sys.exit(1)

c2b_output = json.loads(result.stdout)
print(f"✅ Analyzed {len(c2b_output['c2b']['words'])} words")
print()

# Step 2: Convert to WordForms
print("🔄 Step 2: Converting to WordForm instances...")
print()

word_forms = build_word_forms(c2b_output['c2b']['words'])
print(f"✅ Created {len(word_forms)} WordForm instances")
print()

# Step 3: Find ISNADI links
print("🔗 Step 3: Detecting ISNADI links (مبتدأ/خبر)...")
print()

links = find_isnadi_links(word_forms)
print(f"✅ Found {len(links)} ISNADI link(s)")
print()

# Step 4: Display results
print("="*80)
print("📋 DETECTED ISNADI RELATIONS")
print("="*80)
print()

if len(links) == 0:
    print("⚠️  No ISNADI links detected")
    print()
    print("Possible reasons:")
    print("- No nominal sentences (الجملة الاسمية) found")
    print("- مبتدأ and خبر don't agree in case/number/gender")
    print("- Sentences are verbal (الجملة الفعلية)")
else:
    for i, link in enumerate(links, 1):
        mubtada = word_forms[link.head_id]
        khabar = word_forms[link.dependent_id]
        
        print(f"Link {i}:")
        print(f"  مبتدأ: {mubtada.surface}")
        print(f"    • Position: {mubtada.span.start}-{mubtada.span.end}")
        print(f"    • Case: {mubtada.case.arabic}")
        print(f"    • Number: {mubtada.number.arabic}")
        print(f"    • Gender: {mubtada.gender.arabic}")
        print(f"    • Definite: {mubtada.is_definite}")
        print()
        print(f"  خبر: {khabar.surface}")
        print(f"    • Position: {khabar.span.start}-{khabar.span.end}")
        print(f"    • Case: {khabar.case.arabic}")
        print(f"    • Number: {khabar.number.arabic}")
        print(f"    • Gender: {khabar.gender.arabic}")
        print(f"    • Definite: {khabar.is_definite}")
        print()
        print(f"  Confidence: {link.confidence:.2%}")
        print(f"  Reason: {link.reason}")
        print()
        print("-" * 80)
        print()

# Step 5: Word-by-word analysis
print("="*80)
print("📝 WORD-BY-WORD ANALYSIS")
print("="*80)
print()

print(f"{'#':<4} {'Word':<20} {'POS':<10} {'Case':<10} {'Num':<8} {'Gender':<8} {'Def':<5}")
print("-" * 80)

for i, wf in enumerate(word_forms):
    print(f"{i:<4} {wf.surface:<20} {str(wf.pos):<10} {wf.case.arabic:<10} "
          f"{wf.number.arabic:<8} {wf.gender.arabic:<8} {'✓' if wf.is_definite else '✗':<5}")

print()

# Step 6: Summary statistics
print("="*80)
print("📊 SUMMARY STATISTICS")
print("="*80)
print()

from collections import Counter

pos_counts = Counter(wf.pos for wf in word_forms)
case_counts = Counter(wf.case for wf in word_forms)

print("Part of Speech distribution:")
for pos, count in pos_counts.most_common():
    print(f"  {str(pos):15} {count:3}")
print()

print("Case distribution:")
for case, count in case_counts.most_common():
    print(f"  {case.arabic:15} {count:3}")
print()

print("ISNADI links found:", len(links))
print()

# Step 7: Potential nominal sentences
print("="*80)
print("🔍 POTENTIAL NOMINAL SENTENCES")
print("="*80)
print()

# Look for potential مبتدأ (nominative nouns)
potential_mubtada = [
    (i, wf) for i, wf in enumerate(word_forms)
    if wf.is_noun and wf.case.name == 'NOMINATIVE'
]

if potential_mubtada:
    print(f"Found {len(potential_mubtada)} potential مبتدأ (nominative nouns):")
    print()
    for i, wf in potential_mubtada:
        print(f"  {i:3}. {wf.surface:20} ({wf.case.arabic}, {wf.number.arabic}, "
              f"{'معرفة' if wf.is_definite else 'نكرة'})")
    print()
else:
    print("⚠️  No nominative nouns found (potential مبتدأ)")
    print()

print("="*80)
print("✅ Analysis Complete!")
print("="*80)
