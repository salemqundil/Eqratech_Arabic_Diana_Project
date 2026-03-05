# Adding Labels to Tokenized Data - Guide

## Overview

This guide explains how to add labels to your tokenized data for supervised machine learning training. Labels are essential for training models to predict specific outcomes or categories.

## Understanding the Problem

When you have text data (like Quranic verses) that you want to tokenize for machine learning, you need to associate each piece of text with a label that indicates:
- What category it belongs to
- What you want the model to learn
- What the expected output should be

## Where Can Labels Come From?

Labels can be organized in several ways:

### 1. **Separate Label File**

**Use Case:** You have your text in one file and labels in another file.

**File Structure:**
```
quran_data.txt:
بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ
...

labels.txt:
basmala
praise
...
```

**Requirements:**
- Both files must have the same number of lines
- Line N in the data file corresponds to line N in the labels file

**Code Example:**
```python
from tokenization_with_labels import TokenizationWithLabels

tokenizer = TokenizationWithLabels()
tokenized_data = tokenizer.tokenize_with_labels_from_separate_file(
    'quran_data.txt',
    'labels.txt'
)
```

### 2. **Embedded Labels (CSV Format)**

**Use Case:** Your data and labels are in the same CSV file.

**File Structure:**
```csv
verse,category,surah
بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ,basmala,al-fatiha
الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ,praise,al-fatiha
```

**Code Example:**
```python
from tokenization_with_labels import TokenizationWithLabels

tokenizer = TokenizationWithLabels()
tokenized_data = tokenizer.tokenize_with_embedded_labels(
    'quran_with_labels.csv',
    text_column='verse',
    label_column='category'
)
```

### 3. **Embedded Labels (JSON Format)**

**Use Case:** Your data is structured in JSON format.

**File Structure:**
```json
[
  {
    "verse": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
    "category": "basmala",
    "surah": "al-fatiha"
  },
  {
    "verse": "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
    "category": "praise",
    "surah": "al-fatiha"
  }
]
```

**Code Example:**
```python
from tokenization_with_labels import TokenizationWithLabels

tokenizer = TokenizationWithLabels()
tokenized_data = tokenizer.tokenize_with_embedded_labels(
    'quran_with_labels.json',
    text_column='verse',
    label_column='category',
    file_format='json'
)
```

### 4. **Label Mapping (Dictionary-Based)**

**Use Case:** You have a mapping of line/verse numbers to labels.

**Code Example:**
```python
from tokenization_with_labels import TokenizationWithLabels

# Create a mapping of line index to label
label_mapping = {
    0: 'meccan',
    1: 'medinan',
    2: 'meccan',
    # ... more mappings
}

tokenizer = TokenizationWithLabels()
tokenized_data = tokenizer.tokenize_with_label_mapping(
    'quran_data.txt',
    label_mapping
)
```

### 5. **Pattern-Based Labels (Rule-Based)**

**Use Case:** Labels can be derived from the text itself using rules or patterns.

**Code Example:**
```python
from tokenization_with_labels import TokenizationWithLabels

# Define a function to determine labels based on text
def get_label_from_text(text):
    if 'بِسْمِ اللَّهِ' in text:
        return 'basmala'
    elif len(text) > 100:
        return 'long_verse'
    else:
        return 'short_verse'

tokenizer = TokenizationWithLabels()
tokenized_data = tokenizer.tokenize_with_pattern_based_labels(
    'quran_data.txt',
    get_label_from_text
)
```

## Common Label Types for Quranic Text

Depending on your machine learning goal, you might use different types of labels:

### 1. **Revelation Period**
- `meccan` - Verses revealed in Mecca
- `medinan` - Verses revealed in Medina

### 2. **Thematic Categories**
- `stories` - Narratives about prophets
- `laws` - Legal rulings
- `beliefs` - Articles of faith
- `worship` - Prayer, fasting, etc.
- `ethics` - Moral guidance

### 3. **Surah Names**
- `al-fatiha`
- `al-baqarah`
- `al-imran`
- etc.

### 4. **Grammatical Features**
- `verb_sentence` - Sentences starting with verbs
- `noun_sentence` - Sentences starting with nouns
- `question` - Interrogative verses
- `command` - Imperative verses

### 5. **Stylistic Features**
- `narrative` - Story-telling style
- `dialogue` - Direct speech
- `description` - Descriptive passages

## Integration with Transformers Library

If you're using the Hugging Face `transformers` library, you can integrate the tokenizer:

