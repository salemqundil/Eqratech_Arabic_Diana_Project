"""Tests for GateMadd (Arabic madd detection)."""

from fvafk.c2a.gate_framework import GateStatus
from fvafk.c2a.gates.gate_madd import GateMadd
from fvafk.c2a.syllable import Segment, SegmentKind, VowelKind


def consonant(char):
    return Segment(text=char, kind=SegmentKind.CONSONANT)


def vowel(char, vk):
    return Segment(text=char, kind=SegmentKind.VOWEL, vk=vk)


def test_gate_madd_tabii():
    gate = GateMadd()
    segments = [
        consonant("ق"),
        vowel("َ", VowelKind.FATHA),
        consonant("ا"),
        consonant("ل"),
        vowel("َ", VowelKind.FATHA),
    ]
    result = gate.apply(segments)
    assert result.status == GateStatus.ACCEPT
    assert any("madd_natural" in d or "madd_tabii" in d for d in result.deltas)


def test_gate_madd_with_damma_waw():
    gate = GateMadd()
    segments = [
        consonant("ق"),
        vowel("ُ", VowelKind.DAMMA),
        consonant("و"),
        consonant("ل"),
        vowel("ُ", VowelKind.DAMMA),
    ]
    result = gate.apply(segments)
    assert result.status == GateStatus.ACCEPT
    assert any("madd_natural" in d or "madd_tabii" in d for d in result.deltas)


def test_gate_madd_with_kasra_ya():
    gate = GateMadd()
    segments = [
        consonant("ق"),
        vowel("ِ", VowelKind.KASRA),
        consonant("ي"),
        consonant("ل"),
        vowel("َ", VowelKind.FATHA),
    ]
    result = gate.apply(segments)
    assert result.status == GateStatus.ACCEPT
    assert any("madd_natural" in d or "madd_tabii" in d for d in result.deltas)


def test_gate_madd_lazim():
    gate = GateMadd()
    segments = [
        consonant("ص"),
        vowel("َ", VowelKind.FATHA),
        consonant("ا"),
        vowel("ّ", VowelKind.SHADDA),
        consonant("ل"),
    ]
    result = gate.apply(segments)
    assert result.status == GateStatus.ACCEPT
    assert any("madd_necessary" in d or "madd_lazim" in d for d in result.deltas)


def test_gate_madd_no_madd():
    gate = GateMadd()
    segments = [
        consonant("ك"),
        vowel("َ", VowelKind.FATHA),
        consonant("ت"),
        vowel("َ", VowelKind.FATHA),
        consonant("ب"),
        vowel("َ", VowelKind.FATHA),
    ]
    result = gate.apply(segments)
    assert result.status == GateStatus.ACCEPT
    assert result.deltas == []


def test_gate_madd_multiple():
    gate = GateMadd()
    segments = [
        consonant("ق"),
        vowel("َ", VowelKind.FATHA),
        consonant("ا"),
        consonant("ل"),
        vowel("ُ", VowelKind.DAMMA),
        consonant("و"),
        consonant("ا"),
    ]
    result = gate.apply(segments)
    assert result.status == GateStatus.ACCEPT
    assert len([d for d in result.deltas if "madd" in d]) >= 2
