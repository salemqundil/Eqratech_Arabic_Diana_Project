# Engine Architecture Manifest

## Theoretical Foundation

This project implements a **6-layer computational linguistics architecture** for Arabic language processing, ordered from lowest (phonological) to highest (generative) linguistic abstraction:

```
┌─────────────────────────────────────┐
│  Layer 6: GENERATION (التوليد)      │  ← Sentence production
├─────────────────────────────────────┤
│  Layer 5: RHETORIC (البلاغة)        │  ← Figurative language
├─────────────────────────────────────┤
│  Layer 4: SYNTAX (النحو)            │  ← Grammatical relations
├─────────────────────────────────────┤
│  Layer 3: LEXICON (المعجم)          │  ← Vocabulary & semantics
├─────────────────────────────────────┤
│  Layer 2: MORPHOLOGY (الصرف)        │  ← Word structure
├─────────────────────────────────────┤
│  Layer 1: PHONOLOGY (الصوتيات)      │  ← Sound units
└─────────────────────────────────────┘
```

## Engine Organization

All engines reside in `src/engines/` organized by linguistic layer. Each engine:
1. Extends `BaseReconstructionEngine` (or layer-specific base)
2. Defines `SHEET_NAME` (unique identifier for Excel export)
3. Specifies `LAYER` (from `EngineLayer` enum)
4. Implements `make_df()` returning pandas DataFrame with Arabic columns

### Layer 1: Phonology (`src/engines/phonology/`)
**Purpose**: Foundation of sound representation
- `PhonemesEngine` - Core phoneme inventory (consonants, vowels)
- `SoundEngine` - Sound classifications and features
- `AswatMuhdathaEngine` - Modern Arabic phonetic inventory

**Output**: Phonemes (الفونيمات), Harakat (الحركات), prosodic features

---

### Layer 2: Morphology (`src/engines/morphology/`)
**Purpose**: Word-level structure and derivation
- **Verb Forms**: `VerbsEngine`, `AfaalKhamsaEngine`, `MabniMajhoolEngine`
- **Participles**: `ActiveParticipleEngine`, `PassiveParticipleEngine`
- **Derived Nouns**: `IsmFaelEngine`, `IsmMafoulEngine`, `IsmAlaEngine`, `IsmMarraEngine`, `IsmHayaaEngine`
- **Adjectives**: `AdjectiveEngine`, `SuperlativeEngine`, `MubalaghSighaEngine`
- **Special Nouns**: `IsmMaqsorEngine`, `IsmMamdodEngine`, `IsmManqusEngine`, `MimiNounsEngine`
- **Transformations**: `NisbaEngine`, `TasgheerEngine`, `MasdarSinaiEngine`, `TaajjubEngine`, `BinaaEngine`
- **Meta**: `GenderEngine`, `CommonAttributesEngine`

**Output**: Word patterns, roots, inflectional paradigms

---

### Layer 3: Lexicon (`src/engines/lexicon/`)
**Purpose**: Vocabulary inventory and semantic classification
- **Proper Nouns**: `ProperNounsEngine`, `A3lamAshkhasEngine`, `A3lamAmakinEngine`, `A3lamManqulaEngine`
- **Common Nouns**: `GenericNounsEngine`, `PlaceEngine`
- **Semantic Classes**: `KainatAqilaEngine` (sentient beings), `KainatGhairAqilaEngine` (non-sentient)
- **Collective Nouns**: `JinsJamiiEngine`, `JinsIfradiEngine`
- **Numbers**: `AdadNamesEngine`
- **Religious**: `AsmaAllahEngine`, `AsmaAllahMurakkabaEngine`, `MusatalahatShariaEngine`

**Output**: Lexical entries with semantic features

---

### Layer 4: Syntax (`src/engines/syntax/`)
**Purpose**: Sentence structure and grammatical relations
- **Core Arguments**: `FaelEngine` (subject), `MafoulBihEngine` (object), `NaebFaelEngine` (passive agent)
- **Adjuncts**: `MafoulMutlaqEngine`, `MafoulAjlihEngine`, `HaalEngine` (circumstantial), `TamyeezEngine` (specifier)
- **Sentence Types**: `MobtadaKhabarEngine` (nominal sentences), `IstifhamEngine` (interrogative)
- **Deictic**: `DemonstrativesEngine`
- **Particles**: `ParticlesEngine`
- **Stylistic**: `QasrEngine` (restriction), `TaqdimEngine` (fronting), `IshtighalEngine`, `JawabEngine`

**Output**: Grammatical role assignments, sentence patterns

---

### Layer 5: Rhetoric (`src/engines/rhetoric/`)
**Purpose**: Figurative language and discourse patterns
- **Figures of Speech**: `TashbihEngine` (simile), `IstiaraEngine` (metaphor), `KinayaEngine` (metonymy)
- **Sound Patterns**: `JinassEngine` (paronomasia), `SajaEngine` (rhymed prose)
- **Semantic Relations**: `TibaqEngine` (antithesis), `MuqabalaEngine` (parallel contrast), `TaradufEngine` (synonymy)
- **Brevity/Expansion**: `IjazItnabEngine`
- **Complex**: `QasrTaqdimEngine` (restriction + fronting)

