# Tokenization with Labels - Workflow Diagram

## Overview Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    YOUR DATA + LABELS                                │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
       ┌───────────────────────────────────────────────┐
       │   Choose Your Method (see guide below)        │
       └──────────────────┬────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
   ┌────────┐      ┌──────────┐      ┌──────────┐
   │Method 1│      │Method 2/3│      │Method 4/5│
   │Separate│      │Embedded  │      │Mapping/  │
   │Files   │      │Labels    │      │Pattern   │
   └────┬───┘      └─────┬────┘      └─────┬────┘
        │                │                  │
        └────────────────┼──────────────────┘
                         │
                         ▼
       ┌──────────────────────────────────────┐
       │  TokenizationWithLabels()            │
       │  - tokenize_with_labels_*()          │
       └─────────────────┬────────────────────┘
                         │
                         ▼
       ┌──────────────────────────────────────┐
       │  Tokenized Data with Labels          │
       │  [{text, tokens, label}, ...]        │
       └─────────────────┬────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   ┌────────┐      ┌─────────┐     ┌─────────┐
   │Save as │      │Save as  │     │Use in   │
   │JSON    │      │CSV      │     │Training │
   └────────┘      └─────────┘     └─────────┘
```

## Method Selection Guide

```
┌─────────────────────────────────────────────────────────────────────┐
│ Do you have separate data and label files?                          │
│                                                                      │
│ YES → Method 1: tokenize_with_labels_from_separate_file()          │
│       Example: quran_data.txt + labels.txt                          │
│                                                                      │
│ NO  → Continue below                                                │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ Is your data in CSV or JSON with labels in columns?                 │
│                                                                      │
│ YES → Method 2/3: tokenize_with_embedded_labels()                  │
│       Example: quran_data.csv with 'verse' and 'category' columns  │
│                                                                      │
│ NO  → Continue below                                                │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ Do you have a mapping of line numbers to labels?                    │
│                                                                      │
│ YES → Method 4: tokenize_with_label_mapping()                      │
│       Example: {0: 'meccan', 1: 'medinan', ...}                    │
│                                                                      │
│ NO  → Continue below                                                │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ Can labels be derived from the text using rules?                    │
│                                                                      │
│ YES → Method 5: tokenize_with_pattern_based_labels()               │
│       Example: Label based on text length, keywords, etc.           │
│                                                                      │
│ NO  → You need to prepare labels first (see guide)                 │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Organization Examples

### Method 1: Separate Files
```
Project/
├── quran_data.txt         ← Your verses (one per line)
│   بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
│   الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ
│
└── labels.txt             ← Corresponding labels (one per line)
    basmala
    praise
```

### Method 2: Embedded CSV
```
Project/
└── quran_data.csv
    verse,category,surah
    بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ,basmala,al-fatiha
    الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ,praise,al-fatiha
```

### Method 3: Embedded JSON
```
Project/
└── quran_data.json
    [
      {
        "verse": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
        "category": "basmala",
        "surah": "al-fatiha"
      },
      ...
    ]
```

### Method 4: Label Mapping
```python
# In your Python code
label_mapping = {
    0: 'meccan',      # Line 0 in quran_data.txt
    1: 'medinan',     # Line 1 in quran_data.txt
    2: 'meccan',      # Line 2 in quran_data.txt
    # ...
}
```

### Method 5: Pattern-Based
```python
# In your Python code
def get_label(text):
    if 'بِسْمِ اللَّهِ' in text:
        return 'basmala'
    elif len(text) > 100:
        return 'long_verse'
    elif any(keyword in text for keyword in ['أم', 'هل']):
        return 'question'
    else:
        return 'statement'
```

## Output Structure

After tokenization, each item has this structure:

```python
{
    'text': 'بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ',
    'tokens': ['بِسْمِ', 'اللَّهِ', 'الرَّحْمَٰنِ', 'الرَّحِيمِ'],
    'label': 'basmala'
}
```

With Hugging Face transformers, tokens might be subword tokens:

```python
{
    'text': 'بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ',
    'tokens': ['[CLS]', 'ب', '##س', '##م', 'الله', ...],
    'label': 'basmala'
}
```

## Integration Points

### With Training Pipeline
```python
from tokenization_with_labels import TokenizationWithLabels

# Tokenize data
tokenizer = TokenizationWithLabels()
tokenized_data = tokenizer.tokenize_with_labels_from_separate_file(
    'quran_data.txt', 'labels.txt'
)

# Use in your training
for item in tokenized_data:
    text = item['text']
    tokens = item['tokens']
    label = item['label']
    
    # Your training code here
    model.train(tokens, label)
```

### With Hugging Face Datasets
```python
from datasets import Dataset

# Convert to Hugging Face Dataset
dataset = Dataset.from_dict({
    'text': [item['text'] for item in tokenized_data],
    'tokens': [item['tokens'] for item in tokenized_data],
    'label': [item['label'] for item in tokenized_data]
})
```

## Quick Start Commands

```bash
# 1. Clone/navigate to repository
cd Eqratech_Arabic_Diana_Project

# 2. Run example to see it work
python3 tokenization_with_labels.py

# 3. Open notebook (Jupyter or Colab)
jupyter notebook tokenization_with_labels_examples.ipynb

# 4. Or use directly in Python
python3
>>> from tokenization_with_labels import TokenizationWithLabels
>>> tokenizer = TokenizationWithLabels()
>>> # Use any method...
```

## Need Help?

1. **Quick answers** → See `QUICK_REFERENCE.md`
2. **Detailed guide** → See `TOKENIZATION_LABELS_GUIDE.md`
3. **Working examples** → Open `tokenization_with_labels_examples.ipynb`
4. **Example data** → Check `examples/` directory
5. **Solution overview** → See `SOLUTION_SUMMARY.md`
