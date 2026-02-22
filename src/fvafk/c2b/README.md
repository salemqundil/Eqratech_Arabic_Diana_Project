# C2b: Morphology Layer

Morphological analysis layer for Arabic text processing.

---

## Components

### Core Analysis
- **root_extractor.py** - Extract morphological roots (trilateral, quadrilateral)
- **pattern_matcher.py** - Match words against morphological templates
- **word_classifier.py** - Classify word types (noun, verb, particle)
- **feature_extractor.py** - Extract grammatical features

### Syllabifier (Reference Implementation ⭐)
- **syllabifier.py** - **REFERENCE** syllabification engine
  - Single source of truth for syllable structure
  - Implements CV/CVV/CVC taxonomy
  - Used by morphology for word boundaries
  - 39 comprehensive tests
  - Complementary to Phonology V2 (VC classification)

### WordForm Bridge
- **word_form/** - Bridge to syntax layer
  - word_form.py - WordForm data structure
  - word_form_builder.py - Convert C2b → WordForm
  - Used by syntax linkers (ISNADI, etc.)

---

## Why Syllabifier is in C2b (not C2a)

**Reason:** Syllabification in FVAFK serves morphology:
1. Used by WordBoundaryDetector (Plan B)
2. Helps identify morpheme boundaries
3. Supports root extraction

**Relationship with C2a/Phonology V2:**
- C2a: Phonological gates (repairs, transformations)
- Phonology V2: Context-driven VC classification
- C2b Syllabifier: **Reference implementation** for morphology

They are **complementary**, not duplicate!

---

## Integration (Sprint 2)

Sprint 2 Tasks:
- ✅ Task 2.1: Gate unification (DONE)
- ⏳ Task 2.2.1: Mark syllabifier as reference (IN PROGRESS)
- ⏳ Task 2.2.2: Test syllabifier vs Phonology V2

See: docs/SPRINT2_PLAN.md

---

## Tests

Run syllabifier tests:
```bash
pytest tests/test_syllabifier.py -v  # 39 tests
```

---

## See Also

- [syllabifier.py](syllabifier.py) - Reference implementation
- [../phonology_v2/](../phonology_v2/) - Context-driven VC
- [../c1/form_codec_v2.py](../c1/form_codec_v2.py) - Encoding
- [tests/test_syllabifier.py](../../tests/test_syllabifier.py) - Tests

---

*Last Updated: 2026-02-15 (Sprint 2)*
