# Quick Start Guide - BERT Training Setup

## ✓ Setup Complete!

All Python dependencies have been installed and the BERT training environment is ready.

## Run Training

Start training immediately with:

```bash
python run_training.py --config config/training_config.json
```

## Verify Setup

Test that everything is working:

```bash
python test_setup.py
```

## What Was Installed

- **transformers** 4.57.0 - HuggingFace transformers library
- **torch** 2.8.0+cu128 - PyTorch with CUDA support
- **datasets** 4.2.0 - Dataset handling
- **pandas** 2.3.3 - Data manipulation
- **numpy** 2.3.3 - Numerical computing
- **scikit-learn** 1.7.2 - Machine learning utilities
- **tqdm** 4.67.1 - Progress bars
- **accelerate** 1.10.1 - Training acceleration
- **tensorboard** 2.20.0 - Training visualization
- And all other dependencies from requirements.txt

## What's Available

1. **Training Script**: `run_training.py`
   - BERT model training for Arabic phonemes
   - Curriculum learning with 3 stages
   - Automatic checkpointing
   - GPU/CPU auto-detection

2. **Tokenizer**: `utf8_tokenizer.py`
   - UTF-8 phoneme tokenizer for Arabic
   - Vocabulary: 41 tokens (built from phoneme data)
   - HuggingFace compatible

3. **Configuration**: `config/training_config.json`
   - Customizable training parameters
   - Curriculum learning stages
   - Model architecture settings

4. **Test Script**: `test_setup.py`
   - Verifies all dependencies
   - Tests tokenizer functionality
   - Validates configuration

## Training Features

- **Curriculum Learning**: Progressive training with increasing complexity
  - Stage 1: Phoneme basics (128 tokens)
  - Stage 2: Word level (256 tokens)
  - Stage 3: Full sequences (512 tokens)

- **Automatic Dataset Loading**: Loads from:
  - `الفونيمات.csv` (36 phonemes)
  - `Phonemes.csv`
  - `full_multilayer_grammar1.csv`

- **Model Checkpointing**: Saves every 500 steps
- **Evaluation**: Runs every 500 steps
- **Logging**: TensorBoard logs in `./logs/`

## Output Structure

After training, you'll have:

```
output/bert-arabic-phoneme/
├── stage_1_phoneme_basics/
│   ├── checkpoint-500/
│   └── final_model/
├── stage_2_word_level/
│   ├── checkpoint-500/
│   └── final_model/
└── stage_3_full_sequences/
    ├── checkpoint-500/
    └── final_model/
        ├── config.json
        ├── pytorch_model.bin
        └── vocab.json
```

## Using the Trained Model

```python
from transformers import BertForMaskedLM
from utf8_tokenizer import UTF8PhonemeTokenizer

# Load model
model = BertForMaskedLM.from_pretrained(
    './output/bert-arabic-phoneme/stage_3_full_sequences/final_model'
)

# Load tokenizer
tokenizer = UTF8PhonemeTokenizer()
tokenizer.load_vocab(
    './output/bert-arabic-phoneme/stage_3_full_sequences/final_model/vocab.json'
)

# Predict
text = "مرحبا [MASK] العالم"
inputs = tokenizer.encode(text, padding=True)
# ... inference code
```

## Customization

Edit `config/training_config.json` to customize:

- **Epochs**: `training.num_train_epochs`
- **Batch size**: `training.per_device_train_batch_size`
- **Learning rate**: `training.learning_rate`
- **Max sequence length**: `training.max_seq_length`
- **Curriculum stages**: `curriculum_training.stages`

## Common Commands

```bash
# Run training
python run_training.py --config config/training_config.json

# Skip dependency check
python run_training.py --config config/training_config.json --skip-deps-check

# Test setup
python test_setup.py

# View logs with TensorBoard
tensorboard --logdir ./logs

# Get help
python run_training.py --help
```

## Troubleshooting

### Out of Memory
- Reduce batch size to 4 or 2
- Reduce max_seq_length to 256 or 128
- Increase gradient_accumulation_steps

### Slow Training
- Training on CPU is slower but works
- Consider using a GPU instance
- Reduce model size in config

### Import Errors
- Re-run: `pip install -r requirements.txt`
- Verify: `python test_setup.py`

## Documentation

- **SETUP_COMPLETE.md**: Comprehensive setup guide
- **BERT_TRAINING_README.md**: Detailed training documentation
- **IMPLEMENTATION_SUMMARY.md**: Implementation details

## Next Steps

1. **Start training**: `python run_training.py --config config/training_config.json`
2. **Monitor progress**: Check logs in `./logs/`
3. **Evaluate results**: Review model checkpoints
4. **Fine-tune**: Adjust hyperparameters as needed
5. **Deploy**: Use trained model in applications

---

**Setup Status**: ✓ Complete and Ready

All dependencies installed, all tests passed, ready to train!
