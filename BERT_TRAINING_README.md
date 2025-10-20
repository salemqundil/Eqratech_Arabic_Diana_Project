# BERT Training for Arabic Phoneme Processing

This directory contains the implementation for training a BERT model on Arabic phoneme data with curriculum learning support.

## Files

- `run_training.py` - Main training script
- `utf8_tokenizer.py` - Custom UTF-8 tokenizer for Arabic phonemes
- `config/training_config.json` - Training configuration file
- `requirements.txt` - Python dependencies

## Quick Start

### 1. Automated Setup (Recommended)

The easiest way to set up BERT training is to use the automated setup script:

```bash
python setup_bert_training.py --install
```

This will:
- ✓ Check Python version compatibility
- ✓ Install all required dependencies
- ✓ Verify configuration files
- ✓ Check data availability
- ✓ Create necessary directories
- ✓ Run validation tests

### 2. Manual Setup

If you prefer manual setup:

#### Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- transformers (for BERT model)
- torch (PyTorch framework)
- datasets (for data handling)
- tokenizers (tokenization utilities)
- accelerate (for training acceleration)
- pandas, numpy, scikit-learn (data processing)
- tensorboard (optional, for training visualization)

#### Verify Setup

```bash
python test_setup.py
```

### 3. Run Training

```bash
python run_training.py --config config/training_config.json
```

The script will:
1. Check and install dependencies if needed
2. Build a UTF-8 tokenizer from phoneme data
3. Prepare training and evaluation datasets
4. Create a BERT model
5. Train using curriculum learning (3 stages with increasing sequence length)
6. Save checkpoints and final model

## Setup Script Options

The `setup_bert_training.py` script supports several options:

```bash
# Basic setup without installing dependencies
python setup_bert_training.py

# Setup with automatic dependency installation
python setup_bert_training.py --install

# Force reinstall all dependencies
python setup_bert_training.py --force-install

# View help
python setup_bert_training.py --help
```

## Training Configuration

Edit `config/training_config.json` to customize:

- **Model Settings**: model type, output directory
- **Training Parameters**: epochs, batch size, learning rate
- **Curriculum Learning**: enable/disable, define stages
- **Tokenizer Settings**: vocabulary size, special tokens
- **Data Paths**: training, evaluation, test files

## Curriculum Training

The training uses a curriculum approach with 3 stages:
1. **Phoneme Basics** (max_length: 128) - Learn basic phoneme patterns
2. **Word Level** (max_length: 256) - Learn word-level patterns
3. **Full Sequences** (max_length: 512) - Learn full sequence patterns

## UTF-8 Tokenizer

The custom tokenizer (`utf8_tokenizer.py`) handles Arabic phonemes with proper UTF-8 encoding:

```python
from utf8_tokenizer import UTF8PhonemeTokenizer

# Create tokenizer
tokenizer = UTF8PhonemeTokenizer()
tokenizer.build_vocab_from_phonemes('الفونيمات.csv')

# Encode text
encoded = tokenizer.encode("مَرْحَبًا", padding=True)
print(encoded['input_ids'])

# Decode
decoded = tokenizer.decode(encoded['input_ids'])
print(decoded)
```

## Using the Trained Model

After training completes, load and use the model:

### Quick Start

Run the example script to see usage demonstrations:

```bash
python example_usage.py
```

This script demonstrates:
- Loading a trained BERT model
- Tokenizing Arabic text
- Making predictions with masked language modeling
- Saving and loading tokenizer vocabulary

### Manual Usage

```python
from transformers import BertForMaskedLM
from utf8_tokenizer import UTF8PhonemeTokenizer

# Load model
model = BertForMaskedLM.from_pretrained('./output/bert-arabic-phoneme/final_model')
# Or for curriculum training:
# model = BertForMaskedLM.from_pretrained('./output/bert-arabic-phoneme/stage_3_full_sequences/final_model')

# Load tokenizer
tokenizer = UTF8PhonemeTokenizer()
tokenizer.load_vocab('./output/bert-arabic-phoneme/final_model/vocab.json')

# Use for predictions
text = "مرحبا [MASK] العالم"
inputs = tokenizer.encode(text)
# ... inference code
```

## Output Structure

```
output/bert-arabic-phoneme/
├── stage_1_phoneme_basics/
│   ├── checkpoint-4/
│   └── final_model/
├── stage_2_word_level/
│   ├── checkpoint-4/
│   └── final_model/
└── stage_3_full_sequences/
    ├── checkpoint-4/
    └── final_model/
```

## Logs

Training logs are saved in `./logs/` directory and can be visualized with TensorBoard:

```bash
tensorboard --logdir ./logs
```

## Troubleshooting

### Setup Issues

**Setup script fails with permission errors**
```bash
# Run with user-specific installation
python setup_bert_training.py --install --user
```

**Dependencies conflict with existing packages**
```bash
# Create a virtual environment first
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
python setup_bert_training.py --install
```

### Missing Dependencies

If you get import errors, run:
```bash
pip install -r requirements.txt
```

### Out of Memory

If training fails due to memory issues:
- Reduce `per_device_train_batch_size` in config
- Reduce `max_seq_length` in config
- Increase `gradient_accumulation_steps`

### No GPU Available

The script automatically detects GPU availability and falls back to CPU. Training on CPU is slower but works.

## Development

To modify the training process:

1. **Data Preparation**: Edit `prepare_dataset()` in `run_training.py`
2. **Model Architecture**: Edit `create_model()` in `run_training.py`
3. **Curriculum Stages**: Edit `curriculum_training` section in `config/training_config.json`
4. **Tokenizer**: Modify `utf8_tokenizer.py` for different tokenization strategies

## License

This project is part of the Eqratech Arabic Diana Project.
