# Sprint 2: Phonology Gates Unification & Coq Skeletons

**Duration:** Weeks 3-4 (2 weeks)  
**Goal:** طبقة الصوتيات (C2a) كطبقة مرجعية نظيفة، موثوقة، ومُراقَبة

---


---

## 📊 Progress Update (Feb 15, 2026)

**Sprint 2, Week 3, Day 2 - Status:**

✅ **Completed Tasks:**
- Task 2.1.1: GateResult canonical shape (DONE)
- Task 2.1.2: Unified all gates (DONE - PhonologicalGate = BaseGate alias)
- Task 2.2.1: Syllabifier marked as reference (DONE)
- Task 2.2.2: Integration tests syllabifier vs Phonology V2 (DONE - 16 new tests)
- Housekeeping: Added utility files, updated .gitignore

**Test Count:** 333 passing ✅ (was 317, +16 new)

**Commits Today:**
1. `7052bd7` - docs(sprint2): Mark syllabifier as reference implementation
2. `992556b` - test(sprint2): Add syllabifier vs Phonology V2 integration tests

**Next Up:**
- Task 2.3.1: Property tests with Hypothesis (Gate invariants)

**Estimated Progress:** 55% of Sprint 2 complete (5/9 tasks)

---
## 🎯 Acceptance Criteria

✔️ جميع بوابات C2a لها واجهة موحّدة  
✔️ syllabifier موحّد ومربوط رسميًا بـ Phonology V2  
✔️ لا تغييرات سلوكية غير مقصودة (Golden tests)  
✔️ Trace صوتي قابل للتدقيق  
✔️ Skeleton Coq موجود (حتى لو Admitted)  
✔️ CI أخضر (pytest + property tests)

---

## 📋 Task Breakdown

### Part 2.1: Gate Interface Unification

**Task 2.1.1 — GateResult Canonical Shape** (3-4h)
- File: `src/fvafk/c2a/gate_framework.py`
- Standardize GateResult: status, input_units, output_units, delta, time_ms, notes

**Task 2.1.2 — Unify All Gates** (3-4h)
- 11 gates: Sukun, Shadda, Tanwin, Hamza, Wasl, Waqf, Idgham, Madd, Assimilation, Deletion, Epenthesis
- All inherit from BaseGate, return GateResult

---

### Part 2.2: Reference Syllabifier

**Task 2.2.1 — Syllabifier as Reference** (2-3h)
- File: `src/fvafk/c2a/syllabifier.py`
- Document CV/CVV/CVC patterns
- Link to FormCodecV2 and Phonology V2

**Task 2.2.2 — Test Against Phonology V2** (2h)
- Test cases: كَتَبَ, السَّمَاوَات, يَبْتَغُونَ, أَشِدَّاءُ
- Verify: c1.cv_analysis == phonology_v2 == syllabifier

---

### Part 2.3: Property Tests

**Task 2.3.1 — Gate Invariants with Hypothesis** (4-5h)
- عدد الوحدات لا يصبح صفرًا
- ترتيب الصوامت محفوظ
- لا تظهر CCC بعد gates
- الحركات لا تُنشأ بدون سبب

---

### Part 2.4: Trace Integration

**Task 2.4.1 — Phonology V2 Trace** (3h)
- Log before/after for each gate
- Record reason for changes
- Link to existing Trace V1

---

### Part 2.5: Coq Skeletons

**Task 2.5.1 — Create Coq Files** (3-4h)
- coq/Gates/GateSukun.v
- coq/Gates/GateShadda.v
- coq/Gates/GateTanwin.v
- Each with Definition + Lemma (Admitted)

---

### Part 2.6: CI Integration

**Task 2.6.1 — CI for Phonology** (2h)
- Add CI job: pytest + property tests
- Optional: Coq build
- Block PR if tests fail

---

### Part 2.7: Cleanup & Docs

**Task 2.7.1 — Remove Duplication** (1-2h)
- Remove duplicate syllabifier code
- Unify CV logic

**Task 2.7.2 — Create PHONOLOGY.md** (2h)
- What are gates?
- Gate order
- Invariants
- How to add new gate

---

## 📊 Timeline (2 Weeks)

**Week 3:**
- Day 1-2: Gate Interface (2.1.1, 2.1.2)
- Day 3-4: Syllabifier (2.2.1, 2.2.2)
- Day 5: Property Tests Setup (2.3.1 partial)

**Week 4:**
- Day 1-2: Property Tests Complete (2.3.1)
- Day 3: Trace (2.4.1)
- Day 4: Coq Skeletons (2.5.1)
- Day 5: CI + Cleanup + Docs (2.6.1, 2.7.1, 2.7.2)

---

## ✅ Definition of Done

- [x] كل Gates موحّدة (11 gates) ✅ Task 2.1.1, 2.1.2 DONE
- [x] syllabifier مرجعي واحد ✅ Task 2.2.1 DONE
- [x] syllabifier integration tests ✅ Task 2.2.2 DONE (16 new tests)
- [ ] trace صوتي كامل (Task 2.4.1)
- [ ] property tests موجودة (Task 2.3.1)
- [ ] Coq skeleton جاهز (3 gates) (Task 2.5.1)
- [x] لا تغيير في ناتج CLI ✅ 333 tests passing
- [x] CI أخضر ✅ All tests green
- [ ] docs/PHONOLOGY.md موجود (Task 2.7.2)

**Progress:** 5/9 tasks complete (55%)

---

## 📦 Deliverables

**Code:**
- 11 unified gates with BaseGate
- Reference syllabifier (single source)
- Property tests (Hypothesis)
- Trace integration
- 3 Coq skeleton files

**Tests:**
- Golden tests (no behavioral changes)
- 4+ property test invariants
- Syllabifier integration tests

**Docs:**
- docs/PHONOLOGY.md
- Coq skeleton README

**CI:**
- GitHub Actions workflow
- Pytest + property tests

---

## 🚀 Getting Started

**First Task: 2.1.1 (GateResult)**

```bash
# 1. Inspect current implementation
cat src/fvafk/c2a/gate_framework.py

# 2. Review all gates
ls src/fvafk/c2a/gates/

# 3. Run baseline tests
pytest tests/test_gate_*.py -v

# 4. Create branch
git checkout -b sprint2/gate-unification
```

---

*Sprint 1: 100% Complete ✅*  
*Ready for Sprint 2: YES ✅*  
*Last updated: 2026-02-15*
