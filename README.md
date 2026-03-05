# Eqratech_Arabic_Diana_Project

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/salemqundil/Eqratech_Arabic_Diana_Project/blob/main/Eqratech_Arabic_Colab.ipynb)

**Package**: `bayan-fvafk` v0.1.0 | **Tests**: 497+ passing | **Python**: 3.10+

## مشروع إقرأتك العربية - ديانا
مشروع معالجة اللغة الطبيعية العربية يحتوي على جميع الأدوات العربية والأفعال والأسماء

## Quick Start with Google Colab / البدء السريع مع Google Colab

Click the badge above to open this project in Google Colab and start using it immediately without any installation!

انقر على الشارة أعلاه لفتح هذا المشروع في Google Colab والبدء في استخدامه فوراً بدون أي تثبيت!

## Local Installation / التثبيت المحلي

```bash
# Clone the repository
git clone https://github.com/salemqundil/Eqratech_Arabic_Diana_Project.git
cd Eqratech_Arabic_Diana_Project

# Install dependencies
pip install -r requirements.txt

# Run the server (optional)
python run_server.py
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

### Run tests

```bash
PYTHONPATH=src pytest -q
```

> 📖 See **[TESTING.md](TESTING.md)** for the full local-testing guide (virtual-env setup, running by area, coverage, CLI smoke tests, and troubleshooting).

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

### Operators catalog (C2B)

If `data/operators_catalog_split_enriched.csv` exists, it is used automatically; otherwise the plain `operators_catalog_split.csv` is used. To generate the enriched catalog: `PYTHONPATH=src python -m fvafk.c2b.read_inputs_for_enrichment_pipeline`

---

## 📁 Project Structure

```
Eqratech_Hussein_Hiyassat_Project/
├── app/                    # Application layer (Pydantic models, FastAPI)
│   ├── models/             # Type-safe data models
│   └── api/                # API endpoints (Sprint 6)
├── web_app/                # FastAPI web application (run_server.py entry point)
│   ├── __init__.py
│   └── main.py             # GET /, GET /health, POST /analyse
├── src/fvafk/              # Core pipeline
│   ├── c1/                 # Encoding layer
│   ├── c2a/                # Phonology layer (gates)
│   ├── c2b/                # Morphology layer (roots, patterns)
│   ├── syntax/             # Syntax layer (links, constraints)
│   ├── cli/                # Command-line interface
│   ├── phonology_v2/       # Enhanced phonology engine
│   └── __init__.py
├── tests/                  # Test suite (497+ tests)
├── docs/                   # Documentation
│   ├── CLI_SCHEMA.md       # CLI output reference
│   └── MASTER_PLAN_CHECKLIST.md
├── theories/               # Formal theories (Coq)
├── pyproject.toml          # Package metadata
└── pytest.ini              # Test configuration
```

---

## 📊 Development Status

**Current Sprint**: Sprint 5 (Web API & Advanced Integration)

### Completed ✅
- ✅ **Task 1.1**: pyproject.toml with package metadata
- ✅ **Task 1.2**: Package modules as typed library (bayan-fvafk)
- ✅ **Task 1.3**: Pydantic models (7 models)
- ✅ **Task 1.4**: OrthographyAdapter + FormCodecV2 integration
- ✅ **Task 1.5**: Directory alignment (app/, theories/)
- ✅ **Task 1.6**: Documentation updates
- ✅ **Task 1.7**: CLI with syntax output (WordForm + ISNADI links)
- ✅ **Task 1.8**: Comprehensive CLI tests
- ✅ **Task 1.9**: CLI schema documentation
- ✅ **Sprint 2**: Phonology gates unification, syllabifier, property tests, Coq skeletons
- ✅ **Sprint 3**: Morphological corpus, evaluation metrics, i3rab loader
- ✅ **Sprint 4**: Syntax theory, maqam theory gates, syntax graph generators

### In Progress ⏳
- ⏳ Web API (`web_app/`) — basic FastAPI app available; full endpoint coverage ongoing

See [ENHANCED_ROADMAP.md](ENHANCED_ROADMAP.md) for complete plan.

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [CLI_SCHEMA.md](docs/CLI_SCHEMA.md) | Complete CLI output reference |
| [MASTER_PLAN_CHECKLIST.md](docs/MASTER_PLAN_CHECKLIST.md) | Detailed task checklist |
| [ENHANCED_ROADMAP.md](ENHANCED_ROADMAP.md) | 6-sprint development plan |
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | Current progress vs. plan |

- Comprehensive Arabic grammar engines / محركات قواعد عربية شاملة
- Phoneme and morphology analysis / تحليل الفونيمات والصرف
- Sentence generation / توليد الجمل
- Multi-layer grammar export / تصدير القواعد متعددة الطبقات
- Google Colab integration / التكامل مع Google Colab
