"""
بوابات الاستفهام - Interrogative Gates

ثلاثة أنواع:
1. القطبي (Polar): هل/الهمزة → متغير قيمة صدق θ ∈ {0, 1}
2. الاستفهامي (Wh): من/ما/أين... → متغير مُقيّد z + scope
3. التعييني (Alternative): أ...أم... → متغير اختيار من مجموعة
"""

from typing import Any, Dict, List
from .base_gate import BaseGate, GateType


class InterrogativePolarGate(BaseGate):
    """
    بوابة الاستفهام القطبي
    
    شروط التفعيل:
    - M.q_polar > threshold
    - أو وجود "هل"/همزة استفهام قطبية
    
    قيود الإشباع:
    - متغير قيمة صدق θ موجود
    - Q في أعلى النطاق
    - لا متغيرات wh
    """
    
    def __init__(self):
        super().__init__(GateType.INTERROGATIVE_POLAR)
        self.threshold = 0.5
    
    def can_activate(self, x: Any) -> bool:
        """هل يمكن تفعيل الاستفهام القطبي؟"""
        M = x.get_maqam()
        surf = x.surf
        
        # شرط 1: M.q_polar مرتفع
        if M.q_polar > self.threshold:
            return True
        
        # شرط 2: علامات سطحية
        if surf.has_hal or (surf.has_hamza_istifham and not surf.has_wh_word):
            return True
        
        return False
    
    def compute_satisfaction(self, x: Any, y: Any) -> float:
        """حساب الإشباع"""
        satisfaction = 0.0
        
        # شرط 1: متغير قيمة صدق موجود (0.4)
        if hasattr(y, 'truth_variable') and y.truth_variable is not None:
            satisfaction += 0.4
        
        # شرط 2: Q في أعلى النطاق (0.3)
        scope = x.scope_graph
        if 'Q' in scope.nodes and scope.get_scope('Q'):
            satisfaction += 0.3
        
        # شرط 3: لا متغيرات wh (0.3)
        if not x.binding_map.wh_variables:
            satisfaction += 0.3
        
        return satisfaction
    
    def compute_cost(self, x: Any, y: Any, activated: bool) -> float:
        """حساب الكلفة"""
        M = x.get_maqam()
        
        if activated:
            # كلفة التفعيل = كلفة بسيطة لإضافة متغير
            cost = 0.5
            
            # توفير إذا كان M.q_polar مرتفع
            if M.q_polar > 0.8:
                cost -= 1.0
            
            return cost
        else:
            # كلفة عدم التفعيل
            # إذا كان M.q_polar مرتفع جدًا أو "هل" موجودة → ∞
            if M.q_polar > 0.9 or x.surf.has_hal:
                return float('inf')
            
            return 0.0
    
    def get_modifications(self, x: Any, y: Any) -> Dict[str, Any]:
        """التعديلات"""
        return {
            'add_truth_variable': True,
            'Q_scope': 'highest',
            'expected_answer_type': 'yes_no'
        }
    
    def check_violations(self, x: Any, y: Any) -> List[str]:
        """فحص الانتهاكات"""
        violations = []
        
        # انتهاك 1: متغير غير موجود
        if not hasattr(y, 'truth_variable') or y.truth_variable is None:
            violations.append("missing_truth_variable")
        
        # انتهاك 2: وجود متغيرات wh (تناقض)
        if x.binding_map.wh_variables:
            violations.append("conflicting_wh_variables")
        
        return violations


