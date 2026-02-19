# Sprint 3: Morphology + Corpus Implementation Plan

**Duration**: 4 weeks  
**Goal**: Implement sophisticated morphological analysis with gold corpus evaluation  
**Success Metric**: F1 score ≥ 0.85 on morphological analysis

---

## 📋 Overview

Sprint 3 builds on the existing phonology pipeline (Sprint 1-2) to add comprehensive morphological analysis capabilities. This sprint focuses on practical, measurable outcomes with a gold standard corpus.

### Current State (Post-Sprint 2)
- ✅ 373 tests passing
- ✅ Phonology gates operational (11 gates)
- ✅ Basic morphology components exist:
  - `pattern_matcher.py` (PatternMatcher, PatternDatabase)
  - `root_extractor.py` (RootExtractor)
  - `awzan_loader.py` (external pattern loading)
  - `syllabifier.py` (39 tests)
  - `word_form/` (bridge to syntax)

### Gaps to Fill
1. **WordBoundaryDetector Plan B** - Syllable-based detection
2. **PatternCatalog expansion** - 50+ patterns needed
3. **Gold corpus** - 50-100 annotated sentences
4. **Evaluation framework** - F1 score measurement
5. **Integration tests** - End-to-end morphology pipeline

---

## 🎯 Objectives

### Primary Deliverables
1. **WordBoundaryDetector Plan B** - Sophisticated boundary detection using syllabification
2. **Complete PatternCatalog** - Comprehensive Arabic morphological patterns
3. **Gold Corpus V1** - 50-100 annotated sentences with root/pattern/POS tags
4. **Evaluation Framework** - F1 score computation for morphology
5. **Integration Tests** - 80+ new tests (target: 450+ total)

### Success Criteria
- F1 score ≥ 0.85 on:
  - Root extraction
  - Pattern matching
  - Word boundary detection
- All tests passing (450+ tests)
- Documentation complete
- Ready for Sprint 4 (Syntax)

---

## 📅 4-Week Timeline

### Week 1: WordBoundaryDetector + Pattern Expansion
**Focus**: Core morphology components

**Tasks**:
- [ ] Implement `WordBoundaryDetectorPlanB` class
  - Uses syllabifier for boundary hints
  - Handles clitics (ال، و، ف، ب، ل)
  - Confidence scoring for boundaries
- [ ] Expand `PatternDatabase` to 50+ patterns
  - Add all verb forms (I-X)
  - Add noun patterns (broken plurals, participles)
  - Load from `data/awzan/` JSON files
- [ ] Write 20+ unit tests for new components

**Deliverables**:
- `src/fvafk/c2b/word_boundary_detector.py`
- `data/awzan/patterns_extended.json`
- `tests/test_word_boundary_detector.py`
- `tests/test_pattern_catalog.py`

---

### Week 2: Gold Corpus Creation
**Focus**: Build evaluation dataset

**Tasks**:
- [ ] Create corpus structure in `data/corpus/`
- [ ] Annotate 50+ Arabic sentences with:
  - Word boundaries
  - Roots (ك-ت-ب format)
  - Patterns (فِعَال format)
  - POS tags (noun, verb, particle)
  - Morphological features (prefix, suffix, case)
- [ ] Split into train/val/test sets (60/20/20)
- [ ] Create JSON schema for corpus format
- [ ] Validate annotations for consistency

**Deliverables**:
- `data/corpus/gold_corpus_v1.md` (human-readable)
- `data/corpus/gold_corpus_v1.json` (machine-readable)
- `data/corpus/test_set.json`
- `data/corpus/validation_set.json`
- `data/corpus/README.md` (annotation guidelines)

**Example Sentence Structure**:
```json
{
  "id": "sent_001",
  "text": "الْكِتَابُ عَلَى الطَّاوِلَةِ",
  "translation": "The book is on the table",
  "words": [
    {
      "surface": "الْكِتَابُ",
      "root": "ك-ت-ب",
      "pattern": "فِعَال",
      "pos": "noun",
      "prefix": "ال",
      "case": "nominative"
    },
    ...
  ]
}
```

---

### Week 3: Integration & Testing
**Focus**: Wire everything together

**Tasks**:
- [ ] Integrate all morphology components into pipeline
- [ ] Create `MorphologyPipeline` orchestrator class
- [ ] Write integration tests:
  - End-to-end word → root → pattern
  - Multi-word sentence parsing
  - Edge cases (unknown words, ambiguous patterns)
- [ ] Property-based tests using Hypothesis
- [ ] Performance benchmarking
- [ ] Debug and fix issues

**Deliverables**:
- `src/fvafk/c2b/morphology_pipeline.py`
- `tests/test_morphology_integration.py`
- `tests/test_morphology_properties.py`
- Performance benchmarks document

