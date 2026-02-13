from fvafk.c2a.gates.gate_wasl import GateWasl
from fvafk.c2a.gate_framework import GateStatus
from fvafk.c2a.syllable import Segment, SegmentKind, VowelKind


def make_consonant(letter: str) -> Segment:
    return Segment(text=letter, kind=SegmentKind.CONSONANT)


def make_vowel(letter: str, kind: VowelKind) -> Segment:
    return Segment(text=letter, kind=SegmentKind.VOWEL, vk=kind)


def test_gate_wasl_repairs_initial_sukun_to_kasra():
    gate = GateWasl()
    segments = [
        make_consonant("ل"),
        make_vowel("ْ", VowelKind.SUKUN),
        make_consonant("ي"),
        make_vowel("َ", VowelKind.FATHA),
    ]
    result = gate.apply(segments)
    assert result.status == GateStatus.REPAIR
    assert result.output[1].vk == VowelKind.KASRA


def test_gate_wasl_accepts_when_no_initial_sukun():
    gate = GateWasl()
    segments = [
        make_consonant("ك"),
        make_vowel("َ", VowelKind.FATHA),
        make_consonant("ت"),
    ]
    result = gate.apply(segments)
    assert result.status == GateStatus.ACCEPT

