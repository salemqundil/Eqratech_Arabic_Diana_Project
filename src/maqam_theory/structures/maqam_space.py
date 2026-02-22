"""
ترميز المقام كمتجه سمات في F_M ⊆ F
Maqam encoding as feature vector in F_M ⊆ F

M = (I, Q, A, C, T, N, E, H, O, J, S)

حيث:
- I: القوة الإنجازية (Illocutionary Force)
- Q: الاستفهام (polar/wh/alt)
- A: التنبيه (Attention/Alerting)
- C: الالتزام/التصديق (Commitment)
- T: الطلب (Request types)
- N: النفي (Negation)
- E: التوكيد (Emphasis)
- H: الحصر (Restriction)
- O: القسم (Oath)
- J: التعجب (Exclamation)
- S: النطاق والربط (Scope & Binding)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Tuple, Optional, Set
import math


class IllocutionaryForce(Enum):
    """القوة الإنجازية - Illocutionary Force"""
    KHABAR = "خبر"           # Declarative
    TALAB = "طلب"           # Request
    NIDA = "نداء"           # Vocative
    ISTIFHAM = "استفهام"    # Interrogative
    TAAJJUB = "تعجب"        # Exclamative
    QASAM = "قسم"           # Oath
    TARAJJI = "ترجي"        # Optative (hope)
    TAMANNI = "تمني"        # Wish
    SHART = "شرط"           # Conditional


class InterrogativeType(Enum):
    """أنواع الاستفهام"""
    NONE = "لا"
    POLAR = "قطبي"         # Yes/No (هل/الهمزة)
    WH = "استفهامي"         # Wh-question (من/ما/أين/متى...)
    ALTERNATIVE = "تعييني"  # Alternative (أ...أم...)


class RequestType(Enum):
    """أنواع الطلب"""
    NONE = "لا"
    AMR = "أمر"            # Command
    NAHY = "نهي"           # Prohibition
    ILTIMAS = "التماس"     # Request (polite)
    DUA = "دعاء"          # Supplication
    ISTIFHAM = "استفهام"   # Question (as request)


@dataclass
class MaqamVector:
    """
    متجه المقام M ∈ F_M
    
    كل مركبة scalar في [0, 1] تمثل "قوة/احتمال" تفعيل البوابة
    """
    # I: القوة الإنجازية (vector of forces)
    i_khabar: float = 0.0
    i_talab: float = 0.0
    i_nida: float = 0.0
    i_istifham: float = 0.0
    i_taajjub: float = 0.0
    i_qasam: float = 0.0
    i_tarajji: float = 0.0
    i_tamanni: float = 0.0
    i_shart: float = 0.0
    
    # Q: الاستفهام (q_polar, q_wh, q_alt)
    q_polar: float = 0.0
    q_wh: float = 0.0
    q_alt: float = 0.0
    
    # A: التنبيه
    attention: float = 0.0
    
    # C: الالتزام/التصديق (للخبر)
    commitment: float = 0.0
    
    # T: الطلب
    t_amr: float = 0.0
    t_nahy: float = 0.0
    t_iltimas: float = 0.0
    t_dua: float = 0.0
    t_istifham: float = 0.0
    
    # N: النفي
    negation: float = 0.0
    
    # E: التوكيد
    emphasis: float = 0.0
    
    # H: الحصر/القصر
    restriction: float = 0.0
    
    # O: القسم
    oath: float = 0.0
    
    # J: التعجب/الانفعال
    exclamation: float = 0.0
    
    def __post_init__(self):
        """التحقق من أن كل القيم في [0, 1]"""
        for field_name in [
            'i_khabar', 'i_talab', 'i_nida', 'i_istifham', 'i_taajjub',
            'i_qasam', 'i_tarajji', 'i_tamanni', 'i_shart',
            'q_polar', 'q_wh', 'q_alt',
            'attention', 'commitment',
            't_amr', 't_nahy', 't_iltimas', 't_dua', 't_istifham',
            'negation', 'emphasis', 'restriction', 'oath', 'exclamation'
        ]:
            value = getattr(self, field_name)
            if not (0.0 <= value <= 1.0):
                raise ValueError(f"{field_name} must be in [0, 1], got {value}")
    
    def dominant_force(self) -> IllocutionaryForce:
        """القوة الإنجازية المهيمنة"""
        forces = {
            IllocutionaryForce.KHABAR: self.i_khabar,
            IllocutionaryForce.TALAB: self.i_talab,
            IllocutionaryForce.NIDA: self.i_nida,
            IllocutionaryForce.ISTIFHAM: self.i_istifham,
            IllocutionaryForce.TAAJJUB: self.i_taajjub,
            IllocutionaryForce.QASAM: self.i_qasam,
            IllocutionaryForce.TARAJJI: self.i_tarajji,
            IllocutionaryForce.TAMANNI: self.i_tamanni,
            IllocutionaryForce.SHART: self.i_shart
        }
        return max(forces.items(), key=lambda x: x[1])[0]
    
    def interrogative_type(self) -> InterrogativeType:
        """نوع الاستفهام المهيمن"""
        if self.q_wh > max(self.q_polar, self.q_alt):
            return InterrogativeType.WH
        elif self.q_polar > self.q_alt:
            return InterrogativeType.POLAR
        elif self.q_alt > 0:
            return InterrogativeType.ALTERNATIVE
        return InterrogativeType.NONE
    
    def request_type(self) -> RequestType:
        """نوع الطلب المهيمن"""
        requests = {
            RequestType.AMR: self.t_amr,
            RequestType.NAHY: self.t_nahy,
            RequestType.ILTIMAS: self.t_iltimas,
            RequestType.DUA: self.t_dua,
            RequestType.ISTIFHAM: self.t_istifham
        }
        max_type, max_val = max(requests.items(), key=lambda x: x[1])
        return max_type if max_val > 0 else RequestType.NONE
    
    def to_vector(self) -> List[float]:
        """تحويل إلى vector عددي"""
        return [
            self.i_khabar, self.i_talab, self.i_nida, self.i_istifham,
            self.i_taajjub, self.i_qasam, self.i_tarajji, self.i_tamanni, self.i_shart,
            self.q_polar, self.q_wh, self.q_alt,
            self.attention, self.commitment,
            self.t_amr, self.t_nahy, self.t_iltimas, self.t_dua, self.t_istifham,
            self.negation, self.emphasis, self.restriction, self.oath, self.exclamation
        ]
    
    @classmethod
    def from_vector(cls, vec: List[float]) -> 'MaqamVector':
        """بناء من vector عددي"""
        if len(vec) != 24:
            raise ValueError(f"Expected 24 components, got {len(vec)}")
        return cls(
            i_khabar=vec[0], i_talab=vec[1], i_nida=vec[2], i_istifham=vec[3],
            i_taajjub=vec[4], i_qasam=vec[5], i_tarajji=vec[6], i_tamanni=vec[7], i_shart=vec[8],
            q_polar=vec[9], q_wh=vec[10], q_alt=vec[11],
            attention=vec[12], commitment=vec[13],
            t_amr=vec[14], t_nahy=vec[15], t_iltimas=vec[16], t_dua=vec[17], t_istifham=vec[18],
            negation=vec[19], emphasis=vec[20], restriction=vec[21], oath=vec[22], exclamation=vec[23]
        )
    
    def norm(self) -> float:
        """L2 norm of vector"""
        return math.sqrt(sum(x**2 for x in self.to_vector()))


@dataclass
class ScopeGraph:
    """
    رسم نطاق للعوامل (Scope Graph)
    
    يحدد نطاق تأثير: النفي، الاستفهام، الشرط، الحصر، القسم...
    """
    nodes: List[str] = field(default_factory=list)  # عقد (عوامل/كلمات)
    edges: List[Tuple[str, str, str]] = field(default_factory=list)  # (من، إلى، نوع)
    scope_map: Dict[str, Set[str]] = field(default_factory=dict)  # عامل → مجاله
    
    def add_operator(self, op_id: str, op_type: str):
        """إضافة عامل"""
        if op_id not in self.nodes:
            self.nodes.append(op_id)
            self.scope_map[op_id] = set()
    
    def add_scope_edge(self, operator: str, target: str, edge_type: str = "c-command"):
        """إضافة حافة نطاق"""
        self.edges.append((operator, target, edge_type))
        if operator in self.scope_map:
            self.scope_map[operator].add(target)
        else:
            self.scope_map[operator] = {target}
    
    def get_scope(self, operator: str) -> Set[str]:
        """الحصول على نطاق عامل"""
        return self.scope_map.get(operator, set())
    
    def is_in_scope(self, operator: str, target: str) -> bool:
        """هل target في نطاق operator؟"""
        return target in self.get_scope(operator)


@dataclass
class BindingMap:
    """
    خريطة ربط المتغيرات (Binding Map)
    
    تربط أدوات الاستفهام/الشرط/النسبية بمواضعها/آثارها
    """
    bindings: Dict[str, str] = field(default_factory=dict)  # متغير → موضعه
    traces: Dict[str, str] = field(default_factory=dict)    # أثر → أصله
    wh_variables: Set[str] = field(default_factory=set)     # متغيرات استفهامية
    
    def bind(self, variable: str, position: str):
        """ربط متغير بموضع"""
        self.bindings[variable] = position
    
    def add_trace(self, trace_id: str, source: str):
        """إضافة أثر"""
        self.traces[trace_id] = source
    
    def add_wh_variable(self, var: str, var_type: str):
        """إضافة متغير استفهامي"""
        self.wh_variables.add(var)
        self.bindings[var] = var_type
    
    def get_binding(self, variable: str) -> Optional[str]:
        """الحصول على ربط متغير"""
        return self.bindings.get(variable)
    
    def is_bound(self, variable: str) -> bool:
        """هل المتغير مربوط؟"""
        return variable in self.bindings
    
    def all_wh_bound(self) -> bool:
        """هل كل متغيرات الاستفهام مربوطة؟"""
        return all(self.is_bound(var) for var in self.wh_variables)


@dataclass
class MaqamSpace:
    """
    فضاء المقام F_M ⊆ F
    
    يحدد:
    - البعد dimension
    - القيود constraints
    - الإسقاطات projections
    """
    dimension: int = 24  # عدد المركبات في M
    
    def project_from_surface(self, surface_features: Dict[str, any]) -> MaqamVector:
        """
        إسقاط من السطح إلى M
        
        مثلاً: وجود "هل" → q_polar = 1.0
                وجود "من/ما/أين" → q_wh = 1.0
                صيغة أمر → t_amr = 1.0
        """
        M = MaqamVector()
        
        # استفهام
        if surface_features.get('has_hal'):
            M.q_polar = 1.0
            M.i_istifham = 1.0
        if surface_features.get('has_wh_word'):
            M.q_wh = 1.0
            M.i_istifham = 1.0
        if surface_features.get('has_am'):
            M.q_alt = 1.0
            M.i_istifham = 1.0
        
        # نداء
        if surface_features.get('has_ya'):
            M.i_nida = 1.0
            M.attention = 0.8
        
        # أمر
        if surface_features.get('is_imperative_form'):
            M.t_amr = 1.0
            M.i_talab = 1.0
        
        # نهي
        if surface_features.get('has_la_nahia'):
            M.t_nahy = 1.0
            M.i_talab = 1.0
            M.negation = 1.0
        
        # تعجب
        if surface_features.get('has_ma_ta3ajjub'):
            M.i_taajjub = 1.0
            M.exclamation = 1.0
        
        # توكيد
        if surface_features.get('has_inna'):
            M.emphasis = 1.0
        if surface_features.get('has_lam_tawkid'):
            M.emphasis = 0.8
        
        # نفي
        if surface_features.get('has_negation'):
            M.negation = 1.0
        
        # خبر (default)
        if M.norm() < 0.1:  # إذا لم يُفعّل شيء
            M.i_khabar = 1.0
            M.commitment = 0.7
        
        return M
    
    def is_valid(self, M: MaqamVector) -> bool:
        """
        هل M صحيح؟
        
        قيود:
        - كل مركبة في [0, 1]
        - مجموع I ≤ 2.0 (قد تتداخل قوتان)
        - إذا q_wh > 0 فيجب i_istifham > 0
        """
        # قيود الحدود
        try:
            M.__post_init__()
        except ValueError:
            return False
        
        # قيد مجموع القوى
        total_force = (M.i_khabar + M.i_talab + M.i_nida + M.i_istifham +
                      M.i_taajjub + M.i_qasam + M.i_tarajji + M.i_tamanni + M.i_shart)
        if total_force > 2.0:
            return False
        
        # قيد الاستفهام
        if (M.q_wh > 0 or M.q_polar > 0 or M.q_alt > 0) and M.i_istifham < 0.1:
            return False
        
        # قيد الطلب
        if (M.t_amr > 0 or M.t_nahy > 0 or M.t_iltimas > 0 or M.t_dua > 0) and M.i_talab < 0.1:
            return False
        
        return True
    
    def distance(self, M1: MaqamVector, M2: MaqamVector) -> float:
        """المسافة الإقليدية بين متجهين"""
        v1 = M1.to_vector()
        v2 = M2.to_vector()
        return math.sqrt(sum((a - b)**2 for a, b in zip(v1, v2)))
