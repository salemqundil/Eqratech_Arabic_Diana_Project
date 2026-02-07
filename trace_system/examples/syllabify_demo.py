#!/usr/bin/env python3
"""
SyllabifyGate Demo - Live Examples

Demonstrates:
1. Basic usage of SyllabifyGate
2. All syllable types (CV, CVC, CVV, CVVC, CVCC)
3. Multi-token transitions
4. Weight calculation
"""

import sys
import json
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gates.syllabify_gate import (
    syllabify_phoneme_stream,
    SyllableType,
    SyllableWeight,
    GateStatus
)


def demo_basic_syllables():
    """Demo: T-01 to T-04 - All syllable types"""
    print("=" * 60)
    print("DEMO 1: Basic Syllable Types (T-01 to T-04)")
    print("=" * 60)
    
    examples = [
        {
            "name": "T-01: CV (Light) - ما",
            "phonemes": [
                {"type": "C", "sym": "m", "features": []},
                {"type": "V", "sym": "a", "features": ["VF_LN_001"]}
            ]
        },
        {
            "name": "T-02: CVC (Heavy) - من",
            "phonemes": [
                {"type": "C", "sym": "m", "features": []},
                {"type": "V", "sym": "a", "features": ["VF_LN_001"]},
                {"type": "C", "sym": "n", "features": []}
            ]
        },
        {
            "name": "T-03: CVV (Heavy) - ما (long)",
            "phonemes": [
                {"type": "C", "sym": "m", "features": []},
                {"type": "V", "sym": "aa", "features": ["VF_LN_002"]}
            ]
        },
        {
            "name": "T-04a: CVVC (Superheavy) - مان",
            "phonemes": [
                {"type": "C", "sym": "m", "features": []},
                {"type": "V", "sym": "aa", "features": ["VF_LN_002"]},
                {"type": "C", "sym": "n", "features": []}
            ]
        },
        {
            "name": "T-04b: CVCC (Superheavy) - بنت",
            "phonemes": [
                {"type": "C", "sym": "b", "features": []},
                {"type": "V", "sym": "i", "features": ["VF_LN_001"]},
                {"type": "C", "sym": "n", "features": []},
                {"type": "C", "sym": "t", "features": []}
            ]
        }
    ]
    
    for ex in examples:
        phoneme_stream = [{"token_id": 0, "surface": "test", "phonemes": ex["phonemes"]}]
        result = syllabify_phoneme_stream(phoneme_stream)
        
        print(f"\n{ex['name']}")
        if result.status == GateStatus.OK and result.syllabification:
            syll = result.syllabification[0].syllables[0]
            print(f"  Type: {syll.type.value}")
            print(f"  Weight: {syll.weight.value}")
            print(f"  Structure: {syll}")
            print(f"  Feature ID: {syll.feature_id}")
        else:
            print(f"  ERROR: {result.warnings}")


def demo_multi_syllable():
    """Demo: Multi-syllable words"""
    print("\n" + "=" * 60)
    print("DEMO 2: Multi-Syllable Words")
    print("=" * 60)
    
    examples = [
        {
            "name": "كتب → ka-ta-ba (CV-CV-CV)",
            "phonemes": [
                {"type": "C", "sym": "k", "features": []},
                {"type": "V", "sym": "a", "features": ["VF_LN_001"]},
                {"type": "C", "sym": "t", "features": []},
                {"type": "V", "sym": "a", "features": ["VF_LN_001"]},
                {"type": "C", "sym": "b", "features": []},
                {"type": "V", "sym": "a", "features": ["VF_LN_001"]}
            ]
        },
        {
            "name": "مدرسة → mad-ra-sa (CVC-CV-CV)",
            "phonemes": [
                {"type": "C", "sym": "m", "features": []},
                {"type": "V", "sym": "a", "features": ["VF_LN_001"]},
                {"type": "C", "sym": "d", "features": []},
                {"type": "C", "sym": "r", "features": []},
                {"type": "V", "sym": "a", "features": ["VF_LN_001"]},
                {"type": "C", "sym": "s", "features": []},
                {"type": "V", "sym": "a", "features": ["VF_LN_001"]}
            ]
        }
    ]
    
    for ex in examples:
        phoneme_stream = [{"token_id": 0, "surface": "test", "phonemes": ex["phonemes"]}]
        result = syllabify_phoneme_stream(phoneme_stream)
        
        print(f"\n{ex['name']}")
        if result.status == GateStatus.OK and result.syllabification:
            token_syll = result.syllabification[0]
            print(f"  Syllable count: {token_syll.syllable_count}")
            print(f"  Total weight: {token_syll.total_weight}")
            print(f"  Syllables:")
            for i, syll in enumerate(token_syll.syllables, 1):
                print(f"    {i}. {syll.type.value} ({syll.weight.value}) - {syll}")
        else:
            print(f"  ERROR: {result.warnings}")


