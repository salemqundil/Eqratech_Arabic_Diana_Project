"""
WordForm Package: Unified representation for morphology and syntax

This package provides WordForm, a unified data structure that bridges
the gap between C2B (morphology) output and the Syntax Layer input.

Main Components:
    - WordForm: Main class representing a word with all its features
    - WordFormBuilder: Converts C2B output to WordForm instances
    - Enums: PartOfSpeech, Case, Number, Gender, SyntaxRole
    - Data structures: Root, Pattern, Span, Affixes

Author: Hussein Hiyassat
Date: 2025-02-12
Version: 1.0

Examples:
    >>> from fvafk.c2b.word_form import WordForm, PartOfSpeech, Case
    >>> from fvafk.c2b.word_form_builder import build_word_form
    >>> 
    >>> # From C2B output
    >>> c2b = {
    ...     'word': 'الْكِتَابُ',
    ...     'span': {'start': 0, 'end': 10},
    ...     'kind': 'noun',
    ...     'features': {'case': 'nominative', 'definite': True}
    ... }
    >>> word = build_word_form(c2b)
    >>> print(f"{word.surface} is {word.case.arabic}")
    الْكِتَابُ is مرفوع
"""

from .word_form import (
    # Main class
    WordForm,
    
    # Enumerations
    PartOfSpeech,
    Case,
    Number,
    Gender,
    SyntaxRole,
    
    # Data structures
    Root,
    Pattern,
    Span,
    Affixes,
)

from .word_form_builder import (
    WordFormBuilder,
    build_word_form,
    build_word_forms,
)

__version__ = '1.0.0'

__all__ = [
    # Main class
    'WordForm',
    
    # Enumerations
    'PartOfSpeech',
    'Case',
    'Number',
    'Gender',
    'SyntaxRole',
    
    # Data structures
    'Root',
    'Pattern',
    'Span',
    'Affixes',
    
    # Builder
    'WordFormBuilder',
    'build_word_form',
    'build_word_forms',
]
