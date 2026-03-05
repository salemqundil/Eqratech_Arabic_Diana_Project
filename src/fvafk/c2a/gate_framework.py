from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from time import perf_counter
from typing import Any, Dict, List, Optional, Tuple


class GateStatus(Enum):
    ACCEPT = auto()
    REPAIR = auto()
    REJECT = auto()


@dataclass
class GateDelta:
    """
    Structured diff between input and output.

    Conservative: we keep it very light so it doesn't force
    any gate to compute heavy diffs.
    """
    changed: bool = False
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


@dataclass
class GateResult:
    """
    Canonical GateResult shape (Sprint 2).

    Backward compatible:
      - output == output_units
      - reason == primary note
      - deltas == delta.notes
      - latency_ms == time_ms
    """

    # Canonical fields
    gate_id: str
    status: GateStatus
    input_units: List[str]
    output_units: List[str]

    delta: GateDelta = field(default_factory=GateDelta)
    time_ms: float = 0.0

    notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def __init__(
        self,
        status: GateStatus,
        gate_id: str = "",
        input_units: Optional[List[str]] = None,
        output_units: Optional[List[str]] = None,
        delta: Optional[GateDelta] = None,
        time_ms: float = 0.0,
        notes: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
        errors: Optional[List[str]] = None,
        # Backward compatibility kwargs
        output: Optional[List[str]] = None,
        reason: Optional[str] = None,
        deltas: Optional[List[str]] = None,
        latency_ms: Optional[float] = None,
    ):
        """Initialize with backward compatibility for old field names"""
        self.status = status
        self.gate_id = gate_id
        
        # Handle backward compatibility
        if output is not None:
            self.output_units = output
            self.input_units = input_units or output
        else:
            self.output_units = output_units or []
            self.input_units = input_units or []
        
        # Handle delta backward compatibility
        if deltas is not None:
            self.delta = GateDelta(changed=True, notes=deltas)
        else:
            self.delta = delta or GateDelta(changed=(self.input_units != self.output_units))
        
        # Handle time backward compatibility
        if latency_ms is not None:
            self.time_ms = latency_ms
        else:
            self.time_ms = time_ms
        
        # Handle notes backward compatibility
        if reason is not None:
            self.notes = [reason] + (notes or [])
        else:
            self.notes = notes or []
        
        self.warnings = warnings or []
        self.errors = errors or []

    # -------------------------
    # Backward-compat aliases
    # -------------------------
    @property
    def output(self) -> List[str]:
        return self.output_units

    @property
    def reason(self) -> str:
        # Old code expects a single string.
        # We map to the first note if present.
        return self.notes[0] if self.notes else ""

    @property
    def deltas(self) -> List[str]:
        return self.delta.notes

    @property
    def latency_ms(self) -> float:
        return self.time_ms


class BaseGate(ABC):
    """
    All gates should inherit this. We keep it generic:
    gates can focus on transformation only.
    """
    gate_id: str

    def __init__(self, gate_id: str):
        self.gate_id = gate_id

    @abstractmethod
    def apply(self, segments: List[str]) -> GateResult:
        """
        Must return GateResult (canonical).
        """
        raise NotImplementedError

    def _result(
        self,
        status: GateStatus,
        input_units: List[str],
        output_units: List[str],
        *,
        delta: Optional[GateDelta] = None,
        notes: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
        errors: Optional[List[str]] = None,
        time_ms: float = 0.0,
    ) -> GateResult:
        return GateResult(
            gate_id=self.gate_id,
            status=status,
            input_units=input_units,
            output_units=output_units,
            delta=delta or GateDelta(changed=(input_units != output_units)),
            time_ms=time_ms,
            notes=notes or [],
            warnings=warnings or [],
            errors=errors or [],
        )


class GateOrchestrator:
    """
    Runs gates in order.
    Conservative: does not assume gates share state.
    """
    def __init__(self, gates: List[BaseGate]):
        self.gates = gates

    def run(self, segments: List[str]) -> Tuple[List[str], List[GateResult]]:
        current = segments
        results: List[GateResult] = []

        for gate in self.gates:
            t0 = perf_counter()
            result = gate.apply(current)
            result.time_ms = (perf_counter() - t0) * 1000.0

            results.append(result)

            if result.status == GateStatus.REJECT:
                return current, results

            current = result.output_units

        return current, results


# Legacy alias for backward compatibility
PhonologicalGate = BaseGate
