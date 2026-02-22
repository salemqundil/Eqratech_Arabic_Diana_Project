# Architecture: Bayan / FVAFK Arabic NLP Pipeline

## Overview

The FVAFK pipeline implements a **6-layer formal linguistic model** where each
layer builds on the results of the layer below it. The system uses a
mathematical optimization paradigm: given input `x`, produce output `y*` by
minimizing an energy function `E(x, y)`.

```
x → y₀ → G(x) → y* = arg min E(x, y)
```

---

## The 6-Layer Architecture

```
┌──────────────────────────────────────────────────┐
│  Layer 6: Generation   (التوليد)                 │
│  Sentence production from compositional parts    │
├──────────────────────────────────────────────────┤
│  Layer 5: Rhetoric     (البلاغة)                 │
│  Figurative language & discourse structure       │
├──────────────────────────────────────────────────┤
│  Layer 4: Syntax       (النحو)                   │
│  Grammatical relations: ISN, TADMN, TAQYID       │
├──────────────────────────────────────────────────┤
│  Layer 3: Lexicon      (المعجم)                  │
│  Vocabulary, POS, semantic classification        │
├──────────────────────────────────────────────────┤
│  Layer 2: Morphology   (الصرف)                   │
│  Roots, patterns, inflection, derivation         │
├──────────────────────────────────────────────────┤
│  Layer 1: Phonology    (الصوتيات)                │
│  Phonemes, diacritics, syllable structure        │
└──────────────────────────────────────────────────┘
```

**Dependency rule**: Lower layers provide foundations for higher layers.
A Layer-4 component may use Layer-1/2/3 results but must not import Layer-5/6.

---

## Pipeline Phases (FVAFK)

### Phase C1 — Encoding & Normalization (`src/fvafk/c1/`)

Input: raw Arabic string (with or without diacritics).

Steps:
1. Unicode NFC normalization
2. Orthographic standardization (hamza forms, alif variants)
3. Character-level encoding into typed `Unit` objects
4. CV skeleton extraction (consonant/vowel classification)

Key classes:
- `C1Encoder` — main entry point
- `FormCodecV2` — character-level codec
- `OrthographyAdapter` — handles Arabic orthographic variants

---

### Phase C2a — Phonological Gates (`src/fvafk/c2a/`)

Input: sequence of `Unit` objects from C1.

Each gate applies a Tajweed-based transformation:

| Gate | Transformation |
|------|---------------|
| `GateSukun` | Repair double sukun |
| `GateShadda` | Expand gemination |
| `GateHamza` | Place hamza correctly |
| `GateWaqf` | Apply pause rules |
| `GateIdgham` | Assimilate with ghunnah |
| `GateMadd` | Lengthen vowels |
| `GateDeletion` | Delete alif/hamza |
| `GateEpenthesis` | Insert epenthetic vowel |
| `GateWasl` | Handle hamzat al-wasl |
| `GateTanwin` | Assimilate tanwin |

Gates are composed via `GateFramework`, which applies them in sequence.
Each gate can:
- **Pass** (no change needed)
- **Repair** (apply the transformation)
- **Reject** (mark as ungrammatical — infinite cost)

---

### Phase C2b — Morphological Analysis (`src/fvafk/c2b/`)

Input: Arabic word string (diacritized).

Components:
- **`RootExtractor`** — identifies trilateral/quadrilateral root consonants
- **`PatternMatcher`** — matches word against 25+ morphological templates
- **`ArabicSyllabifier`** — segments word into CV syllables
- **`WordClassifier`** — determines POS (noun/verb/particle) and number/gender
- **`AwzanPatternLoader`** — loads morphological patterns from CSV

Root types supported: `TRILATERAL`, `QUADRILATERAL`, `DEFECTIVE`, `HOLLOW`,
`ASSIMILATED`, `DOUBLED`.

Verb forms recognized: Forms I–X (أوزان الأفعال الثلاثية والرباعية).

---

### Phase C3 — Syntactic Analysis (`src/fvafk/syntax/`)

Input: sequence of `WordForm` objects from C2b.

The ISNADI linker detects **إسنادي** (predicative) links between:
- **مبتدأ** (subject/topic) and **خبر** (predicate/comment)
- **فاعل** (agent/subject) and **فعل** (verb)

Output: list of `Link` objects with type (`ISNADI`, `TAWSIFI`, etc.)
and head/dependent indices.

---

## Phonology V2 Engine (`src/fvafk/phonology_v2/`)

