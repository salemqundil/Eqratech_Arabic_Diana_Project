"""
دالة الطاقة الكلية E_total مع المقام
Total Energy Function with Pragmatic Context

E_total = E_phon + E_morph + E_syn + E_sem + E_maqam + λ·Cost
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List
import math


@dataclass
class EnergyWeights:
    """
    أوزان دالة الطاقة
    """
    # أوزان الطبقات
    λ_phon: float = 1.0      # صوتية
    λ_morph: float = 1.0     # صرفية
    λ_syn: float = 1.0       # تركيبية
    λ_sem: float = 1.0       # دلالية
    λ_maqam: float = 1.0     # مقامية
    
    # عقوبات البوابات
    λ_gate_activation: float = 0.5
    λ_gate_violation: float = 10.0
    λ_scope_violation: float = 5.0
    λ_binding_violation: float = 8.0
    
    # عقوبات الاتساق
    λ_consistency: float = 3.0
    λ_completeness: float = 4.0


class MaqamEnergy:
    """
    دالة طاقة المقام E_maqam
    
    تحسب:
    - كلفة تفعيل/عدم تفعيل البوابات
    - انتهاكات قيود الإشباع
    - اتساق M مع البنية والسطح
    """
    
    def __init__(self, weights: EnergyWeights = None):
        self.weights = weights or EnergyWeights()
    
    def compute(self, x: Any, y: Any, gate_results: List[Any]) -> float:
        """
        حساب E_maqam
        
        Args:
            x: المدخل الكامل (FullInput)
            y: المنشئ (assignments)
            gate_results: نتائج البوابات (List[GateResult])
        
        Returns:
            E_maqam ∈ [0, ∞]
        """
        E = 0.0
        
        # 1. كلفة البوابات المُفعّلة
        E += self._compute_gate_costs(gate_results)
        
        # 2. كلفة انتهاكات الإشباع
        E += self._compute_satisfaction_violations(gate_results)
        
        # 3. كلفة انتهاكات النطاق
        E += self._compute_scope_violations(x, y)
        
        # 4. كلفة انتهاكات الربط
        E += self._compute_binding_violations(x, y)
        
        # 5. كلفة عدم الاتساق (M vs Σ vs Surf)
        E += self._compute_consistency_violations(x, y, gate_results)
        
        # 6. كلفة عدم الاكتمال
        E += self._compute_completeness_violations(x, y, gate_results)
        
        return E
    
    def _compute_gate_costs(self, gate_results: List[Any]) -> float:
        """كلفة تفعيل البوابات"""
        total = 0.0
        for gr in gate_results:
            if gr.activated:
                # كلفة التفعيل (من GateResult.cost_delta)
                total += self.weights.λ_gate_activation * max(0, gr.cost_delta)
        return total
    
    def _compute_satisfaction_violations(self, gate_results: List[Any]) -> float:
        """كلفة انتهاكات الإشباع"""
        total = 0.0
        for gr in gate_results:
            if gr.activated:
                # كل انتهاك = عقوبة ثابتة
                num_violations = len(gr.constraints_violated)
                total += self.weights.λ_gate_violation * num_violations
                
                # عقوبة إشباع منخفض
                if gr.satisfaction_level < 0.5:
                    total += self.weights.λ_gate_violation * (0.5 - gr.satisfaction_level)
        return total
    
    def _compute_scope_violations(self, x: Any, y: Any) -> float:
        """كلفة انتهاكات النطاق"""
        scope_graph = x.scope_graph
        violations = 0
        
        # فحص: كل عامل له نطاق صحيح
        for op in scope_graph.nodes:
            scope = scope_graph.get_scope(op)
            if not scope:
                # عامل بلا نطاق (قد يكون خطأ)
                violations += 0.5
        
        # فحص: Q في أعلى النطاق (إذا كان استفهام)
        M = x.get_maqam()
        if M.i_istifham > 0.5:
            if 'Q' in scope_graph.nodes:
                # Q يجب أن يكون في الأعلى (c-command على الكل)
                q_scope = scope_graph.get_scope('Q')
                # simplified check
                if len(q_scope) < len(x.surf.word_order) - 1:
                    violations += 1.0
        
        return self.weights.λ_scope_violation * violations
    
    def _compute_binding_violations(self, x: Any, y: Any) -> float:
        """كلفة انتهاكات الربط"""
        binding_map = x.binding_map
        violations = 0
        
        # فحص: كل متغيرات wh مربوطة
        for var in binding_map.wh_variables:
            if not binding_map.is_bound(var):
                violations += 1.0
        
        # فحص: كل أثر له مصدر
        for trace_id, source in binding_map.traces.items():
            if not source:
                violations += 0.5
        
        return self.weights.λ_binding_violation * violations
    
    def _compute_consistency_violations(self, x: Any, y: Any, gate_results: List[Any]) -> float:
        """
        كلفة عدم الاتساق
        
        فحص:
        - M يتوافق مع البوابات المُفعّلة
        - البوابات تتوافق مع السطح
        - لا تناقضات (مثلاً: polar و wh معًا)
        """
        M = x.get_maqam()
        violations = 0.0
        
        # استخراج البوابات المُفعّلة
        activated_gates = [gr.gate_type for gr in gate_results if gr.activated]
        
        # فحص: إذا M.i_istifham مرتفع، يجب وجود بوابة استفهام
        if M.i_istifham > 0.7:
            from maqam_theory.gates.base_gate import GateType
            interrogative_gates = [
                GateType.INTERROGATIVE_POLAR,
                GateType.INTERROGATIVE_WH,
                GateType.INTERROGATIVE_ALT
            ]
            if not any(g in activated_gates for g in interrogative_gates):
                violations += 2.0
        
        # فحص: لا تناقض بين polar و wh
        from maqam_theory.gates.base_gate import GateType
        if (GateType.INTERROGATIVE_POLAR in activated_gates and
            GateType.INTERROGATIVE_WH in activated_gates):
            violations += 3.0
        
        # فحص: استفهام wh + أداة wh في السطح
        if GateType.INTERROGATIVE_WH in activated_gates:
            if not x.surf.has_wh_word:
                violations += 2.0
        
        # فحص: نداء + "يا" في السطح
        if GateType.VOCATIVE in activated_gates:
            if not x.surf.has_vocative_marker():
                violations += 1.5
        
        return self.weights.λ_consistency * violations
    
    def _compute_completeness_violations(self, x: Any, y: Any, gate_results: List[Any]) -> float:
        """
        كلفة عدم الاكتمال
        
        فحص:
        - كل استفهام wh له متغير
        - كل نداء له منادى
        - كل شرط له جواب
        """
        violations = 0.0
        
        from maqam_theory.gates.base_gate import GateType
        activated_gates = {gr.gate_type: gr for gr in gate_results if gr.activated}
        
        # استفهام wh → متغير wh
        if GateType.INTERROGATIVE_WH in activated_gates:
            if not x.binding_map.wh_variables:
                violations += 2.0
        
        # نداء → منادى
        if GateType.VOCATIVE in activated_gates:
            if not hasattr(y, 'addressee') or y.addressee is None:
                violations += 1.5
        
        # شرط → شرط + جواب
        if GateType.CONDITIONAL in activated_gates:
            if not (hasattr(y, 'condition_clause') and hasattr(y, 'consequence_clause')):
                violations += 2.0
        
        return self.weights.λ_completeness * violations


class TotalEnergy:
    """
    دالة الطاقة الكلية
    
    E_total = E_phon + E_morph + E_syn + E_sem + E_maqam
    """
    
    def __init__(self, weights: EnergyWeights = None):
        self.weights = weights or EnergyWeights()
        self.maqam_energy = MaqamEnergy(weights)
    
    def compute(self, x: Any, y: Any, gate_results: List[Any],
                E_phon: float = 0.0,
                E_morph: float = 0.0,
                E_syn: float = 0.0,
                E_sem: float = 0.0) -> float:
        """
        حساب الطاقة الكلية
        
        Args:
            x: المدخل
            y: المنشئ
            gate_results: نتائج البوابات
            E_phon, E_morph, E_syn, E_sem: طاقات الطبقات الأخرى
        
        Returns:
            E_total
        """
        E_maqam = self.maqam_energy.compute(x, y, gate_results)
        
        E_total = (
            self.weights.λ_phon * E_phon +
            self.weights.λ_morph * E_morph +
            self.weights.λ_syn * E_syn +
            self.weights.λ_sem * E_sem +
            self.weights.λ_maqam * E_maqam
        )
        
        return E_total
    
    def compute_full(self, x: Any, y: Any, gate_results: List[Any]) -> Dict[str, float]:
        """
        حساب تفصيلي لكل مركبات الطاقة
        
        Returns:
            Dict with E_phon, E_morph, E_syn, E_sem, E_maqam, E_total
        """
        # هنا نربط بالطبقات الأخرى (phonology, syntax...)
        # مبسّط الآن:
        E_phon = 0.0  # سيُربط لاحقًا
        E_morph = 0.0
        E_syn = 0.0
        E_sem = 0.0
        E_maqam = self.maqam_energy.compute(x, y, gate_results)
        
        E_total = self.compute(x, y, gate_results, E_phon, E_morph, E_syn, E_sem)
        
        return {
            'E_phon': E_phon,
            'E_morph': E_morph,
            'E_syn': E_syn,
            'E_sem': E_sem,
            'E_maqam': E_maqam,
            'E_total': E_total
        }
