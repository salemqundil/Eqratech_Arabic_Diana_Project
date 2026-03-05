# How to Test on Your Machine

This guide shows you how to set up the project and run the test suite locally.

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | **3.10 or later** |
| Git | any recent version |

---

## 1. Clone & Install

```bash
# Clone the repository
git clone https://github.com/sonaiso/Eqratech_Hussein_Hiyassat_Project.git
cd Eqratech_Hussein_Hiyassat_Project

# (Recommended) Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install the package together with all test dependencies
pip install -e ".[dev]"
```

> **Alternative** (without editable install):
> ```bash
> pip install -r requirements-dev.txt
> ```

---

## 2. Run All Tests

```bash
pytest
```

Expected output: **all tests pass, 0 errors**.

The test runner is pre-configured via `pytest.ini`:
- `testpaths = tests` — only the `tests/` directory is scanned
- `pythonpath = src .` — `src/` and the repo root are on `PYTHONPATH` automatically
- `addopts = -v --tb=short` — verbose output with short tracebacks

---

## 3. Run Tests by Area

```bash
# Phonological gates
pytest tests/test_gate_sukun.py -v
pytest tests/test_gate_shadda.py -v
pytest tests/test_gate_*.py -v       # all gate tests

# Morphological analysis (C2b)
pytest tests/c2b/ -v

# Syntax theory
pytest tests/syntax/ -v
pytest tests/test_syntax_theory.py -v

# Enrichment pipeline (operators catalog)
pytest tests/test_enrich_operators_catalog.py -v

# CLI smoke tests
pytest tests/test_cli.py -v
```

---

## 4. Run a Single Test

```bash
pytest tests/test_gate_sukun.py::test_gate_sukun_repairs_double_sukun -v
```

---

## 5. Run with Coverage

```bash
pytest --cov=src --cov-report=term-missing
```

---

## 6. Smoke-Test the CLI

After installing, the `fvafk` command is available:

```bash
# Basic phonological analysis
fvafk "كِتَاب"

# JSON output
fvafk "كِتَاب" --json

# With morphology
fvafk "كَاتِبٌ" --morphology --json
```

Or via `python -m`:

```bash
python -m fvafk.cli "كِتَاب" --json
```

---

## 7. Smoke-Test the Enrichment Script

```bash
python scripts/enrich_operators_catalog.py
```

Expected output:
```
Reading input: …/data/operators_catalog_split.csv
Loading Quran i3rab evidence: …/data/i3rab/quran_i3rab.csv
Enriching rows …
Writing CSV: …/data/operators_catalog_split_enriched.csv
Writing JSONL: …/data/operators_catalog_split_enriched.jsonl
Done.
```

---

## 8. Troubleshooting

### `ModuleNotFoundError: No module named 'fvafk'`

Make sure you installed with `pip install -e ".[dev]"` **from the repo root**, or that `src/` is on your Python path:

```bash
PYTHONPATH=src pytest
```

### `command not found: pytest`

Your virtual environment may not be activated, or pytest was not installed:

```bash
source .venv/bin/activate
pip install pytest
```

### Tests were collected but import errors appear

Ensure you are using **Python 3.10 or later**:

```bash
python --version
```

### On Windows — `source .venv/bin/activate` fails

Use the Windows activation instead:

```cmd
.venv\Scripts\activate
```

---

## Related Documents

| Document | Purpose |
|----------|---------|
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Code standards, adding engines/gates, PR workflow |
| [`INSTALLATION_GUIDE.md`](INSTALLATION_GUIDE.md) | Coq formal-proof compilation |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | System architecture overview |
| [`pytest.ini`](pytest.ini) | pytest configuration |
