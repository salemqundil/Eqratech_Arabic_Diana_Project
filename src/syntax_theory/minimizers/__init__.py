"""
المُحسّنات (Minimizers)
======================

تصدير:
- SyntacticEnergy (دالة الكلفة E)
- SyntacticOptimizer (arg min E)
- EnergyWeights (الأوزان)
"""

from .syntactic_energy import (
    SyntacticEnergy,
    SyntacticOptimizer,
    EnergyWeights
)

__all__ = [
    'SyntacticEnergy',
    'SyntacticOptimizer',
    'EnergyWeights',
]
