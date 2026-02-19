"""
دالة الكلفة الواحدة E في التركيب
=================================

E(y|x) = E_lex + E_morph + E_phono + E_syn + E_roles + E_gov + E_rel + E_simp

المكونات:
1. بوابات ∞ (Hard Gates):
   - Gate-typing: أنواع الحواف صحيحة
   - Gate-anchor: المبني له Anchor/Join/Scope
   - Gate-governor: العوامل مغلقة

2. كلفة العلاقات الثلاث:
   - λ_I · #ISN + λ_T · #TADMN + λ_Q · #TAQYID
   - P_unsatisfied إذا بقيت فتحة فارغة

3. كلفة العوامل:
   - P_missing_target + P_wrong_target

4. كلفة الإعراب (للمعرب):
   - ∞ إذا case/mood غير متوافق مع العامل

5. كلفة المبني:
   - ∞ إذا لا Anchor أو Join/Scope خاطئ

6. كلفة الأدوار الدلالية:
   - P(missing Agent/Patient/Cause/Effect)

7. كلفة اللفظ (من نظام اللفظ المفرد):
   - E_token + E_boundary

8. كلفة البساطة:
   - penalty على كثرة الحواف دون ضرورة
"""

import math
from dataclasses import dataclass
from typing import Optional
from ..structures import (
    SyntacticInput, SyntacticGraph,
    Node, EdgeType, CaseMarking, MoodMarking,
    LexicalType, SemanticRole
)
from ..relations import RelationConstraints
from ..operators import OperatorConstraints


@dataclass
class EnergyWeights:
    """
    أوزان دالة الكلفة
    """
    # أوزان العلاقات
    lambda_isn: float = 1.0      # كلفة إضافة ISN
    lambda_tadmn: float = 1.5    # كلفة إضافة TADMN
    lambda_taqyid: float = 0.5   # كلفة إضافة TAQYID (أرخص)
    
    # عقوبات الفتحات الفارغة
    penalty_no_proposition: float = float('inf')  # لا حكم
    penalty_unsatisfied_slot: float = float('inf')  # فتحة فارغة
    
    # عقوبات العوامل
    penalty_missing_target: float = float('inf')  # عامل بدون هدف
    penalty_wrong_target: float = float('inf')    # نوع خاطئ
    penalty_unclosed_operator: float = float('inf')  # عامل غير مغلق
    
    # عقوبات الإعراب
    penalty_case_mismatch: float = float('inf')  # إعراب خاطئ
    penalty_mood_mismatch: float = float('inf')  # صيغة خاطئة
    
    # عقوبات المبني
    penalty_no_anchor: float = float('inf')      # مبني بدون تعلّق
    penalty_wrong_join: float = 100.0            # Join خاطئ
    penalty_wrong_scope: float = 100.0           # Scope خاطئ
    
    # عقوبات الأدوار
    penalty_missing_role: float = float('inf')   # دور مطلوب غير مُعيّن
    
    # كلفة البساطة (لمنع الحواف الزائدة)
    simplicity_weight: float = 0.1  # كلفة صغيرة لكل حافة زائدة


