# Syntax Layer Overview

## Introduction

The Syntax Layer (Sprint 4) adds I3rab (Arabic grammatical annotation) parsing
and evaluation infrastructure on top of the existing morphology layer.

## Architecture: Layered Data Model

```
Raw I3rab text
     │
     ▼
I3rabAnnotation      ← corpus row (word, i3rab_text, surah, ayah, word_index)
     │
     ▼
I3rabComponents      ← parsed fields (i3rab_type, case, case_marker, mahall, confidence)
     │
     ▼
SyntaxFeatures       ← high-level features (syntactic_role, case, i3rab_type_ar/en, confidence)
```

## Components

### `src/fvafk/c2b/syntax/`

| File | Purpose |
|------|---------|
| `mappings.py` | Arabic↔English dictionaries for I3rab terms |
| `i3rab_components.py` | `I3rabAnnotation` and `I3rabComponents` dataclasses |
| `syntax_features.py` | `SyntaxFeatures` dataclass |
| `i3rab_parser.py` | `I3rabParser` – regex-based extraction from raw I3rab text |
| `morph_syntax_bridge.py` | `MorphSyntaxBridge` – rule-based morph→syntax inference |
| `syntax_evaluator.py` | `SyntaxEvaluator` – metrics comparison vs gold |

## Quick Start

```python
from fvafk.c2b.syntax import I3rabParser, MorphSyntaxBridge, SyntaxEvaluator

# Parse raw I3rab text
parser = I3rabParser()
comp = parser.parse("مُبْتَدَأٌ مَرْفُوعٌ وَعَلَامَةُ رَفْعِهِ الضَّمَّةُ")
print(comp.i3rab_type)    # مبتدأ
print(comp.case)          # nominative
print(comp.confidence)    # 1.0

# Predict syntax from morphology
from fvafk.c2b.morphology_flags import MorphologyFlags
bridge = MorphSyntaxBridge()
morph = MorphologyFlags(case="nominative", definiteness=True, confidence=0.9)
features = bridge.predict_syntax(morph, context=[], position=0)
print(features.syntactic_role)   # subject
print(features.i3rab_type_en)    # mubtada
```

## Phase 1 Coverage (Sprint 4)

Top 5 I3rab types (~70% of Quranic text):

| Arabic | English | Syntactic Role |
|--------|---------|----------------|
| مبتدأ | mubtada | subject |
| خبر | khabar | predicate |
| فاعل | fa'il | agent |
| مفعول به | maf'ul_bihi | object |
| حرف | harf | particle |

## Target Metrics

| Metric | Target |
|--------|--------|
| I3rab Type Accuracy | ≥70% |
| Case Accuracy | ≥85% |
| Coverage | ≥90% |
| Overall F1 | ≥0.75 |

## Testing

```bash
pytest tests/test_i3rab_parser.py        # 10+ parser tests
pytest tests/test_syntax_models.py       # 5+ model tests
pytest tests/test_morph_syntax_bridge.py # 8+ bridge tests
pytest tests/test_syntax_evaluator.py    # 8+ evaluator tests
pytest tests/test_syntax_integration.py  # 15+ integration tests
```
