"""Tests for GateIdgham (Tajwid idgham rules)"""

from fvafk.c2a.gates.gate_idgham import GateIdgham
from fvafk.c2a.gate_framework import GateStatus
from fvafk.c2a.syllable import Segment, SegmentKind, VowelKind


def consonant(char: str) -> Segment:
    return Segment(text=char, kind=SegmentKind.CONSONANT)


def vowel(char: str, vk: VowelKind) -> Segment:
    return Segment(text=char, kind=SegmentKind.VOWEL, vk=vk)


def test_gate_idgham_ghunnah_ya():
    gate = GateIdgham()
    segments = [
        consonant("م"),
        vowel("ِ", VowelKind.KASRA),
        consonant("ن"),
        vowel("ْ", VowelKind.SUKUN),
        consonant("ي"),
        vowel("َ", VowelKind.FATHA),
        consonant("و"),
        vowel("ْ", VowelKind.SUKUN),
        consonant("م"),
    ]

    result = gate.apply(segments)

    assert result.status == GateStatus.ACCEPT
    assert any("idgham_ghunnah" in d for d in result.deltas)

    ya_index = next(
        i
        for i, seg in enumerate(result.output)
        if seg.kind == SegmentKind.CONSONANT and seg.text == "ي"
    )
    assert result.output[ya_index + 1].vk == VowelKind.SHADDA


def test_gate_idgham_ghunnah_noon():
    gate = GateIdgham()
    segments = [
        consonant("م"),
        vowel("ِ", VowelKind.KASRA),
        consonant("ن"),
        vowel("ْ", VowelKind.SUKUN),
        consonant("ن"),
        vowel("َ", VowelKind.FATHA),
    ]

    result = gate.apply(segments)
    assert result.status == GateStatus.ACCEPT
    assert "idgham_ghunnah_ن" in result.deltas


def test_gate_idgham_no_ghunnah_lam():
    gate = GateIdgham()
    segments = [
        consonant("م"),
        vowel("ِ", VowelKind.KASRA),
        consonant("ن"),
        vowel("ْ", VowelKind.SUKUN),
        consonant("ل"),
        vowel("َ", VowelKind.FATHA),
    ]

    result = gate.apply(segments)
    assert result.status == GateStatus.ACCEPT
    assert "idgham_no_ghunnah_ل" in result.deltas


def test_gate_idgham_no_ghunnah_ra():
    gate = GateIdgham()
    segments = [
        consonant("م"),
        vowel("ِ", VowelKind.KASRA),
        consonant("ن"),
        vowel("ْ", VowelKind.SUKUN),
        consonant("ر"),
        vowel("َ", VowelKind.FATHA),
    ]

    result = gate.apply(segments)
    assert result.status == GateStatus.ACCEPT
    assert "idgham_no_ghunnah_ر" in result.deltas


def test_gate_idgham_no_change():
    gate = GateIdgham()
    segments = [
        consonant("م"),
        vowel("ِ", VowelKind.KASRA),
        consonant("ن"),
        vowel("ْ", VowelKind.SUKUN),
        consonant("ك"),
        vowel("ِ", VowelKind.KASRA),
    ]

    result = gate.apply(segments)
    assert result.status == GateStatus.ACCEPT
    assert result.deltas == []


def test_gate_idgham_multiple():
    gate = GateIdgham()
    segments = [
        consonant("م"),
        vowel("ِ", VowelKind.KASRA),
        consonant("ن"),
        vowel("ْ", VowelKind.SUKUN),
        consonant("ي"),
        vowel("َ", VowelKind.FATHA),
        consonant("م"),
        vowel("ِ", VowelKind.KASRA),
        consonant("ن"),
        vowel("ْ", VowelKind.SUKUN),
        consonant("ل"),
        vowel("َ", VowelKind.FATHA),
    ]

    result = gate.apply(segments)
    assert result.status == GateStatus.ACCEPT
    assert len(result.deltas) == 2
    assert any("idgham_ghunnah" in d for d in result.deltas)
    assert any("idgham_no_ghunnah" in d for d in result.deltas)
