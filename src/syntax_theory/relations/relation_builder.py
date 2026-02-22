"""
العلاقات الثلاث: ISN, TADMN, TAQYID
===================================

ISN (الإسناد): h → s
   حافة من الرأس (مسند) إلى المسند إليه
   مثل: "كتب أحمد" → ISN(كتب → أحمد)

TADMN (التضمين): h ⇒ C
   حافة من الرأس إلى تكملة (جملة/عبارة تُملأ بها فتحة Argument)
   مثل: "يريد أن يذهب" → TADMN(يريد ⇒ "أن يذهب")

TAQYID (التقييد): h ⊣ m
   حافة من الرأس إلى مقيد (صفة/حال/جار ومجرور/تمييز...)
   مثل: "كتب في البيت" → TAQYID(كتب ⊣ "في البيت")

هذه ليست "تسميات نحاة" بل ثلاث طبائع بنيوية:
- Predication
- Embedding
- Modification
"""

from dataclasses import dataclass
from typing import Optional, List
from ..structures import (
    Node, Edge, EdgeType, SyntacticGraph,
    LexicalType
)


@dataclass
class RelationBuilder:
    """
    بناء العلاقات الثلاث مع التحقق من الأنواع (Typing)
    """
    
    @staticmethod
    def can_predicate(head: Node, subject: Node) -> bool:
        """
        هل يمكن إنشاء ISN(head → subject)؟
        
        شروط:
        - head يجب أن يكون فعلًا أو اسمًا/مشتقًا يصلح للإسناد
        - subject يجب أن يكون اسمًا أو ضميرًا
        """
        if not head.lexical_atom or not subject.lexical_atom:
            return False
        
        # الرأس: فعل أو اسم/مشتق
        head_ok = head.lexical_atom.atom_type in (
            LexicalType.V,   # فعل
            LexicalType.N,   # اسم (قد يكون خبرًا)
            LexicalType.Adj  # صفة (يمكن أن تكون خبرًا)
        )
        
        # المسند إليه: اسم أو ضمير
        subject_ok = subject.lexical_atom.atom_type in (
            LexicalType.N,
            LexicalType.Pron
        )
        
        return head_ok and subject_ok
    
    @staticmethod
    def create_isn(head: Node, subject: Node, graph: SyntacticGraph) -> Optional[Edge]:
        """
        إنشاء علاقة إسناد ISN(head → subject)
        
        Returns:
            Edge إذا نجح، None إذا فشل التحقق من الأنواع
        """
        if not RelationBuilder.can_predicate(head, subject):
            return None
        
        edge = Edge(
            edge_type=EdgeType.ISN,
            source=head,
            target=subject,
            label="predication"
        )
        graph.add_edge(edge)
        return edge
    
    @staticmethod
    def can_embed(head: Node, complement: Node) -> bool:
        """
        هل يمكن إنشاء TADMN(head ⇒ complement)؟
        
        شروط:
        - head يطلب تكملة (فعل متعدٍّ، اسم يحتاج مصدر مؤول...)
        - complement من نوع Clause/NP/VP مناسب
        """
        if not head.lexical_atom:
            return False
        
        # للبساطة: أي فعل أو اسم يمكن أن يأخذ تكملة
        # في تطبيق كامل: نفحص التعدية (Valency)
        return True
    
    @staticmethod
    def create_tadmn(head: Node, complement: Node, graph: SyntacticGraph, 
                     label: str = "complement") -> Optional[Edge]:
        """
        إنشاء علاقة تضمين TADMN(head ⇒ complement)
        
        Args:
            label: نوع التكملة ("object", "clausal_complement", etc.)
        """
        if not RelationBuilder.can_embed(head, complement):
            return None
        
        edge = Edge(
            edge_type=EdgeType.TADMN,
            source=head,
            target=complement,
            label=label
        )
        graph.add_edge(edge)
        return edge
    
    @staticmethod
    def can_modify(head: Node, modifier: Node) -> bool:
        """
        هل يمكن إنشاء TAQYID(head ⊣ modifier)؟
        
        شروط:
        - modifier من نوع Modifier/PP/Adj/Adv
        """
        if not modifier.lexical_atom:
            return False
        
        # المقيد: صفة، ظرف، أو PP (نمثلها كعقدة مركبة أو بعلامة)
        modifier_ok = modifier.lexical_atom.atom_type in (
            LexicalType.Adj,
            LexicalType.Adv,
            LexicalType.P  # حرف جر (سنعتبر PP كوحدة)
        )
        
        # أو إذا كانت العقدة ممثلة كـPP
        if modifier.node_type == "PP":
            modifier_ok = True
        
        return modifier_ok
    
    @staticmethod
    def create_taqyid(head: Node, modifier: Node, graph: SyntacticGraph,
                      label: str = "modifier") -> Optional[Edge]:
        """
        إنشاء علاقة تقييد TAQYID(head ⊣ modifier)
        
        Args:
            label: نوع التقييد ("adjective", "adverb", "pp_modifier", etc.)
        """
        if not RelationBuilder.can_modify(head, modifier):
            return None
        
        edge = Edge(
            edge_type=EdgeType.TAQYID,
            source=head,
            target=modifier,
            label=label
        )
        graph.add_edge(edge)
        return edge


