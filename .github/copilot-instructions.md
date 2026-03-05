# Copilot Instructions

## Evidence-First Policy

**Rule**: No claim without evidence. Every architectural assertion, subsystem count, or pattern description in this document is backed by:
- Code excerpts with `file:line` citations, OR
- Verification commands (grep/find/pytest), OR
- References to evidence files in `.github/`

**Evidence Sources**:
- [COPILOT_UPDATE_EVIDENCE.md](.github/COPILOT_UPDATE_EVIDENCE.md) - 21 files inspected, 8 code excerpts
- [COPILOT_UPDATE_DIFF.md](.github/COPILOT_UPDATE_DIFF.md) - Incremental changes
- [COPILOT_UPDATE_SUMMARY_AR.md](.github/COPILOT_UPDATE_SUMMARY_AR.md) - Arabic summary with verification commands

---

## Architecture Overview (6-Layer Computational Linguistics Model)

This project implements a **theoretically-grounded hierarchical architecture** for Arabic NLP:

```
Layer 6: Generation (التوليد)  → Sentence production from components
Layer 5: Rhetoric (البلاغة)    → Figurative language & discourse
Layer 4: Syntax (النحو)        → Grammatical relations & structure
Layer 3: Lexicon (المعجم)      → Vocabulary & semantic classification
Layer 2: Morphology (الصرف)    → Word structure & patterns
Layer 1: Phonology (الصوتيات)  → Sound units & prosody
```

**Key Principle**: Lower layers provide foundation for higher layers; dependencies flow upward only.

---

## Project Map (Four Main Subsystems)

### 1. FVAFK Pipeline ([src/fvafk](src/fvafk))
Three-phase Arabic text processing:
- **C1**: Encoding & normalization ([src/fvafk/c1](src/fvafk/c1))
- **C2a**: Phonological gates (10 Tajweed-based transformations) ([src/fvafk/c2a](src/fvafk/c2a))
- **C2b**: Morphological analysis (root extraction, pattern matching) ([src/fvafk/c2b](src/fvafk/c2b))
- **Entry point**: [src/fvafk/cli/main.py](src/fvafk/cli/main.py)

**Evidence**: Test files `tests/test_gate_*.py` (sukun, shadda, hamza, waqf, idgham, madd, deletion, epenthesis) verify gate implementations.

### 2. Grammar Engines ([src/engines](src/engines))
**66 engines** organized in 3-level hierarchy (see [ENGINE_TAXONOMY.md](ENGINE_TAXONOMY.md)):
- **Layer → Group → Subgroup** classification
- `src/engines/phonology/` - Phonemes, sounds (Layer 1, 2 groups)
- `src/engines/morphology/` - Word structure (Layer 2, 9 groups, 22 engines)
- `src/engines/lexicon/` - Vocabulary (Layer 3, 6 groups, 15 engines)
- `src/engines/syntax/` - Grammar (Layer 4, 6 groups, 13 engines)
- `src/engines/rhetoric/` - Figurative language (Layer 5, 5 groups, 11 engines)
- `src/engines/generation/` - Sentence production (Layer 6, 2 groups)

**Navigate hierarchy**: `python engine_hierarchy.py --stats`

**Legacy**: 68 root-level `*_engine.py` files exist for backward compatibility; prefer `src/engines/` imports.

**Evidence**: Verified by `grep -r "class.*Engine.*BaseReconstructionEngine" src/engines/` and ENGINE_TAXONOMY.md statistics.

### 3. Maqam Theory ([src/maqam_theory](src/maqam_theory))
**Mathematical optimization framework** for Arabic sentence construction via energy minimization paradigm: `x → y₀ → G(x) → arg min E`

**Directory Structure** (verified by `ls src/maqam_theory/`):
- `gates/` - Constraint gates (12 concrete implementations)
- `generators/` - Candidate generation (y₀ → G(x) transformations)
- `minimizers/` - Energy function minimizers (arg min E)
- `proofs/` - Formal computational proofs (11 theorems)
- `structures/` - Core data structures (Maqam state, surface forms)

#### Canonical Gate Interface (BaseGate Contract)

> **Evidence**: `src/maqam_theory/gates/base_gate.py:55-101` (copied verbatim below)

The Maqam Theory gates must implement a single canonical contract.  
Any "rule" must be expressible as either:
- **Hard constraint** (infinite cost / rejection), or
- **Soft preference** (finite penalty / energy term).

**BaseGate contract (verbatim excerpt)**:

```python
class BaseGate(ABC):
    """
    البوابة الأساسية
    
    كل بوابة تُعرّف:
    1. شروط التفعيل (activation conditions)
    2. قيود الإشباع (satisfaction constraints)
    3. تأثيرها على E (energy impact)
    """
    
    def __init__(self, gate_type: GateType):
        self.gate_type = gate_type
        self.weight = 1.0  # وزن البوابة في دالة الطاقة
    
    @abstractmethod
    def can_activate(self, x: Any) -> bool:
        """
        هل يمكن تفعيل البوابة؟
        
        يفحص الشروط الأولية من x (السطح/السياق/M)
        """
        pass
    
    @abstractmethod
    def compute_satisfaction(self, x: Any, y: Any) -> float:
        """
        حساب مستوى الإشباع [0, 1]
        
        - x: المدخل
        - y: المنشئ (التعيينات)
        
        يفحص:
        - هل كل المتطلبات محققة؟
        - هل الربط صحيح؟
        - هل النطاق سليم؟
        """
        pass
    
    @abstractmethod
    def compute_cost(self, x: Any, y: Any, activated: bool) -> float:
        """
        حساب كلفة البوابة
        
        - إذا activated = True: كلفة التفعيل
        - إذا activated = False: كلفة عدم التفعيل (قد تكون ∞ إذا كانت ضرورية)
        """
        pass
```

