# Pydantic Models

Type-safe data models for FVAFK/Bayan API and CLI.

## Models (Sprint 1, Task 1.3)

| Model | Description | Status |
|-------|-------------|--------|
| `Unit` | Encoding unit (C1) | Planned |
| `Syllable` | Syllable structure (C2a) | Planned |
| `WordForm` | Morphology bridge (C2b→C3) | Planned |
| `Link` | Syntactic link | Planned |
| `Evidence` | Evidence weight | Planned |
| `ProofArtifact` | Coq proof attachment | Planned |
| `AnalysisResult` | Complete pipeline output | Planned |

## Usage

```python
from app.models import WordForm, Link

# Type-safe API
wf = WordForm(surface="كتاب", pos="noun", ...)
```

## See Also

- [MASTER_PLAN_CHECKLIST.md](../../docs/MASTER_PLAN_CHECKLIST.md) - Task 1.3