**Test Targets**:
- 30+ integration tests
- 50+ unit tests for new components
- **Total: 450+ tests** (currently 373)

---

### Week 4: Evaluation & Polish
**Focus**: Measure performance and optimize

**Tasks**:
- [ ] Implement `MorphologyEvaluator` class
- [ ] Run evaluation on gold corpus:
  - Root extraction accuracy
  - Pattern matching accuracy
  - Boundary detection F1
  - Overall pipeline F1
- [ ] Generate evaluation report
- [ ] Optimize low-performing components
- [ ] Update documentation
- [ ] Create Sprint 3 completion report

**Deliverables**:
- `src/fvafk/evaluation/morphology_evaluator.py`
- `tests/test_evaluation.py`
- `docs/SPRINT3_EVALUATION_REPORT.md`
- `docs/SPRINT3_COMPLETION.md`

**Success Metric**: F1 ≥ 0.85 on all morphology tasks

---

## 🏗️ Architecture

### Component Diagram
```
Text Input
    ↓
WordBoundaryDetector Plan B
    ↓ (word tokens)
RootExtractor
    ↓ (roots)
PatternMatcher
    ↓ (patterns)
WordFormBuilder
    ↓
Syntax Layer (Sprint 4)
```

### Key Classes

#### 1. WordBoundaryDetectorPlanB
```python
class WordBoundaryDetectorPlanB:
    """Syllable-based word boundary detection"""
    
    def __init__(self):
        self.syllabifier = Syllabifier()
        self.clitic_patterns = load_clitics()
    
    def detect_boundaries(self, text: str) -> List[WordBoundary]:
        """Detect word boundaries with confidence scores"""
        pass
```

#### 2. PatternCatalog
```python
class PatternCatalog:
    """Complete morphological pattern catalog"""
    
    @classmethod
    def load_full_catalog(cls) -> Dict[str, List[PatternTemplate]]:
        """Load 50+ patterns from awzan + built-in"""
        pass
    
    def get_patterns_by_category(self, category: str) -> List[PatternTemplate]:
        """Get patterns by category (verb, noun, plural)"""
        pass
```

#### 3. MorphologyEvaluator
```python
class MorphologyEvaluator:
    """Evaluate morphology against gold standard"""
    
    def evaluate_root_extraction(self, gold, predicted) -> EvaluationMetrics:
        """Compute precision/recall/F1 for root extraction"""
        pass
    
    def evaluate_pattern_matching(self, gold, predicted) -> EvaluationMetrics:
        """Compute precision/recall/F1 for pattern matching"""
        pass
```

---

## 📊 Metrics & Tracking

### Weekly Progress Metrics
- Tests written / Tests passing
- Lines of code added
- Corpus sentences annotated
- F1 score (week 4)

### Sprint 3 KPIs
| Metric | Target | Current |
|--------|--------|---------|
| Total Tests | 450+ | 373 |
| Corpus Sentences | 50+ | 0 |
| Pattern Catalog Size | 50+ | ~25 |
| Root Extraction F1 | ≥0.85 | TBD |
| Pattern Matching F1 | ≥0.85 | TBD |
| Boundary Detection F1 | ≥0.85 | TBD |

---

## 🔗 Dependencies

### Prerequisites (Already Complete)
- ✅ Sprint 1: Foundation + CLI
- ✅ Sprint 2: Phonology gates

### Sprint 3 Enables
- Sprint 4: Syntax (TADMINI/TAQYIDI)
- Sprint 5: Constraints
- Sprint 6: Full pipeline integration

---

## 📚 References

- **Master Plan**: `docs/MASTER_PLAN_CHECKLIST.md` (Part 3: Morphology)
- **Existing Code**: `src/fvafk/c2b/`
- **Pattern Data**: `data/awzan/`
- **Previous Sprints**: `docs/SPRINT1_COMPLETION.md`, `docs/SPRINT2_COMPLETION.md`

---

## 🚀 Getting Started

### Day 1 Checklist
1. Create branch: `sprint3-morphology-corpus`
2. Review existing morphology code (`src/fvafk/c2b/`)
3. Set up corpus directory structure
4. Begin WordBoundaryDetector implementation

### Development Workflow
1. Write tests first (TDD)
2. Implement feature
3. Run full test suite: `pytest tests/ -v`
4. Document code
5. Commit with descriptive messages

---

**Sprint Owner**: @sonaiso  
**Start Date**: 2026-02-16  
**Target Completion**: 2026-03-16  
**Status**: 🟢 IN PROGRESS

---

*Generated: 2026-02-16*  
*Last Updated: 2026-02-16*