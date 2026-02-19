# Diff: New Sections for copilot-instructions.md

## Section 1: Maqam Theory (Insert after line 48 - after Grammar Engines section)

```markdown
### 3. Maqam Theory ([src/maqam_theory](src/maqam_theory))
**Mathematical optimization framework** for Arabic sentence construction via energy minimization:
- `gates/` - Constraint gates (12 types): Declarative, Interrogative, Vocative, Imperative, etc.
- `generators/` - Candidate generation (y₀ → G(x) transformations)
- `minimizers/` - Energy function minimizers (arg min E)
- `proofs/` - Formal computational proofs (11 theorems)
- `structures/` - Core data structures (Maqam state, surface forms)

**Key Pattern**: Every gate extends `BaseGate` ([base_gate.py](src/maqam_theory/gates/base_gate.py)):
```python
class MyGate(BaseGate):
    def can_activate(self, x) -> bool:  # Activation conditions
    def compute_satisfaction(self, x, y) -> float:  # Constraint satisfaction [0,1]
    def compute_cost(self, x, y, activated) -> float:  # Energy contribution
```

### 4. Syntax Theory ([src/syntax_theory](src/syntax_theory))
**Graph-based syntactic analysis** using `x → y₀ → G(x) → arg min E` paradigm:
- `structures/` - SyntacticInput (x), SyntacticGraph (y), Node/Edge definitions
- `relations/` - Three core relations: ISN (إسناد), TADMN (تضمين), TAQYID (تقييد)
- `operators/` - 14 grammatical operators (إنّ وأخواتها, كان وأخواتها, particles)
- `generators/` - Canon(x) and G(x) functions for graph generation
- `minimizers/` - Multi-component energy function (E_rel + E_gov + E_case + ...)
- `proofs/` - Mechanized proofs of syntactic properties

**Architecture**: Directed graph y = (V_y, E_y, τ, φ) with hard gates (∞ cost for violations)

See [SYNTAX_THEORY_SUMMARY.md](SYNTAX_THEORY_SUMMARY.md) for complete mathematical formulation.
```

---

## Section 2: Enhanced Testing Documentation (Replace lines 112-115)

```markdown
### Testing
```bash
pytest -v                        # PYTHONPATH=src (configured in pytest.ini)
pytest tests/engines/phonology/  # Test specific layer
pytest tests/c2b/                # Test morphological analysis (C2b)
pytest tests/test_gate_*.py      # Test specific phonological gates
pytest tests/test_syntax_theory.py  # Test syntax theory components
```

**Test Naming Convention**:
- `test_*.py` - Module-level tests (e.g., `test_gate_sukun.py`, `test_cli.py`)
- `Test*` - Class-based test suites (e.g., `TestRootExtractorBasic`)
- Tests in subdirectories mirror `src/` structure (e.g., `tests/c2b/`, `tests/engines/`)
- All tests use pytest fixtures; PYTHONPATH automatically set to `src/` via [pytest.ini](pytest.ini)
```

---

## Section 3: Server Status Note (Add after line 131)

```markdown
**Note**: Web server is optional; core functionality is CLI-based and library-oriented.
```

---

## Section 4: Additional Key Files (Add to table at line ~235)

```markdown
| [SYNTAX_THEORY_SUMMARY.md](SYNTAX_THEORY_SUMMARY.md) | Mathematical formulation of syntax theory (x → y₀ → G(x) → arg min E) |
| [src/maqam_theory/gates/base_gate.py](src/maqam_theory/gates/base_gate.py) | Base gate for constraint-based optimization |
| [src/syntax_theory/structures/](src/syntax_theory/structures/) | Core data structures for graph-based syntax |
```

---

## Fix Applied: Removed Duplicate Lines (lines 90-91)

**Before:**
```markdown
   - Additional domain-specific columns
   - `الحركات` - Diacritics (optional, auto-filled)  # ← DUPLICATE
   - Additional domain-specific columns                # ← DUPLICATE
```

**After:**
```markdown
   - Additional domain-specific columns
```

✅ **Fixed in file**

---

## Header Change: "Two" → "Four" Main Subsystems (line 23)

**Before:**
```markdown
## Project Map (Two Main Subsystems)
```

**After:**
```markdown
## Project Map (Four Main Subsystems)
```

✅ **Already applied**

---

## Evidence Summary

All changes based on:
- ✅ 21 files inspected
- ✅ 12 gate implementations verified (`src/maqam_theory/gates/*.py`)
- ✅ 11 theorems counted (`src/maqam_theory/proofs/maqam_theorems.py:4-15`)
- ✅ Syntax theory modules verified (`src/syntax_theory/{structures,relations,generators,minimizers,proofs}/`)
- ✅ Test naming patterns extracted from 15+ test files
- ✅ web_app module confirmed non-existent (file_search + grep_search)
- ✅ SYNTAX_THEORY_SUMMARY.md verified (307 lines)
- ✅ pytest.ini configuration verified (PYTHONPATH=src)

**No speculative content - all tied to source code** ✓
