# Where We Are With Respect to the Plan

This report maps the **current project state** to the master plan in **🎯 خطة شاملة لبناء المحركات اللغوية الحقيقية.md**. It is a snapshot for steering and prioritisation.

**Reference:** Plan = 6 phases (Infrastructure → Gates → Morphology → Syntax → Constraints → Integration), 16–17 weeks, SMART goals (tests, F1, UAS, Coq, performance, docs).

**Current baseline:** 269 tests passing; CLI C1→C2a→C2b (+ Phonology V2, morphology); WordForm + ISNADI in code but syntax not in CLI; CVC theory fixed (β=12.0); no Coq in this repo; no C2c/Meaning/Corpus.

---

## 1. Executive summary

| Area | Plan target | Current state | Status |
|------|-------------|---------------|--------|
| **Tests** | 300+ tests, 95%+ pass | 269 pass | 🟡 Close (≈90%) |
| **C1 (Infrastructure)** | Segment inventory, syllable system, gate framework, OrthographyAdapter | All present; no Coq | 🟢 Done (no formal proofs) |
| **C2a (10 gates)** | 10 gates, 100+ tests, Coq | 11 gates implemented, many tests; no Coq in repo | 🟢 Done (lighter framework) |
| **C2b (Morphology)** | Word boundary, pattern, classifier, root, features, F1≥0.85 | Plan A boundaries, pattern/classifier/root/features; no corpus F1 | 🟢 Core done; 🟡 no corpus metric |
| **Phonology V2** | (Not in original plan; added) | Lattice + witnesses + CLI | 🟢 Done |
| **Syntax (Phase 4)** | ISNADI + TADMINI + TAQYIDI, parser, UAS≥0.80 | ISNADI only; not in CLI; no TADMINI/TAQYIDI | 🟡 Partial |
| **Constraints (Phase 5)** | 5 (or 6) constraints, 0 violations on correct text | Not implemented | 🔴 Not started |
| **C2c / Meaning / Corpus** | Semantic gate, meaning, corpus evaluation | Not implemented | 🔴 Not started |
| **Coq** | 50+ theorems, 100% Qed | No Coq in this repo | 🔴 Not in repo |
| **CLI** | `python -m fvafk.cli`, --verbose, --json | Full CLI with --morphology, --phonology-v2, etc. | 🟢 Done |
| **Documentation** | 50,000+ words, 100% coverage | README, deliverables, plan; not measured | 🟡 Partial |

**Overall:** Phases 1–3 and CLI/Phonology V2 are **largely done** relative to the plan (with the noted gaps: no Coq, no corpus F1, Plan B word boundaries not done). Phase 4 (syntax) is **partially done** (ISNADI in package only). Phases 5 and 6 (constraints, C2c, full integration, corpus, formal proofs) are **not done**.

---

## 2. Plan goals (quick reference)

From the plan:

- **Architecture:** Strict separation C1 (signifier) → C2a (phonology) → C2b (morphology/syntax) → C2c (semantics) → C3 (meaning). No C3 without C2; no C2 without C1 preserved.
- **Measurable targets:**
  - Phonological gates: 10 gates, 100+ tests, 90%+ coverage.
  - Morphology: F1 ≥ 0.85 on a trial corpus.
  - Syntax: UAS ≥ 0.80, LAS ≥ 0.75, link-type accuracy ≥ 85%.
  - Constraints: 5 (or 6) constraints applied; 0 violations on correct text.
  - Coq: 50+ new theorems, 100% proved (Qed).
  - Tests: 300+ tests, 95%+ pass.
  - Performance: 1000 words/second, <1 ms per word.
  - Documentation: 50,000+ words, 100% coverage.

---

## 3. Phase-by-phase status

### 3.1 Phase 1: البنية التحتية (Infrastructure) — Week 1–2

| Plan item | Plan detail | Current state | Status |
|-----------|-------------|---------------|--------|
| **1.1 Segment inventory** | 30 consonants + phonetic features (`segment_inventory.py`) | `src/fvafk/c1/segment_inventory.py` exists; consonant inventory and features | ✅ Done |
| **1.2 Syllable system** | 6 syllable types, `Syllable` with onset/nucleus/coda, constraints | `src/fvafk/c2a/syllable.py`: Segment, SegmentKind, VowelKind; syllable types used in Phonology V2 | ✅ Done (structure present; plan’s strict `Syllable` dataclass with validators not identical) |
| **1.3 Gate framework** | `GateResult`, `PhonologicalGate` with precondition/apply/postcondition, `EpistemicState`, `run()` | `gate_framework.py`: GateResult (status, output, reason, deltas, latency_ms); gates have `apply(segments)`; no epistemic state / pre/post in API | 🟢 Done (simplified: no epistemic state, no Coq) |
| **OrthographyAdapter** | (Added later) Normalisation: hamza, wasl, tanwin, etc. | `orthography_adapter.py` in use by C1 encoder | ✅ Done |
| **FormCodecV2** | Reversible encode/decode, checksum | `form_codec_v2.py`: reversible, tokens+spans, checksum | ✅ Done |
| **Trace V1** | Trace steps, replay | `trace_v1.py`: TraceStep, replay | ✅ Done |
| **C1 encoder** | Text → segments | `C1Encoder.encode(text)` → list of Segment | ✅ Done |
| **Outputs (plan)** | 45+ tests, 90%+ coverage, Coq theories | 269 total tests; no Coq in repo | 🟡 Tests ok; 🔴 Coq absent |

