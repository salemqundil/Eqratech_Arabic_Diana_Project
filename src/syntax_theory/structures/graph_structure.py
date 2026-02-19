"""
تعريف الشكل الناتج y: رسم بياني Typed Graph
===========================================

y := (V_y, E_y, τ, φ)

V_y: عقد (توكنات + عوامل + علاقات)
E_y: حواف من ثلاث عائلات:
     - ISN (الإسناد): h → s
     - TADMN (التضمين): h ⇒ C
     - TAQYID (التقييد): h ⊣ m

τ: تعيين الأنواع (Typing)
φ: سمات (صرف، إعراب، أدوار دلالية...)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set, Tuple
from enum import Enum, auto
import uuid

from .input_structure import LexicalAtom, LexicalType, SemanticRole


class EdgeType(Enum):
    """أنواع الحواف (العلاقات الثلاث)"""
    ISN = auto()      # الإسناد (Predication)
    TADMN = auto()    # التضمين (Embedding)
    TAQYID = auto()   # التقييد (Modification)
    GOV = auto()      # تطبيق عامل (Governor application)


class CaseMarking(Enum):
    """علامات الإعراب (للمعرب)"""
    NOM = auto()  # مرفوع
    ACC = auto()  # منصوب
    GEN = auto()  # مجرور


class MoodMarking(Enum):
    """علامات المضارع (للأفعال)"""
    IND = auto()   # مرفوع (الإخبار)
    SUB = auto()   # منصوب (النصب)
    JUSS = auto()  # مجزوم (الجزم)


@dataclass
class NodeFeatures:
    """
    سمات العقدة φ
    
    تشمل:
    - سمات صرف/صوت (من نظام اللفظ المفرد)
    - سمات إعرابية (case, mood) للمعرب
    - سمات مبني (locked, anchor, join, scope)
    - أدوار دلالية (Agent, Patient, Cause...)
    """
    # سمات صرفية/صوتية
    phonological_form: Optional[str] = None  # الشكل الصوتي (من نظام اللفظ)
    morphological_pattern: Optional[str] = None
    
    # سمات إعرابية (للمعرب)
    is_declinable: bool = True  # معرب؟
    case: Optional[CaseMarking] = None
    mood: Optional[MoodMarking] = None
    
    # سمات مبني (للمبني)
    is_locked: bool = False  # مبني (locked=1)
    anchor: Optional[str] = None  # ما الذي يتعلق به؟
    join_status: Optional[str] = None  # "متصل" أو "منفصل"
    scope: Optional[str] = None  # "local", "clause", "sentence"
    
    # أدوار دلالية (متغيرات يتم تعيينها)
    semantic_role: Optional[SemanticRole] = None
    
    # سمات إضافية
    definiteness: Optional[bool] = None  # معرفة/نكرة
    number: Optional[str] = None  # مفرد/مثنى/جمع
    gender: Optional[str] = None  # مذكر/مؤنث
    
    def clone(self):
        """نسخ السمات"""
        return NodeFeatures(
            phonological_form=self.phonological_form,
            morphological_pattern=self.morphological_pattern,
            is_declinable=self.is_declinable,
            case=self.case,
            mood=self.mood,
            is_locked=self.is_locked,
            anchor=self.anchor,
            join_status=self.join_status,
            scope=self.scope,
            semantic_role=self.semantic_role,
            definiteness=self.definiteness,
            number=self.number,
            gender=self.gender
        )


@dataclass
class Node:
    """
    عقدة في الرسم البياني
    
    يمكن أن تكون:
    - توكن (كلمة/مبني)
    - عامل (إنّ، كان، لم...)
    - علاقة (إن احتجنا فصلها)
    """
    node_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    node_type: str = "TOKEN"  # "TOKEN", "GOVERNOR", "RELATION"
    
    # المادة الأساسية
    lexical_atom: Optional[LexicalAtom] = None
    
    # السمات
    features: NodeFeatures = field(default_factory=NodeFeatures)
    
    # للعوامل: توقيع (Signature)
    operator_signature: Optional[Dict[str, Any]] = None
    
    def __hash__(self):
        return hash(self.node_id)
    
    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.node_id == other.node_id
    
    def __repr__(self):
        if self.lexical_atom:
            return f"Node({self.lexical_atom.raw_material}, {self.node_type})"
        return f"Node({self.node_id}, {self.node_type})"


@dataclass
class Edge:
    """
    حافة في الرسم البياني
    
    أنواع العلاقات:
    - ISN(h → s): الإسناد
    - TADMN(h ⇒ C): التضمين
    - TAQYID(h ⊣ m): التقييد
    - GOV(A → t): تطبيق عامل
    """
    # الحقول الإلزامية أولاً
    edge_type: EdgeType
    source: Node  # الرأس (h) أو العامل (A)
    target: Node  # المسند إليه (s) أو التكملة (C) أو المقيد (m) أو المحكوم (t)
    
    # الحقول الاختيارية ثانيًا
    edge_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    label: Optional[str] = None  # "subj", "obj", "modifier"...
    weight: float = 1.0  # وزن (قد نستخدمه في الكلفة)
    
    def __hash__(self):
        return hash(self.edge_id)
    
    def __eq__(self, other):
        if not isinstance(other, Edge):
            return False
        return self.edge_id == other.edge_id
    
    def __repr__(self):
        return f"Edge({self.edge_type.name}: {self.source} → {self.target})"


@dataclass
class SyntacticGraph:
    """
    الرسم البياني للجملة y
    
    y := (V_y, E_y, τ, φ)
    """
    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    
    # تعيين الأنواع τ (مخزن في Node.lexical_atom.atom_type)
    # سمات φ (مخزنة في Node.features)
    
    graph_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def add_node(self, node: Node):
        """إضافة عقدة"""
        if node not in self.nodes:
            self.nodes.append(node)
    
    def add_edge(self, edge: Edge):
        """إضافة حافة"""
        # تأكد من وجود العقد
        if edge.source not in self.nodes:
            self.add_node(edge.source)
        if edge.target not in self.nodes:
            self.add_node(edge.target)
        
        if edge not in self.edges:
            self.edges.append(edge)
    
    def get_edges_by_type(self, edge_type: EdgeType) -> List[Edge]:
        """الحصول على حواف من نوع معين"""
        return [e for e in self.edges if e.edge_type == edge_type]
    
    def get_isn_edges(self) -> List[Edge]:
        """الحصول على علاقات الإسناد"""
        return self.get_edges_by_type(EdgeType.ISN)
    
    def get_tadmn_edges(self) -> List[Edge]:
        """الحصول على علاقات التضمين"""
        return self.get_edges_by_type(EdgeType.TADMN)
    
    def get_taqyid_edges(self) -> List[Edge]:
        """الحصول على علاقات التقييد"""
        return self.get_edges_by_type(EdgeType.TAQYID)
    
    def get_gov_edges(self) -> List[Edge]:
        """الحصول على تطبيقات العوامل"""
        return self.get_edges_by_type(EdgeType.GOV)
    
    def get_outgoing_edges(self, node: Node) -> List[Edge]:
        """الحواف الصادرة من عقدة"""
        return [e for e in self.edges if e.source == node]
    
    def get_incoming_edges(self, node: Node) -> List[Edge]:
        """الحواف الواردة إلى عقدة"""
        return [e for e in self.edges if e.target == node]
    
    def count_relations(self) -> Dict[str, int]:
        """عدّ العلاقات الثلاث"""
        return {
            "ISN": len(self.get_isn_edges()),
            "TADMN": len(self.get_tadmn_edges()),
            "TAQYID": len(self.get_taqyid_edges()),
            "GOV": len(self.get_gov_edges())
        }
    
    def has_proposition(self) -> bool:
        """هل يوجد حكم واحد على الأقل؟"""
        # الحكم = وجود ISN واحد على الأقل
        return len(self.get_isn_edges()) > 0
    
    def get_governors(self) -> List[Node]:
        """الحصول على عقد العوامل"""
        return [n for n in self.nodes if n.node_type == "GOVERNOR"]
    
    def get_tokens(self) -> List[Node]:
        """الحصول على عقد التوكنات"""
        return [n for n in self.nodes if n.node_type == "TOKEN"]
    
    def clone(self):
        """نسخ الرسم البياني"""
        new_graph = SyntacticGraph()
        
        # نسخ العقد (مع node_id جديد)
        node_mapping = {}  # old_node_id -> new_node
        for node in self.nodes:
            new_node = Node(
                node_type=node.node_type,
                lexical_atom=node.lexical_atom,  # مشاركة المرجع
                features=node.features.clone(),
                operator_signature=node.operator_signature.copy() if node.operator_signature else None
            )
            new_graph.add_node(new_node)
            node_mapping[node.node_id] = new_node
        
        # نسخ الحواف
        for edge in self.edges:
            new_edge = Edge(
                edge_type=edge.edge_type,
                source=node_mapping[edge.source.node_id],
                target=node_mapping[edge.target.node_id],
                label=edge.label,
                weight=edge.weight
            )
            new_graph.add_edge(new_edge)
        
        return new_graph
    
    def __repr__(self):
        counts = self.count_relations()
        return (f"Graph(nodes={len(self.nodes)}, "
                f"ISN={counts['ISN']}, TADMN={counts['TADMN']}, "
                f"TAQYID={counts['TAQYID']}, GOV={counts['GOV']})")


# مساعدات لبناء رسم بياني بسيط
def make_token_node(atom: LexicalAtom) -> Node:
    """إنشاء عقدة توكن من وحدة معجمية"""
    node = Node(
        node_type="TOKEN",
        lexical_atom=atom,
        features=NodeFeatures(
            is_declinable=atom.requires_case,
            is_locked=atom.is_built
        )
    )
    return node


def make_governor_node(atom: LexicalAtom, signature: Dict[str, Any]) -> Node:
    """إنشاء عقدة عامل"""
    node = Node(
        node_type="GOVERNOR",
        lexical_atom=atom,
        features=NodeFeatures(is_locked=True),  # العوامل عادة مبنية
        operator_signature=signature
    )
    return node
