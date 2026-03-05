"""
البوابة الأساسية - Base Gate
كل بوابة = constraint تُفعّل أو لا بناءً على arg min E
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List, Any
from abc import ABC, abstractmethod


class GateType(Enum):
    """أنواع البوابات"""
    DECLARATIVE = "خبر"
    INTERROGATIVE_POLAR = "استفهام_قطبي"
    INTERROGATIVE_WH = "استفهام_استفهامي"
    INTERROGATIVE_ALT = "استفهام_تعييني"
    VOCATIVE = "نداء"
    IMPERATIVE = "أمر"
    PROHIBITIVE = "نهي"
    EXCLAMATIVE = "تعجب"
    OPTATIVE = "ترجي"
    WISH = "تمني"
    CONDITIONAL = "شرط"
    OATH = "قسم"


@dataclass
class GateResult:
    """
    نتيجة تطبيق بوابة
    
    تتضمن:
    - هل تفعّلت؟
    - التعديلات على البنية
    - الكلفة المضافة/المُوفَّرة
    """
    activated: bool = False
    gate_type: Optional[GateType] = None
    modifications: Dict[str, Any] = field(default_factory=dict)
    cost_delta: float = 0.0  # التغيير في الكلفة (سالب = توفير)
    satisfaction_level: float = 0.0  # مستوى الإشباع [0, 1]
    constraints_violated: List[str] = field(default_factory=list)
    
    def is_satisfied(self) -> bool:
        """هل البوابة مُشبَعة؟"""
        return self.activated and self.satisfaction_level > 0.8 and not self.constraints_violated
    
    def __repr__(self) -> str:
        status = "✓" if self.activated else "✗"
        sat = f"{self.satisfaction_level:.2f}" if self.activated else "N/A"
        return f"Gate[{self.gate_type.value if self.gate_type else 'None'}] {status} (sat={sat}, Δcost={self.cost_delta:.2f})"


class BaseGate(ABC):
    """
    البوابة الأساسية
    
    كل بوابة تُعرّف:
    1. شروط التفعيل (activation conditions)
    2. قيود الإشباع (satisfaction constraints)
    3. تأثيرها على E (energy impact)
    """
    
    def __init__(self, gate_type: GateType):
        self.gate_type = gate_type
        self.weight = 1.0  # وزن البوابة في دالة الطاقة
    
    @abstractmethod
    def can_activate(self, x: Any) -> bool:
        """
        هل يمكن تفعيل البوابة؟
        
        يفحص الشروط الأولية من x (السطح/السياق/M)
        """
        pass
    
    @abstractmethod
    def compute_satisfaction(self, x: Any, y: Any) -> float:
        """
        حساب مستوى الإشباع [0, 1]
        
        - x: المدخل
        - y: المنشئ (التعيينات)
        
        يفحص:
        - هل كل المتطلبات محققة؟
        - هل الربط صحيح؟
        - هل النطاق سليم؟
        """
        pass
    
    @abstractmethod
    def compute_cost(self, x: Any, y: Any, activated: bool) -> float:
        """
        حساب كلفة البوابة
        
        - إذا activated = True: كلفة التفعيل
        - إذا activated = False: كلفة عدم التفعيل (قد تكون ∞ إذا كانت ضرورية)
        """
        pass
    
    def apply(self, x: Any, y: Any) -> GateResult:
        """
        تطبيق البوابة
        
        يحاول التفعيل ويحسب النتيجة
        """
        # فحص إمكانية التفعيل
        can_activate = self.can_activate(x)
        
        if not can_activate:
            return GateResult(
                activated=False,
                gate_type=self.gate_type,
                cost_delta=0.0,
                satisfaction_level=0.0
            )
        
        # حساب الإشباع
        satisfaction = self.compute_satisfaction(x, y)
        
        # حساب الكلفة
        cost_on = self.compute_cost(x, y, activated=True)
        cost_off = self.compute_cost(x, y, activated=False)
        cost_delta = cost_on - cost_off
        
        # قرار التفعيل: إذا كان التفعيل يوفّر كلفة (أو إذا كان ضروريًا)
        should_activate = cost_delta < 0 or cost_off == float('inf')
        
        # التعديلات على البنية
        modifications = self.get_modifications(x, y) if should_activate else {}
        
        # الانتهاكات
        violations = self.check_violations(x, y) if should_activate else []
        
        return GateResult(
            activated=should_activate,
            gate_type=self.gate_type,
            modifications=modifications,
            cost_delta=cost_delta,
            satisfaction_level=satisfaction if should_activate else 0.0,
            constraints_violated=violations
        )
    
    @abstractmethod
    def get_modifications(self, x: Any, y: Any) -> Dict[str, Any]:
        """
        التعديلات التي تُطبَّق على البنية
        
        مثلاً:
        - إضافة متغير استفهامي
        - تغيير نطاق عامل
        - ربط ضمير
        """
        pass
    
    @abstractmethod
    def check_violations(self, x: Any, y: Any) -> List[str]:
        """
        فحص انتهاكات القيود
        
        مثلاً:
        - متغير wh غير مربوط
        - نطاق خاطئ
        - عدم تطابق
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[{self.gate_type.value}]"
