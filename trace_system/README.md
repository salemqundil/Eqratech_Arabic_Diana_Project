# Trace System - Arabic NLP Decision Tracing Framework

## Overview

This directory contains the complete infrastructure for **decision trace generation** in Arabic NLP processing. The system implements a **7-layer hierarchical pipeline** with unified JSON schemas, feature enumerations, and gate definitions.

## Architecture: 7-Layer Pipeline

```
Input Text
    ↓
[1] Phonology      → Extract phonemes + features
    ↓
[2] Syllable       → Segment into CV patterns + weight
    ↓
[3] Morphology     → Root extraction + pattern gates
    ↓
[4] Syntax         → Dependency structure + operator scope
    ↓
[5] I'rab/Binā'    → Case/mood assignment + locking
    ↓
[6] Semantics      → Sense selection + predicate classification
    ↓
[7] Pragmatics     → Context inference + epistemic gate
    ↓
Final Judgment J(subject, predicate, constraints, scope)
```

## File Structure

### 1. `feature_enums.json`
**Canonical feature dictionary** with stable IDs for:
- Consonant features (place, manner, voicing, emphasis, root role)
- Vowel features (length, height, backness, diacritics)
- Syllable types + weights
- Morphological features (word class, derivation, tense, mood, case)
- Ma'ani tools (operators: negation, condition, exception...)
- Semantic categories (predicate types, truth modes)

**Usage**: Import feature IDs for Neo4j vector indexing, PostgreSQL constraints, validation.

**Example**:
```json
{
  "ConsonantFeatures": {
    "place": {
      "enum": ["BILABIAL", "ALVEOLAR", ...],
      "ids": {
        "BILABIAL": "CF_PL_001",
        "ALVEOLAR": "CF_PL_004",
        ...
      }
    }
  }
}
```

### 2. `trace_schema.json`
**JSON Schema validation** for complete decision traces:
- Input structure (text, tokens, span)
- Context (register, domain, speaker)
- State (scope, sense, constraints)
- Layers (7 layer templates)
- Judgment (J + epistemic decision)
- Audit (soundness, completeness, traceability)

**Usage**: Validate trace JSON before insertion, generate TypeScript/Python types.

### 3. `example_traces.json`
**Complete worked example**: "من يكذب يعاقب" (whoever lies gets punished)

Demonstrates:
- All 7 layers with full payloads
- Feature ID references throughout
- Scope tracking (condition operator)
- Sense selection (world vs otherworld punishment)
- Epistemic gate decision (world-verifiable claim)

**Usage**: Reference implementation, testing gold standard, documentation.

### 4. `gates_schema.json`
**Gate definitions** for 4 core computational gates:

#### SyllabifyGate
- **Input**: Phoneme stream
- **Output**: Syllabification + transitions + weight
- **Rules**: T-01 to T-06 (CV patterns, weight assignment, transition balance)

#### ScopeGate
- **Input**: Syntax parse + current scope
- **Output**: Updated scope + scope_delta
- **Rules**: Negation, condition, exception, restriction scope rules

#### SenseSelectionGate
- **Input**: Candidates + context + constraints
- **Output**: Selected sense + confidence
- **Rules**: Scoring, context filtering, constraint checking, ambiguity detection

#### EpistemicGate
- **Input**: J (subject, predicate, constraints, scope) + selected sense
- **Output**: Predicate type + truth mode + world_verifiable + needs_hearing
- **Decision table**: Maps predicate types → truth evaluation modes

**Usage**: Implement gate logic, validate gate I/O, generate gate tests.

## Integration Points

### PostgreSQL Storage
```sql
CREATE TABLE feature_enums (
    feature_id TEXT PRIMARY KEY,
    category TEXT NOT NULL,  -- 'consonant', 'vowel', 'syllable', 'morph', 'semantic'
    subcategory TEXT,         -- 'place', 'manner', 'word_class', etc.
    value TEXT NOT NULL,      -- 'BILABIAL', 'VERB', 'JUSSIVE'
    description TEXT
);

CREATE TABLE decision_traces (
    trace_id TEXT PRIMARY KEY,
    input_text TEXT NOT NULL,
    trace_json JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT valid_trace CHECK (jsonb_matches_schema(trace_json, 'trace_schema.json'))
);
```

### Neo4j Graph Structure
```cypher
// Feature nodes with stable IDs
CREATE (f:Feature {id: 'CF_PL_001', category: 'consonant', subcategory: 'place', value: 'BILABIAL'})

// Trace nodes linking to features
CREATE (t:Trace {trace_id: 'DT-000001', input: 'من يكذب يعاقب'})
CREATE (layer:Layer {layer: 'phonology', step: 1})
CREATE (phoneme:Phoneme {token_id: 0, sym: 'm'})
CREATE (phoneme)-[:HAS_FEATURE]->(f)
CREATE (layer)-[:CONTAINS]->(phoneme)
CREATE (t)-[:HAS_LAYER]->(layer)
```

