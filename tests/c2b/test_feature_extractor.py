from fvafk.c2b.features import extract_features
from fvafk.c2b.morpheme import Root, RootType
from fvafk.c2b.pattern_matcher import PatternMatcher
from fvafk.c2b.root_extractor import RootExtractor
from fvafk.c2b.word_classifier import WordKind


def test_features_definiteness_and_case_from_tanwin():
    extractor = RootExtractor()
    extraction = extractor.extract_with_affixes("الكِتَابٌ")

    feats = extract_features("الكِتَابٌ", extraction, None, WordKind.NOUN)
    assert feats["definite"] is True
    assert feats["case"] == "nominative"


def test_features_number_gender_case_from_suffix():
    extractor = RootExtractor()
    extraction = extractor.extract_with_affixes("كَاتِبُونَ")

    feats = extract_features("كَاتِبُونَ", extraction, None, WordKind.NOUN)
    assert feats["number"] == "plural"
    assert feats["gender"] == "masculine"
    assert feats["case"] == "nominative"


def test_features_attached_pronoun_from_extracted_suffix():
    extractor = RootExtractor()
    extraction = extractor.extract_with_affixes("كِتَابُهُ")
    feats = extract_features("كِتَابُهُ", extraction, None, WordKind.NOUN)
    assert feats.get("attached_pronoun") is not None
    assert feats["attached_pronoun"]["suffix"] == "ه"


def test_features_include_pattern_features_when_available():
    matcher = PatternMatcher()
    root = Root(letters=("ك", "ت", "ب"), root_type=RootType.TRILATERAL)
    pattern = matcher.match("كَاتِب", root)
    assert pattern is not None

    extractor = RootExtractor()
    extraction = extractor.extract_with_affixes("كَاتِب")
    feats = extract_features("كَاتِب", extraction, pattern, WordKind.NOUN)
    assert feats.get("pattern_type") is not None
    assert "confidence" in feats

