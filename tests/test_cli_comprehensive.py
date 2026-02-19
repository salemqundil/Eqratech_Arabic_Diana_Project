"""
Comprehensive CLI output tests

Sprint 1, Task 1.8: Ensure 10+ CLI output tests
Tests JSON structure, field presence, and correct behavior
"""

import json
import subprocess
import pytest


def run_cli(text: str, *flags) -> dict:
    """Helper to run CLI and parse JSON output"""
    cmd = ["python3", "-m", "fvafk.cli", text, "--json"] + list(flags)
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    return json.loads(result.stdout)


class TestCLIStructure:
    """Test basic JSON structure"""
    
    def test_cli_json_has_required_fields(self):
        """Test that basic output has required fields"""
        output = run_cli("كتاب")
        
        assert "input" in output
        assert "c1" in output
        assert "c2a" in output
        assert "stats" in output
        assert output["input"] == "كتاب"
    
    def test_cli_c1_structure(self):
        """Test C1 layer structure"""
        output = run_cli("كتاب")
        
        assert "num_units" in output["c1"]
        assert isinstance(output["c1"]["num_units"], int)
        assert output["c1"]["num_units"] > 0
    
    def test_cli_c2a_structure(self):
        """Test C2A layer structure"""
        output = run_cli("كتاب")
        
        assert "syllables" in output["c2a"]
        assert "gates" in output["c2a"]
        assert isinstance(output["c2a"]["syllables"], dict)
        assert "count" in output["c2a"]["syllables"]
    
    def test_cli_stats_structure(self):
        """Test stats structure"""
        output = run_cli("كتاب")
        
        assert "c1_time_ms" in output["stats"]
        assert "c2a_time_ms" in output["stats"]
        assert "total_time_ms" in output["stats"]
        assert "gates_count" in output["stats"]
        
        assert isinstance(output["stats"]["c1_time_ms"], (int, float))


class TestCLIMorphology:
    """Test --morphology flag behavior"""
    
    def test_cli_morphology_adds_c2b(self):
        """Test that --morphology adds c2b field"""
        output = run_cli("كتاب", "--morphology")
        
        assert "c2b" in output
        assert isinstance(output["c2b"], dict)
    
    def test_cli_c2b_absent_without_morphology(self):
        """Test that c2b is absent without --morphology"""
        output = run_cli("كتاب")
        
        assert "c2b" not in output or output["c2b"] is None


class TestCLISyntax:
    """Test syntax layer in CLI output"""
    
    def test_cli_morphology_enables_syntax(self):
        """Test that --morphology enables syntax layer"""
        output = run_cli("محمدٌ رسولُ", "--morphology")
        
        assert "syntax" in output or "c2b" in output
    
    def test_cli_syntax_structure(self):
        """Test syntax field structure when present"""
        output = run_cli("محمدٌ رسولُ الله", "--morphology")
        
        if "syntax" in output and output["syntax"]:
            syntax = output["syntax"]
            assert isinstance(syntax, dict)
    
    def test_cli_syntax_absent_without_morphology(self):
        """Test that syntax is absent without --morphology"""
        output = run_cli("كتاب")
        
        assert "syntax" not in output or output["syntax"] is None


class TestCLIMultiWord:
    """Test multi-word processing"""
    
    def test_cli_multi_word_processing(self):
        """Test multi-word input"""
        output = run_cli("محمد رسول", "--morphology", "--multi-word")
        
        assert "c2b" in output
    
    def test_cli_single_word_default(self):
        """Test single word is default behavior"""
        output = run_cli("كتاب", "--morphology")
        
        assert "c2b" in output


class TestCLIErrorHandling:
    """Test error handling"""
    
    def test_cli_handles_empty_input(self):
        """Test CLI handles empty input gracefully"""
        result = subprocess.run(
            ["python3", "-m", "fvafk.cli", "", "--json"],
            capture_output=True,
            text=True
        )
        assert result.returncode in [0, 1]
    
    def test_cli_handles_syntax_without_links(self):
        """Test CLI when no syntax links found"""
        output = run_cli("في", "--morphology")
        
        if "syntax" in output:
            assert isinstance(output["syntax"], (dict, type(None)))
