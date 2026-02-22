"""
FVAFK / Bayan - Arabic NLP Pipeline

A formal Arabic NLP system with phonology, morphology, and syntax analysis.

Modules:
    - c1: Encoding layer (FormCodec V2)
    - c2a: Phonology layer (gates, syllables)
    - c2b: Morphology layer (roots, patterns)
    - syntax: Syntax layer (links, constraints)
    - cli: Command-line interface
    - phonology_v2: Enhanced phonology engine

Author: Hussein Hiyassat
Version: 0.1.0
License: MIT
"""

__version__ = "0.1.0"
__author__ = "Hussein Hiyassat"

# Core modules
from .orthography_adapter import OrthographyAdapter

__all__ = [
    # Core
    "OrthographyAdapter",
    # Submodules
    "c1",
    "c2a",
    "c2b",
    "syntax",
    "cli",
    "phonology",
    "phonology_v2",
]
