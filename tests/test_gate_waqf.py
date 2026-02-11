"""Unit tests for GateWaqf (pause rules)."""

import pytest

from fvafk.c2a.gate_framework import GateStatus
from fvafk.c2a.gates.gate_waqf import GateWaqf
from fvafk.c2a.syllable import Segment, SegmentKind, VowelKind


def consonant(char: str) -> Segment:
    return Segment(text=char, kind=SegmentKind.CONSONANT)


def vowel(char: str, vk: VowelKind) -> Segment:
    return Segment(text=char, kind=SegmentKind.VOWEL, vk=vk)


@pytest.fixture
def gate():
    return GateWaqf()


def test_gate_waqf_tanwin_to_sukun(gate):
    segments = [
        consonant("ك"),
        vowel("َ", VowelKind.FATHA),
        consonant("ت"),
        vowel("َ", VowelKind.FATHA),
        consonant("ب"),
        vowel("ً", VowelKind.TANWIN_FATH),
    ]

    result = gate.apply(segments)
    assert result.status == GateStatus.REPAIR
    assert result.output[-1].text == "ْ"


def test_gate_waqf_ta_marbuta_to_ha(gate):
    segments = [
        consonant("م"),
        vowel("َ", VowelKind.FATHA),
        consonant("د"),
        vowel("ْ", VowelKind.SUKUN),
        consonant("ر"),
        vowel("َ", VowelKind.FATHA),
        consonant("س"),
        vowel("َ", VowelKind.FATHA),
        consonant("ة"),
    ]

    result = gate.apply(segments)
    assert result.status == GateStatus.REPAIR
    assert result.output[-1].text == "ه"


def test_gate_waqf_tanwin_and_ta_marbuta(gate):
    segments = [
        consonant("ج"),
        vowel("َ", VowelKind.FATHA),
        consonant("ن"),
        vowel("ّ", VowelKind.SHADDA),
        vowel("َ", VowelKind.FATHA),
        consonant("ة"),
        vowel("ٌ", VowelKind.TANWIN_DAMM),
    ]

    result = gate.apply(segments)
    assert result.status == GateStatus.REPAIR
    assert result.output[-2].text == "ه"
    assert result.output[-1].text == "ْ"


def test_gate_waqf_multiple_words(gate):
    segments = [
        consonant("ك"),
        vowel("ِ", VowelKind.KASRA),
        consonant("ت"),
        vowel("َ", VowelKind.FATHA),
        consonant("ب"),
        vowel("ٌ", VowelKind.TANWIN_DAMM),
        consonant(" "),
        consonant("ج"),
        vowel("َ", VowelKind.FATHA),
        consonant("د"),
        vowel("ِ", VowelKind.KASRA),
        consonant("ي"),
        vowel("ُ", VowelKind.DAMMA),
        consonant("د"),
        vowel("ٌ", VowelKind.TANWIN_DAMM),
    ]

    result = gate.apply(segments)
    assert result.status == GateStatus.REPAIR
    assert result.output[5].text == "ْ"
    assert result.output[-1].text == "ْ"


def test_gate_waqf_precondition_fails(gate):
    segments = [
        consonant("ك"),
        vowel("َ", VowelKind.FATHA),
        consonant("ت"),
        vowel("َ", VowelKind.FATHA),
        consonant("ب"),
    ]

    assert gate.precondition(segments) is False


def test_gate_waqf_empty_input(gate):
    result = gate.apply([])
    assert result.status == GateStatus.ACCEPT
    assert result.deltas == []
