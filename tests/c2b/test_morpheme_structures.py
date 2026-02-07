"""Tests for Phase 3 morphology data structures."""

import pytest

from fvafk.c2b.morpheme import (
    Affix,
    Morpheme,
    MorphologicalAnalysis,
    Pattern,
    Root,
    RootType,
)


def test_root_requires_single_characters():
    with pytest.raises(ValueError):
        Root(letters=("كَ", "ت", "ب"), root_type=RootType.TRILATERAL)


def test_pattern_matches_stem_lazily():
    pattern = Pattern(name="fa3al", template="CVC")
    assert pattern.matches("كتب")


def test_morpheme_description_includes_affixes():
    root = Root(letters=("ك", "ت", "ب"), root_type=RootType.TRILATERAL)
    pattern = Pattern(name="fa3il", template="C1C2iC3")
    suffix = Affix(text="ون", position="suffix", name="masc.pl")
    morpheme = Morpheme(root=root, pattern=pattern, stem="كاتب", affixes=[suffix], gloss="writer")

    desc = morpheme.describe()
    assert "Root: كتب" in desc
    assert "Affixes" in desc


def test_morphological_analysis_summary():
    root = Root(letters=("ك", "ت", "ب"), root_type=RootType.TRILATERAL)
    pattern = Pattern(name="fa3il", template="C1aC2iC3")
    morpheme = Morpheme(root=root, pattern=pattern, stem="كاتب")
    analysis = MorphologicalAnalysis(
        morpheme=morpheme,
        affix_sequence=[Affix(text="ون", position="suffix")],
        meaning_category="active participle",
    )

    summary = analysis.summary()
    assert "Root: كتب" in summary
    assert "AffixSeq: ون" in summary
