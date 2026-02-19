# FVAFK Enhanced Roadmap (6-Month Plan)

---

## Executive summary

The FVAFK pipeline today has **C1→C2a→C2b** in the CLI, **WordForm** and **ISNADI** implemented, and **269 tests** passing. This roadmap adds **syntax in the CLI**, **TADMINI** and **TAQYIDI** linkers, a **SyntacticParser**, **5–6 constraint modules**, **corpus evaluation**, and **polish** (300 tests, C2c design) over **6 sprints** without breaking existing behaviour.

**Outcomes by end of 6 months:**

- CLI returns `result["syntax"]` with ISNADI, TADMINI, and TAQYIDI links when morphology is requested.
- A single parser runs all three linkers; an optional validator reports constraint violations.
- Trial corpus with reported F1 (morphology) and UAS/LAS (syntax).
- Test suite ≥300; property-based tests; C2c semantic-gate design doc.

**Critical path:** Sprint 1 (syntax in CLI) → Sprint 2 (TADMINI) → Sprint 3 (TAQYIDI + parser) → Sprint 4 (constraints) → Sprint 5 (corpus) → Sprint 6 (polish).

**References:**  
- **`docs/MASTER_PLAN_CHECKLIST.md`** – Full 6-part task list (foundation, phonology, semantics, morphology, syntax, constraints, integration) and sprint mapping.  
- `WHERE_WE_ARE_VS_PLAN.md`, `project_deleverables.md`, `docs/PLAN_MERGE_ANALYSIS.md`, `src/fvafk/phonology/INTEGRATION_PLAN.md`.

---

## 0. Master plan alignment (Parts 1–6)

The detailed task checklist is in **`docs/MASTER_PLAN_CHECKLIST.md`**. Summary:

| Part | Focus | Sprints |
|------|--------|--------|
| **Part 1** | Foundation and packaging: pyproject.toml, bayan-fvafk library, Pydantic models, OrthographyAdapter/FormCodecV2, CLI JSON (tokens, WordForm, ISNADI), 10+ CLI tests, docs | 1 |
| **Part 2** | Phonology gates (10+ incl. GateWasl), OrthographyAdapter rules, syllabifier CV/CVV/CVC, Coq skeletons (Sukun, Shadda, Tanwin), CI Coq + property tests | 2 |
| **Part 2.5** | Semantic gates and evidence: Bayan semantic_gates_wrapper, EvidenceWeight, RealityLink, accept criteria, falsifiability, assurance_mode | 2–3 |
| **Part 3** | Morphology: WordBoundaryDetector Plan B, PatternCatalog/PatternUniverse, morph_flags, gold corpus, F1 ≥ 0.85 | 3 |
| **Part 4** | Syntax: ISNADI/TADMINI/TAQYIDI, SyntacticParser, EventExtractor, link visualization, UAS/LAS | 4 |
| **Part 5** | Constraints (5 + Amil-Sign), ConstraintValidator, Coq predicates, property tests | 5 |
| **Part 6** | Integration: full pipeline, batch/cache, corpus eval, proof mode, neo4j, FastAPI, CI/CD, full docs | 6 |

**Sprint timeline:** Sprint 1 = Weeks 1–2, Sprint 2 = Weeks 3–4, Sprint 3 = Weeks 5–6, Sprint 4 = Weeks 7–8, Sprint 5 = Weeks 9–10, Sprint 6 = Weeks 11–14.

---

## 1. Principles

- **Preserve:** No breaking changes to existing CLI, tests, or APIs.
- **Incremental:** One feature focus per sprint; small PRs.
- **CI:** Keep 269+ tests passing; add tests for each new feature.
- **Document:** Update PROJECT_STATUS, deliverables, and this roadmap at each milestone.

---

## 2. Six-sprint overview

| Sprint | Weeks | Focus | Key deliverable | Depends on |
|--------|--------|--------|-----------------|------------|
| **Sprint 1** | 1–2 | Part 1: packaging + ISNADI in CLI + docs | pyproject.toml, bayan-fvafk scaffold, Pydantic models, CLI JSON (tokens, WordForm, ISNADI), 10+ CLI tests | — |
| **Sprint 2** | 3–4 | Part 2 (+ 2.5 start): phonology + Coq skeletons | 10+ gates, OrthographyAdapter rules, syllabifier, Coq skeletons; semantic gates base | Sprint 1 |
| **Sprint 3** | 5–6 | Part 3: morphology + corpus F1 | WordBoundaryDetector Plan B, PatternCatalog bridge, morph_flags, gold corpus, F1 ≥ 0.85 | Sprint 2 |
| **Sprint 4** | 7–8 | Part 4: syntax linkers + events | ISNADI/TADMINI/TAQYIDI, SyntacticParser, EventExtractor, visualization, UAS/LAS | Sprints 1, 3 |
| **Sprint 5** | 9–10 | Part 5: constraints + validator | 5 constraints + Amil-Sign, ConstraintValidator, Coq predicates | Sprint 4 |
| **Sprint 6** | 11–14 | Part 6: integration + eval + ops | Full pipeline, batch/cache, corpus reports, proof mode, neo4j, FastAPI, CI/CD, full docs | Sprints 1–5 |

