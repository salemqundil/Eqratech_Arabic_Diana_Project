"""
العوامل (Operators)
==================

تصدير:
- OperatorSignature
- OperatorFactory
- OperatorConstraints
- التوقيعات القياسية
- مساعدات
"""

from .operator_signatures import (
    OperatorSignature,
    OperatorFactory,
    OperatorConstraints,
    # التوقيعات
    INNA_SIGNATURE,
    KANA_SIGNATURE,
    LAM_SIGNATURE,
    LAN_SIGNATURE,
    LA_NAHIA_SIGNATURE,
    PREPOSITION_SIGNATURE,
    # مساعدات
    make_inna_graph,
    make_lam_graph
)

__all__ = [
    'OperatorSignature',
    'OperatorFactory',
    'OperatorConstraints',
    'INNA_SIGNATURE',
    'KANA_SIGNATURE',
    'LAM_SIGNATURE',
    'LAN_SIGNATURE',
    'LA_NAHIA_SIGNATURE',
    'PREPOSITION_SIGNATURE',
    'make_inna_graph',
    'make_lam_graph',
]
