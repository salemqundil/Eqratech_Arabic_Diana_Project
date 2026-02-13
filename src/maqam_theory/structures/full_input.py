"""
المدخل الكامل x = (Σ, Surf, Ctx, M)
Full input structure for maqam theory
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from .maqam_space import MaqamVector, ScopeGraph, BindingMap


@dataclass
class ContextInfo:
    """
    معلومات السياق (Ctx)
    
    تتضمن:
    - النية المُتكلم (speaker intent)
    - الزمن/المكان
    - المرجعيات السابقة
    - علاقة المتكلم والمخاطب
    """
    speaker_intent: Optional[str] = None      # نية المتكلم
    addressee: Optional[str] = None           # المخاطب
    time_reference: Optional[str] = None      # الزمن
    place_reference: Optional[str] = None     # المكان
    prior_discourse: List[str] = field(default_factory=list)  # الكلام السابق
    formality_level: float = 0.5              # مستوى الرسمية [0, 1]
    social_distance: float = 0.5              # المسافة الاجتماعية [0, 1]
    power_relation: float = 0.5               # علاقة القوة [0=equal, 1=speaker higher]
    shared_knowledge: Dict[str, Any] = field(default_factory=dict)  # المعرفة المشتركة
    
    def is_formal(self) -> bool:
        """هل السياق رسمي؟"""
        return self.formality_level > 0.6
    
    def is_close(self) -> bool:
        """هل العلاقة قريبة؟"""
        return self.social_distance < 0.4
    
    def has_prior_context(self) -> bool:
        """هل يوجد سياق سابق؟"""
        return len(self.prior_discourse) > 0


@dataclass
class SurfaceFeatures:
    """
    سمات السطح (Surf)
    
    تتضمن:
    - الفونيمات والمقاطع
    - العلامات الإعرابية
    - الرتبة
    - أدوات خاصة (هل، يا، ما التعجبية...)
    """
    phonemes: List[str] = field(default_factory=list)
    syllables: List[str] = field(default_factory=list)
    case_markers: Dict[str, str] = field(default_factory=dict)  # كلمة → حركة
    word_order: List[str] = field(default_factory=list)         # الرتبة
    
    # أدوات مميزة
    has_hal: bool = False              # هل
    has_hamza_istifham: bool = False   # همزة الاستفهام
    has_wh_word: str = ""              # من/ما/أين/متى... (فارغ = لا يوجد)
    has_am: bool = False               # أم
    has_ya: bool = False               # يا النداء
    has_a_nida: bool = False           # أ النداء
    has_la_nahia: bool = False         # لا الناهية
    has_ma_ta3ajjub: bool = False      # ما التعجبية
    has_inna: bool = False             # إنّ
    has_lam_tawkid: bool = False       # لام التوكيد
    has_negation: bool = False         # نفي عام
    is_imperative_form: bool = False   # صيغة أمر
    is_jussive: bool = False           # مجزوم
    
    # معلومات إضافية
    intonation: str = "neutral"        # النبر: rising/falling/neutral
    pause_pattern: List[int] = field(default_factory=list)  # مواضع الوقف
    
    def get_wh_type(self) -> Optional[str]:
        """نوع أداة الاستفهام"""
        if not self.has_wh_word:
            return None
        
        wh_types = {
            'من': 'person',
            'ما': 'thing',
            'ماذا': 'thing',
            'أين': 'place',
            'متى': 'time',
            'كيف': 'manner',
            'لماذا': 'reason',
            'كم': 'quantity',
            'أي': 'which'
        }
        return wh_types.get(self.has_wh_word, 'unknown')
    
    def has_interrogative_marker(self) -> bool:
        """هل يوجد علامة استفهام؟"""
        return self.has_hal or self.has_hamza_istifham or bool(self.has_wh_word)
    
    def has_vocative_marker(self) -> bool:
        """هل يوجد علامة نداء؟"""
        return self.has_ya or self.has_a_nida


@dataclass
class FullInput:
    """
    المدخل الكامل x = (Σ, Surf, Ctx, M)
    
    - Σ: البنية التركيبية (من syntax_theory)
    - Surf: السطح
    - Ctx: السياق
    - M: متجه المقام (قد يكون مُعطى جزئيًا أو مُستنتج)
    """
    sigma: Optional[Any] = None  # SyntacticGraph (سنربطه لاحقًا)
    surf: SurfaceFeatures = field(default_factory=SurfaceFeatures)
    ctx: ContextInfo = field(default_factory=ContextInfo)
    M_given: Optional[MaqamVector] = None  # المقام المُعطى (إن وُجد)
    
    # النطاق والربط (يُملأ بالتحسين)
    scope_graph: ScopeGraph = field(default_factory=ScopeGraph)
    binding_map: BindingMap = field(default_factory=BindingMap)
    
    def is_valid(self) -> bool:
        """
        هل المدخل صحيح؟
        
        شروط الصلاحية:
        1. السطح يحتوي على كلمات
        2. إذا كان M_given موجودًا، يجب أن يكون صحيحًا
        3. إذا كان استفهام wh، يجب وجود متغير
        """
        # شرط 1: السطح غير فارغ
        if not self.surf.word_order:
            return False
        
        # شرط 2: M_given صحيح
        if self.M_given is not None:
            from .maqam_space import MaqamSpace
            space = MaqamSpace()
            if not space.is_valid(self.M_given):
                return False
        
        # شرط 3: استفهام wh → متغير
        if self.surf.has_wh_word:
            if not self.binding_map.wh_variables:
                # يجب إضافة متغير
                pass
        
        return True
    
    def infer_maqam_from_surface(self) -> MaqamVector:
        """استنتاج M من السطح"""
        from .maqam_space import MaqamSpace
        space = MaqamSpace()
        
        features = {
            'has_hal': self.surf.has_hal,
            'has_wh_word': bool(self.surf.has_wh_word),
            'has_am': self.surf.has_am,
            'has_ya': self.surf.has_ya,
            'is_imperative_form': self.surf.is_imperative_form,
            'has_la_nahia': self.surf.has_la_nahia,
            'has_ma_ta3ajjub': self.surf.has_ma_ta3ajjub,
            'has_inna': self.surf.has_inna,
            'has_lam_tawkid': self.surf.has_lam_tawkid,
            'has_negation': self.surf.has_negation
        }
        
        return space.project_from_surface(features)
    
    def get_maqam(self) -> MaqamVector:
        """الحصول على M (المُعطى أو المُستنتج)"""
        if self.M_given is not None:
            return self.M_given
        return self.infer_maqam_from_surface()
    
    def __repr__(self) -> str:
        M = self.get_maqam()
        return (f"FullInput(\n"
                f"  words={self.surf.word_order},\n"
                f"  M_force={M.dominant_force().value},\n"
                f"  M_interrog={M.interrogative_type().value},\n"
                f"  M_request={M.request_type().value}\n"
                f")")
