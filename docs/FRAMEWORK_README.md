# Vowel Space Optimization and Morphological Framework

A comprehensive, mathematically rigorous framework for Arabic phonology and morphology.

## Quick Start

```bash
# Run all demonstrations
python src/fvafk/vowel_space_optimization.py
python src/fvafk/node_schema.py
python src/fvafk/energy_evaluation.py
python src/fvafk/generative_plurals.py
python src/fvafk/parameter_learning.py
python src/fvafk/augmentation_operators.py
python src/fvafk/particle_loader.py

# Run integration demo
PYTHONPATH=. python examples/integration_demo.py

# Run tests
pytest tests/test_vowel_space_optimization.py tests/test_node_schema_energy.py tests/test_particle_loader.py -v
```

## Modules Overview

### 1. Vowel Space Optimization (`vowel_space_optimization.py`)

Implements rigorous mathematical conditions for optimal vowel systems.

**Key Features:**
- Perceptual distance function with rounding weight κ
- Articulation cost with comfortable center
- Collapse prevention: λ < D_tri / C_tri
- Rounding attachment to /u/: ε < ρ < √κ

**Example:**
```python
from src.fvafk.vowel_space_optimization import *

params = OptimizationParameters(lambda_=0.3, kappa=1.0, rho=0.5)
optimizer = VowelSpaceOptimizer(params)
report = optimizer.verify_optimal_system()
print(f"Optimal: {report['optimal']}")  # True
```

### 2. Unified Node Schema (`node_schema.py`)

Single representation for inflected and built-in words.

**Key Features:**
- Support for معرب (inflected) and مبني (built-in)
- Case/Mood with locking status
- Join policies (MUST, PREFER, FREE, FORBID)
- Attachment signatures

**Example:**
```python
from src.fvafk.node_schema import *

prep = create_preposition("prep1", "في", Case.GEN)
noun = create_noun("noun1", "بيت", Case.GEN)
pron = create_attached_pronoun("pron1", "ه")
```

### 3. Energy-Based Evaluation (`energy_evaluation.py`)

Hard constraints via "infinity gates".

**Key Features:**
- Energy components (E_attach, E_case, E_join, E_dist, E_morph)
- Infinity for constraint violations
- Numerical example: "في بيتِهِ"

**Example:**
```python
from src.fvafk.energy_evaluation import *

evaluator = EnergyEvaluator()
candidate = Candidate([prep, noun, pron])
energies, status = evaluator.evaluate_candidate(candidate)
```

### 4. Generative Plural Templates (`generative_plurals.py`)

Templates generated from constraints, not hardcoded lists.

**Key Features:**
- Syllable constraints (CV, CVC, CVV, CVVC)
- Economy constraints (minimize transitions, avoid OCP)
- Dynamic template generation
- Optimal template selection

**Example:**
```python
from src.fvafk.generative_plurals import *

generator = TemplateGenerator()
root = ('ك', 'ت', 'ب')
templates = generator.generate_plural_templates(root)
```

### 5. Parameter Learning (`parameter_learning.py`)

Learn weights without changing function form.

**Key Features:**
- Fixed function: F_w(x) = argmin Σ w_i φ_i(y; x)
- Regularization: L(w) = Σ loss + μ||w||²
- Structured perceptron algorithm

**Example:**
```python
from src.fvafk.parameter_learning import *

learner = StructuredLearner(features, mu=0.01)
learner.train(training_data, candidate_generator)
weights = learner.get_weights()
```

### 6. Augmentation Operators (`augmentation_operators.py`)

Augmentation letters as insertion operators.

**Key Features:**
- Position-specific operators (PRE, IN1, IN2, IN3, POST)
- C_2 as economy center
- Support for س، ل، ت، ن، م، ه، ء + ال
- Derivational forms (Forms I-X)

**Example:**
```python
from src.fvafk.augmentation_operators import *

system = AugmentationSystem()
root = Root(C1='ك', C2='ت', C3='ب')
derived = system.apply_operators(root, [system.operators[2]])
```

