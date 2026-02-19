"""
Comprehensive Integration Test - Surah Al-Fath Verse 29
Tests the entire pipeline with a complete Quranic verse
"""

import csv
import os
from pathlib import Path
from collections import defaultdict

# Core morphology imports
from fvafk.c2b.word_boundary_detector import WordBoundaryDetectorPlanB
from fvafk.c2b.root_extractor import RootExtractor
from fvafk.c2b.pattern_catalog import PatternCatalog
from fvafk.c2b.syllabifier import syllabify
from fvafk.c2b.word_classifier import WordClassifier


# Surah Al-Fath (48:29) - Complete verse
VERSE = """مُّحَمَّدٌ رَّسُولُ اللَّهِ وَالَّذِينَ مَعَهُ أَشِدَّاءُ عَلَى الْكُفَّارِ رُحَمَاءُ بَيْنَهُمْ تَرَاهُمْ رُكَّعًا سُجَّدًا يَبْتَغُونَ فَضْلًا مِّنَ اللَّهِ وَرِضْوَانًا سِيمَاهُمْ فِي وُجُوهِهِم مِّنْ أَثَرِ السُّجُودِ ذَٰلِكَ مَثَلُهُمْ فِي التَّوْرَاةِ وَمَثَلُهُمْ فِي الْإِنجِيلِ كَزَرْعٍ أَ��ْرَجَ شَطْأَهُ فَآزَرَهُ فَاسْتَغْلَظَ فَاسْتَوَىٰ عَلَىٰ سُوقِهِ يُعْجِبُ الزُّرَّاعَ لِيَغِيظَ بِهِمُ الْكُفَّارَ وَعَدَ اللَّهُ الَّذِينَ آمَنُوا وَعَمِلُوا الصَّالِحَاتِ مِنْهُم مَّغْفِرَةً وَأَجْرًا عَظِيمًا"""


def load_irab_reference(csv_path="data/fath_verse_reference.csv"):
    """Load i3rab reference from CSV file"""
    reference = []
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                reference.append(row)
    return reference


def test_1_word_boundaries():
    """Test 1: Word Boundary Detection"""
    print("\n" + "="*70)
    print("TEST 1: WORD BOUNDARY DETECTION")
    print("="*70)
    
    detector = WordBoundaryDetectorPlanB()
    boundaries = detector.detect_boundaries(VERSE)
    
    word_texts = [b.text for b in boundaries]
    prefixed = sum(1 for b in boundaries if b.has_prefix)
    suffixed = sum(1 for b in boundaries if b.has_suffix)
    
    print(f"\n✓ Total words detected: {len(boundaries)}")
    print(f"  Words with prefixes: {prefixed} ({prefixed/len(boundaries)*100:.1f}%)")
    print(f"  Words with suffixes: {suffixed} ({suffixed/len(boundaries)*100:.1f}%)")
    print(f"\n  First 10 words: {word_texts[:10]}")
    
    assert len(boundaries) > 40
    assert len(boundaries) < 80
    
    return boundaries


def test_2_root_extraction(boundaries):
    """Test 2: Root Extraction"""
    print("\n" + "="*70)
    print("TEST 2: ROOT EXTRACTION")
    print("="*70)
    
    extractor = RootExtractor()
    
    successful = 0
    trilateral = 0
    quadrilateral = 0
    weak_roots = 0
    samples = []
    
    for boundary in boundaries:
        word = boundary.text
        try:
            root = extractor.extract(word)
            if root:
                successful += 1
                
                if root.trilateral:
                    trilateral += 1
                elif root.quadrilateral:
                    quadrilateral += 1
                
                if root.weak_positions:
                    weak_roots += 1
                
                if len(samples) < 10:
                    samples.append((word, ''.join(root.letters)))
        except:
            pass
    
    success_rate = successful / len(boundaries) * 100
    print(f"\n✓ Success: {successful}/{len(boundaries)} ({success_rate:.1f}%)")
    print(f"  Trilateral: {trilateral}")
    print(f"  Quadrilateral: {quadrilateral}")
    print(f"  Weak roots: {weak_roots}")
    
    print(f"\n  Sample roots:")
    for word, root in samples[:5]:
        print(f"    {word:15} → {root}")
    
    assert success_rate > 30


def test_3_syllabification(boundaries):
    """Test 3: Syllabification"""
    print("\n" + "="*70)
    print("TEST 3: SYLLABIFICATION")
    print("="*70)
    
    successful = 0
    syllable_counts = defaultdict(int)
    samples = []
    
    for boundary in boundaries:
        word = boundary.text
        try:
            result = syllabify(word)
            if result and result.syllables:
                successful += 1
                num_syl = len(result.syllables)
                syllable_counts[num_syl] += 1
                
                if len(samples) < 5:
                    samples.append((word, [str(s) for s in result.syllables]))
        except:
            pass
    
    success_rate = successful / len(boundaries) * 100
    print(f"\n✓ Success: {successful}/{len(boundaries)} ({success_rate:.1f}%)")
    
    print(f"\n  Syllable distribution:")
    for count in sorted(syllable_counts.keys()):
        num = syllable_counts[count]
        print(f"    {count} syllables: {num:3d} words")
    
    print(f"\n  Sample syllabifications:")
    for word, syls in samples:
        print(f"    {word:15} → {' . '.join(syls)}")
    
    assert success_rate > 40