**Verdict:** Phase 1 is **done** in code. Gaps: no Coq proofs, no formal reversibility proofs in this repo.

---

### 3.2 Phase 2: البوابات الصوتية (Phonological gates) — Week 3–5

| Plan item | Plan detail | Current state | Status |
|-----------|-------------|---------------|--------|
| **10 gates** | Sukun, Shadda, Tanwin, Assimilation, Idgham, Hamza, Madd, Waqf, Deletion, Epenthesis | All 10 + GateWasl implemented in `c2a/gates/` | ✅ Done |
| **Gate logic** | Precondition, apply, postcondition, epistemic level | Each gate implements `apply(segments) -> GateResult`; no pre/post/epistemic in interface | 🟢 Done (simplified) |
| **Orchestrator** | Sequential run, stop on REJECT | `GateOrchestrator.run(segments)` | ✅ Done |
| **Tests** | 100+ tests (10×10), 85%+ coverage | Many gate tests (sukun, shadda, wasl, hamza, waqf, idgham, madd, assimilation, tanwin, deletion, epenthesis) + framework | 🟢 Done |
| **Coq** | One theorem per gate (e.g. GateSukun eliminates double-sukun) | No Coq in repo | 🔴 Not in repo |
| **Performance** | <500 µs per gate | Not measured in report | 🟡 Unknown |

**Verdict:** Phase 2 is **done** in Python. Coq and formal gate contracts are **not** in this repo.

---

### 3.3 Phase 3: المحلل الصرفي (Morphology) — Week 6–8

| Plan item | Plan detail | Current state | Status |
|-----------|-------------|---------------|--------|
| **3.1 Word boundary** | From syllables (Plan B): `detect_boundaries(syllables)` with BoundaryKind, tanwin | Plan A: `WordBoundaryDetector.detect(text)` → tokens with spans (no syllable stream) | 🟢 Plan A done; 🔴 Plan B (from syllables) not done |
| **3.2 Pattern analysis** | PatternAnalyzer from syllables, pattern kinds (e.g. VERB_MUJARRAD), weight matching | `pattern_analyzer.py` + `pattern_matcher.py` + `awzan_loader.py`; CV-based matching; templates from CSV | ✅ Done (different design: text/CV-based, not syllable-based) |
| **3.3 Word classification** | WordKind (noun/verb/particle), closed list + pattern | `word_classifier.py`: operator, pronoun, verb, noun, demonstrative, name, particle; operators_catalog | ✅ Done |
| **Root extraction** | Root + affixes | `root_extractor.py`: RootExtractionResult (root, normalized, stripped, prefix, suffix); hamza normalisation | ✅ Done |
| **Affix identification** | Prefix/suffix in result | Explicit in RootExtractionResult | ✅ Done |
| **Morphological features** | Definiteness, number, gender, case | `features.py`: extract_features (V1 heuristics) | 🟢 Done (V1; not full Iʿrāb) |
| **Success criteria (plan)** | 90+ tests, F1≥0.85, word-kind accuracy ≥90%, root accuracy ≥80% | Many C2b tests; no corpus F1/accuracy reported | 🟡 Tests ok; 🔴 No corpus metrics yet |

**Verdict:** Phase 3 **core is done** (boundaries Plan A, pattern, classifier, root, features). Gaps: Plan B boundaries, no corpus F1/accuracy, deep Iʿrāb not done.

---

### 3.4 Phase 4: المحلل النحوي (Syntax) — Week 9–11

