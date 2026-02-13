A production-ready Arabic NLP system implementing a **6-layer computational linguistics model** with dual architecture:

1. **FVAFK Pipeline**: Three-phase text processing (C1 → C2a → C2b)
2. **Grammar Engines**: 66 engines organized in a 3-level hierarchical taxonomy

---

## 🎯 Overview

### Two Main Subsystems

#### 1. FVAFK Pipeline (Text Processing)
- **C1**: Text normalization & encoding
- **C2a**: Phonological analysis (10 Tajweed-based gates)
- **C2b**: Morphological analysis (root extraction, pattern matching)
- **Performance**: Sub-millisecond (<0.5ms per word)
- **Quality**: 101 tests (100% passing)

#### 2. Grammar Engines (66 Total)
**Organized in 6-Layer Computational Linguistics Model**:
```
Layer 6: Generation (التوليد)  → 3 engines
Layer 5: Rhetoric (البلاغة)    → 11 engines
Layer 4: Syntax (النحو)        → 13 engines
Layer 3: Lexicon (المعجم)      → 15 engines
Layer 2: Morphology (الصرف)    → 22 engines
Layer 1: Phonology (الصوتيات)  → 3 engines
```

**3-Level Taxonomy**: Layer → Group (30 total) → Subgroup (66+)

📘 **[See HIERARCHY_README.md](HIERARCHY_README.md)** for complete navigation guide  
📚 **[See ENGINE_TAXONOMY.md](ENGINE_TAXONOMY.md)** for detailed classification

---

## ✨ Features

### Phase 1 (C1): Text Encoding & Normalization
- Unicode normalization (NFC/NFD)
- Diacritic preservation
- Character encoding standardization
- Orthographic adaptation

### Phase 2 (C2a): Phonological Gates (Tajweed Rules)
1. **GateSukun**: Double sukun repair
2. **GateShadda**: Gemination expansion
3. **GateHamza**: Hamza placement rules
4. **GateWaqf**: Pause and stop rules
5. **GateIdgham**: Assimilation with ghunnah
6. **GateMadd**: Vowel lengthening
7. **GateDeletion**: Alif/hamza deletion
8. **GateEpenthesis**: Vowel insertion

### Phase 3 (C2b): Morphological Analysis
- **Root Extraction**: Trilateral and quadrilateral roots
- **Pattern Matching**: 25+ morphological templates
- **Verb Forms**: Recognition of Forms I-X
- **Weak Roots**: Special handling for و, ي, ء
- **Noun Patterns**: Singular, plural, broken plurals
- **Participles**: Active and passive forms

---

## 🏗️ Hierarchical Grammar Engine System

### Explore the Hierarchy
Use the built-in CLI tool to navigate 66 engines:

```bash
# Show full tree
python engine_hierarchy.py

# Filter by layer
python engine_hierarchy.py --layer 2     # Morphology engines

# Search by term
python engine_hierarchy.py --search "فاعل"

# Show statistics
python engine_hierarchy.py --stats

# Export to JSON
python engine_hierarchy.py --export json
```

### Example Output
```
📂 Layer 1: PHONOLOGY (الصوتيات)
  └─ Group 1.1: Core Phonemes (الفونيمات الأساسية)
      └─ 1.1.1: Phoneme Inventory (قائمة الفونيمات)
          • PhonemesEngine

📂 Layer 2: MORPHOLOGY (الصرف)
  └─ Group 2.1: Verbal Morphology (صرف الأفعال)
      └─ 2.1.1: Basic Verbs (الأفعال الأساسية)
          • VerbsEngine
          • AfaalKhamsaEngine
```

**See [HIERARCHY_README.md](HIERARCHY_README.md) for complete guide**

---

## 🚀 Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/sonaiso/Eqratech_Hussein_Hiyassat_Project.git
cd Eqratech_Hussein_Hiyassat_Project

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests to verify installation
PYTHONPATH=src pytest tests/ -v
💻 Usage
Command Line Interface
Basic Usage
bash
# Simple text analysis
python -m fvafk.cli "كَاتِبٌ"

# With morphological analysis
python -m fvafk.cli "كَاتِبٌ" --morphology

# JSON output
python -m fvafk.cli "كَاتِبٌ" --morphology --json

# Verbose output with timing
python -m fvafk.cli "كَاتِبٌ" --morphology --verbose
