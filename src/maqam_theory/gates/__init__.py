"""
بوابات الأساليب - Style Gates
Gates as arg min outcomes, not definitions
"""

from .base_gate import (
    BaseGate,
    GateResult,
    GateType
)

from .interrogative_gates import (
    InterrogativePolarGate,
    InterrogativeWhGate,
    InterrogativeAlternativeGate
)

from .vocative_gate import VocativeGate
from .imperative_gates import ImperativeGate, ProhibitiveGate
from .exclamative_gate import ExclamativeGate
from .declarative_gate import DeclarativeGate
from .optative_gates import OptativeGate, WishGate
from .conditional_gate import ConditionalGate
from .oath_gate import OathGate

__all__ = [
    'BaseGate',
    'GateResult',
    'GateType',
    'InterrogativePolarGate',
    'InterrogativeWhGate',
    'InterrogativeAlternativeGate',
    'VocativeGate',
    'ImperativeGate',
    'ProhibitiveGate',
    'ExclamativeGate',
    'DeclarativeGate',
    'OptativeGate',
    'WishGate',
    'ConditionalGate',
    'OathGate'
]
