"""
مولد المرشحين G(x)
==================

G(x) = {y: y ناتج عن تعديلات محدودة على y₀ ضمن الحد B}

التعديلات:
- تبديل نمط الحكم (اسمي/فعلي)
- إدراج/إزالة علاقة من ISN/TADMN/TAQYID
- إعادة ربط PP
- تبديل مواضع العوامل
- تعيين الإعراب للمعرب
- قرار Join للمبني
"""

from typing import List, Generator
from ..structures import (
    SyntacticInput, SyntacticGraph,
    CaseMarking, MoodMarking, EdgeType
)
from .canonical_constructor import CanonicalConstructor


class CandidateGenerator:
    """
    توليد المرشحين G(x) المنتهي
    
    مع حد B يصبح عدد المرشحين منتهيًا
    """
    
    @staticmethod
    def generate(x: SyntacticInput, max_modifications: int = 3) -> List[SyntacticGraph]:
        """
        توليد جميع المرشحين ضمن الحد
        
        Args:
            x: المدخل
            max_modifications: عدد التعديلات الأقصى على y₀
        
        Returns:
            قائمة المرشحين (منتهية)
        """
        # 1. ابدأ بـy₀
        y0 = CanonicalConstructor.construct(x)
        
        candidates = [y0]
        
        # 2. ولّد تعديلات من الدرجة الأولى
        for mod_count in range(1, max_modifications + 1):
            new_candidates = CandidateGenerator._apply_modifications(
                y0, x, mod_count
            )
            candidates.extend(new_candidates)
        
        # تحديد بالحد B
        if len(candidates) > x.B:
            candidates = candidates[:x.B]
        
        return candidates
    
    @staticmethod
    def _apply_modifications(base: SyntacticGraph, x: SyntacticInput, 
                            count: int) -> List[SyntacticGraph]:
        """
        تطبيق تعديلات بعدد محدد
        
        Args:
            base: الرسم الأساسي (y₀)
            x: المدخل
            count: عدد التعديلات
        
        Returns:
            قائمة الرسوم البيانية المعدلة
        """
        if count == 0:
            return [base]
        
        modified = []
        
        # تعديل 1: تبديل case لعقدة معربة
        for node in base.get_tokens():
            if node.features.is_declinable and not node.features.is_locked:
                for case in [CaseMarking.NOM, CaseMarking.ACC, CaseMarking.GEN]:
                    new_graph = base.clone()
                    # ابحث عن العقدة المطابقة
                    matching = [n for n in new_graph.get_tokens() 
                               if n.lexical_atom == node.lexical_atom]
                    if matching:
                        matching[0].features.case = case
                        modified.append(new_graph)
        
        # تعديل 2: إضافة TAQYID جديد (إن كان هناك معدل غير مستخدم)
        # (مبسّط: نفترض أن هناك صفات/ظروف يمكن إضافتها)
        
        # تعديل 3: إزالة TAQYID موجود (التقييد اختياري)
        for edge in base.get_taqyid_edges():
            new_graph = base.clone()
            # ابحث عن الحافة المطابقة
            matching_edges = [e for e in new_graph.edges 
                             if e.edge_type == EdgeType.TAQYID 
                             and e.source.lexical_atom == edge.source.lexical_atom
                             and e.target.lexical_atom == edge.target.lexical_atom]
            if matching_edges:
                new_graph.edges.remove(matching_edges[0])
                modified.append(new_graph)
        
        # تحديد بعدد معقول
        return modified[:20]  # حد مؤقت


class SimpleGenerator:
    """
    مولد مبسّط لأمثلة الاختبار
    
    يولّد 2-3 مرشحين فقط لمقارنة واضحة
    """
    
    @staticmethod
    def generate_two_candidates(x: SyntacticInput) -> tuple:
        """
        توليد مرشحين: واحد صحيح وواحد خاطئ
        
        Returns:
            (y_correct, y_wrong)
        """
        # المرشح الصحيح
        y_correct = CanonicalConstructor.construct(x)
        
        # المرشح الخاطئ: نترك فتحة فارغة
        y_wrong = y_correct.clone()
        
        # احذف علاقة TADMN (إن وُجدت) لترك فتحة فارغة
        tadmn_edges = y_wrong.get_tadmn_edges()
        if tadmn_edges:
            y_wrong.edges.remove(tadmn_edges[0])
        
        return y_correct, y_wrong
    
    @staticmethod
    def generate_case_variants(x: SyntacticInput) -> List[SyntacticGraph]:
        """
        توليد مرشحين بإعرابات مختلفة
        
        مفيد لاختبار: هل arg min يختار الإعراب الصحيح؟
        """
        y0 = CanonicalConstructor.construct(x)
        
        variants = [y0]
        
        # ولّد نسخًا بإعرابات مختلفة
        for node in y0.get_tokens():
            if node.features.is_declinable:
                for case in [CaseMarking.NOM, CaseMarking.ACC, CaseMarking.GEN]:
                    if node.features.case != case:
                        variant = y0.clone()
                        matching = [n for n in variant.get_tokens() 
                                   if n.lexical_atom == node.lexical_atom]
                        if matching:
                            matching[0].features.case = case
                            variants.append(variant)
        
        return variants[:5]  # حد 5 مرشحين


# اختبار
def test_generator():
    """اختبار المولد"""
    from ..structures import make_simple_input
    
    x = make_simple_input(
        verbs=["كتب"],
        nouns=["أحمد", "الرسالة"]
    )
    
    # توليد مرشحين
    candidates = CandidateGenerator.generate(x, max_modifications=2)
    
    print(f"عدد المرشحين: {len(candidates)}")
    for i, cand in enumerate(candidates[:5]):
        print(f"  {i+1}. {cand}")
    
    # توليد مرشحين بسيطين
    y_correct, y_wrong = SimpleGenerator.generate_two_candidates(x)
    print(f"\nالصحيح: {y_correct}")
    print(f"الخاطئ: {y_wrong}")


if __name__ == "__main__":
    test_generator()
