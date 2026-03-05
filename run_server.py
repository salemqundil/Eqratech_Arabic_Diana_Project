#!/usr/bin/env python3
"""
Web server entry point (stub - web_app module planned for future release).

⚠️  IMPORTANT: The web_app module does NOT exist as of 2026-02-03.
See: .github/copilot-instructions.md (Known Pitfalls section)

Core functionality is fully available via:
  1. CLI: python -m fvafk.cli "كَاتِبٌ" --morphology
  2. Library: from engines import ...; from maqam_theory.gates import ...
  3. Grammar export: python export_full_multilayer_grammar_minimal.py
  4. Tests: pytest -v

Web API (FastAPI/Uvicorn) is planned; do not depend on this file for workflows.
"""

import sys
import argparse


def main():
    """Stub server entry point explaining non-existence of web_app module."""
    parser = argparse.ArgumentParser(
        description="Web server stub (not yet implemented)"
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    print("\n" + "="*70)
    print("❌ Web Server Module 'web_app' Does Not Exist")
    print("="*70)
    print("\n✓ Core functionality IS available via:")
    print("\n  1. FVAFK CLI Pipeline:")
    print("     python -m fvafk.cli 'كَاتِبٌ' --morphology")
    print("     python -m fvafk.cli 'كَاتِبٌ' --morphology --json --verbose")
    print("\n  2. Direct Python Imports:")
    print("     from engines.phonology import PhonemesEngine")
    print("     from engines.morphology import ActiveParticipleEngine")
    print("     from maqam_theory.gates import VocativeGate, DeclarativeGate")
    print("     from syntax_theory.structures import SyntacticInput, SyntacticGraph")
    print("\n  3. Grammar Export:")
    print("     python export_full_multilayer_grammar_minimal.py")
    print("     python Main_engine.py")
    print("\n  4. Test Suite:")
    print("     pytest -v")
    print("     pytest tests/c2b/ -v")
    print("     pytest tests/test_gate_*.py -v")
    print("\n📋 Web API is planned for Phase 3+")
    print("   See: ENHANCED_ROADMAP.md")
    print("   Architecture: 6-layer model, 66 engines, 12 Maqam gates")
    print("\n" + "="*70 + "\n")

    sys.exit(1)


if __name__ == "__main__":
    main()