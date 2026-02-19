# Task 2.4.1: Phonology V2 Trace Integration

**Sprint 2, Part 2.4**  
**Status:** Starting...  
**Estimated Time:** 3 hours

---

## 🎯 Goal

Integrate phonological gate tracing with the existing Trace V1 system, making the phonology layer auditable and debuggable.

---

## 📋 Requirements

### 1. Gate Trace Structure

Each gate should log:
- **Input:** Units before gate application
- **Output:** Units after gate application
- **Status:** ACCEPT / REPAIR / REJECT
- **Changes:** What was modified (delta)
- **Reason:** Why the change was made
- **Time:** Execution time (time_ms)

### 2. Integration with Trace V1

Connect to existing trace system:
- File: `src/fvafk/trace_v1.py`
- Add phonology-specific trace entries
- Maintain compatibility with existing trace format

### 3. Trace Replay

Enable step-by-step replay:
- Start from input
- Apply each gate in sequence
- Show intermediate states
- Verify final output matches

---

## 🔧 Implementation Plan

### Step 1: Enhance GateResult for Tracing (30 min)

**File:** `src/fvafk/c2a/gate_framework.py`

Already has:
- ✅ `input_units`
- ✅ `output_units`
- ✅ `delta: GateDelta`
- ✅ `time_ms`
- ✅ `notes`

Add:
- Trace serialization method
- Human-readable format

### Step 2: Create PhonologyTrace Class (1h)

**New File:** `src/fvafk/c2a/phonology_trace.py`

```python
@dataclass
class PhonologyTrace:
    """Trace for phonological gate execution"""
    gate_id: str
    input_units: List[Segment]
    output_units: List[Segment]
    status: GateStatus
    delta: GateDelta
    time_ms: float
    timestamp: float
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        ...
    
    def diff_view(self) -> str:
        """Show before/after diff"""
        ...
```

### Step 3: Integrate with GateOrchestrator (30 min)

**File:** `src/fvafk/c2a/gate_framework.py`

Update `GateOrchestrator.run()`:
- Collect trace for each gate
- Store in orchestrator
- Return traces with results

### Step 4: Connect to Trace V1 (1h)

**File:** `src/fvafk/trace_v1.py`

Add phonology section:
```python
{
    "traces": [...],
    "phonology_v2": {
        "gates": [
            {
                "gate_id": "sukun",
                "status": "REPAIR",
                "changes": [...],
                "time_ms": 0.5
            }
        ],
        "total_time_ms": 15.3
    }
}
```

---

## 🧪 Testing Strategy

### Test 1: Basic Trace Collection
```python
def test_gate_trace_collection():
    gate = GateSukun()
    segments = [...]
    result = gate.apply(segments)
    
    # Should have trace info
    assert result.gate_id == "sukun"
    assert result.input_units is not None
    assert result.time_ms > 0
```

### Test 2: Orchestrator Trace
```python
def test_orchestrator_collects_traces():
    orchestrator = GateOrchestrator([gate1, gate2])
    output, results = orchestrator.run(input_segments)
    
    # Should have trace for each gate
    assert len(results) == 2
    for result in results:
        assert result.gate_id
        assert result.time_ms >= 0
```

### Test 3: Trace Replay
```python
def test_trace_replay():
    # Apply gates and collect trace
    original_output, traces = run_with_trace(input)
    
    # Replay from trace
    replayed_output = replay_from_trace(traces)
    
    # Should produce same output
    assert replayed_output == original_output
```

---

## 📊 Deliverables

- [ ] `src/fvafk/c2a/phonology_trace.py` (new file)
- [ ] Enhanced `GateOrchestrator` with trace collection
- [ ] Integration with `trace_v1.py`
- [ ] 5+ tests for tracing functionality
- [ ] Example trace output in docs

---

## ✅ Acceptance Criteria

- [ ] All gates produce traceable results
- [ ] Orchestrator collects full trace
- [ ] Trace can be serialized to JSON
- [ ] Trace can be replayed step-by-step
- [ ] Integration with existing Trace V1
- [ ] All tests passing
- [ ] CLI can output trace with `--trace` flag

---

## 🔍 Example Output

```json
{
  "input": "الْكِتَابُ",
  "phonology_trace": {
    "gates": [
      {
        "gate_id": "sukun",
        "status": "REPAIR",
        "input": ["ا", "لْ", "كِ", "تَ", "ا", "بُ"],
        "output": ["ا", "لَ", "كِ", "تَ", "ا", "بُ"],
        "changes": ["repaired sukun at index 1: ْ → َ"],
        "time_ms": 0.8
      },
      {
        "gate_id": "shadda",
        "status": "ACCEPT",
        "time_ms": 0.3
      }
    ],
    "total_gates": 11,
    "total_time_ms": 12.5
  }
}
```

---

*Created: Feb 15, 2026*  
*Sprint 2, Task 2.4.1*  
*Priority: Medium*
