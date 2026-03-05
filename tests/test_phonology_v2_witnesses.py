import json
import subprocess
import os
import sys


def test_cli_phonology_v2_witnesses_populated_and_has_long_vowel():
    """
    Regression: when --phonology-v2-witnesses is enabled, witnesses must not be empty.

    For كِتَاب we expect a madd/long vowel witness (ا -> V_LONG).
    """
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "fvafk.cli",
            "كِتَاب",
            "--json",
            "--phonology-v2",
            "--phonology-v2-details",
            "--phonology-v2-witnesses",
        ],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": "src"},
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)

    # Details flag ensures the per-word analysis is present.
    words = data["c2a"]["phonology_v2"]["words"]
    assert len(words) == 1
    w0 = words[0]
    assert w0["success"] is True
    assert w0["version"] == "2.0"

    witnesses = w0.get("witnesses", [])
    assert isinstance(witnesses, list)
    assert len(witnesses) > 0

    # Must include a long vowel witness for the alif in كِتَاب.
    assert any(
        (wi.get("grapheme") == "ا" and wi.get("role") == "V_LONG")
        for wi in witnesses
    )

