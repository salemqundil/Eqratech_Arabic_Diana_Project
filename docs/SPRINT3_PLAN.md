# Sprint 3 Plan: Morphology + Corpus Evaluation

**Duration:** 2 weeks (Weeks 5-6)  
**Status:** 🎯 Ready to Start  
**Prerequisites:** ✅ Sprint 1 Complete, ✅ Sprint 2 Complete  
**Current Tests:** 373 passing

---

## 🎯 Sprint Goals

1. Complete morphology layer with Plan B word boundary detection
2. Integrate PatternCatalog with Bayan's PatternUniverse
3. Expose morphological flags (case, definite, number, gender)
4. Build gold corpus evaluation infrastructure
5. Achieve F1 ≥ 0.85 for morphology accuracy

---

## 📋 Tasks Breakdown

### Task 3.1: WordBoundaryDetector Plan B (3-4 days)

**Description:** Implement syllable-based word boundary detection as an alternative to character-pattern-based Plan A.

**Subtasks:**
- [ ] 3.1.1: Design syllable-based boundary detection algorithm
- [ ] 3.1.2: Implement `WordBoundaryDetectorPlanB` class
- [ ] 3.1.3: Integrate with existing `Syllabifier`
- [ ] 3.1.4: Add clitic detection (prefixes/suffixes)
- [ ] 3.1.5: Implement confidence scoring
- [ ] 3.1.6: Add 10+ tests for edge cases
- [ ] 3.1.7: Compare Plan A vs Plan B accuracy
- [ ] 3.1.8: Update CLI to expose `--word-detector=plan-b` option
- [ ] 3.1.9: Document algorithm in `docs/MORPHOLOGY.md`

**Files to Create:**
- `src/fvafk/c2b/word_boundary_detector.py`
- `tests/test_word_boundary_detector.py` (already exists, needs implementation)
- `docs/MORPHOLOGY.md`

**Success Criteria:**
- Plan B detector achieves ≥85% accuracy on test cases
- All 10+ new tests pass
- Performance: <5ms per word

---

### Task 3.2: PatternCatalog Integration (2-3 days)

**Description:** Connect PatternAnalyzer to Bayan's comprehensive PatternUniverse for better pattern recognition.

**Subtasks:**
- [ ] 3.2.1: Create `PatternCatalog` wrapper class
- [ ] 3.2.2: Map existing `PatternAnalyzer` to `PatternUniverse`
- [ ] 3.2.3: Add pattern taxonomy (verb forms, noun forms, plurals)
- [ ] 3.2.4: Implement pattern matching with confidence scores
- [ ] 3.2.5: Add 8+ tests for pattern matching
- [ ] 3.2.6: Update documentation with pattern categories

**Files to Create:**
- `src/fvafk/c2b/pattern_catalog.py`
- `tests/test_pattern_catalog.py`

**Success Criteria:**
- Pattern catalog covers 50+ common patterns
- Pattern matching accuracy ≥90%
- All tests pass

---

### Task 3.3: Morphology Flags Exposure (2 days)

**Description:** Surface linguistic features (case, definite, number, gender) in WordForm output.

**Subtasks:**
- [ ] 3.3.1: Add `morph_flags` field to `WordForm` Pydantic model
- [ ] 3.3.2: Extract case markers (nominative, accusative, genitive)
- [ ] 3.3.3: Extract definiteness from article/nunation
- [ ] 3.3.4: Extract number (singular, dual, plural)
- [ ] 3.3.5: Extract gender (masculine, feminine)
- [ ] 3.3.6: Update CLI JSON output with flags
- [ ] 3.3.7: Add 5+ tests for flag combinations
- [ ] 3.3.8: Update `CLI_SCHEMA.md` documentation

**Files to Modify:**
- `app/models/word_form.py`
- `src/fvafk/c2b/word_form/word_form_builder.py`
- `src/fvafk/cli/main.py`
- `docs/CLI_SCHEMA.md`

**Files to Create:**
- `tests/test_morph_flags.py`

**Success Criteria:**
- Flags correctly extracted for 95% of test cases
- CLI output includes all morphological flags
- Documentation updated

---

### Task 3.4: Gold Corpus Loader (3-4 days)

**Description:** Build evaluation infrastructure with gold-standard Arabic corpus.

**Subtasks:**
- [ ] 3.4.1: Choose corpus source (Quranic Arabic recommended)
- [ ] 3.4.2: Select 100 verses for initial corpus
- [ ] 3.4.3: Create corpus data format (JSON/CSV)
- [ ] 3.4.4: Implement `CorpusLoader` class
- [ ] 3.4.5: Add gold standard annotations (roots, patterns, morphology)
- [ ] 3.4.6: Build corpus validation tests
- [ ] 3.4.7: Create corpus documentation

**Files to Create:**
- `src/fvafk/corpus/corpus_loader.py`
- `src/fvafk/corpus/gold_standard.py`
- `data/corpus/quran_100_verses.json` (or similar)
- `tests/test_corpus_loader.py`
- `docs/CORPUS.md`

**Success Criteria:**
- Corpus loader handles 100+ verses
- Gold standard includes roots, patterns, features
- All corpus tests pass

---

### Task 3.5: Evaluation Metrics (2-3 days)

**Description:** Implement F1, precision, recall metrics for morphology evaluation.

**Subtasks:**
- [ ] 3.5.1: Implement F1 score calculation
- [ ] 3.5.2: Implement precision/recall for root extraction
- [ ] 3.5.3: Implement word-kind accuracy metric
- [ ] 3.5.4: Implement pattern matching accuracy
- [ ] 3.5.5: Build evaluation report generator
- [ ] 3.5.6: Run evaluation on corpus
- [ ] 3.5.7: Generate HTML/Markdown report
- [ ] 3.5.8: Add 5+ metric tests

