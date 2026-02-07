"""
مولد التعيينات - Assignment Generator

ينشئ y₀ (المنشئ القانوني) ويطبّق التعديلات
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set


@dataclass
class Assignment:
    """
    تعيينات المنشئ y
    
    تتضمن:
    - متغيرات الاستفهام
    - متغير قيمة الصدق
    - العلاقات (ISN/TADMN/TAQYID)
    - الأدوار (Agent/Patient...)
    - الحالات الإعرابية
    """
    # متغيرات استفهامية
    wh_variables: Set[str] = field(default_factory=set)
    truth_variable: Optional[bool] = None
    choice_variable: Optional[str] = None
    alternatives: list = field(default_factory=list)
    
    # علاقات
    isn_relations: list = field(default_factory=list)
    tadmn_relations: list = field(default_factory=list)
    taqyid_relations: list = field(default_factory=list)
    
    # نداء
    has_vocative_relation: bool = False
    addressee: Optional[str] = None
    vocative_case: Optional[str] = None
    
    # طلب
    request_type: Optional[str] = None
    scope_type: Optional[str] = None
    
    # تعجب
    exclamation_pattern: Optional[str] = None
    emotional_intensity: float = 0.0
    
    # خبر
    proposition: bool = False
    truth_evaluable: bool = False
    
    # ترجي/تمني
    hope_particle: Optional[str] = None
    wish_particle: Optional[str] = None
    expectation_level: float = 0.5
    realizability: float = 0.5
    
    # شرط
    condition_clause: bool = False
    consequence_clause: bool = False
    conditional_particle: Optional[str] = None
    
    # قسم
    oath_formula: bool = False
    oath_particle: Optional[str] = None
    
    # عام
    negation: bool = False
    verb_mood: Optional[str] = None
    emphasis_level: float = 0.0


class AssignmentGenerator:
    """
    مولد التعيينات
    
    ينشئ y₀ ويطبّق التعديلات من البوابات
    """
    
    @staticmethod
    def initialize() -> Assignment:
        """إنشاء y₀ فارغ"""
        return Assignment()
    
    @staticmethod
    def apply_modifications(y: Assignment, modifications: Dict[str, Any]) -> Assignment:
        """
        تطبيق التعديلات من بوابة
        
        Args:
            y: التعيين الحالي
            modifications: التعديلات من GateResult.modifications
        
        Returns:
            y جديد مع التعديلات
        """
        # نسخ y
        import copy
        y_new = copy.deepcopy(y)
        
        # تطبيق كل تعديل
        for key, value in modifications.items():
            if key == 'add_truth_variable':
                y_new.truth_variable = False  # متغير boolean
            
            elif key == 'add_wh_variable':
                wh_type = modifications.get('wh_type', 'unknown')
                y_new.wh_variables.add(f"z_{wh_type}")
            
            elif key == 'add_choice_variable':
                y_new.choice_variable = "choice"
                y_new.alternatives = modifications.get('alternatives', [])
            
            elif key == 'add_vocative_relation':
                y_new.has_vocative_relation = True
            
            elif key == 'addressee_required':
                if y_new.addressee is None:
                    y_new.addressee = "addressee_placeholder"
            
            elif key == 'request_type':
                y_new.request_type = value
            
            elif key == 'scope_type':
                y_new.scope_type = value
            
            elif key == 'exclamation_pattern':
                y_new.exclamation_pattern = value
            
            elif key == 'emotional_intensity':
                y_new.emotional_intensity = value
            
            elif key == 'proposition':
                y_new.proposition = value
            
            elif key == 'truth_evaluable':
                y_new.truth_evaluable = value
            
            elif key == 'hope_particle':
                y_new.hope_particle = value
            
            elif key == 'wish_particle':
                y_new.wish_particle = value
            
            elif key == 'expectation_level':
                y_new.expectation_level = value
            
            elif key == 'realizability':
                y_new.realizability = value
            
            elif key == 'condition_clause':
                y_new.condition_clause = value
            
            elif key == 'consequence_clause':
                y_new.consequence_clause = value
            
            elif key == 'conditional_particle':
                y_new.conditional_particle = value
            
            elif key == 'oath_formula':
                y_new.oath_formula = value
            
            elif key == 'oath_particle':
                y_new.oath_particle = value
            
            elif key == 'negation':
                y_new.negation = value
            
            elif key == 'verb_mood':
                y_new.verb_mood = value
            
            elif key == 'emphasis_level':
                y_new.emphasis_level = value
            
            elif key == 'vocative_case':
                y_new.vocative_case = value
            
            # يمكن إضافة المزيد حسب الحاجة
        
        return y_new
    
    @staticmethod
    def validate(y: Assignment) -> bool:
        """
        التحقق من صلاحية التعيين
        
        Returns:
            True إذا كان صحيحًا
        """
        # فحص: إذا كان استفهام wh، يجب وجود متغير
        if y.wh_variables:
            # صحيح
            pass
        
        # فحص: إذا كان نداء، يجب وجود منادى
        if y.has_vocative_relation and y.addressee is None:
            return False
        
        # فحص: إذا كان شرط، يجب وجود شرط وجواب
        if y.condition_clause and not y.consequence_clause:
            return False
        
        return True
