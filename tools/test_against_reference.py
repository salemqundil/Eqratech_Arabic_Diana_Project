#!/usr/bin/env python3
"""
Test ISNADI Linker against Reference Grammatical Analysis

Compares detected links with the reference CSV from traditional إعراب

Author: Hussein Hiyassat
Date: 2025-02-13
"""

import sys
import csv
from pathlib import Path

sys.path.insert(0, 'src')

print("="*80)
print("📊 ISNADI Linker - Reference Test")
print("   Surah Al-Fath (48:29)")
print("="*80)
print()

# Load reference data
reference_file = Path("tools/fath_verse_reference.csv")

if not reference_file.exists():
    print(f"❌ Reference file not found: {reference_file}")
    print("   Please ensure fath_verse_reference.csv is in tools/")
    sys.exit(1)

# Parse reference
reference_data = []
with open(reference_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        reference_data.append(row)

print(f"✅ Loaded {len(reference_data)} words from reference")
print()

# Extract مبتدأ/خبر pairs from reference
print("="*80)
print("📋 EXPECTED ISNADI RELATIONS (from reference)")
print("="*80)
print()

mubtada_khabar_pairs = []
current_mubtada = None

for i, word in enumerate(reference_data):
    role = word['grammatical_role']
    
    # Check if مبتدأ
    if 'مبتدأ' in role:
        current_mubtada = {
            'index': i,
            'word': word['word'],
            'akhbar': []
        }
    
    # Check if خبر
    elif 'خبر' in role and current_mubtada:
        # Check if it's خبر for this مبتدأ
        parent = word.get('parent_word', '')
        
        # Extract خبر type
        if 'خبر أول' in role or 'خبر ثانٍ' in role or 'خبر ثالث' in role:
            khabar_num = role
        elif parent == current_mubtada['word'] or parent in [current_mubtada['word']]:
            khabar_num = role
        else:
            khabar_num = role
        
        current_mubtada['akhbar'].append({
            'index': i,
            'word': word['word'],
            'type': khabar_num
        })
    
    # If we hit a new مبتدأ, save the previous one
    if 'مبتدأ' in role and current_mubtada and current_mubtada.get('akhbar'):
        mubtada_khabar_pairs.append(current_mubtada)
        current_mubtada = {
            'index': i,
            'word': word['word'],
            'akhbar': []
        }

# Don't forget the last مبتدأ
if current_mubtada and current_mubtada.get('akhbar'):
    mubtada_khabar_pairs.append(current_mubtada)

print(f"Found {len(mubtada_khabar_pairs)} مبتدأ with خبر:")
print()

for i, pair in enumerate(mubtada_khabar_pairs, 1):
    print(f"{i}. مبتدأ: {pair['word']}")
    for khabar in pair['akhbar']:
        print(f"   → خبر: {khabar['word']} ({khabar['type']})")
    print()

# Summary statistics
print("="*80)
print("📊 REFERENCE SUMMARY")
print("="*80)
print()

from collections import Counter

# Count grammatical roles
roles = [w['grammatical_role'] for w in reference_data if w['grammatical_role']]
role_counts = Counter(roles)

print("Top grammatical roles:")
for role, count in role_counts.most_common(10):
    print(f"  {role:30} {count:2}")
print()

# Count POS
pos_counts = Counter(w['pos'] for w in reference_data)
print("Part of Speech distribution:")
for pos, count in pos_counts.most_common():
    print(f"  {pos:15} {count:2}")
print()

# Count cases
case_counts = Counter(w['case'] for w in reference_data if w['case'] != 'unknown')
print("Case distribution:")
for case, count in case_counts.most_common():
    print(f"  {case:15} {count:2}")
print()

print("="*80)
print("💡 USE THIS AS REFERENCE")
print("="*80)
print()

print("This reference shows the EXPECTED analysis.")
print("Compare your ISNADI Linker results against this.")
print()

print("Expected مبتدأ/خبر pairs:")
print(f"  • Total pairs: {len(mubtada_khabar_pairs)}")
print()

for i, pair in enumerate(mubtada_khabar_pairs, 1):
    akhbar_list = ', '.join([k['word'] for k in pair['akhbar']])
    print(f"  {i}. {pair['word']} ← {akhbar_list}")

print()
print("="*80)
print("✅ Reference loaded successfully")
print("="*80)
print()

print("📝 Next steps:")
print("  1. Run your ISNADI Linker on the verse")
print("  2. Compare detected links with this reference")
print("  3. Calculate precision/recall")
print("  4. Improve the linker based on gaps")
