# Task 3.2: PatternCatalog Integration — What Exists

**Goal:** Connect PatternAnalyzer to Bayan's PatternUniverse for better pattern recognition.

---

## What exists in the codebase (zhe)

### 1. **PatternAnalyzer** — `src/fvafk/c2b/pattern_analyzer.py`

- **Role:** Thin wrapper that gives a stable result shape for CLI/classifiers.
- **API:** `analyze(token: str, root: Root) -> Optional[PatternAnalysis]`
- **Internals:** Uses a `PatternMatcher`; calls `matcher.match(token, root)` and wraps the result in `PatternAnalysis(pattern, confidence, features)`.
- **Dependencies:** `PatternMatcher`, `Pattern`, `Root` from morpheme/pattern_matcher.

```python
# Usage (from CLI):
from fvafk.c2b.pattern_analyzer import PatternAnalyzer
analyzer = PatternAnalyzer()
result = analyzer.analyze("كَتَبَ", root)  # root from RootExtractor
```

---

### 2. **PatternMatcher** — `src/fvafk/c2b/pattern_matcher.py`

- **Role:** Core pattern recognition: given a **word** and a **root**, returns a matching `Pattern` (or None).
- **API:** `match(word: str, root: Root) -> Optional[Pattern]`
- **Algorithm:**
  1. Compute CV from the **original word** (advanced_cv_pattern, cv_pattern from C1).
  2. Iterate over templates by category (verb, noun, plural).
  3. For each template: instantiate ف ع ل from root, compare with normalized word; if match, return `Pattern` with confidence.
  4. **CV fallback:** if no exact match, match by `cv_advanced` or `cv_simple` from the template DB (lower confidence ~0.70–0.75).
- **Dependencies:** `PatternDatabase`, `AwzanPatternLoader`, `advanced_cv_pattern` / `cv_pattern` (C1), `Pattern`, `PatternType`, `Root`.

---

### 3. **PatternDatabase** — inside `pattern_matcher.py`

- **Role:** Holds all pattern templates used by `PatternMatcher`.
- **Contents:**
  - **Hardcoded base list:** ~25+ `PatternTemplate` objects (فَعَلَ, فَعَّلَ, فَاعِل, مَفْعُول, plurals, etc.).
  - **Extra from CSV:** `AwzanPatternLoader.load()` appends more templates (no duplicates by template string).
- **API:** `get_all()`, `get_by_category(category: str)` (e.g. `"verb"`, `"noun"`, `"plural"`).
- **PatternTemplate fields:** template, pattern_type, category, form, meaning, cv_simple, cv_detailed, cv_advanced, notes; `feature_map()`, `matches_root_type(root)`.

---

### 4. **AwzanPatternLoader** — `src/fvafk/c2b/awzan_loader.py`

- **Role:** Loads additional patterns from CSV (أوزان).
- **Paths (in order):**  
  `phonology/awzan_merged_final_clean.csv` → `phonology/awzan_merged_final.csv` → `data/awzan_merged_final.csv` → `awzan-claude-atwah.csv`.
- **Returns:** `List[dict]` with keys: template, pattern_type, category, form, meaning, cv_simple, cv_detailed, cv_advanced, notes.
- **PATTERN_TYPE_MAP:** Maps Arabic template strings to `PatternType` enum (verb forms, participles, plurals, etc.).

---

### 5. **Morpheme types** — `src/fvafk/c2b/morpheme.py`

- **Root:** letters (tuple), root_type (TRILATERAL/QUADRILATERAL), weak_positions, has_hamza.
- **Pattern:** name, template, pattern_type, stem, description, weight, features.
- **PatternType:** enum (FORM_I … FORM_X, ACTIVE_PARTICIPLE, PASSIVE_PARTICIPLE, VERBAL_NOUN, plurals, etc.).
- **PatternAnalysis** (in pattern_analyzer): pattern + confidence + features dict.

