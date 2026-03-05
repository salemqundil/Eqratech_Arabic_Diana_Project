"""Syntax package - I3rab parsing, data models, and evaluation."""

from .mappings import (
    I3RAB_TYPE_MAPPING,
    I3RAB_TYPE_MAPPING_REVERSE,
    SYNTACTIC_ROLE_MAPPING,
    CASE_MAPPING,
    CASE_MAPPING_REVERSE,
    CASE_MARKER_MAPPING,
    MAHALL_MAPPING,
    TOP5_I3RAB_TYPES,
)

from .i3rab_components import (
    I3rabAnnotation,
    I3rabComponents,
)

from .syntax_features import SyntaxFeatures

from .i3rab_parser import I3rabParser

from .morph_syntax_bridge import MorphSyntaxBridge

from .syntax_evaluator import SyntaxMetrics, SyntaxEvaluator

__all__ = [
    # Mappings
    "I3RAB_TYPE_MAPPING",
    "I3RAB_TYPE_MAPPING_REVERSE",
    "SYNTACTIC_ROLE_MAPPING",
    "CASE_MAPPING",
    "CASE_MAPPING_REVERSE",
    "CASE_MARKER_MAPPING",
    "MAHALL_MAPPING",
    "TOP5_I3RAB_TYPES",
    # Data models
    "I3rabAnnotation",
    "I3rabComponents",
    "SyntaxFeatures",
    # Parser
    "I3rabParser",
    # Bridge
    "MorphSyntaxBridge",
    # Evaluator
    "SyntaxMetrics",
    "SyntaxEvaluator",
]
