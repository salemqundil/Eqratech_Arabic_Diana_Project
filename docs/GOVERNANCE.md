# Governance | الحوكمة

This document outlines how we organize work, review changes, and publish releases.

## Roles | الأدوار

- Maintainer: approves PRs, manages releases, triages issues.
- Contributor: submits PRs and issues following the templates.

## Branching strategy | استراتيجية الفروع

- `main`: stable, protected branch.
- `feature/*` and `fix/*`: short-lived branches merged via PR.

## Reviews | المراجعات

- Minimum 1 approval required for `main`.
- CI must be green (Python syntax + tokenizer smoke).

## Releases | الإصدارات

- Use GitHub Releases. Large artifacts go as assets (preferred) or via Git LFS if needed.
