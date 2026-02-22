#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Phonology Trace System
=================================

Sprint 2, Task 2.4.1: Tests for phonology trace functionality.

Date: February 15, 2026
"""

import pytest
from fvafk.c2a.phonology_trace import (
    PhonologyTrace,
    PhonologyTraceStep,
    SegmentDiff,
    create_trace_step
)
from fvafk.c2a.syllable import Segment, SegmentKind, VowelKind
from fvafk.c2a.gate_framework import GateResult, GateStatus, GateDelta
from fvafk.c2a.gates.gate_sukun import GateSukun


# =============================================================================
# Helper Functions
# =============================================================================

def make_segment(text: str, kind: SegmentKind, vk: VowelKind = None) -> Segment:
    """Create a segment for testing"""
    return Segment(text=text, kind=kind, vk=vk)


def make_consonant(letter: str) -> Segment:
    """Create consonant segment"""
    return make_segment(letter, SegmentKind.CONSONANT)


def make_vowel(letter: str, vk: VowelKind) -> Segment:
    """Create vowel segment"""
    return make_segment(letter, SegmentKind.VOWEL, vk)


# =============================================================================
# Tests: SegmentDiff
# =============================================================================

def test_segment_diff_to_dict():
    """Test SegmentDiff.to_dict()"""
    diff = SegmentDiff(
        index=0,
        operation="modified",
        before="ْ",
        after="َ",
        reason="sukun repaired"
    )
    
    result = diff.to_dict()
    
    assert result["index"] == 0
    assert result["operation"] == "modified"
    assert result["before"] == "ْ"
    assert result["after"] == "َ"
    assert result["reason"] == "sukun repaired"


# =============================================================================
# Tests: PhonologyTraceStep
# =============================================================================

def test_trace_step_from_gate_result():
    """Test creating PhonologyTraceStep from GateResult"""
    input_segments = [
        make_consonant("ب"),
        make_vowel("ْ", VowelKind.SUKUN),
    ]
    
    output_segments = [
        make_consonant("ب"),
        make_vowel("َ", VowelKind.FATHA),
    ]
    
    result = GateResult(
        gate_id="test_gate",
        status=GateStatus.REPAIR,
        input_units=input_segments,
        output_units=output_segments,
        delta=GateDelta(changed=True, notes=["test change"]),
        time_ms=1.5,
        notes=["test note"]
    )
    
    step = PhonologyTraceStep.from_gate_result(result)
    
    assert step.gate_id == "test_gate"
    assert step.status == GateStatus.REPAIR
    assert len(step.input_segments) == 2
    assert len(step.output_segments) == 2
    assert step.time_ms == 1.5
    assert step.notes == ["test note"]


def test_trace_step_compute_diffs():
    """Test computing diffs between input and output"""
    input_segments = [
        make_consonant("ب"),
        make_vowel("ْ", VowelKind.SUKUN),
    ]
    
    output_segments = [
        make_consonant("ب"),
        make_vowel("َ", VowelKind.FATHA),
    ]
    
    step = PhonologyTraceStep(
        gate_id="sukun",
        status=GateStatus.REPAIR,
        input_segments=input_segments,
        output_segments=output_segments,
        delta=None,
        time_ms=1.0,
        timestamp=0.0
    )
    
    diffs = step.compute_diffs()
    
    # Should have 1 modification (vowel change)
    assert len(diffs) == 1
    assert diffs[0].operation == "modified"
    assert diffs[0].index == 1
    assert diffs[0].before == "ْ"
    assert diffs[0].after == "َ"


def test_trace_step_to_dict():
    """Test TraceStep.to_dict()"""
    input_segments = [make_consonant("ب")]
    output_segments = [make_consonant("ب")]
    
    step = PhonologyTraceStep(
        gate_id="test",
        status=GateStatus.ACCEPT,
        input_segments=input_segments,
        output_segments=output_segments,
        delta=None,
        time_ms=0.5,
        timestamp=123.456
    )
    
    result = step.to_dict()
    
    assert result["gate_id"] == "test"
    assert result["status"] == "ACCEPT"
    assert result["input_count"] == 1
    assert result["output_count"] == 1
    assert result["time_ms"] == 0.5
    assert "changes" in result


# =============================================================================
# Tests: PhonologyTrace
# =============================================================================

def test_phonology_trace_creation():
    """Test creating PhonologyTrace"""
    trace = PhonologyTrace(
        input_text="كِتَابٌ",
        output_text="كِتَابٌ"
    )
    
    assert trace.input_text == "كِتَابٌ"
    assert trace.output_text == "كِتَابٌ"
    assert len(trace.steps) == 0
    assert trace.total_time_ms == 0.0


def test_phonology_trace_add_step():
    """Test adding steps to trace"""
    trace = PhonologyTrace(
        input_text="test",
        output_text="test"
    )
    
    step1 = PhonologyTraceStep(
        gate_id="gate1",
        status=GateStatus.ACCEPT,
        input_segments=[],
        output_segments=[],
        delta=None,
        time_ms=1.0,
        timestamp=0.0
    )
    
    step2 = PhonologyTraceStep(
        gate_id="gate2",
        status=GateStatus.REPAIR,
        input_segments=[],
        output_segments=[],
        delta=None,
        time_ms=2.5,
        timestamp=0.0
    )
    
    trace.add_step(step1)
    trace.add_step(step2)
    
    assert len(trace.steps) == 2
    assert trace.total_time_ms == 3.5


def test_phonology_trace_to_dict():
    """Test PhonologyTrace.to_dict()"""
    trace = PhonologyTrace(
        input_text="input",
        output_text="output"
    )
    
    step = PhonologyTraceStep(
        gate_id="test",
        status=GateStatus.ACCEPT,
        input_segments=[],
        output_segments=[],
        delta=None,
        time_ms=1.0,
        timestamp=0.0
    )
    
    trace.add_step(step)
    
    result = trace.to_dict()
    
    assert result["input_text"] == "input"
    assert result["output_text"] == "output"
    assert result["total_gates"] == 1
    assert result["total_time_ms"] == 1.0
    assert len(result["gates"]) == 1
    assert "summary" in result
    assert result["summary"]["accept_count"] == 1


def test_phonology_trace_to_json():
    """Test PhonologyTrace.to_json()"""
    trace = PhonologyTrace(
        input_text="test",
        output_text="test"
    )
    
    json_str = trace.to_json()
    
    assert isinstance(json_str, str)
    assert "test" in json_str
    assert "total_gates" in json_str


def test_phonology_trace_format_summary():
    """Test formatting trace as summary"""
    trace = PhonologyTrace(
        input_text="input",
        output_text="output"
    )
    
    step = PhonologyTraceStep(
        gate_id="test_gate",
        status=GateStatus.REPAIR,
        input_segments=[],
        output_segments=[],
        delta=None,
        time_ms=1.5,
        timestamp=0.0
    )
    
    trace.add_step(step)
    
    summary = trace.format_summary()
    
    assert "Phonology Pipeline Trace" in summary
    assert "input" in summary
    assert "output" in summary
    assert "test_gate" in summary
    assert "1.50ms" in summary or "1.5" in summary


# =============================================================================
# Tests: Integration with Real Gates
# =============================================================================

def test_trace_with_real_gate():
    """Test tracing with actual GateSukun"""
    gate = GateSukun()
    
    # Input with double sukun
    segments = [
        make_consonant("ب"),
        make_vowel("ْ", VowelKind.SUKUN),
        make_consonant("ت"),
        make_vowel("ْ", VowelKind.SUKUN),
    ]
    
    result = gate.apply(segments)
    
    # Create trace step from result
    step = create_trace_step(result)
    
    # Gate ID may not be set by all gates yet (that's OK)
    assert step.gate_id is not None
    assert step.status == GateStatus.REPAIR
    assert len(step.input_segments) == 4
    assert step.time_ms >= 0


def test_trace_summary_counts():
    """Test trace summary counts accept/repair/reject correctly"""
    trace = PhonologyTrace("input", "output")
    
    # Add different status steps
    trace.add_step(PhonologyTraceStep(
        "gate1", GateStatus.ACCEPT, [], [], None, 1.0, 0.0
    ))
    trace.add_step(PhonologyTraceStep(
        "gate2", GateStatus.REPAIR, [], [], None, 2.0, 0.0
    ))
    trace.add_step(PhonologyTraceStep(
        "gate3", GateStatus.ACCEPT, [], [], None, 1.0, 0.0
    ))
    
    summary = trace.to_dict()["summary"]
    
    assert summary["accept_count"] == 2
    assert summary["repair_count"] == 1
    assert summary["reject_count"] == 0


# =============================================================================
# Tests: Edge Cases
# =============================================================================

def test_trace_with_no_steps():
    """Test trace with no steps"""
    trace = PhonologyTrace("input", "output")
    
    result = trace.to_dict()
    
    assert result["total_gates"] == 0
    assert result["total_time_ms"] == 0.0
    assert len(result["gates"]) == 0


def test_trace_step_with_empty_segments():
    """Test trace step with empty segments"""
    step = PhonologyTraceStep(
        gate_id="test",
        status=GateStatus.ACCEPT,
        input_segments=[],
        output_segments=[],
        delta=None,
        time_ms=0.0,
        timestamp=0.0
    )
    
    diffs = step.compute_diffs()
    assert len(diffs) == 0
    
    result = step.to_dict()
    assert result["input_count"] == 0
    assert result["output_count"] == 0


def test_trace_step_with_insertion():
    """Test diff with segment insertion"""
    input_segments = [make_consonant("ب")]
    output_segments = [make_consonant("ب"), make_vowel("َ", VowelKind.FATHA)]
    
    step = PhonologyTraceStep(
        "test", GateStatus.REPAIR,
        input_segments, output_segments,
        None, 1.0, 0.0
    )
    
    diffs = step.compute_diffs()
    
    assert len(diffs) == 1
    assert diffs[0].operation == "inserted"
    assert diffs[0].before is None
    assert diffs[0].after == "َ"


def test_trace_step_with_deletion():
    """Test diff with segment deletion"""
    input_segments = [make_consonant("ب"), make_vowel("َ", VowelKind.FATHA)]
    output_segments = [make_consonant("ب")]
    
    step = PhonologyTraceStep(
        "test", GateStatus.REPAIR,
        input_segments, output_segments,
        None, 1.0, 0.0
    )
    
    diffs = step.compute_diffs()
    
    assert len(diffs) == 1
    assert diffs[0].operation == "deleted"
    assert diffs[0].before == "َ"
    assert diffs[0].after is None


# =============================================================================
# Run: pytest tests/test_phonology_trace.py -v
# =============================================================================
