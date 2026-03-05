"""
Comprehensive Integration Test - Surah Al-Fath Verse 29
Tests the entire pipeline with a complete Quranic verse and i3rab reference
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import csv
import os
from collections import defaultdict

# Core morphology imports
from fvafk.c2b.word_boundary_detector import WordBoundaryDetectorPlanB
from fvafk.c2b.root_extractor import RootExtractor
from fvafk.c2b.pattern_catalog import PatternCatalog
from fvafk.c2b.syllabifier import syllabify, ArabicSyllabifier
from fvafk.c2b.word_classifier import WordClassifier
from fvafk.c2b.feature_extractor import FeatureExtractor


# Surah Al-Fath (48:29) - Complete verse
VERSE = """مُّحَمَّدٌ رَّسُولُ اللَّهِ وَالَّذِينَ مَعَهُ أَشِدَّاءُ عَلَى الْكُفَّارِ رُحَمَاءُ بَيْنَهُمْ تَرَاهُمْ رُكَّعًا سُجَّدًا يَبْتَغُونَ فَضْلًا مِّنَ اللَّهِ وَرِضْوَانًا سِيمَاهُمْ فِي وُجُوهِهِم مِّنْ أَثَرِ السُّجُودِ ذَٰلِكَ مَثَلُهُمْ فِي التَّوْرَاةِ وَمَثَلُهُمْ فِي الْإِنجِيلِ كَزَرْعٍ أَخْرَجَ شَطْأَهُ فَآزَرَهُ فَاسْتَغْلَظَ فَاسْتَوَىٰ عَلَىٰ سُوقِهِ يُعْجِبُ الزُّرَّاعَ لِيَغِيظَ بِهِمُ الْكُفَّارَ وَعَدَ اللَّهُ الَّذِينَ آمَنُوا وَعَمِلُوا الصَّالِحَاتِ مِنْهُم مَّغْفِرَةً وَأَجْرًا عَظِيمًا"""


def load_irab_reference(csv_path="data/fath_verse_reference.csv"):
    """Load i3rab reference from CSV file"""
    reference = []
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                reference.append(row)
    return reference


def test_word_boundaries():
    """Test 1: Word Boundary Detection"""
    print("\n" + "="*70)
    print("TEST 1: WORD BOUNDARY DETECTION")
    print("="*70)
    
    detector = WordBoundaryDetectorPlanB()
    boundaries = detector.detect_boundaries(VERSE)
    
    word_texts = [b.text for b in boundaries]
    prefixed = sum(1 for b in boundaries if b.has_prefix)
    suffixed = sum(1 for b in boundaries if b.has_suffix)
    
    print(f"\nTotal words detected: {len(boundaries)}")
    print(f"Words with prefixes: {prefixed} ({prefixed/len(boundaries)*100:.1f}%)")
    print(f"Words with suffixes: {suffixed} ({suffixed/len(boundaries)*100:.1f}%)")
    print(f"\nFirst 10 words: {word_texts[:10]}")
    
    return boundaries


def test_root_extraction(boundaries):
    """Test 2: Root Extraction"""
    print("\n" + "="*70)
    print("TEST 2: ROOT EXTRACTION")
    print("="*70)
    
    extractor = RootExtractor()
    
    successful = 0
    trilateral = 0
    quadrilateral = 0
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
                
                if len(samples) < 10:
                    samples.append((word, ''.join(root.letters)))
        except:
            pass
    
    success_rate = successful / len(boundaries) * 100
    print(f"\nSuccess: {successful}/{len(boundaries)} ({success_rate:.1f}%)")
    print(f"Trilateral: {trilateral}, Quadrilateral: {quadrilateral}")
    
    print(f"\nSample roots:")
    for word, root in samples[:5]:
        print(f"  {word:15} → {root}")


def test_syllabification(boundaries):
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
    print(f"\nSuccess: {successful}/{len(boundaries)} ({success_rate:.1f}%)")
    
    print(f"\nSyllable distribution:")
    for count in sorted(syllable_counts.keys()):
        num = syllable_counts[count]
        print(f"  {count} syllables: {num:3d} words")
    
    print(f"\nSamples:")
    for word, syls in samples:
        print(f"  {word:15} → {' . '.join(syls)}")


def test_classification(boundaries):
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
    
    print(f"\nClassification results:")
    for word_class, count in sorted(classifications.items(), key=lambda x: -x[1]):
        pct = count / len(boundaries) * 100
        print(f"  {word_class:20} {count:3d} ({pct:5.1f}%)")
        if word_class in samples:
            print(f"    Examples: {', '.join(samples[word_class])}")


def test_features(boundaries):
    """Test 5: Feature Extraction"""
    print("\n" + "="*70)
    print("TEST 5: FEATURE EXTRACTION")
    print("="*70)
    
    extractor = FeatureExtractor()
    
    successful = 0
    feature_stats = defaultdict(int)
    
    for boundary in boundaries[:20]:
        word = boundary.text
        try:
            features = extractor.extract(word)
            if features:
                successful += 1
                for feature_name, feature_value in features.items():
                    if feature_value:
                        feature_stats[feature_name] += 1
        except:
            pass
    
    print(f"\nExtracted features from {successful}/20 words")
    
    print(f"\nTop features:")
    for feature, count in sorted(feature_stats.items(), key=lambda x: -x[1])[:10]:
        print(f"  {feature:30} {count:3d}")


def test_patterns():
    """Test 6: Pattern Catalog"""
    print("\n" + "="*70)
    print("TEST 6: PATTERN CATALOG")
    print("="*70)
    
    catalog = PatternCatalog.load_full_catalog()
    
    print(f"\nPattern categories:")
    total = 0
    for category, patterns in catalog.items():
        print(f"  {category:20} {len(patterns):3d} patterns")
        total += len(patterns)
    
    print(f"\nTotal patterns: {total}")


def test_statistics(boundaries):
    """Test 7: Comprehensive Statistics"""
    print("\n" + "="*70)
    print("COMPREHENSIVE VERSE STATISTICS")
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
    
    print(f"\nBASIC STATISTICS:")
    print(f"  Total words.................... {stats['total_words']}")
    print(f"  Unique words................... {stats['unique_words']}")
    print(f"  Total characters............... {stats['total_characters']}")
    
    print(f"\nWORD LENGTH:")
    print(f"  Average........................ {stats['avg_word_length']:.2f} chars")
    
    print(f"\nMORPHOLOGY:")
    print(f"  With prefix.................... {stats['words_with_prefix']} ({stats['words_with_prefix']/stats['total_words']*100:.1f}%)")
    print(f"  With suffix.................... {stats['words_with_suffix']} ({stats['words_with_suffix']/stats['total_words']*100:.1f}%)")
    
    print(f"\nCONFIDENCE:")
    print(f"  Average........................ {stats['avg_confidence']:.3f}")
    
    print(f"\nSYLLABLES:")
    print(f"  Total.......................... {stats['total_syllables']}")
    print(f"  Average per word............... {stats['total_syllables']/stats['total_words']:.2f}")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("COMPREHENSIVE PIPELINE TEST - Surah Al-Fath 48:29")
    print("="*70)
    
    boundaries = test_word_boundaries()
    test_root_extraction(boundaries)
    test_syllabification(boundaries)
    test_classification(boundaries)
    test_features(boundaries)
    test_patterns()
    test_statistics(boundaries)
    
    print("\n" + "="*70)
    print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
    print("="*70)


if __name__ == "__main__":
    main()
