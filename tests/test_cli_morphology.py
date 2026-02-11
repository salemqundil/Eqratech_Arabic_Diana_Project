"""Tests for CLI morphology integration."""

import json
import subprocess
import sys


class TestCLIMorphologyIntegration:
    def test_morphology_active_participle(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fvafk.cli",
                "كَاتِبٌ",
                "--morphology",
                "--json"
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"}
        )

        assert result.returncode == 0

        data = json.loads(result.stdout)

        assert "c2b" in data
        assert "root" in data["c2b"]
        assert "pattern" in data["c2b"]

        root = data["c2b"]["root"]
        assert root["letters"] == ["ك", "ت", "ب"]
        assert root["type"] == "trilateral"
        assert root["formatted"] == "ك-ت-ب"

        pattern = data["c2b"]["pattern"]
        assert pattern["template"] == "فَاعِل"
        assert pattern["type"] == "active_participle"
        assert pattern["category"] == "noun"

    def test_morphology_form_ii_verb(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fvafk.cli",
                "عَلَّمَ",
                "--morphology",
                "--json"
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"}
        )

        assert result.returncode == 0

        data = json.loads(result.stdout)

        root = data["c2b"]["root"]
        assert root["letters"] == ["ع", "ل", "م"]

        pattern = data["c2b"]["pattern"]
        assert pattern["type"] == "form_ii"
        assert pattern["category"] == "verb"

    def test_morphology_passive_participle(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fvafk.cli",
                "مَكْتُوب",
                "--morphology",
                "--json"
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"}
        )

        assert result.returncode == 0

        data = json.loads(result.stdout)

        root = data["c2b"]["root"]
        assert root["letters"] == ["ك", "ت", "ب"]

        pattern = data["c2b"]["pattern"]
        assert pattern["type"] == "passive_participle"

    def test_without_morphology_flag(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fvafk.cli",
                "كَاتِبٌ",
                "--json"
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"}
        )

        assert result.returncode == 0

        data = json.loads(result.stdout)

        assert "c2b" not in data
        assert "c1" in data
        assert "c2a" in data

    def test_morphology_performance(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fvafk.cli",
                "كَاتِبٌ",
                "--morphology",
                "--json"
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"}
        )

        assert result.returncode == 0

        data = json.loads(result.stdout)

        assert "c2b_time_ms" in data["stats"]
        assert data["stats"]["c2b_time_ms"] < 10.0

    def test_plural_aa_hamza_root_patch_ashidda(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fvafk.cli",
                "أَشِدَّاءُ",
                "--morphology",
                "--json",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["c2b"]["kind"] == "noun"
        assert data["c2b"]["root"]["letters"] == ["ش", "د", "د"]
        # Template marker is forced when the patch is applied.
        assert data["c2b"]["pattern"]["template"] == "فُعَلَاءُ"
        assert data["c2b"]["pattern"]["type"] == "broken_plural_fu3alaa"

    def test_form_iv_present_yu3jibu_not_unknown(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fvafk.cli",
                "يُعْجِبُ",
                "--morphology",
                "--json",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["c2b"]["kind"] == "verb"
        assert data["c2b"]["pattern"]["template"] == "يُفْعِلُ"
        assert data["c2b"]["pattern"]["type"] == "form_iv"

    def test_taraahum_defective_raaa_pattern_override(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fvafk.cli",
                "تَرَاهُمْ",
                "--morphology",
                "--json",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"},
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["c2b"]["kind"] == "verb"
        assert data["c2b"]["root"]["letters"] == ["ر", "أ", "ي"]
        assert data["c2b"]["pattern"]["template"] == "تَفْعَلُ"
        assert data["c2b"]["pattern"]["type"] == "form_i"


class TestCLIMorphologyHumanReadable:
    def test_human_readable_output(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fvafk.cli",
                "كَاتِبٌ",
                "--morphology"
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": "src"}
        )

        assert result.returncode == 0

        output = result.stdout

        assert "Phase C2b (Morphology)" in output
        assert "Root:" in output
        assert "ك-ت-ب" in output
        assert "Pattern:" in output
        assert "فَاعِل" in output
