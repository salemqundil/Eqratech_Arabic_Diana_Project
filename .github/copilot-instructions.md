# Copilot agent instructions for Eqratech_Arabic_Diana_Project

Purpose: Arabic grammar engines + BERT training for Arabic phoneme processing, with an optional FastAPI web API.

## Big picture
- Two subsystems:
  1) Rule‑based “engines” that generate pandas DataFrames of Arabic grammar artifacts and export to Excel/CSV.
  2) ML pipeline to train a BERT model using a custom UTF‑8 phoneme tokenizer.
- Data flows: engines -> CSV/Excel (e.g., `full_multilayer_grammar.csv`) -> tokenizer/datasets -> BERT training outputs under `./output/`.

## Key components and files
- Engines: many `*_engine.py` modules. Each engine typically:
  - Subclasses `BaseReconstructionEngine` and implements `SHEET_NAME` and `@classmethod make_df()` returning a pandas DataFrame with Arabic columns (e.g., `"الأداة"`, `"القالب/التركيب"`, `"الوظيفة النحوية"`).
  - Orchestrators: `Main_engine.py` (collects engines and writes an Excel with one sheet per engine), `comprehensive_sentence_generator.py` (combines outputs and synthesizes sentences).
- Phoneme pipeline: `phonemes_engine.py` builds/loads `full_multilayer_grammar.csv`, adds derived columns (`Unicode`, `UTF-8`, `IPA`) and offers matching utilities.
- Ontology: `config/phoneme_ontology.yaml` (Arabic phonemes, diacritics, operators) with loader `phoneme_ontology.py` exposing helpers like `list_particles()`, `mudari_prefixes()`, and `allowed_syllable_gates()`.
- Tokenizer: `utf8_tokenizer.py` implements `UTF8PhonemeTokenizer` with `encode/decode`, `build_vocab_from_phonemes`, `save_vocab/save_pretrained` (vocab at `./tokenizers/vocab.json`).
- Training: `run_training.py` drives BERT MLM training using HuggingFace Trainer with a custom MLM collator and optional curriculum stages from `config/training_config.json`.
  - For a fast hardware/dep sanity check without datasets/pyarrow, use `run_training_smoke.py` or `.\n+    run_training_smoke.ps1`.
- Web: `run_server.py` launches `uvicorn web_app.main:app`. Note: `web_app/` may be missing on this branch; create it if you need to run the API.

## Common workflows (Windows | Python 3.8+)
- Install deps: `pip install -r requirements.txt`
- Health check: `python test_setup.py` (imports, tokenizer, config, script presence)
- Train BERT: `python run_training.py --config config/training_config.json`
  - Looks for data in `الفونيمات.csv`, `Phonemes.csv`, or `full_multilayer_grammar.csv` (repo root). Falls back to a tiny sample if missing.
  - Outputs in `./output/bert-arabic-phoneme/...` and logs in `./logs`.
- Export all engines to Excel: `python Main_engine.py` (writes `full_multilayer_grammar.xlsx`; sheet names truncated to 31 chars).
- Generate sentences: run `comprehensive_sentence_generator.py` (writes `comprehensive_multilayer_grammar.xlsx`).
- Run API (if `web_app` exists): `python run_server.py --reload` (expects `web_app/main.py` with `app = FastAPI()`).

## Conventions and patterns
- Engine modules: name `*_engine.py`; class extends `BaseReconstructionEngine`; define `SHEET_NAME` (<= 31 chars) and `make_df()` (classmethod). Prefer a primary text column `"الأداة"` when applicable; reuse Arabic column names across engines.
- CSV I/O: prefer `encoding='utf-8-sig'` for Arabic CSVs. Loaders often auto-detect a phoneme column; avoid disruptive renames.
- UTF‑8: `run_training.py` sets `PYTHONIOENCODING=utf-8` on Windows. When dumping JSON, use `ensure_ascii=False` (see tokenizer).
- Ontology-first seeding: tokenizer attempts to seed its vocab from the ontology inventory and functional sets (mudari prefixes, ten augments) before scanning CSVs; ontology is optional and gracefully skipped if missing.
- Training config: tune `training.max_seq_length`, `per_device_*_batch_size`, and `curriculum_training.stages[*]` in `config/training_config.json`. Mixed precision auto‑enables if CUDA available.

## Integration tips and gotchas
- Missing CSVs: training synthesizes a tiny sample—ok for smoke tests, not for real results.
- Web app placeholder: `run_server.py` assumes `web_app.main:app`. Create a minimal FastAPI app if absent before running.
- Arabic columns: utilities expect specific Arabic column names; reusing the existing names enables cross‑engine interop.
- Sheet naming: Excel sheet names are truncated to 31 chars in `Main_engine.py`; keep `SHEET_NAME` short.

## Examples
- Tokenizer: see `BERT_TRAINING_README.md` and the `__main__` section in `utf8_tokenizer.py` for encode/decode and vocab saving.
- Ontology: see `phoneme_ontology.py` for `get_ontology()` and helpers; YAML lives in `config/phoneme_ontology.yaml`.
- Adding an engine: mirror an existing `*_engine.py` implementing `SHEET_NAME` and `make_df()` returning a DataFrame with `"الأداة"` and related metadata columns.

## Extras
- Features pipeline: `features_pipeline.py` extracts diacritics-based features, computes MI/Fisher vs. tri-vowel patterns, and writes CSV/JSON reports. It auto-loads `config/phoneme_ontology.yaml` if available and degrades gracefully if sklearn is missing.
  - Quick run (after deps): `python features_pipeline.py` (creates `out_features.csv`, `out_mi_fisher.csv`, `out_summary.json`).
  - Training smoke: `python run_training_smoke.py` (or `./run_training_smoke.ps1`) runs a tiny in-memory MLM step to validate torch/transformers.
