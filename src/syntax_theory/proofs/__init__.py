"""
البراهين (Proofs)
================

تصدير:
- TheoremResult
- StructuralSelectionTheorem (ISN/TADMN/TAQYID)
- BuiltVsDeclensionTheorem (المبني/المعرب)
- SemanticRolesTheorem (الأدوار الدلالية)
- prove_all_theorems (شامل)
"""

from .selection_theorem import (
    TheoremResult,
    StructuralSelectionTheorem,
    BuiltVsDeclensionTheorem,
    SemanticRolesTheorem,
    prove_all_theorems
)

__all__ = [
    'TheoremResult',
    'StructuralSelectionTheorem',
    'BuiltVsDeclensionTheorem',
    'SemanticRolesTheorem',
    'prove_all_theorems',
]
