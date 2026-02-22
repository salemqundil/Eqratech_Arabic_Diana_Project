# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ Yes     |

## Reporting a Vulnerability

If you discover a security vulnerability, please **do not** open a public
GitHub issue. Instead, email the maintainer directly or open a private
security advisory on GitHub:

1. Go to the repository **Security** tab.
2. Click **"Report a vulnerability"**.
3. Fill in the form with as much detail as possible.

We aim to respond within **72 hours** and provide a patch within **7 days**
for confirmed high-severity issues.

## Scope

This project processes Arabic text strings. Known security considerations:

- **Input validation**: All text inputs should be treated as untrusted.
  The pipeline does not execute user-supplied code.
- **CSV data files**: Data files loaded at startup are read-only; they are
  not written to at runtime.
- **Web API**: The `POST /analyze` endpoint accepts arbitrary text. Implement
  authentication and rate limiting before exposing it publicly.
- **Dependencies**: All runtime dependencies are listed in `pyproject.toml`.
  Run `pip audit` or use Dependabot to monitor for known CVEs.
