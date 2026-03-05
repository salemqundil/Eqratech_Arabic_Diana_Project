# FVAFK Framework Tutorial

**Version:** 1.0  
**Last Updated:** 2026-02-03

## Table of Contents
1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Tutorial 1: Basic Text Processing](#tutorial-1-basic-text-processing)
4. [Tutorial 2: Phonological Gate Processing](#tutorial-2-phonological-gate-processing)
5. [Tutorial 3: Morphological Analysis](#tutorial-3-morphological-analysis)
6. [Tutorial 4: Complete Pipeline](#tutorial-4-complete-pipeline)
7. [Tutorial 5: Working with Weak Roots](#tutorial-5-working-with-weak-roots)
8. [Tutorial 6: Batch Processing](#tutorial-6-batch-processing)
9. [Common Patterns & Recipes](#common-patterns--recipes)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

This tutorial walks you through using the FVAFK (Formal Verification of Arabic Fully-Optimized Knowledge) framework for Arabic text processing. You'll learn how to:

- Normalize and encode Arabic text
- Apply phonological rules through gates
- Extract roots and match morphological patterns
- Build complete morphological analyses

### Prerequisites

- Python 3.8 or higher
- Basic understanding of Arabic morphology (helpful but not required)
- Familiarity with Python programming

### Installation

```bash
# Clone the repository
git clone https://github.com/sonaiso/Eqratech_Hussein_Hiyassat_Project.git
cd Eqratech_Hussein_Hiyassat_Project

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For running tests
```

---

## Quick Start

### 5-Minute Example

```python
# Add src to Python path
import sys
sys.path.insert(0, 'src')

from fvafk.orthography_adapter import OrthographyAdapter
from fvafk.c1.encoder import Encoder
from fvafk.c2b.root_extractor import RootExtractor
from fvafk.c2b.pattern_matcher import PatternMatcher

# Input: "كَاتِبٌ" (kātibun - "a writer")
text = "كَاتِبٌ"

# Phase 1: Normalize and encode
adapter = OrthographyAdapter()
normalized = adapter.normalize(text)
print(f"Normalized: {normalized}")  # "كاتب"

# Phase 3: Extract root and pattern
extractor = RootExtractor()
root = extractor.extract(normalized)
print(f"Root: {'-'.join(root.letters)}")  # "ك-ت-ب"

matcher = PatternMatcher()
pattern = matcher.match(normalized, root)
print(f"Pattern: {pattern.name}")  # "فَاعِل"
print(f"Type: {pattern.pattern_type}")  # "ACTIVE_PARTICIPLE"
```

**Output:**
```
Normalized: كاتب
Root: ك-ت-ب
Pattern: فَاعِل
Type: ACTIVE_PARTICIPLE
```

---

## Tutorial 1: Basic Text Processing

### Goal
Learn to normalize Arabic text and convert it into segments.

### Step 1: Import Modules

```python
import sys
sys.path.insert(0, 'src')

from fvafk.orthography_adapter import OrthographyAdapter
from fvafk.c1.encoder import Encoder
```

### Step 2: Normalize Text

```python
# Create adapter
adapter = OrthographyAdapter()

# Test various inputs
texts = [
    "أَكَلَ",      # Hamza on alif
    "مُؤْمِن",     # Hamza on waw
    "مَسْئُول",    # Hamza on yaa
    "مُوسَى",      # Alif maqsura
]

for text in texts:
    normalized = adapter.normalize(text)
    print(f"{text:12} → {normalized}")
```

**Output:**
```
أَكَلَ       → اكل
مُؤْمِن      → مامن
مَسْئُول     → مسيول
مُوسَى       → موسي
```

### Step 3: Encode to Segments

```python
encoder = Encoder()

# Encode text with diacritics
text = "كَاتِبٌ"
segments = encoder.encode(text)
print(f"Text: {text}")
print(f"Segments: {segments}")
print(f"Count: {len(segments)} segments")
```

**Output:**
```
Text: كَاتِبٌ
Segments: ['ك', 'َ', 'ا', 'ت', 'ِ', 'ب', 'ٌ']
Count: 7 segments
```

### Understanding Segments

Each segment is:
- **Consonant**: 'ك', 'ت', 'ب'
- **Short vowel**: 'َ' (fatha), 'ِ' (kasra), 'ُ' (damma)
- **Long vowel**: 'ا', 'و', 'ي' (when functioning as vowels)
- **Diacritic**: 'ْ' (sukun), 'ّ' (shadda), 'ٌ' (tanwin)

---

## Tutorial 2: Phonological Gate Processing

### Goal
Apply Tajweed-based phonological rules to segment sequences.

### Step 1: Import Gates

```python
from fvafk.c2a.gate_framework import GateOrchestrator
from fvafk.c2a.gates import (
    GateSukun, GateShadda, GateHamza, GateWaqf,
    GateIdgham, GateMadd, GateDeletion, GateEpenthesis,
    GateAssimilation, GateTanwin
)
```

### Step 2: Create Orchestrator

```python
# Create all gates
gates = [
    GateSukun(),
    GateShadda(),
    GateHamza(),
    GateWaqf(),
    GateIdgham(),
    GateMadd(),
    GateDeletion(),
    GateEpenthesis(),
    GateAssimilation(),
    GateTanwin()
]

orchestrator = GateOrchestrator(gates)
```

### Step 3: Process Segments

#### Example 1: Double Sukun Repair

```python
# Input with double sukun (violation)
segments = ['ك', 'ْ', 'ت', 'ْ', 'ب']

output, results = orchestrator.run(segments)

print("Input:", segments)
print("Output:", output)
print("\nGate Results:")
for i, result in enumerate(results):
    gate_name = gates[i].gate_id
    print(f"{gate_name:15} {result.status.name:10} {result.reason}")
```

**Output:**
```
Input: ['ك', 'ْ', 'ت', 'ْ', 'ب']
Output: ['ك', 'َ', 'ت', 'ْ', 'ب']

Gate Results:
sukun           REPAIR     Double sukun repaired at position 1
shadda          ACCEPT     No shadda found
hamza           ACCEPT     No hamza violations
...
```

#### Example 2: Tanwin Expansion

```python
# Input with tanwin (dammatan ٌ)
segments = ['ك', 'ت', 'ا', 'ب', 'ٌ']

output, results = orchestrator.run(segments)

print("Input:", segments)
print("Output:", output)

# Find tanwin gate result
tanwin_result = results[9]  # GateTanwin is 10th gate (index 9)
print(f"\nTanwin gate: {tanwin_result.status.name}")
print(f"Reason: {tanwin_result.reason}")
print(f"Changes: {tanwin_result.deltas}")
```

**Output:**
```
Input: ['ك', 'ت', 'ا', 'ب', 'ٌ']
Output: ['ك', 'ت', 'ا', 'ب', 'ُ', 'ن']

Tanwin gate: REPAIR
Reason: Dammatan expanded to damma + noon
Changes: ['ٌ → ُ + ن']
```

#### Example 3: Lam Assimilation

```python
# Input: "الشَّمْس" (ash-shams - "the sun")
segments = ['ا', 'ل', 'ش', 'ّ', 'م', 'ْ', 'س']

output, results = orchestrator.run(segments)

print("Input:", ''.join(segments))
print("Output:", ''.join(output))

# Find assimilation gate result
assim_result = results[8]  # GateAssimilation
print(f"\nAssimilation: {assim_result.status.name}")
print(f"Reason: {assim_result.reason}")
```

**Output:**
```
Input: الشّمْس
Output: اشّمْس

Assimilation: REPAIR
Reason: Lam assimilated to sun letter ش
```

### Step 4: Examine Individual Gates

```python
from fvafk.c2a.gates import GateSukun

# Test single gate
gate = GateSukun()
result = gate.apply(['م', 'ْ', 'ن', 'ْ', 'ذ'])

print(f"Status: {result.status.name}")
print(f"Input:  {['م', 'ْ', 'ن', 'ْ', 'ذ']}")
print(f"Output: {result.output}")
print(f"Reason: {result.reason}")
print(f"Deltas: {result.deltas}")
```

---

## Tutorial 3: Morphological Analysis

### Goal
Extract roots and match morphological patterns.

### Step 1: Root Extraction

```python
from fvafk.c2b.root_extractor import RootExtractor

extractor = RootExtractor()

# Example 1: Simple word
word1 = "كَاتِب"
root1 = extractor.extract(word1)
print(f"Word: {word1}")
print(f"Root: {'-'.join(root1.letters)}")
print(f"Type: {root1.root_type.name}")
print()

# Example 2: Word with affixes
word2 = "المُسْتَخْرَجُون"  # "the extractors"
root2 = extractor.extract(word2)
print(f"Word: {word2}")
print(f"Root: {'-'.join(root2.letters)}")
print(f"Prefixes removed: ال، مُ")
print(f"Suffixes removed: ُون")
```

**Output:**
```
Word: كَاتِب
Root: ك-ت-ب
Type: TRILATERAL

Word: المُسْتَخْرَجُون
Root: خ-ر-ج
Prefixes removed: ال، مُ
Suffixes removed: ُون
```

### Step 2: Pattern Matching

```python
from fvafk.c2b.pattern_matcher import PatternMatcher

matcher = PatternMatcher()

# Example 1: Active participle (فَاعِل)
word = "كَاتِب"
root = extractor.extract(word)
pattern = matcher.match(word, root)

print(f"Word: {word}")
print(f"Pattern: {pattern.name}")
print(f"Template: {pattern.template}")
print(f"Type: {pattern.pattern_type.name}")
print(f"Description: {pattern.description}")
print()

# Example 2: Verb Form II (فَعَّلَ)
word = "دَرَّسَ"  # "taught" (causative)
root = extractor.extract(word)
pattern = matcher.match(word, root)

print(f"Word: {word}")
print(f"Root: {'-'.join(root.letters)}")
print(f"Pattern: {pattern.name}")
print(f"Type: {pattern.pattern_type.name}")
```

**Output:**
```
Word: كَاتِب
Pattern: فَاعِل
Template: CvaCiC
Type: ACTIVE_PARTICIPLE
Description: Active participle pattern

Word: دَرَّسَ
Root: د-ر-س
Pattern: فَعَّلَ
Type: VERB_FORM_II
```

### Step 3: Complete Morpheme Assembly

```python
from fvafk.c2b.morpheme import Morpheme, Affix, AffixPosition

# Analyze word: "الكَاتِبُون" (the writers)
word = "الكَاتِبُون"

# Extract components
root = extractor.extract(word)
pattern = matcher.match("كَاتِب", root)

# Create affixes
affixes = [
    Affix(text='ال', position=AffixPosition.PREFIX, name='definite-article'),
    Affix(text='ُون', position=AffixPosition.SUFFIX, name='masc-pl-nom')
]

# Assemble morpheme
morpheme = Morpheme(
    root=root,
    pattern=pattern,
    stem='كَاتِب',
    affixes=affixes,
    gloss='DEF-writer.MASC.PL.NOM'
)

# Display analysis
print(f"Word: {word}")
print(f"Root: {'-'.join(morpheme.root.letters)}")
print(f"Pattern: {morpheme.pattern.name}")
print(f"Stem: {morpheme.stem}")
print(f"Affixes:")
for affix in morpheme.affixes:
    print(f"  {affix.position.name}: {affix.text} ({affix.name})")
print(f"Gloss: {morpheme.gloss}")
```

**Output:**
```
Word: الكَاتِبُون
Root: ك-ت-ب
Pattern: فَاعِل
Stem: كَاتِب
Affixes:
  PREFIX: ال (definite-article)
  SUFFIX: ُون (masc-pl-nom)
Gloss: DEF-writer.MASC.PL.NOM
```

---

## Tutorial 4: Complete Pipeline

### Goal
Process text through all three phases (C1 → C2a → C2b).

### Complete Example

```python
import sys
sys.path.insert(0, 'src')

from fvafk.orthography_adapter import OrthographyAdapter
from fvafk.c1.encoder import Encoder
from fvafk.c2a.gate_framework import GateOrchestrator
from fvafk.c2a.gates import *
from fvafk.c2b.root_extractor import RootExtractor
from fvafk.c2b.pattern_matcher import PatternMatcher
from fvafk.c2b.morpheme import Morpheme

def analyze_word(text: str):
    """Complete morphological analysis pipeline."""
    
    print(f"{'='*60}")
    print(f"Analyzing: {text}")
    print(f"{'='*60}\n")
    
    # Phase 1: Text Encoding (C1)
    print("PHASE 1: Text Encoding")
    print("-" * 40)
    adapter = OrthographyAdapter()
    normalized = adapter.normalize(text)
    print(f"Input:      {text}")
    print(f"Normalized: {normalized}")
    
    encoder = Encoder()
    segments = encoder.encode(text)
    print(f"Segments:   {segments}")
    print(f"Count:      {len(segments)} segments\n")
    
    # Phase 2: Phonological Processing (C2a)
    print("PHASE 2: Phonological Processing")
    print("-" * 40)
    gates = [
        GateSukun(), GateShadda(), GateHamza(), GateWaqf(),
        GateIdgham(), GateMadd(), GateDeletion(), GateEpenthesis(),
        GateAssimilation(), GateTanwin()
    ]
    orchestrator = GateOrchestrator(gates)
    output_segments, gate_results = orchestrator.run(segments)
    
    # Show repairs
    for i, result in enumerate(gate_results):
        if result.status.name == 'REPAIR':
            print(f"{gates[i].gate_id:15} {result.status.name:10} {result.reason}")
    
    print(f"Output:     {output_segments}\n")
    
    # Phase 3: Morphological Analysis (C2b)
    print("PHASE 3: Morphological Analysis")
    print("-" * 40)
    extractor = RootExtractor()
    root = extractor.extract(normalized)
    
    if root:
        print(f"Root:       {'-'.join(root.letters)}")
        print(f"Root Type:  {root.root_type.name}")
        
        if root.weak_positions:
            print(f"Weak:       Positions {root.weak_positions}")
        
        matcher = PatternMatcher()
        pattern = matcher.match(normalized, root)
        
        if pattern:
            print(f"Pattern:    {pattern.name}")
            print(f"Template:   {pattern.template}")
            print(f"Type:       {pattern.pattern_type.name}")
            print(f"Description: {pattern.description}")
        else:
            print("Pattern:    No match found")
    else:
        print("Root:       Extraction failed")
    
    print()

# Test with multiple words
words = [
    "كَاتِبٌ",        # Simple: "a writer"
    "المُؤْمِنُون",   # Complex: "the believers"
    "اسْتَخْرَجَ",    # Verb Form X: "extracted"
]

for word in words:
    analyze_word(word)
```

---

## Tutorial 5: Working with Weak Roots

### Understanding Weak Roots

Weak roots contain و، ي، or ء (hamza) which undergo changes in different forms.

### Types of Weak Roots

```python
from fvafk.c2b.root_extractor import RootExtractor

extractor = RootExtractor()

# Type 1: Initial weak (مثال) - و at start
root1 = extractor.extract("وَعَدَ")  # "promised"
print(f"Root: {'-'.join(root1.letters)}")  # و-ع-د
print(f"Weak positions: {root1.weak_positions}")  # [0]

# Type 2: Medial weak (أجوف) - و/ي in middle
root2 = extractor.extract("قَالَ")  # "said" (from ق-و-ل)
print(f"Root: {'-'.join(root2.letters)}")  # ق-و-ل
print(f"Weak positions: {root2.weak_positions}")  # [1]

# Type 3: Final weak (ناقص) - و/ي at end
root3 = extractor.extract("رَمَى")  # "threw" (from ر-م-ي)
print(f"Root: {'-'.join(root3.letters)}")  # ر-م-ي
print(f"Weak positions: {root3.weak_positions}")  # [2]

# Type 4: Doubly weak (لفيف) - two weak letters
root4 = extractor.extract("وَقَى")  # "protected" (من و-ق-ي)
print(f"Root: {'-'.join(root4.letters)}")  # و-ق-ي
print(f"Weak positions: {root4.weak_positions}")  # [0, 2]
```

### Handling Vowel Changes

```python
# Medial weak: و/ي becomes long vowel in perfect tense
words = [
    ("قَالَ", "ق-و-ل"),  # قال (said) - و becomes ا
    ("بَاعَ", "ب-ي-ع"),  # باع (sold) - ي becomes ا
    ("نَامَ", "ن-و-م"),  # نام (slept) - و becomes ا
]

for word, expected_root in words:
    root = extractor.extract(word)
    actual_root = '-'.join(root.letters)
    print(f"{word:8} → Root: {actual_root} (expected: {expected_root})")
```

---

## Tutorial 6: Batch Processing

### Processing Multiple Words

```python
def batch_analyze(words: list):
    """Analyze multiple words efficiently."""
    from fvafk.c2b.root_extractor import RootExtractor
    from fvafk.c2b.pattern_matcher import PatternMatcher
    
    extractor = RootExtractor()
    matcher = PatternMatcher()
    results = []
    
    for word in words:
        root = extractor.extract(word)
        if root:
            pattern = matcher.match(word, root)
            results.append({
                'word': word,
                'root': '-'.join(root.letters),
                'pattern': pattern.name if pattern else 'Unknown',
                'type': pattern.pattern_type.name if pattern else 'Unknown'
            })
        else:
            results.append({
                'word': word,
                'root': 'Failed',
                'pattern': 'N/A',
                'type': 'N/A'
            })
    
    return results

# Test batch processing
words = [
    "كَاتِب", "مَكْتُوب", "كِتَاب", "كُتُب",  # From ك-ت-ب
    "ذَاهِب", "مَذْهَب", "ذَهَاب",           # From ذ-ه-ب
    "عَالِم", "مَعْلُوم", "عِلْم",           # From ع-ل-م
]

results = batch_analyze(words)

# Display as table
print(f"{'Word':15} {'Root':10} {'Pattern':12} {'Type':25}")
print("-" * 65)
for r in results:
    print(f"{r['word']:15} {r['root']:10} {r['pattern']:12} {r['type']:25}")
```

**Output:**
```
Word            Root       Pattern      Type
-----------------------------------------------------------------
كَاتِب          ك-ت-ب      فَاعِل       ACTIVE_PARTICIPLE
مَكْتُوب        ك-ت-ب      مَفْعُول     PASSIVE_PARTICIPLE
كِتَاب          ك-ت-ب      فِعَال       NOUN_SINGULAR
كُتُب           ك-ت-ب      فُعُل        BROKEN_PLURAL
...
```

---

## Common Patterns & Recipes

### Recipe 1: Validate Arabic Text

```python
def is_valid_arabic(text: str) -> bool:
    """Check if text is valid Arabic."""
    from fvafk.c1.segment_inventory import is_consonant, is_vowel
    
    for char in text:
        if char.isspace():
            continue
        if not (is_consonant(char) or is_vowel(char) or char in 'ًٌٍّْ'):
            return False
    return True

print(is_valid_arabic("كَاتِب"))  # True
print(is_valid_arabic("hello"))   # False
```

### Recipe 2: Remove All Diacritics

```python
def strip_diacritics(text: str) -> str:
    """Remove all diacritical marks."""
    from fvafk.orthography_adapter import OrthographyAdapter
    adapter = OrthographyAdapter()
    return adapter.remove_diacritics(text)

print(strip_diacritics("كَاتِبٌ"))  # "كاتب"
```

### Recipe 3: Get All Patterns for Root

```python
def find_all_forms(root_str: str):
    """Find all possible forms of a root."""
    from fvafk.c2b.pattern_matcher import PatternMatcher
    from fvafk.c2b.morpheme import Root, RootType
    
    # Create root object
    letters = tuple(root_str.split('-'))
    root = Root(letters=letters, root_type=RootType.TRILATERAL)
    
    # Get all patterns
    matcher = PatternMatcher()
    patterns = matcher.get_all_patterns()
    
    # Try matching each pattern
    print(f"Root: {root_str}")
    print(f"{'Pattern':15} {'Type':25} {'Example':15}")
    print("-" * 60)
    
    for template in patterns[:10]:  # Show first 10
        # Generate hypothetical form (simplified)
        print(f"{template.name:15} {template.pattern_type.name:25} {template.stem:15}")

find_all_forms("ك-ت-ب")
```

### Recipe 4: Compare Two Words

```python
def compare_words(word1: str, word2: str):
    """Compare morphological structure of two words."""
    from fvafk.c2b.root_extractor import RootExtractor
    from fvafk.c2b.pattern_matcher import PatternMatcher
    
    extractor = RootExtractor()
    matcher = PatternMatcher()
    
    # Analyze both words
    root1 = extractor.extract(word1)
    root2 = extractor.extract(word2)
    
    pattern1 = matcher.match(word1, root1) if root1 else None
    pattern2 = matcher.match(word2, root2) if root2 else None
    
    # Compare
    print(f"Word 1: {word1}")
    print(f"  Root: {'-'.join(root1.letters) if root1 else 'N/A'}")
    print(f"  Pattern: {pattern1.name if pattern1 else 'N/A'}")
    print()
    print(f"Word 2: {word2}")
    print(f"  Root: {'-'.join(root2.letters) if root2 else 'N/A'}")
    print(f"  Pattern: {pattern2.name if pattern2 else 'N/A'}")
    print()
    
    if root1 and root2:
        if root1.letters == root2.letters:
            print("✓ Same root")
        else:
            print("✗ Different roots")
        
        if pattern1 and pattern2:
            if pattern1.name == pattern2.name:
                print("✓ Same pattern")
            else:
                print("✗ Different patterns")

compare_words("كَاتِب", "مَكْتُوب")
```

---

## Troubleshooting

### Problem: Root Extraction Fails

**Symptom:** `extractor.extract()` returns `None`

**Solutions:**
```python
# 1. Check if word is too short (< 3 letters)
word = "من"  # Too short
root = extractor.extract(word)
if not root:
    print("Word too short for root extraction")

# 2. Provide known roots dictionary
known_roots = {'ك-ت-ب', 'ذ-ه-ب', 'ع-ل-م'}
extractor = RootExtractor(known_roots=known_roots)
root = extractor.extract("كَاتِب")

# 3. Normalize text first
from fvafk.orthography_adapter import OrthographyAdapter
adapter = OrthographyAdapter()
normalized = adapter.normalize("أَكَلَ")
root = extractor.extract(normalized)
```

### Problem: Pattern Match Not Found

**Symptom:** `matcher.match()` returns `None`

**Solutions:**
```python
# 1. Lower threshold
matcher = PatternMatcher(threshold=0.5)  # Default is 0.7

# 2. Check available patterns
patterns = matcher.get_all_patterns()
print(f"Available patterns: {len(patterns)}")

# 3. Verify root extraction worked
root = extractor.extract(word)
if not root:
    print("Root extraction failed first")
```

### Problem: Unicode Issues

**Symptom:** Text appears garbled

**Solutions:**
```python
# 1. Ensure UTF-8 encoding
text = "كَاتِب"
text_bytes = text.encode('utf-8')
text_decoded = text_bytes.decode('utf-8')

# 2. Normalize Unicode
import unicodedata
text = unicodedata.normalize('NFC', text)

# 3. Use OrthographyAdapter
from fvafk.orthography_adapter import OrthographyAdapter
adapter = OrthographyAdapter()
normalized = adapter.normalize(text)
```

---

## Next Steps

Now that you've completed the tutorials, you can:

1. **Read the detailed guides:**
   - [Architecture Overview](ARCHITECTURE.md)
   - [Phonological Gates Reference](PHONOLOGICAL_GATES.md)
   - [Morphology Guide](MORPHOLOGY_GUIDE.md)
   - [API Reference](API_REFERENCE.md)

2. **Explore the tests:**
   - Check `tests/` directory for more examples
   - Run: `PYTHONPATH=src pytest tests/ -v`

3. **Build your own application:**
   - Text analysis tools
   - Educational software
   - Morphological databases
   - Quranic analysis tools

4. **Contribute:**
   - Add new patterns
   - Improve gate logic
   - Extend documentation
   - Report issues

---

## Support

- **GitHub Issues**: https://github.com/sonaiso/Eqratech_Hussein_Hiyassat_Project/issues
- **Documentation**: `docs/` directory
- **Examples**: `tests/` directory

Happy coding! 🚀
