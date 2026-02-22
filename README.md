# Bayan / FVAFK — Arabic NLP Pipeline

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-498%20passing-brightgreen)](tests/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Package](https://img.shields.io/badge/package-bayan--fvafk%20v0.1.0-orange)](pyproject.toml)

A comprehensive Arabic NLP pipeline implementing a formal 6-layer linguistic architecture:
**phonology → morphology → lexicon → syntax → rhetoric → generation**.

---

## 🎯 Overview

The **FVAFK** (*Formal Verification Arabic Formal Knowledge*) pipeline processes diacritized Arabic text through three main phases and an optional enhanced phonology engine:

| Phase | Code | Description |
|-------|------|-------------|
| Encoding & Normalization | **C1** | Unicode normalization, orthographic standardization |
| Phonological Gates | **C2a** | 10 Tajweed-based transformation gates |
| Morphological Analysis | **C2b** | Root extraction and pattern matching |
| Syntactic Analysis | **C3** | ISNADI link detection (مبتدأ–خبر) |
| Phonology V2 *(optional)* | — | Syllable-lattice VC classification with witnesses |

---

## 🏗️ Project Structure

```
Eqratech_Hussein_Hiyassat_Project/
│
├── src/                            # All installable source code
│   ├── fvafk/                      # Core pipeline (pip-installable)
│   │   ├── c1/                     # C1: Text encoding & normalization
│   │   ├── c2a/                    # C2a: Phonological gates (Tajweed)
│   │   │   └── gates/              # 10 gate implementations
│   │   ├── c2b/                    # C2b: Morphological analysis
│   │   │   ├── morpheme.py         # Root & pattern types
│   │   │   ├── root_extractor.py   # Trilateral / quadrilateral roots
│   │   │   ├── pattern_matcher.py  # 25+ morphological templates
│   │   │   └── syllabifier.py      # Arabic syllabifier
│   │   ├── syntax/                 # C3: Syntactic links
│   │   │   └── linkers/            # ISNADI linker (v1, v1.1)
│   │   ├── phonology_v2/           # Enhanced syllable-lattice engine
│   │   ├── cli/                    # `python -m fvafk.cli` entry-point
│   │   └── __init__.py             # Package public API
│   │
│   ├── engines/                    # Linguistic data engines (66 engines)
│   │   ├── base.py                 # BaseReconstructionEngine + EngineLayer
│   │   ├── phonology/              # Layer 1: Phonology engines
│   │   ├── morphology/             # Layer 2: Morphology engines (22)
│   │   ├── lexicon/                # Layer 3: Lexicon engines (15)
│   │   ├── syntax/                 # Layer 4: Syntax engines (13)
│   │   ├── rhetoric/               # Layer 5: Rhetoric engines (11)
│   │   └── generation/             # Layer 6: Generation engines
│   │
│   ├── maqam_theory/               # Maqam constraint-optimization gates
│   │   ├── gates/                  # 12 gate implementations
│   │   ├── minimizers/             # Energy minimizers (arg min E)
│   │   ├── proofs/                 # 11 formal theorems
│   │   └── structures/             # MaqamVector, ScopeGraph, BindingMap
│   │
│   ├── syntax_theory/              # Graph-based syntactic analysis
│   │   ├── structures/             # SyntacticInput, SyntacticGraph
│   │   ├── relations/              # ISN, TADMN, TAQYID relations
│   │   ├── operators/              # 14 grammatical operators
│   │   ├── generators/             # CanonicalConstructor + CandidateGenerator
│   │   ├── minimizers/             # Multi-component energy function
│   │   └── proofs/                 # Mechanized syntactic proofs
│   │
│   └── theory/                     # Abstract mathematical theory
│
├── app/                            # Application layer
│   ├── models/                     # Pydantic v2 data models (7 models)
│   └── api/                        # FastAPI endpoints (Sprint 6)
│
├── web_app/                        # FastAPI web application
│   └── main.py                     # GET /health · POST /analyze
│
├── tests/                          # Test suite (498 tests)
│   ├── c2b/                        # Morphological analysis tests
│   ├── syntax/                     # Syntax layer tests
│   └── test_*.py                   # Unit + integration tests
│
├── docs/                           # Documentation
│   ├── CLI_SCHEMA.md               # Full CLI JSON output reference
│   ├── ARCHITECTURE.md             # Architecture deep-dive
│   ├── MIGRATION_GUIDE.md          # Migration notes
│   ├── PHONOLOGY.md                # Phonology system documentation
│   └── ...                         # Sprint plans, task audits
│
├── data/                           # Reference data
│   ├── i3rab/                      # Quranic I'rab dataset
│   └── awzan_merged_final.csv      # Morphological patterns
│
├── coq/                            # Coq formal proofs (gates)
├── coq_proofs/                     # Additional Coq verification
├── examples/                       # Usage examples
├── notebooks/                      # Jupyter notebooks
├── scripts/                        # Build / data-preparation scripts
├── tools/                          # Development / analysis utilities
├── theories/                       # Standalone formal theories
│
├── *_engine.py                     # Legacy re-export wrappers (backward compat)
├── reconstruction_utils.py         # DataFrame normalization utility
├── Main_engine.py                  # Auto-discovery grammar exporter
├── run_server.py                   # Web server launcher
│
├── pyproject.toml                  # Package metadata & build config
├── setup.py                        # Legacy setuptools config
├── pytest.ini                      # Test configuration
├── .gitattributes                  # Line-ending policy (LF everywhere)
└── README.md                       # This file
```

---

## 🚀 Installation

### Prerequisites
- Python **3.10+**
- pip

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/sonaiso/Eqratech_Hussein_Hiyassat_Project.git
cd Eqratech_Hussein_Hiyassat_Project

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

# 3. Install package with all dependencies
pip install -e ".[dev]"

# 4. Verify installation
python -c "import fvafk; print(f'FVAFK v{fvafk.__version__}')"

# 5. Run the test suite
pytest
```

### Runtime dependencies only (no dev tools)

```bash
pip install -e .
```

---

## 💻 Usage

### Command-Line Interface

```bash
# Basic analysis (C1 + C2a)
python -m fvafk.cli "كِتَاب"

# JSON output
python -m fvafk.cli "كِتَاب" --json

# Full morphological analysis (C1 + C2a + C2b + syntax)
python -m fvafk.cli "كَاتِبٌ" --morphology --json

# Phonology V2 — syllable-lattice engine
python -m fvafk.cli "كِتَاب" --json --phonology-v2

# Phonology V2 with syllabification details
python -m fvafk.cli "كِتَاب" --json --phonology-v2 --phonology-v2-details

# Full output with VC witnesses (decision traces)
python -m fvafk.cli "كِتَاب" --json --phonology-v2 --phonology-v2-details --phonology-v2-witnesses
```

See [`docs/CLI_SCHEMA.md`](docs/CLI_SCHEMA.md) for the complete JSON output schema.

### Python API

```python
from fvafk.c1 import C1Encoder
from fvafk.c2a import GateFramework, GateSukun, GateShadda, GateHamza
from fvafk.c2b import RootExtractor, PatternMatcher

# C1: Encode text
encoder = C1Encoder()
units = encoder.encode("كَاتِبٌ")

# C2a: Apply phonological gates
gates = [GateSukun(), GateShadda(), GateHamza()]
framework = GateFramework(gates)
gate_results = framework.apply(units)

# C2b: Morphological analysis
root = RootExtractor().extract("كَاتِبٌ")   # → Root(letters=('ك','ت','ب'), type=TRILATERAL)
pattern = PatternMatcher().match("كَاتِبٌ") # → Pattern(template='فَاعِل', type='active_participle')
```

### Web API

```bash
# Start the server
python run_server.py --host 127.0.0.1 --port 8000

# Health check
curl http://localhost:8000/health

# Analyze Arabic text
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "كِتَاب", "morphology": false}'
```

Interactive API docs available at `http://localhost:8000/docs`.