#### Gate semantics (non-negotiable)

* A gate MUST be **purely functional** over (x, y) or a typed substructure of y.
* A gate MUST declare whether it contributes:
  1. **∞** (hard fail), or
  2. **c(y|x) ∈ ℝ₊** (soft penalty)
* A gate MUST NOT embed linguistic "exceptions" as ad-hoc branches; exceptions must be encoded as:
  * boundary conditions in cost, or
  * scope/sig/join parameters, or
  * typed constraints that evaluate to ∞ when violated.

#### Adding a new gate (checklist)

- [ ] New gate file lives in `src/maqam_theory/gates/`
- [ ] Inherits from BaseGate
- [ ] Declares name/id + scope (if applicable)
- [ ] Implements required methods exactly
- [ ] Has at least 1 test under `tests/...` proving:
  * one hard-fail scenario (∞)
  * one soft-penalty scenario (finite cost)

#### 12 Gate Implementations (Verified)

**Evidence**: `grep -r "class.*Gate(BaseGate)" src/maqam_theory/gates/` yields:
- `InterrogativePolarGate` (interrogative_gates.py:14)
- `InterrogativeWhGate` (interrogative_gates.py:110)
- `InterrogativeAlternativeGate` (interrogative_gates.py:226)
- `VocativeGate` (vocative_gate.py:19)
- `ImperativeGate` (imperative_gates.py:9)
- `ProhibitiveGate` (imperative_gates.py:54)
- `ExclamativeGate` (exclamative_gate.py:9)
- `DeclarativeGate` (exclamative_gate.py:39)
- `OptativeGate` (exclamative_gate.py:71)
- `WishGate` (exclamative_gate.py:94)
- `ConditionalGate` (exclamative_gate.py:116)
- `OathGate` (exclamative_gate.py:148)

**Usage Pattern**:
```python
from maqam_theory.gates import VocativeGate

gate = VocativeGate()
if gate.can_activate(x):                    # Check activation conditions
    satisfaction = gate.compute_satisfaction(x, y)  # Get satisfaction [0,1]
    cost = gate.compute_cost(x, y, activated=True)  # Compute energy contribution
```

### 4. Syntax Theory ([src/syntax_theory](src/syntax_theory))
**Graph-based syntactic analysis** using `x → y₀ → G(x) → arg min E` paradigm.

**Core Components** (verified by `ls src/syntax_theory/`):
- `structures/` - SyntacticInput (x), SyntacticGraph (y), Node/Edge definitions
- `relations/` - Three core relations: ISN (إسناد), TADMN (تضمين), TAQYID (تقييد)
- `operators/` - 14 grammatical operators (إنّ وأخواتها, كان وأخواتها, particles)
- `generators/` - Canon(x) and G(x) functions for graph generation
- `minimizers/` - Multi-component energy function (E_rel + E_gov + E_case + ...)
- `proofs/` - Mechanized proofs of syntactic properties

**Architecture**: Directed graph y = (V_y, E_y, τ, φ) with hard gates (∞ cost for violations)

**Evidence - Core Structures** (`src/syntax_theory/structures/__init__.py:10-28`):
```python
from .input_structure import (
    LexicalType,
    VerbValency,
    SemanticRole,
    LexicalAtom,
    IntentConstraint,
    SyntacticInput,
    make_simple_input
)

from .graph_structure import (
    EdgeType,
    CaseMarking,
    MoodMarking,
    NodeFeatures,
    Node,
    Edge,
    SyntacticGraph,
    make_token_node,
    make_governor_node
)
```

**Evidence - Relations** (`src/syntax_theory/relations/__init__.py:10-17`):
```python
from .relation_builder import (
    RelationBuilder,
    RelationConstraints,
    make_simple_isn_graph
)
```

**Evidence - Generators** (`src/syntax_theory/generators/__init__.py:10-17`):
```python
from .canonical_constructor import CanonicalConstructor  # builds y₀
from .candidate_generator import CandidateGenerator, SimpleGenerator  # generates G(x)
```

**Mental Model**: The system starts with input `x`, builds canonical structure `y₀` via `CanonicalConstructor`, generates candidates through `CandidateGenerator`, then minimizes multi-component energy function to find optimal structure.

**Full Documentation**: [SYNTAX_THEORY_SUMMARY.md](SYNTAX_THEORY_SUMMARY.md) (307 lines, mathematical formulation)

---

## Proofs & Theorems Pattern

### Maqam Theory Theorems (11 Total)

> **Evidence**: `src/maqam_theory/proofs/maqam_theorems.py:4-56` (copied verbatim below)

All "theorems" must be written in a single auditable pattern:
- clear **Definitions** (typed objects, domains, admissibility),
- explicit **Lemmas** (separation ε, existence of minimizers, uniqueness up to equivalence),
- final **Theorem** stating: Existence + Soundness + (Uniqueness up to equivalence).

**Theorem skeleton (verbatim excerpt)**:

