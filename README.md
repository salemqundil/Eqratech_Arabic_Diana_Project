# Eqratech_Arabic_Diana_Project
Python_NLP Project with all Arabic tools verbs and names

## Features

- **Arabic Grammar Engine**: Comprehensive Arabic linguistic data processing
- **BERT Model Training**: Train BERT models for Arabic phoneme processing
- **UTF-8 Tokenizer**: Custom tokenizer for Arabic text with phoneme support
- **Web API**: FastAPI-based web service for Arabic grammar classification
- **Sentence Generation**: Tools for generating Arabic sentences

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### BERT Model Training

Train a BERT model for Arabic phoneme processing:

```bash
# Run test to verify setup
python test_setup.py

# Start training
python run_training.py --config config/training_config.json
```

See [BERT_TRAINING_README.md](BERT_TRAINING_README.md) for detailed documentation.

### Web Server

Run the Arabic grammar web classifier:

```bash
python run_server.py --host 127.0.0.1 --port 8000
```

## Project Structure

```
.
├── run_training.py          # BERT training script
├── utf8_tokenizer.py        # UTF-8 phoneme tokenizer
├── config/                  # Configuration files
│   └── training_config.json # Training configuration
├── phonemes_engine.py       # Phoneme processing engine
├── *_engine.py              # Various Arabic grammar engines
├── run_server.py            # Web server launcher
└── web_app/                 # FastAPI web application
```

## Documentation

- [BERT Training Guide](BERT_TRAINING_README.md) - Complete guide for training BERT models

## Requirements

- Python 3.8+
- PyTorch 2.0+
- Transformers 4.30+
- FastAPI
- pandas, numpy, scikit-learn

See `requirements.txt` for complete list.

## License

This project is part of the Eqratech Arabic Diana Project.

---

## Rule-based Built Pronouns/Verbs Lab

This repo includes an educational lab to attach diacritics, syllabify into six gates, detect built pronouns/particles/verbs, and export statistics from a UTF-8 Quran text.

Run on Windows PowerShell:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_built_stats.py --text ./data/quran-simple-enhanced.txt --out ./reports/built_quran
```

Outputs will appear in `./reports/built_quran/` as CSV/JSON and optional PNG plots.
