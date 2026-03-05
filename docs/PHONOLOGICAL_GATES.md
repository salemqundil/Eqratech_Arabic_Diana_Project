# Phonological Gates Reference

**Version:** 1.0  
**Last Updated:** 2026-02-03

## Table of Contents
1. [Overview](#overview)
2. [Gate Specifications](#gate-specifications)
   - [Gate 1: GateSukun](#gate-1-gatesukun)
   - [Gate 2: GateShadda](#gate-2-gateshadda)
   - [Gate 3: GateHamza](#gate-3-gatehamza)
   - [Gate 4: GateWaqf](#gate-4-gatewaqf)
   - [Gate 5: GateIdgham](#gate-5-gateidgham)
   - [Gate 6: GateMadd](#gate-6-gatemadd)
   - [Gate 7: GateDeletion](#gate-7-gatedeletion)
   - [Gate 8: GateEpenthesis](#gate-8-gateepenthesis)
   - [Gate 9: GateAssimilation](#gate-9-gateassimilation)
   - [Gate 10: GateTanwin](#gate-10-gatetanwin)
3. [Gate Orchestration](#gate-orchestration)
4. [Implementation Guide](#implementation-guide)

---

## Overview

Phonological gates implement Tajweed-based rules for Arabic text processing. Each gate examines a sequence of segments and either:
- **ACCEPT**: Pass segments through unchanged
- **REPAIR**: Modify segments to fix violations
- **REJECT**: Fail processing due to unrecoverable error

### Base Interface

```python
from abc import ABC, abstractmethod
from typing import List

class PhonologicalGate(ABC):
    """Base class for all phonological gates."""
    
    def __init__(self, gate_id: str):
        self.gate_id = gate_id
    
    @abstractmethod
    def apply(self, segments: List[str]) -> GateResult:
        """
        Apply gate logic to segment sequence.
        
        Args:
            segments: List of Arabic segments (consonants, vowels, diacritics)
            
        Returns:
            GateResult with status (ACCEPT/REPAIR/REJECT), 
            output segments, reason, and deltas
        """
        pass
```

---

## Gate Specifications

### Gate 1: GateSukun

**File:** `src/fvafk/c2a/gates/gate_sukun.py`

**Purpose:** Repair double sukun violations (two consecutive consonants with sukun).

**Linguistic Rule:**  
In Arabic, two consecutive consonants cannot both have sukun (ْ). This violates syllable structure constraints. The first sukun must be converted to a short vowel (typically fatha).

**Algorithm:**
```
Input: [C₁, ْ, C₂, ْ, ...]

Check: If segments[i] = 'ْ' and segments[i+2] = 'ْ'
  ↓ VIOLATION DETECTED
Repair: Replace first 'ْ' with 'َ' (fatha)
  ↓
Output: [C₁, َ, C₂, ْ, ...]
Status: REPAIR
```

**Examples:**

| Input | Output | Status | Reason |
|-------|--------|--------|--------|
| `['ك', 'ْ', 'ت', 'ْ', 'ب']` | `['ك', 'َ', 'ت', 'ْ', 'ب']` | REPAIR | "Double sukun repaired at position 1" |
| `['ك', 'َ', 'ت', 'ْ', 'ب']` | `['ك', 'َ', 'ت', 'ْ', 'ب']` | ACCEPT | "No double sukun violation" |

**Code Structure:**
```python
class GateSukun(PhonologicalGate):
    def apply(self, segments: List[str]) -> GateResult:
        output = segments.copy()
        deltas = []
        
        for i in range(len(segments) - 2):
            if segments[i] == 'ْ' and segments[i + 2] == 'ْ':
                output[i] = 'َ'
                deltas.append(f"sukun→fatha at position {i}")
                return GateResult(
                    status=GateStatus.REPAIR,
                    output=output,
                    reason="Double sukun repaired",
                    deltas=deltas
                )
        
        return GateResult(
            status=GateStatus.ACCEPT,
            output=segments,
            reason="No sukun violation"
        )
```

---

### Gate 2: GateShadda

**File:** `src/fvafk/c2a/gates/gate_shadda.py`

**Purpose:** Handle gemination (consonant doubling) represented by shadda (ّ).

**Linguistic Rule:**  
Shadda (ّ) marks a geminated consonant (doubled consonant). It should be expanded to explicit doubling for morphological analysis or accepted as-is for phonological representation.

**Algorithm:**
```
Input: [C, ّ, ...]

Option 1 (Expand): [C, ّ, ...] → [C, C, ...]
Option 2 (Accept): [C, ّ, ...] → ACCEPT as valid
```

**Examples:**

| Input | Output | Status | Reason |
|-------|--------|--------|--------|
| `['د', 'ّ', 'ر', 'س']` | `['د', 'ّ', 'ر', 'س']` | ACCEPT | "Shadda preserved" |
| `['م', 'ُ', 'د', 'ّ', 'ر', 'س']` | `['م', 'ُ', 'د', 'ّ', 'ر', 'س']` | ACCEPT | "Gemination valid" |

**Implementation Note:**  
Current implementation ACCEPTs shadda rather than expanding, as morphological analysis handles gemination during root extraction.

---

### Gate 3: GateHamza

**File:** `src/fvafk/c2a/gates/gate_hamza.py`

**Purpose:** Validate hamza placement rules (أ، إ، ؤ، ئ، ء).

**Linguistic Rule:**  
Hamza (ء) appears:
- On alif (أ، إ، آ) when word-initial
- On waw (ؤ) when preceded by damma
- On yaa (ئ) when preceded by kasra
- On the line (ء) when preceded by sukun or long vowel

**Algorithm:**
```
For each hamza carrier in input:
  1. Check preceding vowel/diacritic
  2. Verify carrier matches rule
  3. ACCEPT if valid, REPAIR if incorrect carrier
```

**Examples:**

| Context | Valid Carrier | Invalid | Repair |
|---------|---------------|---------|--------|
| Word-initial | أ (alif) | - | - |
| After damma (ُ) | ؤ (waw) | ئ | ُ + ئ → ُ + ؤ |
| After kasra (ِ) | ئ (yaa) | ؤ | ِ + ؤ → ِ + ئ |
| After sukun (ْ) | ء (on line) | أ | ْ + أ → ْ + ء |

**Code Example:**
```python
class GateHamza(PhonologicalGate):
    HAMZA_CARRIERS = {'أ', 'إ', 'آ', 'ؤ', 'ئ', 'ء'}
    
    def apply(self, segments: List[str]) -> GateResult:
        for i, seg in enumerate(segments):
            if seg in self.HAMZA_CARRIERS:
                if not self._is_valid_hamza_position(segments, i):
                    # Repair logic
                    correct_carrier = self._get_correct_carrier(segments, i)
                    output = segments.copy()
                    output[i] = correct_carrier
                    return GateResult(
                        status=GateStatus.REPAIR,
                        output=output,
                        reason=f"Hamza carrier corrected to {correct_carrier}"
                    )
        return GateResult(status=GateStatus.ACCEPT, output=segments, reason="Hamza valid")
```

---

### Gate 4: GateWaqf

**File:** `src/fvafk/c2a/gates/gate_waqf.py`

**Purpose:** Apply pause (وقف) and stopping rules at word boundaries.

**Linguistic Rule:**  
When pausing at word end:
- Drop final short vowel (fatha, kasra, damma)
- Convert tanwin (ً، ٌ، ٍ) to sukun
- Preserve long vowels and consonants

**Algorithm:**
```
If at word boundary (detected by space or end):
  1. Check last segment
  2. If short vowel or tanwin → drop/convert
  3. Otherwise → ACCEPT
```

**Examples:**

| Input (word-final) | Output | Status | Reason |
|-------------------|--------|--------|--------|
| `['ك', 'ت', 'ا', 'ب', 'ُ']` | `['ك', 'ت', 'ا', 'ب']` | REPAIR | "Final damma dropped for waqf" |
| `['ك', 'ت', 'ا', 'ب', 'ٌ']` | `['ك', 'ت', 'ا', 'ب', 'ْ']` | REPAIR | "Tanwin converted to sukun" |
| `['ك', 'ت', 'ا', 'ب']` | `['ك', 'ت', 'ا', 'ب']` | ACCEPT | "No waqf needed" |

---

### Gate 5: GateIdgham

**File:** `src/fvafk/c2a/gates/gate_idgham.py`

**Purpose:** Handle assimilation with ghunnah (nasal sound) in Tajweed.

**Linguistic Rule:**  
When noon sakinah (نْ) or tanwin (ً، ٌ، ٍ) is followed by certain letters (ي، ن، م، و), assimilation (إدغام) occurs with ghunnah (nasal prolongation).

**Assimilation Letters:** ي، ن، م، و (mnemonic: "ينمو")

**Algorithm:**
```
Input: [ن, ْ, Y, ...] where Y ∈ {ي، ن، م، و}

Check: If نْ or tanwin followed by assimilation letter
  ↓ ASSIMILATION DETECTED
Repair: Merge noon into following letter with ghunnah marker
  ↓
Output: [Y, '~', ...]  # '~' = ghunnah marker
Status: REPAIR
```

**Examples:**

| Input | Output | Status | Reason |
|-------|--------|--------|--------|
| `['م', 'ن', 'ْ', 'ي', 'و', 'م']` | `['م', 'ي', '~', 'و', 'م']` | REPAIR | "Idgham with ghunnah: نْ + ي" |
| `['م', 'ن', 'ْ', 'ب']` | `['م', 'ن', 'ْ', 'ب']` | ACCEPT | "No idgham (ب not in ينمو)" |

---

### Gate 6: GateMadd

**File:** `src/fvafk/c2a/gates/gate_madd.py`

**Purpose:** Detect and classify vowel lengthening (مد).

**Linguistic Rule:**  
Madd occurs when:
1. **Natural madd (طبيعي)**: Long vowel (ا، و، ي) after matching short vowel
2. **Connected madd (متصل)**: Long vowel followed by hamza in same word
3. **Separate madd (منفصل)**: Long vowel at end of word, hamza at start of next
4. **Necessary madd (لازم)**: Long vowel followed by shadda

**Algorithm:**
```
For each long vowel position:
  1. Check preceding short vowel (match?)
  2. Check following segment (hamza? shadda? word boundary?)
  3. Classify madd type
  4. Tag with appropriate marker
```

**Examples:**

| Input | Madd Type | Output | Reason |
|-------|-----------|--------|--------|
| `['ق', 'َ', 'ا', 'ل']` | Natural | `['ق', 'َ', 'ا', '~2', 'ل']` | "Fatha + alif = 2 counts" |
| `['س', 'َ', 'ا', 'ء']` | Connected | `['س', 'َ', 'ا', '~4', 'ء']` | "Long vowel + hamza = 4-5 counts" |
| `['م', 'َ', 'ا', 'ّ']` | Necessary | `['م', 'َ', 'ا', '~6', 'ّ']` | "Long vowel + shadda = 6 counts" |

---

### Gate 7: GateDeletion

**File:** `src/fvafk/c2a/gates/gate_deletion.py`

**Purpose:** Delete predictable segments in connected speech.

**Linguistic Rule:**  
In fluent speech, certain segments are deleted:
- Hamzat al-wasl (ا) at word-initial after vowel
- Short vowels in unstressed positions
- Alif after long vowel in some patterns

**Algorithm:**
```
For each segment:
  1. Check if deletable (hamzat wasl, unstressed vowel)
  2. Check context (after vowel? in middle of utterance?)
  3. Delete if conditions met
```

**Examples:**

| Input (connected speech) | Output | Status | Reason |
|--------------------------|--------|--------|--------|
| `['و', 'َ', 'ال', 'ك', 'ت', 'ا', 'ب']` | `['و', 'َ', 'ل', 'ك', 'ت', 'ا', 'ب']` | REPAIR | "Hamzat wasl deleted after vowel" |
| `['ك', 'ت', 'ا', 'ا', 'ب']` | `['ك', 'ت', 'ا', 'ب']` | REPAIR | "Redundant alif deleted" |

---

### Gate 8: GateEpenthesis

**File:** `src/fvafk/c2a/gates/gate_epenthesis.py`

**Purpose:** Insert vowels to break illicit consonant clusters.

**Linguistic Rule:**  
Arabic syllable structure forbids certain consonant clusters. When they occur (e.g., at word boundaries, with borrowed words), insert kasra (ِ) to break the cluster.

**Algorithm:**
```
Input: [..., C₁, C₂, C₃, ...]

Check: If three consonants appear with no intervening vowel
  ↓ CLUSTER DETECTED
Repair: Insert kasra between C₁ and C₂
  ↓
Output: [..., C₁, ِ, C₂, C₃, ...]
Status: REPAIR
```

**Examples:**

| Input | Output | Status | Reason |
|-------|--------|--------|--------|
| `['ك', 'ت', 'ب']` (3 consonants) | `['ك', 'ِ', 'ت', 'ب']` | REPAIR | "Epenthetic kasra breaks cluster" |
| `['ك', 'َ', 'ت', 'ب']` | `['ك', 'َ', 'ت', 'ب']` | ACCEPT | "No cluster (vowel present)" |

---

### Gate 9: GateAssimilation

**File:** `src/fvafk/c2a/gates/gate_assimilation.py`

**Purpose:** Handle lam (ل) assimilation with sun letters.

**Linguistic Rule:**  
The definite article ال (alif-lam) assimilates its lam to following "sun letters" (الحروف الشمسية):  
**Sun letters:** ت، ث، د، ذ، ر، ز، س، ش، ص، ض، ط، ظ، ل، ن

**Algorithm:**
```
Input: [ا, ل, ْ, S, ...] where S = sun letter

Check: If ال followed by sun letter
  ↓ ASSIMILATION
Repair: Replace ل with sun letter + shadda
  ↓
Output: [ا, S, ّ, ...]
Status: REPAIR
```

**Examples:**

| Input | Output | Status | Reason |
|-------|--------|--------|--------|
| `['ا', 'ل', 'ش', 'م', 'س']` (الشمس) | `['ا', 'ش', 'ّ', 'م', 'س']` | REPAIR | "Lam assimilated to ش (sun letter)" |
| `['ا', 'ل', 'ق', 'م', 'ر']` (القمر) | `['ا', 'ل', 'ق', 'م', 'ر']` | ACCEPT | "No assimilation (ق is moon letter)" |

**Sun vs. Moon Letters:**
- **Sun (شمسية):** ت ث د ذ ر ز س ش ص ض ط ظ ل ن (14 letters)
- **Moon (قمرية):** ا ب ج ح خ ع غ ف ق ك م ه و ي (14 letters)

---

### Gate 10: GateTanwin

**File:** `src/fvafk/c2a/gates/gate_tanwin.py`

**Purpose:** Expand tanwin (double diacritics) into explicit noon.

**Linguistic Rule:**  
Tanwin (ً، ٌ، ٍ) represents "-n" sound at word end for indefinite nouns. It should be expanded to short vowel + noon (ن).

**Algorithm:**
```
Input: [..., C, ً/ٌ/ٍ]

Expand:
  ً (fathatan) → َ + ن
  ٌ (dammatan) → ُ + ن
  ٍ (kasratan) → ِ + ن

Output: [..., C, V, ن]
Status: REPAIR
```

**Examples:**

| Input | Output | Status | Reason |
|-------|--------|--------|--------|
| `['ك', 'ت', 'ا', 'ب', 'ٌ']` | `['ك', 'ت', 'ا', 'ب', 'ُ', 'ن']` | REPAIR | "Dammatan → damma + noon" |
| `['ب', 'ي', 'ت', 'ٍ']` | `['ب', 'ي', 'ت', 'ِ', 'ن']` | REPAIR | "Kasratan → kasra + noon" |
| `['م', 'د', 'ر', 'س', 'ة', 'ً']` | `['م', 'د', 'ر', 'س', 'ة', 'َ', 'ن']` | REPAIR | "Fathatan → fatha + noon" |

**Note:** Tanwin only appears on indefinite nouns in nominative, accusative, or genitive case.

---

## Gate Orchestration

### Sequential Processing

Gates are applied in a fixed order to ensure correct linguistic processing:

```python
from fvafk.c2a.gate_framework import GateOrchestrator
from fvafk.c2a.gates import (
    GateSukun, GateShadda, GateHamza, GateWaqf,
    GateIdgham, GateMadd, GateDeletion, GateEpenthesis,
    GateAssimilation, GateTanwin
)

# Create orchestrator with gates in order
orchestrator = GateOrchestrator([
    GateSukun("sukun"),
    GateShadda("shadda"),
    GateHamza("hamza"),
    GateWaqf("waqf"),
    GateIdgham("idgham"),
    GateMadd("madd"),
    GateDeletion("deletion"),
    GateEpenthesis("epenthesis"),
    GateAssimilation("assimilation"),
    GateTanwin("tanwin")
])

# Process segments
input_segments = ['ك', 'َ', 'ا', 'ت', 'ِ', 'ب', 'ٌ']
output_segments, results = orchestrator.run(input_segments)

# Inspect results
for i, result in enumerate(results):
    gate_name = orchestrator.gates[i].gate_id
    print(f"{gate_name}: {result.status.name} - {result.reason}")
    if result.deltas:
        print(f"  Changes: {', '.join(result.deltas)}")
```

### Early Termination

If any gate returns `GateStatus.REJECT`, orchestration stops immediately:

```python
def run(self, segments: List[str]) -> Tuple[List[str], List[GateResult]]:
    current = segments
    results = []
    
    for gate in self.gates:
        result = gate.apply(current)
        results.append(result)
        
        if result.status == GateStatus.REJECT:
            # Stop processing, return current state
            return current, results
        
        # Update segments for next gate
        current = result.output
    
    return current, results
```

---

## Implementation Guide

### Adding a New Gate

1. **Create gate file** in `src/fvafk/c2a/gates/`:
```python
# gate_mygate.py
from ..gate_framework import PhonologicalGate, GateResult, GateStatus
from typing import List

class GateMyGate(PhonologicalGate):
    def __init__(self):
        super().__init__("mygate")
    
    def apply(self, segments: List[str]) -> GateResult:
        # Implement your logic
        if self._check_violation(segments):
            repaired = self._repair(segments)
            return GateResult(
                status=GateStatus.REPAIR,
                output=repaired,
                reason="Violation repaired",
                deltas=[f"change at position X"]
            )
        return GateResult(
            status=GateStatus.ACCEPT,
            output=segments,
            reason="No violation"
        )
    
    def _check_violation(self, segments: List[str]) -> bool:
        # Check logic
        pass
    
    def _repair(self, segments: List[str]) -> List[str]:
        # Repair logic
        pass
```

2. **Add to `__init__.py`:**
```python
from .gate_mygate import GateMyGate

__all__ = [
    # ... existing gates
    'GateMyGate',
]
```

3. **Add to orchestrator:**
```python
orchestrator = GateOrchestrator([
    # ... existing gates
    GateMyGate(),
])
```

4. **Write tests** in `tests/test_gate_mygate.py`:
```python
import pytest
from fvafk.c2a.gates import GateMyGate
from fvafk.c2a.gate_framework import GateStatus

def test_mygate_accepts_valid():
    gate = GateMyGate()
    result = gate.apply(['valid', 'input'])
    assert result.status == GateStatus.ACCEPT

def test_mygate_repairs_violation():
    gate = GateMyGate()
    result = gate.apply(['invalid', 'input'])
    assert result.status == GateStatus.REPAIR
    assert result.output == ['expected', 'output']
```

---

## Related Documentation
- [Architecture Overview](ARCHITECTURE.md)
- [API Reference](API_REFERENCE.md)
- [Tutorial](TUTORIAL.md)

---

## References
- Tajweed rules: Ibn al-Jazari, *An-Nashr fi al-Qira'at al-'Ashr*
- Arabic phonology: Al-Nassir, *Sibawayh the Phonologist*
- Assimilation: Watson, J. *The Phonology and Morphology of Arabic* (2002)
