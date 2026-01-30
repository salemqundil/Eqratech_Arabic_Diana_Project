from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Tuple


class GateStatus(Enum):
    ACCEPT = auto()
    REPAIR = auto()
    REJECT = auto()


@dataclass
class GateResult:
    status: GateStatus
    output: List[str]
    reason: str
    deltas: List[str] = field(default_factory=list)
    latency_ms: float = 0.0


class PhonologicalGate(ABC):
    def __init__(self, gate_id: str):
        self.gate_id = gate_id

    @abstractmethod
    def apply(self, segments: List[str]) -> GateResult:
        pass


class GateOrchestrator:
    def __init__(self, gates: List[PhonologicalGate]):
        self.gates = gates

    def run(self, segments: List[str]) -> Tuple[List[str], List[GateResult]]:
        current = segments
        results: List[GateResult] = []
        for gate in self.gates:
            result = gate.apply(current)
            results.append(result)
            if result.status == GateStatus.REJECT:
                return current, results
            current = result.output
        return current, results
