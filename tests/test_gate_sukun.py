import pytest

from fvafk.c2a.gates.gate_sukun import GateSukun
from fvafk.c2a.syllable import Segment, SegmentKind, VowelKind
from fvafk.c2a.gate_framework import GateStatus


def make_consonant(letter: str) -> Segment:
    return Segment(text=letter, kind=SegmentKind.CONSONANT)


def make_vowel(letter: str, kind: VowelKind) -> Segment:
    return Segment(text=letter, kind=SegmentKind.VOWEL, vk=kind)


def test_gate_sukun_repairs_double_sukun():
    gate = GateSukun()
    segments = [
        make_consonant("ب"),
        make_vowel("ْ", VowelKind.SUKUN),
        make_consonant("ت"),
        make_vowel("ْ", VowelKind.SUKUN),
    ]
    result = gate.apply(segments)
    assert result.status == GateStatus.REPAIR
    assert result.output[1].vk == VowelKind.FATHA


def test_gate_sukun_accepts_without_double_sukun():
    gate = GateSukun()
    segments = [
        make_consonant("ك"),
        make_vowel("ْ", VowelKind.SUKUN),
        make_consonant("ب"),
        make_vowel("َ", VowelKind.FATHA),
    ]
    result = gate.apply(segments)
    assert result.status == GateStatus.ACCEPT


def test_gate_sukun_precondition_requires_sukun():
    gate = GateSukun()
    segments = [
        make_consonant("س"),
        make_vowel("َ", VowelKind.FATHA),
    ]
    assert not gate.precondition(segments)
