"""
بوابات الأمر والنهي - Imperative and Prohibitive Gates
"""

from typing import Any, Dict, List
from .base_gate import BaseGate, GateType


class ImperativeGate(BaseGate):
    """بوابة الأمر"""
    
    def __init__(self):
        super().__init__(GateType.IMPERATIVE)
        self.threshold = 0.5
    
    def can_activate(self, x: Any) -> bool:
        M = x.get_maqam()
        return M.t_amr > self.threshold or x.surf.is_imperative_form
    
    def compute_satisfaction(self, x: Any, y: Any) -> float:
        satisfaction = 0.0
        if hasattr(y, 'request_type') and y.request_type == 'command':
            satisfaction += 0.5
        if hasattr(y, 'scope_type') and y.scope_type == 'talab':
            satisfaction += 0.5
        return satisfaction
    
    def compute_cost(self, x: Any, y: Any, activated: bool) -> float:
        M = x.get_maqam()
        if activated:
            cost = 0.7
            if M.t_amr > 0.8 or x.surf.is_imperative_form:
                cost -= 1.2
            return cost
        else:
            if x.surf.is_imperative_form or M.t_amr > 0.9:
                return float('inf')
            return 0.0
    
    def get_modifications(self, x: Any, y: Any) -> Dict[str, Any]:
        return {
            'request_type': 'command',
            'scope_type': 'talab',
            'expected_compliance': True
        }
    
    def check_violations(self, x: Any, y: Any) -> List[str]:
        violations = []
        if not hasattr(y, 'request_type') or y.request_type != 'command':
            violations.append("missing_command_structure")
        return violations


class ProhibitiveGate(BaseGate):
    """بوابة النهي"""
    
    def __init__(self):
        super().__init__(GateType.PROHIBITIVE)
        self.threshold = 0.5
    
    def can_activate(self, x: Any) -> bool:
        M = x.get_maqam()
        return M.t_nahy > self.threshold or (x.surf.has_la_nahia and x.surf.is_jussive)
    
    def compute_satisfaction(self, x: Any, y: Any) -> float:
        satisfaction = 0.0
        if hasattr(y, 'request_type') and y.request_type == 'prohibition':
            satisfaction += 0.4
        if hasattr(y, 'negation') and y.negation:
            satisfaction += 0.3
        if hasattr(y, 'verb_mood') and y.verb_mood == 'jussive':
            satisfaction += 0.3
        return satisfaction
    
    def compute_cost(self, x: Any, y: Any, activated: bool) -> float:
        M = x.get_maqam()
        if activated:
            cost = 0.8
            if M.t_nahy > 0.8 and x.surf.has_la_nahia:
                cost -= 1.3
            return cost
        else:
            if x.surf.has_la_nahia and x.surf.is_jussive:
                return float('inf')
            return 0.0
    
    def get_modifications(self, x: Any, y: Any) -> Dict[str, Any]:
        return {
            'request_type': 'prohibition',
            'negation': True,
            'verb_mood': 'jussive',
            'particle': 'لا الناهية'
        }
    
    def check_violations(self, x: Any, y: Any) -> List[str]:
        violations = []
        if not hasattr(y, 'negation') or not y.negation:
            violations.append("missing_negation")
        if hasattr(y, 'verb_mood') and y.verb_mood != 'jussive':
            violations.append("wrong_mood")
        return violations