class SyntacticEnergy:
    """
    حساب دالة الكلفة E(y|x)
    
    نفس فلسفة اللفظ المفرد: arg min E
    """
    
    def __init__(self, weights: Optional[EnergyWeights] = None):
        self.weights = weights or EnergyWeights()
    
    def compute(self, y: SyntacticGraph, x: SyntacticInput) -> float:
        """
        حساب E(y|x)
        
        Args:
            y: الرسم البياني (المرشح)
            x: المدخل
        
        Returns:
            الكلفة الكلية
        """
        # 1. البوابات ∞
        if not self._check_hard_gates(y, x):
            return float('inf')
        
        # 2. كلفة العلاقات
        e_rel = self._compute_relation_cost(y, x)
        if math.isinf(e_rel):
            return float('inf')
        
        # 3. كلفة العوامل
        e_gov = self._compute_governor_cost(y)
        if math.isinf(e_gov):
            return float('inf')
        
        # 4. كلفة الإعراب
        e_case = self._compute_case_cost(y)
        if math.isinf(e_case):
            return float('inf')
        
        # 5. كلفة المبني
        e_built = self._compute_built_cost(y)
        if math.isinf(e_built):
            return float('inf')
        
        # 6. كلفة الأدوار
        e_roles = self._compute_role_cost(y, x)
        if math.isinf(e_roles):
            return float('inf')
        
        # 7. كلفة اللفظ (مبسّط هنا)
        e_phono = 0.0  # سيتم الربط بنظام اللفظ المفرد
        
        # 8. كلفة البساطة
        e_simp = self._compute_simplicity_cost(y)
        
        # الكلفة الكلية
        total = e_rel + e_gov + e_case + e_built + e_roles + e_phono + e_simp
        
        return total
    
    def _check_hard_gates(self, y: SyntacticGraph, x: SyntacticInput) -> bool:
        """
        التحقق من البوابات ∞
        
        Returns:
            True إذا مرّت جميع البوابات، False وإلا (→ ∞)
        """
        # Gate-typing: أنواع الحواف صحيحة
        # (تم التحقق في RelationBuilder، هنا نفترض أنها صحيحة)
        
        # Gate-anchor: المبني له Anchor
        for node in y.get_tokens():
            if node.features.is_locked:  # مبني
                if node.features.requires_anchor and not node.features.anchor:
                    return False  # لا تعلّق
        
        # Gate-governor: العوامل مغلقة
        # (سنتحقق في _compute_governor_cost)
        
        return True
    
    def _compute_relation_cost(self, y: SyntacticGraph, x: SyntacticInput) -> float:
        """
        كلفة العلاقات الثلاث
        
        E_rel = λ_I·#ISN + λ_T·#TADMN + λ_Q·#TAQYID + P_unsatisfied
        """
        counts = y.count_relations()
        
        cost = (
            self.weights.lambda_isn * counts["ISN"] +
            self.weights.lambda_tadmn * counts["TADMN"] +
            self.weights.lambda_taqyid * counts["TAQYID"]
        )
        
        # التحقق من الفتحات
        # 1. هل يوجد حكم؟
        if not RelationConstraints.must_have_proposition(y):
            return float('inf')
        
        # 2. عدّ الفتحات الفارغة
        unsatisfied = RelationConstraints.count_unsatisfied_slots(y)
        if unsatisfied > 0:
            cost += self.weights.penalty_unsatisfied_slot * unsatisfied
        
        return cost
    
    def _compute_governor_cost(self, y: SyntacticGraph) -> float:
        """
        كلفة العوامل
        
        E_gov = Σ (P_missing_target + P_wrong_target)
        """
        cost = 0.0
        
        for op in y.get_governors():
            if not OperatorConstraints.is_operator_closed(op, y):
                # عامل غير مغلق
                cost += self.weights.penalty_unclosed_operator
        
        # التحقق من GOV edges: هل الأنواع صحيحة؟
        for edge in y.get_gov_edges():
            op = edge.source
            target = edge.target
            
            if not op.operator_signature:
                continue
            
            sig_dict = op.operator_signature
            req_types = [LexicalType[t] for t in sig_dict["requires_types"]]
            
            if target.lexical_atom:
                if target.lexical_atom.atom_type not in req_types:
                    # نوع خاطئ
                    cost += self.weights.penalty_wrong_target
        
        return cost
    
    def _compute_case_cost(self, y: SyntacticGraph) -> float:
        """
        كلفة الإعراب (للمعرب)
        
        P_case(t, A) = ∞ إذا case غير متوافق مع العامل
        """
        cost = 0.0
        
        # لكل عقدة معربة: تحقق من التوافق مع العامل
        for edge in y.get_gov_edges():
            op = edge.source
            target = edge.target
            
            if not target.features.is_declinable:
                continue  # مبني
            
            # استخرج ما يفرضه العامل
            if not op.operator_signature:
                continue
            
            sig_dict = op.operator_signature
            assigns_case_name = sig_dict.get("assigns_case")
            assigns_mood_name = sig_dict.get("assigns_mood")
            
            # تحقق من case
            if assigns_case_name:
                expected_case = CaseMarking[assigns_case_name]
                if target.features.case and target.features.case != expected_case:
                    # عدم توافق
                    cost += self.weights.penalty_case_mismatch
            
            # تحقق من mood
            if assigns_mood_name:
                expected_mood = MoodMarking[assigns_mood_name]
                if target.features.mood and target.features.mood != expected_mood:
                    cost += self.weights.penalty_mood_mismatch
        
        return cost
    
    def _compute_built_cost(self, y: SyntacticGraph) -> float:
        """
        كلفة المبني
        
        P_anchor = ∞ إذا لا تعلّق
        """
        cost = 0.0
        
        for node in y.get_tokens():
            if not node.features.is_locked:
                continue  # معرب
            
            # المبني يحتاج Anchor
            if node.features.requires_anchor:
                if not node.features.anchor:
                    cost += self.weights.penalty_no_anchor
            
            # تحقق من Join/Scope (مبسّط)
            if node.features.join_status:
                # يمكن إضافة قيود محددة هنا
                pass
        
        return cost
    
    def _compute_role_cost(self, y: SyntacticGraph, x: SyntacticInput) -> float:
        """
        كلفة الأدوار الدلالية
        
        E_roles = P(missing Agent) + P(missing Patient) + ...
        """
        cost = 0.0
        
        # لكل فعل: تحقق من الأدوار
        for node in y.get_tokens():
            if not node.lexical_atom or node.lexical_atom.atom_type != LexicalType.V:
                continue
            
            valency = node.lexical_atom.valency
            if not valency:
                continue
            
            # استخرج الأدوار المرتبطة
            outgoing = y.get_outgoing_edges(node)
            incoming = y.get_incoming_edges(node)
            
            # ابحث عن Agent (من ISN أو كفاعل)
            has_agent = any(
                e.edge_type == EdgeType.ISN for e in outgoing
            )
            
            # ابحث عن Patient (من TADMN أو كمفعول)
            has_patient = any(
                e.edge_type == EdgeType.TADMN and e.label in ("object", "complement")
                for e in outgoing
            )
            
            # الفعل المتعدي يحتاج Agent + Patient
            from ..structures import VerbValency
            if valency in (VerbValency.TRANSITIVE, VerbValency.DITRANSITIVE):
                if not has_agent:
                    cost += self.weights.penalty_missing_role
                if not has_patient:
                    cost += self.weights.penalty_missing_role
        
        return cost
    
    def _compute_simplicity_cost(self, y: SyntacticGraph) -> float:
        """
        كلفة البساطة
        
        E_simp = w · (عدد الحواف)
        
        لمنع إضافة حواف زائدة دون ضرورة
        """
        total_edges = len(y.edges)
        
        # استثني الحواف الضرورية (ISN, GOV)
        necessary = len(y.get_isn_edges()) + len(y.get_gov_edges())
        
        # الحواف الزائدة
        extra = total_edges - necessary
        
        cost = self.weights.simplicity_weight * max(0, extra)
        
        return cost


