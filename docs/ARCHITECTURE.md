# FVAFK Framework Architecture

**Version:** 1.0  
**Last Updated:** 2026-02-03

## Table of Contents
1. [Overview](#overview)
2. [Three-Phase Model](#three-phase-model)
3. [Phase 1: Text Encoding (C1)](#phase-1-text-encoding-c1)
4. [Phase 2: Phonological Processing (C2a)](#phase-2-phonological-processing-c2a)
5. [Phase 3: Morphological Analysis (C2b)](#phase-3-morphological-analysis-c2b)
6. [Data Flow](#data-flow)
7. [Design Principles](#design-principles)
8. [Performance Characteristics](#performance-characteristics)

---

## Overview

FVAFK (Formal Verification of Arabic Fully-Optimized Knowledge) is an optimization-based framework for Arabic language processing that implements a three-phase computational model. The framework is designed to handle Arabic text processing from raw input to deep morphological analysis while maintaining linguistic accuracy and computational efficiency.

### Key Goals
- **Linguistic Accuracy**: Implement Tajweed-based phonological rules
- **Computational Efficiency**: Sub-millisecond processing per word (<0.5ms)
- **Formal Verification**: Support for Coq-based correctness proofs
- **Modularity**: Independent gates and analyzers for easy extension

### Core Philosophy
The framework follows an **optimization-based approach** where:
1. Text is progressively refined through sequential phases
2. Each phase produces output that serves as input to the next
3. Gates can ACCEPT (pass-through), REPAIR (modify), or REJECT (fail)
4. All transformations are traceable and reversible (where appropriate)

---

## Three-Phase Model

```
┌─────────────────────────────────────────────────────────────────┐
│                    FVAFK Processing Pipeline                     │
└─────────────────────────────────────────────────────────────────┘

Input Text: "كَاتِبٌ"
    │
    ▼
┌──────────────────────────────────┐
│  Phase 1 (C1): Text Encoding     │
│  • Unicode normalization          │
│  • Diacritic preservation         │
│  • Segment inventory creation     │
└──────────────────────────────────┘
    │ Segments: ['ك', 'َ', 'ا', 'ت', 'ِ', 'ب', 'ٌ']
    ▼
┌──────────────────────────────────┐
│  Phase 2 (C2a): Phonological     │
│  • 10 Tajweed-based gates         │
│  • Sequential gate processing     │
│  • Repair/reject mechanisms       │
└──────────────────────────────────┘
    │ Phonologically valid segments
    ▼
┌──────────────────────────────────┐
│  Phase 3 (C2b): Morphological    │
│  • Root extraction                │
│  • Pattern matching               │
│  • Affix identification           │
└──────────────────────────────────┘
    │
    ▼
Output: Root='ك-ت-ب', Pattern='فَاعِل', Gloss='active-participle'
```

---

## Phase 1: Text Encoding (C1)

### Purpose
Convert raw Arabic text into a normalized, segmented representation suitable for phonological and morphological processing.

### Components

#### 1. Segment Inventory (`src/fvafk/c1/segment_inventory.py`)
- Defines 28 Arabic consonants + 6 short vowels
- Maps Unicode characters to canonical segments
- Handles diacritic marks (fatha, kasra, damma, sukun, shadda, tanwin)

**Example:**
```python
CONSONANTS = ['ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', ...]
SHORT_VOWELS = ['َ', 'ِ', 'ُ']  # fatha, kasra, damma
DIACRITICS = ['ْ', 'ّ', 'ً', 'ٌ', 'ٍ']  # sukun, shadda, tanwin
```

#### 2. Orthography Adapter (`src/fvafk/orthography_adapter.py`)
Normalizes Arabic orthography:
- **Hamza normalization**: أ، إ، آ → ا
- **Alif maqsura**: ى → ي
- **Taa marbuta**: ة preservation
- **Unicode normalization**: NFC/NFD conversion
- **Diacritic handling**: Preserve or strip based on context

#### 3. Encoder (`src/fvafk/c1/encoder.py`)
Converts normalized text into segment sequences:
```python
Input:  "كَاتِبٌ"
Output: ['ك', 'َ', 'ا', 'ت', 'ِ', 'ب', 'ٌ']
```

### Output Format
A `List[str]` where each element is:
- A consonant (e.g., 'ك', 'ت')
- A short vowel (e.g., 'َ', 'ِ', 'ُ')
- A diacritic (e.g., 'ْ' sukun, 'ّ' shadda)
- A long vowel (e.g., 'ا', 'و', 'ي' when functioning as vowels)

---

## Phase 2: Phonological Processing (C2a)

### Purpose
Apply 10 Tajweed-based phonological rules to ensure the segment sequence is phonologically valid according to Arabic linguistic rules.

### Architecture

#### Gate Framework (`src/fvafk/c2a/gate_framework.py`)

**Core Classes:**
```python
class PhonologicalGate(ABC):
    """Base class for all phonological gates."""
    @abstractmethod
    def apply(self, segments: List[str]) -> GateResult:
        pass

class GateOrchestrator:
    """Chains gates sequentially."""
    def run(self, segments: List[str]) -> Tuple[List[str], List[GateResult]]:
        # Apply each gate in order, stop on REJECT
```

**Gate Results:**
```python
@dataclass
class GateResult:
    status: GateStatus      # ACCEPT, REPAIR, REJECT
    output: List[str]       # Modified segment list
    reason: str             # Human-readable explanation
    deltas: List[str]       # List of changes made
    latency_ms: float       # Processing time
```

### The 10 Phonological Gates

| Order | Gate | Rule Category | Example |
|-------|------|---------------|---------|
| 1 | `GateSukun` | Sukun repair | C-ْ-C-ْ → C-َ-C-ْ |
| 2 | `GateShadda` | Gemination | Cّ → C-C |
| 3 | `GateHamza` | Hamza placement | أ/إ/ؤ/ئ rules |
| 4 | `GateWaqf` | Pause/stopping | Word-final rules |
| 5 | `GateIdgham` | Assimilation with ghunnah | إدغام |
| 6 | `GateMadd` | Vowel lengthening | مد |
| 7 | `GateDeletion` | Predictable deletions | Alif/hamza in speech |
| 8 | `GateEpenthesis` | Vowel insertion | Break clusters |
| 9 | `GateAssimilation` | Lam assimilation | ال + sun letters |
| 10 | `GateTanwin` | Tanwin expansion | ٌ → ُ-ن |

**Processing Flow:**
```python
orchestrator = GateOrchestrator([
    GateSukun(),
    GateShadda(),
    GateHamza(),
    # ... all 10 gates
])

final_segments, results = orchestrator.run(input_segments)

for gate_result in results:
    print(f"{gate_result.status}: {gate_result.reason}")
    if gate_result.deltas:
        print(f"  Changes: {gate_result.deltas}")
```

### Gate Sequencing
The order of gates is linguistically motivated:
1. **Structural repairs first** (sukun, shadda)
2. **Orthographic rules** (hamza, waqf)
3. **Phonetic processes** (idgham, madd, assimilation)
4. **Predictable operations** (deletion, epenthesis, tanwin)

---

## Phase 3: Morphological Analysis (C2b)

### Purpose
Extract morphological structure from phonologically valid segments: roots, patterns, affixes, and morphological features.

### Components

#### 1. Root Extractor (`src/fvafk/c2b/root_extractor.py`)

**Algorithm:**
```
Input: "كَاتِبٌ"
  ↓ 1. Normalize (remove diacritics, hamza carriers)
  ↓ 2. Strip affixes (prefixes like ال، و، ف; suffixes like ون، ين)
  ↓ 3. Extract consonants (filter out long vowels between consonants)
  ↓ 4. Validate root (trilateral or quadrilateral)
Output: Root(letters=['ك', 'ت', 'ب'], root_type=TRILATERAL)
```

**Features:**
- Handles weak roots (و، ي، ء)
- Detects gemination (doubled consonants from shadda)
- Supports known root dictionary validation
- Recognizes 50+ common prefixes and suffixes

#### 2. Pattern Matcher (`src/fvafk/c2b/pattern_matcher.py`)

**Template System:**
```python
PATTERNS = {
    'فَاعِل': PatternTemplate(  # Active participle
        name='فَاعِل',
        template='CvvCvC',      # Consonant-vowel notation
        pattern_type=PatternType.ACTIVE_PARTICIPLE,
        weight='فاعل',
        description='Active participle pattern'
    ),
    # ... 25+ patterns for Forms I-X, plurals, etc.
}
```

**Matching Process:**
1. Normalize word to consonant skeleton
2. Try each pattern template
3. Align root consonants to pattern positions
4. Verify vowel/diacritic match
5. Return best match with confidence score

#### 3. Morpheme Assembly (`src/fvafk/c2b/morpheme.py`)

**Data Structures:**
```python
@dataclass
class Root:
    letters: Tuple[str, ...]
    root_type: RootType           # TRILATERAL, QUADRILATERAL
    weak_positions: List[int]
    has_hamza: bool

@dataclass  
class Pattern:
    name: str
    template: str
    pattern_type: PatternType     # VERB_FORM_I, NOUN_SINGULAR, etc.
    stem: str
    description: str
    weight: str

@dataclass
class Morpheme:
    root: Root
    pattern: Pattern
    stem: str
    affixes: List[Affix]
    gloss: str                    # Linguistic gloss
```

#### 4. Syllabifier (`src/fvafk/c2b/syllabifier.py`)
Breaks words into syllable structures (CV, CVC, CVV, etc.) for prosodic analysis.

---

## Data Flow

### Complete Pipeline Example

**Input:** "كَاتِبٌ" (kātibun - "a writer")

**Phase 1 (C1):**
```python
text = "كَاتِبٌ"
adapter = OrthographyAdapter()
normalized = adapter.normalize(text)  # Unicode normalization
encoder = Encoder()
segments = encoder.encode(normalized)
# Output: ['ك', 'َ', 'ا', 'ت', 'ِ', 'ب', 'ٌ']
```

**Phase 2 (C2a):**
```python
gates = [GateSukun(), GateShadda(), ..., GateTanwin()]
orchestrator = GateOrchestrator(gates)
phonological_output, gate_results = orchestrator.run(segments)

# GateTanwin expands 'ٌ' → 'ُ' + 'ن'
# Output: ['ك', 'َ', 'ا', 'ت', 'ِ', 'ب', 'ُ', 'ن']
```

**Phase 3 (C2b):**
```python
root_extractor = RootExtractor()
pattern_matcher = PatternMatcher()

# Extract root
root = root_extractor.extract("كاتب")
# Output: Root(letters=('ك', 'ت', 'ب'), root_type=TRILATERAL)

# Match pattern
pattern = pattern_matcher.match("كاتب", root)
# Output: Pattern(name='فَاعِل', pattern_type=ACTIVE_PARTICIPLE)

# Assemble morpheme
morpheme = Morpheme(
    root=root,
    pattern=pattern,
    stem='كاتب',
    affixes=[Affix(text='ٌ', position=SUFFIX, name='tanwin-damma')],
    gloss='writer.MASC.SG.INDEF.NOM'
)
```

---

## Design Principles

### 1. **Separation of Concerns**
Each phase handles a distinct linguistic level:
- C1: Orthographic
- C2a: Phonological
- C2b: Morphological

### 2. **Linguistic Accuracy**
Rules are based on:
- Classical Arabic grammar (Sībawayh tradition)
- Tajweed rules for phonology
- Modern computational morphology

### 3. **Traceability**
Every transformation records:
- Input state
- Output state
- Reason for change
- Processing time

### 4. **Extensibility**
- Gates implement `PhonologicalGate` interface
- New gates can be added to orchestrator
- Pattern templates are data-driven (YAML/JSON)

### 5. **Formal Verification Ready**
- Coq proofs can be extracted from Python code
- Invariants are explicitly documented
- Theorems: `T_CODEC_REVERSIBLE`, `T_NO_C3_WITHOUT_C2`, `C1_IMMUTABILITY`

---

## Performance Characteristics

### Target Metrics
- **Latency**: <0.5ms per word (C1 + C2a + C2b)
- **Throughput**: >2000 words/second on modern CPU
- **Memory**: <100MB for full dictionary + patterns

### Optimization Strategies
1. **Lazy evaluation**: Gates only process when needed
2. **Early termination**: Stop on REJECT status
3. **Pattern caching**: Pre-compiled regex for templates
4. **Affix stripping**: Rule-based (no ML overhead)

### Scalability
- **Parallel processing**: Independent words can process concurrently
- **Batch mode**: Vector operations for multiple inputs
- **Streaming**: Process text incrementally

---

## Related Documentation
- [Phonological Gates Reference](PHONOLOGICAL_GATES.md)
- [Morphology Guide](MORPHOLOGY_GUIDE.md)
- [API Reference](API_REFERENCE.md)
- [Tutorial](TUTORIAL.md)
- [Implementation Status](implementation_status.md)

---

## References
- Sībawayh. *Al-Kitāb fī an-Naḥw* (The Book on Grammar)
- Ibn al-Jazari. *Tajweed rules* (Quranic recitation)
- McCarthy, J. *Prosodic Morphology* (1979)
- Beesley, K. & Karttunen, L. *Finite State Morphology* (2003)
