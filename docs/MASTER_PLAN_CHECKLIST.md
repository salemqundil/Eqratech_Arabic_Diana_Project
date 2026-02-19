# FVAFK / Bayan – Master Plan Checklist

Single checklist for foundation, phonology, semantics, morphology, syntax, constraints, and integration. Track via GitHub issues; link dependencies.

**Sprint mapping:** Sprint 1 (Weeks 1–2) … Sprint 6 (Weeks 11–14). See **ENHANCED_ROADMAP.md** for deliverables and **PROJECT_STATUS.md** for current state.

---

## Part 1: Foundation and packaging

| # | Task | Sprint | Notes |
|---|------|--------|------|
| 1.1 | Add `pyproject.toml`; align minimal requirements | 1 | |
| 1.2 | Package modules into typed Python library (bayan-fvafk) | 1 | |
| 1.3 | Define Pydantic models: Unit, Syllable, WordForm, Link, Evidence, ProofArtifact, AnalysisResult | 1 | |
| 1.4 | Integrate OrthographyAdapter with FormCodecV2; enforce reversibility (encode/decode) | 1 | |
| 1.5 | Align directories: `theories/`, `docs/`, `app/`, `cli/`, `tests/` | 1 | |
| 1.6 | Update docs to reflect packaging/models | 1 | |
| 1.7 | Extend `fvafk.cli` to output JSON: tokens, WordForm, ISNADI links | 1 | **CLI with syntax** |
| 1.8 | Add 10+ unit tests for CLI outputs | 1 | |
| 1.9 | Document CLI schema and example outputs | 1 | |

---

## Part 2: Phonology gates and Coq skeletons

| # | Task | Sprint | Notes |
|---|------|--------|------|
| 2.1 | Implement/refactor 10+ gate classes (incl. GateWasl) with status/timing/deltas | 2 | |
| 2.2 | Add OrthographyAdapter rules (hamzat al-wasl, taa marbuta, alef maqsurah, tanwin-in-waqf) | 2 | |
| 2.3 | Implement syllabifier consistent with CV/CVV/CVC taxonomy | 2 | |
| 2.4 | Start Coq skeletons for GateSukun, GateShadda, GateTanwin (Admitted initially) | 2 | |
| 2.5 | CI job to compile Coq subset; add property tests for well-formedness/preservation | 2 | |

---

## Part 2.5: Semantic gates and evidence integration

| # | Task | Sprint | Notes |
|---|------|--------|------|
| 2.5.1 | Integrate Bayan’s semantic_gates_wrapper as base | 2–3 | |
| 2.5.2 | Implement EvidenceWeight composition and RealityLink checks | 2–3 | |
| 2.5.3 | Define accept criteria: evidence.score ≥ 0.5 AND scope_ok AND truth_ok AND reference_ok | 2–3 | |
| 2.5.4 | Add falsifiability protocol and property-based tests | 2–3 | |
| 2.5.5 | Add assurance_mode flag (strict vs relaxed) in CLI/API; document evidence weights and accept rules | 2–3 | |

---

## Part 3: Morphology analyzer and corpus metrics

| # | Task | Sprint | Notes |
|---|------|--------|------|
| 3.1 | Refine WordBoundaryDetector; add Plan B boundaries from syllables | 3 | |
| 3.2 | Map PatternAnalyzer and root extractor to Bayan’s PatternCatalog/PatternUniverse | 3 | |
| 3.3 | Integrate WordClassifier; expose morph_flags (case, definite, number, gender) | 3 | |
| 3.4 | Build gold corpus loader (Quran/Hadith/MSA); compute F1 ≥ 0.85; test iʿrab and root accuracy | 3 | |

---

## Part 4: Syntax linkers, parser, and events

| # | Task | Sprint | Notes |
|---|------|--------|------|
| 4.1 | Build/finalize ISNADI, TADMINI, TAQYIDI linkers as classes | 4 | |
| 4.2 | Create SyntacticParser orchestrator; combine links/errors; wire outputs to CLI JSON | 4 | |
| 4.3 | Implement EventExtractor (verb events, participants, time/place refs); attach events to traces | 4 | |
| 4.4 | Add simple visualization for links in CLI output | 4 | |

---

## Part 5: Constraints, validator, and Coq predicates

