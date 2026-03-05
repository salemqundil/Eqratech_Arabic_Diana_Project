"""
Combined Arabic Text Analyzer
Comprehensive morphological, phonological, and fractal weight analysis

Usage:
  python3 tests/analyze_combined.py
  python3 tests/analyze_combined.py --file path/to/text.txt
  python3 tests/analyze_combined.py --json output.json
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import csv
import os
import json
import argparse
from collections import defaultdict
from typing import List, Dict, Any

from fvafk.c2b.word_boundary_detector import WordBoundaryDetectorPlanB
from fvafk.c2b.root_extractor import RootExtractor
from fvafk.c2b.pattern_catalog import PatternCatalog, create_default_catalog
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


def print_table_row(col1, col2, col3="", col4="", width1=20, width2=40, width3=15, width4=15):
    """Print formatted table row"""
    if col4:
        print(f"  │ {col1:<{width1}} │ {col2:<{width2}} │ {col3:>{width3}} │ {col4:>{width4}} │")
    else:
        print(f"  │ {col1:<{width1}} │ {col2:<{width2}} │ {col3:>{width3}} │")


def determine_weight_status(syllable_count: int) -> str:
    """Determine if word is weight candidate or underweight"""
    if syllable_count >= 3:
        return "WEIGHT_CANDIDATE"
    elif syllable_count == 2:
        return "UNDER_WEIGHT"
    else:
        return "MINIMAL"


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
    
    return successful


def test_3_syllabification_and_weight(boundaries):
    """Test 3: Syllabification + Fractal Weight Analysis"""
    print_header("TEST 3: SYLLABIFICATION & FRACTAL WEIGHT ANALYSIS", 80)
    
    successful = []
    syllable_counts = defaultdict(int)
    syllable_types = defaultdict(int)
    weight_distribution = defaultdict(int)
    weight_words = []
    underweight_words = []
    
    for boundary in boundaries:
        try:
            result = syllabify(boundary.text)
            if result and result.syllables:
                successful.append((boundary.text, result))
                num_syl = len(result.syllables)
                syllable_counts[num_syl] += 1
                
                # Weight analysis
                weight_status = determine_weight_status(num_syl)
                weight_distribution[weight_status] += 1
                
                if weight_status == "WEIGHT_CANDIDATE":
                    weight_words.append((boundary.text, num_syl, result.syllables))
                elif weight_status == "UNDER_WEIGHT":
                    underweight_words.append((boundary.text, num_syl, result.syllables))
                
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
    
    # FRACTAL WEIGHT ANALYSIS
    print_section("⚖️  FRACTAL WEIGHT ANALYSIS")
    
    total = len(boundaries)
    weight_count = weight_distribution.get("WEIGHT_CANDIDATE", 0)
    under_count = weight_distribution.get("UNDER_WEIGHT", 0)
    minimal_count = weight_distribution.get("MINIMAL", 0)
    
    print_result("Weight-bearing words (≥3 syllables)", f"{weight_count} ({weight_count/total*100:.1f}%)")
    print_result("Underweight words (2 syllables)", f"{under_count} ({under_count/total*100:.1f}%)")
    print_result("Minimal words (0-1 syllables)", f"{minimal_count} ({minimal_count/total*100:.1f}%)")
    
    print_section("Weight Distribution Bar Chart")
    print(f"    ✅ Weight-bearing  │ {weight_count:3d} words │ {'■' * int(weight_count/total*50)}")
    print(f"    ⚪ Underweight     │ {under_count:3d} words │ {'░' * int(under_count/total*50)}")
    print(f"    ⚫ Minimal         │ {minimal_count:3d} words │ {'▪' * int(minimal_count/total*50)}")
    
    print_section("Sample Syllabifications with Weight Status")
    for word, result in successful[:10]:
        syls = [str(s) for s in result.syllables]
        num_syl = len(result.syllables)
        weight = determine_weight_status(num_syl)
        emoji = "✅" if weight == "WEIGHT_CANDIDATE" else "⚪" if weight == "UNDER_WEIGHT" else "⚫"
        print(f"  {emoji} {word:20} [{weight:18}] → {' · '.join(syls)}")
    
    if underweight_words:
        print_section(f"⚪ Underweight Words ({len(underweight_words)} total)")
        underweight_list = [w[0] for w in underweight_words[:20]]
        print(f"    {' | '.join(underweight_list)}")
        if len(underweight_words) > 20:
            print(f"    ... and {len(underweight_words) - 20} more")
    
    return successful, weight_words, underweight_words


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
    
    return classifications


def test_5_patterns():
    """Test 5: Pattern Catalog"""
    print_header("TEST 5: MORPHOLOGICAL PATTERN CATALOG", 80)
    
    try:
        catalog = create_default_catalog()
        
        print_section("Pattern Categories")
        
        stats = catalog.get_statistics()
        total = sum(stats.values())
        
        for category, count in stats.items():
            category_name = str(category).split('.')[-1].replace('_', ' ').title()
            print_result(category_name, f"{count} patterns")
        
        print_result("TOTAL PATTERNS", f"{total} patterns", indent=4)
        
        print_section("Sample Verb Forms")
        verb_forms = catalog.get_verb_forms()[:5]
        for pattern in verb_forms:
            template = pattern.template.pattern if hasattr(pattern.template, 'pattern') else str(pattern.template)
            print(f"    {pattern.category.name:25} {template:12}")
        
        print_section("Sample Noun Patterns")
        noun_patterns = catalog.get_noun_patterns()[:5]
        for pattern in noun_patterns:
            template = pattern.template.pattern if hasattr(pattern.template, 'pattern') else str(pattern.template)
            print(f"    {pattern.category.name:25} {template:12}")
    
    except Exception as e:
        print(f"\n  ⚠️  Pattern catalog error: {e}")


def test_6_comprehensive_statistics(boundaries, weight_words, underweight_words):
    """Test 6: Comprehensive Statistics"""
    print_header("TEST 6: COMPREHENSIVE TEXT STATISTICS", 80)
    
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
    
    print_section("Fractal Weight Summary")
    print_result("Weight-bearing words", f"{len(weight_words)} words ({len(weight_words)/len(boundaries)*100:.1f}%)")
    print_result("Underweight words", f"{len(underweight_words)} words ({len(underweight_words)/len(boundaries)*100:.1f}%)")
    
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


def export_json(boundaries, roots, syllables, classifications, weight_words, underweight_words, output_file):
    """Export all analysis to JSON"""
    data = {
        "total_words": len(boundaries),
        "analysis": []
    }
    
    for i, boundary in enumerate(boundaries):
        word_data = {
            "word": boundary.text,
            "has_prefix": boundary.has_prefix,
            "has_suffix": boundary.has_suffix,
            "confidence": boundary.confidence,
            "syllable_count": boundary.syllable_count
        }
        
        # Add root if available
        root_match = next((r for r in roots if r[0] == boundary.text), None)
        if root_match:
            word_data["root"] = ''.join(root_match[1].letters)
            word_data["root_type"] = "trilateral" if root_match[1].trilateral else "quadrilateral"
        
        # Add syllables
        syl_match = next((s for s in syllables if s[0] == boundary.text), None)
        if syl_match:
            word_data["syllables"] = [str(syl) for syl in syl_match[1].syllables]
            word_data["weight_status"] = determine_weight_status(len(syl_match[1].syllables))
        
        data["analysis"].append(word_data)
    
    data["statistics"] = {
        "total_words": len(boundaries),
        "unique_words": len(set(b.text for b in boundaries)),
        "weight_bearing": len(weight_words),
        "underweight": len(underweight_words),
        "avg_confidence": sum(b.confidence for b in boundaries) / len(boundaries)
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ JSON exported to: {output_file}")


def main():
    """Run all tests"""
    parser = argparse.ArgumentParser(description='Combined Arabic text analysis')
    parser.add_argument('--file', '-f', type=str, default='tests/test_text.txt',
                       help='Path to text file (default: tests/test_text.txt)')
    parser.add_argument('--json', '-j', type=str, help='Export results to JSON file')
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
    print("║" + "COMBINED ARABIC TEXT ANALYSIS PIPELINE".center(78) + "║")
    print("║" + "Morphology + Syllabification + Fractal Weight".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    
    print(f"\n📄 Source: {source}")
    print(f"📝 Text length: {len(text)} characters")
    print(f"🔤 Text preview: {text[:100]}...")
    
    # Run all tests
    boundaries = test_1_word_boundaries(text)
    roots = test_2_root_extraction(boundaries)
    syllables, weight_words, underweight_words = test_3_syllabification_and_weight(boundaries)
    classifications = test_4_classification(boundaries)
    test_5_patterns()
    test_6_comprehensive_statistics(boundaries, weight_words, underweight_words)
    
    # Export JSON if requested
    if args.json:
        export_json(boundaries, roots, syllables, classifications, weight_words, underweight_words, args.json)
    
    # Final summary
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "✓✓✓ COMBINED ANALYSIS COMPLETED SUCCESSFULLY ✓✓✓".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝\n")


if __name__ == "__main__":
    main()
