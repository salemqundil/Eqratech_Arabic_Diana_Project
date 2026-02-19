import json
import subprocess
import sys


def test_cli_phonology_v2_flag_runs_and_sets_engine():
    result = subprocess.run(
        [sys.executable, "-m", "fvafk.cli", "كِتَاب يَوْم قَوْل", "--json", "--phonology-v2"],
        capture_output=True,
        text=True,
        env={"PYTHONPATH": "src"},
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["c1"]["cv_analysis"]["engine"] == "phonology_v2"
    assert isinstance(data["c1"]["cv_analysis"]["words"], list)


def test_cli_phonology_v2_details_field():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "fvafk.cli",
            "كِتَاب يَوْم قَوْل",
            "--json",
            "--phonology-v2",
            "--phonology-v2-details",
        ],
        capture_output=True,
        text=True,
        env={"PYTHONPATH": "src"},
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["c1"]["cv_analysis"]["engine"] == "phonology_v2"
    assert "phonology_v2" in data["c2a"]
    assert data["c2a"]["phonology_v2"]["total_words_analyzed"] >= 1

