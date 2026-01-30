"""
Minimal CLI for Phase 2 phonological gates.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Dict, List, Optional

from fvafk.c2a.gate_framework import GateStatus
from fvafk.c2a.gates.gate_deletion import GateDeletion
from fvafk.c2a.gates.gate_epenthesis import GateEpenthesis
from fvafk.c2a.gates.gate_hamza import GateHamza
from fvafk.c2a.gates.gate_idgham import GateIdgham
from fvafk.c2a.gates.gate_madd import GateMadd
from fvafk.c2a.gates.gate_shadda import GateShadda
from fvafk.c2a.gates.gate_sukun import GateSukun
from fvafk.c2a.gates.gate_waqf import GateWaqf
from fvafk.c2a.syllable import (
    Segment,
    SegmentKind,
    Syllable,
    SyllableType,
    VowelKind,
)
from fvafk.orthography_adapter import OrthographyAdapter


HARAKAT_TO_VK: Dict[str, VowelKind] = {
    "َ": VowelKind.FATHA,
    "ُ": VowelKind.DAMMA,
    "ِ": VowelKind.KASRA,
    "ْ": VowelKind.SUKUN,
    "ّ": VowelKind.SHADDA,
    "ً": VowelKind.TANWIN_FATH,
    "ٌ": VowelKind.TANWIN_DAMM,
    "ٍ": VowelKind.TANWIN_KASR,
}


class SimpleTextEncoder:
    """Very simple encoder that maps Arabic characters to CV segments."""

    def __init__(self) -> None:
        self.adapter = OrthographyAdapter()

    def encode(self, text: str) -> List[Segment]:
        segments: List[Segment] = []
        for char in text:
            if char.isspace():
                continue
            if char in HARAKAT_TO_VK:
                segments.append(
                    Segment(
                        text=char,
                        kind=SegmentKind.VOWEL,
                        vk=HARAKAT_TO_VK[char],
                    )
                )
                continue
            normalized = self.adapter.normalize(char)
            if not normalized:
                continue
            segments.append(Segment(text=normalized, kind=SegmentKind.CONSONANT))
        return segments


class SimpleSyllabifier:
    """Naive syllable builder for CLI reporting."""

    def syllabify(self, segments: List[Segment]) -> Optional[List[Syllable]]:
        syllables: List[Syllable] = []
        i = 0
        while i < len(segments):
            onset: List[Segment] = []
            while i < len(segments) and segments[i].kind == SegmentKind.CONSONANT:
                onset.append(segments[i])
                i += 1
            if i >= len(segments) or segments[i].kind != SegmentKind.VOWEL:
                break
            nucleus = segments[i]
            i += 1
            coda: List[Segment] = []
            while i < len(segments) and segments[i].kind == SegmentKind.CONSONANT:
                coda.append(segments[i])
                i += 1
            syllables.append(
                Syllable(
                    onset=onset,
                    nucleus=nucleus,
                    coda=coda,
                    type=self._guess_type(coda),
                )
            )
        return syllables if syllables else None

    def _guess_type(self, coda: List[Segment]) -> SyllableType:
        if not coda:
            return SyllableType.CV
        if len(coda) == 1:
            return SyllableType.CVC
        if len(coda) == 2:
            return SyllableType.CVCC
        return SyllableType.CVVCC


class MinimalCLI:
    """Minimal CLI for running Phase 2 gates."""

    def __init__(self, verbose: bool = False, json_output: bool = False) -> None:
        self.verbose = verbose
        self.json_output = json_output
        self.encoder = SimpleTextEncoder()
        self.syllabifier = SimpleSyllabifier()
        self.gates = [
            GateSukun(),
            GateShadda(),
            GateHamza(),
            GateWaqf(),
            GateIdgham(),
            GateMadd(),
            GateDeletion(),
            GateEpenthesis(),
        ]

    def process(self, text: str) -> Dict[str, object]:
        result: Dict[str, object] = {
            "input": text,
            "success": False,
            "c1": {},
            "c2a": {},
            "stats": {},
        }
        start = time.time()

        try:
            c1_start = time.time()
            units = self.encoder.encode(text)
            c1_time = (time.time() - c1_start) * 1000

            result["c1"] = {
                "num_units": len(units),
                "units": [self._unit_to_dict(u) for u in units] if self.verbose else None,
            }

            current = units
            gate_results: List[Dict[str, object]] = []
            c2a_start = time.time()

            for gate in self.gates:
                gate_start = time.time()
                gate_result = gate.apply(current)
                gate_time = (time.time() - gate_start) * 1000

                info = {
                    "gate_id": gate.gate_id,
                    "status": gate_result.status.name,
                    "time_ms": gate_time,
                    "deltas": len(gate_result.deltas),
                    "reason": gate_result.reason if self.verbose else None,
                }
                gate_results.append(info)

                if gate_result.status == GateStatus.REJECT:
                    result["c2a"] = {
                        "gates": gate_results,
                        "reject_reason": gate_result.reason,
                        "rejected_at": gate.gate_id,
                    }
                    break

                current = gate_result.output

            else:
                result["c2a"]["gates"] = gate_results
                syllables = self.syllabifier.syllabify(current)
                if syllables is None:
                    result["c2a"]["reject_reason"] = "syllabification_failed"
                else:
                    result["c2a"]["syllables"] = {
                        "count": len(syllables),
                        "syllables": [self._syllable_to_dict(s) for s in syllables]
                        if self.verbose
                        else None,
                    }

            result["stats"] = {
                "c1_time_ms": c1_time,
                "c2a_time_ms": (time.time() - c2a_start) * 1000 if current else 0,
                "total_time_ms": (time.time() - start) * 1000,
                "gates_count": len(self.gates),
            }

            result["success"] = True

        except Exception as exc:
            result["error"] = str(exc)
            result["exception"] = type(exc).__name__

        return result

    def _unit_to_dict(self, unit: Segment) -> Dict[str, Optional[str]]:
        return {
            "text": unit.text,
            "kind": unit.kind.name,
            "vk": unit.vk.name if unit.vk else None,
        }

    def _syllable_to_dict(self, syllable: Syllable) -> Dict[str, object]:
        return {
            "type": syllable.type.name,
            "onset": [seg.text for seg in syllable.onset],
            "nucleus": syllable.nucleus.text,
            "coda": [seg.text for seg in syllable.coda],
        }

    def print_result(self, result: Dict[str, object]) -> None:
        if self.json_output:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return

        print("\n" + "=" * 60)
        print("📊 FVAFK Phase 2 Analysis")
        print("=" * 60)
        print(f"\n📝 Input: {result['input']}")

        if result.get("error"):
            print(f"\n❌ Error: {result['error']}")
            return

        c1 = result["c1"]
        print(f"\n🔤 C1 (Text Encoding):")
        print(f"   Units: {c1['num_units']}")
        if self.verbose and c1.get("units"):
            print(f"   Visible units: {len(c1['units'])}")

        c2a = result["c2a"]
        print(f"\n🎵 C2a (Phonological Gates):")
        if "reject_reason" in c2a:
            print(f"   ❌ Rejected at {c2a['rejected_at']}")
            print(f"   Reason: {c2a['reject_reason']}")
        else:
            print(f"   ✅ All {len(c2a.get('gates', []))} gates passed")
            if c2a.get("syllables"):
                print(f"   Syllables: {c2a['syllables']['count']}")

        stats = result["stats"]
        print(f"\n⏱️  Performance:")
        print(f"   C1 time: {stats['c1_time_ms']:.2f}ms")
        print(f"   C2a time: {stats['c2a_time_ms']:.2f}ms")
        print(f"   Total: {stats['total_time_ms']:.2f}ms")

        print("\n✅ Analysis complete!")
        print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="FVAFK Minimal CLI - Phase 2 Phonological Gates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("text", type=str, help="Arabic text to analyze")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show intermediate data")
    parser.add_argument("-j", "--json", action="store_true", help="JSON output")

    args = parser.parse_args()
    cli = MinimalCLI(verbose=args.verbose, json_output=args.json)
    result = cli.process(args.text)
    cli.print_result(result)
    sys.exit(0 if result["success"] else 1)
