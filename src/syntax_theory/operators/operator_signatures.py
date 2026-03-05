"""
العوامل (Operators/Governors)
=============================

العامل كعقدة (Node) لها توقيع (Signature):
  sig(A) = (req_types, assigns_features)

أنواع العوامل:
1. إنّ وأخواتها: تنصب الاسم وترفع الخبر
2. كان وأخواتها: ترفع الاسم وتنصب الخبر
3. لم/لن/لا: تجزم/تنصب المضارع
4. حروف الجر: تجر الاسم

كل عامل له:
- متطلبات (req_types): ما الذي يحكمه؟
- تعيينات (assigns_features): ما الذي يفرضه؟ (case, mood)
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from ..structures import (
    Node, Edge, EdgeType, SyntacticGraph,
    CaseMarking, MoodMarking, LexicalType, LexicalAtom
)


@dataclass
class OperatorSignature:
    """
    توقيع العامل
    
    sig(A) = (req_types, assigns_features)
    """
    operator_name: str  # "إنّ", "كان", "لم"...
    
    # المتطلبات
    requires_types: List[LexicalType]  # أنواع ما يحكمه
    requires_count: int = 1  # كم يحكم؟ (إنّ: 1 اسم، كان: 1 اسم...)
    
    # التعيينات
    assigns_case: Optional[CaseMarking] = None  # الحالة الإعرابية
    assigns_mood: Optional[MoodMarking] = None  # الصيغة (للأفعال)
    
    # إضافات
    requires_khabar: bool = False  # هل يحتاج خبرًا؟ (إنّ، كان)
    khabar_case: Optional[CaseMarking] = None  # إعراب الخبر
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل إلى قاموس للتخزين"""
        return {
            "operator_name": self.operator_name,
            "requires_types": [t.name for t in self.requires_types],
            "requires_count": self.requires_count,
            "assigns_case": self.assigns_case.name if self.assigns_case else None,
            "assigns_mood": self.assigns_mood.name if self.assigns_mood else None,
            "requires_khabar": self.requires_khabar,
            "khabar_case": self.khabar_case.name if self.khabar_case else None
        }


# === توقيعات قياسية ===

# 1. إنّ وأخواتها (إنّ، أنّ، كأنّ، لكنّ، ليت، لعلّ)
INNA_SIGNATURE = OperatorSignature(
    operator_name="إنّ",
    requires_types=[LexicalType.N, LexicalType.Pron],
    requires_count=1,
    assigns_case=CaseMarking.ACC,  # تنصب الاسم
    requires_khabar=True,
    khabar_case=CaseMarking.NOM    # ترفع الخبر
)

# 2. كان وأخواتها (كان، أصبح، أضحى، ظلّ، بات، صار، ليس، ما زال...)
KANA_SIGNATURE = OperatorSignature(
    operator_name="كان",
    requires_types=[LexicalType.N, LexicalType.Pron],
    requires_count=1,
    assigns_case=CaseMarking.NOM,  # ترفع الاسم
    requires_khabar=True,
    khabar_case=CaseMarking.ACC    # تنصب الخبر
)

# 3. لم (جازمة)
LAM_SIGNATURE = OperatorSignature(
    operator_name="لم",
    requires_types=[LexicalType.V],
    requires_count=1,
    assigns_mood=MoodMarking.JUSS  # تجزم المضارع
)

# 4. لن (ناصبة)
LAN_SIGNATURE = OperatorSignature(
    operator_name="لن",
    requires_types=[LexicalType.V],
    requires_count=1,
    assigns_mood=MoodMarking.SUB   # تنصب المضارع
)

# 5. لا الناهية (جازمة)
LA_NAHIA_SIGNATURE = OperatorSignature(
    operator_name="لا_ناهية",
    requires_types=[LexicalType.V],
    requires_count=1,
    assigns_mood=MoodMarking.JUSS
)

