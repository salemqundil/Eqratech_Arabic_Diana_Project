from fvafk.c2a.gates.gate_assimilation import GateAssimilation
from fvafk.c2a.gate_framework import GateStatus
from fvafk.c2a.syllable import Segment, SegmentKind, VowelKind


def make_segment(kind: SegmentKind, cid: int = 0, text: str = "", vk: VowelKind = VowelKind.NONE):
    return Segment(text=text, kind=kind, vk=vk, cid=cid)


def test_gate_assimilation_sun_letters():
    gate = GateAssimilation()
    segments = [
        make_segment(SegmentKind.CONSONANT, cid=0, text="ا"),
        make_segment(SegmentKind.CONSONANT, cid=11, text="ل"),
        make_segment(SegmentKind.VOWEL, vk=VowelKind.SUKUN, text="ْ"),
        make_segment(SegmentKind.CONSONANT, cid=8, text="ش"),
        make_segment(SegmentKind.VOWEL, vk=VowelKind.FATHA, text="َ"),
    ]
    result = gate.apply(segments)
    assert result.status == GateStatus.REPAIR
    assert any(seg.vk == VowelKind.SHADDA for seg in result.output)


def test_gate_assimilation_moon_letters():
    gate = GateAssimilation()
    segments = [
        make_segment(SegmentKind.CONSONANT, cid=0, text="ا"),
        make_segment(SegmentKind.CONSONANT, cid=11, text="ل"),
        make_segment(SegmentKind.VOWEL, vk=VowelKind.SUKUN, text="ْ"),
        make_segment(SegmentKind.CONSONANT, cid=20, text="ق"),
        make_segment(SegmentKind.VOWEL, vk=VowelKind.FATHA, text="َ"),
    ]
    result = gate.apply(segments)
    assert result.status == GateStatus.ACCEPT
    assert len(result.deltas) == 0


def test_gate_assimilation_nasal_before_bilabial():
    gate = GateAssimilation()
    segments = [
        make_segment(SegmentKind.CONSONANT, cid=12, text="ن"),
        make_segment(SegmentKind.VOWEL, vk=VowelKind.SUKUN),
        make_segment(SegmentKind.CONSONANT, cid=1, text="ب"),
    ]
    result = gate.apply(segments)
    assert any(seg.text == "م" for seg in result.output)
    assert "nasal" in result.reason or any("nasal" in d for d in result.deltas)


def test_gate_assimilation_multiple_sun():
    gate = GateAssimilation()
    segments = [
        make_segment(SegmentKind.CONSONANT, cid=0, text="ا"),
        make_segment(SegmentKind.CONSONANT, cid=11, text="ل"),
        make_segment(SegmentKind.VOWEL, vk=VowelKind.SUKUN),
        make_segment(SegmentKind.CONSONANT, cid=8, text="ش"),
        make_segment(SegmentKind.VOWEL, vk=VowelKind.FATHA),
        make_segment(SegmentKind.CONSONANT, cid=0, text="ا"),
        make_segment(SegmentKind.CONSONANT, cid=11, text="ل"),
        make_segment(SegmentKind.VOWEL, vk=VowelKind.SUKUN),
        make_segment(SegmentKind.CONSONANT, cid=12, text="ن"),
        make_segment(SegmentKind.VOWEL, vk=VowelKind.FATHA),
    ]
    result = gate.apply(segments)
    assert len([d for d in result.deltas if "sun" in d]) == 2


def test_gate_assimilation_no_change():
    gate = GateAssimilation()
    segments = [
        make_segment(SegmentKind.CONSONANT, cid=1, text="ب"),
        make_segment(SegmentKind.VOWEL, vk=VowelKind.FATHA, text="َ"),
        make_segment(SegmentKind.CONSONANT, cid=2, text="ق"),
    ]
    result = gate.apply(segments)
    assert result.status == GateStatus.ACCEPT
    assert len(result.deltas) == 0
