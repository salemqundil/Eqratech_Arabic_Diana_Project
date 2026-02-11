A production-ready Arabic NLP system implementing a three-stage FVAFK pipeline for Arabic text processing: encoding/CV (C1), phonological gates (C2a), and morphology (C2b) — with an optional **Phonology V2** engine (syllable lattice + witnesses).

---

## 🎯 Overview

This project implements a comprehensive Arabic language processing pipeline capable of:

- **Text Normalization**: Unicode normalization and orthographic standardization
- **Phonological Processing**: 10 Tajweed-based gates for accurate phonetic analysis
- **Morphological Analysis**: Root extraction and pattern matching for Arabic words
- **High Performance**: Sub-millisecond processing on typical inputs
- **Production Ready**: Comprehensive unit + integration test suite

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

## 🚀 Installation

### Prerequisites
- Python 3.10+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/sonaiso/Eqratech_Hussein_Hiyassat_Project.git
cd Eqratech_Hussein_Hiyassat_Project

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run tests

```bash
PYTHONPATH=src pytest -q
```

---

## 💻 Usage (CLI)

### Basic analysis

```bash
PYTHONPATH=src python -m fvafk.cli "كِتَاب"
```

### JSON output

```bash
PYTHONPATH=src python -m fvafk.cli "كِتَاب" --json
```

### Morphology

```bash
PYTHONPATH=src python -m fvafk.cli "كَاتِبٌ" --morphology --json
```

### Phonology V2 (optional)

```bash
# Use Phonology V2 for CV analysis
PYTHONPATH=src python -m fvafk.cli "كِتَاب" --json --phonology-v2

# Add detailed syllabification output
PYTHONPATH=src python -m fvafk.cli "كِتَاب" --json --phonology-v2 --phonology-v2-details

# Include witnesses (decision traces)
PYTHONPATH=src python -m fvafk.cli "كِتَاب" --json --phonology-v2 --phonology-v2-details --phonology-v2-witnesses
```

See `docs/MIGRATION_GUIDE.md` for migration notes and JSON schema details.
