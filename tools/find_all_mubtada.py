#!/usr/bin/env python3
"""
Find ALL potential مبتدأ in Surah Al-Fath (48:29)

Analyzes the complete verse to identify all nominative nouns

Author: Hussein Hiyassat
Date: 2025-02-13
"""

import sys
sys.path.insert(0, 'src')

from fvafk.c2b.word_form import WordForm, Span, PartOfSpeech, Case, Number, Gender

print("="*80)
print("🔍 Complete Analysis of Surah Al-Fath (48:29)")
print("   Finding ALL potential مبتدأ")
print("="*80)
print()

# The complete verse with all major words
# Based on: مُّحَمَّدٌ رَّسُولُ اللَّهِ وَالَّذِينَ مَعَهُ أَشِدَّاءُ عَلَى الْكُفَّارِ 
#          رُحَمَاءُ بَيْنَهُمْ تَرَاهُمْ رُكَّعًا سُجَّدًا يَبْتَغُونَ فَضْلًا مِّنَ اللَّهِ 
#          وَرِضْوَانًا سِيمَاهُمْ فِي وُجُوهِهِم مِّنْ أَثَرِ السُّجُودِ...

all_words = [
    # Part 1: محمدٌ رسولُ الله
    WordForm(word_id=0, surface='مُّحَمَّدٌ', span=Span(0, 10),
             pos=PartOfSpeech.NOUN, case=Case.NOMINATIVE,
             definiteness=False, number=Number.SINGULAR, gender=Gender.MASCULINE),
    
    WordForm(word_id=1, surface='رَّسُولُ', span=Span(11, 19),
             pos=PartOfSpeech.NOUN, case=Case.NOMINATIVE,
             definiteness=False, number=Number.SINGULAR, gender=Gender.MASCULINE),
    
    WordForm(word_id=2, surface='اللَّهِ', span=Span(20, 26),
             pos=PartOfSpeech.NOUN, case=Case.GENITIVE,
             definiteness=True, number=Number.SINGULAR, gender=Gender.MASCULINE),
    
    # Part 2: والذين معه أشداءُ على الكفار
    WordForm(word_id=3, surface='وَالَّذِينَ', span=Span(27, 37),
             pos=PartOfSpeech.NOUN, case=Case.NOMINATIVE,
             definiteness=True, number=Number.PLURAL, gender=Gender.MASCULINE),
    
    WordForm(word_id=4, surface='مَعَهُ', span=Span(38, 43),
             pos=PartOfSpeech.PARTICLE, case=Case.UNKNOWN,
             number=Number.SINGULAR, gender=Gender.MASCULINE),
    
    WordForm(word_id=5, surface='أَشِدَّاءُ', span=Span(44, 53),
             pos=PartOfSpeech.NOUN, case=Case.NOMINATIVE,
             definiteness=False, number=Number.PLURAL, gender=Gender.MASCULINE),
    
    WordForm(word_id=6, surface='عَلَى', span=Span(54, 58),
             pos=PartOfSpeech.PARTICLE, case=Case.UNKNOWN,
             number=Number.SINGULAR, gender=Gender.MASCULINE),
    
    WordForm(word_id=7, surface='الْكُفَّارِ', span=Span(59, 68),
             pos=PartOfSpeech.NOUN, case=Case.GENITIVE,
             definiteness=True, number=Number.PLURAL, gender=Gender.MASCULINE),
    
    # Part 3: رحماءُ بينهم
    WordForm(word_id=8, surface='رُحَمَاءُ', span=Span(69, 77),
             pos=PartOfSpeech.NOUN, case=Case.NOMINATIVE,
             definiteness=False, number=Number.PLURAL, gender=Gender.MASCULINE),
    
    WordForm(word_id=9, surface='بَيْنَهُمْ', span=Span(78, 87),
             pos=PartOfSpeech.PARTICLE, case=Case.UNKNOWN,
             number=Number.PLURAL, gender=Gender.MASCULINE),
    
    # Part 4: تراهم ركعاً سجداً
    WordForm(word_id=10, surface='تَرَاهُمْ', span=Span(88, 95),
             pos=PartOfSpeech.VERB, case=Case.UNKNOWN,
             number=Number.PLURAL, gender=Gender.MASCULINE),
    
    WordForm(word_id=11, surface='رُكَّعًا', span=Span(96, 103),
             pos=PartOfSpeech.NOUN, case=Case.ACCUSATIVE,
             definiteness=False, number=Number.PLURAL, gender=Gender.MASCULINE),
    
    WordForm(word_id=12, surface='سُجَّدًا', span=Span(104, 111),
             pos=PartOfSpeech.NOUN, case=Case.ACCUSATIVE,
             definiteness=False, number=Number.PLURAL, gender=Gender.MASCULINE),
    
    # Part 5: يبتغون فضلاً
    WordForm(word_id=13, surface='يَبْتَغُونَ', span=Span(112, 121),
             pos=PartOfSpeech.VERB, case=Case.UNKNOWN,
             number=Number.PLURAL, gender=Gender.MASCULINE),
    
    WordForm(word_id=14, surface='فَضْلًا', span=Span(122, 128),
             pos=PartOfSpeech.NOUN, case=Case.ACCUSATIVE,
             definiteness=False, number=Number.SINGULAR, gender=Gender.MASCULINE),
    
    # Part 6: سيماهم في وجوههم
    WordForm(word_id=15, surface='سِيمَاهُمْ', span=Span(129, 138),
             pos=PartOfSpeech.NOUN, case=Case.NOMINATIVE,
             definiteness=False, number=Number.SINGULAR, gender=Gender.FEMININE),
    
    WordForm(word_id=16, surface='فِي', span=Span(139, 141),
             pos=PartOfSpeech.PARTICLE, case=Case.UNKNOWN,
             number=Number.SINGULAR, gender=Gender.MASCULINE),
    
    WordForm(word_id=17, surface='وُجُوهِهِم', span=Span(142, 151),
             pos=PartOfSpeech.NOUN, case=Case.GENITIVE,
             definiteness=False, number=Number.PLURAL, gender=Gender.MASCULINE),
]