```python
from transformers import AutoTokenizer
from tokenization_with_labels import TokenizationWithLabels

# Load a pre-trained Arabic tokenizer
hf_tokenizer = AutoTokenizer.from_pretrained('aubmindlab/bert-base-arabertv2')

# Create tokenizer with the Hugging Face tokenizer
tokenizer = TokenizationWithLabels(tokenizer=hf_tokenizer)

# Use any of the methods above
tokenized_data = tokenizer.tokenize_with_labels_from_separate_file(
    'quran_data.txt',
    'labels.txt'
)
```

## Saving Tokenized Data

Once you've tokenized your data with labels, you can save it:

```python
# Save as JSON
tokenizer.save_tokenized_data(
    tokenized_data,
    'tokenized_quran_data.json',
    format='json'
)

# Save as CSV
tokenizer.save_tokenized_data(
    tokenized_data,
    'tokenized_quran_data.csv',
    format='csv'
)
```

## Using in Jupyter Notebook

Here's how to use this in a Jupyter notebook cell (like cell efffdefa):

```python
# Cell: Tokenization with Labels
from tokenization_with_labels import TokenizationWithLabels

# Initialize tokenizer
tokenizer = TokenizationWithLabels()

# Method 1: If you have separate files
tokenized_data = tokenizer.tokenize_with_labels_from_separate_file(
    'path/to/quran_data.txt',
    'path/to/labels.txt'
)

# Method 2: If you have a CSV with embedded labels
tokenized_data = tokenizer.tokenize_with_embedded_labels(
    'path/to/quran_with_labels.csv',
    text_column='text',
    label_column='label'
)

# Display first few examples
for i, item in enumerate(tokenized_data[:3]):
    print(f"Example {i+1}:")
    print(f"  Text: {item['text']}")
    print(f"  Tokens: {item['tokens']}")
    print(f"  Label: {item['label']}")
    print()

# Save the tokenized data
tokenizer.save_tokenized_data(
    tokenized_data,
    'tokenized_quran_with_labels.json',
    format='json'
)

print(f"Tokenized {len(tokenized_data)} items with labels")
```

## Next Steps

1. **Determine Your Label Source**: Based on your project, decide which method best fits your data organization.

2. **Prepare Your Labels**: Create or organize your labels according to one of the methods above.

3. **Modify Your Tokenization Code**: Update your existing tokenization cell (like cell efffdefa) to use one of these methods.

4. **Verify the Results**: Check that each tokenized item has the correct label associated with it.

5. **Train Your Model**: Use the tokenized data with labels to train your supervised learning model.

## Example: Complete Workflow

```python
# Step 1: Import the utility
from tokenization_with_labels import TokenizationWithLabels

# Step 2: Initialize
tokenizer = TokenizationWithLabels()

# Step 3: Tokenize with labels (choose your method)
tokenized_data = tokenizer.tokenize_with_embedded_labels(
    'quran_complete.csv',
    text_column='verse_text',
    label_column='theme'
)

# Step 4: Verify
print(f"Total items: {len(tokenized_data)}")
print(f"Sample item: {tokenized_data[0]}")

# Step 5: Save
tokenizer.save_tokenized_data(
    tokenized_data,
    'training_data.json',
    format='json'
)

# Step 6: Use in training
# Now you can load this data in your training script
```

## Troubleshooting

### Issue: Files have different lengths
**Solution:** Ensure your data file and labels file have the same number of lines.

### Issue: Column not found in CSV
**Solution:** Check the column names in your CSV file and make sure they match the `text_column` and `label_column` parameters.

### Issue: Encoding errors with Arabic text
**Solution:** Make sure all files are saved with UTF-8 encoding.

### Issue: Labels not matching data
**Solution:** Verify the order of labels matches the order of data. You might need to add an ID column to both files to ensure correct matching.

## Questions to Answer

Before implementing, please determine:

1. **Where are your labels?**
   - [ ] In a separate file
   - [ ] In the same file as the data
   - [ ] Need to be created based on metadata
   - [ ] Need to be derived from the text

2. **What format are your labels in?**
   - [ ] Text file (one label per line)
   - [ ] CSV file
   - [ ] JSON file
   - [ ] Database
   - [ ] Need to be created

3. **What do your labels represent?**
   - [ ] Categories/classes
   - [ ] Numerical values
   - [ ] Multiple tags per item
   - [ ] Other

4. **How are labels associated with data?**
   - [ ] Line-by-line correspondence
   - [ ] By ID/index
   - [ ] By metadata
   - [ ] Need to establish association

Once you answer these questions, you can choose the appropriate method from this guide.