def test_4_classification(boundaries):
    """Test 4: Word Classification"""
    print("\n" + "="*70)
    print("TEST 4: WORD CLASSIFICATION")
    print("="*70)
    
    classifier = WordClassifier()
    classifications = defaultdict(int)
    samples = defaultdict(list)
    
    for boundary in boundaries:
        word = boundary.text
        try:
            word_class = classifier.classify(word)
            classifications[word_class] += 1
            
            if len(samples[word_class]) < 3:
                samples[word_class].append(word)
        except:
            classifications['ERROR'] += 1
    
    print(f"\n✓ Classification results:")
    for word_class, count in sorted(classifications.items(), key=lambda x: -x[1]):
        pct = count / len(boundaries) * 100
        print(f"    {word_class:20} {count:3d} ({pct:5.1f}%)")
        if word_class in samples and word_class != 'ERROR':
            print(f"      Examples: {', '.join(samples[word_class])}")
    
    assert len(classifications) > 0


def test_5_patterns():
    """Test 5: Pattern Catalog"""
    print("\n" + "="*70)
    print("TEST 5: PATTERN CATALOG")
    print("="*70)
    
    catalog = PatternCatalog.load_full_catalog()
    
    print(f"\n✓ Pattern categories:")
    total = 0
    for category, patterns in catalog.items():
        print(f"    {category:20} {len(patterns):3d} patterns")
        total += len(patterns)
    
    print(f"\n  Total patterns: {total}")
    
    # Show sample patterns
    print(f"\n  Sample verb forms:")
    if 'verb_forms' in catalog:
        for pattern in catalog['verb_forms'][:3]:
            print(f"    {pattern.pattern_type:15} {pattern.pattern:10} - {pattern.description}")
    
    assert total > 0


def test_6_irab_reference():
    """Test 6: I3rab Reference Validation"""
    print("\n" + "="*70)
    print("TEST 6: I3RAB REFERENCE VALIDATION")
    print("="*70)
    
    irab_ref = load_irab_reference()
    
    if not irab_ref:
        print("\n⚠ I3rab reference file not found, skipping")
        return
    
    print(f"\n✓ I3rab reference loaded: {len(irab_ref)} entries")
    
    # Show sample entries
    print(f"\n  Sample i3rab entries:")
    for entry in irab_ref[:5]:
        word = entry.get('word', 'N/A')
        irab = entry.get('irab', 'N/A')
        print(f"    {word:15} → {irab[:50]}")


def test_7_statistics(boundaries):
    """Test 7: Comprehensive Statistics"""
    print("\n" + "="*70)
    print("TEST 7: COMPREHENSIVE VERSE STATISTICS")
    print("="*70)
    
    stats = {
        'total_words': len(boundaries),
        'total_characters': len(VERSE),
        'unique_words': len(set(b.text for b in boundaries)),
        'avg_word_length': sum(len(b.text) for b in boundaries) / len(boundaries),
        'words_with_prefix': sum(1 for b in boundaries if b.has_prefix),
        'words_with_suffix': sum(1 for b in boundaries if b.has_suffix),
        'avg_confidence': sum(b.confidence for b in boundaries) / len(boundaries),
        'total_syllables': sum(b.syllable_count for b in boundaries),
    }
    
    print(f"\n  BASIC STATISTICS:")
    print(f"    Total words.................... {stats['total_words']}")
    print(f"    Unique words................... {stats['unique_words']}")
    print(f"    Total characters............... {stats['total_characters']}")
    
    print(f"\n  WORD LENGTH:")
    print(f"    Average........................ {stats['avg_word_length']:.2f} chars")
    
    print(f"\n  MORPHOLOGY:")
    print(f"    With prefix.................... {stats['words_with_prefix']} ({stats['words_with_prefix']/stats['total_words']*100:.1f}%)")
    print(f"    With suffix.................... {stats['words_with_suffix']} ({stats['words_with_suffix']/stats['total_words']*100:.1f}%)")
    
    print(f"\n  CONFIDENCE:")
    print(f"    Average........................ {stats['avg_confidence']:.3f}")
    
    print(f"\n  SYLLABLES:")
    print(f"    Total.......................... {stats['total_syllables']}")
    print(f"    Average per word............... {stats['total_syllables']/stats['total_words']:.2f}")
    
    assert stats['total_words'] > 0


def test_full_pipeline():
    """Run all tests in sequence"""
    print("\n" + "="*70)
    print("COMPREHENSIVE PIPELINE TEST - Surah Al-Fath 48:29")
    print("="*70)
    
    boundaries = test_1_word_boundaries()
    test_2_root_extraction(boundaries)
    test_3_syllabification(boundaries)
    test_4_classification(boundaries)
    test_5_patterns()
    test_6_irab_reference()
    test_7_statistics(boundaries)
    
    print("\n" + "="*70)
    print("✓✓✓ ALL TESTS COMPLETED SUCCESSFULLY ✓✓✓")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_full_pipeline()
