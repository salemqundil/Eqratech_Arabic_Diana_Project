# Eqratech_Arabic_Diana_Project
Python_NLP Project with all Arabic tools verbs and names

## Features

- **Arabic Grammar Engine**: Comprehensive Arabic linguistic data processing
- **BERT Model Training**: Train BERT models for Arabic phoneme processing
- **UTF-8 Tokenizer**: Custom tokenizer for Arabic text with phoneme support
- **Cloud GPU Training**: Support for AWS, GCP, Azure, Lambda Labs, and RunPod
- **Web API**: FastAPI-based web service for Arabic grammar classification
- **Sentence Generation**: Tools for generating Arabic sentences
- **Docker Support**: Containerized training with GPU acceleration

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

# Start training (local)
python run_training.py --config config/training_config.json

# Or use cloud GPU training
./quick_start_cloud_training.sh  # Linux/Mac
# OR
.\quick_start_cloud_training.ps1  # Windows
```

See [BERT_TRAINING_README.md](BERT_TRAINING_README.md) and [CLOUD_GPU_TRAINING.md](CLOUD_GPU_TRAINING.md) for detailed documentation.

### Web Server

Run the Arabic grammar web classifier:

```bash
python run_server.py --host 127.0.0.1 --port 8000
```

## Project Structure

```
.
├── run_training.py                # BERT training script
├── cloud_training_launcher.py     # Cloud GPU training launcher
├── cloud_gpu_utils.py             # GPU monitoring and optimization
├── utf8_tokenizer.py              # UTF-8 phoneme tokenizer
├── config/                        # Configuration files
│   ├── training_config.json       # Training configuration
│   └── cloud_gpu_config.json      # Cloud GPU configuration
├── cloud_examples/                # Cloud provider examples
│   ├── aws_training.sh            # AWS EC2 setup
│   ├── lambda_training.sh         # Lambda Labs setup
│   └── runpod_training.sh         # RunPod setup
├── docker/                        # Docker configurations
│   ├── Dockerfile.gpu             # GPU training Dockerfile
│   ├── docker-compose.gpu.yml     # Docker Compose config
│   └── docker_helper.sh           # Docker helper script
├── phonemes_engine.py             # Phoneme processing engine
├── *_engine.py                    # Various Arabic grammar engines
├── run_server.py                  # Web server launcher
└── web_app/                       # FastAPI web application
```

## Documentation

- [BERT Training Guide](BERT_TRAINING_README.md) - Complete guide for training BERT models
- [Cloud GPU Training Guide](CLOUD_GPU_TRAINING.md) - Cloud GPU setup for AWS, GCP, Azure, Lambda Labs, RunPod

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
