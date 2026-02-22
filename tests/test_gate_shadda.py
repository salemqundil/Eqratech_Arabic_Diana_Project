from fvafk.c2a.gates.gate_shadda import GateShadda
from fvafk.c2a.gate_framework import GateStatus
from fvafk.c2a.syllable import Segment, SegmentKind, VowelKind


def make_consonant(letter: str) -> Segment:
    return Segment(text=letter, kind=SegmentKind.CONSONANT)


def make_vowel(kind: VowelKind) -> Segment:
    return Segment(text="", kind=SegmentKind.VOWEL, vk=kind)


def test_gate_shadda_expands_gemination():
    gate = GateShadda()
    segments = [
        make_consonant("د"),
        make_vowel(VowelKind.SHADDA),
        make_vowel(VowelKind.FATHA),
    ]
    result = gate.apply(segments)
    assert len(result.output) == 4
    assert result.output[1].vk == VowelKind.SUKUN
    assert result.output[2].kind == SegmentKind.CONSONANT
    assert result.status == GateStatus.REPAIR


def test_gate_shadda_pass_through():
    gate = GateShadda()
    segments = [
        make_consonant("م"),
        make_vowel(VowelKind.FATHA),
    ]
    result = gate.apply(segments)
    assert result.status == GateStatus.ACCEPT
    assert result.output == segments


def test_gate_shadda_handles_missing_vowel_after_shadda():
    gate = GateShadda()
    segments = [
        make_consonant("س"),
        make_vowel(VowelKind.SHADDA),
    ]
    result = gate.apply(segments)
    assert any(seg.vk == VowelKind.SUKUN for seg in result.output)
    assert result.status == GateStatus.REPAIR
