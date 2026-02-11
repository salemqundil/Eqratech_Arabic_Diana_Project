from fvafk.c2b.word_boundary import WordBoundaryDetector


def test_word_boundary_tokens_and_spans_skip_quranic_marks():
    text = "وَإِن تَوَلَّوْا ۖ فَإِنَّمَا هُمْ فِي شِقَاقٍ"
    spans = WordBoundaryDetector().detect(text)

    tokens = [s.token for s in spans]
    assert tokens == ["وَإِن", "تَوَلَّوْا", "فَإِنَّمَا", "هُمْ", "فِي", "شِقَاقٍ"]

    for s in spans:
        assert text[s.start : s.end] == s.token


def test_word_boundary_empty_text():
    assert WordBoundaryDetector().detect("") == []

