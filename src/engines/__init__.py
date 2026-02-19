"""
Engine Package Namespace
=========================
Organized hierarchy of Arabic grammar engines by computational linguistics layers.

Architecture:
    Layer 1: Phonology  - phonemes, sounds, prosody
    Layer 2: Morphology - word structure, patterns, inflections
    Layer 3: Lexicon    - vocabulary, proper nouns, semantic classes
    Layer 4: Syntax     - sentence structure, grammatical relations
    Layer 5: Rhetoric   - figurative language, discourse patterns
    Layer 6: Generation - sentence production

Usage:
    from engines.phonology import PhonemesEngine
    from engines.morphology import ActiveParticipleEngine
    from engines.syntax import FaelEngine
    from engines.generation import SentenceGenerationEngine
    
    # Or import base classes
    from engines.base import (
        BaseReconstructionEngine,
        PhonologyEngine,
        MorphologyEngine,
        LexiconEngine,
        SyntaxEngine,
        RhetoricEngine,
        GenerationEngine,
        EngineLayer
    )
"""

from engines.base import (
    BaseReconstructionEngine,
    EngineLayer,
    PhonologyEngine,
    MorphologyEngine,
    LexiconEngine,
    SyntaxEngine,
    RhetoricEngine,
    GenerationEngine,
)

# Layer imports
from engines import phonology
from engines import morphology  
from engines import lexicon
from engines import syntax
from engines import rhetoric
# from engines import generation  # Temporarily disabled due to root-level dependencies

__all__ = [
    'BaseReconstructionEngine',
    'EngineLayer',
    'PhonologyEngine',
    'MorphologyEngine',
    'LexiconEngine',
    'SyntaxEngine',
    'RhetoricEngine',
    'GenerationEngine',
    'phonology',
    'morphology',
    'lexicon',
    'syntax',
    'rhetoric',
    # 'generation',
]

__version__ = '2.0.0'
