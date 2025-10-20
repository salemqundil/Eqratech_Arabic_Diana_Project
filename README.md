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

#### Option 1: Automated Setup (Recommended)

```bash
# Run the setup script with automatic dependency installation
python setup_bert_training.py --install
```

#### Option 2: Manual Installation

```bash
# Install dependencies manually
pip install -r requirements.txt
```

### BERT Model Training

Train a BERT model for Arabic phoneme processing:

```bash
# Option 1: Use the setup script (automatically installs dependencies and validates setup)
python setup_bert_training.py --install

# Option 2: Manual verification and training
python test_setup.py           # Verify setup
python run_training.py --config config/training_config.json  # Start training
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
├── setup_bert_training.py   # Automated setup script for BERT training
├── run_training.py          # BERT training script
├── test_setup.py            # Setup validation script
├── utf8_tokenizer.py        # UTF-8 phoneme tokenizer
├── config/                  # Configuration files
│   └── training_config.json # Training configuration
├── phonemes_engine.py       # Phoneme processing engine
├── *_engine.py              # Various Arabic grammar engines
├── run_server.py            # Web server launcher
└── output/                  # Training outputs (created by setup)
    └── logs/                # Training logs
```

## Documentation

- [Quick Start Guide](QUICKSTART.md) - Get started in under 5 minutes
- [BERT Training Guide](BERT_TRAINING_README.md) - Complete guide for training BERT models
- [Usage Examples](example_usage.py) - Code examples for using trained models

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
