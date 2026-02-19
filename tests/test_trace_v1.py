import unicodedata

import pytest

from fvafk.c1.form_codec_v2 import FormCodecV2
from fvafk.c1.trace_v1 import apply_gate_with_trace, encode_with_trace, replay


def _gate_drop_tatweel(stream, *, rule_id=None):
    # Example "gate": remove tatweel but keep reversibility at C1 layer via trace.
    # (In real usage you'd likely keep a reversible op log or keep original stream too.)
    text = stream.decode().replace("\u0640", "")
    codec = FormCodecV2(keep_tatweel=True)
    return codec.encode(text)


def _gate_normalize_alif_madda(stream, *, rule_id=None):
    # Example deterministic normalize: آ -> أا (toy example)
    text = stream.decode().replace("آ", "أا")
    codec = FormCodecV2(keep_tatweel=True)
    return codec.encode(text)


def test_trace_replay_roundtrip_with_registry():
    codec = FormCodecV2(keep_tatweel=True)
    original_text = "آمَنُوا ــ"
    fs0, tr = encode_with_trace(codec, original_text)

    fs1, tr = apply_gate_with_trace(fs0, tr, gate_id="DROP_TATWEEL", gate=_gate_drop_tatweel)
    fs2, tr = apply_gate_with_trace(fs1, tr, gate_id="NORM_ALIF_MADDA", gate=_gate_normalize_alif_madda)

    out = replay(
        fs0,
        tr,
        registry={
            "DROP_TATWEEL": _gate_drop_tatweel,
            "NORM_ALIF_MADDA": _gate_normalize_alif_madda,
        },
    )
    assert out.decode() == fs2.decode()


def test_trace_records_diffs():
    codec = FormCodecV2(keep_tatweel=True)
    fs0, tr = encode_with_trace(codec, "لِيَغِيظَ ــ")
    _, tr2 = apply_gate_with_trace(fs0, tr, gate_id="DROP_TATWEEL", gate=_gate_drop_tatweel)
    assert len(tr2.steps) == 1
    assert tr2.steps[0].gate_id == "DROP_TATWEEL"
    # diff should exist and include at least one non-equal opcode
    assert any(d.op != "equal" for d in tr2.steps[0].diff)

