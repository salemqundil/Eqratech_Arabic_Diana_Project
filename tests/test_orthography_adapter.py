from fvafk.orthography_adapter import OrthographyAdapter


def test_orthography_adapter_normalizes_hamza_variants():
    adapter = OrthographyAdapter()
    assert adapter.normalize("ٱلْكِتَابُ") == "الكتاب"


def test_orthography_adapter_replaces_ta_marbuta_and_alif_maqsura():
    adapter = OrthographyAdapter()
    assert adapter.normalize("مَدِينَةٌ هَذِهِ هَذِهِ") == "مدينتن هذه هذه"


def test_orthography_adapter_tanwin_collapses_to_noon():
    adapter = OrthographyAdapter()
    assert adapter.normalize("كِتَابٌ مَدِينَةٍ") == "كتابن مدينتن"
