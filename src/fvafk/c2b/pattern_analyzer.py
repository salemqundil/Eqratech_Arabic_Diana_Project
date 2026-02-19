"""
Pattern analysis layer (Plan A).

This is a thin wrapper around `PatternMatcher` that provides a stable
result shape for downstream consumers (CLI, classifiers, feature extractors).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .morpheme import Pattern, Root
from .pattern_matcher import PatternMatcher


@dataclass(frozen=True)
class PatternAnalysis:
    pattern: Pattern
    confidence: float
    features: Dict[str, Any]


class PatternAnalyzer:
    def __init__(self, matcher: Optional[PatternMatcher] = None) -> None:
        self._matcher = matcher or PatternMatcher()

    def analyze(self, token: str, root: Root) -> Optional[PatternAnalysis]:
        pattern = self._matcher.match(token, root)
        if not pattern:
            return None
        features: Dict[str, Any] = dict(pattern.features or {})
        conf_raw = features.get("confidence", 0.0)
        try:
            confidence = float(conf_raw)
        except Exception:
            confidence = 0.0
        return PatternAnalysis(pattern=pattern, confidence=confidence, features=features)

