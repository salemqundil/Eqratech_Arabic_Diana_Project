# GitHub issues structure

Use this to create **milestones** and **issues** in GitHub. Labels and dependencies are below.

---

## Labels to create

| Label | Color | Description |
|-------|--------|-------------|
| `priority:P0` | red | Critical path; do first |
| `priority:P1` | orange | High priority; required for roadmap |
| `priority:P2` | gray | Nice to have; can defer |
| `type:feature` | blue | New feature |
| `type:enhancement` | green | Improvement to existing |
| `type:docs` | purple | Documentation only |

---

## Milestones (create 6)

| Milestone | Description | Due (example) |
|-----------|-------------|----------------|
| **Sprint 1** | Syntax in CLI + docs | 1 month from now |
| **Sprint 2** | TADMINI linker | 2 months from now |
| **Sprint 3** | TAQYIDI + Parser | 3 months from now |
| **Sprint 4** | Constraints | 4 months from now |
| **Sprint 5** | Corpus + metrics | 5 months from now |
| **Sprint 6** | Polish + 300 tests | 6 months from now |

---

## Top 20 issues

**Acceptance criteria:** Each issue should have “Acceptance criteria” in the body (checklist). Example for #1: “CLI with --morphology returns result['syntax']['isnadi_links']; 269 tests pass.”

| # | Title | Labels | Milestone | Depends on |
|---|--------|--------|-----------|------------|
| 1 | Wire syntax into CLI: WordForm + ISNADI in result | P0, feature | Sprint 1 | — |
| 2 | Add PROJECT_STATUS.md with current progress + roadmap | P0, docs | Sprint 1 | — |
| 3 | Create ENHANCED_ROADMAP.md (6-month plan) | P0, docs | Sprint 1 | — |
| 4 | Update INTEGRATION_PLAN.md with post-integration milestones | P1, docs | Sprint 1 | — |
| 5 | Update project_deleverables.md (269 tests, syntax next) | P1, docs | Sprint 1 | — |
| 6 | Implement TadminiLinker (transitive → object) | P1, feature | Sprint 2 | #1 |
| 7 | Add TADMINI to CLI syntax output | P1, feature | Sprint 2 | #6 |
| 8 | Tests for TADMINI linker | P1, feature | Sprint 2 | #6 |
| 9 | Implement TaqyidiLinker (noun→adjective, mudhaf ilayh) | P1, feature | Sprint 3 | #7 |
| 10 | Add SyntacticParser (ISNADI→TADMINI→TAQYIDI) | P1, feature | Sprint 3 | #6, #9 |
| 11 | Wire parser into CLI; expose all links | P1, feature | Sprint 3 | #10 |
| 12 | Tests for TAQYIDI and parser | P1, feature | Sprint 3 | #9, #10 |
| 13 | Implement VerbSubjectConstraint (no verb without subject) | P1, feature | Sprint 4 | #11 |
| 14 | Implement TransitiveObjectConstraint | P1, feature | Sprint 4 | #11 |
| 15 | Implement AdjectiveAgreementConstraint | P1, feature | Sprint 4 | #11 |
| 16 | Implement ConstraintValidator (aggregate violations) | P1, feature | Sprint 4 | #13, #14, #15 |
| 17 | Add --validate-constraints to CLI (optional) | P2, enhancement | Sprint 4 | #16 |
| 18 | Trial corpus + F1/UAS/LAS evaluation script | P1, feature | Sprint 5 | #11 |
| 19 | Add tests to reach 300 total | P2, feature | Sprint 6 | — |
| 20 | C2c semantic gate design doc | P2, docs | Sprint 6 | — |

---

## Dependencies (for GitHub “blocked by” or description)

- #6, #7, #8 depend on #1 (syntax in CLI).
- #9, #10, #11, #12 depend on #7 (TADMINI in CLI).
- #13, #14, #15, #16 depend on #11 (parser in CLI).
- #17 depends on #16.
- #18 depends on #11.

---

## THIS WEEK (copy to project board or sprint)

1. **Implement** CLI: when `--morphology`, build WordForms from C2b, run IsnadiLinker, set `result["syntax"] = {"isnadi_links": [...]}`.
2. **Add** 1–2 integration tests for `result["syntax"]`.
3. **Create** PROJECT_STATUS.md and ENHANCED_ROADMAP.md (done).
4. **Update** INTEGRATION_PLAN.md with post-integration milestones (done).
5. **Update** project_deleverables.md: 269 tests; “Syntax in CLI” in next priorities.
6. **Create** GitHub milestones (Sprint 1–6) and top 20 issues with labels above.
