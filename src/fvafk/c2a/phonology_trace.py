"""
Phonology Trace System (C2a Layer)
===================================

Tracing system for phonological gate execution, integrated with Trace V1.

Sprint 2, Task 2.4.1
Date: February 15, 2026
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from .syllable import Segment
from .gate_framework import GateResult, GateStatus, GateDelta


@dataclass
class SegmentDiff:
    """Represents a change to segments during gate application"""
    index: int
    operation: str  # "unchanged" | "modified" | "inserted" | "deleted"
    before: Optional[str]
    after: Optional[str]
    reason: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "operation": self.operation,
            "before": self.before,
            "after": self.after,
            "reason": self.reason
        }


@dataclass
class PhonologyTraceStep:
    """Records a single gate application in the phonology pipeline"""
    gate_id: str
    status: GateStatus
    input_segments: List[Segment]
    output_segments: List[Segment]
    delta: Optional[GateDelta]
    time_ms: float
    timestamp: float
    notes: List[str] = field(default_factory=list)
    
    @classmethod
    def from_gate_result(cls, result: GateResult, timestamp: Optional[float] = None) -> "PhonologyTraceStep":
        """Create trace step from GateResult"""
        if timestamp is None:
            timestamp = datetime.now().timestamp()
        
        return cls(
            gate_id=result.gate_id or "unknown",
            status=result.status,
            input_segments=list(result.input_units) if result.input_units else [],
            output_segments=list(result.output) if hasattr(result, 'output') else list(result.output_units),
            delta=result.delta,
            time_ms=result.time_ms,
            timestamp=timestamp,
            notes=list(result.notes) if result.notes else []
        )
    
    def compute_diffs(self) -> List[SegmentDiff]:
        """Compute differences between input and output segments"""
        diffs: List[SegmentDiff] = []
        max_len = max(len(self.input_segments), len(self.output_segments))
        
        for i in range(max_len):
            input_seg = self.input_segments[i] if i < len(self.input_segments) else None
            output_seg = self.output_segments[i] if i < len(self.output_segments) else None
            
            if input_seg is None:
                diffs.append(SegmentDiff(i, "inserted", None, output_seg.text if output_seg else None))
            elif output_seg is None:
                diffs.append(SegmentDiff(i, "deleted", input_seg.text, None))
            elif input_seg.text != output_seg.text:
                diffs.append(SegmentDiff(i, "modified", input_seg.text, output_seg.text))
        
        return diffs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        diffs = self.compute_diffs()
        return {
            "gate_id": self.gate_id,
            "status": self.status.name,
            "input_count": len(self.input_segments),
            "output_count": len(self.output_segments),
            "changes": [d.to_dict() for d in diffs if d.operation != "unchanged"],
            "time_ms": round(self.time_ms, 3),
            "notes": self.notes
        }


@dataclass
class PhonologyTrace:
    """Complete trace of phonology pipeline execution"""
    input_text: str
    output_text: str
    steps: List[PhonologyTraceStep] = field(default_factory=list)
    total_time_ms: float = 0.0
    
    def add_step(self, step: PhonologyTraceStep) -> None:
        """Add trace step and update total time"""
        self.steps.append(step)
        self.total_time_ms += step.time_ms
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "input_text": self.input_text,
            "output_text": self.output_text,
            "total_gates": len(self.steps),
            "total_time_ms": round(self.total_time_ms, 3),
            "gates": [step.to_dict() for step in self.steps],
            "summary": {
                "accept_count": sum(1 for s in self.steps if s.status == GateStatus.ACCEPT),
                "repair_count": sum(1 for s in self.steps if s.status == GateStatus.REPAIR),
                "reject_count": sum(1 for s in self.steps if s.status == GateStatus.REJECT),
            }
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def format_summary(self) -> str:
        """Format as human-readable summary"""
        lines = [
            "=" * 60,
            "Phonology Pipeline Trace",
            "=" * 60,
            f"Input:  {self.input_text}",
            f"Output: {self.output_text}",
            f"Gates:  {len(self.steps)} executed",
            f"Time:   {self.total_time_ms:.2f}ms",
            "",
            "Gate Execution:",
        ]
        
        for i, step in enumerate(self.steps, 1):
            symbol = "✓" if step.status == GateStatus.ACCEPT else "⚡" if step.status == GateStatus.REPAIR else "✗"
            lines.append(f"  {i:2}. {symbol} {step.gate_id:15} {step.time_ms:6.2f}ms")
        
        summary = self.to_dict()["summary"]
        lines.extend(["", f"Summary: {summary['accept_count']} accept, {summary['repair_count']} repair, {summary['reject_count']} reject", "=" * 60])
        return "\n".join(lines)


def create_trace_step(result: GateResult) -> PhonologyTraceStep:
    """Convenience function to create trace step from GateResult"""
    return PhonologyTraceStep.from_gate_result(result)
