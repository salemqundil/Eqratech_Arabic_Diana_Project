"""
نظام الأنواع للمحرك اللغوي العربي
Arabic NLP Type System - Python Implementation

هذا الملف يحول Typing Calculus + Type Policies إلى كود قابل للتنفيذ
مع فحص آلي للقوانين القاطعة (Hard Invariants)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Union, Literal
from enum import Enum, auto
import json


# ═══════════════════════════════════════════════════════════════════════
# 1) الأنواع الأساسية (Base Types)
# ═══════════════════════════════════════════════════════════════════════

class RootKind(Enum):
    """أنواع الجذور"""
    GENDER_ROOT = "GenderRoot"      # جامد/اسم جنس
    EVENT_ROOT = "EventRoot"        # فعل/حدث
    QUALITY_ROOT = "QualityRoot"    # صفة

class RefType(Enum):
    """أنواع المبنيات الإحالية"""
    PRONOUN = "PRONOUN"             # ضمير
    DEMONSTRATIVE = "DEMONSTRATIVE" # إشارة
    RELATIVE = "RELATIVE"           # موصول
    CONDITIONAL = "CONDITIONAL"     # اسم شرط

class Ma3aniToolClass(Enum):
    """أنواع أدوات المعاني"""
    NEG = "NEG"                     # نفي
    COND = "COND"                   # شرط
    EXCEPT = "EXCEPT"               # استثناء
    ONLY = "ONLY"                   # حصر
    EMPHASIS = "EMPHASIS"           # توكيد
    REASON = "REASON"               # تعليل
    PURPOSE = "PURPOSE"             # غاية
    RESULT = "RESULT"               # نتيجة
    SWEAR = "SWEAR"                 # قسم

class Capability(Enum):
    """القدرات (ما يمكن للعقدة فعله)"""
    CAN_WRITE_SUBJECT = auto()
    CAN_WRITE_PREDICATE = auto()
    CAN_PRODUCE_SCOPE = auto()
    CAN_PRODUCE_CONSTRAINT = auto()
    CAN_PRODUCE_REF = auto()
    CAN_INSTANTIATE_ROOT = auto()
    CAN_INSTANTIATE_QUALITY = auto()
    CAN_MODIFY = auto()

class ScopeOperatorType(Enum):
    """أنواع مشغلات النطاق"""
    NEG = "NEG"
    IF_THEN = "IF_THEN"
    EXCEPT = "EXCEPT"
    ONLY = "ONLY"
    FOR_ALL = "FOR_ALL"
    THERE_EXISTS = "THERE_EXISTS"
    EMPHASIS = "EMPHASIS"


# ═══════════════════════════════════════════════════════════════════════
# 2) العقد (Nodes)
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class Node:
    """عقدة أساسية"""
    id: str
    capabilities: Set[Capability] = field(default_factory=set)
    
    def has_capability(self, cap: Capability) -> bool:
        """فحص: هل العقدة تملك القدرة؟"""
        return cap in self.capabilities


@dataclass
class TokenNode(Node):
    """عقدة وحدة سطحية (كلمة/أداة)"""
    surface: str = ""
    tags: List[str] = field(default_factory=list)
    phon_form: Optional[str] = None
    syllables: Optional[List] = None
    morph: Optional[Dict] = None
    syntax_role: Optional[str] = None


@dataclass
class RootNode(Node):
    """عقدة جذر"""
    radicals: List[str] = field(default_factory=list)
    root_kind: RootKind = RootKind.GENDER_ROOT
    
    def __post_init__(self):
        """تعيين القدرات بناءً على نوع الجذر"""
        if self.root_kind == RootKind.GENDER_ROOT:
            self.capabilities.add(Capability.CAN_WRITE_SUBJECT)
        elif self.root_kind == RootKind.EVENT_ROOT:
            self.capabilities.add(Capability.CAN_WRITE_SUBJECT)
            self.capabilities.add(Capability.CAN_WRITE_PREDICATE)
        elif self.root_kind == RootKind.QUALITY_ROOT:
            self.capabilities.add(Capability.CAN_MODIFY)


@dataclass
class Ma3aniToolNode(Node):
    """عقدة أداة معاني - القانون القاطع 5.1 مطبق هنا"""
    tool_class: Ma3aniToolClass = Ma3aniToolClass.NEG
    
    def __post_init__(self):
        """تعيين القدرات: فقط Scope + Constraint"""
        self.capabilities.add(Capability.CAN_PRODUCE_SCOPE)
        self.capabilities.add(Capability.CAN_PRODUCE_CONSTRAINT)
        # ممنوع: CAN_WRITE_SUBJECT, CAN_WRITE_PREDICATE


@dataclass
class MabniRefNode(Node):
    """عقدة مبني إحالي - القانون القاطع 5.2 مطبق هنا"""
    ref_type: RefType = RefType.PRONOUN
    
    def __post_init__(self):
        """تعيين القدرات: فقط Ref"""
        self.capabilities.add(Capability.CAN_PRODUCE_REF)
        # ممنوع: CAN_INSTANTIATE_ROOT, CAN_INSTANTIATE_QUALITY


@dataclass
class RefNode(Node):
    """عقدة مرجع (ناتجة من MabniRefNode عبر Gate)"""
    ref_source: str = ""  # id of source MabniRefNode
    antecedent: Optional[str] = None  # id of antecedent
    restrictors: List[str] = field(default_factory=list)


@dataclass
class ScopeOperatorNode(Node):
    """عقدة مشغل نطاق"""
    operator_type: ScopeOperatorType = ScopeOperatorType.NEG
    arity: int = 1
    span: tuple = field(default_factory=tuple)
    priority: int = 0
    effect: str = ""


# ═══════════════════════════════════════════════════════════════════════
# 3) القرارات الدلالية (Semantic Constructs)
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class LinguisticJudgment:
    """
    الحكم اللغوي J = (Subject, Predicate, Constraints, Scope)
    
    ملاحظة: هذا ليس حكمًا منطقيًا (True/False)
    بل استخراج لغوي فقط
    """
    subject: Optional[str] = None       # id of subject node
    predicate: Optional[str] = None     # id of predicate node
    constraints: List[str] = field(default_factory=list)  # constraint ids
    scope: List[str] = field(default_factory=list)        # scope operator ids
    
    def __repr__(self):
        return f"J(subj={self.subject}, pred={self.predicate}, scope={len(self.scope)}, constr={len(self.constraints)})"


# ═══════════════════════════════════════════════════════════════════════
# 4) البوابات (Gates)
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class GateApplication:
    """تسجيل تطبيق بوابة (للبرهنة والتتبع)"""
    gate_type: str
    input_node_id: str
    output_node_id: str
    trace: Dict = field(default_factory=dict)


class Gate:
    """بوابة أساسية"""
    def apply(self, input_node: Node) -> Node:
        raise NotImplementedError


class Ma3aniScopeGate(Gate):
    """بوابة: Ma3aniToolNode → ScopeOperatorNode"""
    
    MAPPING = {
        Ma3aniToolClass.NEG: ScopeOperatorType.NEG,
        Ma3aniToolClass.COND: ScopeOperatorType.IF_THEN,
        Ma3aniToolClass.EXCEPT: ScopeOperatorType.EXCEPT,
        Ma3aniToolClass.ONLY: ScopeOperatorType.ONLY,
    }
    
    def apply(self, input_node: Ma3aniToolNode) -> ScopeOperatorNode:
        """تحويل أداة معاني إلى مشغل نطاق"""
        if not isinstance(input_node, Ma3aniToolNode):
            raise TypeError(f"Expected Ma3aniToolNode, got {type(input_node)}")
        
        op_type = self.MAPPING.get(input_node.tool_class, ScopeOperatorType.NEG)
        
        return ScopeOperatorNode(
            id=f"scope_{input_node.id}",
            operator_type=op_type,
            arity=1,
            effect=op_type.value
        )


class MabniRefGate(Gate):
    """بوابة: MabniRefNode → RefNode"""
    
    def apply(self, input_node: MabniRefNode) -> RefNode:
        """تحويل مبني إلى مرجع"""
        if not isinstance(input_node, MabniRefNode):
            raise TypeError(f"Expected MabniRefNode, got {type(input_node)}")
        
        return RefNode(
            id=f"ref_{input_node.id}",
            ref_source=input_node.id
        )


class DerivationGate(Gate):
    """بوابة: RootNode(kind₁) → RootNode(kind₂) + trace"""
    
    def __init__(self, from_kind: RootKind, to_kind: RootKind):
        self.from_kind = from_kind
        self.to_kind = to_kind
    
    def apply(self, input_node: RootNode) -> tuple[RootNode, GateApplication]:
        """تحويل نوع الجذر مع توثيق"""
        if not isinstance(input_node, RootNode):
            raise TypeError(f"Expected RootNode, got {type(input_node)}")
        
        if input_node.root_kind != self.from_kind:
            raise ValueError(f"Root kind mismatch: expected {self.from_kind}, got {input_node.root_kind}")
        
        # Create new node with changed kind
        output_node = RootNode(
            id=f"{input_node.id}_derived",
            radicals=input_node.radicals,
            root_kind=self.to_kind
        )
        
        # Record trace
        trace = GateApplication(
            gate_type=f"DerivationGate({self.from_kind.value}→{self.to_kind.value})",
            input_node_id=input_node.id,
            output_node_id=output_node.id,
            trace={
                "from_kind": self.from_kind.value,
                "to_kind": self.to_kind.value,
                "radicals": input_node.radicals
            }
        )
        
        return output_node, trace


# ═══════════════════════════════════════════════════════════════════════
# 5) نظام الفحص (Type Checker)
# ═══════════════════════════════════════════════════════════════════════

class TypeViolation(Exception):
    """انتهاك قاعدة نوع → خطأ نوع → ∞ cost"""
    def __init__(self, rule_id: str, message: str):
        self.rule_id = rule_id
        self.message = message
        super().__init__(f"[{rule_id}] {message}")


class TypeChecker:
    """فاحص الأنواع - يطبق Hard Invariants"""
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.traces: List[GateApplication] = []
    
    def register_node(self, node: Node):
        """تسجيل عقدة"""
        self.nodes[node.id] = node
    
    def check_write_subject(self, node: Node, J: LinguisticJudgment):
        """
        فحص القانون 5.1: فحص كتابة Subject
        
        ممنوع: Ma3aniToolNode تكتب Subject
        """
        if isinstance(node, Ma3aniToolNode):
            raise TypeViolation(
                "INV_MA3ANI_5.1",
                f"Ma3aniToolNode ({node.id}) cannot write Subject"
            )
        
        if not node.has_capability(Capability.CAN_WRITE_SUBJECT):
            raise TypeViolation(
                "CAP_CHECK",
                f"Node ({node.id}) lacks CAN_WRITE_SUBJECT capability"
            )
        
        # إذا نجح الفحص
        J.subject = node.id
    
    def check_write_predicate(self, node: Node, J: LinguisticJudgment):
        """
        فحص القانون 5.1: فحص كتابة Predicate
        
        ممنوع: Ma3aniToolNode تكتب Predicate
        """
        if isinstance(node, Ma3aniToolNode):
            raise TypeViolation(
                "INV_MA3ANI_5.1",
                f"Ma3aniToolNode ({node.id}) cannot write Predicate"
            )
        
        if not node.has_capability(Capability.CAN_WRITE_PREDICATE):
            raise TypeViolation(
                "CAP_CHECK",
                f"Node ({node.id}) lacks CAN_WRITE_PREDICATE capability"
            )
        
        # إذا نجح الفحص
        J.predicate = node.id
    
    def check_produce_scope(self, node: Node, J: LinguisticJudgment, scope_op_id: str):
        """فحص: إنتاج Scope"""
        if not node.has_capability(Capability.CAN_PRODUCE_SCOPE):
            raise TypeViolation(
                "CAP_CHECK",
                f"Node ({node.id}) lacks CAN_PRODUCE_SCOPE capability"
            )
        
        J.scope.append(scope_op_id)
    
    def check_instantiate_root(self, node: Node):
        """
        فحص القانون 5.2: فحص instantiation كجذر
        
        ممنوع: MabniRefNode تُعامل كجذر
        """
        if isinstance(node, MabniRefNode):
            raise TypeViolation(
                "INV_MABNI_5.2",
                f"MabniRefNode ({node.id}) cannot be instantiated as Root"
            )
        
        if not node.has_capability(Capability.CAN_INSTANTIATE_ROOT):
            raise TypeViolation(
                "CAP_CHECK",
                f"Node ({node.id}) lacks CAN_INSTANTIATE_ROOT capability"
            )
    
    def check_root_kind_change(self, old_kind: RootKind, new_kind: RootKind, 
                               gate_trace: Optional[GateApplication]):
        """
        فحص القانون 5.3: تغيير root_kind يتطلب Gate + trace
        """
        if old_kind == new_kind:
            return  # no change
        
        if gate_trace is None:
            raise TypeViolation(
                "INV_DERIVATION",
                f"Root kind change ({old_kind} → {new_kind}) requires DerivationGate with trace"
            )
        
        if "DerivationGate" not in gate_trace.gate_type:
            raise TypeViolation(
                "INV_DERIVATION",
                f"Root kind change requires DerivationGate, got {gate_trace.gate_type}"
            )
        
        # تسجيل trace
        self.traces.append(gate_trace)
    
    def validate_graph(self) -> bool:
        """فحص شامل للرسم"""
        # يمكن إضافة فحوصات أخرى هنا
        return True


# ═══════════════════════════════════════════════════════════════════════
# 6) مثال: بناء "من يكذب يعاقب" مع Type Checking
# ═══════════════════════════════════════════════════════════════════════

def example_man_yakdhib_yuaqab():
    """
    مثال: من يكذب يعاقب
    
    Step 1: من → Ma3aniToolNode
    Step 2: Ma3aniScopeGate → ScopeOp(IF_THEN)
    Step 3: يكذب → RootNode(EventRoot) → Predicate
    Step 4: يعاقب → RootNode(EventRoot) → Predicate
    """
    
    print("=" * 70)
    print("مثال: من يكذب يعاقب")
    print("=" * 70)
    
    checker = TypeChecker()
    J = LinguisticJudgment()
    
    # Step 1: من
    print("\nStep 1: تسجيل 'من' كأداة معاني")
    token1 = TokenNode(id="t1", surface="من")
    ma3ani1 = Ma3aniToolNode(id="m1", tool_class=Ma3aniToolClass.COND)
    checker.register_node(token1)
    checker.register_node(ma3ani1)
    print(f"  ✓ Ma3aniToolNode registered: {ma3ani1.id}")
    print(f"    Capabilities: {[c.name for c in ma3ani1.capabilities]}")
    
    # Step 2: تطبيق Ma3aniScopeGate
    print("\nStep 2: تطبيق Ma3aniScopeGate")
    gate1 = Ma3aniScopeGate()
    scope_op = gate1.apply(ma3ani1)
    checker.register_node(scope_op)
    print(f"  ✓ ScopeOperator created: {scope_op.id}")
    print(f"    Type: {scope_op.operator_type.value}")
    
    # Step 3: إضافة Scope إلى J
    print("\nStep 3: إضافة Scope إلى J")
    try:
        checker.check_produce_scope(ma3ani1, J, scope_op.id)
        print(f"  ✓ Scope added to J: {J.scope}")
    except TypeViolation as e:
        print(f"  ✗ Type violation: {e}")
        return
    
    # Step 4: محاولة فاشلة - Ma3aniTool تكتب Predicate
    print("\nStep 4: محاولة (فاشلة): Ma3aniTool تكتب Predicate")
    try:
        checker.check_write_predicate(ma3ani1, J)
        print("  ✓ Predicate written (this should not happen!)")
    except TypeViolation as e:
        print(f"  ✗ Type violation (expected): [{e.rule_id}] {e.message}")
    
    # Step 5: يكذب - RootNode(EventRoot)
    print("\nStep 5: تسجيل 'يكذب' كجذر حدث")
    root2 = RootNode(id="r2", radicals=["ك", "ذ", "ب"], root_kind=RootKind.EVENT_ROOT)
    checker.register_node(root2)
    print(f"  ✓ RootNode registered: {root2.id}")
    print(f"    Kind: {root2.root_kind.value}")
    print(f"    Capabilities: {[c.name for c in root2.capabilities]}")
    
    # Step 6: EventRoot يكتب Predicate
    print("\nStep 6: EventRoot يكتب Predicate")
    try:
        checker.check_write_predicate(root2, J)
        print(f"  ✓ Predicate written: {J.predicate}")
    except TypeViolation as e:
        print(f"  ✗ Type violation: {e}")
        return
    
    # Final J
    print("\n" + "=" * 70)
    print("النتيجة النهائية:")
    print("=" * 70)
    print(f"  {J}")
    print(f"  Scope operators: {J.scope}")
    print(f"  Subject: {J.subject}")
    print(f"  Predicate: {J.predicate}")
    print("\n✓ All type checks passed!")


def example_invalid_mabni_as_root():
    """
    مثال: محاولة فاشلة - معاملة 'هو' كجذر
    """
    
    print("\n" + "=" * 70)
    print("مثال: محاولة فاشلة - 'هو' كجذر")
    print("=" * 70)
    
    checker = TypeChecker()
    
    # Step 1: هو
    print("\nStep 1: تسجيل 'هو' كمبني")
    mabni = MabniRefNode(id="mb1", ref_type=RefType.PRONOUN)
    checker.register_node(mabni)
    print(f"  ✓ MabniRefNode registered: {mabni.id}")
    print(f"    Capabilities: {[c.name for c in mabni.capabilities]}")
    
    # Step 2: محاولة instantiate as root
    print("\nStep 2: محاولة instantiate as root")
    try:
        checker.check_instantiate_root(mabni)
        print("  ✓ Instantiated as root (this should not happen!)")
    except TypeViolation as e:
        print(f"  ✗ Type violation (expected): [{e.rule_id}] {e.message}")
    
    # Step 3: الطريقة الصحيحة - MabniRefGate
    print("\nStep 3: الطريقة الصحيحة - استخدام MabniRefGate")
    gate = MabniRefGate()
    ref_node = gate.apply(mabni)
    checker.register_node(ref_node)
    print(f"  ✓ RefNode created: {ref_node.id}")
    print(f"    Source: {ref_node.ref_source}")


def example_root_derivation():
    """
    مثال: تحويل نوع الجذر عبر DerivationGate
    
    GenderRoot → QualityRoot (adjectivization)
    """
    
    print("\n" + "=" * 70)
    print("مثال: تحويل جذر جامد → صفة")
    print("=" * 70)
    
    checker = TypeChecker()
    
    # Step 1: جذر جامد
    print("\nStep 1: إنشاء جذر جامد (كتاب)")
    root = RootNode(id="r1", radicals=["ك", "ت", "ب"], root_kind=RootKind.GENDER_ROOT)
    checker.register_node(root)
    print(f"  ✓ RootNode: {root.id}, kind={root.root_kind.value}")
    print(f"    Capabilities: {[c.name for c in root.capabilities]}")
    
    # Step 2: محاولة بدون Gate
    print("\nStep 2: محاولة تغيير نوع بدون Gate")
    try:
        checker.check_root_kind_change(
            RootKind.GENDER_ROOT, 
            RootKind.QUALITY_ROOT, 
            gate_trace=None
        )
        print("  ✓ Changed without gate (this should not happen!)")
    except TypeViolation as e:
        print(f"  ✗ Type violation (expected): [{e.rule_id}] {e.message}")
    
    # Step 3: استخدام DerivationGate
    print("\nStep 3: استخدام DerivationGate")
    gate = DerivationGate(
        from_kind=RootKind.GENDER_ROOT,
        to_kind=RootKind.QUALITY_ROOT
    )
    
    derived_root, trace = gate.apply(root)
    checker.register_node(derived_root)
    print(f"  ✓ Derived RootNode: {derived_root.id}, kind={derived_root.root_kind.value}")
    print(f"    Gate type: {trace.gate_type}")
    print(f"    Capabilities: {[c.name for c in derived_root.capabilities]}")
    
    # Step 4: تسجيل trace
    print("\nStep 4: فحص trace")
    checker.check_root_kind_change(
        RootKind.GENDER_ROOT,
        RootKind.QUALITY_ROOT,
        gate_trace=trace
    )
    print(f"  ✓ Trace validated and recorded")
    print(f"    Total traces: {len(checker.traces)}")


# ═══════════════════════════════════════════════════════════════════════
# 7) Main
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Run examples
    example_man_yakdhib_yuaqab()
    example_invalid_mabni_as_root()
    example_root_derivation()
    
    print("\n" + "=" * 70)
    print("✓ All examples completed successfully")
    print("=" * 70)