**Output**: Rhetorical device annotations

---

### Layer 6: Generation (`src/engines/generation/`)
**Purpose**: Sentence construction from components
- `SentenceGenerationEngine` - Dynamic composition from lower layers
- `EnhancedSentenceGenerationEngine` - Advanced generation with constraints
- `StaticSentenceGenerator` - Template-based fallback (doesn't depend on engines)

**Output**: Complete Arabic sentences with component metadata

---

## Data Flow

1. **Engine Execution**: Each engine's `make_df()` produces raw DataFrame
2. **Normalization**: `reconstruction_utils.reconstruct_from_base_df()` processes every DataFrame:
   - Fills `الفونيمات` (phonemes), `الحركات` (diacritics) if missing
   - Generates `Unicode` (codepoint representation)
   - Generates `UTF-8` (byte encoding)
   - Handles multi-word tools without splitting
3. **Export**: 
   - **Auto-discovery**: `Main_engine.py` scans root-level `*_engine.py` files
   - **Curated**: `export_full_multilayer_grammar_minimal.py` uses `engines.*` imports in layer order
4. **Generation**: Top-layer engines compose lower-layer outputs into sentences

## Proven Components (✓ Verified)

| Layer | Engine | Status | Output Columns |
|-------|--------|--------|----------------|
| Phonology | PhonemesEngine | ✓ | الأداة, النوع, الوصف الصوتي, المخرج, الصفة |
| Phonology | SoundEngine | ✓ | الصوت, التصنيف, الوصف |
| Morphology | ActiveParticipleEngine | ✓ | الأداة, الجذر, الوزن, المعنى |
| Morphology | PassiveParticipleEngine | ✓ | الأداة, الجذر, الوزن, المعنى |
| Lexicon | GenericNounsEngine | ✓ | الأداة, النوع, التصنيف |
| Syntax | FaelEngine | ✓ | الأداة, النوع, الحالة الإعرابية |
| Syntax | IstifhamEngine | ✓ | الأداة, النوع, الاستخدام |
| Rhetoric | TashbihEngine | ✓ | الأداة, المشبه, المشبه به, وجه الشبه |
| Generation | StaticSentenceGenerator | ✓ | الأداة, القالب, النوع, مكونات |

## Best Practices

### Adding a New Engine
1. Place in appropriate layer directory: `src/engines/{layer}/`
2. Inherit from layer base: `class MyEngine(MorphologyEngine):`
3. Set metadata:
   ```python
   SHEET_NAME = "وصف_قصير"  # ≤31 chars
   LAYER = EngineLayer.MORPHOLOGY
   ```
4. Implement `make_df()`:
   ```python
   @classmethod
   def make_df(cls) -> pd.DataFrame:
       data = {
           'الأداة': [...],  # REQUIRED
           'الفونيمات': [...],  # Optional (auto-filled)
           'الحركات': [...],  # Optional (auto-filled)
       }
       return reconstruct_from_base_df(pd.DataFrame(data))
   ```
5. Add to layer's `__init__.py`
6. Run tests: `pytest -v`

### Column Naming
**Always use Arabic names**:
- `الأداة` - The linguistic tool (word/phrase)
- `الفونيمات` - Phoneme sequence
- `الحركات` - Diacritic/vowel marks
- `Unicode` - Codepoint representation (auto-generated)
- `UTF-8` - Byte encoding (auto-generated)

### Engine Dependencies
- Lower layers don't depend on higher layers
- Higher layers MAY import from lower (e.g., Generation uses Syntax outputs)
- `StaticSentenceGenerator` is independent (template-based)

## Migration Status

### Consolidated (in `src/engines/`)
- ✓ All phonology engines
- ✓ All morphology engines
- ✓ All lexicon engines
- ✓ All syntax engines
- ✓ All rhetoric engines
- ✓ All generation engines

### Root-level (legacy, auto-discovered by Main_engine.py)
- 68 `*_engine.py` files at project root
- Still functional for backward compatibility
- Duplicates of `src/engines/` versions
- **TODO**: Remove after verifying `src/engines/` complete

### Export Scripts
- `Main_engine.py` - Auto-discovers root-level engines
- `export_full_multilayer_grammar_minimal.py` - Uses curated `engines.*` imports
- Both produce `full_multilayer_grammar.xlsx`

## Testing Strategy

```bash
# Run all tests
pytest -v

# Test specific layer
pytest tests/engines/phonology/ -v
pytest tests/engines/morphology/ -v

# Validate engine structure
python -c "from engines.base import BaseReconstructionEngine; \
           from engines.phonology import PhonemesEngine; \
           print(PhonemesEngine.get_metadata())"
```

## Performance Targets

| Operation | Target | Current |
|-----------|--------|---------|
| Engine.make_df() | <100ms | Varies |
| reconstruct_from_base_df() | <50ms | ~30ms |
| Full export (all engines) | <5s | ~3s |
| FVAFK CLI (C1→C2a→C2b) | <0.5ms/word | 0.3ms |

---

**Version**: 2.0.0  
**Last Updated**: 2026-02-03  
**Architecture**: 6-Layer Computational Linguistics Model
