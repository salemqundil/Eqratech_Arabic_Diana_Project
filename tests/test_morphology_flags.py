"""Tests for morphology_flags: MorphologyFlags, MorphologyFlagsExtractor, extract_morphology_flags."""

import pytest
from fvafk.c2b.morphology_flags import (
    MorphologyFlags,
    MorphologyFlagsExtractor,
    extract_morphology_flags,
)


def test_morphology_flags_default():
    flags = MorphologyFlags()
    assert flags.case is None
    assert flags.number is None
    assert flags.gender is None
    assert flags.definiteness is False
    assert flags.confidence == 0.0


def test_extract_morphology_flags_convenience():
    flags = extract_morphology_flags("الْكِتَابُ")
    assert flags.definiteness is True
    assert flags.case == "nominative"
    assert flags.number == "singular"
    assert flags.gender == "masculine"
    assert 0 <= flags.confidence <= 1.0


def test_definiteness():
    extractor = MorphologyFlagsExtractor()
    assert extractor.extract("الكتاب").definiteness is True
    assert extractor.extract("الْكِتَابُ").definiteness is True
    assert extractor.extract("كتاب").definiteness is False
    assert extractor.extract("كِتَابٌ").definiteness is False


def test_case_tanwin():
    extractor = MorphologyFlagsExtractor()
    assert extractor.extract("كِتَابٌ").case == "nominative"
    assert extractor.extract("كِتَابًا").case == "accusative"
    assert extractor.extract("كِتَابٍ").case == "genitive"


def test_case_short_vowels():
    extractor = MorphologyFlagsExtractor()
    assert extractor.extract("كِتَابُ").case == "nominative"
    assert extractor.extract("كِتَابَ").case == "accusative"
    assert extractor.extract("كِتَابِ").case == "genitive"


def test_number_singular_dual_plural():
    extractor = MorphologyFlagsExtractor()
    assert extractor.extract("كِتَابٌ").number == "singular"
    assert extractor.extract("كِتَابَانِ").number == "dual"
    assert extractor.extract("مُعَلِّمُونَ").number == "plural"
    assert extractor.extract("مُعَلِّمَاتٌ").number == "plural"


def test_gender():
    extractor = MorphologyFlagsExtractor()
    assert extractor.extract("كِتَابٌ").gender == "masculine"
    assert extractor.extract("مَدْرَسَةٌ").gender == "feminine"
    assert extractor.extract("مُعَلِّمَاتٌ").gender == "feminine"
    assert extractor.extract("سَمَاء").gender == "feminine"


def test_confidence_increases_with_features_and_diacritics():
    extractor = MorphologyFlagsExtractor()
    empty = extractor.extract("")
    no_diac = extractor.extract("كتاب")
    with_diac = extractor.extract("كِتَابٌ")
    full = extractor.extract("الْكِتَابُ")
    assert empty.confidence == 0.0
    assert no_diac.confidence <= with_diac.confidence
    assert with_diac.confidence <= full.confidence
    assert full.confidence <= 1.0


def test_empty_and_whitespace():
    extractor = MorphologyFlagsExtractor()
    for word in ["", "   ", "\t"]:
        flags = extractor.extract(word)
        assert flags.case is None
        assert flags.definiteness is False
        assert flags.confidence == 0.0


def test_strip_definite_article_used_internally():
    extractor = MorphologyFlagsExtractor()
    flags_al = extractor.extract("الْكِتَابُ")
    flags_no_al = extractor.extract("كِتَابُ")
    assert flags_al.case == flags_no_al.case == "nominative"
    assert flags_al.definiteness is True
    assert flags_no_al.definiteness is False
