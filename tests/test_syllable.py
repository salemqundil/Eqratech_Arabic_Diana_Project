import pytest

from fvafk.c2a.syllable import Segment, SegmentKind, Syllable, SyllableType


def _make_consonant(letter: str) -> Segment:
    return Segment(text=letter, kind=SegmentKind.CONSONANT)


def _make_vowel(letter: str) -> Segment:
    return Segment(text=letter, kind=SegmentKind.VOWEL)


def test_syllable_happy_path():
    syllable = Syllable(
        onset=[_make_consonant("ب")],
        nucleus=_make_vowel("ا"),
        coda=[],
        type=SyllableType.CV,
    )
    assert syllable.is_open()
    assert not syllable.is_closed()
    assert not syllable.is_heavy()


def test_syllable_heavy():
    syllable = Syllable(
        onset=[_make_consonant("ك")],
        nucleus=_make_vowel("ي"),
        coda=[_make_consonant("ت")],
        type=SyllableType.CVC,
    )
    assert syllable.is_heavy()


def test_syllable_rejects_non_vowel_nucleus():
    with pytest.raises(ValueError):
        Syllable(
            onset=[_make_consonant("ب")],
            nucleus=_make_consonant("ب"),
            coda=[],
            type=SyllableType.CV,
        )
