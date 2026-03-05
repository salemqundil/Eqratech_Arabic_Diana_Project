# FVAFK Application Layer

This directory contains the application layer for FVAFK/Bayan.

## Structure

```
app/
├── api/          # FastAPI endpoints (Sprint 6)
├── models/       # Pydantic models (Sprint 1, Task 1.3)
└── README.md
```

## Status

- **Sprint 1**: Pydantic models (in progress)
- **Sprint 6**: FastAPI service, endpoints, deployment

## Usage

```python
from app.models import WordForm, Link, AnalysisResult

# Use typed models for API/CLI
```

## See Also

- [pyproject.toml](../pyproject.toml) - Package metadata
- [src/fvafk/](../src/fvafk/) - Core pipeline implementation
- [ENHANCED_ROADMAP.md](../ENHANCED_ROADMAP.md) - Development plan