---

## 3. Sprint 1 – Syntax in CLI and documentation

**Goal:** Expose ISNADI in the pipeline and establish project status and roadmap docs.

### 3.1 Deliverables

| ID | Deliverable | Owner |
|----|-------------|--------|
| D1.1 | CLI builds WordForms from C2b when `--morphology` (or `--syntax`) is set | Dev |
| D1.2 | CLI runs IsnadiLinker on WordForms and sets `result["syntax"] = { "isnadi_links": [...] }` | Dev |
| D1.3 | PROJECT_STATUS.md created (current progress + roadmap pointer) | Dev |
| D1.4 | ENHANCED_ROADMAP.md created/updated (this file) | Dev |
| D1.5 | INTEGRATION_PLAN.md updated with “Post-integration milestones” section | Dev |
| D1.6 | project_deleverables.md updated (269 tests, syntax in pipeline as next) | Dev |
| D1.7 | 1–2 integration tests that assert presence of `result["syntax"]` (and optionally isnadi_links) | Dev |

### 3.2 Dependencies

- **Blocked by:** None (uses existing WordFormBuilder, IsnadiLinker).
- **Blocks:** Sprint 2 (TADMINI needs syntax block in CLI).

### 3.3 Success metrics

| Metric | Target |
|--------|--------|
| CLI with `--morphology --json` returns `result["syntax"]["isnadi_links"]` for multi-word nominal sentences | 100% |
| All existing tests pass | 269/269 |
| CI | Green |
| PROJECT_STATUS.md and ENHANCED_ROADMAP.md exist; INTEGRATION_PLAN has post-integration section | Done |

---

## 4. Sprint 2 – TADMINI linker

**Goal:** Implement TADMINI (transitive verb → object) and add it to the CLI syntax output.

### 4.1 Deliverables

| ID | Deliverable | Owner |
|----|-------------|--------|
| D2.1 | TadminiLinker class: `build_links(wordforms, isnadi_links) -> List[Link]` with LinkType.TADMINI | Dev |
| D2.2 | CLI runs TADMINI after ISNADI and adds `result["syntax"]["tadmini_links"]` | Dev |
| D2.3 | ≥10 unit/integration tests for TADMINI | Dev |
| D2.4 | Docs: TADMINI rules and usage in README or docs/ | Dev |

### 4.2 Dependencies

- **Blocked by:** Sprint 1 (syntax in CLI; WordForms and isnadi_links available).
- **Blocks:** Sprint 3 (parser consumes TADMINI).

### 4.3 Success metrics

| Metric | Target |
|--------|--------|
| TadminiLinker returns correct TADMINI links for transitive V + object examples | Pass in tests |
| JSON contains `result["syntax"]["tadmini_links"]` when applicable | 100% |
| New tests in tests/syntax/; total tests ≥279 | Yes |
| CI | Green |

---

## 5. Sprint 3 – TAQYIDI linker and SyntacticParser

**Goal:** Implement TAQYIDI (noun→adjective, noun→mudhaf ilayh) and a single parser that runs ISNADI → TADMINI → TAQYIDI.

### 5.1 Deliverables

| ID | Deliverable | Owner |
|----|-------------|--------|
| D3.1 | TaqyidiLinker: `build_links(wordforms) -> List[Link]` (LinkType.TAQYIDI) | Dev |
| D3.2 | SyntacticParser: runs ISNADI → TADMINI → TAQYIDI; returns (links, errors) | Dev |
| D3.3 | CLI uses SyntacticParser; exposes all links under `result["syntax"]` | Dev |
| D3.4 | Tests for TaqyidiLinker and SyntacticParser | Dev |

### 5.2 Dependencies

- **Blocked by:** Sprints 1 and 2 (syntax in CLI, TADMINI in place).
- **Blocks:** Sprint 4 (constraints need parser output); Sprint 5 (corpus eval needs full links).

### 5.3 Success metrics

