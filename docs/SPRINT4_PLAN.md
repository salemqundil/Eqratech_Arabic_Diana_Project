# Sprint 4 Plan: Syntax Layer Foundation

**Duration:** 2 weeks (Weeks 7-8)  
**Status:** 🎯 Ready to Start  
**Prerequisites:** ✅ Sprint 3 Complete (498 tests passing)  
**Current Status:** I3rab corpus ready (77,374 words)

---

## 🎯 Sprint Goals

1. Design and implement Syntax data models (I3rab representation)
2. Build I3rab corpus loader using existing `data/i3rab/quran_i3rab.csv`
3. Create Syntax evaluation framework
4. Build Morphology-Syntax integration bridge
5. Achieve ≥85% I3rab extraction accuracy

---

## 📋 Tasks Breakdown

### Task 4.1: Syntax Data Model (3 days)

**Description:** Design and implement the core data structures for I3rab (syntactic case) representation.

**Subtasks:**
- [ ] 4.1.1: Design I3rab data structures (Case, I3rabType, SyntaxFeatures)
- [ ] 4.1.2: Create Pydantic models for syntax representation
- [ ] 4.1.3: Define syntax-morphology relationship
- [ ] 4.1.4: Add 10+ unit tests
- [ ] 4.1.5: Document in `docs/SYNTAX.md`

**Files to Create:**
- `src/fvafk/c2b/syntax/models.py`
- `src/fvafk/c2b/syntax/__init__.py`
- `tests/test_syntax_models.py`
- `docs/SYNTAX.md`

**Success Criteria:**
- All syntax models defined with proper typing
- Models integrate with existing WordForm
- All tests pass

---

### Task 4.2: I3rab Corpus Loader (2-3 days)

**Description:** Load and parse the Quranic I3rab corpus to serve as gold-standard evaluation data.

**Subtasks:**
- [ ] 4.2.1: Load and parse `data/i3rab/quran_i3rab.csv`
- [ ] 4.2.2: Map I3rab annotations to syntax models
- [ ] 4.2.3: Handle special cases (e.g., محل له من الإعراب)
- [ ] 4.2.4: Validate corpus integrity
- [ ] 4.2.5: Add 8+ tests

**Files to Create:**
- `src/fvafk/c2b/corpus/i3rab_loader.py`
- `tests/test_i3rab_loader.py`
- Update `docs/CORPUS.md` with I3rab section

**Success Criteria:**
- All 77,374 words loaded successfully
- I3rab cases correctly mapped
- Coverage report shows >95% parsing success

---

### Task 4.3: Syntax Evaluator (3 days)

**Description:** Implement evaluation framework to measure I3rab extraction accuracy against the gold corpus.

**Subtasks:**
- [ ] 4.3.1: Implement I3rab extraction from WordForm
- [ ] 4.3.2: Create SyntaxEvaluator similar to MorphologyEvaluator
- [ ] 4.3.3: Calculate accuracy metrics for I3rab prediction
- [ ] 4.3.4: Generate I3rab evaluation reports
- [ ] 4.3.5: Add 10+ tests

**Files to Create:**
- `src/fvafk/c2b/evaluation/syntax_evaluator.py`
- `src/fvafk/c2b/syntax/i3rab_extractor.py`
- `tests/test_syntax_evaluator.py`
- `docs/SYNTAX_EVALUATION.md`

**Success Criteria:**
- I3rab evaluator works end-to-end
- Metrics include case accuracy, i3rab type accuracy
- Report generation successful

---

### Task 4.4: Morphology-Syntax Bridge (2 days)

**Description:** Connect morphological features to syntax predictions, enabling inference of I3rab from morphological markers.

**Subtasks:**
- [ ] 4.4.1: Connect morphological features to syntax predictions
- [ ] 4.4.2: Use case markers (tanween, etc.) to infer I3rab
- [ ] 4.4.3: Implement confidence scoring
- [ ] 4.4.4: Add integration tests
- [ ] 4.4.5: Update CLI to show syntax output

**Files to Create/Modify:**
- `src/fvafk/c2b/syntax/morph_syntax_bridge.py`
- `tests/test_morph_syntax_integration.py`
- Update `src/fvafk/cli/main.py` (add --syntax flag)
- Update `docs/CLI_SCHEMA.md`

