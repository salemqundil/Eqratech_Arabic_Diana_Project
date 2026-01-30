"""Unit tests for GateDeletion."""

import pytest

from fvafk.c2a.gate_framework import GateStatus
from fvafk.c2a.gates.gate_deletion import GateDeletion
from fvafk.c2a.syllable import Segment, SegmentKind, VowelKind


def consonant(char: str) -> Segment:
    return Segment(text=char, kind=SegmentKind.CONSONANT)


def vowel(char: str, vk: VowelKind) -> Segment:
    return Segment(text=char, kind=SegmentKind.VOWEL, vk=vk)


@pytest.fixture
def gate():
    return GateDeletion()


def test_gate_deletion_alif_connected(gate):
    segments = [
        consonant("ف"),
        vowel("ِ", VowelKind.KASRA),
        consonant("ا"),
        consonant("ل"),
    ]

    result = gate.apply(segments)
    assert result.status == GateStatus.REPAIR
    assert result.output[2].deleted


def test_gate_deletion_alif_initial(gate):
    segments = [
        consonant("ا"),
        consonant("ل"),
    ]

    result = gate.apply(segments)
    assert result.status == GateStatus.ACCEPT
    assert not result.output[0].deleted


def test_gate_deletion_hamza_connected(gate):
    segments = [
        vowel("َ", VowelKind.FATHA),
        consonant("إ"),
    ]

    result = gate.apply(segments)
    assert result.status == GateStatus.REPAIR
    assert result.output[1].deleted


def test_gate_deletion_precondition_without_patterns(gate):
    segments = [
        consonant("ك"),
        vowel("َ", VowelKind.FATHA),
    ]

    assert gate.precondition(segments) is False
