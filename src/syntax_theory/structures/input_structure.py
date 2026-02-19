"""
تعريف المدخل الصحيح x ∈ X_valid
================================

x := (L, T, I, B)

L: قائمة وحدات Lexical Atoms (جذور/أوزان/مبنيات/أدوات)
T: أهداف صرفية/صوتية لكل وحدة
I: قصد تركيبي-دلالي (متطلبات وظيفية)
B: حد طول/تعقيد

كل وحدة في L تحمل نوعًا (Type):
N, V, P, Part, Pron, Dem, Adj, Adv...
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from enum import Enum, auto


class LexicalType(Enum):
    """أنواع الوحدات المعجمية (Typing)"""
    N = auto()      # اسم
    V = auto()      # فعل
    P = auto()      # حرف جر
    Part = auto()   # أداة (إنّ، كان، لم، لن، لا...)
    Pron = auto()   # ضمير
    Dem = auto()    # إشارة
    Adj = auto()    # صفة
    Adv = auto()    # ظرف/حال
    Conj = auto()   # حرف عطف
    Rel = auto()    # موصول


class VerbValency(Enum):
    """تعدية الفعل (Valency)"""
    INTRANSITIVE = auto()  # لازم
    TRANSITIVE = auto()    # متعدٍّ لواحد
    DITRANSITIVE = auto()  # متعدٍّ لاثنين
    CAUSATIVE = auto()     # سببي (أفعل، فعّل...)


class SemanticRole(Enum):
    """الأدوار الدلالية"""
    AGENT = auto()      # الفاعل (من يفعل)
    PATIENT = auto()    # المفعول (من يقع عليه الفعل)
    THEME = auto()      # الموضوع
    CAUSE = auto()      # السبب
    EFFECT = auto()     # النتيجة/الأثر
    EXPERIENCER = auto()  # المُجرّب
    BENEFICIARY = auto()  # المستفيد
    INSTRUMENT = auto()   # الأداة
    LOCATION = auto()     # المكان
    TIME = auto()         # الزمان


@dataclass
class LexicalAtom:
    """
    وحدة معجمية واحدة (L_i)
    
    الحد الأدنى: نوع + مادة خام
    """
    atom_type: LexicalType
    raw_material: str  # جذر أو كلمة خام (ك-ت-ب، أحمد، في...)
    
    # أهداف صرفية/صوتية (من T)
    morphological_target: Optional[Dict[str, Any]] = None
    
    # سمات إضافية
    valency: Optional[VerbValency] = None  # للأفعال
    requires_case: bool = True  # هل قابل للإعراب؟
    is_built: bool = False  # مبني؟
    
    # متطلبات المبني
    requires_anchor: bool = False
    anchor_scope: Optional[str] = None  # "local", "clause", "sentence"
    join_policy: Optional[str] = None   # "must", "prefer", "forbid"
    
    def __hash__(self):
        return hash((self.atom_type, self.raw_material))
    
    def __eq__(self, other):
        if not isinstance(other, LexicalAtom):
            return False
        return (self.atom_type == other.atom_type and 
                self.raw_material == other.raw_material)


@dataclass
class IntentConstraint:
    """
    قيد وظيفي واحد من I (Minimal Intent)
    
    أمثلة:
    - "يجب وجود حكم واحد على الأقل"
    - "فعل متعدٍّ يحتاج مفعولًا"
    - "حرف جر يحتاج اسمًا"
    """
    constraint_type: str  # "REQUIRES_PROPOSITION", "REQUIRES_OBJECT", ...
    applies_to: Optional[LexicalAtom] = None
    required_role: Optional[SemanticRole] = None
    violation_cost: float = float('inf')  # كلفة الفشل (عادة ∞)
    
    def is_satisfied(self, graph) -> bool:
        """هل القيد مُشبع في الرسم البياني؟"""
        # سيتم تنفيذها في Graph
        raise NotImplementedError("يُحدد في السياق")


@dataclass
class SyntacticInput:
    """
    المدخل الصحيح x ∈ X_valid
    
    x := (L, T, I, B)
    """
    L: List[LexicalAtom] = field(default_factory=list)  # الوحدات المعجمية
    T: Dict[str, Any] = field(default_factory=dict)     # الأهداف الصرفية (مرتبطة بـL)
    I: List[IntentConstraint] = field(default_factory=list)  # القيود الوظيفية
    B: int = 20  # حد التعقيد (عدد العقد/الحواف)
    
    def is_valid(self) -> bool:
        """
        شرط الصحة:
        1. الأنواع في L متسقة
        2. المتطلبات في I قابلة للإشباع من حيث الأنواع
        3. B موجب
        """
        if self.B <= 0:
            return False
        
        if not self.L:
            return False
        
        # كل وحدة يجب أن يكون نوعها معرفًا
        for atom in self.L:
            if atom.atom_type is None:
                return False
        
        # التحقق من الأنواع: Typing-satisfiable
        # (مبسّط هنا: نفترض الأنواع متسقة إذا لم يوجد تعارض واضح)
        verb_count = sum(1 for a in self.L if a.atom_type == LexicalType.V)
        noun_count = sum(1 for a in self.L if a.atom_type == LexicalType.N or a.atom_type == LexicalType.Pron)
        
        # يجب وجود إمكانية حكم: فعل أو اسم
        if verb_count == 0 and noun_count == 0:
            return False
        
        # التحقق من قابلية إشباع القيود (مبسّط)
        for constraint in self.I:
            if constraint.constraint_type == "REQUIRES_OBJECT":
                # يحتاج اسمًا
                if noun_count == 0:
                    return False
        
        return True
    
    def extract_verb_atoms(self) -> List[LexicalAtom]:
        """استخراج الأفعال"""
        return [a for a in self.L if a.atom_type == LexicalType.V]
    
    def extract_noun_atoms(self) -> List[LexicalAtom]:
        """استخراج الأسماء"""
        return [a for a in self.L if a.atom_type in (LexicalType.N, LexicalType.Pron)]
    
    def extract_particles(self) -> List[LexicalAtom]:
        """استخراج الأدوات (إنّ، كان، لم...)"""
        return [a for a in self.L if a.atom_type == LexicalType.Part]
    
    def extract_prepositions(self) -> List[LexicalAtom]:
        """استخراج حروف الجر"""
        return [a for a in self.L if a.atom_type == LexicalType.P]
    
    def __repr__(self):
        atom_str = ", ".join([f"{a.raw_material}({a.atom_type.name})" for a in self.L])
        return f"x=({atom_str} | B={self.B} | I={len(self.I)} قيود)"


# مساعدات لبناء x بسرعة
def make_simple_input(
    verbs: List[str] = None,
    nouns: List[str] = None,
    prepositions: List[str] = None,
    particles: List[str] = None,
    bound: int = 20
) -> SyntacticInput:
    """
    إنشاء مدخل بسيط بسرعة
    
    مثال:
    >>> x = make_simple_input(
    ...     verbs=["كتب"],
    ...     nouns=["أحمد", "الرسالة"],
    ...     prepositions=["في"],
    ...     nouns_for_prep=["البيت"]
    ... )
    """
    atoms = []
    
    if verbs:
        for v in verbs:
            atoms.append(LexicalAtom(
                atom_type=LexicalType.V,
                raw_material=v,
                valency=VerbValency.TRANSITIVE  # افتراضي
            ))
    
    if nouns:
        for n in nouns:
            atoms.append(LexicalAtom(
                atom_type=LexicalType.N,
                raw_material=n
            ))
    
    if prepositions:
        for p in prepositions:
            atoms.append(LexicalAtom(
                atom_type=LexicalType.P,
                raw_material=p
            ))
    
    if particles:
        for part in particles:
            atoms.append(LexicalAtom(
                atom_type=LexicalType.Part,
                raw_material=part,
                is_built=True,
                requires_anchor=True
            ))
    
    # قيود افتراضية
    constraints = [
        IntentConstraint(
            constraint_type="REQUIRES_PROPOSITION",
            violation_cost=float('inf')
        )
    ]
    
    # إضافة قيود للأفعال المتعدية
    for atom in atoms:
        if atom.atom_type == LexicalType.V and atom.valency in (VerbValency.TRANSITIVE, VerbValency.DITRANSITIVE):
            constraints.append(IntentConstraint(
                constraint_type="REQUIRES_OBJECT",
                applies_to=atom,
                required_role=SemanticRole.PATIENT,
                violation_cost=float('inf')
            ))
    
    # قيود حروف الجر
    for atom in atoms:
        if atom.atom_type == LexicalType.P:
            constraints.append(IntentConstraint(
                constraint_type="REQUIRES_GOVERNED_NOUN",
                applies_to=atom,
                violation_cost=float('inf')
            ))
    
    return SyntacticInput(L=atoms, I=constraints, B=bound)