# 6. حرف الجر (عام)
PREPOSITION_SIGNATURE = OperatorSignature(
    operator_name="حرف_جر",
    requires_types=[LexicalType.N, LexicalType.Pron],
    requires_count=1,
    assigns_case=CaseMarking.GEN   # يجر الاسم
)


class OperatorFactory:
    """
    مصنع لإنشاء عقد العوامل بتوقيعاتها
    """
    
    # خريطة الأسماء → التوقيعات
    SIGNATURES = {
        "إنّ": INNA_SIGNATURE,
        "أنّ": INNA_SIGNATURE,
        "كأنّ": INNA_SIGNATURE,
        "لكنّ": INNA_SIGNATURE,
        "ليت": INNA_SIGNATURE,
        "لعلّ": INNA_SIGNATURE,
        
        "كان": KANA_SIGNATURE,
        "أصبح": KANA_SIGNATURE,
        "أضحى": KANA_SIGNATURE,
        "ظلّ": KANA_SIGNATURE,
        "بات": KANA_SIGNATURE,
        "صار": KANA_SIGNATURE,
        "ليس": KANA_SIGNATURE,
        
        "لم": LAM_SIGNATURE,
        "لن": LAN_SIGNATURE,
        "لا": LA_NAHIA_SIGNATURE,
        
        # حروف الجر
        "في": PREPOSITION_SIGNATURE,
        "إلى": PREPOSITION_SIGNATURE,
        "من": PREPOSITION_SIGNATURE,
        "على": PREPOSITION_SIGNATURE,
        "عن": PREPOSITION_SIGNATURE,
        "ب": PREPOSITION_SIGNATURE,
        "ل": PREPOSITION_SIGNATURE,
        "ك": PREPOSITION_SIGNATURE,
    }
    
    @staticmethod
    def create_operator_node(atom: LexicalAtom) -> Node:
        """
        إنشاء عقدة عامل من وحدة معجمية
        
        Args:
            atom: وحدة معجمية (أداة)
        
        Returns:
            Node بنوع GOVERNOR وتوقيع مناسب
        """
        sig = OperatorFactory.SIGNATURES.get(atom.raw_material)
        
        if not sig:
            # حرف جر عام
            if atom.atom_type == LexicalType.P:
                sig = PREPOSITION_SIGNATURE
            else:
                # عامل غير معروف
                sig = OperatorSignature(
                    operator_name=atom.raw_material,
                    requires_types=[LexicalType.N],
                    requires_count=1
                )
        
        node = Node(
            node_type="GOVERNOR",
            lexical_atom=atom,
            operator_signature=sig.to_dict()
        )
        
        return node
    
    @staticmethod
    def apply_operator(operator_node: Node, target_node: Node, 
                       graph: SyntacticGraph) -> Optional[Edge]:
        """
        تطبيق عامل على هدف: إنشاء GOV(operator → target)
        
        وتعيين السمات (case/mood) حسب التوقيع
        
        Returns:
            Edge(GOV) إذا نجح، None إذا فشل
        """
        if operator_node.node_type != "GOVERNOR":
            return None
        
        if not operator_node.operator_signature:
            return None
        
        sig_dict = operator_node.operator_signature
        
        # استخراج التوقيع
        req_types = [LexicalType[t] for t in sig_dict["requires_types"]]
        assigns_case_name = sig_dict.get("assigns_case")
        assigns_mood_name = sig_dict.get("assigns_mood")
        
        # التحقق من النوع
        if target_node.lexical_atom:
            if target_node.lexical_atom.atom_type not in req_types:
                # نوع خاطئ
                return None
        
        # تعيين السمات
        if assigns_case_name:
            target_node.features.case = CaseMarking[assigns_case_name]
        
        if assigns_mood_name:
            target_node.features.mood = MoodMarking[assigns_mood_name]
        
        # إنشاء الحافة
        edge = Edge(
            edge_type=EdgeType.GOV,
            source=operator_node,
            target=target_node,
            label="governs"
        )
        
        graph.add_edge(edge)
        
        return edge


