from fvafk.c2b.morpheme import PatternType
from fvafk.c2b.word_classifier import WordClassifier, WordKind


class DummyOperators:
    def classify(self, token: str):
        if token == "في":
            return {"operator": "في", "token_bare": "في"}
        return None


class DummySpecial:
    def classify(self, token: str):
        if token == "ذَٰلِكَ":
            return {"token_bare": "ذلك", "kind": "demonstrative", "category": "DEMONSTRATIVE"}
        return None


def test_classifier_operator_via_injected_catalog():
    clf = WordClassifier(operators=DummyOperators(), special=DummySpecial())  # type: ignore[arg-type]
    res = clf.classify("في")
    assert res.kind == WordKind.OPERATOR
    assert res.operator and res.operator["operator"] == "في"


def test_classifier_detached_pronoun():
    clf = WordClassifier(operators=DummyOperators(), special=DummySpecial())  # type: ignore[arg-type]
    res = clf.classify("هُمْ")
    assert res.kind == WordKind.PRONOUN
    assert res.pronoun and res.pronoun["person"] == 3
    assert res.pronoun["number"] == "plural"


def test_classifier_verb_when_pattern_type_is_verb_form():
    clf = WordClassifier(operators=DummyOperators(), special=DummySpecial())  # type: ignore[arg-type]
    res = clf.classify("عَلَّمَ", pattern_type=PatternType.FORM_II)
    assert res.kind == WordKind.VERB


def test_classifier_demonstrative_from_special_catalog():
    clf = WordClassifier(operators=DummyOperators(), special=DummySpecial())  # type: ignore[arg-type]
    res = clf.classify("ذَٰلِكَ")
    assert res.kind == WordKind.DEMONSTRATIVE
    assert res.special and res.special["token_bare"] == "ذلك"


def test_classifier_prep_clitic_particle_builtin():
    clf = WordClassifier(operators=DummyOperators(), special=DummySpecial())  # type: ignore[arg-type]
    res = clf.classify("بِهِمْ")
    assert res.kind == WordKind.PARTICLE
    assert res.special
    assert res.special["category"] == "PREP_CLITIC"
    assert res.special["base"] == "ب"
    assert res.special["attached_pronoun"]["suffix"] == "هم"


def test_classifier_verb_from_suffix_wa():
    clf = WordClassifier(operators=DummyOperators(), special=DummySpecial())  # type: ignore[arg-type]
    res = clf.classify("آمَنُوا", prefix=None, suffix="وا")
    assert res.kind == WordKind.VERB


def test_classifier_verb_from_imperfect_prefix_and_plural_suffix():
    clf = WordClassifier(operators=DummyOperators(), special=DummySpecial())  # type: ignore[arg-type]
    res = clf.classify("يَبْتَغُونَ", prefix="ي", suffix="ون")
    assert res.kind == WordKind.VERB

