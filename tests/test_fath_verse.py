"""
Comprehensive Integration Test - Arabic Text Analysis
Analyzes any Arabic text through the complete morphology pipeline
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import csv
import os
from collections import defaultdict
import argparse

from fvafk.c2b.word_boundary_detector import WordBoundaryDetectorPlanB
from fvafk.c2b.root_extractor import RootExtractor
from fvafk.c2b.pattern_catalog import PatternCatalog
from fvafk.c2b.syllabifier import syllabify
from fvafk.c2b.word_classifier import WordClassifier


# Default verse if no file provided
DEFAULT_VERSE = """مُّحَمَّدٌ رَّسُولُ اللَّهِ وَالَّذِينَ مَعَهُ أَشِدَّاءُ عَلَى الْكُفَّارِ رُحَمَاءُ بَيْنَهُمْ تَرَاهُمْ رُكَّعًا سُجَّدًا يَبْتَغُونَ فَضْلًا مِّنَ اللَّهِ وَرِضْوَانًا سِيمَاهُمْ فِي وُجُوهِهِم مِّنْ أَثَرِ السُّجُودِ ذَٰلِكَ مَثَلُهُمْ فِي التَّوْرَاةِ وَمَثَلُهُمْ فِي الْإِنجِيلِ كَزَرْعٍ أَخْرَجَ شَطْأَهُ فَآزَرَهُ فَاسْتَغْلَظَ فَاسْتَوَىٰ عَلَىٰ سُوقِهِ يُعْجِبُ الزُّرَّاعَ لِيَغِيظَ بِهِمُ الْكُفَّارَ وَعَدَ اللَّهُ الَّذِينَ آمَنُوا وَعَمِلُوا الصَّالِحَاتِ مِنْهُم مَّغْفِرَةً وَأَجْرًا عَظِيمًا"""


def load_text_from_file(file_path):
    """Load Arabic text from file"""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return None


def load_irab_reference(csv_path="tests/fath_verse_reference.csv"):
    """Load i3rab reference"""
    reference = []
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            reference = list(reader)
    return reference


def print_header(title, width=80):
    """Print formatted header"""
    print("\n" + "╔" + "═" * (width - 2) + "╗")
    print("║" + title.center(width - 2) + "║")
    print("╚" + "═" * (width - 2) + "╝")


def print_section(title, width=80):
    """Print section header"""
    print("\n" + "─" * width)
    print(f"  {title}")
    print("─" * width)


def print_result(label, value, indent=2):
    """Print formatted result"""
    spaces = " " * indent
    print(f"{spaces}• {label:30} {value}")


def print_table_row(col1, col2, col3="", width1=20, width2=40, width3=15):
    """Print formatted table row"""
    print(f"  │ {col1:<{width1}} │ {col2:<{width2}} │ {col3:>{width3}} │")


def test_1_word_boundaries(text):
    """Test 1: Word Boundary Detection"""
    print_header("TEST 1: WORD BOUNDARY DETECTION", 80)
    
    detector = WordBoundaryDetectorPlanB()
    boundaries = detector.detect_boundaries(text)
    
    word_texts = [b.text for b in boundaries]
    prefixed = [b for b in boundaries if b.has_prefix]
    suffixed = [b for b in boundaries if b.has_suffix]
    
    print_section("Summary Statistics")
    print_result("Total words detected", f"{len(boundaries)} words")
    print_result("Words with prefixes", f"{len(prefixed)} ({len(prefixed)/len(boundaries)*100:.1f}%)")
    print_result("Words with suffixes", f"{len(suffixed)} ({len(suffixed)/len(boundaries)*100:.1f}%)")
    
    print_section("Sample Words (First 15)")
    for i, word in enumerate(word_texts[:15], 1):
        prefix_mark = "✓" if boundaries[i-1].has_prefix else " "
        suffix_mark = "✓" if boundaries[i-1].has_suffix else " "
        conf = boundaries[i-1].confidence
        print(f"  {i:2d}. {word:20} [Prefix:{prefix_mark}] [Suffix:{suffix_mark}] Conf:{conf:.2f}")
    
    if len(prefixed) > 0:
        print_section("Sample Prefixed Words")
        for word in [b.text for b in prefixed[:5]]:
            print(f"    → {word}")
    
    if len(suffixed) > 0:
        print_section("Sample Suffixed Words")
        for word in [b.text for b in suffixed[:5]]:
            print(f"    → {word}")
    
    return boundaries


def test_2_root_extraction(boundaries):
    """Test 2: Root Extraction"""
    print_header("TEST 2: ROOT EXTRACTION ANALYSIS", 80)
    
    extractor = RootExtractor()
    successful = []
    failed = []
    trilateral = 0
    quadrilateral = 0
    weak_roots = []
    
    for boundary in boundaries:
        try:
            root = extractor.extract(boundary.text)
            if root:
                successful.append((boundary.text, root))
                if root.trilateral:
                    trilateral += 1
                elif root.quadrilateral:
                    quadrilateral += 1
                if root.weak_positions:
                    weak_roots.append((boundary.text, ''.join(root.letters)))
        except:
            failed.append(boundary.text)
    
    success_rate = len(successful) / len(boundaries) * 100
    
    print_section("Extraction Statistics")
    print_result("Success rate", f"{len(successful)}/{len(boundaries)} ({success_rate:.1f}%)")
    print_result("Trilateral roots", f"{trilateral}")
    print_result("Quadrilateral roots", f"{quadrilateral}")
    print_result("Weak roots detected", f"{len(weak_roots)}")
    
    print_section("Sample Root Extractions")
    print_table_row("Word", "Root", "Type", width1=20, width2=15, width3=15)
    print("  " + "─" * 76)
    
    for word, root in successful[:10]:
        root_str = ''.join(root.letters)
        root_type = "Trilateral" if root.trilateral else "Quadrilateral"
        print_table_row(word, root_str, root_type, width1=20, width2=15, width3=15)
    
    if weak_roots:
        print_section("Weak Roots (containing و، ي، ا)")
        for word, root in weak_roots[:5]:
            print(f"    {word:20} → {root}")
    
    if failed:
        print_section(f"Failed Extractions ({len(failed)} words)")
        print(f"    {', '.join(failed[:10])}")


def test_3_syllabification(boundaries):
    """Test 3: Syllabification"""
    print_header("TEST 3: SYLLABIFICATION ANALYSIS", 80)
    
    successful = []
    syllable_counts = defaultdict(int)
    syllable_types = defaultdict(int)
    
    for boundary in boundaries:
        try:
            result = syllabify(boundary.text)
            if result and result.syllables:
                successful.append((boundary.text, result))
                num_syl = len(result.syllables)
                syllable_counts[num_syl] += 1
                
                for syl in result.syllables:
                    syllable_types[syl.syllable_type] += 1
        except:
            pass
    
    success_rate = len(successful) / len(boundaries) * 100
    
    print_section("Syllabification Statistics")
    print_result("Success rate", f"{len(successful)}/{len(boundaries)} ({success_rate:.1f}%)")
    print_result("Total syllables", f"{sum(syllable_counts[k] * k for k in syllable_counts)}")
    
    print_section("Syllable Count Distribution")
    for count in sorted(syllable_counts.keys()):
        num = syllable_counts[count]
        bar = "█" * int(num / len(boundaries) * 50)
        print(f"    {count} syllables │ {num:3d} words │ {bar}")
    
    print_section("Syllable Type Distribution")
    total_syllables = sum(syllable_types.values())
    for syl_type in sorted(syllable_types.keys(), key=lambda x: syllable_types[x], reverse=True)[:8]:
        count = syllable_types[syl_type]
        pct = count / total_syllables * 100
        bar = "▓" * int(pct / 2)
        print(f"    {syl_type:6} │ {count:3d} ({pct:5.1f}%) │ {bar}")
    
    print_section("Sample Syllabifications")
    for word, result in successful[:8]:
        syls = [str(s) for s in result.syllables]
        print(f"    {word:20} → {' · '.join(syls)}")


def test_4_classification(boundaries):
    """Test 4: Word Classification"""
    print_header("TEST 4: WORD CLASSIFICATION", 80)
    
    classifier = WordClassifier()
    classifications = defaultdict(int)
    samples = defaultdict(list)
    
    for boundary in boundaries:
        try:
            word_class = classifier.classify(boundary.text)
            word_class_str = str(word_class.kind).split('.')[-1] if hasattr(word_class, 'kind') else str(word_class)
            classifications[word_class_str] += 1
            
            if len(samples[word_class_str]) < 3:
                samples[word_class_str].append(boundary.text)
        except Exception as e:
            classifications['ERROR'] += 1
    
    print_section("Classification Distribution")
    
    total = len(boundaries)
    for word_class in sorted(classifications.keys(), key=lambda x: classifications[x], reverse=True):
        count = classifications[word_class]
        pct = count / total * 100
        bar = "■" * int(pct / 2)
        
        print(f"\n  {word_class:20} │ {count:3d} words ({pct:5.1f}%) │ {bar}")
        
        if word_class in samples and word_class != 'ERROR':
            examples = ', '.join(samples[word_class])
            print(f"  {'':20} │ Examples: {examples}")


def test_5_patterns():
    """Test 5: Pattern Catalog"""
    print_header("TEST 5: MORPHOLOGICAL PATTERN CATALOG", 80)
    
    catalog = PatternCatalog.load_full_catalog()
    
    print_section("Pattern Categories")
    
    total = 0
    for category, patterns in catalog.items():
        count = len(patterns)
        total += count
        category_name = category.replace('_', ' ').title()
        print_result(category_name, f"{count} patterns")
    
    print_result("TOTAL PATTERNS", f"{total} patterns", indent=4)
    
    # Show sample verb forms
    if 'verb_forms' in catalog:
        print_section("Sample Verb Forms")
        for pattern in catalog['verb_forms'][:5]:
            print(f"    {pattern.name:25} {pattern.template:12} → {pattern.description}")
            if pattern.examples:
                print(f"    {'':25} Examples: {', '.join(pattern.examples[:3])}")
    
    # Show sample noun patterns
    if 'noun_patterns' in catalog:
        print_section("Sample Noun Patterns")
        for pattern in catalog['noun_patterns'][:5]:
            print(f"    {pattern.name:25} {pattern.template:12} → {pattern.description}")
            if pattern.examples:
                print(f"    {'':25} Examples: {', '.join(pattern.examples[:3])}")


def test_6_irab(boundaries):
    """Test 6: I3rab Reference"""
    print_header("TEST 6: I3RAB REFERENCE VALIDATION", 80)
    
    irab_ref = load_irab_reference()
    
    if not irab_ref:
        print("\n  ⚠️  I3rab reference file not found")
        return
    
    print_section("I3rab Reference Statistics")
    print_result("Total entries loaded", f"{len(irab_ref)} entries")
    
    # Try to match with detected words
    word_texts = [b.text for b in boundaries]
    matched = 0
    
    for entry in irab_ref:
        if entry.get('word') in word_texts:
            matched += 1
    
    if matched > 0:
        print_result("Matched with detected words", f"{matched}/{len(irab_ref)} ({matched/len(irab_ref)*100:.1f}%)")
    
    print_section("Sample I3rab Entries")
    print_table_row("Word", "I3rab Analysis", "", width1=15, width2=60, width3=0)
    print("  " + "─" * 76)
    
    for entry in irab_ref[:8]:
        word = entry.get('word', 'N/A')
        irab = entry.get('irab', 'N/A')[:55]
        print_table_row(word, irab, "", width1=15, width2=60, width3=0)


def test_7_statistics(boundaries):
    """Test 7: Comprehensive Statistics"""
    print_header("TEST 7: COMPREHENSIVE TEXT STATISTICS", 80)
    
    word_texts = [b.text for b in boundaries]
    word_lengths = [len(b.text) for b in boundaries]
    confidences = [b.confidence for b in boundaries]
    syllable_counts = [b.syllable_count for b in boundaries]
    
    print_section("Basic Statistics")
    print_result("Total words", f"{len(boundaries)} words")
    print_result("Unique words", f"{len(set(word_texts))} words")
    print_result("Repetition rate", f"{(1 - len(set(word_texts))/len(word_texts))*100:.1f}%")
    
    print_section("Word Length Analysis")
    print_result("Average word length", f"{sum(word_lengths)/len(word_lengths):.2f} characters")
    print_result("Shortest word", f"{min(word_lengths)} characters")
    print_result("Longest word", f"{max(word_lengths)} characters")
    
    print_section("Syllable Analysis")
    print_result("Total syllables", f"{sum(syllable_counts)} syllables")
    print_result("Average syllables/word", f"{sum(syllable_counts)/len(syllable_counts):.2f}")
    
    print_section("Confidence Scores")
    print_result("Average confidence", f"{sum(confidences)/len(confidences):.3f}")
    print_result("Minimum confidence", f"{min(confidences):.3f}")
    print_result("Maximum confidence", f"{max(confidences):.3f}")
    
    high_conf = sum(1 for c in confidences if c >= 0.8)
    med_conf = sum(1 for c in confidences if 0.5 <= c < 0.8)
    low_conf = sum(1 for c in confidences if c < 0.5)
    
    print_section("Confidence Distribution")
    print(f"    High (≥0.8)  │ {high_conf:3d} words │ {'█' * int(high_conf/len(boundaries)*50)}")
    print(f"    Med (0.5-0.8)│ {med_conf:3d} words │ {'▓' * int(med_conf/len(boundaries)*50)}")
    print(f"    Low (<0.5)   │ {low_conf:3d} words │ {'░' * int(low_conf/len(boundaries)*50)}")


def main():
    """Run all tests"""
    parser = argparse.ArgumentParser(description='Analyze Arabic text through morphology pipeline')
    parser.add_argument('--file', '-f', type=str, default='tests/test_text.txt',
                       help='Path to text file (default: tests/test_text.txt)')
    args = parser.parse_args()
    
    # Load text
    text = load_text_from_file(args.file)
    
    if text is None:
        print(f"\n⚠️  File not found: {args.file}")
        print(f"📄 Using default verse (Surah Al-Fath 48:29)\n")
        text = DEFAULT_VERSE
        source = "Surah Al-Fath 48:29 (Default)"
    else:
        source = args.file
    
    # Print main header
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "COMPREHENSIVE ARABIC TEXT ANALYSIS PIPELINE".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    
    print(f"\n📄 Source: {source}")
    print(f"📝 Text length: {len(text)} characters")
    print(f"🔤 Text preview: {text[:100]}...")
    
    # Run all tests
    boundaries = test_1_word_boundaries(text)
    test_2_root_extraction(boundaries)
    test_3_syllabification(boundaries)
    test_4_classification(boundaries)
    test_5_patterns()
    test_6_irab(boundaries)
    test_7_statistics(boundaries)
    
    # Final summary
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "✓✓✓ ANALYSIS COMPLETED SUCCESSFULLY ✓✓✓".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝\n")


if __name__ == "__main__":
    main()
