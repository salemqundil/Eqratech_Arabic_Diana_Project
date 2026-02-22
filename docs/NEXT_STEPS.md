# FVAFK — Next Steps and Priorities

**Date:** 2026-02-16  
**Current Status:** Sprint 1 ✅, Sprint 2 ✅ (373 tests passed, 1 skipped)  
**Branch:** sprint2/gate-unification (ready for merge)

---

## Immediate Actions (Priority 1)

### 1. Merge Sprint 2 Branch
```bash
# Review and merge sprint2/gate-unification → main
git checkout main
git merge sprint2/gate-unification
git push origin main
```

**Deliverables included:**
- 11 gates unified with BaseGate
- GateResult canonical shape (input_units, output_units, delta, time_ms)
- Reference syllabifier with CV/CVV/CVC documentation
- 25 property tests with Hypothesis
- Phonology trace integration (15 tests)
- 3 Coq skeletons (GateSukun.v, GateShadda.v, GateTanwin.v)
- CI integration (pytest + coqc)
- docs/PHONOLOGY.md

### 2. Update Documentation
- ✅ PROJECT_STATUS.md updated (373 tests, Sprint 2 complete)
- ✅ WHERE_WE_ARE_VS_PLAN.md updated
- ✅ ENHANCED_ROADMAP.md updated
- ✅ WHERE_WE_ARE_VS_PLAN_DETAILED.md created
- ✅ FUTURE_PLAN.md created
- [ ] Update README.md with current test count
- [ ] Update project_deleverables.md if needed

---

## Sprint 3 Options (Choose One)

### Option A: Part 3 — Morphology + Corpus (Recommended)
**Duration:** 2 weeks (Weeks 5-6)  
**Focus:** Complete morphology layer and establish evaluation metrics

**Tasks:**
1. WordBoundaryDetector Plan B (from syllables)
2. PatternCatalog integration with Bayan's PatternUniverse
3. morph_flags exposure (case, definite, number, gender)
4. Gold corpus loader (Quran/Hadith/MSA)
5. Compute F1 ≥ 0.85 for morphology

**Why this option:**
- Completes the foundation layers (C1 → C2a → C2b)
- Establishes evaluation methodology
- Required before syntax expansion

### Option B: Part 2.5 — Semantic Gates
**Duration:** 1-2 weeks (can overlap with Sprint 3)  
**Focus:** Evidence and reality integration

**Tasks:**
1. semantic_gates_wrapper integration
2. EvidenceWeight composition
3. RealityLink checks
4. Accept criteria (evidence.score ≥ 0.5 + scope/truth/reference)
5. Falsifiability protocol
6. assurance_mode flag (strict/relaxed)

**Why this option:**
- Independent of morphology/syntax
- Can run in parallel with other work
- Smaller scope, faster completion

### Option C: Part 4 — TADMINI/TAQYIDI Syntax
**Duration:** 2 weeks (Weeks 7-8)  
**Focus:** Complete syntax linkers

**Tasks:**
1. TADMINI linker (transitive verb → object)
2. TAQYIDI linker (noun→adjective, noun→mudhaf ilayh)
3. SyntacticParser orchestrator
4. EventExtractor implementation
5. Link visualization

**Why this option:**
- Builds on existing ISNADI implementation
- High value for syntax analysis
- Requires morphology to be stable

---

## Recommended Sequence

**Immediate (Week 5):**
1. Merge sprint2/gate-unification
2. Choose next sprint focus

**Best Path Forward:**
```
Week 5-6:   Sprint 3 (Morphology + Corpus) — Option A
Week 7-8:   Sprint 4 (TADMINI/TAQYIDI) — Option C  
Week 9-10:  Sprint 5 (Constraints)
Week 11-14: Sprint 6 (Integration)
```

**Alternative (if morphology corpus is complex):**
```
Week 5:     Part 2.5 (Semantic gates) — Option B
Week 5-6:   Sprint 3 (Morphology + Corpus) — Option A (parallel)
Week 7-8:   Sprint 4 (TADMINI/TAQYIDI) — Option C
Week 9-10:  Sprint 5 (Constraints)
Week 11-14: Sprint 6 (Integration)
```

---

## Success Metrics (Sprint 3)

If choosing Option A (Morphology + Corpus):

| Metric | Target |
|--------|--------|
| F1 score (morphology) | ≥ 0.85 |
| Word-kind accuracy | ≥ 90% |
| Root extraction accuracy | ≥ 80% |
| Tests added | 20-30 |
| Total tests | ≥ 395 |
| Documentation | Corpus evaluation report |

---

## Outstanding Questions

1. **Corpus Source:** Which corpus to use for evaluation?
   - Quranic Arabic (most structured)
   - Hadith (classical Arabic)
   - Modern Standard Arabic (MSA)
   - Recommendation: Start with 100 Quranic verses

2. **Evaluation Tools:** Manual annotation or automated?
   - Need gold standard for morphology (roots, patterns, features)
   - Consider using existing Arabic NLP datasets

3. **Part 2.5 Priority:** Can semantic gates wait?
   - Yes, if focus is on core NLP layers first
   - No, if evidence/reality modeling is critical

---

## Resources and References

**Planning Documents:**
- `docs/MASTER_PLAN_CHECKLIST.md` — Full 6-part task list
- `ENHANCED_ROADMAP.md` — 6-sprint timeline
- `WHERE_WE_ARE_VS_PLAN_DETAILED.md` — Sprint 2 completion report
- `FUTURE_PLAN.md` — Remaining work summary
- `docs/SPRINT2_PLAN.md` — Sprint 2 detailed plan (✅ complete)

**Technical Documentation:**
- `docs/PHONOLOGY.md` — Gate system documentation
- `docs/CLI_SCHEMA.md` — CLI interface specification
- `coq/Gates/` — Coq skeleton files

**Status Reports:**
- `PROJECT_STATUS.md` — Single source of truth
- `WHERE_WE_ARE_VS_PLAN.md` — Phase-by-phase status

---

## Decision Matrix

| Option | Effort | Impact | Blocking | Risk |
|--------|--------|--------|----------|------|
| **A: Morphology + Corpus** | High (2 weeks) | High | Nothing | Medium (corpus complexity) |
| **B: Semantic Gates** | Low (1 week) | Medium | Nothing | Low |
| **C: TADMINI/TAQYIDI** | Medium (2 weeks) | High | Morphology stability | Low |

**Recommendation:** Option A (Morphology + Corpus) to complete foundation, then Option C (TADMINI/TAQYIDI).

---

*Document created: 2026-02-16*  
*For questions or updates, see PROJECT_STATUS.md*