**Success Criteria:**
- Morphology features correctly mapped to syntax
- CLI outputs I3rab information
- Integration tests pass

---

## 📊 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| I3rab extraction accuracy | ≥ 85% | Against gold corpus |
| Case marking accuracy | ≥ 90% | Nominative/accusative/genitive |
| Coverage | ≥ 95% | Words with I3rab extracted |
| Tests added | 30-40 | New test files |
| Total tests | ≥ 530 | 498 current + new tests |
| Documentation | Complete | All new features documented |

---

## 📁 Deliverables

### New Files (10+)
1. `src/fvafk/c2b/syntax/__init__.py`
2. `src/fvafk/c2b/syntax/models.py`
3. `src/fvafk/c2b/syntax/i3rab_extractor.py`
4. `src/fvafk/c2b/syntax/morph_syntax_bridge.py`
5. `src/fvafk/c2b/corpus/i3rab_loader.py`
6. `src/fvafk/c2b/evaluation/syntax_evaluator.py`
7. `docs/SYNTAX.md`
8. `docs/SYNTAX_EVALUATION.md`
9. `tests/test_syntax_models.py`
10. `tests/test_i3rab_loader.py`
11. `tests/test_syntax_evaluator.py`
12. `tests/test_morph_syntax_integration.py`

### Modified Files
1. `src/fvafk/cli/main.py` (add --syntax flag)
2. `docs/CLI_SCHEMA.md` (document syntax output)
3. `docs/CORPUS.md` (add I3rab section)
4. `PROJECT_STATUS.md` (update progress)
5. `README.md` (update test count)

---

## 🗓️ Timeline

| Week | Days | Tasks | Deliverables |
|------|------|-------|--------------|
| **Week 7** | Mon-Wed | Task 4.1 (Syntax models) | Data models complete |
| | Thu-Fri | Task 4.2 start (I3rab loader) | Loader skeleton |
| **Week 8** | Mon | Task 4.2 complete | Corpus loaded |
| | Tue-Thu | Task 4.3 (Evaluator) | Syntax evaluation working |
| | Fri | Task 4.4 (Bridge) | Integration complete |

---

## 🔗 Dependencies

### Required Before Sprint 4
- [x] Sprint 3 complete - ✅ Done
- [x] I3rab corpus ready - ✅ data/i3rab/quran_i3rab.csv (77,374 words)
- [x] Evaluation framework - ✅ MorphologyEvaluator
- [x] 498 tests passing - ✅ Complete

### Blocking Future Work
- [ ] Sprint 5 (Semantic layer) - Requires syntax foundation
- [ ] Sprint 6 (Full integration) - Requires all layers

---

## 🧪 Testing Strategy

### Unit Tests
- Test syntax models in isolation
- I3rab case mapping accuracy
- Extractor correctness

### Integration Tests
- End-to-end corpus processing
- Morphology → Syntax pipeline
- CLI output validation

### Corpus Tests
- Validate against 77,374 words
- Edge case handling
- Coverage metrics

---

## 🎬 Getting Started

```bash
# 1. Create Sprint 4 branch
git checkout main
git pull origin main
git checkout -b sprint4/syntax-foundation

# 2. Set up syntax directory
mkdir -p src/fvafk/c2b/syntax
touch src/fvafk/c2b/syntax/__init__.py

# 3. Verify corpus exists
ls -lh data/i3rab/quran_i3rab.csv

# 4. Start with Task 4.1
# Create syntax data models
```

---

## ✅ Completion Checklist

Sprint 4 is complete when:
- [ ] All 4 tasks completed
- [ ] 30-40 new tests added (total ≥530)
- [ ] I3rab accuracy ≥85%
- [ ] All documentation updated
- [ ] PR created and reviewed
- [ ] Tests pass in CI
- [ ] Merged to main

---

## 📝 Notes

- **Corpus Advantage:** We already have 77,374 annotated words - huge head start!
- **I3rab Focus:** This is unique compared to other morphology tools
- **Research Value:** Syntax evaluation is rare in Arabic NLP tools
- **Testing:** Use TDD - write tests before implementation
- **Documentation:** Keep SYNTAX.md updated as you build

---

**Created:** 2026-02-21  
**Status:** Ready to Start  
**Assigned:** @sonaiso  
**Sprint:** 4 of 6  
**Previous Sprint:** Sprint 3 (Morphology + Corpus) - ✅ Complete
