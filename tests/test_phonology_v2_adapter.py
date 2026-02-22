import os


def test_phonology_v2_adapter_basic_cv():
    # Ensure imports behave like pytest (pythonpath=src)
    os.environ.setdefault("PYTHONPATH", "src")

    from fvafk.phonology_v2.phonology_adapter import PhonologyV2Adapter

    adapter = PhonologyV2Adapter()
    r = adapter.analyze_word("كِتَاب")
    assert r["success"] is True
    assert r["cv_pattern"] == "CVCVVC"


def test_phonology_v2_adapter_syllables():
    from fvafk.phonology_v2.phonology_adapter import PhonologyV2Adapter

    adapter = PhonologyV2Adapter()
    r = adapter.analyze_word("مَدْرَسَة")
    assert r["success"] is True
    assert r["syllable_count"] >= 2

