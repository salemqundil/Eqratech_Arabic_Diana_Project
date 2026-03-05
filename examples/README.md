# Example Data Files

This directory contains example data files that demonstrate different methods of organizing text data with labels for supervised machine learning.

## Files

### 1. Separate Files Method

**quran_data_example.txt** - Contains the text data (one verse per line)
```
بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ
الرَّحْمَٰنِ الرَّحِيمِ
```

**labels_example.txt** - Contains corresponding labels (one label per line)
```
basmala
praise
attribute
```

### 2. Embedded Labels Method (CSV)

**quran_with_labels_example.csv** - Contains both text and labels in columns
```csv
verse,category,surah
بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ,basmala,al-fatiha
الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ,praise,al-fatiha
الرَّحْمَٰنِ الرَّحِيمِ,attribute,al-fatiha
```

### 3. Embedded Labels Method (JSON)

**quran_with_labels_example.json** - Contains structured data with text and labels
```json
[
  {
    "verse": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
    "category": "basmala",
    "surah": "al-fatiha"
  },
  ...
]
```

## Usage

These files are used by the example code in:
- `tokenization_with_labels.py` (when run as main)
- `tokenization_with_labels_examples.ipynb` (all example cells)

## Creating Your Own Data

Replace these example files with your actual data:
1. Organize your Quranic verses or text data
2. Prepare your labels according to your classification needs
3. Choose the appropriate format for your use case
4. Update the file paths in your tokenization code

For detailed instructions, see `TOKENIZATION_LABELS_GUIDE.md` in the parent directory.