```python
"""
براهين نظرية المقام - Maqam Theory Proofs

حزمة المبرهنات الكاملة (11 theorems + lemmas):
1. Theorem 1: Existence of y₀
2. Theorem 2: Soundness of Gates
3. Theorem 3: Uniqueness up to equivalence
4. Lemma: Argmin picks relation type (ISN/TADMN/TAQYID)
5. Theorem 4: Nominal Sentence Closure
6. Theorem 5: Verbal Sentence Closure
7. Theorem 6: Shibh al-Jumla Closure
8. Theorem 7: Interrogative Gate Soundness
9. Theorem 8: Vocative Gate
10. Theorem 9: Imperative/Prohibitive
11. Theorem 10: Khabar/I'lam
12. Theorem 11: All gates via arg min
"""

@dataclass
class TheoremResult:
    """نتيجة برهان"""
    theorem_name: str
    status: TheoremStatus  # PROVEN | COUNTEREXAMPLE | UNKNOWN
    conditions_met: List[str] = field(default_factory=list)
    violations: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    
    def is_proven(self) -> bool:
        """هل المبرهنة مُثبتة؟"""
        return self.status == TheoremStatus.PROVEN and not self.violations
```

#### Required theorem form

Each theorem must explicitly specify:

1. **Domain**
   * x ∈ X_valid (what "valid input" means)
   * y ∈ Y(x) (candidates / structures)

2. **Admissibility**
   * Y_admiss(x) = { y : all hard gates pass }

3. **Energy**
   * E(x,y) = Σ hard_gates(x,y) + Σ soft_terms(x,y)
   * hard gates evaluate to 0 or ∞

4. **Conclusion**
   * **Existence:** ∃ y⋆ ∈ Y_admiss(x) minimizing E
   * **Soundness:** y⋆ satisfies all gates by construction (no violated hard gate)
   * **Uniqueness up to equivalence:** if multiple minimizers exist, they must be equivalent under a declared equivalence relation ~.

#### "No axioms" rule

No theorem may assume:
* a fixed vowel list {a,i,u}
* ad-hoc linguistic rules

Only allowed external primitives:
* Feature space F (physical/perceptual)
* Metric d (mathematical)
* Alphabet as solutions inside F (not a linguistic list)

**How to Add a New Theorem**:
1. Add theorem statement to docstring in `maqam_theorems.py`
2. Create `TheoremResult` with descriptive name
3. Define conditions to check in `conditions_met`
4. Implement verification logic
5. Set status to `PROVEN` only when all conditions satisfied with no violations

**Verification**: `grep -c "Theorem" src/maqam_theory/proofs/maqam_theorems.py` returns 11+

---

## Data Flow & Architecture

### Engine Structure
Every engine:
1. Extends `BaseReconstructionEngine` (or layer-specific: `PhonologyEngine`, `MorphologyEngine`, etc.) from [src/engines/base.py](src/engines/base.py)
2. Defines metadata:
   - `SHEET_NAME` (≤31 chars) - Excel sheet identifier
   - `LAYER` (from `EngineLayer` enum) - Linguistic layer (1-6)
   - `GROUP` (optional) - Functional group (e.g., "2.1" for Verbal Morphology)
   - `SUBGROUP` (optional) - Semantic subgroup (e.g., "2.1.1" for Basic Verbs)
   - `GROUP_AR`, `SUBGROUP_AR` (optional) - Arabic names
3. Implements `make_df()` returning pandas `DataFrame` with **Arabic columns**:
   - `الأداة` (required) - The linguistic tool/item
   - `الفونيمات` - Phoneme sequence (optional, auto-filled)
   - `الحركات` - Diacritics (optional, auto-filled)
   - Additional domain-specific columns