| # | Task | Sprint | Notes |
|---|------|--------|------|
| 5.1 | No verb without subject | 5 | |
| 5.2 | No transitive without object | 5 | |
| 5.3 | Adjective–noun agreement | 5 | |
| 5.4 | Causality requires events | 5 | |
| 5.5 | Passive requires morphology + deputy subject | 5 | |
| 5.6 | Sixth constraint: Amil-Sign Rules (no iʿrab without operator; no operator without link) | 5 | |
| 5.7 | Build ConstraintValidator (violations + reports) | 5 | |
| 5.8 | Add property tests; create Coq predicates for each constraint (compile in CI; close proofs iteratively) | 5 | |

---

## Part 6: Integration, evaluation, performance, proof mode, ops

| # | Task | Sprint | Notes |
|---|------|--------|------|
| 6.1 | CompletePipeline wiring C1→C2a→C2b→C2c→C3 with timing/stats | 6 | |
| 6.2 | Add batch processing and LRU caching utilities | 6 | |
| 6.3 | Corpus evaluation (100 ayahs + 50 hadith + 50 MSA): accept rate, latency, morphology F1, UAS/LAS; performance and accuracy reports | 6 | |
| 6.4 | Strict assurance mode: integrate coq_exporter/coq_proof_checker; attach proof artifacts; safe fallback when path touches Admitted | 6 | |
| 6.5 | Graph export: neo4j_exporter; sample queries and docs | 6 | |
| 6.6 | CI/CD and Docker: GitHub Actions for Coq subset, Python tests, lint/typecheck, Docker build; deploy FastAPI service; logging/monitoring | 6 | |
| 6.7 | Documentation and hygiene: SPEC, ARCHITECTURE, GATES, CONSTRAINTS, TRACE, EVIDENCE, EXAMPLES, PERFORMANCE_REPORT, ACCURACY_REPORT; update WHERE_WE_ARE_VS_PLAN.md; clean duplicates and repo split; LICENSE, SECURITY, CONTRIBUTING, CODE_OF_CONDUCT | 6 | |

---

## Sprint milestones (weeks)

| Sprint | Weeks | Focus | Key outcomes |
|--------|--------|--------|----------------|
| **Sprint 1** | 1–2 | Part 1 + ISNADI in CLI, packaging, hygiene/docs, initial tests | pyproject.toml, bayan-fvafk scaffold, Pydantic models, CLI JSON with tokens/WordForm/ISNADI, 10+ CLI tests, docs |
| **Sprint 2** | 3–4 | Part 2 phonology + Coq skeletons, property tests, syllabifier | 10+ gates refactored, OrthographyAdapter rules, syllabifier CV/CVV/CVC, Coq skeletons (Sukun, Shadda, Tanwin), CI Coq + property tests |
| **Sprint 3** | 5–6 | Part 3 morphology bridge to Bayan patterns; corpus F1; WordForm flags | WordBoundaryDetector Plan B, PatternCatalog/PatternUniverse bridge, morph_flags, gold corpus loader, F1 ≥ 0.85 |
| **Sprint 4** | 7–8 | Part 4 syntax linkers + events; parser; UAS/LAS; visualization | ISNADI/TADMINI/TAQYIDI final, SyntacticParser, EventExtractor, link visualization, UAS/LAS |
| **Sprint 5** | 9–10 | Part 5 constraints + validator; Coq predicates; C2c integration | Five constraints + Amil-Sign, ConstraintValidator, property tests, Coq predicates in CI |
| **Sprint 6** | 11–14 | Part 6 integration, corpus eval, performance, proof mode, graph, FastAPI, CI/CD, docs | Full pipeline, batch/cache, corpus reports, proof mode, neo4j export, FastAPI, GitHub Actions, Docker, full doc set |

---

## Dependencies (high level)

- **Part 1** blocks Parts 2–6 (scaffold and CLI with syntax).
- **Part 2** blocks Part 2.5 (semantic gates use phonology); Part 2.5 can overlap with Part 3.
- **Part 3** blocks Part 4 (morphology feeds syntax linkers).
- **Part 4** blocks Part 5 (constraints need links).
- **Part 5** blocks Part 6 (full pipeline and assurance mode).

---

## References

- **ENHANCED_ROADMAP.md** – Sprint deliverables and success metrics.
- **PROJECT_STATUS.md** – Current progress and gaps.
- **WHERE_WE_ARE_VS_PLAN.md** – Phase-by-phase status vs master plan.
- **project_deleverables.md** – Living deliverables (Arabic + English).

---

*Last updated: 2026-02-01. Convert to GitHub issues with labels, priorities, and dependency links as needed.*
