# Morphology Guide

**Version:** 1.0  
**Last Updated:** 2026-02-03

## Table of Contents
1. [Overview](#overview)
2. [Root Extraction](#root-extraction)
3. [Pattern Matching](#pattern-matching)
4. [Morpheme Assembly](#morpheme-assembly)
5. [Syllabification](#syllabification)
6. [Arabic Morphological Patterns](#arabic-morphological-patterns)
7. [Implementation Examples](#implementation-examples)

---

## Overview

Arabic morphology is **non-concatenative**: words are formed by interleaving consonantal roots with vocalic patterns, rather than simply concatenating affixes. The FVAFK framework implements computational morphology based on this root-and-pattern system.

### Key Concepts

**Root (جذر):**  
A sequence of 3-4 consonants carrying core meaning.  
Example: **ك-ت-ب** (k-t-b) → writing, books, office, etc.

**Pattern (وزن):**  
A template with slots for root consonants and specified vowels.  
Example: **فَاعِل** (fā'il) = active participle pattern

**Stem (جذع):**  
The result of applying pattern to root.  
Example: ك-ت-ب + فَاعِل = **كَاتِب** (kātib, "writer")

**Affixes (زوائد):**  
Prefixes, suffixes, or infixes added to stem.  
Example: كَاتِب + ٌ (tanwin) = **كَاتِبٌ** (kātibun, "a writer")

---

## Root Extraction

**File:** `src/fvafk/c2b/root_extractor.py`

### Algorithm Overview

```
Input: Arabic word (with or without diacritics)
  ↓
1. Normalize: Remove diacritics, normalize hamza carriers
  ↓
2. Strip affixes: Remove known prefixes and suffixes
  ↓
3. Extract consonants: Filter out pattern vowels (ا، و، ي)
  ↓
4. Validate: Check length (3-4) and optionally against known roots
  ↓
Output: Root(letters, root_type, weak_positions, has_hamza)
```

### RootExtractor Class

```python
from fvafk.c2b.root_extractor import RootExtractor

# Initialize with optional known roots dictionary
extractor = RootExtractor(known_roots={'ك-ت-ب', 'ذ-ه-ب', 'ع-ل-م'})

# Extract root
root = extractor.extract("كَاتِبٌ")
# Output: Root(letters=('ك', 'ت', 'ب'), root_type=TRILATERAL)

root = extractor.extract("مُسْتَخْرَج")
# Output: Root(letters=('خ', 'ر', 'ج'), root_type=TRILATERAL)
# (strips prefix 'مُسْتَ', suffix 'َ')
```

### Normalization

**Hamza Normalization:**
```python
def normalize_hamza_for_roots(text: str) -> str:
    """
    Normalize hamza carriers to base letters.
    
    أ، إ، آ → ا
    ؤ → و  
    ئ → ي
    """
    text = text.replace('أ', 'ا')
    text = text.replace('إ', 'ا')
    text = text.replace('آ', 'ا')
    text = text.replace('ؤ', 'و')
    text = text.replace('ئ', 'ي')
    return text
```

**Diacritic Removal:**
```python
DIACRITICS = "َُِْٰٓٔٱًٌٍّ"

def remove_diacritics(text: str) -> str:
    return ''.join(c for c in text if c not in DIACRITICS)
```

**Shadda Expansion:**
```python
# "مُدَّرِس" → "مُدَدَرِس" (ّ on د doubles the consonant)
def expand_shadda(text: str) -> str:
    result = []
    for i, char in enumerate(text):
        if char == 'ّ' and result:
            result.append(result[-1])  # Double previous consonant
        elif char != 'ّ':
            result.append(char)
    return ''.join(result)
```

### Affix Stripping

**Common Prefixes:**
```python
PREFIXES = [
    'است',      # استفعل (Form X)
    'ال',       # Definite article
    'وال', 'فال', 'بال', 'كال', 'لل',  # Article with conjunctions
    'س', 'سي', 'سو',   # Future marker
    'ف', 'و', 'ب', 'ك', 'ل',  # Conjunctions/prepositions
    'م', 'ت', 'ي', 'ن', 'أ',  # Present tense prefixes
]
```

**Common Suffixes:**
```python
SUFFIXES = [
    'ون', 'ين', 'ات', 'ان',  # Plural markers
    'تم', 'تن', 'وا',         # Verb suffixes
    'ها', 'هم', 'هما', 'هن',  # Pronouns (3rd person)
    'كم', 'كن',               # Pronouns (2nd person)
    'ني', 'نا', 'ك', 'ه',    # Pronouns (singular)
    'ة', 'ن'                 # Taa marbuta, nunation
]
```

**Stripping Logic:**
```python
def _strip_affixes(self, word: str) -> str:
    text = word
    
    # Remove complex prefixes first (longest match)
    for prefix in sorted(self.PREFIXES, key=len, reverse=True):
        if text.startswith(prefix) and len(text) - len(prefix) >= 3:
            text = text[len(prefix):]
            break
    
    # Remove suffixes (can be multiple)
    for _ in range(2):  # Maximum 2 suffixes
        for suffix in sorted(self.SUFFIXES, key=len, reverse=True):
            if text.endswith(suffix) and len(text) - len(suffix) >= 3:
                text = text[:-len(suffix)]
                break
    
    return text
```

### Consonant Extraction

**Pattern Letters vs. Root Consonants:**
```python
PATTERN_LETTERS = {'ا', 'و', 'ي'}  # Long vowels used in patterns

def _extract_consonants(self, word: str) -> List[str]:
    letters = [ch for ch in word if self._is_arabic_letter(ch)]
    consonants = []
    
    for i, letter in enumerate(letters):
        # Skip pattern letter if between two consonants
        if letter in PATTERN_LETTERS and 0 < i < len(letters) - 1:
            prev_is_consonant = letters[i-1] not in PATTERN_LETTERS
            next_is_consonant = letters[i+1] not in PATTERN_LETTERS
            if prev_is_consonant and next_is_consonant:
                continue  # This is a pattern vowel, not root consonant
        consonants.append(letter)
    
    return consonants
```

**Example:**
```
Word: "كَاتِب"
Letters: ['ك', 'ا', 'ت', 'ب']
Analysis:
  - 'ك': consonant → keep
  - 'ا': between 'ك' and 'ت' (both consonants) → skip (pattern vowel)
  - 'ت': consonant → keep
  - 'ب': consonant → keep
Result: ['ك', 'ت', 'ب']
```

### Root Types

```python
from enum import Enum, auto

class RootType(Enum):
    TRILATERAL = auto()      # 3 consonants (most common)
    QUADRILATERAL = auto()   # 4 consonants (rare)
```

**Examples:**
- **Trilateral:** ك-ت-ب، ذ-ه-ب، ع-ل-م، ق-ر-أ
- **Quadrilateral:** ز-ل-ز-ل، و-س-و-س، ت-ر-ج-م، د-ح-ر-ج

### Weak Roots

Roots containing weak letters (و، ي، ء) undergo special morphological changes:

```python
@dataclass
class Root:
    letters: Tuple[str, ...]
    root_type: RootType
    weak_positions: List[int] = field(default_factory=list)
    has_hamza: bool = False

# Example weak roots
root1 = Root(letters=('ق', 'و', 'ل'), weak_positions=[1])  # و in middle
root2 = Root(letters=('و', 'ج', 'د'), weak_positions=[0])  # و at start
root3 = Root(letters=('ر', 'م', 'ي'), weak_positions=[2])  # ي at end
```

**Weak Letter Behavior:**
- **Initial weak (مثال):** و → often dropped (وعد → عدة)
- **Medial weak (أجوف):** و/ي → often becomes long vowel (قال from ق-و-ل)
- **Final weak (ناقص):** ي → often becomes ى (رمى from ر-م-ي)

---

## Pattern Matching

**File:** `src/fvafk/c2b/pattern_matcher.py`

### Pattern Templates

Arabic patterns use **فعل** (f-'-l) as the canonical root. Each pattern specifies:
- Consonant positions (where root letters go)
- Vowel positions (short and long vowels)
- Additional affixes

```python
from dataclasses import dataclass
from enum import Enum, auto

class PatternType(Enum):
    VERB_FORM_I = auto()
    VERB_FORM_II = auto()
    # ... Forms III-X
    ACTIVE_PARTICIPLE = auto()
    PASSIVE_PARTICIPLE = auto()
    NOUN_SINGULAR = auto()
    NOUN_PLURAL = auto()
    BROKEN_PLURAL = auto()

@dataclass
class PatternTemplate:
    name: str                # Arabic pattern name (e.g., 'فَاعِل')
    template: str            # CV notation (e.g., 'CvvCvC')
    pattern_type: PatternType
    stem: str               # Example with canonical root (e.g., 'فاعل')
    description: str
    weight: str             # Morphological weight
```

### Common Patterns

#### Verb Forms (أوزان الأفعال)

| Form | Pattern | Template | Example (ك-ت-ب) | Meaning |
|------|---------|----------|-----------------|---------|
| I | فَعَلَ | CaCaCa | كَتَبَ | wrote (basic) |
| II | فَعَّلَ | CaCCaCa | كَتَّبَ | caused to write |
| III | فَاعَلَ | CvaCaCa | كَاتَبَ | corresponded |
| IV | أَفْعَلَ | 'aCCaCa | أَكْتَبَ | dictated |
| V | تَفَعَّلَ | taCaCCaCa | تَكَتَّبَ | enrolled |
| VI | تَفَاعَلَ | taCvaCaCa | تَكَاتَبَ | corresponded (reciprocal) |
| VII | انْفَعَلَ | inCaCaCa | انْكَتَبَ | subscribed |
| VIII | افْتَعَلَ | iCtaCaCa | اكْتَتَبَ | subscribed |
| IX | افْعَلَّ | iCCaCCa | - | (colors/defects only) |
| X | اسْتَفْعَلَ | istaCCaCa | اسْتَكْتَبَ | asked to write |

#### Participles (اسم الفاعل والمفعول)

| Type | Pattern | Template | Example (ك-ت-ب) | Meaning |
|------|---------|----------|-----------------|---------|
| Active | فَاعِل | CvaCiC | كَاتِب | writer (one who writes) |
| Passive | مَفْعُول | maCCuuC | مَكْتُوب | written |

#### Noun Patterns (أوزان الأسماء)

| Pattern | Template | Example | Meaning |
|---------|----------|---------|---------|
| فِعْل | CiCC | عِلْم | knowledge |
| فَعْل | CaCC | عَقْل | intellect |
| فُعْل | CuCC | حُكْم | judgment |
| فَعَال | CaCvvC | كِتَاب | book |
| فُعُول | CuCuuC | بُيُوت | houses |
| فَوَاعِل | CawvaCiC | كَوَاتِب | (female) writers |

### PatternMatcher Class

```python
from fvafk.c2b.pattern_matcher import PatternMatcher
from fvafk.c2b.morpheme import Root

# Initialize
matcher = PatternMatcher()

# Match word to pattern
root = Root(letters=('ك', 'ت', 'ب'), root_type=RootType.TRILATERAL)
pattern = matcher.match("كَاتِب", root)

print(pattern.name)          # 'فَاعِل'
print(pattern.pattern_type)  # PatternType.ACTIVE_PARTICIPLE
print(pattern.description)   # 'Active participle pattern'
```

### Matching Algorithm

```python
def match(self, word: str, root: Root) -> Optional[Pattern]:
    """
    Match word against known patterns.
    
    Algorithm:
    1. Normalize word (remove diacritics)
    2. For each pattern template:
       a. Align root consonants to pattern slots
       b. Check if vowels match pattern
       c. Compute confidence score
    3. Return best match above threshold
    """
    normalized = self._normalize(word)
    best_match = None
    best_score = 0.0
    
    for template in self.patterns:
        score = self._compute_match_score(normalized, root, template)
        if score > best_score:
            best_score = score
            best_match = template
    
    if best_score >= self.threshold:
        return Pattern(
            name=best_match.name,
            template=best_match.template,
            pattern_type=best_match.pattern_type,
            stem=word,
            description=best_match.description,
            weight=best_match.weight
        )
    return None
```

### Consonant-Vowel Notation

Patterns use **CV notation** to describe phonological structure:
- **C**: Consonant (root letter)
- **v**: Short vowel (َ fatha, ِ kasra, ُ damma)
- **vv**: Long vowel (ا، و، ي)
- **'**: Glottal stop (hamza)
- **t, m, n, s**: Specific consonants (not from root)

**Examples:**
```
فَاعِل   → CvaCiC    (C1-a-a-C2-i-C3)
مَفْعُول → maCCuuC   (m-C1-C2-uu-C3)
اسْتَفْعَلَ → istaCCaCa (i-s-t-C1-C2-a-C3-a)
```

---

## Morpheme Assembly

**File:** `src/fvafk/c2b/morpheme.py`

### Data Structures

```python
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum, auto

@dataclass
class Root:
    letters: Tuple[str, ...]
    root_type: RootType
    weak_positions: List[int] = field(default_factory=list)
    has_hamza: bool = False

@dataclass
class Pattern:
    name: str
    template: str
    pattern_type: PatternType
    stem: str
    description: str
    weight: str

class AffixPosition(Enum):
    PREFIX = auto()
    SUFFIX = auto()
    INFIX = auto()

@dataclass
class Affix:
    text: str
    position: AffixPosition
    name: str  # Linguistic name (e.g., 'tanwin-damma', 'definite-article')

@dataclass
class Morpheme:
    root: Root
    pattern: Pattern
    stem: str
    affixes: List[Affix] = field(default_factory=list)
    gloss: str = ""  # Linguistic gloss
```

### Complete Example

```python
from fvafk.c2b.morpheme import Root, Pattern, Morpheme, Affix, AffixPosition
from fvafk.c2b.morpheme import RootType, PatternType

# Create root
root = Root(
    letters=('ك', 'ت', 'ب'),
    root_type=RootType.TRILATERAL,
    weak_positions=[],
    has_hamza=False
)

# Create pattern
pattern = Pattern(
    name='فَاعِل',
    template='CvaCiC',
    pattern_type=PatternType.ACTIVE_PARTICIPLE,
    stem='كَاتِب',
    description='Active participle pattern',
    weight='فاعل'
)

# Create affixes
affixes = [
    Affix(text='ال', position=AffixPosition.PREFIX, name='definite-article'),
    Affix(text='ُ', position=AffixPosition.SUFFIX, name='damma-nominative')
]

# Assemble morpheme
morpheme = Morpheme(
    root=root,
    pattern=pattern,
    stem='كَاتِب',
    affixes=affixes,
    gloss='DEF-writer.MASC.SG.NOM'
)

# Reconstruct word
word = ''.join(a.text for a in affixes if a.position == AffixPosition.PREFIX)
word += morpheme.stem
word += ''.join(a.text for a in affixes if a.position == AffixPosition.SUFFIX)
# Result: "الكَاتِبُ" (the writer)
```

### Linguistic Glosses

Morphological glosses use Leipzig Glossing Rules format:

```
كَاتِبٌ → writer.MASC.SG.INDEF.NOM
        ↓
    writer: lexical root (ك-ت-ب)
    MASC: masculine gender
    SG: singular number
    INDEF: indefinite (tanwin)
    NOM: nominative case
```

**Common Gloss Abbreviations:**
- **DEF/INDEF**: Definite/indefinite
- **MASC/FEM**: Masculine/feminine
- **SG/DU/PL**: Singular/dual/plural
- **NOM/ACC/GEN**: Nominative/accusative/genitive case
- **ACT/PASS**: Active/passive voice
- **PERF/IMPF**: Perfect/imperfect aspect

---

## Syllabification

**File:** `src/fvafk/c2b/syllabifier.py`

### Syllable Structure

Arabic syllables follow these patterns:

| Type | Structure | Example | Arabic |
|------|-----------|---------|--------|
| CV | Consonant + Short Vowel | ka | كَ |
| CVV | Consonant + Long Vowel | kaa | كَا |
| CVC | Consonant + Vowel + Consonant | kat | كَتْ |
| CVVC | Consonant + Long Vowel + Consonant | kaat | كَاتْ |
| CVCC | Consonant + Vowel + 2 Consonants | katb | كَتْب |

**Constraints:**
- Syllables must start with consonant (no word-initial vowels)
- No more than 2 consonants in coda (word-final position)
- Long vowels count as 2 moras (timing units)

### Syllabifier Class

```python
from fvafk.c2b.syllabifier import Syllabifier

syllabifier = Syllabifier()

# Syllabify word
syllables = syllabifier.syllabify("كَاتِبٌ")
# Output: [('ك', 'ا'), ('ت', 'ِ'), ('ب', 'ٌ')]
#         [  CVV,       CV,       CV     ]

# With syllable types
result = syllabifier.syllabify_with_types("مَكْتُوب")
# Output: [
#   Syllable(onset='م', nucleus='َ', coda='كْ', type=CVC),
#   Syllable(onset='ت', nucleus='ُو', coda='ب', type=CVVC)
# ]
```

### Syllabification Algorithm

```python
def syllabify(self, word: str) -> List[Tuple[str, ...]]:
    """
    Break word into syllables.
    
    Algorithm:
    1. Identify consonants and vowels
    2. Start from left
    3. Build syllable: C + V (+ optional V) (+ optional C/CC)
    4. Move to next consonant, repeat
    """
    segments = self._segment_word(word)
    syllables = []
    i = 0
    
    while i < len(segments):
        syllable = []
        
        # Onset (consonant)
        if self._is_consonant(segments[i]):
            syllable.append(segments[i])
            i += 1
        
        # Nucleus (vowel)
        if i < len(segments) and self._is_vowel(segments[i]):
            syllable.append(segments[i])
            i += 1
            
            # Long vowel?
            if i < len(segments) and self._is_long_vowel(segments[i]):
                syllable.append(segments[i])
                i += 1
        
        # Coda (optional consonant)
        if i < len(segments) and self._is_consonant(segments[i]):
            # Check if it's better to include in this syllable or start next
            if self._should_be_coda(segments, i):
                syllable.append(segments[i])
                i += 1
        
        syllables.append(tuple(syllable))
    
    return syllables
```

---

## Arabic Morphological Patterns

### Verb Derivation System

Arabic verbs are organized into **10 forms** (أوزان), each with semantic implications:

```python
VERB_FORMS = {
    'I': {
        'pattern': 'فَعَلَ',
        'meaning': 'Basic action',
        'example': 'كَتَبَ (wrote)'
    },
    'II': {
        'pattern': 'فَعَّلَ',
        'meaning': 'Causative/intensive',
        'example': 'كَتَّبَ (caused to write)'
    },
    'III': {
        'pattern': 'فَاعَلَ',
        'meaning': 'Try to do, participate',
        'example': 'كَاتَبَ (corresponded with)'
    },
    'IV': {
        'pattern': 'أَفْعَلَ',
        'meaning': 'Causative',
        'example': 'أَكْتَبَ (dictated)'
    },
    'V': {
        'pattern': 'تَفَعَّلَ',
        'meaning': 'Reflexive of Form II',
        'example': 'تَكَتَّبَ (enrolled)'
    },
    'VI': {
        'pattern': 'تَفَاعَلَ',
        'meaning': 'Reciprocal',
        'example': 'تَكَاتَبَ (exchanged letters)'
    },
    'VII': {
        'pattern': 'انْفَعَلَ',
        'meaning': 'Passive/reflexive',
        'example': 'انْكَتَبَ (was written, enrolled)'
    },
    'VIII': {
        'pattern': 'افْتَعَلَ',
        'meaning': 'Reflexive',
        'example': 'اكْتَتَبَ (subscribed)'
    },
    'IX': {
        'pattern': 'افْعَلَّ',
        'meaning': 'Colors/defects',
        'example': 'اخْضَرَّ (became green)'
    },
    'X': {
        'pattern': 'اسْتَفْعَلَ',
        'meaning': 'Request/seek',
        'example': 'اسْتَكْتَبَ (asked to write)'
    }
}
```

### Noun Patterns

#### Singular Nouns (أسماء المفرد)

```python
SINGULAR_NOUN_PATTERNS = {
    'فَعْل': ['عَقْل (intellect)', 'عِلْم (knowledge)'],
    'فُعْل': ['حُكْم (judgment)', 'شُكْر (thanks)'],
    'فِعْل': ['ذِكْر (mention)', 'فِكْر (thought)'],
    'فَعَل': ['سَبَب (reason)', 'جَبَل (mountain)'],
    'فُعُل': ['رُسُل (messengers)', 'كُتُب (books)'],
    'فَعِيل': ['كَرِيم (generous)', 'عَلِيم (knowledgeable)'],
    'فَعَال': ['كِتَاب (book)', 'سَلَام (peace)'],
    'فِعَال': ['حِسَاب (calculation)', 'نِصَاب (threshold)'],
}
```

#### Plural Patterns (جموع التكسير)

**Broken Plurals** (irregular, very common in Arabic):

```python
BROKEN_PLURAL_PATTERNS = {
    'فُعُول': 'كِتَاب → كُتُب (books)',
    'فُعَّال': 'كَاتِب → كُتَّاب (writers)',
    'فَوَاعِل': 'كَاتِب → كَوَاتِب (female writers)',
    'أَفْعَال': 'وَلَد → أَوْلَاد (children)',
    'فِعَال': 'جَبَل → جِبَال (mountains)',
    'أَفْعِلَة': 'سُؤَال → أَسْئِلَة (questions)',
}
```

**Sound Plurals** (regular):
- **Masculine:** Add ون (nominative) or ين (accusative/genitive)
  - مُسْلِم → مُسْلِمُون / مُسْلِمِين
- **Feminine:** Add ات
  - مُسْلِمَة → مُسْلِمَات

---

## Implementation Examples

### Complete Morphological Analysis

```python
from fvafk.c2b.root_extractor import RootExtractor
from fvafk.c2b.pattern_matcher import PatternMatcher
from fvafk.c2b.morpheme import Morpheme, Affix, AffixPosition

# Initialize components
root_extractor = RootExtractor()
pattern_matcher = PatternMatcher()

# Input word
word = "الكَاتِبُون"  # "the writers"

# Step 1: Extract root
root = root_extractor.extract(word)
print(root)
# Output: Root(letters=('ك', 'ت', 'ب'), root_type=TRILATERAL)

# Step 2: Match pattern
pattern = pattern_matcher.match("كَاتِب", root)
print(pattern)
# Output: Pattern(name='فَاعِل', pattern_type=ACTIVE_PARTICIPLE)

# Step 3: Identify affixes
affixes = [
    Affix(text='ال', position=AffixPosition.PREFIX, name='definite-article'),
    Affix(text='ُون', position=AffixPosition.SUFFIX, name='masculine-plural-nominative')
]

# Step 4: Assemble morpheme
morpheme = Morpheme(
    root=root,
    pattern=pattern,
    stem='كَاتِب',
    affixes=affixes,
    gloss='DEF-writer.MASC.PL.NOM'
)

print(morpheme)
# Output: Morpheme(
#   root=Root(letters=('ك', 'ت', 'ب')),
#   pattern=Pattern(name='فَاعِل'),
#   stem='كَاتِب',
#   affixes=[...],
#   gloss='DEF-writer.MASC.PL.NOM'
# )
```

### Handling Weak Roots

```python
# Weak root example: ق-و-ل (to say)
root = root_extractor.extract("قَالَ")  # Perfect tense
# The و in the root becomes ا in this form

print(root)
# Output: Root(
#   letters=('ق', 'و', 'ل'),
#   weak_positions=[1],
#   has_hamza=False
# )

# Pattern matching handles the vowel change
pattern = pattern_matcher.match("قَالَ", root)
print(pattern)
# Output: Pattern(name='فَعَلَ', pattern_type=VERB_FORM_I)
```

### Broken Plural Analysis

```python
# Singular: كِتَاب (book)
# Plural: كُتُب (books)

root = root_extractor.extract("كُتُب")
# Output: Root(letters=('ك', 'ت', 'ب'))

pattern = pattern_matcher.match("كُتُب", root)
# Output: Pattern(name='فُعُل', pattern_type=BROKEN_PLURAL)
```

---

## Related Documentation
- [Architecture Overview](ARCHITECTURE.md)
- [Phonological Gates](PHONOLOGICAL_GATES.md)
- [API Reference](API_REFERENCE.md)
- [Tutorial](TUTORIAL.md)

---

## References
- McCarthy, J. (1981). *A Prosodic Theory of Nonconcatenative Morphology*
- Wright, W. (1896). *A Grammar of the Arabic Language* (3rd ed.)
- Ryding, K. (2005). *A Reference Grammar of Modern Standard Arabic*
- Beesley, K. & Karttunen, L. (2003). *Finite State Morphology*
- Holes, C. (2004). *Modern Arabic: Structures, Functions, and Varieties*
