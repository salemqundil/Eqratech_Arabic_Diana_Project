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


def test_gate_epenthesis_breaks_cv_sense_ccc_with_sukun(gate):
    # Consonants separated only by sukun still appear as CCC in CV output,
    # so GateEpenthesis should insert a short vowel to break the run.
    segments = [
        consonant("ب"),
        sukun(),
        consonant("ل"),
        sukun(),
        consonant("غ"),
        Segment(text="َ", kind=SegmentKind.VOWEL, vk=VowelKind.FATHA),
    ]
    result = gate.apply(segments)
    assert result.status == GateStatus.REPAIR
    assert any(getattr(s, "vk", None) == VowelKind.KASRA for s in result.output)
