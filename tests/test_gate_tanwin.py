from fvafk.c2a.gates.gate_tanwin import GateTanwin
from fvafk.c2a.gate_framework import GateStatus
from fvafk.c2a.syllable import Segment, SegmentKind, VowelKind


def test_gate_tanwin_expands_to_nunation():
    gate = GateTanwin()
    segments = [
        Segment(text="ك", kind=SegmentKind.CONSONANT),
        Segment(text="ٌ", kind=SegmentKind.VOWEL, vk=VowelKind.TANWIN_DAMM),
    ]

    result = gate.apply(segments)

    assert result.status == GateStatus.REPAIR
    assert len(result.output) == 4
    assert result.output[1].vk == VowelKind.DAMMA
    assert result.output[2].kind == SegmentKind.CONSONANT
    assert result.output[2].text == "ن"
    assert result.output[3].vk == VowelKind.SUKUN


def test_gate_tanwin_no_change_when_absent():
    gate = GateTanwin()
    segments = [
        Segment(text="ك", kind=SegmentKind.CONSONANT),
        Segment(text="َ", kind=SegmentKind.VOWEL, vk=VowelKind.FATHA),
    ]

    result = gate.apply(segments)

    assert result.status == GateStatus.ACCEPT
    assert result.output == segments
