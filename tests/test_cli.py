"""Basic tests for the Phase 2 CLI."""

import json

from fvafk.cli.main import MinimalCLI


def test_cli_basic_runs():
    cli = MinimalCLI(verbose=False, json_output=False)
    result = cli.process("كِتابٌ")

    assert result["success"]
    assert result["c1"]["num_units"] > 0
    assert "gates" in result["c2a"]
    assert "stats" in result


def test_cli_verbose_includes_units():
    cli = MinimalCLI(verbose=True, json_output=False)
    result = cli.process("ذَهَبَ")

    assert result["success"]
    assert isinstance(result["c1"]["units"], list)


def test_cli_json_output_serializable():
    cli = MinimalCLI(verbose=False, json_output=True)
    result = cli.process("الْحَمْدُ لِلَّهِ")

    json.dumps(result, ensure_ascii=False)
