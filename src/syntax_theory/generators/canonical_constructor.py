"""
المُنشئ القانوني y₀ = Canon(x)
==============================

ضمان وجود حل مبدئي لكل x صحيح:
E(y₀) < ∞

الخطوات:
1. اختيار رأس الحكم (Head Selection)
2. إنشاء ISN واحد مبدئيًا
3. إشباع الفتحات بالحد الأدنى
4. قفل العوامل الدنيا
"""

from typing import Optional
from ..structures import (
    SyntacticInput, SyntacticGraph, Node,
    LexicalType, LexicalAtom, VerbValency,
    make_token_node
)
from ..relations import RelationBuilder
from ..operators import OperatorFactory


class CanonicalConstructor:
    """
    بناء y₀ = Canon(x) القانوني
    
    يضمن: E(y₀) < ∞ (لا يُرفض بـ∞)
    """
    
    @staticmethod
    def construct(x: SyntacticInput) -> SyntacticGraph:
        """
        إنشاء الرسم البياني القانوني y₀
        
        Args:
            x: المدخل الصحيح
        
        Returns:
            y₀: رسم بياني يشبع المتطلبات الدنيا
        """
        if not x.is_valid():
            raise ValueError("المدخل x غير صحيح")
        
        y0 = SyntacticGraph()
        
        # 1. اختيار رأس الحكم
        head = CanonicalConstructor._select_head(x, y0)
        
        if not head:
            raise ValueError("لا يمكن اختيار رأس حكم")
        
        # 2. إنشاء ISN واحد
        subject = CanonicalConstructor._create_isn(x, y0, head)
        
        # 3. إشباع الفتحات
        CanonicalConstructor._satisfy_slots(x, y0, head)
        
        # 4. قفل العوامل
        CanonicalConstructor._close_operators(x, y0)
        
        return y0
    
    @staticmethod
    def _select_head(x: SyntacticInput, y0: SyntacticGraph) -> Optional[Node]:
        """
        اختيار رأس الحكم (Head Selection)
        
        الأولوية:
        1. فعل (إذا وُجد وهدفه "فعلية")
        2. اسم/مشتق يصلح خبرًا
        """
        # محاولة 1: ابحث عن فعل
        verbs = x.extract_verb_atoms()
        if verbs:
            # اختر أول فعل
            verb_atom = verbs[0]
            head = make_token_node(verb_atom)
            y0.add_node(head)
            return head
        
        # محاولة 2: ابحث عن اسم يصلح خبرًا
        nouns = x.extract_noun_atoms()
        if nouns:
            # اختر أول اسم
            noun_atom = nouns[0]
            head = make_token_node(noun_atom)
            y0.add_node(head)
            return head
        
        return None
    
    @staticmethod
    def _create_isn(x: SyntacticInput, y0: SyntacticGraph, 
                    head: Node) -> Optional[Node]:
        """
        إنشاء ISN(head → subject) واحد مبدئيًا
        
        Returns:
            subject node
        """
        # ابحث عن مسند إليه مناسب
        nouns = x.extract_noun_atoms()
        
        # استثني الرأس إن كان اسمًا
        if head.lexical_atom and head.lexical_atom in nouns:
            nouns = [n for n in nouns if n != head.lexical_atom]
        
        if nouns:
            # اختر أول اسم
            subject_atom = nouns[0]
            subject = make_token_node(subject_atom)
        else:
            # أنشئ ضميرًا افتراضيًا
            subject_atom = LexicalAtom(
                atom_type=LexicalType.Pron,
                raw_material="هو"  # ضمير ضمني
            )
            subject = make_token_node(subject_atom)
        
        # أنشئ ISN
        RelationBuilder.create_isn(head, subject, y0)
        
        return subject
    
    @staticmethod
    def _satisfy_slots(x: SyntacticInput, y0: SyntacticGraph, head: Node):
        """
        إشباع الفتحات (Slots) بالحد الأدنى
        
        - فعل متعدٍّ: أنشئ مفعولًا
        - حرف جر: اربطه باسم
        """
        # 1. إشباع فتحة المفعول (إن كان الرأس فعلًا متعديًا)
        if (head.lexical_atom and 
            head.lexical_atom.atom_type == LexicalType.V and
            head.lexical_atom.valency in (VerbValency.TRANSITIVE, VerbValency.DITRANSITIVE)):
            
            # ابحث عن اسم للمفعول
            nouns = x.extract_noun_atoms()
            
            # استثني المسند إليه (الذي استخدمناه في ISN)
            isn_edges = y0.get_isn_edges()
            used_nouns = [e.target.lexical_atom for e in isn_edges if e.target.lexical_atom]
            
            available_nouns = [n for n in nouns if n not in used_nouns]
            
            if available_nouns:
                obj_atom = available_nouns[0]
                obj_node = make_token_node(obj_atom)
                
                # أنشئ TADMN(head ⇒ obj)
                RelationBuilder.create_tadmn(head, obj_node, y0, label="object")
            else:
                # أنشئ اسمًا افتراضيًا إن لم يوجد
                obj_atom = LexicalAtom(
                    atom_type=LexicalType.N,
                    raw_material="شيء"  # مفعول افتراضي
                )
                obj_node = make_token_node(obj_atom)
                RelationBuilder.create_tadmn(head, obj_node, y0, label="object")
        
        # 2. إشباع حروف الجر
        preps = x.extract_prepositions()
        for prep_atom in preps:
            prep_node = make_token_node(prep_atom)
            
            # ابحث عن اسم للجر
            nouns = x.extract_noun_atoms()
            
            # استثني المستخدم
            used_in_graph = [n.lexical_atom for n in y0.get_tokens() 
                             if n.lexical_atom and n.lexical_atom.atom_type in (LexicalType.N, LexicalType.Pron)]
            available = [n for n in nouns if n not in used_in_graph]
            
            if available:
                noun_atom = available[0]
            else:
                # استخدم أول اسم (أو أنشئ واحدًا)
                if nouns:
                    noun_atom = nouns[0]
                else:
                    noun_atom = LexicalAtom(
                        atom_type=LexicalType.N,
                        raw_material="مكان"
                    )
            
            noun_node = make_token_node(noun_atom)
            
            # أنشئ PP كعقدة مركبة أو كحافة
            # للبساطة: نجعل PP عقدة ثم نربطها بـTAQYID
            pp_node = Node(
                node_type="PP",
                lexical_atom=prep_atom
            )
            y0.add_node(pp_node)
            
            # GOV(prep → noun)
            # نحول prep_node إلى عامل
            prep_gov = OperatorFactory.create_operator_node(prep_atom)
            OperatorFactory.apply_operator(prep_gov, noun_node, y0)
            
            # TAQYID(head ⊣ PP)
            RelationBuilder.create_taqyid(head, pp_node, y0, label="pp_modifier")
    
    @staticmethod
    def _close_operators(x: SyntacticInput, y0: SyntacticGraph):
        """
        قفل العوامل الدنيا (إنّ، كان، لم...)
        
        أدخل عقدة عامل لكل أداة وطبّقها على ما يلزم
        """
        particles = x.extract_particles()
        
        for part_atom in particles:
            # أنشئ عامل
            op_node = OperatorFactory.create_operator_node(part_atom)
            y0.add_node(op_node)
            
            # طبّقه على هدف مناسب
            sig_dict = op_node.operator_signature
            if not sig_dict:
                continue
            
            req_types = [LexicalType[t] for t in sig_dict["requires_types"]]
            
            # ابحث عن هدف مناسب
            for token in y0.get_tokens():
                if token.lexical_atom and token.lexical_atom.atom_type in req_types:
                    # طبّق العامل
                    OperatorFactory.apply_operator(op_node, token, y0)
                    break


# اختبار سريع
def test_canon():
    """اختبار المُنشئ القانوني"""
    from ..structures import make_simple_input, VerbValency
    
    # مثال: "كتب أحمد الرسالة"
    x = make_simple_input(
        verbs=["كتب"],
        nouns=["أحمد", "الرسالة"]
    )
    
    # بناء y₀
    y0 = CanonicalConstructor.construct(x)
    
    print("y₀ =", y0)
    print("العلاقات:", y0.count_relations())
    print("يوجد حكم؟", y0.has_proposition())
    
    return y0


if __name__ == "__main__":
    test_canon()
