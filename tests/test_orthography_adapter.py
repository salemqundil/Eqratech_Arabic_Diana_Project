from fvafk.orthography_adapter import OrthographyAdapter


def test_orthography_adapter_normalizes_hamza_variants():
    adapter = OrthographyAdapter()
    # strip_diacritics=True for test expectation (adapter default preserves diacritics)
    assert adapter.normalize("ٱلْكِتَابُ", strip_diacritics=True) == "الكتاب"


def test_orthography_adapter_replaces_ta_marbuta_and_alif_maqsura():
    adapter = OrthographyAdapter()
    assert adapter.normalize("مَدِينَةٌ هَذِهِ هَذِهِ", strip_diacritics=True) == "مدينتن هذه هذه"


def test_orthography_adapter_tanwin_collapses_to_noon():
    adapter = OrthographyAdapter()
    assert adapter.normalize("كِتَابٌ مَدِينَةٍ", strip_diacritics=True) == "كتابن مدينتن"