| Metric | Target |
|--------|--------|
| TaqyidiLinker returns TAQYIDI links for noun–adjective / idafa examples | Pass in tests |
| Parser returns combined isnadi_links, tadmini_links, taqyidi_links | Yes |
| CLI shows all three link types in result["syntax"] | 100% |
| No regression; CI green | Yes |

---

## 6. Sprint 4 – Constraints

**Goal:** Implement 5 (or 6) constraint modules and a validator that returns violations from wordforms + links.

### 6.1 Deliverables

| ID | Deliverable | Owner |
|----|-------------|--------|
| D4.1 | VerbSubjectConstraint (no verb without subject except passive) | Dev |
| D4.2 | TransitiveObjectConstraint (no transitive without object) | Dev |
| D4.3 | AdjectiveAgreementConstraint (naat–manout agreement) | Dev |
| D4.4 | CausalityEventsConstraint (optional) | Dev |
| D4.5 | PassiveVoiceConstraint (optional) | Dev |
| D4.6 | ConstraintValidator(wordforms, links) → List[ConstraintViolation] | Dev |
| D4.7 | Optional CLI flag `--validate-constraints` → `result["syntax"]["violations"]` | Dev |
| D4.8 | Tests per constraint and for validator | Dev |

### 6.2 Dependencies

- **Blocked by:** Sprint 3 (parser and full links in CLI).
- **Blocks:** Sprint 5 (corpus can include violation counts).

### 6.3 Success metrics

| Metric | Target |
|--------|--------|
| Each constraint has validate(wordforms, links) → List[ConstraintViolation] | Yes |
| Violations include constraint_id, word_idx, message, severity | Yes |
| At least one positive/negative test per constraint | Yes |
| CI green | Yes |

---

## 7. Sprint 5 – Corpus and metrics

**Goal:** Define a trial corpus and report F1 (morphology) and UAS/LAS (syntax).

### 7.1 Deliverables

| ID | Deliverable | Owner |
|----|-------------|--------|
| D5.1 | Trial corpus (e.g. 100 verses or 50 MSA sentences); path or format documented | Dev |
| D5.2 | Script: run pipeline on corpus, compute F1 (morphology), UAS/LAS (syntax), link-type accuracy | Dev |
| D5.3 | docs/ACCURACY_REPORT.md or EVALUATION.md with baseline results | Dev |

### 7.2 Dependencies

- **Blocked by:** Sprints 1–4 (syntax and constraints in place).
- **Blocks:** None (Sprint 6 is independent for test count).

### 7.3 Success metrics

| Metric | Target |
|--------|--------|
| Corpus and script in repo or documented | Yes |
| At least one full run with reported F1, UAS, LAS | Yes |
| Baseline documented for future comparison | Yes |

---

## 8. Sprint 6 – Polish and C2c prep

**Goal:** Reach 300 tests, add property-based tests, and document C2c design.

### 8.1 Deliverables

| ID | Deliverable | Owner |
|----|-------------|--------|
| D6.1 | Test count ≥300 (edge cases, integration, constraints) | Dev |
| D6.2 | Property-based tests (e.g. Hypothesis): idempotence/preservation/reversibility where applicable | Dev |
| D6.3 | docs/C2C_DESIGN.md: evidence model, falsifiability, accept/reject (no implementation) | Dev |
| D6.4 | Release notes and roadmap update for post–Sprint 6 | Dev |

### 8.2 Dependencies

- **Blocked by:** Sprints 1–5 (all features available to test).
- **Blocks:** Nothing (roadmap complete for this cycle).

### 8.3 Success metrics

| Metric | Target |
|--------|--------|
| pytest -q | ≥300 passed |
| At least one property-based test file | Yes |
| C2c design doc in docs/ | Yes |
| Roadmap updated | Yes |

---

## 9. Dependency graph (critical path)

```
Sprint 1 (Syntax in CLI + docs)
    │
    └──► Sprint 2 (TADMINI)
              │
              └──► Sprint 3 (TAQYIDI + Parser)
                        │
                        ├──► Sprint 4 (Constraints)
                        │
                        └──► Sprint 5 (Corpus + metrics)

Sprint 4 ──► Sprint 5 (optional: violations in corpus)
Sprint 1–5 ──► Sprint 6 (Polish + 300 tests + C2c design)
```

---

## 10. What can be deferred

- Coq / formal proofs
- Plan B word boundaries (from syllable stream)
- C2c implementation (design only in Sprint 6)
- Event extraction
- --coq-verify in CLI
- Large corpus (100+ verses + hadith + MSA); Sprint 5 uses a trial corpus

---

*Document version: 1.1. Last updated: 2026-02-01.*