| Plan item | Plan detail | Current state | Status |
|-----------|-------------|---------------|--------|
| **4.1 ISNADI** | IsnadiLinker: verb→subject, mubtada→khabar, VSO | `syntax/linkers/isnadi_linker.py`: find_links(WordForm list) → Link list; mubtada/khabar rules | ✅ Implemented |
| **4.2 TADMINI** | TadminiLinker: transitive verb → object | Not implemented | 🔴 Not done |
| **4.3 TAQYIDI** | TaqyidiLinker: noun→adjective, noun→mudhaf ilayh | Not implemented | 🔴 Not done |
| **4.4 Parser** | SyntacticParser: run ISNADI → TADMINI → TAQYIDI, validate constraints | No single parser; ISNADI only; no orchestration | 🔴 Not done |
| **WordForm** | Bridge from C2b to syntax | `word_form.py`, `word_form_builder.py`, `word_form_validator.py` | ✅ Done |
| **CLI integration** | Build WordForms from C2b, run linkers, add result["syntax"] | CLI does not build WordForms or call ISNADI; no result["syntax"] | 🔴 Not done |
| **Link types** | Link(rel, head, dep, confidence) | `syntax/linkers/link.py`: Link, LinkType (e.g. ISNADI) | ✅ Done |
| **Success criteria (plan)** | 80+ tests, UAS≥0.80, LAS≥0.75, link-type ≥85% | test_isnadi_linker present; no UAS/LAS | 🟡 ISNADI tests only; 🔴 No metrics |

**Verdict:** Phase 4 is **partial**: ISNADI and WordForm exist in code, but **syntax is not in the CLI**, and TADMINI/TAQYIDI/parser are **not implemented**.

---

### 3.5 Phase 5: القيود النحوية (Constraints) — Week 12–13

| Plan item | Plan detail | Current state | Status |
|-----------|-------------|---------------|--------|
| **Constraint 1** | No verb without subject (except passive) | Not implemented | 🔴 Not done |
| **Constraint 2** | No transitive without object | Not implemented | 🔴 Not done |
| **Constraint 3** | Adjective–noun agreement (case, definiteness, number, gender) | Not implemented | 🔴 Not done |
| **Constraint 4** | Causality requires events | Not implemented | 🔴 Not done |
| **Constraint 5** | Passive requires form change | Not implemented | 🔴 Not done |
| **Constraint 6 (added)** | Amil-Sign (no i3rab without operator, no operator without link) | Not implemented | 🔴 Not done |
| **Validator** | Validate wordforms + links → list of violations | Not implemented | 🔴 Not done |

**Verdict:** Phase 5 is **not started** in this repo.

---

### 3.6 Phase 6: التكامل والتحسين (Integration) — Week 14–17

| Plan item | Plan detail | Current state | Status |
|-----------|-------------|---------------|--------|
| **Full pipeline** | C1→C2a→C2b→(syntax)→(C2c) | C1→C2a→C2b in CLI; syntax not in pipeline | 🟡 C2b integrated; syntax not |
| **CLI** | `python -m fvafk.cli`, --verbose, --json, --coq-verify | CLI with --json, --morphology, --phonology-v2, --phonology-v2-details, --phonology-v2-witnesses, --multi-word | ✅ Done (no --coq-verify) |
| **Corpus testing** | 100 verses + 50 hadith + 50 MSA; F1/UAS | No corpus evaluation in repo | 🔴 Not done |
| **Performance** | 1000 words/s, <1 ms/word, <500 MB for 1000 sentences | Not measured in report | 🟡 Unknown |
| **C2c (Semantic gate)** | Evidence model, falsifiability, reality link, accept threshold | Not implemented | 🔴 Not done |
| **Event extraction** | Event type, participants, time/place, certainty | Not implemented | 🔴 Not done |
| **Property-based tests** | Idempotence, preservation, reversibility (e.g. Hypothesis) | Not in repo | 🔴 Not done |
| **Documentation** | 50,000+ words, SPEC, ARCHITECTURE, GATES, etc. | README, project_deleverables, plan, INTEGRATION_PLAN; not to plan scale | 🟡 Partial |

**Verdict:** Phase 6 is **partial**: CLI and pipeline up to C2b are in place; corpus, C2c, event extraction, property tests, and full docs are **not done**.

---

## 4. Measurable targets vs current state

| Target | Plan | Current | Gap |
|--------|------|---------|-----|
| **Tests** | 300+, 95%+ pass | 269 pass | ~30 tests to 300; rate already high |
| **Gate tests** | 100+ | Many (all gates + framework covered) | Likely close or above 100 in total |
| **Morphology F1** | ≥ 0.85 | Not measured | Need corpus + evaluation script |
| **Word-kind accuracy** | ≥ 90% | Not measured | Same |
| **Root extraction accuracy** | ≥ 80% | Not measured | Same |
| **UAS (syntax)** | ≥ 0.80 | N/A (syntax not in pipeline) | Need syntax in CLI + annotated corpus |
| **LAS** | ≥ 0.75 | N/A | Same |
| **Link-type accuracy** | ≥ 85% | N/A | Same |
| **Constraint violations** | 0 on correct text | N/A (no constraints) | Need Phase 5 |
| **Coq** | 50+ theorems, 100% Qed | 0 in repo | Full formalisation out of scope for this snapshot |
| **Performance** | 1000 words/s, <1 ms/word | Not measured | Add benchmarks |
| **Documentation** | 50,000+ words | Not measured | Add/expand docs to meet target |

