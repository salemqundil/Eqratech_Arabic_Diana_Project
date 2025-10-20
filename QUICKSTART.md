# Quick Start Guide - BERT Training

This guide will get you started with BERT model training in under 5 minutes.

## Prerequisites

- Python 3.8 or higher
- 4GB+ RAM (8GB recommended)
- GPU optional (speeds up training significantly)

## Step 1: Clone the Repository

```bash
git clone https://github.com/salemqundil/Eqratech_Arabic_Diana_Project.git
cd Eqratech_Arabic_Diana_Project
```

## Step 2: Run Setup Script

Run the automated setup script:

```bash
python setup_bert_training.py --install
```

This single command will:
- ✅ Check your Python version
- ✅ Install all required dependencies (PyTorch, Transformers, etc.)
- ✅ Verify configuration files
- ✅ Check for training data
- ✅ Create output directories
- ✅ Run validation tests

**Expected output:**
```
======================================================================
  BERT Training Environment Setup
======================================================================

[1/9] Checking Python version
✓ Python version: 3.x.x

[2/9] Installing dependencies
ℹ Installing dependencies from requirements.txt...
✓ Dependencies installed successfully

...

======================================================================
  Setup Complete!
======================================================================
```

## Step 3: Start Training

Once setup is complete, start training:

```bash
python run_training.py --config config/training_config.json
```

The training will:
1. Load Arabic phoneme data
2. Create a custom UTF-8 tokenizer
3. Initialize a BERT model
4. Train using curriculum learning (3 stages)
5. Save the trained model to `./output/`

**Training progress:**
```
[TRAINING] Starting model training...
[TRAINING] Device: GPU / CPU
Epoch 1/3: 100%|████████████| 100/100 [00:30<00:00,  3.33it/s]
...
[TRAINING] Model saved to ./output/bert-arabic-phoneme/final_model
```

## Step 4: Monitor Training (Optional)

In a separate terminal, launch TensorBoard to monitor training:

```bash
tensorboard --logdir ./logs
```

Then open http://localhost:6006 in your browser.

## What's Next?

### Use the Trained Model

```python
from transformers import BertForMaskedLM
from utf8_tokenizer import UTF8PhonemeTokenizer

# Load model
model = BertForMaskedLM.from_pretrained('./output/bert-arabic-phoneme/final_model')

# Load tokenizer
tokenizer = UTF8PhonemeTokenizer()
tokenizer.load_vocab('./output/bert-arabic-phoneme/final_model/vocab.json')

# Use for predictions
text = "مرحبا بكم"
inputs = tokenizer.encode(text, padding=True, max_length=128)
# ... your inference code here
```

### Customize Training

Edit `config/training_config.json` to adjust:
- Number of epochs
- Batch size
- Learning rate
- Curriculum learning stages
- Output directory

### View Results

After training completes, check these directories:
- `./output/bert-arabic-phoneme/` - Trained models
- `./logs/` - Training logs
- `./tokenizers/` - Tokenizer vocabulary

## Troubleshooting

### Common Issues

**"No module named 'transformers'"**
```bash
# Run setup script again with install flag
python setup_bert_training.py --install
```

**"CUDA out of memory"**
```bash
# Edit config/training_config.json
# Reduce "per_device_train_batch_size" from 8 to 4 or 2
```

**"No training data found"**
- The script will automatically use sample data
- To use your own data, place CSV files in the project root
- Supported files: الفونيمات.csv, Phonemes.csv

### Get Help

1. Check the detailed documentation: [BERT_TRAINING_README.md](BERT_TRAINING_README.md)
2. Run validation tests: `python test_setup.py`
3. View setup help: `python setup_bert_training.py --help`

## Summary of Commands

```bash
# 1. Setup (one-time)
python setup_bert_training.py --install

# 2. Verify setup (optional)
python test_setup.py

# 3. Train model
python run_training.py --config config/training_config.json

# 4. Monitor training (optional)
tensorboard --logdir ./logs
```

That's it! You're now ready to train Arabic BERT models. 🚀
