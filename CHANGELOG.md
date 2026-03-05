# Changelog

All notable changes to **bayan-fvafk** are documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).  
Versions follow [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Added
- `web_app/` FastAPI application (`GET /`, `GET /health`, `POST /analyse`)
- `CHANGELOG.md` and `CONTRIBUTING.md`
- CLI input-length guard (max 10 000 characters)

### Fixed
- Migrated all `app/models/*.py` from deprecated `class Config` to `model_config = ConfigDict(...)` (Pydantic V2)
- Removed duplicate `ci.yml` from repo root (only `.github/workflows/ci.yml` is active)
- Fixed dead-code `if … pass` in `Main_engine._iter_engine_modules` — now uses `continue`
- Added `@lru_cache` to `reconstruction_utils.load_maps()` to avoid repeated imports
- `colabcode.py`: graceful error when PyTorch is not installed
- `pyproject.toml`: added `fastapi`, `uvicorn`, `pandas`, `openpyxl` to `dependencies`
- `requirements.txt`: added `numpy`, `pydantic` to align with `pyproject.toml`
- Removed `setup.py` (conflicted with `pyproject.toml`; listed `pytest` as runtime dep)
- `~$full_multilayer_grammar.xlsx` untracked (already covered by `.gitignore ~$*`)
- `connect.ipynb` moved to `notebooks/`

### Changed
- `README.md`: updated test count to 497+, Sprint status to Sprint 5

---

## [0.1.0] — 2026-01-15

### Added
- Initial package release: `bayan-fvafk`
- C1 encoding layer (`FormCodecV2`, `C1Encoder`)
- C2a phonology layer: 10 Tajweed gates (Sukun, Shadda, Wasl, Hamza, Waqf, Idgham, Madd, Assimilation, Tanwin, Deletion, Epenthesis)
- C2b morphology layer: root extractor (trilateral/quadrilateral), pattern matcher (25+ templates)
- Syntax layer: WordForm + ISNADI link detection
- Phonology V2 engine: syllable lattice + witnesses
- Maqam Theory: 12 gates (interrogative, vocative, imperative, exclamative, declarative, etc.)
- Syntax Theory: graph-based analysis (ISN/TADMN/TAQYID)
- 66 linguistic engines across 6 layers (Phonology → Generation)
- Coq formal proofs: GateSukun, GateShadda, GateTanwin
- CLI: `python -m fvafk.cli`
- FastAPI app skeleton (`app/`)
- 497 passing tests (unit + integration + property-based)
- `pyproject.toml` package metadata

[Unreleased]: https://github.com/sonaiso/Eqratech_Hussein_Hiyassat_Project/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/sonaiso/Eqratech_Hussein_Hiyassat_Project/releases/tag/v0.1.0
