"""
بوابة النداء - Vocative Gate

شروط التفعيل:
- M.i_nida > threshold
- M.attention مرتفع
- وجود "يا" أو أدوات نداء أخرى

قيود الإشباع:
- علاقة ISN/TADMN خاصة: Call → Addressee
- منادى محدد
- حالة النداء (منصوب/مبني)
"""

from typing import Any, Dict, List
from .base_gate import BaseGate, GateType


class VocativeGate(BaseGate):
    """
    بوابة النداء
    
    النداء = تنبيه + إنشاء علاقة خاصة مع المخاطب
    """
    
    def __init__(self):
        super().__init__(GateType.VOCATIVE)
        self.threshold_nida = 0.5
        self.threshold_attention = 0.4
    
    def can_activate(self, x: Any) -> bool:
        """هل يمكن تفعيل النداء؟"""
        M = x.get_maqam()
        surf = x.surf
        
        # شرط 1: قوة النداء
        if M.i_nida > self.threshold_nida:
            return True
        
        # شرط 2: التنبيه + علامة سطحية
        if M.attention > self.threshold_attention and surf.has_vocative_marker():
            return True
        
        # شرط 3: "يا" موجودة
        if surf.has_ya or surf.has_a_nida:
            return True
        
        return False
    
    def compute_satisfaction(self, x: Any, y: Any) -> float:
        """حساب الإشباع"""
        satisfaction = 0.0
        
        # شرط 1: علاقة Call → Addressee موجودة (0.4)
        if hasattr(y, 'has_vocative_relation') and y.has_vocative_relation:
            satisfaction += 0.4
        
        # شرط 2: منادى محدد (0.3)
        if hasattr(y, 'addressee') and y.addressee is not None:
            satisfaction += 0.3
        
        # شرط 3: حالة النداء صحيحة (0.3)
        # منصوب (إذا مضاف/شبيه بالمضاف) أو مبني (إذا مفرد معرفة)
        if hasattr(y, 'vocative_case') and y.vocative_case in ['منصوب', 'مبني']:
            satisfaction += 0.3
        
        return satisfaction
    
    def compute_cost(self, x: Any, y: Any, activated: bool) -> float:
        """حساب الكلفة"""
        M = x.get_maqam()
        surf = x.surf
        
        if activated:
            # كلفة التفعيل
            cost = 0.6
            
            # توفير إذا كان M.i_nida مرتفع
            if M.i_nida > 0.8:
                cost -= 1.0
            
            # توفير إذا كان هناك "يا"
            if surf.has_ya:
                cost -= 0.8
            
            return cost
        else:
            # كلفة عدم التفعيل
            # إذا كان هناك "يا" أو M.i_nida مرتفع جدًا → ∞
            if surf.has_ya or surf.has_a_nida or M.i_nida > 0.9:
                return float('inf')
            
            return 0.0
    
    def get_modifications(self, x: Any, y: Any) -> Dict[str, Any]:
        """التعديلات"""
        return {
            'add_vocative_relation': True,
            'relation_type': 'ISN',  # أو TADMN حسب السياق
            'addressee_required': True,
            'vocative_particle': x.surf.has_ya,
            'set_attention_high': True
        }
    
    def check_violations(self, x: Any, y: Any) -> List[str]:
        """فحص الانتهاكات"""
        violations = []
        
        # انتهاك 1: لا علاقة نداء
        if not hasattr(y, 'has_vocative_relation') or not y.has_vocative_relation:
            violations.append("missing_vocative_relation")
        
        # انتهاك 2: لا منادى
        if not hasattr(y, 'addressee') or y.addressee is None:
            violations.append("missing_addressee")
        
        # انتهاك 3: حالة خاطئة
        if hasattr(y, 'vocative_case') and y.vocative_case not in ['منصوب', 'مبني']:
            violations.append(f"wrong_case_{y.vocative_case}")
        
        return violations