class RelationConstraints:
    """
    قيود على العلاقات (لاستخدامها في دالة الكلفة E)
    """
    
    @staticmethod
    def must_have_proposition(graph: SyntacticGraph) -> bool:
        """
        يجب وجود ISN واحد على الأقل
        
        Returns:
            True إذا تحقق الشرط، False وإلا
        """
        return graph.has_proposition()
    
    @staticmethod
    def argument_slots_filled(graph: SyntacticGraph, verb_node: Node) -> bool:
        """
        هل فتحات الفعل (Arguments) مملوءة؟
        
        للفعل المتعدي: يجب وجود مفعول (TADMN أو ISN-subject + TADMN-object)
        """
        if not verb_node.lexical_atom:
            return True  # ليس فعلًا
        
        if verb_node.lexical_atom.atom_type != LexicalType.V:
            return True  # ليس فعلًا
        
        valency = verb_node.lexical_atom.valency
        if not valency:
            return True  # غير محدد
        
        # للفعل اللازم: لا يحتاج مفعولًا
        if valency == verb_node.lexical_atom.valency.INTRANSITIVE:
            return True
        
        # للفعل المتعدي: يجب وجود object
        outgoing = graph.get_outgoing_edges(verb_node)
        
        # ابحث عن TADMN labeled as "object"
        has_object = any(
            e.edge_type == EdgeType.TADMN and e.label in ("object", "complement")
            for e in outgoing
        )
        
        return has_object
    
    @staticmethod
    def preposition_has_noun(graph: SyntacticGraph, prep_node: Node) -> bool:
        """
        هل حرف الجر يحكم اسمًا؟
        
        Returns:
            True إذا كان هناك GOV(prep → noun)
        """
        if not prep_node.lexical_atom:
            return True
        
        if prep_node.lexical_atom.atom_type != LexicalType.P:
            return True  # ليس حرف جر
        
        # ابحث عن GOV من حرف الجر
        outgoing = graph.get_outgoing_edges(prep_node)
        has_governed_noun = any(
            e.edge_type == EdgeType.GOV and 
            e.target.lexical_atom and
            e.target.lexical_atom.atom_type in (LexicalType.N, LexicalType.Pron)
            for e in outgoing
        )
        
        return has_governed_noun
    
    @staticmethod
    def count_unsatisfied_slots(graph: SyntacticGraph) -> int:
        """
        عدّ الفتحات غير المشبعة
        
        Returns:
            عدد الفتحات الفارغة (violation count)
        """
        violations = 0
        
        # 1. هل يوجد حكم؟
        if not RelationConstraints.must_have_proposition(graph):
            violations += 1
        
        # 2. هل كل فعل متعدٍّ له مفعول؟
        for node in graph.get_tokens():
            if node.lexical_atom and node.lexical_atom.atom_type == LexicalType.V:
                if not RelationConstraints.argument_slots_filled(graph, node):
                    violations += 1
        
        # 3. هل كل حرف جر يحكم اسمًا؟
        for node in graph.get_tokens():
            if node.lexical_atom and node.lexical_atom.atom_type == LexicalType.P:
                if not RelationConstraints.preposition_has_noun(graph, node):
                    violations += 1
        
        # 4. هل كل عامل (إنّ، كان...) مُغلق؟
        for gov in graph.get_governors():
            # سيتم تنفيذها في operators/
            pass
        
        return violations


# مساعدات سريعة
def make_simple_isn_graph(verb_atom, subject_atom) -> SyntacticGraph:
    """
    إنشاء رسم بياني بسيط: ISN واحد
    
    مثال: "كتب أحمد" → ISN(كتب → أحمد)
    """
    from ..structures import make_token_node
    
    graph = SyntacticGraph()
    
    verb_node = make_token_node(verb_atom)
    subject_node = make_token_node(subject_atom)
    
    RelationBuilder.create_isn(verb_node, subject_node, graph)
    
    return graph
