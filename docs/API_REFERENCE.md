# API Reference

**Version:** 1.0  
**Last Updated:** 2026-02-03

## Table of Contents
1. [Installation](#installation)
2. [Core Modules](#core-modules)
3. [Phase 1 (C1): Text Encoding](#phase-1-c1-text-encoding)
4. [Phase 2 (C2a): Phonological Gates](#phase-2-c2a-phonological-gates)
5. [Phase 3 (C2b): Morphological Analysis](#phase-3-c2b-morphological-analysis)
6. [CLI Interface](#cli-interface)
7. [Type Definitions](#type-definitions)

---

## Installation

```bash
# Clone repository
git clone https://github.com/sonaiso/Eqratech_Hussein_Hiyassat_Project.git
cd Eqratech_Hussein_Hiyassat_Project

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For testing

# Verify installation
PYTHONPATH=src python -c "from fvafk import __version__; print(__version__)"
```

---

## Core Modules

### Package Structure

```
fvafk/
├── __init__.py
├── c1/                      # Phase 1: Text Encoding
│   ├── encoder.py
│   ├── segment_inventory.py
│   └── unit.py
├── c2a/                     # Phase 2: Phonological Processing
│   ├── gate_framework.py
│   ├── gates/
│   │   ├── gate_sukun.py
│   │   ├── gate_shadda.py
│   │   ├── gate_hamza.py
│   │   ├── gate_waqf.py
│   │   ├── gate_idgham.py
│   │   ├── gate_madd.py
│   │   ├── gate_deletion.py
│   │   ├── gate_epenthesis.py
│   │   ├── gate_assimilation.py
│   │   └── gate_tanwin.py
│   └── syllable.py
├── c2b/                     # Phase 3: Morphological Analysis
│   ├── root_extractor.py
│   ├── pattern_matcher.py
│   ├── morpheme.py
│   └── syllabifier.py
├── cli/                     # Command-line interface
│   └── main.py
└── orthography_adapter.py   # Orthographic normalization
```

---

## Phase 1 (C1): Text Encoding

### OrthographyAdapter

**File:** `src/fvafk/orthography_adapter.py`

#### Class Definition

```python
class OrthographyAdapter:
    """
    Normalizes Arabic text orthography.
    
    Handles:
    - Unicode normalization (NFC/NFD)
    - Hamza carrier normalization
    - Alif maqsura conversion
    - Taa marbuta handling
    """
    
    def normalize(self, text: str) -> str:
        """
        Normalize Arabic text.
        
        Args:
            text: Raw Arabic text
            
        Returns:
            Normalized text with consistent orthography
            
        Example:
            >>> adapter = OrthographyAdapter()
            >>> adapter.normalize("أَكَلَ")
            'اكل'
        """
```

#### Methods

##### `normalize(text: str) -> str`

Normalize Arabic text to canonical form.

**Parameters:**
- `text` (str): Input Arabic text

**Returns:**
- `str`: Normalized text

**Example:**
```python
from fvafk.orthography_adapter import OrthographyAdapter

adapter = OrthographyAdapter()

# Hamza normalization
print(adapter.normalize("أَكَلَ"))  # → "اكل"

# Alif maqsura
print(adapter.normalize("مُوسَى"))  # → "موسي"

# Mixed
print(adapter.normalize("الْمُؤْمِنُونَ"))  # → "المامنون"
```

##### `remove_diacritics(text: str) -> str`

Remove all diacritical marks.

**Parameters:**
- `text` (str): Arabic text with diacritics

**Returns:**
- `str`: Text without diacritics

**Example:**
```python
adapter = OrthographyAdapter()
print(adapter.remove_diacritics("كَاتِبٌ"))  # → "كاتب"
```

##### `normalize_hamza(text: str) -> str`

Normalize hamza carriers to base letters.

**Parameters:**
- `text` (str): Text with hamza carriers

**Returns:**
- `str`: Text with normalized hamza

**Example:**
```python
adapter = OrthographyAdapter()
print(adapter.normalize_hamza("سُؤَال"))  # → "سوال"
print(adapter.normalize_hamza("مَسْئُول"))  # → "مسيول"
```

---

### SegmentInventory

**File:** `src/fvafk/c1/segment_inventory.py`

#### Constants

```python
CONSONANTS = [
    'ء', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز',
    'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك',
    'ل', 'م', 'ن', 'ه', 'و', 'ي'
]  # 28 Arabic consonants

SHORT_VOWELS = ['َ', 'ِ', 'ُ']  # fatha, kasra, damma

LONG_VOWELS = ['ا', 'و', 'ي']  # when functioning as vowels

DIACRITICS = [
    'ْ',  # sukun
    'ّ',  # shadda
    'ً',  # fathatan
    'ٌ',  # dammatan
    'ٍ',  # kasratan
]

SUN_LETTERS = ['ت', 'ث', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ل', 'ن']
MOON_LETTERS = ['ا', 'ب', 'ج', 'ح', 'خ', 'ع', 'غ', 'ف', 'ق', 'ك', 'م', 'ه', 'و', 'ي']
```

#### Functions

##### `is_consonant(char: str) -> bool`

Check if character is a consonant.

**Example:**
```python
from fvafk.c1.segment_inventory import is_consonant

print(is_consonant('ك'))   # True
print(is_consonant('َ'))   # False
```

##### `is_vowel(char: str) -> bool`

Check if character is a vowel (short or long).

##### `is_sun_letter(char: str) -> bool`

Check if character is a sun letter (for assimilation).

---

### Encoder

**File:** `src/fvafk/c1/encoder.py`

#### Class Definition

```python
class Encoder:
    """
    Encodes Arabic text into segment sequences.
    """
    
    def encode(self, text: str) -> List[str]:
        """
        Encode text into segment list.
        
        Args:
            text: Normalized Arabic text
            
        Returns:
            List of segments (consonants, vowels, diacritics)
            
        Example:
            >>> encoder = Encoder()
            >>> encoder.encode("كَاتِب")
            ['ك', 'َ', 'ا', 'ت', 'ِ', 'ب']
        """
```

#### Methods

##### `encode(text: str) -> List[str]`

Convert text to segment sequence.

**Example:**
```python
from fvafk.c1.encoder import Encoder

encoder = Encoder()
segments = encoder.encode("كَاتِبٌ")
print(segments)
# Output: ['ك', 'َ', 'ا', 'ت', 'ِ', 'ب', 'ٌ']
```

---

## Phase 2 (C2a): Phonological Gates

### GateFramework

**File:** `src/fvafk/c2a/gate_framework.py`

#### Enums

```python
class GateStatus(Enum):
    """Status returned by phonological gate."""
    ACCEPT = auto()   # Pass through unchanged
    REPAIR = auto()   # Modified to fix violation
    REJECT = auto()   # Unrecoverable error
```

#### Classes

##### GateResult

```python
@dataclass
class GateResult:
    """Result of applying a phonological gate."""
    status: GateStatus
    output: List[str]
    reason: str
    deltas: List[str] = field(default_factory=list)
    latency_ms: float = 0.0
```

**Attributes:**
- `status`: ACCEPT, REPAIR, or REJECT
- `output`: Modified segment list
- `reason`: Human-readable explanation
- `deltas`: List of changes made
- `latency_ms`: Processing time

##### PhonologicalGate (Abstract)

```python
class PhonologicalGate(ABC):
    """Base class for all phonological gates."""
    
    def __init__(self, gate_id: str):
        self.gate_id = gate_id
    
    @abstractmethod
    def apply(self, segments: List[str]) -> GateResult:
        """
        Apply gate logic to segments.
        
        Args:
            segments: List of Arabic segments
            
        Returns:
            GateResult with status, output, and reason
        """
        pass
```

##### GateOrchestrator

```python
class GateOrchestrator:
    """Chains phonological gates sequentially."""
    
    def __init__(self, gates: List[PhonologicalGate]):
        """
        Initialize orchestrator.
        
        Args:
            gates: List of gates in processing order
        """
        self.gates = gates
    
    def run(self, segments: List[str]) -> Tuple[List[str], List[GateResult]]:
        """
        Run all gates sequentially.
        
        Args:
            segments: Input segment list
            
        Returns:
            Tuple of (final_segments, gate_results)
            
        Example:
            >>> orchestrator = GateOrchestrator([GateSukun(), GateShadda()])
            >>> output, results = orchestrator.run(['ك', 'ْ', 'ت', 'ْ', 'ب'])
            >>> print(results[0].status)
            GateStatus.REPAIR
        """
```

#### Usage Example

```python
from fvafk.c2a.gate_framework import GateOrchestrator
from fvafk.c2a.gates import (
    GateSukun, GateShadda, GateHamza, GateWaqf,
    GateIdgham, GateMadd, GateDeletion, GateEpenthesis,
    GateAssimilation, GateTanwin
)

# Create orchestrator
orchestrator = GateOrchestrator([
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
])

# Process segments
input_segments = ['ك', 'َ', 'ا', 'ت', 'ِ', 'ب', 'ٌ']
output_segments, gate_results = orchestrator.run(input_segments)

# Examine results
for i, result in enumerate(gate_results):
    gate_name = orchestrator.gates[i].gate_id
    print(f"{gate_name}: {result.status.name}")
    if result.deltas:
        print(f"  Changes: {', '.join(result.deltas)}")
    print(f"  Latency: {result.latency_ms:.3f}ms")
```

---

### Individual Gates

All gates in `src/fvafk/c2a/gates/` implement the `PhonologicalGate` interface.

#### Common Methods

Each gate class has:

```python
class GateXXX(PhonologicalGate):
    def __init__(self):
        super().__init__("gate_id")
    
    def apply(self, segments: List[str]) -> GateResult:
        """Apply gate-specific logic."""
        pass
```

#### Gate Examples

```python
# GateSukun
from fvafk.c2a.gates import GateSukun

gate = GateSukun()
result = gate.apply(['ك', 'ْ', 'ت', 'ْ', 'ب'])
print(result.status)  # REPAIR
print(result.output)  # ['ك', 'َ', 'ت', 'ْ', 'ب']

# GateAssimilation
from fvafk.c2a.gates import GateAssimilation

gate = GateAssimilation()
result = gate.apply(['ا', 'ل', 'ش', 'م', 'س'])
print(result.status)  # REPAIR
print(result.output)  # ['ا', 'ش', 'ّ', 'م', 'س']

# GateTanwin
from fvafk.c2a.gates import GateTanwin

gate = GateTanwin()
result = gate.apply(['ك', 'ت', 'ا', 'ب', 'ٌ'])
print(result.status)  # REPAIR
print(result.output)  # ['ك', 'ت', 'ا', 'ب', 'ُ', 'ن']
```

---

## Phase 3 (C2b): Morphological Analysis

### RootExtractor

**File:** `src/fvafk/c2b/root_extractor.py`

#### Class Definition

```python
class RootExtractor:
    """
    Extracts consonantal roots from Arabic words.
    
    Supports:
    - Trilateral (3-letter) and quadrilateral (4-letter) roots
    - Weak roots (containing و، ي، ء)
    - Hamza normalization
    - Affix stripping
    """
    
    PREFIXES = ['است', 'ال', 'وال', 'فال', ...]
    SUFFIXES = ['ون', 'ين', 'ات', 'ان', ...]
    WEAK_LETTERS = {'و', 'ي', 'ا', 'ء'}
    
    def __init__(self, known_roots: Optional[Set[str]] = None):
        """
        Initialize root extractor.
        
        Args:
            known_roots: Optional set of valid roots for validation
        """
```

#### Methods

##### `extract(word: str) -> Optional[Root]`

Extract root from word.

**Parameters:**
- `word` (str): Arabic word (with or without diacritics)

**Returns:**
- `Root` object if successful, `None` if extraction fails

**Example:**
```python
from fvafk.c2b.root_extractor import RootExtractor

extractor = RootExtractor()

# Basic extraction
root = extractor.extract("كَاتِب")
print(root.letters)  # ('ك', 'ت', 'ب')
print(root.root_type)  # RootType.TRILATERAL

# With affixes
root = extractor.extract("الْمُسْتَخْرَجُون")
print(root.letters)  # ('خ', 'ر', 'ج')

# Weak root
root = extractor.extract("قَالَ")
print(root.letters)  # ('ق', 'و', 'ل')
print(root.weak_positions)  # [1]
```

##### `_normalize(word: str) -> str`

Internal normalization (remove diacritics, expand shadda).

##### `_strip_affixes(word: str) -> str`

Remove known prefixes and suffixes.

##### `_extract_consonants(word: str) -> List[str]`

Extract root consonants, filtering pattern vowels.

---

### PatternMatcher

**File:** `src/fvafk/c2b/pattern_matcher.py`

#### Class Definition

```python
class PatternMatcher:
    """
    Matches words against morphological patterns.
    
    Supports:
    - 10 verb forms (I-X)
    - Active/passive participles
    - Noun patterns (singular, plural, broken plural)
    - Pattern templates with CV notation
    """
    
    def __init__(self, threshold: float = 0.7):
        """
        Initialize pattern matcher.
        
        Args:
            threshold: Minimum confidence score (0.0-1.0)
        """
```

#### Methods

##### `match(word: str, root: Root) -> Optional[Pattern]`

Match word to morphological pattern.

**Parameters:**
- `word` (str): Arabic word
- `root` (Root): Extracted root

**Returns:**
- `Pattern` object if match found, `None` otherwise

**Example:**
```python
from fvafk.c2b.pattern_matcher import PatternMatcher
from fvafk.c2b.root_extractor import RootExtractor

extractor = RootExtractor()
matcher = PatternMatcher()

# Active participle
root = extractor.extract("كَاتِب")
pattern = matcher.match("كَاتِب", root)
print(pattern.name)  # 'فَاعِل'
print(pattern.pattern_type)  # PatternType.ACTIVE_PARTICIPLE

# Verb Form II
root = extractor.extract("دَرَّسَ")
pattern = matcher.match("دَرَّسَ", root)
print(pattern.name)  # 'فَعَّلَ'
print(pattern.pattern_type)  # PatternType.VERB_FORM_II

# Broken plural
root = extractor.extract("كُتُب")
pattern = matcher.match("كُتُب", root)
print(pattern.name)  # 'فُعُل'
print(pattern.pattern_type)  # PatternType.BROKEN_PLURAL
```

##### `get_all_patterns() -> List[PatternTemplate]`

Get list of all known pattern templates.

---

### Morpheme Classes

**File:** `src/fvafk/c2b/morpheme.py`

#### Root

```python
@dataclass
class Root:
    """Consonantal root."""
    letters: Tuple[str, ...]          # Root consonants
    root_type: RootType               # TRILATERAL or QUADRILATERAL
    weak_positions: List[int] = field(default_factory=list)
    has_hamza: bool = False
```

#### Pattern

```python
@dataclass
class Pattern:
    """Morphological pattern."""
    name: str                  # Arabic pattern name
    template: str              # CV notation
    pattern_type: PatternType  # Verb/noun/participle type
    stem: str                  # Actual word stem
    description: str           # Description
    weight: str                # Morphological weight
```

#### Affix

```python
@dataclass
class Affix:
    """Morphological affix."""
    text: str
    position: AffixPosition  # PREFIX, SUFFIX, INFIX
    name: str                # Linguistic name
```

#### Morpheme

```python
@dataclass
class Morpheme:
    """Complete morphological analysis."""
    root: Root
    pattern: Pattern
    stem: str
    affixes: List[Affix] = field(default_factory=list)
    gloss: str = ""  # Linguistic gloss
```

#### Example

```python
from fvafk.c2b.morpheme import Root, Pattern, Morpheme, Affix, AffixPosition
from fvafk.c2b.morpheme import RootType, PatternType

# Create morpheme
morpheme = Morpheme(
    root=Root(
        letters=('ك', 'ت', 'ب'),
        root_type=RootType.TRILATERAL
    ),
    pattern=Pattern(
        name='فَاعِل',
        template='CvaCiC',
        pattern_type=PatternType.ACTIVE_PARTICIPLE,
        stem='كَاتِب',
        description='Active participle',
        weight='فاعل'
    ),
    stem='كَاتِب',
    affixes=[
        Affix(text='ال', position=AffixPosition.PREFIX, name='definite'),
        Affix(text='ُون', position=AffixPosition.SUFFIX, name='masc-pl-nom')
    ],
    gloss='DEF-writer.MASC.PL.NOM'
)

print(morpheme.root.letters)  # ('ك', 'ت', 'ب')
print(morpheme.pattern.name)  # 'فَاعِل'
print(morpheme.gloss)  # 'DEF-writer.MASC.PL.NOM'
```

---

### Syllabifier

**File:** `src/fvafk/c2b/syllabifier.py`

#### Class Definition

```python
class Syllabifier:
    """
    Breaks words into syllables.
    
    Supports syllable types:
    - CV: Consonant + Short Vowel
    - CVV: Consonant + Long Vowel
    - CVC: Consonant + Vowel + Consonant
    - CVVC, CVCC: Complex syllables
    """
```

#### Methods

##### `syllabify(word: str) -> List[Tuple[str, ...]]`

Break word into syllables.

**Example:**
```python
from fvafk.c2b.syllabifier import Syllabifier

syllabifier = Syllabifier()

syllables = syllabifier.syllabify("كَاتِبٌ")
print(syllables)
# Output: [('ك', 'ا'), ('ت', 'ِ'), ('ب', 'ٌ')]
#         [  CVV,       CV,       CV     ]

syllables = syllabifier.syllabify("مَكْتُوب")
print(syllables)
# Output: [('م', 'َ', 'كْ'), ('ت', 'ُو', 'ب')]
#         [     CVC,           CVVC      ]
```

---

## CLI Interface

**File:** `src/fvafk/cli/main.py`

### Command-Line Usage

```bash
# Basic usage
python -m fvafk.cli "كَاتِبٌ"

# With morphology
python -m fvafk.cli "كَاتِبٌ" --morphology

# JSON output
python -m fvafk.cli "كَاتِبٌ" --morphology --json

# Verbose (show gate details)
python -m fvafk.cli "كَاتِبٌ" --morphology --verbose
```

### Python API

```python
from fvafk.cli.main import analyze_text

# Analyze text
result = analyze_text("كَاتِبٌ", morphology=True, verbose=True)

print(result['input'])         # Original text
print(result['segments'])      # C1 segments
print(result['gate_results'])  # C2a gate results
print(result['root'])          # C2b root
print(result['pattern'])       # C2b pattern
print(result['morpheme'])      # Complete analysis
```

---

## Type Definitions

### Enums

```python
from enum import Enum, auto

class RootType(Enum):
    TRILATERAL = auto()
    QUADRILATERAL = auto()

class PatternType(Enum):
    VERB_FORM_I = auto()
    VERB_FORM_II = auto()
    # ... Forms III-X
    ACTIVE_PARTICIPLE = auto()
    PASSIVE_PARTICIPLE = auto()
    NOUN_SINGULAR = auto()
    NOUN_PLURAL = auto()
    BROKEN_PLURAL = auto()

class AffixPosition(Enum):
    PREFIX = auto()
    SUFFIX = auto()
    INFIX = auto()

class GateStatus(Enum):
    ACCEPT = auto()
    REPAIR = auto()
    REJECT = auto()
```

---

## Related Documentation
- [Architecture Overview](ARCHITECTURE.md)
- [Phonological Gates Reference](PHONOLOGICAL_GATES.md)
- [Morphology Guide](MORPHOLOGY_GUIDE.md)
- [Tutorial](TUTORIAL.md)

---

## Support

For issues or questions:
- **GitHub Issues**: https://github.com/sonaiso/Eqratech_Hussein_Hiyassat_Project/issues
- **Documentation**: See `docs/` directory
- **Tests**: See `tests/` directory for usage examples
