# Contributing to Bayan / FVAFK

Thank you for your interest in contributing to the Bayan Arabic NLP pipeline!

---

## 🛠️ Development Setup

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/Eqratech_Hussein_Hiyassat_Project.git
cd Eqratech_Hussein_Hiyassat_Project

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
# .venv\Scripts\activate    # Windows

# 3. Install with dev dependencies
pip install -e ".[dev]"

# 4. Verify everything works
pytest
```

---

## 🧪 Running Tests

```bash
# Full suite
pytest

# Only unit tests
pytest tests/c2b/ tests/syntax/

# With coverage report
pytest --cov=src --cov-report=html

# Only tests matching a keyword
pytest -k "root_extractor"
```

All **498 tests** must pass before submitting a pull request.
No new warnings should be introduced.

---

## 📐 Code Style

- **Python 3.10+** — use type hints on all public functions and classes.
- Follow **PEP 8** (4-space indentation, max 100 chars per line).
- Use `from __future__ import annotations` in every new module.
- All strings should use **double quotes**.
- Keep line endings **LF** (enforced by `.gitattributes`).

### Naming conventions

| Item | Convention | Example |
|------|-----------|---------|
| Classes | `PascalCase` | `RootExtractor` |
| Functions / methods | `snake_case` | `extract_root()` |
| Constants | `UPPER_SNAKE` | `MAX_ROOT_LENGTH` |
| Private | leading `_` | `_load_csv()` |

---

## 🗂️ Project Layout

All new **library** code goes under `src/` — never in the root directory.

| Where to add | What to add |
|--------------|-------------|
| `src/fvafk/c1/` | Encoding / normalization code |
| `src/fvafk/c2a/gates/` | New phonological gates |
| `src/fvafk/c2b/` | Morphological analysis |
| `src/fvafk/syntax/` | Syntax / linking code |
| `src/engines/<layer>/` | New linguistic data engines |
| `src/maqam_theory/gates/` | New Maqam constraint gates |
| `tests/` | Tests mirroring `src/` structure |
| `docs/` | Documentation files (.md) |

---

## 🔀 Branch and PR Workflow

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feat/my-feature
   ```
2. Make your changes with **small, focused commits**.
3. Ensure all tests pass:
   ```bash
   pytest
   ```
4. Open a pull request against `main`.
5. Fill in the PR template: describe the change, link related issues.

### Branch naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feat/…` | `feat/gate-tanwin` |
| Bug fix | `fix/…` | `fix/cli-subprocess-env` |
| Documentation | `docs/…` | `docs/architecture` |
| Refactor | `refactor/…` | `refactor/engine-base` |
| Sprint | `sprint<N>/…` | `sprint2/gate-unification` |

---

## ✅ Checklist for new features

- [ ] All new public functions have **type hints** and a **docstring**
- [ ] New tests added under `tests/` covering both happy and error paths
- [ ] `pytest` passes with **0 failures and 0 new warnings**
- [ ] New documentation added to `docs/` if applicable
- [ ] `CHANGELOG.md` updated under `[Unreleased]`

---

## ➕ Adding a new linguistic engine

1. Place the engine in `src/engines/<layer>/your_engine.py`
2. Inherit from the appropriate base class:
   ```python
   from engines.base import MorphologyEngine, EngineLayer

   class YourEngine(MorphologyEngine):
       SHEET_NAME = "اسم_قصير"   # ≤ 31 chars (Excel limit)
       LAYER = EngineLayer.MORPHOLOGY
       GROUP = "2.1"
       SUBGROUP = "2.1.3"

       @classmethod
       def make_df(cls):
           ...
   ```
3. Export from `src/engines/<layer>/__init__.py`
4. Add the root-level backward-compat wrapper:
   ```python
   # root/your_engine.py
   from engines.<layer>.your_engine import YourEngine  # noqa: F401
   ```
5. Run `pytest` and verify the engine is discoverable:
   ```bash
   PYTHONPATH=src python engine_hierarchy.py --search YourEngine
   ```

---

## ➕ Adding a new Maqam gate

1. Create `src/maqam_theory/gates/your_gate.py`
2. Inherit from `BaseGate` and implement three required methods:
   `can_activate`, `compute_satisfaction`, `compute_cost`
3. Add at least two tests:
   - one hard-fail scenario (cost → ∞)
   - one soft-penalty scenario (finite cost)
4. Export from `src/maqam_theory/gates/__init__.py`

---

## 🐛 Reporting Bugs

Please open a GitHub issue including:

1. Python version (`python --version`)
2. Steps to reproduce
3. Expected vs. actual output
4. Traceback if applicable

---

## 📬 Questions

Open a GitHub Discussion or contact the maintainer.
