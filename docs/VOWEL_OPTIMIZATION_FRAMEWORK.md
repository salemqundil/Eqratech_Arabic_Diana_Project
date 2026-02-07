# Vowel Space Optimization and Morphological Framework

This document describes the comprehensive linguistic/phonological framework for Arabic morphology and phonology implemented in this project.

## Table of Contents

1. [Overview](#overview)
2. [Vowel Space Optimization](#vowel-space-optimization)
3. [Unified Node Schema](#unified-node-schema)
4. [Energy-Based Evaluation](#energy-based-evaluation)
5. [Generative Plural Templates](#generative-plural-templates)
6. [Parameter Learning](#parameter-learning)
7. [Augmentation Operators](#augmentation-operators)
8. [Usage Examples](#usage-examples)

---

## Overview

This framework implements a rigorous mathematical approach to Arabic phonology and morphology based on optimization principles. The key innovations are:

1. **Vowel Space Optimization**: Mathematical conditions on parameters (λ, κ, ρ) that ensure optimal vowel systems
2. **Unified Node Schema**: A single representation for both inflected (معرب) and built-in (مبني) words
3. **Energy Functions**: Hard constraints via "infinity gates" that filter invalid structures
4. **Generative Templates**: Plural and other morphological patterns generated from constraints, not lists
5. **Structured Learning**: Parameter learning without changing function form
6. **Operator-Based Augmentation**: Augmentation letters as insertion operators with position-specific costs

---

## Vowel Space Optimization

### Mathematical Model

The vowel space is defined as:

```
𝓕_V = [0,1] × [0,1] × {0,1}    where (h, b, r) = (height, backness, rounding)
```

### Perceptual Distance

```
d_P(v_i, v_j) = √((h_i - h_j)² + (b_i - b_j)² + κ(r_i - r_j)²)
```

where κ is the perceptual weight for the rounding dimension.

### Articulation Cost

```
c_A(v) = (h - 0.5)² + (b - 0.5)² + ρ·r
```

where ρ is the cost of rounding, and (0.5, 0.5) is the comfortable articulation center.

### Optimization Criterion

For a set S of vowels:

```
J_λ(S) = -D(S) + λ·C(S)

where:
  D(S) = min_{i≠j} d_P(v_i, v_j)    (minimum dispersion)
  C(S) = Σ c_A(v_i)                  (total cost)
```

### Sufficient Conditions

#### 1. Collapse Prevention

To prevent collapse to the center:

```
λ < D_tri / C_tri
```

where D_tri and C_tri are the dispersion and cost of the {a, i, u} system.

#### 2. Rounding Attachment to High Back Vowel

To ensure rounding attaches to /u/ and not /i/:

```
ε < ρ < √κ                          (useful but costly)
d_P(a, u) - d_P(a, u_unrounded) > λ·ρ    (back rounding increases dispersion enough)
d_P(a, i_rounded) - d_P(a, i) < λ·ρ       (front rounding doesn't pay for itself)
```

### Usage

```python
from src.fvafk.vowel_space_optimization import (
    OptimizationParameters, VowelSpaceOptimizer
)

# Create optimizer with parameters
params = OptimizationParameters(lambda_=0.3, kappa=1.0, rho=0.5)
optimizer = VowelSpaceOptimizer(params)

# Verify the {a, i, u} system is optimal
report = optimizer.verify_optimal_system()

print(f"Optimal: {report['optimal']}")
print(f"Dispersion: {report['dispersion']:.4f}")
print(f"Cost: {report['cost']:.4f}")
```

---

## Unified Node Schema

### Node Structure

Every linguistic element (consonant, vowel, word, clitic) is represented as a Node:

```python
@dataclass
class Node:
    id: str                    # Unique identifier
    type: NodeType            # C, V, FUNC, MABNI, NOUN, VERB, etc.
    anchor: Anchor            # Position information
    sig: Signature            # Attachment requirements
    case_mood: CaseMood       # Case/mood with locking status
    join: Join                # Attachment policy
    roles: Roles              # Semantic and syntactic roles
    surface: str              # Surface form
    features: dict            # Additional features
```

### Key Distinctions

#### Inflected (معرب) vs Built-in (مبني)

- **Inflected**: `case_mood.locked = False`, case/mood varies with context
- **Built-in**: `case_mood.locked = True`, case/mood is fixed

#### Attachment Policies

```python
class JoinPolicy(Enum):
    MUST = "must_attach"      # Clitics (ضمائر متصلة)
    PREFER = "prefer_attach"  # Prepositions
    FREE = "free"             # Independent words
    FORBID = "forbid_attach"  # Words that cannot attach
```

### Usage

```python
from src.fvafk.node_schema import (
    create_preposition, create_noun, create_attached_pronoun
)

# Create "في بيتِهِ" (in his house)
prep = create_preposition("prep1", "في", Case.GEN)
noun = create_noun("noun1", "بيت", Case.GEN)
pron = create_attached_pronoun("pron1", "ه")
pron.join.value = 1  # Mark as attached
```

---

## Energy-Based Evaluation

### Energy Components

```python
@dataclass
class EnergyComponents:
    E_attach: float   # Attachment requirement violations
    E_case: float     # Case mismatch
    E_join: float     # Join policy violations
    E_dist: float     # Distance/economy (phonology)
    E_morph: float    # Morphological constraints
```

### Infinity Gates

Hard constraints are enforced by returning `∞` energy:

- **E_attach = ∞**: Required attachment not satisfied
- **E_case = ∞**: Case mismatch (e.g., preposition + nominative)
- **E_join = ∞**: Join policy violated (e.g., clitic not attached)

### Example: "في بيتِهِ"

Three candidates:

1. **CORRECT**: `في + بيتِ(GEN) + ـهِ(attached)`
   - E_total = 0.0 (all constraints satisfied)

2. **WRONG**: `في + بيتُ(NOM) + ـهِ(attached)`
   - E_case = ∞ (preposition requires genitive)

3. **WRONG**: `في + بيتِ(GEN) + هو(separate)`
   - E_join = ∞ (clitic must attach)

### Usage

```python
from src.fvafk.energy_evaluation import EnergyEvaluator, Candidate

evaluator = EnergyEvaluator()
candidate = Candidate([prep, noun, pron], "description")
energies, status = evaluator.evaluate_candidate(candidate)

if status == CandidateStatus.VALID:
    print(f"Valid with energy: {energies.total()}")
else:
    print("Invalid (infinity energy)")
```

---

## Generative Plural Templates

### Generative Approach

Instead of listing plural patterns manually, we **generate** them from:

1. **Syllable constraints**: CV, CVC, CVV, CVVC patterns
2. **Economy constraints**: Minimize transitions, avoid OCP violations
3. **Morphological features**: Plural marking requirement

### Template Generation

```
G_pl(root) = AllTemplates(root, target=plural, under E_syll + E_economy)
```

Then select optimal:

```
F(x) = argmin_{y ∈ G_pl(x)} E(y; x)
```

### Common Patterns Generated

- **فُعُول** (fu3uul): C1-u-C2-uu-C3
- **فِعَال** (fi3aal): C1-i-C2-aa-C3
- **أَفْعَال** (af3aal): a-C1-C2-aa-C3
- **فُعَلَاء** (fu3alaa'): C1-u-C2-a-C3-aa-'

### Usage

```python
from src.fvafk.generative_plurals import TemplateGenerator

generator = TemplateGenerator()
root = ('ك', 'ت', 'ب')  # k-t-b "write"

# Generate plural templates
templates = generator.generate_plural_templates(root, target_feature="plural")

for template in templates:
    surface = generator.apply_template(template, root)
    cost = generator.compute_economy_cost(template)
    print(f"{template.name}: {surface} (cost: {cost:.2f})")
```

---

## Parameter Learning

### Fixed Function Form

The function form is **never changed**:

```
F_w(x) = argmin_{y ∈ G(x)} Σ_i w_i φ_i(y; x)
```

Only the weights **w** are learned from data.

### Structured Learning

Minimize:

```
L(w) = Σ_j loss(F_w(x_j), y_j) + μ||w||²
```

where:
- `loss(·)` is structured loss (e.g., 0-1, Hamming, edit distance)
- `μ` is regularization parameter (prevents overfitting)

### Usage

```python
from src.fvafk.parameter_learning import (
    StructuredLearner, FeatureFunction, TrainingExample
)

# Define features
features = [
    FeatureFunction("length", lambda y, x: len(y)),
    FeatureFunction("vowels", lambda y, x: sum(1 for c in y if c in 'aiu')),
]

# Create learner
learner = StructuredLearner(features, mu=0.01, learning_rate=0.1)

# Train
training_data = [
    TrainingExample(x="ktb", y_gold="kutub"),
    TrainingExample(x="qlm", y_gold="aqlaam"),
]

learner.train(training_data, candidate_generator, epochs=10)

# Get learned weights
weights = learner.get_weights()
```

---

## Augmentation Operators

### Augmentation as Operators

Augmentation letters (س، ل، ت، ن، م، ه، ء + ال) are **insertion operators**:

```python
OP_ins(position, feature_goal, segment)
```

### Positions

- **PRE**: Prefix (before root)
- **IN1**: After C1
- **IN2**: After C2 (economy center)
- **IN3**: After C3
- **POST**: Suffix (after root)

### Why C_2 is the Economy Center

1. **Symmetry**: Equidistant from C1 and C3
2. **Maximum impact**: Changes affect both transitions (C1→C2 and C2→C3)
3. **Derivational patterns**: Many verb forms modify C2
4. **Lower cost**: Insertions at C2 have lower economy cost

### Standard Operators

- **أ** (prefix): Causative (Form IV)
- **ت** (prefix): Reflexive (Form V, VI)
- **Gemination on C2**: Intensive (Form II)
- **Long vowel after C2**: Reciprocal (Form III)
- **ت** (after C1): Middle voice (Form VIII)
- **ال** (prefix): Definiteness
- **ة** (suffix): Feminine

### Usage

```python
from src.fvafk.augmentation_operators import (
    AugmentationSystem, Root
)

system = AugmentationSystem()
root = Root(C1='ك', C2='ت', C3='ب')  # k-t-b "write"

# Apply operators
operators = [system.operators[2]]  # Gemination on C2
derived = system.apply_operators(root, operators)

print(f"Surface: {derived.surface}")
print(f"Cost: {system.compute_total_cost(operators)}")
```

---

## Usage Examples

### Complete Example: Analyze "في بيتِهِ"

```python
from src.fvafk.node_schema import *
from src.fvafk.energy_evaluation import *

# Create nodes
prep = create_preposition("prep1", "في", Case.GEN)
noun = create_noun("noun1", "بيت", Case.GEN)
pron = create_attached_pronoun("pron1", "ه")
pron.join.value = 1

# Create candidate
candidate = Candidate([prep, noun, pron], "في بيتِهِ")

# Evaluate
evaluator = EnergyEvaluator()
energies, status = evaluator.evaluate_candidate(candidate)

print(f"Status: {status.value}")
print(f"Total energy: {energies.total()}")
```

### Run All Demonstrations

```bash
# Vowel space optimization
python src/fvafk/vowel_space_optimization.py

# Node schema
python src/fvafk/node_schema.py

# Energy evaluation with example
python src/fvafk/energy_evaluation.py

# Generative plurals
python src/fvafk/generative_plurals.py

# Parameter learning
python src/fvafk/parameter_learning.py

# Augmentation operators
python src/fvafk/augmentation_operators.py
```

### Run Tests

```bash
# All tests
pytest tests/test_vowel_space_optimization.py tests/test_node_schema_energy.py -v

# Specific test
pytest tests/test_vowel_space_optimization.py::TestVowelSpaceOptimizer -v
```

---

## Mathematical Foundations

### Theorem: {a, i, u} is Optimal

**Theorem**: If parameters satisfy:
1. λ < D_tri / C_tri (collapse prevention)
2. ε < ρ < √κ (rounding is useful but costly)
3. Rounding back increases dispersion more than cost

Then any optimal solution S* for 3 vowels has the structure:
- Low unrounded vowel (a)
- High front unrounded vowel (i)
- High back rounded vowel (u)

### Proof Sketch

1. Collapse prevention ensures points don't cluster at center
2. Rounding conditions ensure one rounded vowel is used
3. Dispersion maximization places vowels at corners
4. Cost minimization prefers rounding on back (already distant in b dimension)

---

## References

This implementation is based on the theoretical framework described in the problem statement, which draws on:

- Dispersion theory (Liljencrants & Lindblom, 1972)
- Feature geometry (Clements, 1985)
- Optimality Theory (Prince & Smolensky, 1993)
- Structured prediction (Taskar et al., 2004)
- Arabic morphology (McCarthy, 1981)

---

## License

This project is part of the Eqratech Hussein Hiyassat Project.
