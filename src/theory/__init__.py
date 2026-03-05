"""
النظرية الرياضية للتوليد الصوتي
Mathematical Theory of Phonetic Generation

كل شيء من التصغير (arg min E) - لا جداول، لا قواعد لغوية.
Everything from minimization (arg min E) - no tables, no linguistic rules.
"""

from theory.phonetic_space.feature_space import FeatureSpace, ConsonantSpace, VowelSpace
from theory.phonetic_space.projection import ProjectionPsi
from theory.minimizers.syllable_energy import SyllableEnergy
from theory.minimizers.optimizer import VowelOptimizer
from theory.proofs.existence_uniqueness import ExistenceUniquenessTheorem

__all__ = [
    'FeatureSpace',
    'ConsonantSpace', 
    'VowelSpace',
    'ProjectionPsi',
    'SyllableEnergy',
    'VowelOptimizer',
    'ExistenceUniquenessTheorem',
]

__version__ = '1.0.0'
__author__ = 'Theoretical Phonetics Framework'
