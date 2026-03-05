"""Tests for CLI morphology integration."""

import json
import subprocess
import os
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
            env={**os.environ, "PYTHONPATH": "src"}
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
            env={**os.environ, "PYTHONPATH": "src"}
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
            env={**os.environ, "PYTHONPATH": "src"}
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
            env={**os.environ, "PYTHONPATH": "src"}
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
            env={**os.environ, "PYTHONPATH": "src"}
        )

        assert result.returncode == 0

        data = json.loads(result.stdout)

        assert "c2b_time_ms" in data["stats"]
        assert data["stats"]["c2b_time_ms"] < 50.0

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
            env={**os.environ, "PYTHONPATH": "src"},
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
            env={**os.environ, "PYTHONPATH": "src"},
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
            env={**os.environ, "PYTHONPATH": "src"},
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["c2b"]["kind"] == "verb"
        assert data["c2b"]["root"]["letters"] == ["ر", "أ", "ي"]
        assert data["c2b"]["pattern"]["template"] == "تَفْعَلُ"
        assert data["c2b"]["pattern"]["type"] == "form_i"


class TestCLISyntaxOutput:
    """Sprint 1, Task #1.7 / PR-A: CLI outputs syntax when --morphology is set."""

    def test_morphology_json_includes_syntax_section(self):
        """With --morphology --json, result must include syntax.word_forms and syntax.links.isnadi."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fvafk.cli",
                "مُحَمَّدٌ رَسُولُ اللَّهِ",
                "--morphology",
                "--json",
            ],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": "src"},
            cwd=None,
        )
        assert result.returncode == 0, result.stderr or result.stdout
        data = json.loads(result.stdout)
        assert "syntax" in data
        syntax = data["syntax"]
        assert "word_forms" in syntax
        assert "links" in syntax
        assert isinstance(syntax["links"], dict)
        assert "isnadi" in syntax["links"]
        assert isinstance(syntax["links"]["isnadi"], list)

    def test_without_morphology_no_syntax(self):
        """Without --morphology, result must not include syntax."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fvafk.cli",
                "مُحَمَّدٌ رَسُولُ اللَّهِ",
                "--json",
            ],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": "src"},
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "syntax" not in data


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
            env={**os.environ, "PYTHONPATH": "src"}
        )

        assert result.returncode == 0

        output = result.stdout

        assert "Phase C2b (Morphology)" in output
        assert "Root:" in output
        assert "ك-ت-ب" in output
        assert "Pattern:" in output
        assert "فَاعِل" in output
