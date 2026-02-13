"""
FVAFK Phonology V2 Adapter
=========================

Provides a small compatibility layer that returns dict-shaped outputs (easy to
embed into CLI JSON) while using the Phonology V2 syllable-lattice engine.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Optional

from . import analyze_word as _analyze_word
from .phonology_utils import format_syllabification


class PhonologyV2Adapter:
    def __init__(self) -> None:
        self.version = "2.0"

    def analyze_word(self, word: str) -> Dict[str, Any]:
        try:
            wa = _analyze_word(word, verbose=False)
            best = wa.best_syllabification
            if not best or not wa.cv_pattern:
                return {
                    "word": word,
                    "cv_pattern": "",
                    "syllables": [],
                    "syllabification": "",
                    "syllable_count": 0,
                    "success": False,
                    "error": "no_valid_syllabification",
                    "version": self.version,
                }

            syllabification = format_syllabification(best)
            syllables = [getattr(s, "surface", "") for s in best]

            witnesses: List[Dict[str, Any]] = []
            for syl in best:
                for trace in getattr(syl, "vc_witnesses", []) or []:
                    witnesses.append(
                        {
                            "grapheme": trace.base,
                            "role": trace.decided_role.name,
                            "witness": trace.witness.name,
                            "need_nucleus": trace.need_nucleus,
                            "force_onset_c": trace.force_onset_c,
                        }
                    )

            return {
                "word": word,
                "cv_pattern": wa.cv_pattern,
                "syllables": syllables,
                "syllabification": syllabification,
                "syllable_count": len(best),
                "success": True,
                "witnesses": witnesses,
                "version": self.version,
            }
        except Exception as e:
            return {
                "word": word,
                "cv_pattern": "",
                "syllables": [],
                "syllabification": "",
                "syllable_count": 0,
                "success": False,
                "error": str(e),
                "version": self.version,
            }

    def get_cv_pattern(self, word: str) -> Optional[str]:
        r = self.analyze_word(word)
        return r["cv_pattern"] if r.get("success") else None

    def get_syllables(self, word: str) -> Optional[List[str]]:
        r = self.analyze_word(word)
        return r["syllables"] if r.get("success") else None


_phonology = PhonologyV2Adapter()


def analyze_word(word: str) -> Dict[str, Any]:
    return _phonology.analyze_word(word)


def get_cv_pattern(word: str) -> Optional[str]:
    return _phonology.get_cv_pattern(word)


def get_syllables(word: str) -> Optional[List[str]]:
    return _phonology.get_syllables(word)

