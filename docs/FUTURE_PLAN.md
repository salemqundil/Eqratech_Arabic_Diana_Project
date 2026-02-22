# FVAFK — Future Plan (Post–Sprint 2)

**Current:** Sprint 1 ✅ Sprint 2 ✅ | **Tests:** 373

---

## Roadmap (remaining)

| Sprint | Focus | Key deliverable |
|--------|--------|------------------|
| **3** | Morphology + corpus | WordBoundaryDetector Plan B, PatternCatalog, morph_flags, gold corpus, F1 ≥ 0.85 |
| **4** | Syntax linkers | TADMINI, TAQYIDI, SyntacticParser, EventExtractor, UAS/LAS |
| **5** | Constraints | 5–6 constraints, ConstraintValidator, Coq predicates |
| **6** | Integration + ops | Full pipeline, batch/cache, corpus reports, FastAPI, CI/CD, docs |

---

## Optional: Part 2.5 (Semantic gates)

- semantic_gates_wrapper, EvidenceWeight, RealityLink
- assurance_mode (strict/relaxed), evidence accept rules
- Can run alongside Sprint 3

---

## Suggested order

1. Merge sprint2/gate-unification → main
2. Next: **Sprint 3** (morphology) **or** **Sprint 4** (TADMINI/TAQYIDI) **or** Part 2.5 (semantic)
3. Then: Sprint 5 → Sprint 6

---

**Refs:** MASTER_PLAN_CHECKLIST.md, ENHANCED_ROADMAP.md, WHERE_WE_ARE_VS_PLAN_DETAILED.md
