# Syntax Evaluation Methodology

## Overview

The `SyntaxEvaluator` class compares system predictions (`SyntaxFeatures`) against
gold-standard corpus annotations (`I3rabComponents`) and reports three primary metrics.

## Metrics

### I3rab Type Accuracy

Fraction of words where the predicted Arabic I3rab type label matches the gold label.

```
i3rab_type_accuracy = correct_i3rab_types / total_words
```

**Target**: ≥70%

### Case Accuracy

Fraction of words where the predicted grammatical case matches the gold case.

```
case_accuracy = correct_cases / total_words
```

**Target**: ≥85%

### Coverage

Fraction of words for which the system produced a non-"unknown" I3rab type prediction.

```
coverage = predicted_words / total_words
```

**Target**: ≥90%

### Overall F1

Macro-averaged F1 score across all I3rab type labels detected in the evaluation set.

**Target**: ≥0.75

## Usage

```python
from fvafk.c2b.syntax import SyntaxEvaluator, I3rabParser, MorphSyntaxBridge
from fvafk.c2b.morphology_flags import MorphologyFlagsExtractor

parser = I3rabParser()
bridge = MorphSyntaxBridge()
extractor = MorphologyFlagsExtractor()
evaluator = SyntaxEvaluator()

# Build gold from corpus
gold = [parser.parse(row["i3rab"]) for row in corpus_rows]

# Build predictions
preds = [
    bridge.predict_syntax(extractor.extract(row["word"]), context=[], position=i)
    for i, row in enumerate(corpus_rows)
]

metrics = evaluator.evaluate(preds, gold)
print(f"I3rab Type Accuracy: {metrics.i3rab_type_accuracy:.1%}")
print(f"Case Accuracy:       {metrics.case_accuracy:.1%}")
print(f"Coverage:            {metrics.coverage:.1%}")
print(f"Overall F1:          {metrics.overall_f1:.3f}")
```

## Interpretation

| Score | Meaning |
|-------|---------|
| 1.0 | Perfect match with gold standard |
| ≥0.85 | Excellent – production quality |
| ≥0.70 | Good – Sprint 4 target |
| ≥0.60 | Acceptable for Phase 1 |
| <0.60 | Needs improvement |

## Limitations

- The `MorphSyntaxBridge` uses rule-based inference; accuracy depends on diacritic
  quality in the input.
- Phase 1 covers Top 5 I3rab types (~70% of words); remaining types return "unknown".
- Confidence scores below 0.5 are flagged with a warning for manual review.
