# Current vs New Plan: Gaps and Overlaps

This document analyses the **current FVAFK state** and **existing plan docs** against the **6-phase enhancement roadmap** (from the master plan: Infrastructure → Gates → Morphology → Syntax → Constraints → Integration) to produce a merged, dependency-clear plan.

---

## 1. Current state (what we have)

| Component | Status | Location / notes |
|-----------|--------|-------------------|
| CLI C1→C2a→C2b | ✅ Working | `src/fvafk/cli/main.py` |
| WordForm bridge | ✅ Implemented | `c2b/word_form.py`, `word_form_builder.py`, `word_form_validator.py` |
| ISNADI V1 | ✅ In package | `syntax/linkers/isnadi_linker.py` |
| ISNADI V1.1 | ✅ Working (phrase-skip) | `tools/isnadi_linker_v1_1.py` or similar; tests may load from tools |
| Phonology V2 | ✅ In CLI | `--phonology-v2`, `--phonology-v2-details`, `--phonology-v2-witnesses` |
| Tests | ✅ 269 passing, CI green | `tests/` |
| Structure | ✅ | `src/fvafk/`, `tests/`, `docs/` |

**Current plan docs:**

- **INTEGRATION_PLAN.md** – Phonology V2 integration (copy, adapter, CLI, tests); 10 phases; mostly **done**.
- **INTEGRATION_ROADMAP.md** – Not found in repo (to be created or referenced from ENHANCED_ROADMAP).
- **PROJECT_STATUS.md** – Not found in repo (to be created).
- **project_deleverables.md** – Living deliverables; says 229 tests (update to 269); lists C1–C2b and gaps.

---

## 2. New enhancement roadmap (6-phase reference)

The **new** roadmap is the **6-phase plan** from the master plan (🎯 خطة شاملة...):

| Phase | Name | Plan scope | Original timeline |
|-------|------|------------|-------------------|
| 1 | Infrastructure | Segment inventory, syllable system, gate framework, OrthographyAdapter, codec, trace | Week 1–2 |
| 2 | Phonological gates | 10 gates, 100+ tests, Coq (optional) | Week 3–5 |
| 3 | Morphology | Word boundary, pattern, classifier, root, features, F1≥0.85 | Week 6–8 |
| 4 | Syntax | ISNADI, TADMINI, TAQYIDI, parser, UAS≥0.80 | Week 9–11 |
| 5 | Constraints | 5–6 constraints, validator | Week 12–13 |
| 6 | Integration | Full pipeline, CLI, corpus, C2c, docs | Week 14–17 |

---

## 3. Gaps (plan asks for it; we don’t have it)

| # | Gap | Phase | Priority | Blocks |
|---|-----|--------|----------|--------|
| G1 | **Syntax in CLI** – build WordForms from C2b, run ISNADI, add `result["syntax"]` | 4 | P0 | Using ISNADI in production |
| G2 | **TADMINI linker** – transitive verb → object | 4 | P1 | Parser, constraints |
| G3 | **TAQYIDI linker** – noun→adjective, noun→mudhaf ilayh | 4 | P1 | Parser, constraints |
| G4 | **SyntacticParser** – orchestrate ISNADI → TADMINI → TAQYIDI, return links + errors | 4 | P1 | Constraints, corpus |
| G5 | **5–6 constraint modules** – verb–subject, transitive–object, adjective agreement, causality, passive, (Amil-Sign) | 5 | P1 | Phase 6 validation |
| G6 | **Constraint validator** – input: wordforms + links → output: violations | 5 | P1 | Phase 6 |
| G7 | **Corpus evaluation** – F1 morphology, UAS/LAS syntax, violation counts | 6 | P1 | Metrics, regression |
| G8 | **C2c (semantic gate)** – evidence, falsifiability, accept/reject | 6 | P2 | Meaning layer |
| G9 | **Plan B word boundaries** – from syllable stream (optional) | 3 | P2 | Not blocking |
| G10 | **Coq / formal proofs** – 50+ theorems (optional for this repo) | 1–5 | P2 | Out of scope for MVP |
| G11 | **PROJECT_STATUS.md / INTEGRATION_ROADMAP** – single source of truth | Doc | P0 | Clarity |
| G12 | **Test count 300+** – add ~31 tests to reach 300 | 6 | P2 | Plan target |

---

## 4. Overlaps (we have it; plan also mentions it)

| # | Overlap | Resolution |
|----|--------|------------|
| O1 | **C1 / Infrastructure** | Keep as-is; no rework. Mark Phase 1 complete. |
| O2 | **C2a / 10 gates** | Keep as-is. Mark Phase 2 complete. |
| O3 | **C2b / Morphology** | Keep as-is. Mark Phase 3 complete. Add only: corpus F1 later. |
| O4 | **ISNADI + WordForm** | Keep; only **wire into CLI** (G1). |
| O5 | **Phonology V2** | Already in INTEGRATION_PLAN; mark done. New milestones in INTEGRATION_PLAN = post-Phonology (syntax, constraints, corpus). |
| O6 | **CLI** | Keep; extend with `--syntax` or syntax block when morphology is on. |

---

## 5. Dependencies (critical path)

```
Current code (C1, C2a, C2b, WordForm, ISNADI)
    │
    ├─► [G1] Syntax in CLI  ──────────────────────────────────────────► [G7] Corpus eval (syntax)
    │         │
    │         ├─► [G2] TADMINI  ──┐
    │         ├─► [G3] TAQYIDI  ──┼─► [G4] SyntacticParser ─► [G5,G6] Constraints ─► [G7] Corpus
    │         └─► ISNADI (done)  ──┘
    │
    └─► [G11] PROJECT_STATUS / ENHANCED_ROADMAP (docs, no code dep)
```

**Critical path:** G1 (syntax in CLI) → G2/G3 → G4 → G5/G6 → G7. G1 is the single highest-leverage item.

---

## 6. What to preserve (no breaking changes)

- All existing tests (269); CI must stay green.
- CLI flags and JSON shape for C1/C2a/C2b (additive only: e.g. `result["syntax"]`).
- WordForm and ISNADI APIs (call from CLI, don’t replace).
- Phonology V2 integration (already done per INTEGRATION_PLAN).
- Incremental PRs: one feature per PR where possible (syntax in CLI, then TADMINI, then TAQYIDI, then parser, then constraints).

---

## 7. Summary: changes to existing plans

| Doc | Change |
|-----|--------|
| **INTEGRATION_PLAN.md** | Add “Post-integration milestones” section: Syntax in CLI, TADMINI/TAQYIDI, parser, constraints, corpus. Link to ENHANCED_ROADMAP.md. |
| **project_deleverables.md** | Update test count to 269; add “Syntax in CLI” and “ISNADI in pipeline” to next priorities; add reference to ENHANCED_ROADMAP and PROJECT_STATUS. |
| **New: PROJECT_STATUS.md** | Create: current progress (269 tests, C1–C2b, WordForm, ISNADI), roadmap pointer, critical path. |
| **New: ENHANCED_ROADMAP.md** | Create: 6-month plan, 6 sprints, dependencies, timelines, GitHub milestones/issues, this-week actions. |

No big-bang change; all additive and documented.