---

## 🔬 Phonological Gates (C2a)

| Gate | Arabic | Description |
|------|--------|-------------|
| `GateSukun` | السكون | Double-sukun repair |
| `GateShadda` | الشدة | Gemination expansion |
| `GateHamza` | الهمزة | Hamza placement |
| `GateWaqf` | الوقف | Pause rules |
| `GateIdgham` | الإدغام | Assimilation with ghunnah |
| `GateMadd` | المد | Vowel lengthening |
| `GateDeletion` | الحذف | Alif/hamza deletion |
| `GateEpenthesis` | الإشباع | Vowel insertion |
| `GateWasl` | الوصل | Hamzat al-wasl |
| `GateTanwin` | التنوين | Tanwin assimilation |

---

## 🧪 Testing

```bash
# Run the full test suite
pytest

# Verbose output
pytest -v

# Specific layer
pytest tests/c2b/         # Morphology tests
pytest tests/syntax/      # Syntax tests

# With coverage
pytest --cov=src --cov-report=html
```

**Current status**: **498 tests passing**, 0 failing, 0 skipped.

---

## 📊 Architecture: 6-Layer Linguistic Model

```
Layer 6: Generation  (التوليد)   → Sentence production from components
Layer 5: Rhetoric    (البلاغة)   → Figurative language & discourse
Layer 4: Syntax      (النحو)     → Grammatical relations & structure
Layer 3: Lexicon     (المعجم)    → Vocabulary & semantic classification
Layer 2: Morphology  (الصرف)    → Word structure & patterns
Layer 1: Phonology   (الصوتيات) → Sound units & prosody
```

**66 engines** are organized under this hierarchy in `src/engines/`. See [`docs/ENGINE_TAXONOMY.md`](docs/ENGINE_TAXONOMY.md) for the complete catalog.

---

## 📚 Documentation Index

| Document | Location | Description |
|----------|----------|-------------|
| CLI JSON Schema | [`docs/CLI_SCHEMA.md`](docs/CLI_SCHEMA.md) | Complete CLI output reference |
| Architecture | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Deep-dive into the 6-layer model |
| Engine Taxonomy | [`docs/ENGINE_TAXONOMY.md`](docs/ENGINE_TAXONOMY.md) | Catalog of all 66 engines |
| Phonology Guide | [`docs/PHONOLOGY.md`](docs/PHONOLOGY.md) | Phonological system |
| Migration Guide | [`docs/MIGRATION_GUIDE.md`](docs/MIGRATION_GUIDE.md) | V1 → V2 migration notes |
| Project Review | [`docs/PROJECT_REVIEW.md`](docs/PROJECT_REVIEW.md) | Code quality audit report |
| Roadmap | [`docs/ENHANCED_ROADMAP.md`](docs/ENHANCED_ROADMAP.md) | 6-sprint development plan |
| Changelog | [`CHANGELOG.md`](CHANGELOG.md) | Release history |
| Contributing | [`CONTRIBUTING.md`](CONTRIBUTING.md) | How to contribute |

---

## 🤝 Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines on:
- Setting up the development environment
- Code style and conventions
- Running tests before submitting
- Branch and PR workflow

---

## 📄 License

This project is licensed under the **MIT License** — see the
[`pyproject.toml`](pyproject.toml) for details.

---

## 👤 Author

**Hussein Hiyassat** — Arabic computational linguistics researcher.