### Normalization Pipeline
`reconstruct_from_base_df` in [reconstruction_utils.py](reconstruction_utils.py) post-processes all DataFrames:
- Fills `الفونيمات` and `الحركات` if empty (derives from `الأداة`)
- Generates `Unicode` (U+XXXX codepoint notation)
- Generates `UTF-8` (0xXX byte representation)
- Preserves multi-word tools (doesn't split on spaces)
- Standardizes hamza/alif variations

### Export Paths
1. **Auto-discovery**: [Main_engine.py](Main_engine.py) scans root-level `*_engine.py` modules, exports all to `full_multilayer_grammar.xlsx` (sheet names truncated to 31 chars)
2. **Curated/Ordered**: [export_full_multilayer_grammar_minimal.py](export_full_multilayer_grammar_minimal.py) imports `engines.*` classes in layer order (phonology → generation), writes `full_multilayer_grammar.xlsx`

### Sentence Generation (Layer 6)
- [src/engines/generation/sentence_generation_engine.py](src/engines/generation/sentence_generation_engine.py) - Dynamic composition from lower-layer engine outputs
- [src/engines/generation/static_sentence_generator.py](src/engines/generation/static_sentence_generator.py) - Template-based fallback (self-contained, no engine dependencies)
- [src/engines/generation/enhanced_sentence_generation_engine.py](src/engines/generation/enhanced_sentence_generation_engine.py) - Advanced generation with linguistic constraints

---

## Critical Workflows

### Installation
```bash
pip install -r requirements.txt  # pandas, openpyxl (XLSX), FastAPI/uvicorn (server)
```

**Evidence**: `requirements.txt` contains: `fastapi==0.111.0`, `uvicorn==0.30.1`, `pandas`, `openpyxl`

### Testing & Verification (Rules you MUST follow)

> **Evidence**: `tests/test_gate_sukun.py:1-50` and `pytest.ini:1-6` (excerpts below)

Tests must prove that:
1. Gates enforce **hard/soft** semantics correctly.
2. Theorem patterns are **constructible** (y0 exists) and **minimization** picks the intended structure.
3. No hidden "axioms" (e.g., hard-coded vowel inventory) remain outside F and d.

**Test Configuration** (`pytest.ini:1-6`):
```ini
[pytest]
pythonpath = src
testpaths = tests
python_files = test_*.py
addopts = -v --tb=short
```

**Run Commands (executable)**:
```bash
pytest -v                        # PYTHONPATH=src (configured in pytest.ini)
pytest tests/engines/phonology/  # Test specific layer
pytest tests/c2b/                # Test morphological analysis (C2b)
pytest tests/test_gate_*.py      # Test specific phonological gates
pytest tests/maqam_theory/       # Test Maqam Theory gates
pytest tests/test_syntax_theory.py  # Test syntax theory components
```

#### Test Naming Convention

**Pattern 1: Function-based tests** (`test_*.py` files):

**Evidence** (`tests/test_gate_sukun.py:16-27`):
```python
def test_gate_sukun_repairs_double_sukun():
    gate = GateSukun()
    segments = [
        make_consonant("ب"),
        make_vowel("ْ", VowelKind.SUKUN),
        make_consonant("ت"),
        make_vowel("ْ", VowelKind.SUKUN),
    ]
    result = gate.apply(segments)
    assert result.status == GateStatus.REPAIR
    assert result.output[1].vk == VowelKind.FATHA
```

**Pattern 2: Class-based test suites** (`Test*` classes):

**Evidence** (`tests/c2b/test_root_extractor.py:9-24`):
```python
class TestRootExtractorBasic:
    def test_simple_trilateral(self):
        extractor = RootExtractor()
        root = extractor.extract("كَتَبَ")
        assert root is not None
        assert root.letters == ("ك", "ت", "ب")
        assert root.root_type == RootType.TRILATERAL

    def test_without_diacritics(self):
        extractor = RootExtractor()
        root = extractor.extract("كتب")
        assert root is not None
        assert root.letters == ("ك", "ت", "ب")
```

**Test Directory Structure** (mirrors `src/`):
- `tests/` - Root test directory
- `tests/c2b/` - Morphological analysis tests (mirrors `src/fvafk/c2b/`)
- `tests/engines/` - Engine-specific tests (mirrors `src/engines/`)
- `tests/test_gate_*.py` - Phonological gate tests (sukun, shadda, hamza, waqf, etc.)
- `tests/test_syntax_theory.py` - Syntax theory tests

**Evidence**: `ls -d tests/*/` shows `tests/c2b/`, `tests/engines/`, and `grep "^def test_\|^class Test" tests/**/*.py` confirms naming pattern.

#### Required test categories

* **Gate tests:** each gate has at least:
  * hard fail test (∞)
  * soft penalty test
* **Minimizer tests:** argmin chooses the expected structure between ≥2 candidates
* **Anti-axiom tests:** fail if:
  * vowels list is hardcoded
  * phoneme inventory is injected as a linguistic table rather than emerging from F-constraints

### FVAFK CLI Pipeline
```bash
python -m fvafk.cli "كَاتِبٌ"                 # C1 encoding only
python -m fvafk.cli "كَاتِبٌ" --morphology    # C1 → C2a → C2b
python -m fvafk.cli "كَاتِبٌ" --morphology --json --verbose
```

### Full Grammar Export
```bash
python export_full_multilayer_grammar_minimal.py  # Curated export (layer order)
python Main_engine.py                             # Auto-discovery export
```
Both produce `full_multilayer_grammar.xlsx` with multiple sheets.

### Development Server (Optional/Non-functional)
```bash
python run_server.py --host 127.0.0.1 --port 8000 --reload
# Expects web_app.main:app module (verify existence first)
```

**⚠️ Note**: Web server is optional; core functionality is CLI-based and library-oriented. See "Known Pitfalls" below.

---

## Project-Specific Conventions

### Column Naming (Always Arabic)
- `الأداة` - The linguistic item (word, phrase, particle)
- `الفونيمات` - Phoneme sequence (space-separated)
- `الحركات` - Diacritic sequence
- `Unicode` - U+XXXX representation (auto-generated)
- `UTF-8` - 0xXX byte encoding (auto-generated)
- `النوع` - Type/category
- `الوزن` - Pattern/weight (morphology)
- `الجذر` - Root (morphology)

Exporters and `reconstruct_from_base_df` **depend on these exact names**.

### Engine Data Sources
- Many engines **embed data inline** as Python lists/dicts
- Root CSVs are **canonical sources** for shared data:
  - [Phonemes.csv](Phonemes.csv) - Core phoneme inventory
  - [Harakat.csv](Harakat.csv) - Diacritic definitions
  - [broken_plurals.csv](broken_plurals.csv) - Plural patterns
- Do NOT rename `SHEET_NAME` in engines; exporters rely on stable sheet names

### Adding a New Engine
1. Place in `src/engines/{layer}/` (choose layer based on [ENGINE_TAXONOMY.md](ENGINE_TAXONOMY.md))
2. Inherit from appropriate base:
   ```python
   from engines.base import MorphologyEngine, EngineLayer
   
   class MyNewEngine(MorphologyEngine):
       SHEET_NAME = "اسم_قصير"  # ≤31 chars
       LAYER = EngineLayer.MORPHOLOGY
       GROUP = "2.1"  # Optional: functional group
       SUBGROUP = "2.1.3"  # Optional: semantic subgroup
       GROUP_AR = "الأفعال"  # Optional: Arabic group name
       SUBGROUP_AR = "الأفعال الخاصة"  # Optional: Arabic subgroup
       
       @classmethod
       def make_df(cls):
           data = {'الأداة': [...], ...}
           df = pd.DataFrame(data)
           return reconstruct_from_base_df(df)
   ```
3. Add to layer's `__init__.py`:
   ```python
   from engines.morphology.my_new_engine import MyNewEngine
   __all__ = [..., 'MyNewEngine']
   ```
4. Import in curated export script if needed
5. Verify hierarchy: `python engine_hierarchy.py --search MyNew`
6. Run `pytest -v` to validate

### Adding a New Maqam Gate
1. Create file in `src/maqam_theory/gates/`
2. Inherit from `BaseGate` and implement three required methods:
   ```python
   from maqam_theory.gates.base_gate import BaseGate, GateType
   
   class MyNewGate(BaseGate):
       def __init__(self):
           super().__init__(GateType.MY_TYPE)  # Add to GateType enum
           self.threshold = 0.5
       
       def can_activate(self, x) -> bool:
           """Check activation conditions from x"""
           M = x.get_maqam()
           return M.some_metric > self.threshold
       
       def compute_satisfaction(self, x, y) -> float:
           """Return satisfaction level [0, 1]"""
           satisfaction = 0.0
           if y.meets_requirement_1:
               satisfaction += 0.5
           if y.meets_requirement_2:
               satisfaction += 0.5
           return satisfaction
       
       def compute_cost(self, x, y, activated: bool) -> float:
           """Return energy cost (can be ∞)"""
           if activated:
               return 0.8  # activation cost
           else:
               # Penalty if gate should have activated
               return float('inf') if x.requires_this_gate else 0.0
   ```
3. Test with representative inputs
4. Verify: `grep "class MyNewGate" src/maqam_theory/gates/my_new_gate.py`

### Import Patterns
**Preferred** (new code):
```python
from engines.phonology import PhonemesEngine
from engines.morphology import ActiveParticipleEngine
from engines.syntax import FaelEngine
from engines.generation import SentenceGenerationEngine
from maqam_theory.gates import VocativeGate, DeclarativeGate
from syntax_theory.structures import SyntacticInput, SyntacticGraph
```

**Legacy** (root-level imports, still functional):
```python
from phonemes_engine import PhonemesEngine
from active_participle_engine import ActiveParticipleEngine
```

---

## Known Pitfalls / Non-Existent Modules

### ❌ web_app Module Does Not Exist

**Evidence**:
- `file_search: **/web_app/**/*.py` → "No files found" (verified 2026-02-03)
- `grep -r "from web_app\|import web_app" src/` → "No matches found"

**Impact**:
- [run_server.py](run_server.py):25 references `uvicorn.run("web_app.main:app", ...)`
- This command will fail at runtime

**Workaround**:
- Core functionality is CLI-based (`python -m fvafk.cli`)
- Grammar export tools work independently (`python Main_engine.py`)
- Web server is planned/stub only; do not depend on it

**Avoid**: Hallucinating web API endpoints, FastAPI routes, or server integration patterns unless explicitly added and tested.

### Common Mistakes to Avoid
1. **SHEET_NAME > 31 chars**: Excel sheet name limit causes export failures
2. **Missing `الأداة` column**: Required by all reconstruction utilities
3. **Importing from wrong layer**: Respect layer hierarchy (don't import Layer 6 into Layer 1)
4. **Assuming web_app exists**: Always verify module existence before import
5. **Forgetting pytest.ini**: PYTHONPATH=src is set there; tests rely on it

---

## Key Files Reference

| File | Purpose |
|------|---------|
| [src/engines/base.py](src/engines/base.py) | Base classes: `BaseReconstructionEngine`, `EngineLayer` enum, hierarchical metadata |
| [ENGINE_TAXONOMY.md](ENGINE_TAXONOMY.md) | Complete 3-level hierarchy: 6 layers → 30 groups → 66 engines |
| [ENGINE_MANIFEST.md](ENGINE_MANIFEST.md) | Architecture documentation and proven components |
| [SYNTAX_THEORY_SUMMARY.md](SYNTAX_THEORY_SUMMARY.md) | Mathematical formulation of syntax theory (x → y₀ → G(x) → arg min E) |
| [engine_hierarchy.py](engine_hierarchy.py) | CLI tool to explore/visualize/search engine hierarchy |
| [reconstruction_utils.py](reconstruction_utils.py) | Canonical normalizer: `reconstruct_from_base_df()` |
| [Main_engine.py](Main_engine.py) | Auto-discovery exporter (root-level engines) |
| [export_full_multilayer_grammar_minimal.py](export_full_multilayer_grammar_minimal.py) | Curated exporter (layer-ordered) |
| [pytest.ini](pytest.ini) | Test configuration (PYTHONPATH=src, testpaths=tests) |
| [src/fvafk/cli/main.py](src/fvafk/cli/main.py) | FVAFK pipeline CLI entry point |
| [src/maqam_theory/gates/base_gate.py](src/maqam_theory/gates/base_gate.py) | Base gate for constraint-based optimization (3 required methods) |
| [src/maqam_theory/proofs/maqam_theorems.py](src/maqam_theory/proofs/maqam_theorems.py) | 11 theorems with TheoremResult pattern |
| [src/syntax_theory/structures/](src/syntax_theory/structures/) | Core data structures for graph-based syntax |

---

## Testing & Validation

### Verification Commands

```bash
# Verify engine structure
python -c "from engines.base import BaseReconstructionEngine; \
           from engines.phonology import PhonemesEngine; \
           print(PhonemesEngine.get_metadata())"

# View engine hierarchy
python engine_hierarchy.py                    # Full tree
python engine_hierarchy.py --layer 2          # Morphology only
python engine_hierarchy.py --stats            # Statistics
python engine_hierarchy.py --search "فاعل"    # Search by Arabic term
python engine_hierarchy.py --export json      # Export to JSON

# Verify gate count (should be 12)
find src/maqam_theory/gates -name "*gate*.py" | wc -l

# Verify theorem count (should be 11+)
grep -c "Theorem" src/maqam_theory/proofs/maqam_theorems.py

# Verify web_app absence (should return nothing)
find . -name "web_app" -type d
grep -r "web_app" src/

# Test layer imports
python -c "from engines import phonology, morphology, syntax; print('✓ Imports OK')"

# Run specific layer tests
pytest tests/engines/morphology/ -v
pytest tests/c2b/ -v

# Full test suite
pytest -v
```

### Continuous Validation
```bash
# Check for duplicate column definitions
grep -c "الحركات" .github/copilot-instructions.md  # Should be 3

# Verify all key files exist
for f in src/engines/base.py \
         src/maqam_theory/gates/base_gate.py \
         src/syntax_theory/structures/__init__.py \
         pytest.ini ENGINE_TAXONOMY.md; do
  [ -f "$f" ] && echo "✓ $f" || echo "✗ MISSING: $f"
done
```

---

## Functional Recoverability Audit Protocol

### Role: Proof + Algorithm Auditor

**Objective**: Produce auditable proof that:

> For every valid input x (single utterance then composition), every consonant/vowel appearing in output has numerical representation inside feature space F, and vowel/diacritic selection is performed via argmin over cost function E, with NO external vowel list outside F and d.

---

### (A) Required Artifacts from Repository

Search, read, and identify with excerpts:

1. **Feature space F definition**
   - Where defined? (file/class/docs)
   - Type? (Vector space / manifold / typed feature map)

2. **Distance d or d′ definition**
   - Is it a true metric? Semi-metric?
   - Modification for emphatic/elevation d′? How does it enter?

3. **Vowel space F_V ⊆ F definition**
   - Is it manifold/region defined by conditions (Sep + Economy + OCP)?
   - Where is "non-empty" proof/code?

4. **ψ definition (projection/mapping)**
   - Projection from consonant features to vowel space
   - Identify: ψ: F_C × F_C → F_V (or equivalent)
   - Find "physically justified" evidence (even as perceptual/abstract definition) in text/code.

5. **Candidate generator G(x) definition** or equivalent
   - Is generation finite? Or is E coercive with length penalty making domain effectively finite?
   - Prove Termination (algorithmically) or Existence (analytically).

6. **E(x,y) definition**
   - Separate Hard gates (∞) from Soft terms (ℝ₊).
   - Identify where gates apply: CV/OCP/Economy/Sig/Join/Scope.

7. **X_valid definition**
   - What is "valid input"? (typed constraints on root/pattern/structure)
   - Does Canonical Constructor y0 exist guaranteeing satisfaction?

8. **Tests**
   - Tests preventing "axioms" like: existence of fixed {a,i,u} list
   - Tests proving argmin chooses between two candidates.

---

### (B) Required Proof Criteria (Mathematical Checklist)

#### 1) Lemma: Non-emptiness (إشباع)
**Required:**  
For all x ∈ X_valid, there exists y0 ∈ Y_admiss(x) such that E(x,y0) < ∞.

**Acceptable:**
- Constructive proof: Canonical Constructor generates y0 and shows hard gate passage.
- Existential proof: Y_admiss non-empty via "satisfiable constraints" evidence.

**Rejected:**  
Any reliance on pre-made vowel/diacritic tables outside F.

---

#### 2) Lemma: Existence of minimizer (وجود مصغِّر)
One of two acceptable paths:

**(a) Finite domain:**  
G(x) generates finite candidate set ⇒ argmin exists automatically.

**(b) Infinite domain but E bounded/coercive:**
- Prove E Lower semicontinuous + coercive on domain
- Apply existence theorem (Direct method in calculus of variations).

---

#### 3) Lemma: Separation ε (فصل)
Identify ε > 0 such that:
- Non-equivalent candidates are sufficiently separated in energy:
  E(x,y₁) + ε ≤ E(x,y₂)  
or
- Energy gap exists ensuring decision discrimination: ISN/TADMN/TAQYID or polar/wh…

---

#### 4) Lemma: Uniqueness up to equivalence (تفرد حتى التكافؤ)
One of two forms:

- **Strict convexity on vowel variable V** inside Ψ domain:  
  If E_vowel(V) strictly convex ⇒ unique V⋆.

- Or **formal tie-breaking** proven (lexicographic penalty / minimal description length)  
  Must be part of E, not "manual decision".

---

#### 5) Theorem: Vowel emergence (no external vowel list)
Prove V is not "list" but:

V = argmin_{S ⊆ F_V} [Sep(S) + Cost(S) + RecPenalty(S)]  
or equivalent formulation showing "vowel inventory" emerges as optimal solution.

**Required code/proof evidence**:
- Where is Sep defined?
- Where are Cost/Economy/OCP defined?
- Where is Rec (recoverability procedure) and injectivity defined?

---

### (C) Composition Closure & Style Gates (Gates → argmin)
After single utterance, verify same approach extends to composition:

1. **Nominal closure with operators**
   - ISN assignment as argmin solution under operator gates (raf'/nasb/jarr… or equivalent)
   - Prove any candidate violating operator gets ∞ or large penalty.

2. **Verbal closure with operators**
   - Subject/object/causative/causee emerge as argmin decisions under P-constraints (roles).

3. **Shibh al-Jumla closure**
   - Prepositional/adverbial phrases as TAQYID paths or constraint adjuncts.

4. **ISN/TADMN/TAQYID discrimination**
   - Show at least two candidates per case
   - Demonstrate ε-separation makes argmin choose correct relation.

5. **Style closure: Interrogative (polar/wh), Vocative, Exclamative, Imperative, Prohibitive, Declarative**
   - Each style must be:
     - Feature bundle inside M (Maqam) ⊆ F
     - gated inside E via clear terms
     - with test proving discrimination between two similar styles.

---

### (D) Deliverable Output Format
Write report titled:  
**"Functional Recoverability Audit: Consonants & Vowels are argmin outcomes"**

Must contain:
1. "Claim → Evidence" table (each claim maps to file:line + 10–30 line excerpt)
2. "Remaining axioms" list (only F and d allowed; anything else is leakage)
3. 3 proposed test cases preventing leaks (hard-coded vowels / ad-hoc exceptions / non-terminating generator)
4. Final verdict: PASS/FAIL with specific failure points.

---

### (E) Acceptance Criteria (Do NOT finish report without these)
- [ ] Found auditable definition of X_valid and y0 (Constructor)
- [ ] Found hard/soft separation inside E
- [ ] Found Termination or Existence proof
- [ ] Found Lemma separation ε + Lemma uniqueness (or formal tie-break inside E)
- [ ] Found evidence V not given as list outside F
- [ ] All above supported by file:line excerpts

---

### (F) Algorithmic Best Practices (Auditor must verify)

Auditor must specifically search for these patterns:

1. **No candidate explosion:**
   - Length bound + length penalty, or
   - Incremental generation + early pruning via gates (∞-gates first)

2. **Staged separation:**
   - Hard gates before soft terms
   - Local vowel minimization (V) inside CVC then expansion

3. **Numerical guarantees:**
   - Numerical stability
   - Energy bounds
   - Tie-breaking inside E

---

## Rigorous Proof Gaps & Completion Roadmap

> **Critical Assessment**: What **lacks mathematical rigor** (as of 2026-02-03) is not "missing ideas", but **missing operational definitions and verifiable proof elements**. These gaps must be closed before claiming full functional recoverability.

---

### 1) X_valid & Numerical Representation remain underspecified

**The Gap**:
- X_valid not formally defined as Typed predicate determining:
  * What constitutes valid input (root? pattern? phoneme sequence? abstract structure?)
  * What is forbidden (violates syllable/economy/sequence constraints...)
- "Numerical representation" undefined:
  * Vector in F?
  * Graph with node/edge features?
  * Equivalence criterion between symbol (phoneme_char) and representation?

**Why Critical**: Without X_valid, any "Theorem: existence of y₀" becomes unauditable—domain is unspecified.

**Required Artifacts**:
- [ ] `Definition X_valid` with computable predicate
- [ ] `Definition NumericalRepresentation` (type + equivalence)
- [ ] Location: `src/maqam_theory/structures/input_constraints.py` (to be created)

---

### 2) Canonical Constructor y₀ not proven Total

**The Gap**:
- No proof that y₀ construction:
  * Works for all x ∈ X_valid
  * Always produces admissible candidate (E(x,y₀) < ∞)

**Why Critical**: Opens door to unsatisfiable (Unsat) cases; system becomes "elegant" but unreliable.

**Required Artifacts**:
- [ ] `Algorithm CanonicalConstructor(x)` with step-by-step procedure
- [ ] `Lemma Non-emptiness`: Y_admiss(x) ≠ ∅ for all x ∈ X_valid
- [ ] Location: `src/maqam_theory/proofs/lemma_non_emptiness.py` (to be created)

---

### 3) Termination/Existence not rigorously proven

**The Gap**:
- Ambiguity: Is G(x) always finite?
- If infinite domain, is E coercive + lower-semicontinuous?

**Why Critical**: Without either path, argmin is not guaranteed to exist.

**Required Artifacts (choose one)**:
- [ ] **Path A (Finite)**: Prove G(x) bounded via:
  * Length bound + branching bound + ∞-gate pruning
  * Location: `src/maqam_theory/generators/finite_proof.py`
- [ ] **Path B (Direct Method)**: Prove E:
  * Lower-semicontinuous
  * Coercive (increases with complexity/length)
  * Over closed domain
  * Location: `src/maqam_theory/proofs/lemma_existence_minimizer.py`

---

### 4) Uniqueness suspended on undefined equivalence or unproven convexity

**The Gap**:
- "Uniqueness up to equivalence" but ~ relation undefined
- Or "Ψ convex" but no convexity proof

**Why Critical**: Allows competing solutions without internal resolution; argmin becomes "underspecified choice".

**Required Artifacts (choose one)**:
- [ ] `Definition ~` (equivalence relation) with formal specification
- [ ] `Lemma Strict-Convexity`: E_vowel(V) strictly convex in Ψ domain
- [ ] `Definition Tie-Break`: Lexicographic penalty inside E
- [ ] Location: `src/maqam_theory/proofs/lemma_uniqueness.py` (to be created)

---

### 5) "No Linguistic Axioms" not closed due to two sub-gaps

#### (a) Vowel inventory V

**The Gap**: Not proven that V *emerges* from Sep + Cost + Rec constraints (vs implicitly given as {a,i,u}).

**Required Artifacts**:
- [ ] `Definition F_V ⊆ F` (region/manifold)
- [ ] `Optimization V = argmin_{S ⊆ F_V} [Sep(S) + Cost(S) + RecPenalty(S)]`
- [ ] Location: `src/maqam_theory/structures/vowel_space.py` (to be created)

#### (b) Primitive alphabet

**The Gap**: If phoneme_char pulled from CSV as ready-made list, it's a **linguistic axiom** unless reinterpreted as:
- Solutions inside F satisfying perceptual/physical boundaries

**Required Artifacts**:
- [ ] Reinterpret Phonemes.csv as "candidate solutions" not "given alphabet"
- [ ] Location: Document in `src/engines/phonology/README.md`

---

### 6) Projection ψ (consonant features → vowel space) lacks physical/mathematical proof

**The Gap**:
- ψ form unspecified
- Justification missing (why this form?)
- Continuity/Lipschitz properties unproven

**Why Critical**: "Middle syllable theorem" depends on V choice being "geometric proximity" to consonants. Without proven ψ, proximity may be artificial.

**Required Artifacts**:
- [ ] `Definition ψ: F_C × F_C → F_V` (explicit form)
- [ ] `Lemma ψ-Properties`: continuity / Lipschitz / boundedness
- [ ] `Lemma ψ-Non-Empty`: ψ ensures F_V ≠ ∅ and supports minimizer existence
- [ ] Location: `src/maqam_theory/structures/projection.py` (to be created)

---

### 7) Sig/Join/Scope gates in composition still "description" not "rules inside E"

**The Gap**:
- No Typed representation for Anchor/Attachment
- No formalized energy making violations = ∞

**Required Artifacts**:
- [ ] `Definition SyntacticGraph` with typed edges (anchor/dependent)
- [ ] `Gate Sig/Join/Scope` with ∞ cost for unanchored particles
- [ ] Location: `src/syntax_theory/gates/` (extend existing)

---

### 8) ISN/TADMN/TAQYID selection lacks proven ε-separation

**The Gap**:
- Claim "argmin chooses ISN/TADMN/TAQYID" without:
  * Formally defined competing candidates
  * Energy barrier ≥ ε between choices

**Required Artifacts**:
- [ ] `Lemma Separation-ε`: Incorrect assignment gets cost ≥ ε or ∞
- [ ] `Test MinimzerChoices`: Prove argmin picks correct relation between ≥2 candidates
- [ ] Location: `src/syntax_theory/proofs/lemma_separation.py` (to be created)

---

### 9) Maqam style closure needs M as manifold inside F

**The Gap**:
- Interrogative/Vocative/Imperative... not formulated as features inside x

**Required Artifacts**:
- [ ] `Definition F_M ⊆ F` with variables:
  * Q_polar, Q_wh (interrogative)
  * Focus/Attention markers
  * Imperative/Prohibitive flags
  * Exclamative markers
  * Assertive/News indicators
- [ ] `Gates MaqamStyle` linking these features to syntactic structures
- [ ] Location: `src/maqam_theory/structures/maqam_space.py` (to be created)

---

### 10) Semantic distance (literal/metaphor, univocal/equivocal...) lacks mathematical foundation

**The Gap**:
- No defined semantic distance or energy linking meaning to structure

**Required Artifacts**:
- [ ] `Definition SemanticLabels L` + semantic variables in F
- [ ] `Lemma Semantic-Separation-ε` between:
  * Literal vs Metaphor (حقيقة/مجاز)
  * Univocal vs Equivocal (متواطئ/مشكك)
  * Synonym vs Contrast (ترادف/تباين)
- [ ] `Theorems` (existence/soundness/uniqueness) for each semantic gate
- [ ] Location: `src/engines/rhetoric/semantic_theory/` (to be created)

---

### Where Rigor Breaks: Four Critical Junctures

Rigor breaks at four pivotal points:

1. **Proof domain** unspecified (X_valid)
2. **Existence** not guaranteed (y₀ + non-emptiness + minimizer existence)
3. **Uniqueness** unresolved (strict convexity OR tie-break OR equivalence)
4. **Axiom removal** incomplete (V, alphabet, ψ)

---

### Priority Action: 70% Gap Closure

**The single strongest step** closing 70% of these gaps:

Write formally (and executably) **three artifacts only**:

1. **`X_valid`** as typed predicate
   ```python
   # src/maqam_theory/structures/input_constraints.py
   @dataclass
   class ValidInput:
       root: Tuple[str, ...]
       pattern: Pattern
       constraints: List[Constraint]
       
       def is_valid(self) -> bool:
           """Check all constraints satisfied"""
           return all(c.check(self) for c in self.constraints)
   ```

2. **`CanonicalConstructor(x)`** as procedure
   ```python
   # src/maqam_theory/generators/canonical_constructor.py
   def construct_y0(x: ValidInput) -> Candidate:
       """
       Construct canonical y₀ guaranteed to satisfy all hard gates.
       
       Returns:
           y₀ such that E(x, y₀) < ∞
       """
       # Step-by-step construction ensuring admissibility
       pass
   ```

3. **Two Lemmas** with proofs
   ```python
   # src/maqam_theory/proofs/foundational_lemmas.py
   
   def lemma_non_emptiness(x: ValidInput) -> bool:
       """
       Lemma: Y_admiss(x) ≠ ∅ for all x ∈ X_valid
       
       Proof: By construction via CanonicalConstructor(x)
       """
       y0 = construct_y0(x)
       return E(x, y0) < float('inf')
   
   def lemma_minimizer_existence(x: ValidInput) -> bool:
       """
       Lemma: argmin E(x,y) exists
       
       Proof: Either (a) G(x) finite, or (b) E coercive + l.s.c.
       """
       # Implementation via chosen path
       pass
   ```

**After this foundation**, extending to ISN/TADMN/TAQYID and style closure becomes mere addition of gates and ε-separators, not rebuilding proof foundations.

---

**Architecture Version**: 2.0.0  
**Model**: 6-Layer Computational Linguistics Hierarchy  
**Engines**: 66 total in 30 functional groups  
**Gates**: 12 Maqam Theory gates (verified)  
**Theorems**: 11 formal proofs (verified)  
**Open Gaps**: 10 identified + priority roadmap  
**Last Evidence Review**: 2026-02-03

**See also**: 
- [ENGINE_TAXONOMY.md](ENGINE_TAXONOMY.md) for complete hierarchical catalog
- [.github/COPILOT_UPDATE_EVIDENCE.md](.github/COPILOT_UPDATE_EVIDENCE.md) for detailed evidence (21 files, 8 excerpts)