---

### 6. **CLI usage**

- `src/fvafk/cli/main.py` imports `PatternAnalyzer`, builds it (optionally with morphology), and uses it for tokens that have a root (from `RootExtractor`). So the pipeline is: **token → RootExtractor → root → PatternAnalyzer.analyze(token, root) → PatternAnalysis**.

---

## What does **not** exist (yet)

| Item | Status |
|------|--------|
| **`pattern_catalog.py`** | Not present in `src/fvafk/c2b/`. Task 3.2 asks to create it. |
| **Bayan / PatternUniverse** | No module or class named "Bayan" or "PatternUniverse" in the repo. The plan refers to integrating with "Bayan's PatternUniverse" as an external or future source of patterns. |
| **`tests/test_pattern_catalog.py`** | Not present; to be added per Sprint 3 plan. |

So: **PatternAnalyzer** and **PatternMatcher** (and **PatternDatabase** + **AwzanPatternLoader**) are the current “pattern universe”; there is no separate Bayan implementation in this repo.

---

## Flow summary

```
Token (word)
    ↓
RootExtractor.extract(word)  →  Root
    ↓
PatternMatcher.match(word, root)  [uses PatternDatabase + Awzan CSV]
    ↓
Pattern  (or None)
    ↓
PatternAnalyzer wraps as  PatternAnalysis(pattern, confidence, features)
```

---

## Task 3.2 subtasks vs current state

| Subtask | Current state |
|---------|----------------|
| 3.2.1 Create `PatternCatalog` wrapper class | **To do.** No `PatternCatalog` yet; could wrap `PatternDatabase` + optional “Bayan”/external source. |
| 3.2.2 Map PatternAnalyzer to PatternUniverse | **To do.** No PatternUniverse in repo; mapping would be: PatternAnalyzer → uses a catalog that can be fed from current DB + future Bayan source. |
| 3.2.3 Pattern taxonomy (verb/noun/plural) | **Exists.** `PatternDatabase.get_by_category("verb"|"noun"|"plural")`, and `AwzanPatternLoader._infer_category`. |
| 3.2.4 Pattern matching with confidence | **Exists.** `PatternMatcher.match()` returns `Pattern` with `features["confidence"]`; CV fallback uses 0.70–0.75. |
| 3.2.5 Add 8+ tests for pattern catalog | **To do.** No `test_pattern_catalog.py` yet; there are existing tests in `tests/c2b/test_pattern_matcher.py` (and related). |
| 3.2.6 Update documentation | **To do.** Can add a short doc (e.g. in `docs/MORPHOLOGY.md` or a dedicated catalog doc) describing catalog and taxonomy. |

---

## Suggested next steps for Task 3.2

1. **Define “PatternUniverse” in this repo:** Either (a) treat the current `PatternDatabase` + Awzan as “the” pattern universe, or (b) introduce a small interface (e.g. `PatternUniverse` protocol) that `PatternDatabase` implements and a future Bayan adapter could implement.
2. **Add `pattern_catalog.py`:** A `PatternCatalog` class that:
   - Holds or wraps `PatternDatabase` (and optionally another source).
   - Exposes a simple API (e.g. `get_patterns()`, `get_by_category()`, or `match(word, root)`) used by `PatternAnalyzer`/`PatternMatcher`.
3. **Wire PatternAnalyzer to PatternCatalog:** So that `PatternAnalyzer` (or `PatternMatcher`) takes a `PatternCatalog` (or backend) instead of only the current `PatternDatabase`.
4. **Add `tests/test_pattern_catalog.py`:** At least 8 tests for catalog lookup, taxonomy, and matching with confidence.
5. **Document:** Pattern taxonomy and how PatternCatalog fits in (and how a future “Bayan” source would plug in).

This document reflects the state of the **zhe** worktree. Paths are relative to the repo root (e.g. `src/fvafk/c2b/`).
