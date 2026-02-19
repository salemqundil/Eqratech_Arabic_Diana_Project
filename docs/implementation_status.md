# Implementation Status & Plan (Living Document)

Last updated: 2026-02-03

## Purpose
This document tracks what is implemented, what is missing, and the next steps. It should be updated after each change set that affects the roadmap.

## Summary (as of 2026-02-03)
- **Phase 1 (C1 Infrastructure):** Mostly complete.
- **Phase 2 (C2a Phonological Gates):** Complete (10/10 gates implemented).
- **Phase 3 (C2b Morphology):** Partial (root extraction, pattern matching, syllabification exist; missing word boundary detection, POS, i3rab, affix/feature systems).
- **Syntax / Constraints / Semantics:** Not implemented in `src/fvafk`.
- **Tests:** Present for C1/C2a/C2b and CLI.

---

## Detailed Status

### Phase 1 — Infrastructure (C1)
**Implemented**
- Consonant inventory: `src/fvafk/c1/segment_inventory.py`
- Orthography adapter (simplified): `src/fvafk/orthography_adapter.py`
- Encoder and unit structures: `src/fvafk/c1/encoder.py`, `src/fvafk/c1/unit.py`

**Missing / To Improve**
- Expanded orthography framework per full plan (carrier/hamza rules, advanced normalization)
- Documentation mapping to plan milestones

### Phase 2 — Phonological Gates (C2a)
**Implemented (10/10)**
- `GateSukun`, `GateIdgham`, `GateDeletion`, `GateEpenthesis`, `GateHamza`, `GateMadd`, `GateWaqf`, `GateShadda`
  - `GateAssimilation`, `GateTanwin`
  - Location: `src/fvafk/c2a/gates/`

**Missing (0/10)**

**Notes**
- Gate orchestration exists: `src/fvafk/c2a/gate_framework.py`
- Tests exist for the above gates under `tests/`

### Phase 3 — Morphology (C2b)
**Implemented**
- Root extraction: `src/fvafk/c2b/root_extractor.py`
- Pattern matching and templates: `src/fvafk/c2b/pattern_matcher.py`
- Syllabification: `src/fvafk/c2b/syllabifier.py`
- Morpheme structures: `src/fvafk/c2b/morpheme.py`

**Missing / Partial**
- Word boundary detection (tokenization)
- Word kind classification (noun/verb/particle)
- I3rab analysis (mabni/mu'rab)
- Affix identification and morphological feature extraction
- Evaluation metrics and corpus testing pipeline

### Phase 4 — Syntax + Constraints
**Missing**
- Syntactic parser (VSO, ISNADI, TADMINI, TAQYIDI relations)
- 5 grammar constraints (no verb without subject, etc.)

### Phase 5 — Semantics / Events
**Missing**
- Event extraction
- C2c semantic gate logic

### Phase 6 — Coq Proofs / Formalization
**Status**
- Not validated in this workspace. No Coq proofs linked under `src/fvafk/`.

---

## What We Did So Far (Recorded)
- Implemented C1 segment inventory and orthography adapter.
- Implemented 10 phonological gates and the gate orchestration.
- Added `GateAssimilation` and `GateTanwin`.
- Implemented C2b root extraction, pattern matcher, syllabifier, and morpheme structures.
- Added CLI integration for C1→C2a→C2b (see `src/fvafk/cli/main.py`).
- Added tests for C1/C2a/C2b and CLI under `tests/`.

---

## Immediate Next Steps (Ordered)
1. Add word boundary detection (tokenization) for multi-word morphology.
2. Add word kind classification (noun/verb/particle).
3. Add affix identification and morphological feature extraction.
4. Add I3rab analysis.
5. Add syntax parser + grammar constraints.
6. Add event extraction + semantic gating.
7. Connect Coq proofs to code artifacts (if required in this repo).

---

## Update Procedure (Keep This Document Fresh)
When you merge or push changes:
- Update the **Last updated** date.
- Move completed items from “Missing” to “Implemented”.
- Add new tasks discovered during development.
- Link new files or tests that were added.