The enhanced phonology engine uses a **syllable-lattice** approach with
**VC witnesses** (decision traces):

1. `text_to_graphemes()` — parse Arabic characters into typed `Grapheme` objects
2. `vc_classify()` — classify each grapheme as Vowel/Consonant using contextual rules
3. `build_syllable_lattice_v2()` — build a lattice of candidate syllabifications
4. `find_best_syllabification()` — select optimal path through the lattice
5. `analyze_word()` — high-level API combining all steps

The `PhonologyV2Adapter` wraps this into a dict-shaped output compatible with
the CLI JSON format.

---

## Engine System (`src/engines/`)

66 linguistic engines organized in a 3-level hierarchy:

```
Layer → Group → Subgroup
```

All engines inherit from `BaseReconstructionEngine` and implement `make_df()`,
which returns a pandas DataFrame with mandatory Arabic column names:

| Column | Meaning |
|--------|---------|
| `الأداة` | The linguistic item (required) |
| `الفونيمات` | Phoneme sequence (auto-filled) |
| `الحركات` | Diacritic sequence (auto-filled) |
| `Unicode` | U+XXXX codepoints (auto-generated) |
| `UTF-8` | 0xXX byte encoding (auto-generated) |

The `reconstruct_from_base_df()` utility in `reconstruction_utils.py`
normalizes every DataFrame during export.

---

## Maqam Theory (`src/maqam_theory/`)

A constraint-optimization framework for sentence construction:

```
Energy: E(x, y) = Σ hard_gates(x,y) + Σ soft_terms(x,y)
Optimal: y* = arg min_{y ∈ Y_admiss(x)} E(x, y)
```

**Hard gates** return ∞ for violations; **soft terms** return finite penalties.

The `MaqamVector` (24-dimensional float vector) encodes:
- Illocutionary force (declarative, interrogative, vocative, …)
- Interrogative type (polar/wh/alternative)
- Request type (command, prohibition, supplication, …)
- Emphasis, negation, restriction, oath, exclamation

12 gate implementations cover all major Arabic sentence modalities.
11 formal theorems are proved in `src/maqam_theory/proofs/maqam_theorems.py`.

---

## Syntax Theory (`src/syntax_theory/`)

Graph-based syntactic analysis using three core relations:

| Relation | Arabic | Meaning |
|----------|--------|---------|
| `ISN` | إسناد | Predicative relation (subject–predicate) |
| `TADMN` | تضمين | Embedding relation (phrase structure) |
| `TAQYID` | تقييد | Modification relation (adjunct) |

A `SyntacticGraph` is a directed typed graph `y = (V, E, τ, φ)` where:
- `V` = nodes (lexical items)
- `E` = edges (grammatical relations)
- `τ` = node typing function
- `φ` = edge labeling function

---

## Web Application (`web_app/`)

FastAPI application exposing the FVAFK pipeline:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness probe |
| `POST` | `/analyze` | Run FVAFK pipeline on text |
| `GET` | `/docs` | Interactive Swagger UI |

Start with:
```bash
python run_server.py --host 127.0.0.1 --port 8000
```

---

## Data Flow Summary

```
Raw Arabic Text
      │
      ▼ C1Encoder
[Unit, Unit, Unit, …]   (typed character segments)
      │
      ▼ GateFramework (10 gates)
[GateResult, …]          (phonological transformations)
      │
      ▼ RootExtractor + PatternMatcher
WordForm {root, pattern, kind, pos}
      │
      ▼ IsnadiLinker
[Link(head=i, dep=j, type=ISNADI), …]
      │
      ▼ JSON / Pydantic models
AnalysisResult {c1, c2a, c2b, syntax, stats}
```

---

## Coq Formal Proofs

Three Coq modules verify gate semantics:
- `coq/Gates/GateSukun.v`
- `coq/Gates/GateShadda.v`
- `coq/Gates/GateTanwin.v`

Run with:
```bash
coqc coq/Gates/GateSukun.v
```

---

## Key Design Principles

1. **Layer isolation** — each layer imports only from lower layers.
2. **Energy minimization** — all output selection expressed as `arg min E`.
3. **Hard/soft gate separation** — hard constraints = ∞ cost; preferences = finite cost.
4. **No linguistic axioms** — vowel inventory and phoneme alphabet emerge from
   feature-space constraints, not hardcoded lists.
5. **Type safety** — all public APIs use Pydantic v2 models.
6. **Reproducibility** — deterministic processing; no randomness in the pipeline.
