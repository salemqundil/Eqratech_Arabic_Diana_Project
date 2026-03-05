"""
الهياكل (Structures)
===================

تصدير:
- SyntacticInput (x)
- SyntacticGraph (y)
- العلاقات والأنواع
"""

from .input_structure import (
    LexicalType,
    VerbValency,
    SemanticRole,
    LexicalAtom,
    IntentConstraint,
    SyntacticInput,
    make_simple_input
)

from .graph_structure import (
    EdgeType,
    CaseMarking,
    MoodMarking,
    NodeFeatures,
    Node,
    Edge,
    SyntacticGraph,
    make_token_node,
    make_governor_node
)

__all__ = [
    # من input_structure
    'LexicalType',
    'VerbValency',
    'SemanticRole',
    'LexicalAtom',
    'IntentConstraint',
    'SyntacticInput',
    'make_simple_input',
    
    # من graph_structure
    'EdgeType',
    'CaseMarking',
    'MoodMarking',
    'NodeFeatures',
    'Node',
    'Edge',
    'SyntacticGraph',
    'make_token_node',
    'make_governor_node',
]
