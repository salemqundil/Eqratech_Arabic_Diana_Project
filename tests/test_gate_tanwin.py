from fvafk.c2a.gates.gate_tanwin import GateTanwin
from fvafk.c2a.gate_framework import GateStatus
from fvafk.c2a.syllable import Segment, SegmentKind, VowelKind


def make_consonant(letter: str, cid: int) -> Segment:
    return Segment(text=letter, kind=SegmentKind.CONSONANT, cid=cid)


def make_vowel(kind: VowelKind, text: str) -> Segment:
    return Segment(text=text, kind=SegmentKind.VOWEL, vk=kind)


def test_gate_tanwin_converts_tanwin_general():
    gate = GateTanwin()
    segments = [
        make_consonant("ك", 11),
        make_vowel(VowelKind.TANWIN_DAMM, "ٌ"),
    ]
    result = gate.apply(segments)
    assert result.status == GateStatus.REPAIR
    assert len(result.output) == 4
    assert result.output[1].vk == VowelKind.DAMMA
    assert result.output[2].text == "ن"
    assert result.output[3].vk == VowelKind.SUKUN


def test_gate_tanwin_keeps_non_tanwin():
    gate = GateTanwin()
    segments = [
        make_consonant("ب", 1),
        make_vowel(VowelKind.FATHA, "َ"),
    ]
    result = gate.apply(segments)
    assert result.status == GateStatus.ACCEPT
    assert result.output == segments


def test_gate_tanwin_handles_multiple_instances():
    gate = GateTanwin()
    segments = [
        make_consonant("م", 13),
        make_vowel(VowelKind.TANWIN_FATH, "ً"),
        make_consonant("ن", 14),
        make_vowel(VowelKind.TANWIN_KASR, "ٍ"),
    ]
    result = gate.apply(segments)
    assert "2 instances" in result.reason
    expanded_noons = [seg for seg in result.output if seg.text == "ن" and seg.cid == 12]
    assert len(expanded_noons) == 2