class SyntacticOptimizer:
    """
    حل arg min E(y|x) على G(x)
    
    y* = arg min_{y ∈ G(x)} E(y|x)
    """
    
    def __init__(self, energy: Optional[SyntacticEnergy] = None):
        self.energy = energy or SyntacticEnergy()
    
    def solve(self, x: SyntacticInput, candidates: list) -> SyntacticGraph:
        """
        اختيار المرشح الأفضل
        
        Args:
            x: المدخل
            candidates: G(x) قائمة المرشحين
        
        Returns:
            y* الأفضل
        """
        best_y = None
        best_E = float('inf')
        
        for y in candidates:
            E_y = self.energy.compute(y, x)
            
            if E_y < best_E:
                best_E = E_y
                best_y = y
        
        return best_y
    
    def solve_with_log(self, x: SyntacticInput, candidates: list) -> dict:
        """
        حل مع سجل تفصيلي
        
        Returns:
            {
                'best': y*,
                'best_energy': E(y*),
                'all_energies': [(y, E(y))],
                'log': [...]
            }
        """
        results = []
        log = []
        
        for i, y in enumerate(candidates):
            E_y = self.energy.compute(y, x)
            results.append((y, E_y))
            
            log.append(f"المرشح {i+1}: E = {E_y:.2f}, {y}")
        
        # ترتيب
        results.sort(key=lambda item: item[1])
        
        best_y, best_E = results[0]
        
        log.append(f"\n✓ الأفضل: E = {best_E:.2f}")
        
        return {
            'best': best_y,
            'best_energy': best_E,
            'all_energies': results,
            'log': log
        }


# اختبار سريع
def test_energy():
    """اختبار دالة الكلفة"""
    from ..structures import make_simple_input
    from ..generators import CanonicalConstructor, SimpleGenerator
    
    # مدخل: "كتب أحمد الرسالة"
    x = make_simple_input(
        verbs=["كتب"],
        nouns=["أحمد", "الرسالة"]
    )
    
    # مرشحان: صحيح وخاطئ
    y_correct, y_wrong = SimpleGenerator.generate_two_candidates(x)
    
    # حساب الكلفة
    energy = SyntacticEnergy()
    
    E_correct = energy.compute(y_correct, x)
    E_wrong = energy.compute(y_wrong, x)
    
    print(f"E(y_correct) = {E_correct:.2f}")
    print(f"E(y_wrong) = {E_wrong:.2f}")
    print(f"\nهل الصحيح أقل؟ {E_correct < E_wrong}")
    
    return E_correct, E_wrong


if __name__ == "__main__":
    test_energy()
