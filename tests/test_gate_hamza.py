"""Unit tests for GateHamza (hamza placement rules)."""

import pytest

from fvafk.c2a.gate_framework import GateStatus
from fvafk.c2a.gates.gate_hamza import GateHamza
from fvafk.c2a.syllable import Segment, SegmentKind, VowelKind


def consonant(char: str) -> Segment:
    return Segment(text=char, kind=SegmentKind.CONSONANT)


def vowel(char: str, vk: VowelKind) -> Segment:
    return Segment(text=char, kind=SegmentKind.VOWEL, vk=vk)


@pytest.fixture
def gate():
    return GateHamza()


def test_gate_hamza_initial_fatha(gate):
    segments = [
        consonant("ء"),
        vowel("َ", VowelKind.FATHA),
        consonant("ك"),
    ]
    result = gate.apply(segments)
    assert result.status in {GateStatus.REPAIR, GateStatus.ACCEPT}
    assert result.output[0].text == "أ"


def test_gate_hamza_initial_kasra(gate):
    segments = [
        consonant("ء"),
        vowel("ِ", VowelKind.KASRA),
    ]
    result = gate.apply(segments)
    assert result.output[0].text == "إ"


def test_gate_hamza_medial_kasra_strength(gate):
    segments = [
        consonant("س"),
        vowel("ُ", VowelKind.DAMMA),
        consonant("ء"),
        vowel("ِ", VowelKind.KASRA),
        consonant("ل"),
    ]
    result = gate.apply(segments)
    assert result.output[2].text == "ئ"


def test_gate_hamza_medial_after_long_vowel(gate):
    segments = [
        consonant("م"),
        vowel("َ", VowelKind.FATHA),
        consonant("ا"),
        consonant("ء"),
        vowel("ٌ", VowelKind.TANWIN_DAMM),
    ]
    result = gate.apply(segments)
    assert result.output[3].text == "ء"


def test_gate_hamza_final_after_fatha(gate):
    segments = [
        consonant("م"),
        vowel("َ", VowelKind.FATHA),
        consonant("ل"),
        vowel("ْ", VowelKind.SUKUN),
        consonant("ء"),
    ]
    result = gate.apply(segments)
    assert result.output[-1].text == "ء" or result.output[-1].text == "أ"


def test_gate_hamza_no_hamza_precondition(gate):
    segments = [
        consonant("ك"),
        vowel("َ", VowelKind.FATHA),
    ]
    assert gate.precondition(segments) is False
