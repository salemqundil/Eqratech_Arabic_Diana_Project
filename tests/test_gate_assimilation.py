from fvafk.c2a.gates.gate_assimilation import GateAssimilation
from fvafk.c2a.gate_framework import GateStatus
from fvafk.c2a.syllable import Segment, SegmentKind, VowelKind


def test_gate_assimilation_inserts_shadda_and_deletes_lam():
    gate = GateAssimilation()
    segments = [
        Segment(text="ا", kind=SegmentKind.CONSONANT),
        Segment(text="ل", kind=SegmentKind.CONSONANT),
        Segment(text="ش", kind=SegmentKind.CONSONANT),
    ]

    result = gate.apply(segments)

    assert result.status == GateStatus.REPAIR
    assert result.output[1].deleted is True
    assert any(
        seg.kind == SegmentKind.VOWEL and seg.vk == VowelKind.SHADDA
        for seg in result.output
    )


def test_gate_assimilation_no_change_for_moon_letters():
    gate = GateAssimilation()
    segments = [
        Segment(text="ا", kind=SegmentKind.CONSONANT),
        Segment(text="ل", kind=SegmentKind.CONSONANT),
        Segment(text="ق", kind=SegmentKind.CONSONANT),
    ]

    result = gate.apply(segments)

    assert result.status == GateStatus.ACCEPT
    assert result.output == segments
