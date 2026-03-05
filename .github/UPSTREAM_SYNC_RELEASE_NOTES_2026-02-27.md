# Upstream Sync Release Notes

Date: 2026-02-27
Source repo: sonaiso/Eqratech_Hussein_Hiyassat_Project
Target upstream: salemqundil/Eqratech_Arabic_Diana_Project
Branch: main

## Commits for Sync (ordered)

1) c800dd2 — fix(core): recover C2a/C2b integrity and restore test-stable morphology pipeline
- Restores stable C2a/C2b internals after merge corruption.
- Recovers morphology pipeline behavior and API consistency.
- Includes dependency alignment in requirements for runtime compatibility.

2) 97f176e — feat(web-api): align FastAPI routes and response contract with test expectations
- Aligns web API routes (`/analyse` + `/analyze`) and response contract.
- Adds HTML root endpoint behavior and health/version response consistency.
- Normalizes analyze output shape used by web tests.

3) db42aaf — docs(audit): add compact branch merge strategy log
- Adds compact audit documentation for merged branches and fallback strategy usage.
- File added: `.github/MERGE_AUDIT_LOG_2026-02-27.md`.

## Validation Snapshot
- Test suite status at handoff: 679 passed, 0 failed.
- Command used: `python -m pytest -q`

## Recommended Upstream Integration
- Preferred: open PR from this branch/repo to upstream `main` with these 3 commits.
- Alternative (direct in upstream clone):
  - `git cherry-pick c800dd2`
  - `git cherry-pick 97f176e`
  - `git cherry-pick db42aaf`

## Risk/Notes
- Low-to-moderate risk: core recovery touched morphology internals; validated by full green test run.
- Web/API changes are backward-compatible (kept `/analyse`, added `/analyze`).
