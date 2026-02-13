from .syllable import Segment, SegmentKind, Syllable, SyllableType
from .gates import (
    GateAssimilation,
    GateDeletion,
    GateEpenthesis,
    GateHamza,
    GateIdgham,
    GateMadd,
    GateTanwin,
    GateShadda,
    GateSukun,
    GateWasl,
    GateWaqf,
)
from .gate_framework import GateOrchestrator

GateFramework = GateOrchestrator

__all__ = [
    "Segment",
    "SegmentKind",
    "Syllable",
    "SyllableType",
    "GateAssimilation",
    "GateDeletion",
    "GateEpenthesis",
    "GateHamza",
    "GateIdgham",
    "GateMadd",
    "GateTanwin",
    "GateShadda",
    "GateSukun",
    "GateWasl",
    "GateWaqf",
    "GateFramework",
]