**Files to Create:**
- `src/fvafk/evaluation/metrics.py`
- `src/fvafk/evaluation/report_generator.py`
- `tests/test_evaluation_metrics.py`
- `docs/CORPUS_EVALUATION.md`

**Success Criteria:**
- F1 score ≥ 0.85 for morphology
- Word-kind accuracy ≥ 90%
- Root extraction accuracy ≥ 80%
- Report generated successfully

---

## 📊 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| F1 score (morphology) | ≥ 0.85 | Against gold corpus |
| Word-kind accuracy | ≥ 90% | Noun/verb/particle classification |
| Root extraction accuracy | ≥ 80% | Correct trilateral/quadrilateral roots |
| Tests added | 20-30 | New test files |
| Total tests | ≥ 395 | 373 current + new tests |
| Documentation | Complete | All new features documented |

---

## 📁 Deliverables

### New Files (Minimum)
1. `src/fvafk/c2b/word_boundary_detector.py`
2. `src/fvafk/c2b/pattern_catalog.py`
3. `src/fvafk/corpus/corpus_loader.py`
4. `src/fvafk/corpus/gold_standard.py`
5. `src/fvafk/evaluation/metrics.py`
6. `src/fvafk/evaluation/report_generator.py`
7. `data/corpus/quran_100_verses.json`
8. `docs/MORPHOLOGY.md`
9. `docs/CORPUS.md`
10. `docs/CORPUS_EVALUATION.md`

### Modified Files
1. `app/models/word_form.py` (add morph_flags)
2. `src/fvafk/cli/main.py` (add flags to output)
3. `docs/CLI_SCHEMA.md` (document new fields)
4. `PROJECT_STATUS.md` (update progress)
5. `README.md` (update test count)

### Test Files (8+)
1. `tests/test_word_boundary_detector.py` (complete implementation)
2. `tests/test_pattern_catalog.py`
3. `tests/test_morph_flags.py`
4. `tests/test_corpus_loader.py`
5. `tests/test_evaluation_metrics.py`

---

## 🗓️ Timeline

| Week | Days | Tasks | Deliverables |
|------|------|-------|--------------|
| **Week 5** | Mon-Tue | Task 3.1 (Plan B detector) | WordBoundaryDetectorPlanB |
| | Wed | Task 3.2 (PatternCatalog) | PatternCatalog integration |
| | Thu | Task 3.3 (Morph flags) | Flags in CLI output |
| | Fri | Task 3.4 start (Corpus) | Corpus loader skeleton |
| **Week 6** | Mon-Tue | Task 3.4 complete | Gold corpus ready |
| | Wed-Thu | Task 3.5 (Metrics) | Evaluation report |
| | Fri | Testing & docs | Sprint 3 complete |

---

## 🔗 Dependencies

### Required Before Sprint 3
- [x] Sprint 1 (Foundation) - Complete
- [x] Sprint 2 (Phonology) - Complete
- [x] Syllabifier working - Complete
- [x] 373 tests passing - Complete

### Blocking Future Work
- [ ] Sprint 4 (TADMINI/TAQYIDI) - Requires stable morphology
- [ ] Sprint 5 (Constraints) - Requires evaluation metrics

---

## 🧪 Testing Strategy

### Unit Tests
- Test each component in isolation
- Edge cases for boundary detection
- Pattern matching accuracy
- Flag extraction correctness

### Integration Tests
- End-to-end corpus processing
- CLI output validation
- Metric calculation accuracy

### Property Tests
- Use Hypothesis for boundary detection
- Fuzz testing for pattern matching

---

## 📚 Resources

### Planning Documents
- `NEXT_STEPS.md` - Sprint 3 decision rationale
- `FUTURE_PLAN.md` - Remaining roadmap
- `MASTER_PLAN_CHECKLIST.md` - Complete task list
- `WHERE_WE_ARE_VS_PLAN_DETAILED.md` - Current status

### Technical References
- `docs/PHONOLOGY.md` - Gate system (Sprint 2)
- `docs/CLI_SCHEMA.md` - CLI interface
- `src/fvafk/c2b/syllabifier.py` - Reference for Plan B

### Corpus Sources (Recommendations)
1. **Quranic Arabic** - Most structured, best for initial testing
2. **Hadith** - Classical Arabic with varied vocabulary
3. **Modern Standard Arabic (MSA)** - Contemporary usage

---

## 🎬 Getting Started

### 1. Create Sprint 3 branch
```bash
git checkout main
git pull origin main
git checkout -b sprint3/morphology-corpus
```

### 2. Set up corpus directory
```bash
mkdir -p data/corpus
mkdir -p src/fvafk/corpus
mkdir -p src/fvafk/evaluation
```

### 3. Start with Task 3.1
Begin implementing `WordBoundaryDetectorPlanB` using the existing test file as a guide.

---

## ✅ Completion Checklist

Sprint 3 is complete when:
- [ ] All 5 tasks completed
- [ ] 20-30 new tests added (total ≥395)
- [ ] F1 ≥ 0.85 achieved
- [ ] All documentation updated
- [ ] PR created and reviewed
- [ ] Tests pass in CI
- [ ] Merged to main

---

## 📝 Notes

- **Corpus Choice:** Start with 100 Quranic verses for consistency and structure
- **Evaluation Focus:** Prioritize morphology accuracy over speed in Sprint 3
- **Documentation:** Keep MORPHOLOGY.md and CORPUS.md up-to-date as you go
- **Testing:** Write tests before implementation (TDD approach recommended)

---

**Created:** 2026-02-19 08:59:18  
**Status:** Ready to Start  
**Assigned:** @sonaiso  
**Sprint:** 3 of 6