### Python Usage
```python
import json
from jsonschema import validate

# Load schemas
with open('trace_schema.json') as f:
    schema = json.load(f)
with open('feature_enums.json') as f:
    features = json.load(f)

# Generate trace
trace = {
    "trace_id": "DT-000002",
    "input": {"text": "لم يكتب", "tokens": [...]},
    # ... populate layers
}

# Validate
validate(instance=trace, schema=schema)

# Get feature ID
place_id = features['ConsonantFeatures']['place']['ids']['ALVEOLAR']
# → "CF_PL_004"
```

## Example Workflow: Processing New Sentence

```python
# 1. Input
text = "لم يكتب"

# 2. Phonology Layer
phonemes = phonology_engine.extract(text)
# → [{"type": "C", "sym": "l", "features": ["CF_PL_004", "CF_MN_005", ...]}, ...]

# 3. Syllable Layer
syllables = syllabify_gate.apply(phonemes)
# → {"syllabification": [...], "transitions": [...], "status": "ok"}

# 4. Morphology Layer
morphs = morphology_engine.analyze(syllables)
# → {"word_class": "VERB", "word_class_id": "MF_WC_002", "root": {"radicals": ["ك","ت","ب"], ...}}

# 5. Syntax Layer
parse = syntax_engine.parse(morphs)
scope_result = scope_gate.apply(parse, current_scope)
# → {"updated_scope": {"operators": ["NEGATE"], ...}, "scope_delta": [...]}

# 6. I'rab Layer
i3rab = i3rab_engine.assign(parse, morphs)
# → {"mode": "MU3RAB", "mode_id": "IF_MD_001", "mood": "JUSSIVE", ...}

# 7. Semantics Layer
J = semantics_engine.construct_J(parse, i3rab, morphs)
sense_result = sense_selection_gate.apply(J.predicate_candidates, context, constraints)
# → {"selected": "WRITE_ACTION", "confidence": 0.92, ...}

# 8. Pragmatics Layer
epistemic_result = epistemic_gate.apply(J, sense_result.selected)
# → {"predicate_type": "SENSIBLE_WORLD_CLAIM", "truth_mode": "WORLD_VERIFICATION", ...}

# 9. Assemble Trace
trace = assemble_trace(text, [phonemes, syllables, morphs, parse, i3rab, J, epistemic_result])

# 10. Validate & Store
validate(trace, trace_schema)
db.store_trace(trace)
```

## Testing Strategy

### Unit Tests (Per Gate)
```python
def test_syllabify_gate_cv():
    input_phonemes = [{"type": "C", "sym": "m"}, {"type": "V", "sym": "a"}]
    result = syllabify_gate.apply({"phoneme_stream": [{"token_id": 0, "phonemes": input_phonemes}]})
    assert result['syllabification'][0]['syllables'][0]['type'] == 'CV'
    assert result['syllabification'][0]['syllables'][0]['weight'] == 'LIGHT'
    assert result['status'] == 'ok'
```

### Integration Tests (Full Pipeline)
```python
def test_full_pipeline_conditional():
    text = "من يكذب يعاقب"
    trace = run_full_pipeline(text)
    
    # Check layers
    assert len(trace['layers']) == 7
    assert trace['layers'][3]['layer'] == 'syntax'
    
    # Check scope
    assert 'IF_THEN' in trace['state']['scope']['operators']
    
    # Check epistemic
    assert trace['judgment']['epistemic']['predicate_type'] == 'SENSIBLE_WORLD_CLAIM'
    assert trace['judgment']['epistemic']['world_verifiable'] == True
```

### Gold Standard Validation
```bash
# Compare against example_traces.json
python validate_traces.py --gold example_traces.json --test output_traces.json
```

## Next Steps (Implementation Checklist)

- [ ] Implement `SyllabifyGate` class with T-01 to T-06 rules
- [ ] Implement `ScopeGate` with operator stack management
- [ ] Implement `SenseSelectionGate` with context-aware scoring
- [ ] Implement `EpistemicGate` with decision table logic
- [ ] Create PostgreSQL migration for `feature_enums` table
- [ ] Create Neo4j schema constraints for feature nodes
- [ ] Generate Python dataclasses from `trace_schema.json`
- [ ] Generate TypeScript types for frontend integration
- [ ] Build trace validation pipeline
- [ ] Create trace visualization dashboard (Neo4j Browser + custom UI)

## References

- **Theoretical Foundation**: `.github/copilot-instructions.md` (6-layer computational linguistics model)
- **Evidence-Based Development**: `.github/COPILOT_UPDATE_EVIDENCE.md`
- **Engine Taxonomy**: `ENGINE_TAXONOMY.md` (66 engines, hierarchical organization)

---

**Version**: 1.0.0  
**Last Updated**: 2026-02-04  
**Status**: ✅ Ready for implementation
