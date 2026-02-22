import unicodedata

import pytest

from fvafk.c1.form_codec_v2 import FormCodecV2, Inventory


@pytest.mark.parametrize(
    "text",
    [
        "",
        "مُّحَمَّدٌ رَّسُولُ اللَّهِ",
        "وَالَّذِينَ مَعَهُ",
        "آمَنُوا",
        "لِيَغِيظَ",
        "سِيمَاهُمْ",
        "طسم",
        "abc",  # non-arabic still reversible
        " ــ ",  # spaces + tatweel
    ],
)
def test_form_codec_v2_reversible_roundtrip(text: str):
    codec = FormCodecV2(Inventory(), keep_tatweel=True)
    fs = codec.encode(text)
    back = codec.decode(fs)
    assert back == unicodedata.normalize("NFC", text)
    assert fs.decode() == back
    assert fs.original_nfc == back


def test_form_codec_v2_stable_checksum_for_same_input():
    codec = FormCodecV2(keep_tatweel=True)
    a = codec.encode("آمَنُوا")
    b = codec.encode("آمَنُوا")
    assert a.checksum == b.checksum

