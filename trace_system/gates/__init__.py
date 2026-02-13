"""
Gates Package - Computational Linguistics Gates

Available gates:
- SyllabifyGate: Phoneme stream → syllable segmentation + weight + transitions
- ScopeGate: Syntax parse → operator scope tracking (TODO)
- SenseSelectionGate: Candidates → sense disambiguation (TODO)
- EpistemicGate: J + sense → predicate classification + truth mode (TODO)
"""

from .syllabify_gate import SyllabifyGate

__all__ = ['SyllabifyGate']