---

## 5. What is in the plan but not in this repo

- **Coq:** No Coq theories or proofs (plan assumes 50+ theorems, gate postconditions, reversibility).
- **Word boundary Plan B:** Boundaries from syllable stream (BoundaryKind, tanwin in nucleus); only Plan A (text + spans) is implemented.
- **TADMINI and TAQYIDI linkers:** Only ISNADI is implemented.
- **SyntacticParser:** No single parser that runs ISNADI → TADMINI → TAQYIDI and returns links + errors.
- **Syntax in CLI:** No building of WordForms from C2b and no `result["syntax"]` (e.g. isnadi_links).
- **All 5 (or 6) constraints:** None implemented.
- **C2c (semantic gate):** Evidence model, falsifiability, reality link, accept/reject.
- **C3 / Meaning:** Not in repo.
- **Event extraction:** Not implemented.
- **Corpus evaluation:** No F1/UAS/LAS or violation counts on a designated corpus.
- **Property-based tests:** No Hypothesis (or similar) tests for idempotence/preservation/reversibility.
- **Formal epistemic state in gates:** Plan’s EpistemicState and pre/post conditions are not in the current gate API.

---

## 6. Risks and inconsistencies

- **Docs vs code:** README/project_deleverables may still say 229 tests or omit WordForm/ISNADI; plan’s “ما ينقصنا” section lists gates/morphology/syntax as ❌ while they are partly or fully implemented.
- **Duplicate files:** `syntax/linkers/link (1).py`, `syntax/link.py` duplicate linkers’ link; should be removed or consolidated.
- **ISNADI v1.1:** Phrase-skipping logic in `tools/`; tests may depend on `tools/` path; should live under `fvafk.syntax` with stable imports.
- **Theory (CVC):** In main repo, not in zhe worktree; ensure both stay in sync after changes (e.g. β=12.0).

---

## 7. Recommended next steps (priority)

1. **Syntax in CLI (high):** In `main.py`, when `--morphology` is set: build WordForms from `result["c2b"]["words"]` (or equivalent), call `IsnadiLinker().find_links(word_forms)`, set `result["syntax"] = {"isnadi_links": [link.to_dict() for link in links]}` (or equivalent). Unblocks use of ISNADI in the pipeline.
2. **Update docs (high):** Set test count to 269 in README and project_deleverables; add WordForm and ISNADI to “completed”; align plan’s “ما لدينا / ما ينقصنا” with this report.
3. **TADMINI / TAQYIDI (medium):** Implement linkers and optionally a small SyntacticParser that runs ISNADI → TADMINI → TAQYIDI and returns links (and later, errors).
4. **Constraint stubs (medium):** Add the 5 (or 6) constraint modules and a validator that takes wordforms + links and returns violations; integrate after syntax is in CLI.
5. **Corpus and metrics (medium):** Define a small trial corpus (e.g. 100 verses or MSA sentences), run morphology and (when ready) syntax, and report F1 for morphology and UAS/LAS for syntax.
6. **Repo hygiene (low):** Remove duplicate link files; move ISNADI v1.1 into package; fix test imports.

---

## 8. Summary table (plan vs current)

| Phase | Plan | Current | Status |
|-------|------|---------|--------|
| **1. Infrastructure** | C1, inventory, syllable, gate framework, orthography, codec, trace | Implemented; no Coq | ✅ Done |
| **2. Gates** | 10 gates, 100+ tests, Coq | 11 gates, tests; no Coq | ✅ Done |
| **3. Morphology** | Boundaries, pattern, classifier, root, features, F1≥0.85 | Plan A + pattern/classifier/root/features; no F1 | ✅ Core done |
| **4. Syntax** | ISNADI, TADMINI, TAQYIDI, parser, UAS≥0.80 | ISNADI only; not in CLI | 🟡 Partial |
| **5. Constraints** | 5–6 constraints, validator | None | 🔴 Not started |
| **6. Integration** | Pipeline, CLI, corpus, C2c, docs | CLI + C2b; no corpus/C2c/full docs | 🟡 Partial |

This document should be updated whenever a major phase is completed or success criteria are redefined.