class OperatorConstraints:
    """
    قيود إغلاق العوامل (Closure Constraints)
    
    كل عامل يجب أن "يُغلق" تطبيقاته:
    - إنّ: يحكم اسمًا ويحتاج خبرًا
    - لم: يحكم فعلًا مضارعًا
    - حرف جر: يحكم اسمًا
    """
    
    @staticmethod
    def is_operator_closed(operator_node: Node, graph: SyntacticGraph) -> bool:
        """
        هل العامل مُغلق؟
        
        Returns:
            True إذا كان العامل قد أتم متطلباته، False وإلا
        """
        if operator_node.node_type != "GOVERNOR":
            return True  # ليس عاملًا
        
        sig_dict = operator_node.operator_signature
        if not sig_dict:
            return True  # بدون توقيع
        
        # 1. هل يحكم العدد المطلوب؟
        req_count = sig_dict.get("requires_count", 1)
        outgoing_gov = [e for e in graph.get_outgoing_edges(operator_node)
                        if e.edge_type == EdgeType.GOV]
        
        if len(outgoing_gov) < req_count:
            return False  # لم يحكم ما يكفي
        
        # 2. هل يحتاج خبرًا؟
        requires_khabar = sig_dict.get("requires_khabar", False)
        if requires_khabar:
            # ابحث عن ISN أو TADMN خاص بالخبر
            # (مبسّط هنا: نفترض وجود علاقة ISN تربط الخبر بالاسم)
            # في تطبيق كامل: نتحقق من بنية الجملة الاسمية
            
            # للتبسيط: نفترض أن وجود ISN في الرسم يكفي
            if not graph.has_proposition():
                return False
        
        return True
    
    @staticmethod
    def count_unclosed_operators(graph: SyntacticGraph) -> int:
        """
        عدّ العوامل غير المغلقة
        
        Returns:
            عدد العوامل التي لم تتم متطلباتها
        """
        unclosed = 0
        
        for op in graph.get_governors():
            if not OperatorConstraints.is_operator_closed(op, graph):
                unclosed += 1
        
        return unclosed


# مساعدات لبناء أمثلة
def make_inna_graph(ism_atom, khabar_atom) -> SyntacticGraph:
    """
    إنشاء جملة اسمية مع إنّ
    
    مثال: "إنّ أحمدَ كاتبٌ"
    
    البنية:
    - عامل إنّ: GOV(إنّ → أحمد) + assigns ACC
    - ISN(كاتب → أحمد) للخبر
    """
    from ..structures import make_token_node
    from ..relations import RelationBuilder
    
    graph = SyntacticGraph()
    
    # إنشاء إنّ
    inna_atom = LexicalAtom(
        atom_type=LexicalType.Part,
        raw_material="إنّ",
        is_built=True
    )
    inna_node = OperatorFactory.create_operator_node(inna_atom)
    graph.add_node(inna_node)
    
    # الاسم
    ism_node = make_token_node(ism_atom)
    
    # الخبر
    khabar_node = make_token_node(khabar_atom)
    
    # تطبيق إنّ على الاسم
    OperatorFactory.apply_operator(inna_node, ism_node, graph)
    
    # ISN بين الخبر والاسم
    RelationBuilder.create_isn(khabar_node, ism_node, graph)
    
    return graph


def make_lam_graph(verb_atom) -> SyntacticGraph:
    """
    إنشاء جملة فعلية مع لم
    
    مثال: "لم يكتبْ"
    
    البنية:
    - عامل لم: GOV(لم → يكتب) + assigns JUSS
    """
    from ..structures import make_token_node
    
    graph = SyntacticGraph()
    
    # لم
    lam_atom = LexicalAtom(
        atom_type=LexicalType.Part,
        raw_material="لم",
        is_built=True
    )
    lam_node = OperatorFactory.create_operator_node(lam_atom)
    graph.add_node(lam_node)
    
    # الفعل
    verb_node = make_token_node(verb_atom)
    
    # تطبيق لم
    OperatorFactory.apply_operator(lam_node, verb_node, graph)
    
    return graph
