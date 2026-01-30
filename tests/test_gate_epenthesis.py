"""Unit tests for GateEpenthesis."""

import pytest

from fvafk.c2a.gate_framework import GateStatus
from fvafk.c2a.gates.gate_epenthesis import GateEpenthesis
from fvafk.c2a.syllable import Segment, SegmentKind, VowelKind


def consonant(char: str) -> Segment:
    return Segment(text=char, kind=SegmentKind.CONSONANT)


def sukun() -> Segment:
    return Segment(text="ْ", kind=SegmentKind.VOWEL, vk=VowelKind.SUKUN)


@pytest.fixture
def gate():
    return GateEpenthesis()


def test_gate_epenthesis_breaks_cluster(gate):
    segments = [
        consonant("ض"),
        sukun(),
        consonant("ر"),
        sukun(),
        consonant("ب"),
    ]
    result = gate.apply(segments)
    assert result.status == GateStatus.REPAIR
    assert len(result.output) > len(segments)


def test_gate_epenthesis_no_cluster(gate):
    segments = [
        consonant("ك"),
        Segment(text="َ", kind=SegmentKind.VOWEL, vk=VowelKind.FATHA),
        consonant("ت"),
    ]
    result = gate.apply(segments)
    assert result.status == GateStatus.ACCEPT
    assert len(result.deltas) == 0


def test_gate_epenthesis_precondition_false(gate):
    segments = [
        consonant("ب"),
        Segment(text="َ", kind=SegmentKind.VOWEL, vk=VowelKind.FATHA),
        consonant("ت"),
    ]
    assert gate.precondition(segments) is False
