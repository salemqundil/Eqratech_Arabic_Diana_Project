"""
بوابات التعجب والخبر والترجي والتمني والشرط والقسم
"""

from typing import Any, Dict, List
from .base_gate import BaseGate, GateType


class ExclamativeGate(BaseGate):
    """بوابة التعجب"""
    
    def __init__(self):
        super().__init__(GateType.EXCLAMATIVE)
    
    def can_activate(self, x: Any) -> bool:
        M = x.get_maqam()
        return M.i_taajjub > 0.5 or x.surf.has_ma_ta3ajjub
    
    def compute_satisfaction(self, x: Any, y: Any) -> float:
        satisfaction = 0.0
        if hasattr(y, 'exclamation_pattern'):
            satisfaction += 0.6
        if hasattr(y, 'emotional_intensity') and y.emotional_intensity > 0.5:
            satisfaction += 0.4
        return satisfaction
    
    def compute_cost(self, x: Any, y: Any, activated: bool) -> float:
        if activated:
            return 0.5 - (x.get_maqam().i_taajjub * 1.0)
        return float('inf') if x.surf.has_ma_ta3ajjub else 0.0
    
    def get_modifications(self, x: Any, y: Any) -> Dict[str, Any]:
        return {'exclamation_pattern': 'ما أفعل', 'emotional_intensity': 0.8}
    
    def check_violations(self, x: Any, y: Any) -> List[str]:
        return [] if hasattr(y, 'exclamation_pattern') else ["missing_pattern"]


class DeclarativeGate(BaseGate):
    """بوابة الخبر"""
    
    def __init__(self):
        super().__init__(GateType.DECLARATIVE)
    
    def can_activate(self, x: Any) -> bool:
        M = x.get_maqam()
        return M.i_khabar > 0.3 or M.commitment > 0.5
    
    def compute_satisfaction(self, x: Any, y: Any) -> float:
        satisfaction = 0.0
        if hasattr(y, 'proposition') and y.proposition:
            satisfaction += 0.5
        if hasattr(y, 'truth_evaluable') and y.truth_evaluable:
            satisfaction += 0.5
        return satisfaction
    
    def compute_cost(self, x: Any, y: Any, activated: bool) -> float:
        M = x.get_maqam()
        if activated:
            return 0.3 - (M.i_khabar * 0.5)
        # Default gate - low cost if not activated
        return 1.0
    
    def get_modifications(self, x: Any, y: Any) -> Dict[str, Any]:
        return {'proposition': True, 'truth_evaluable': True, 'illocution': 'inform'}
    
    def check_violations(self, x: Any, y: Any) -> List[str]:
        return [] if hasattr(y, 'proposition') else ["missing_proposition"]


class OptativeGate(BaseGate):
    """بوابة الترجي"""
    
    def __init__(self):
        super().__init__(GateType.OPTATIVE)
    
    def can_activate(self, x: Any) -> bool:
        return x.get_maqam().i_tarajji > 0.5
    
    def compute_satisfaction(self, x: Any, y: Any) -> float:
        return 0.8 if hasattr(y, 'hope_particle') else 0.0
    
    def compute_cost(self, x: Any, y: Any, activated: bool) -> float:
        M = x.get_maqam()
        return 0.6 - M.i_tarajji if activated else 0.0
    
    def get_modifications(self, x: Any, y: Any) -> Dict[str, Any]:
        return {'hope_particle': 'لعل', 'expectation_level': 0.6}
    
    def check_violations(self, x: Any, y: Any) -> List[str]:
        return []


class WishGate(BaseGate):
    """بوابة التمني"""
    
    def __init__(self):
        super().__init__(GateType.WISH)
    
    def can_activate(self, x: Any) -> bool:
        return x.get_maqam().i_tamanni > 0.5
    
    def compute_satisfaction(self, x: Any, y: Any) -> float:
        return 0.8 if hasattr(y, 'wish_particle') else 0.0
    
    def compute_cost(self, x: Any, y: Any, activated: bool) -> float:
        return 0.6 - x.get_maqam().i_tamanni if activated else 0.0
    
    def get_modifications(self, x: Any, y: Any) -> Dict[str, Any]:
        return {'wish_particle': 'ليت', 'realizability': 0.2}
    
    def check_violations(self, x: Any, y: Any) -> List[str]:
        return []


class ConditionalGate(BaseGate):
    """بوابة الشرط"""
    
    def __init__(self):
        super().__init__(GateType.CONDITIONAL)
    
    def can_activate(self, x: Any) -> bool:
        return x.get_maqam().i_shart > 0.5
    
    def compute_satisfaction(self, x: Any, y: Any) -> float:
        sat = 0.0
        if hasattr(y, 'condition_clause'):
            sat += 0.5
        if hasattr(y, 'consequence_clause'):
            sat += 0.5
        return sat
    
    def compute_cost(self, x: Any, y: Any, activated: bool) -> float:
        return 1.0 - x.get_maqam().i_shart if activated else 0.0
    
    def get_modifications(self, x: Any, y: Any) -> Dict[str, Any]:
        return {'condition_clause': True, 'consequence_clause': True, 'conditional_particle': 'إن'}
    
    def check_violations(self, x: Any, y: Any) -> List[str]:
        viols = []
        if not hasattr(y, 'condition_clause'):
            viols.append("missing_condition")
        if not hasattr(y, 'consequence_clause'):
            viols.append("missing_consequence")
        return viols


class OathGate(BaseGate):
    """بوابة القسم"""
    
    def __init__(self):
        super().__init__(GateType.OATH)
    
    def can_activate(self, x: Any) -> bool:
        return x.get_maqam().i_qasam > 0.5 or x.get_maqam().oath > 0.5
    
    def compute_satisfaction(self, x: Any, y: Any) -> float:
        return 0.9 if hasattr(y, 'oath_formula') else 0.0
    
    def compute_cost(self, x: Any, y: Any, activated: bool) -> float:
        M = x.get_maqam()
        return 0.8 - M.i_qasam if activated else 0.0
    
    def get_modifications(self, x: Any, y: Any) -> Dict[str, Any]:
        return {'oath_formula': True, 'emphasis_level': 0.9, 'oath_particle': 'والله'}
    
    def check_violations(self, x: Any, y: Any) -> List[str]:
        return []
