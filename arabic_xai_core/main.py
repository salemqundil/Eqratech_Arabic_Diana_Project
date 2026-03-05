"""
main.py — Arabic XAI Core Pipeline Entry Point.

Run directly:
    python arabic_xai_core/main.py
    python arabic_xai_core/main.py كَتَبَ
    python -m arabic_xai_core كَتَبَ
"""
from __future__ import annotations

import json
import sys

from .normalizer import normalize_text
from .grapheme_parser import parse_graphemes
from .composite_expander import expand_units
from .phonology_map import classify_phonounits
from .sline_core import build_sline_for_word
from .syllable_engine import build_syllables
from .weight_engine import extract_weight_units
from .lexicon_builtins import classify_mabni
from .morph_gate import analyze_morphology
from .prover import build_proof_report


def run_pipeline(word: str, mode: str = "orthographic", verbose: bool = False) -> dict:
    """
    Run the full 10-stage XAI pipeline on a single Arabic word.

    Returns ProofReport as dict.
    """
    # Stage 1: Normalize
    normalized = normalize_text(word, mode=mode)
    if verbose:
        print(f"[1] Normalized: {normalized.normalized_text!r}")
        print(f"    Log: {normalized.normalization_log}")

    # Stage 2: Parse graphemes
    clusters = parse_graphemes(normalized.normalized_text)
    if verbose:
        print(f"[2] Grapheme clusters: {[c.full for c in clusters]}")

    # Stage 3: Expand composites
    expanded = expand_units(clusters)
    if verbose:
        print(f"[3] Expanded units: {[(u.base_char, u.role) for u in expanded]}")

    # Stage 4: Classify phonology
    phono_units = classify_phonounits(expanded)
    if verbose:
        print(f"[4] Phono units: {[(p.symbol, p.unit_type) for p in phono_units]}")

    # Stage 5: Build S-Line graph
    sline_graph = build_sline_for_word(phono_units, word_index=0)
    if verbose:
        print(f"[5] S-Line nodes: {len(sline_graph.nodes)}, edges: {len(sline_graph.edges)}")

    # Stage 6: Build syllables
    syllable_analysis = build_syllables(sline_graph=sline_graph, phono_units=phono_units)
    if verbose:
        syllable_str = " | ".join(f"{s.pattern}({'✓' if s.is_valid else '✗'})"
                                   for s in syllable_analysis.syllables)
        print(f"[6] Syllables: {syllable_str}")

    # Stage 7: Extract weight units
    weight_analysis = extract_weight_units(syllable_analysis, sline_graph)
    if verbose:
        print(f"[7] Weight units (حامل): {weight_analysis.weight_unit_count}")
        print(f"    Valid weight: {weight_analysis.valid_weight}")

    # Stage 8: Classify builtins
    builtin_analysis = classify_mabni(word, sline_graph, weight_analysis)
    if verbose:
        print(f"[8] Mabni: {builtin_analysis.is_mabni} ({builtin_analysis.mabni_type})")

    # Stage 9: Morphological gate
    morph_analysis = analyze_morphology(
        normalized.normalized_text,
        sline_graph=sline_graph,
        weight_analysis=weight_analysis,
        builtin_analysis=builtin_analysis,
    )
    if verbose:
        print(f"[9] Root: {morph_analysis.root_candidate}, "
              f"Pattern: {morph_analysis.pattern_candidate}, "
              f"{morph_analysis.tri_or_quad}, {morph_analysis.mujarrad_or_mazid}")

    # Stage 10: Build proof report
    proof = build_proof_report(
        word=word,
        normalized=normalized,
        syllable_analysis=syllable_analysis,
        weight_analysis=weight_analysis,
        builtin_analysis=builtin_analysis,
        morph_analysis=morph_analysis,
        sline_graph=sline_graph,
    )
    if verbose:
        print(f"\n[10] PROOF REPORT for: {word}")
        print("=" * 60)
        for claim in proof.claims:
            print(f"  ◈ {claim.text}")
            print(f"    الحكم: {claim.verdict} (ثقة: {claim.confidence:.0%})")
            for step in claim.reasoning_steps:
                print(f"      → {step}")
        print(f"\n  الثقة الإجمالية: {proof.overall_confidence:.0%}")

    return proof.to_dict()


def main() -> None:
    """CLI entry point."""
    words = sys.argv[1:] if len(sys.argv) > 1 else ["كَتَبَ", "في", "هذا", "الكتابُ"]

    for word in words:
        print(f"\n{'='*60}")
        print(f"تحليل: {word}")
        print('='*60)
        result = run_pipeline(word, verbose=True)
        print("\nJSON:")
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
