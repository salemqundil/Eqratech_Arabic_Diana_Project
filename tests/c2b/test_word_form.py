from fvafk.c2b.word_form import PartOfSpeech, WordFormBuilder


def test_word_form_builder_content_word_from_multi_word_item():
    item = {
        "word": "كِتَاب",
        "span": {"start": 0, "end": 5},
        "kind": "noun",
        "root": {"letters": ["ك", "ت", "ب"], "formatted": "ك-ت-ب", "type": "trilateral", "length": 3},
        "pattern": {
            "template": "فِعَال",
            "type": "verbal_noun",
            "category": "noun",
            "features": {"pattern_type": "VERBAL_NOUN", "category": "noun", "confidence": "0.75"},
        },
        "affixes": {"prefix": None, "suffix": None, "normalized": "كتاب", "stripped": "كتاب"},
        "features": {"kind": "noun", "definite": None, "number": "singular", "gender": "unknown", "case": None},
    }

    wf = WordFormBuilder().from_c2b(item)
    assert wf.surface == "كِتَاب"
    assert wf.pos == PartOfSpeech.NOUN
    assert wf.span is not None and wf.span.start == 0 and wf.span.end == 5
    assert wf.root is not None and wf.root.formatted == "ك-ت-ب"
    assert wf.pattern is not None and wf.pattern.template == "فِعَال"



def test_word_form_builder_operator_item_allows_missing_root_pattern():
    item = {
        "word": "مِنْ",
        "span": {"start": 0, "end": 3},
        "kind": "operator",
        "operator": {"operator": "من", "category": "PREP", "source_path": "builtin"},
        "root": None,
        "pattern": None,
    }
    wf = WordFormBuilder().from_c2b(item)
    assert wf.pos == PartOfSpeech.UNKNOWN
    assert wf.root is None
    assert wf.pattern is None