def demo_transitions():
    """Demo: T-06 - Transitions between tokens"""
    print("\n" + "=" * 60)
    print("DEMO 3: T-06 - Transitions Between Tokens")
    print("=" * 60)
    
    phoneme_stream = [
        {
            "token_id": 0,
            "surface": "من",
            "phonemes": [
                {"type": "C", "sym": "m", "features": []},
                {"type": "V", "sym": "a", "features": ["VF_LN_001"]},
                {"type": "C", "sym": "n", "features": []}
            ]
        },
        {
            "token_id": 1,
            "surface": "يكذب",
            "phonemes": [
                {"type": "C", "sym": "y", "features": []},
                {"type": "V", "sym": "a", "features": ["VF_LN_001"]},
                {"type": "C", "sym": "k", "features": []},
                {"type": "V", "sym": "dh", "features": ["VF_LN_001"]},
                {"type": "C", "sym": "dh", "features": []},
                {"type": "V", "sym": "i", "features": ["VF_LN_001"]},
                {"type": "C", "sym": "b", "features": []}
            ]
        },
        {
            "token_id": 2,
            "surface": "يعاقب",
            "phonemes": [
                {"type": "C", "sym": "y", "features": []},
                {"type": "V", "sym": "u", "features": ["VF_LN_001"]},
                {"type": "C", "sym": "ʕ", "features": []},
                {"type": "V", "sym": "aa", "features": ["VF_LN_002"]},
                {"type": "C", "sym": "q", "features": []},
                {"type": "V", "sym": "a", "features": ["VF_LN_001"]},
                {"type": "C", "sym": "b", "features": []}
            ]
        }
    ]
    
    result = syllabify_phoneme_stream(phoneme_stream)
    
    print(f"\nInput: من يكذب يعاقب")
    print(f"Status: {result.status.value}")
    print(f"\nSyllabification:")
    
    for token_syll in result.syllabification:
        print(f"\n  Token {token_syll.token_id}:")
        for i, syll in enumerate(token_syll.syllables, 1):
            print(f"    {i}. {syll.type.value:8s} ({syll.weight.value:12s}) - {syll}")
    
    print(f"\nTransitions ({len(result.transitions)} total):")
    for trans in result.transitions:
        print(f"  Token {trans.between['from_token']} → {trans.between['to_token']}")
        print(f"    Pattern: {trans.pattern['left']} → {trans.pattern['right']}")
        print(f"    Decision: {trans.decision.value}")
        print(f"    Notes: {', '.join(trans.notes)}")


def demo_json_output():
    """Demo: JSON output for storage"""
    print("\n" + "=" * 60)
    print("DEMO 4: JSON Output (ready for database)")
    print("=" * 60)
    
    phoneme_stream = [{
        "token_id": 0,
        "surface": "من",
        "phonemes": [
            {"type": "C", "sym": "m", "features": ["CF_PL_001"]},
            {"type": "V", "sym": "a", "features": ["VF_LN_001"]},
            {"type": "C", "sym": "n", "features": ["CF_PL_004"]}
        ]
    }]
    
    result = syllabify_phoneme_stream(phoneme_stream)
    
    # Convert to dict for JSON
    output = {
        "syllabification": [
            {
                "token_id": ts.token_id,
                "syllables": [
                    {
                        "type": s.type.value,
                        "onset": s.onset,
                        "nucleus": s.nucleus,
                        "coda": s.coda,
                        "weight": s.weight.value,
                        "feature_id": s.feature_id
                    }
                    for s in ts.syllables
                ]
            }
            for ts in result.syllabification
        ],
        "transitions": [
            {
                "between": t.between,
                "pattern": t.pattern,
                "decision": t.decision.value,
                "notes": t.notes
            }
            for t in result.transitions
        ],
        "status": result.status.value,
        "warnings": result.warnings
    }
    
    print("\nJSON Output:")
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    demo_basic_syllables()
    demo_multi_syllable()
    demo_transitions()
    demo_json_output()
    
    print("\n" + "=" * 60)
    print("✅ All demos completed successfully!")
    print("=" * 60)