### 7. Particle Loader (`particle_loader.py`)

Loads Arabic particles from CSV files for integration with node schema.

**Key Features:**
- Loads prepositions (حروف الجر), conjunctions (حروف العطف), interrogatives, etc.
- Supports operators_catalog_split.csv when available
- Creates Node instances from particle data
- Comprehensive particle metadata

**Example:**
```python
from src.fvafk.particle_loader import ParticleLoader

loader = ParticleLoader()
loader.load_all()

# Get all prepositions
prepositions = loader.get_prepositions()

# Get specific particle
bi = loader.get_particle("بِ")

# Create node from particle
node = loader.create_node_from_particle(bi)
```

## Mathematical Foundations

### Vowel Space

```
𝓕_V = [0,1] × [0,1] × {0,1}    # (height, backness, rounding)

d_P(v_i, v_j) = √((h_i - h_j)² + (b_i - b_j)² + κ(r_i - r_j)²)

c_A(v) = (h - 0.5)² + (b - 0.5)² + ρ·r

J_λ(S) = -D(S) + λ·C(S)
```

### Sufficient Conditions

**Collapse Prevention:**
```
λ < D_tri / C_tri
```

**Rounding Attachment to /u/:**
```
ε < ρ < √κ
d_P(a, u) - d_P(a, u_unrounded) > λ·ρ
```

### Theorem

If conditions hold, then optimal 3-vowel system is:
- Low unrounded (a)
- High front unrounded (i)
- High back rounded (u)

## Tests

```bash
# Run all tests (43 tests, all passing)
pytest tests/test_vowel_space_optimization.py tests/test_node_schema_energy.py tests/test_particle_loader.py -v
```

Test coverage:
- Vowel space optimization: 20 tests
- Node schema and energy: 13 tests
- Particle loader: 10 tests

## Documentation

See `docs/VOWEL_OPTIMIZATION_FRAMEWORK.md` for comprehensive documentation including:
- Mathematical foundations
- Usage examples for all modules
- Theorem statement and proof sketch
- References to linguistic theory

## Architecture

```
src/fvafk/
├── vowel_space_optimization.py  # Phonological optimization
├── node_schema.py               # Unified node representation
├── energy_evaluation.py         # Constraint evaluation
├── generative_plurals.py        # Template generation
├── parameter_learning.py        # Weight learning
├── augmentation_operators.py    # Morphological operators
└── particle_loader.py           # Particle data loader (NEW)

tests/
├── test_vowel_space_optimization.py  # 20 tests
├── test_node_schema_energy.py        # 13 tests
└── test_particle_loader.py           # 10 tests (NEW)
└── augmentation_operators.py    # Morphological operators

tests/
├── test_vowel_space_optimization.py  # 20 tests
└── test_node_schema_energy.py        # 13 tests

examples/
└── integration_demo.py          # Complete pipeline demo

docs/
└── VOWEL_OPTIMIZATION_FRAMEWORK.md  # Full documentation
```

## Key Insights

1. **Vowel systems are optimal solutions** to optimization problems, not arbitrary lists
2. **Templates are generated** from constraints, not hardcoded patterns
3. **Hard constraints use infinity gates** for clean filtering
4. **Inflected and built-in words** share the same representation
5. **C_2 is the economy center** due to symmetry and transition impact
6. **Parameter learning preserves function form** - only weights change

## Theory Background

This framework synthesizes:
- **Dispersion Theory** (Liljencrants & Lindblom, 1972)
- **Feature Geometry** (Clements, 1985)
- **Optimality Theory** (Prince & Smolensky, 1993)
- **Structured Prediction** (Taskar et al., 2004)
- **Arabic Morphology** (McCarthy, 1981)

## Citation

```bibtex
@software{vowel_optimization_framework,
  title = {Vowel Space Optimization and Morphological Framework for Arabic},
  year = {2026},
  url = {https://github.com/sonaiso/Eqratech_Hussein_Hiyassat_Project}
}
```

## License

Part of the Eqratech Hussein Hiyassat Project.
