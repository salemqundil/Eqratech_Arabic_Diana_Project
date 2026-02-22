# Sprint 3 Quick Reference Guide

## 🚀 How to Use the Evaluation Pipeline

### 1. Load I3rab Corpus
```python
from fvafk.c2b.evaluation import I3rabLoader
from pathlib import Path

loader = I3rabLoader(Path("data/i3rab/quran_i3rab.csv"))

# Load specific ayah
entry = loader.load_ayah(1, 1)  # Al-Fatiha 1:1

# Load entire surah
entries = loader.load_surah(1)  # All of Al-Fatiha

# Load all corpus
all_entries = loader.load()  # 77,374 words
```

### 2. Evaluate Your Analyzer
```python
from fvafk.c2b.evaluation import MorphologyEvaluator

# Your predictions
pred_entries = your_analyzer.analyze(gold_entries)

# Evaluate
evaluator = MorphologyEvaluator()
result = evaluator.evaluate_corpus_entries(pred_entries, gold_entries)

# Get results
summary = result.summary()
print(f"Case accuracy: {summary['features']['case']['accuracy']:.2%}")
print(f"POS F1: {summary['features']['pos']['macro_f1']:.2f}")
```

### 3. Available Metrics
- **Accuracy**: Overall correctness
- **Precision**: Per-class precision
- **Recall**: Per-class recall
- **F1-Score**: Harmonic mean
- **Confusion Matrix**: Detailed error analysis

### 4. Evaluated Features
- Case: nominative, accusative, genitive
- POS: noun, verb, particle
- Number: singular, dual, plural
- Gender: masculine, feminine

## 📊 Test Commands

```bash
# Run all tests
pytest

# Run only evaluation tests
pytest tests/test_evaluation_metrics.py -v
pytest tests/test_morphology_evaluator.py -v

# Run I3rab tests
pytest tests/test_i3rab_loader.py -v
pytest tests/test_i3rab_integration.py -v

# Run with coverage
pytest --cov=src/fvafk/c2b/evaluation
```

## 📁 Key Files

- **Corpus**: `src/fvafk/c2b/corpus/`
- **Evaluation**: `src/fvafk/c2b/evaluation/`
- **Tests**: `tests/test_*evaluation*.py`
- **Data**: `data/i3rab/quran_i3rab.csv`
- **Docs**: `docs/SPRINT3_COMPLETE.md`

## 🎯 What's Next?

1. Merge sprint3 branch to main
2. Test with real morphology analyzers
3. Generate evaluation reports
4. Identify improvement opportunities

---
*Sprint 3 Complete - 2026-02-21*
