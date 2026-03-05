from fvafk.c1.cv_pattern import analyze_text_for_cv_after_phonology


def _cv_one(token: str, engine: str):
    r = analyze_text_for_cv_after_phonology(token, engine=engine)
    assert r["total_words_computed"] == 1
    assert len(r["words"]) == 1
    return r["words"][0]


def test_old_vs_new_cv_snapshot_small_set():
    """
    Phase 8.2 regression/snapshot: make c2a-vs-v2 differences explicit.

    Old = engine="c2a"
    New = engine="phonology_v2"
    """
    cases = {
        # Stable, expected to match.
        "كِتَاب": {
            "c2a": {"cv": "CVCVVC", "cv_advanced": "CViCVAC"},
            "phonology_v2": {"cv": "CVCVVC", "cv_advanced": "CViCVAC"},
        },
        "يَوْم": {
            "c2a": {"cv": "CVCC", "cv_advanced": "CVaCC"},
            "phonology_v2": {"cv": "CVCC", "cv_advanced": "CVaCC"},
        },
        # A known divergence: shadda/gemination handling differs between engines.
        "مُدَرِّس": {
            "c2a": {"cv": "CVCVCVC", "cv_advanced": "CVoCVaCViC"},
            "phonology_v2": {"cv": "CVCVCCVC", "cv_advanced": "CVoCVaCCViC"},
        },
    }

    for token, expected in cases.items():
        got_c2a = _cv_one(token, "c2a")
        got_v2 = _cv_one(token, "phonology_v2")
        assert got_c2a == expected["c2a"], (token, "c2a", got_c2a)
        assert got_v2 == expected["phonology_v2"], (token, "phonology_v2", got_v2)

