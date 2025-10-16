# Quick Reference Guide - Google Colab Integration
# دليل مرجعي سريع - التكامل مع Google Colab

## Quick Start Commands

### 1. Open in Colab
```
Click: https://colab.research.google.com/github/salemqundil/Eqratech_Arabic_Diana_Project/blob/main/Eqratech_Arabic_Colab.ipynb
```

### 2. Setup (Run these in order)
```python
# Clone repository
!git clone https://github.com/salemqundil/Eqratech_Arabic_Diana_Project.git
%cd Eqratech_Arabic_Diana_Project

# Install dependencies
!pip install -q -r requirements.txt
```

### 3. Common Operations

#### List All Engines
```python
import glob
engines = sorted(glob.glob('*_engine.py'))
for i, e in enumerate(engines, 1):
    print(f"{i}. {e}")
```

#### Load an Engine
```python
# Example: Phonemes
from phonemes_engine import PhonemesEngine
df = PhonemesEngine.make_df()
df.head()
```

#### Export to Excel
```python
from export_full_multilayer_grammar_minimal import main as export_main
export_main()

# Download the file
from google.colab import files
files.download('full_multilayer_grammar.xlsx')
```

#### View CSV Files
```python
import pandas as pd
df = pd.read_csv('Harakat.csv')
df.head()
```

## Keyboard Shortcuts in Colab

| Action | Shortcut |
|--------|----------|
| Run cell | `Shift + Enter` |
| Insert cell above | `Ctrl + M A` |
| Insert cell below | `Ctrl + M B` |
| Delete cell | `Ctrl + M D` |
| Convert to markdown | `Ctrl + M M` |
| Convert to code | `Ctrl + M Y` |

## Common Patterns

### Pattern 1: Explore Data
```python
import pandas as pd
df = pd.read_csv('your_file.csv')
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
df.head(10)
```

### Pattern 2: Generate and Save
```python
from some_engine import SomeEngine
df = SomeEngine.make_df()
df.to_csv('output.csv', index=False)
files.download('output.csv')
```

### Pattern 3: Batch Processing
```python
engines = [
    ('phonemes', PhonemesEngine),
    ('verbs', VerbsEngine),
    # Add more...
]

for name, engine_class in engines:
    df = engine_class.make_df()
    print(f"{name}: {len(df)} rows")
```

## Troubleshooting Quick Fixes

### Issue: Module not found
```python
# Reinstall requirements
!pip install -q -r requirements.txt
```

### Issue: File not found
```python
# Check current directory
!pwd
!ls

# Go to project directory
%cd /content/Eqratech_Arabic_Diana_Project
```

### Issue: Memory error
```python
# Restart runtime
# Runtime > Restart runtime (from menu)
```

### Issue: Arabic text not displaying
```python
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
```

## Tips

1. **Save Your Work**: `File > Save a copy in Drive`
2. **Share Notebook**: `File > Share` or use the Share button
3. **Run All Cells**: `Runtime > Run all`
4. **Clear Output**: `Edit > Clear all outputs`
5. **Check Runtime Type**: `Runtime > Change runtime type` (CPU/GPU/TPU)

## Available Engines Reference

### Core Engines
- `phonemes_engine.py` - Phoneme processing
- `verbs_engine.py` - Verb conjugations
- `pronouns_engine.py` - Pronoun handling
- `adjective_engine.py` - Adjective processing

### Grammar Engines
- `fael_engine.py` - Subject processing
- `mafoul_bih_engine.py` - Direct object
- `mafoul_mutlaq_engine.py` - Absolute object
- `mafoul_ajlih_engine.py` - Object of purpose

### Advanced Features
- `simple_sentence_generator.py` - Sentence generation
- `export_full_multilayer_grammar_minimal.py` - Full export
- `enhanced_sentence_generation_engine.py` - Enhanced generation

## Example Workflows

### Workflow 1: Quick Data Exploration
1. Clone and install (Steps 1-2)
2. List all engines
3. Pick one engine and load it
4. Explore the DataFrame
5. Export if needed

### Workflow 2: Full Grammar Export
1. Clone and install (Steps 1-2)
2. Run export script
3. Wait for completion (may take 5-10 minutes)
4. Download the Excel file

### Workflow 3: Custom Analysis
1. Clone and install (Steps 1-2)
2. Load multiple engines
3. Merge or analyze data
4. Create visualizations
5. Export results

## Need More Help?

- Full Guide: See `COLAB_USAGE_GUIDE.md`
- Repository: https://github.com/salemqundil/Eqratech_Arabic_Diana_Project
- Issues: https://github.com/salemqundil/Eqratech_Arabic_Diana_Project/issues
