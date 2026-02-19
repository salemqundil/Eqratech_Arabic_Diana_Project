# Task 2.3.1: Gate Invariants with Hypothesis

**Sprint 2, Part 2.3**  
**Status:** Starting...

---

## 🎯 Goal

Use property-based testing (Hypothesis) to verify that all phonological gates maintain critical invariants.

---

## 📋 Invariants to Test

### 1. **Non-Empty Output** (Critical)
- Gates should never produce empty output
- If input has units, output must have units
- Even REJECT status should return original input

### 2. **Consonant Order Preservation** (Critical)
- Relative order of consonants must be preserved
- Example: ك-ت-ب → must stay ك-ت-ب (not ت-ك-ب)
- Even with repairs, consonant sequence is stable

### 3. **No CCC Sequences** (Arabic Phonology Law)
- Arabic does not allow three consonants in a row
- Gates should not introduce CCC violations
- Example: INVALID: كتبْصْرْ (three sukuns)

### 4. **Vowel Conservation** (Repair Rule)
- Gates can add vowels (repair)
- Gates can modify vowels
- Gates should not delete vowels arbitrarily

### 5. **Structural Integrity** (General)
- Output length should be reasonable (not 10x input)
- No null/None in output units
- All output units are valid strings

---

## 🧪 Test Strategy

### Gates to Test (11 total)

**Group A: Core Gates (Priority 1)**
1. GateSukun - Vowel insertion for sukun sequences
2. GateShadda - Gemination handling
3. GateTanwin - Tanwin normalization

**Group B: Hamza & Special (Priority 2)**
4. GateHamza - Hamza rules
5. GateWasl - Hamzat al-wasl
6. GateWaqf - Pausal forms

**Group C: Advanced (Priority 3)**
7. GateIdgham - Assimilation
8. GateMadd - Long vowel rules
9. GateAssimilation - General assimilation
10. GateDeletion - Deletion rules
11. GateEpenthesis - Epenthesis rules

---

## 🔧 Implementation Plan

### Step 1: Create Hypothesis Strategies (30 min)

Create generators for:
- Arabic consonants (ب ت ث ج ح خ...)
- Arabic vowels (َ ُ ِ ا و ي)
- Valid Arabic units (consonant+vowel combos)
- Valid Arabic sequences (2-10 units)

### Step 2: Core Invariant Tests (2h)

For each gate:
```python
@given(arabic_sequence())
def test_gate_X_non_empty(units):
    result = gate_X.apply(units)
    assert len(result.output_units) > 0

@given(arabic_sequence())
def test_gate_X_consonant_order(units):
    consonants_in = extract_consonants(units)
    result = gate_X.apply(units)
    consonants_out = extract_consonants(result.output_units)
    assert consonants_in == consonants_out  # same order

@given(arabic_sequence())
def test_gate_X_no_ccc(units):
    result = gate_X.apply(units)
    assert not has_ccc_sequence(result.output_units)
```

### Step 3: Gate-Specific Tests (2h)

- GateSukun: Never introduces more than 1 consecutive sukun
- GateShadda: Geminated consonants are adjacent
- GateTanwin: Only affects word-final positions

### Step 4: Integration Tests (30 min)

- Run all gates in sequence (orchestrator)
- Verify final output maintains all invariants

---

## ✅ Acceptance Criteria

- [ ] 20+ property tests (2 per gate minimum)
- [ ] All tests pass with 100 examples (Hypothesis default)
- [ ] No flaky tests
- [ ] Tests run in <5 seconds total
- [ ] Clear error messages when invariant violated

---

## 📊 Expected Test Count

- Baseline: 333 tests
- New property tests: ~25 tests
- Final: ~358 tests

---

*Created: Feb 15, 2026*  
*Estimated Time: 4-5 hours*  
*Priority: High (Sprint 2 core task)*
