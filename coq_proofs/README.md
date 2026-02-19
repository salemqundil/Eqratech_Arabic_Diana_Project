# Coq Proofs: Argmin-Based Arabic NLP System

## Overview

This directory contains a **complete Coq formalization** of the argmin-based energy minimization framework for Arabic linguistic analysis. The development proves existence, termination, soundness, and uniqueness (up to equivalence) of optimal analyses.

## Architecture

The system is built on the core paradigm:
```
x → y₀ → G(x) → argmin E(x,·) → y*
```

Where:
- `x` : Valid input (tokens + maqam features)
- `y₀` : Canonical admissible candidate
- `G(x)` : Finite candidate generator  
- `E(x,y)` : Energy function (hard gates + soft penalties)
- `y*` : Optimal analysis (minimizer)

## File Structure

### Core Modules (Dependency Order)

1. **Assumptions.v** - Mathematical/physical axioms ONLY
   - Feature space finiteness
   - Distance properties  
   - Input bounds
   - Epsilon separation
   - **All axioms justified with weakest forms**

2. **CoreTypes.v** - Type definitions (axiom-free)
   - Input X, output Y
   - Tokens, features, maqam
   - Syntactic relations (ISN/TADMN/TAQYID)
   - Equivalence relation

3. **Energy.v** - Cost function
   - Cost type (Finite n | Infinite)
   - Hard gates (CV, Sig, Join, Scope, Maqam)
   - Soft penalties (complexity, relations)
   - Total energy E(x,y)

4. **Generator.v** - Candidate generation
   - G(x) produces finite list
   - Proves finiteness and boundedness
   - Base candidate construction

5. **Canonical.v** - y₀ constructor
   - **Theorem**: y₀ is admissible (E(x,y₀) ≠ ∞)
   - **Theorem**: Non-emptiness of admissible set

6. **Minimizer.v** - Argmin implementation
   - Argmin on finite lists
   - **Theorem**: Minimizer existence for valid inputs
   - Proves minimality properties

7. **SyntaxGates.v** - ISN/TADMN/TAQYID separation
   - Epsilon-separation between relations
   - **Theorem**: Argmin chooses correct structure

8. **Maqam.v** - Style features
   - Maqam feature space FM
   - Style gates (interrogative, imperative, etc.)
   - **Theorems**: Style-specific structures

9. **Theorems.v** - Main results
   - **10 numbered theorems** (proven constructively)
   - Existence, Termination, Soundness, Uniqueness
   - Closure properties for all styles

## Building

### Prerequisites
```bash
# Install Coq (version 8.15 or later)
sudo apt-get install coq
# Or via opam:
opam install coq
```

### Compile All Files
```bash
cd coq_proofs
make all
```

This will:
1. Compile all `.v` files in dependency order
2. Run verification checks
3. Report any axioms outside Assumptions.v

### Individual Compilation
```bash
coqc -R . ArgminArabic Assumptions.v
coqc -R . ArgminArabic CoreTypes.v
# ... etc
```

### Verification
```bash
make verify
```

Checks:
- ✓ No `Axiom`/`Admitted`/`Parameter` outside Assumptions.v
- ✓ All theorems end with `Qed.`
- ✓ Successful compilation

### Clean Build Artifacts
```bash
make clean
```

## Theorem Summary

### Fundamental Theorems (Constructive Proofs)

**Theorem 1**: Feature space FM is well-defined and non-empty

**Theorem 2**: For all valid x, ∃ admissible y ∈ G(x) with E(x,y) < ∞

**Theorem 3**: For all valid x, argmin terminates (returns Some y*)

**Theorem 4**: Minimizer y* satisfies all hard gates (soundness)

**Theorem 5**: Minimizers are unique up to equivalence

**Theorem 6**: Nominal sentences (ISN) via argmin

**Theorem 7**: Verbal sentences (ISN) via argmin

**Theorem 8**: Interrogative polar structures

**Theorem 9**: Imperative structures

**Theorem 10**: Declarative structures

### Proof Strategy

All proofs are **constructive** (no classical logic):
- Use `nat` instead of `real` for costs
- Finite candidate lists (not infinite domains)
- Decidable predicates only
- No `Axiom` beyond Assumptions.v

## Key Properties Proven

### Existence
- **y₀ exists** for all valid inputs
- **Admissible set is non-empty**

### Termination
- **G(x) is finite** (explicit list)
- **argmin always returns** Some y*

### Soundness  
- **y* satisfies all hard gates** (no ∞ cost)
- **Structural constraints verified**

### Uniqueness
- **Up to equivalence relation** `eqv`
- **Epsilon-separation** between distinct structures

## Verification Contract

See `VerificationChecklist.md` for detailed checks.

### Zero-Hallucination Guarantee

Every axiom in `Assumptions.v` has:
- Justification (physical/mathematical grounding)
- Weakest form specification
- Clear necessity for proofs

No hidden assumptions allowed.

## Extending the System

### Adding a New Style Gate

1. Define gate in `Maqam.v`:
   ```coq
   Definition gate_my_style (m : FM) (g : AnalysisGraph) : bool := ...
   ```

2. Add to energy in `Energy.v`:
   ```coq
   gate_my_style (maqam x) (graph y)
   ```

3. Prove structure theorem in `Maqam.v`:
   ```coq
   Theorem my_style_structure : forall x,
     X_valid x ->
     my_style_condition (maqam x) = true ->
     exists y*, argmin (E x) (G x) = Some y* /\ ...
   ```

4. Add to main theorems in `Theorems.v`

### Adding New Relations

Extend `Relation` type in `CoreTypes.v` and prove epsilon-separation in `SyntaxGates.v`.

## Testing

Extract executable code:
```bash
coqc -R . ArgminArabic Extraction.v
```

(Requires separate Extraction.v with Extraction directives)

## References

- Coq Documentation: https://coq.inria.fr/documentation
- Mathematical Components: https://math-comp.github.io/
- Calculus of Variations (Direct Method): Dacorogna, 2008

## License

Same as main project (see repository root)

## Contributors

Generated by AI assistant (GitHub Copilot) as rigorous formalization of the Arabic NLP argmin framework.

---

**Status**: ✅ Complete formalization with constructive proofs
**Date**: 2026-02-03
**Coq Version**: 8.15+
