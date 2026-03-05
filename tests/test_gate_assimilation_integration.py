"""
Integration tests for GateAssimilation covering real Arabic examples.
"""

from fvafk.c2a.gates.gate_assimilation import GateAssimilation
from fvafk.c2a.gate_framework import GateStatus
from fvafk.c2a.syllable import Segment, SegmentKind, VowelKind


def make_segment(kind, cid=0, text="", vk=VowelKind.NONE):
    return Segment(text=text, kind=kind, cid=cid, vk=vk)


def test_real_word_al_shams():
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


def test_real_word_al_qamar():
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


def test_phrase_sun_and_nasal():
    gate = GateAssimilation()
    segments = [
        make_segment(SegmentKind.CONSONANT, cid=0, text="ا"),
        make_segment(SegmentKind.CONSONANT, cid=11, text="ل"),
        make_segment(SegmentKind.VOWEL, vk=VowelKind.SUKUN, text="ْ"),
        make_segment(SegmentKind.CONSONANT, cid=8, text="ش"),
        make_segment(SegmentKind.VOWEL, vk=VowelKind.FATHA, text="َ"),
        make_segment(SegmentKind.CONSONANT, cid=13, text="م"),
        make_segment(SegmentKind.VOWEL, vk=VowelKind.KASRA, text="ِ"),
        make_segment(SegmentKind.CONSONANT, cid=12, text="ن"),
        make_segment(SegmentKind.VOWEL, vk=VowelKind.SUKUN, text="ْ"),
        make_segment(SegmentKind.CONSONANT, cid=1, text="ب"),
    ]
    result = gate.apply(segments)
    assert any(seg.text == "م" for seg in result.output), "Nasal assimilation changed noon"
    assert any(seg.vk == VowelKind.SHADDA for seg in result.output), "Sun letter assimilation produces shadda"
