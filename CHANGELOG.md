# Changelog

All notable changes to **Bayan / FVAFK** are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Added
- `web_app/main.py` — FastAPI application with `GET /health` and `POST /analyze`
  endpoints, making `run_server.py` fully operational.
- `CONTRIBUTING.md` — development setup, code style, branch workflow, and
  checklists for adding new engines and gates.
- `CHANGELOG.md` — this file.
- `docs/ARCHITECTURE.md` — deep-dive into the 6-layer linguistic architecture.
- `.gitattributes` — enforces LF line endings for all text files; CRLF for
  `.bat`/`.ps1` scripts.

### Changed
- **README.md** — full rewrite: accurate test count (498), comprehensive project
  structure tree, Python API examples, Web API examples, and docs index.
- **Markdown organization** — 23 documentation files moved from root into `docs/`
  so only `README.md`, `CONTRIBUTING.md`, and `CHANGELOG.md` remain at root.
- **`pyproject.toml`** — added `fastapi`, `uvicorn`, `pandas`, `openpyxl` to
  `[project.dependencies]`; removed `pytest`/`pytest-cov` from runtime deps.
- **`.gitignore`** — added `dist/`, `build/`, `*.egg-info/`, `.pytest_cache/`,
  `.coverage`, `htmlcov/`, and Microsoft Office temp files (`~$*`).

### Fixed
- **`maqam_space.py`** — `DU'A` (apostrophe in identifier) caused a
  `SyntaxError`; renamed to `DUA`.
- **4 root-level engine wrappers** — orphaned class-body code (CRLF artefact)
  reduced to single re-export line.
- **`search_words.py`** — bare `except:` replaced with `except ValueError:`.
- **`tests/test_cli_comprehensive.py`** — 12 tests were failing because
  `["python3", ...]` subprocess calls used a stripped env without `PYTHONPATH`.
  Fixed with `[sys.executable, ..., env={**os.environ, "PYTHONPATH": "src"}]`.
- **16 subprocess calls** across 4 test files — all `env={"PYTHONPATH": "src"}`
  replaced with `env={**os.environ, "PYTHONPATH": "src"}`.
- **`fvafk.phonology_v2`** — exported `PhonologyV2Adapter`; resolved circular
  import by moving the import after `analyze_word` definition.
- **`tests/test_syllabifier_vs_phonology_v2.py`** — added missing
  `PhonologyV2Adapter` import so the previously-skipped test now passes.
- **Pydantic V2 deprecations** — replaced `class Config` with
  `model_config = ConfigDict(...)` across all 7 `app/models/` files.
- **55 Python files** converted from Windows CRLF to LF.
- **`run_server.py`** docstring typo: `"python run_server.pyif"` → `"if"`.
- **`setup.py`** — removed `pytest`/`pytest-cov` from `install_requires`.
- **`requirements.txt`** — added missing `numpy>=1.20.0`.
- **CI workflows** — merged `python-tests.yml` into `ci.yml`; replaced
  `requirements.txt`-based install with `pip install -e ".[dev]"`.
- **Missing `__init__.py`** files added in `src/maqam_theory/proofs/` and
  `tests/c2b/`.

---

## [0.1.0] — 2026-01-30

### Added
- Initial release of the FVAFK / Bayan Arabic NLP pipeline.
- **C1** encoding layer with Unicode normalization and orthographic adaptation.
- **C2a** phonological gates (10 Tajweed-based transformations):
  GateSukun, GateShadda, GateHamza, GateWaqf, GateIdgham, GateMadd,
  GateDeletion, GateEpenthesis, GateWasl, GateTanwin.
- **C2b** morphological analysis: root extraction (trilateral & quadrilateral)
  and pattern matching (25+ templates, Forms I–X).
- **C3** syntactic analysis: ISNADI linker (مبتدأ–خبر detection).
- **Phonology V2** optional engine: syllable-lattice VC classification with
  witnesses and decision traces.
- **CLI** (`python -m fvafk.cli`) with `--json`, `--morphology`,
  `--phonology-v2`, `--phonology-v2-details`, `--phonology-v2-witnesses` flags.
- **Pydantic v2 models** in `app/models/`: Unit, Syllable, WordForm, Link,
  Evidence, ProofArtifact, AnalysisResult.
- **66 linguistic engines** organized in 6-layer hierarchy under `src/engines/`.
- **12 Maqam Theory gates** with formal energy-minimization framework.
- **Coq skeletons** for GateSukun, GateShadda, GateTanwin.
- `pyproject.toml` with `[project.scripts]` entry-point `fvafk`.
- Comprehensive test suite with **pytest** and **Hypothesis** property tests.

---

[Unreleased]: https://github.com/sonaiso/Eqratech_Hussein_Hiyassat_Project/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/sonaiso/Eqratech_Hussein_Hiyassat_Project/releases/tag/v0.1.0