print(f"Total words analyzed: {len(all_words)}")
print()

# Find ALL nominative nouns
print("="*80)
print("📋 ALL NOMINATIVE NOUNS (potential مبتدأ)")
print("="*80)
print()

nominative_nouns = [
    (i, wf) for i, wf in enumerate(all_words)
    if wf.is_noun and wf.case == Case.NOMINATIVE
]

print(f"Found {len(nominative_nouns)} nominative noun(s):")
print()

for idx, (i, wf) in enumerate(nominative_nouns, 1):
    def_str = "معرفة" if wf.is_definite else "نكرة"
    print(f"{idx}. Word #{i:2}: {wf.surface:15} "
          f"({def_str:5}, {wf.number.arabic:5}, {wf.gender.arabic:5})")

print()

# Analyze which ones could be مبتدأ
print("="*80)
print("🔍 DETAILED ANALYSIS - Which are مبتدأ?")
print("="*80)
print()

for idx, (i, wf) in enumerate(nominative_nouns, 1):
    print(f"{idx}. {wf.surface}")
    
    # Check if it's at a valid position for مبتدأ
    # مبتدأ usually comes:
    # - At beginning (i=0)
    # - After و (coordinating)
    # - After period/new clause
    
    # Look for potential خبر after it
    has_khabar = False
    khabar_candidate = None
    skipped_words = []
    
    for j in range(i + 1, min(len(all_words), i + 6)):
        next_word = all_words[j]
        
        # Skip particles and genitives
        if next_word.is_particle or next_word.case == Case.GENITIVE:
            skipped_words.append(next_word.surface)
            continue
        
        # Check if nominative noun (potential خبر)
        if next_word.is_noun and next_word.case == Case.NOMINATIVE:
            # Check agreement
            if wf.agrees_with(next_word, ['number', 'gender']):
                has_khabar = True
                khabar_candidate = next_word
                break
    
    def_str = "معرفة" if wf.is_definite else "نكرة"
    print(f"   Type: {def_str}, {wf.number.arabic}, {wf.gender.arabic}")
    
    if has_khabar:
        print(f"   ✅ Likely مبتدأ")
        print(f"   خبر candidate: {khabar_candidate.surface}")
        if skipped_words:
            print(f"   Words between: {', '.join(skipped_words)}")
    else:
        print(f"   ❓ Might be:")
        
        # Check context
        if i > 0:
            prev_word = all_words[i-1]
            if prev_word.is_particle:
                print(f"      - Part of previous phrase (after {prev_word.surface})")
            elif prev_word.is_verb:
                print(f"      - فاعل for verb {prev_word.surface}")
        
        # Check if it's a second خبر (عطف)
        if idx > 1:
            prev_nom = nominative_nouns[idx-2][1]
            if wf.agrees_with(prev_nom, ['number', 'gender']):
                print(f"      - خبر ثانٍ (معطوف) for {prev_nom.surface}")
    
    print()

# Summary
print("="*80)
print("📊 SUMMARY")
print("="*80)
print()

likely_mubtada = []
for i, wf in nominative_nouns:
    # Check for خبر
    for j in range(i + 1, min(len(all_words), i + 6)):
        next_word = all_words[j]
        if next_word.is_particle or next_word.case == Case.GENITIVE:
            continue
        if next_word.is_noun and next_word.case == Case.NOMINATIVE:
            if wf.agrees_with(next_word, ['number', 'gender']):
                likely_mubtada.append(wf.surface)
                break

print(f"Likely مبتدأ: {len(likely_mubtada)}")
for word in likely_mubtada:
    print(f"  • {word}")
print()

print(f"Total nominative nouns: {len(nominative_nouns)}")
print()

print("💡 Notes:")
print("  - Some nominative nouns might be خبر (not مبتدأ)")
print("  - Some might be خبر ثانٍ (second predicate with عطف)")
print("  - Some might be part of complex phrases")
print()

print("="*80)
print("✅ Analysis Complete")
print("="*80)