class InterrogativeWhGate(BaseGate):
    """
    بوابة الاستفهام الاستفهامي (Wh)
    
    شروط التفعيل:
    - M.q_wh > threshold
    - وجود أداة استفهام (من/ما/أين...)
    
    قيود الإشباع:
    - متغير wh مُقيّد (z)
    - نوع المتغير يطابق الأداة (person/thing/place...)
    - ربط صحيح في BindingMap
    - نطاق Q يحتوي على z
    """
    
    def __init__(self):
        super().__init__(GateType.INTERROGATIVE_WH)
        self.threshold = 0.5
    
    def can_activate(self, x: Any) -> bool:
        """هل يمكن تفعيل الاستفهام الاستفهامي؟"""
        M = x.get_maqam()
        surf = x.surf
        
        # شرط: M.q_wh مرتفع أو وجود أداة wh
        return M.q_wh > self.threshold or bool(surf.has_wh_word)
    
    def compute_satisfaction(self, x: Any, y: Any) -> float:
        """حساب الإشباع"""
        satisfaction = 0.0
        
        # شرط 1: متغير wh موجود (0.3)
        if x.binding_map.wh_variables:
            satisfaction += 0.3
        
        # شرط 2: المتغير مربوط (0.4)
        if x.binding_map.all_wh_bound():
            satisfaction += 0.4
        
        # شرط 3: النوع يطابق الأداة (0.3)
        if x.surf.has_wh_word:
            expected_type = x.surf.get_wh_type()
            if expected_type:
                # فحص التطابق (simplified)
                for var in x.binding_map.wh_variables:
                    binding = x.binding_map.get_binding(var)
                    if binding and expected_type in binding:
                        satisfaction += 0.3
                        break
        
        return satisfaction
    
    def compute_cost(self, x: Any, y: Any, activated: bool) -> float:
        """حساب الكلفة"""
        M = x.get_maqam()
        
        if activated:
            # كلفة التفعيل = كلفة متوسطة (أعلى من polar لتعقيد الربط)
            cost = 1.0
            
            # توفير إذا كان M.q_wh مرتفع
            if M.q_wh > 0.8:
                cost -= 1.5
            
            # عقوبة إذا كان الربط غير كامل
            if not x.binding_map.all_wh_bound():
                cost += 2.0
            
            return cost
        else:
            # كلفة عدم التفعيل
            # إذا كان هناك أداة wh → ∞
            if x.surf.has_wh_word or M.q_wh > 0.9:
                return float('inf')
            
            return 0.0
    
    def get_modifications(self, x: Any, y: Any) -> Dict[str, Any]:
        """التعديلات"""
        wh_type = x.surf.get_wh_type() if x.surf.has_wh_word else 'unknown'
        
        return {
            'add_wh_variable': True,
            'wh_type': wh_type,
            'Q_scope': 'c-command',
            'requires_binding': True,
            'wh_word': x.surf.has_wh_word
        }
    
    def check_violations(self, x: Any, y: Any) -> List[str]:
        """فحص الانتهاكات"""
        violations = []
        
        # انتهاك 1: لا متغيرات wh
        if not x.binding_map.wh_variables:
            violations.append("missing_wh_variable")
        
        # انتهاك 2: متغيرات غير مربوطة
        if not x.binding_map.all_wh_bound():
            violations.append("unbound_wh_variables")
        
        # انتهاك 3: عدم تطابق النوع
        if x.surf.has_wh_word:
            expected = x.surf.get_wh_type()
            found_match = False
            for var in x.binding_map.wh_variables:
                binding = x.binding_map.get_binding(var)
                if binding and expected in binding:
                    found_match = True
                    break
            if not found_match:
                violations.append(f"type_mismatch_expected_{expected}")
        
        return violations


class InterrogativeAlternativeGate(BaseGate):
    """
    بوابة الاستفهام التعييني
    
    شروط التفعيل:
    - M.q_alt > threshold
    - وجود "أم"
    
    قيود الإشباع:
    - متغير اختيار من مجموعة محددة
    - خياران أو أكثر محددان
    """
    
    def __init__(self):
        super().__init__(GateType.INTERROGATIVE_ALT)
        self.threshold = 0.5
    
    def can_activate(self, x: Any) -> bool:
        """هل يمكن تفعيل الاستفهام التعييني؟"""
        M = x.get_maqam()
        return M.q_alt > self.threshold or x.surf.has_am
    
    def compute_satisfaction(self, x: Any, y: Any) -> float:
        """حساب الإشباع"""
        satisfaction = 0.0
        
        # شرط 1: متغير اختيار موجود (0.5)
        if hasattr(y, 'choice_variable') and y.choice_variable is not None:
            satisfaction += 0.5
        
        # شرط 2: خياران محددان (0.5)
        if hasattr(y, 'alternatives') and len(y.alternatives) >= 2:
            satisfaction += 0.5
        
        return satisfaction
    
    def compute_cost(self, x: Any, y: Any, activated: bool) -> float:
        """حساب الكلفة"""
        M = x.get_maqam()
        
        if activated:
            cost = 0.8
            if M.q_alt > 0.8:
                cost -= 1.2
            return cost
        else:
            if M.q_alt > 0.9 or x.surf.has_am:
                return float('inf')
            return 0.0
    
    def get_modifications(self, x: Any, y: Any) -> Dict[str, Any]:
        """التعديلات"""
        return {
            'add_choice_variable': True,
            'requires_alternatives': True,
            'min_alternatives': 2
        }
    
    def check_violations(self, x: Any, y: Any) -> List[str]:
        """فحص الانتهاكات"""
        violations = []
        
        if not hasattr(y, 'choice_variable') or y.choice_variable is None:
            violations.append("missing_choice_variable")
        
        if not hasattr(y, 'alternatives') or len(y.alternatives) < 2:
            violations.append("insufficient_alternatives")
        
        return violations
