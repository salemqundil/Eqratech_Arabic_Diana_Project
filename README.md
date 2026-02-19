# FVAFK / Bayan - Arabic NLP Pipeline

A production-ready Arabic NLP system implementing a comprehensive FVAFK pipeline for Arabic text processing: encoding/CV (C1), phonological gates (C2a), morphology (C2b), and syntax (C3) — with an optional **Phonology V2** engine (syllable lattice + witnesses).

**Package**: `bayan-fvafk` v0.1.0 | **Tests**: 282 passing | **Python**: 3.10+

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

### Package Installation

```bash
# Install as editable package
pip install -e .

# Verify installation
python -c "import fvafk; print(f'FVAFK v{fvafk.__version__}')"

# Run tests
pytest
```

### From PyPI (future)

```bash
pip install bayan-fvafk
```

```bash
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

---

## 📁 Project Structure

```
Eqratech_Hussein_Hiyassat_Project/
├── app/                    # Application layer (Pydantic models, FastAPI)
│   ├── models/             # Type-safe data models
│   └── api/                # API endpoints (Sprint 6)
├── src/fvafk/              # Core pipeline
│   ├── c1/                 # Encoding layer
│   ├── c2a/                # Phonology layer (gates)
│   ├── c2b/                # Morphology layer (roots, patterns)
│   ├── syntax/             # Syntax layer (links, constraints)
│   ├── cli/                # Command-line interface
│   ├── phonology_v2/       # Enhanced phonology engine
│   └── __init__.py
├── tests/                  # Test suite (282 tests)
├── docs/                   # Documentation
│   ├── CLI_SCHEMA.md       # CLI output reference
│   └── MASTER_PLAN_CHECKLIST.md
├── theories/               # Formal theories (Coq)
├── pyproject.toml          # Package metadata
└── pytest.ini              # Test configuration
```

---

## 📊 Development Status

**Current Sprint**: Sprint 1 (Foundation and Packaging)

### Completed ✅
- ✅ **Task 1.1**: pyproject.toml with package metadata
- ✅ **Task 1.2**: Package modules as typed library (bayan-fvafk)
- ✅ **Task 1.5**: Directory alignment (app/, theories/)
- ✅ **Task 1.6**: Documentation updates
- ✅ **Task 1.7**: CLI with syntax output (WordForm + ISNADI links)
- ✅ **Task 1.8**: 13 comprehensive CLI tests (29 total)
- ✅ **Task 1.9**: CLI schema documentation

### In Progress ⏳
- ⏳ **Task 1.3**: Pydantic models (7 models)
- ⏳ **Task 1.4**: OrthographyAdapter + FormCodecV2 integration

### Next: Sprint 2 🎯
- Phonology gates unification
- Reference syllabifier
- Property tests with Hypothesis
- Coq skeletons (GateSukun, GateShadda, GateTanwin)

See [ENHANCED_ROADMAP.md](ENHANCED_ROADMAP.md) for complete plan.

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [CLI_SCHEMA.md](docs/CLI_SCHEMA.md) | Complete CLI output reference |
| [MASTER_PLAN_CHECKLIST.md](docs/MASTER_PLAN_CHECKLIST.md) | Detailed task checklist |
| [ENHANCED_ROADMAP.md](ENHANCED_ROADMAP.md) | 6-sprint development plan |
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | Current progress vs. plan |

