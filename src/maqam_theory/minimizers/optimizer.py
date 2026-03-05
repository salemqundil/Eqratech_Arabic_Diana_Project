"""
المحسّن - Optimizer for arg min E_total

(Σ*, M*, y₀) = arg min E_total(Σ, M, y)
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Any, Optional
import math


@dataclass
class OptimizationResult:
    """نتيجة التحسين"""
    x_optimal: Any  # المدخل الأمثل
    y_optimal: Any  # المنشئ الأمثل
    gate_results: List[Any] = field(default_factory=list)
    E_total: float = float('inf')
    E_components: dict = field(default_factory=dict)
    iterations: int = 0
    converged: bool = False
    
    def __repr__(self) -> str:
        gates_active = [gr.gate_type.value for gr in self.gate_results if gr.activated]
        return (f"OptimizationResult(\n"
                f"  E_total={self.E_total:.2f},\n"
                f"  gates_active={gates_active},\n"
                f"  converged={self.converged}\n"
                f")")


class MaqamOptimizer:
    """
    المُحسّن للمقام
    
    يبحث عن (M*, y*) بتثبيت Σ
    """
    
    def __init__(self, max_iterations: int = 100, tolerance: float = 1e-4):
        self.max_iterations = max_iterations
        self.tolerance = tolerance
    
    def optimize(self, x: Any, gates: List[Any], energy_func: Any) -> OptimizationResult:
        """
        تحسين المقام والمنشئ
        
        خوارزمية:
        1. استنتاج M من السطح
        2. تطبيق البوابات بالترتيب
        3. بناء y₀
        4. حساب E
        5. تكرار حتى التقارب
        """
        from .assignment_generator import AssignmentGenerator
        
        # خطوة 1: استنتاج M
        M = x.infer_maqam_from_surface()
        
        # خطوة 2: تطبيق البوابات
        y = AssignmentGenerator.initialize()
        gate_results = []
        
        for gate in gates:
            gr = gate.apply(x, y)
            gate_results.append(gr)
            
            if gr.activated:
                # تطبيق التعديلات
                y = AssignmentGenerator.apply_modifications(y, gr.modifications)
        
        # خطوة 3: حساب الطاقة
        E_total = energy_func.compute_full(x, y, gate_results)['E_total']
        
        # خطوة 4: محاولة تحسين (greedy)
        best_E = E_total
        best_y = y
        best_gates = gate_results
        
        for iteration in range(self.max_iterations):
            # جرّب إيقاف/تشغيل بوابة
            improved = False
            
            for i, gate in enumerate(gates):
                # جرّب عكس التفعيل
                y_trial = AssignmentGenerator.initialize()
                gate_results_trial = []
                
                for j, g in enumerate(gates):
                    if j == i:
                        # عكس هذه البوابة
                        gr = g.apply(x, y_trial)
                        gr.activated = not gr.activated
                        gate_results_trial.append(gr)
                    else:
                        gr = g.apply(x, y_trial)
                        gate_results_trial.append(gr)
                        if gr.activated:
                            y_trial = AssignmentGenerator.apply_modifications(y_trial, gr.modifications)
                
                E_trial = energy_func.compute_full(x, y_trial, gate_results_trial)['E_total']
                
                if E_trial < best_E - self.tolerance:
                    best_E = E_trial
                    best_y = y_trial
                    best_gates = gate_results_trial
                    improved = True
            
            if not improved:
                # تقارب
                return OptimizationResult(
                    x_optimal=x,
                    y_optimal=best_y,
                    gate_results=best_gates,
                    E_total=best_E,
                    E_components=energy_func.compute_full(x, best_y, best_gates),
                    iterations=iteration + 1,
                    converged=True
                )
        
        # لم يتقارب
        return OptimizationResult(
            x_optimal=x,
            y_optimal=best_y,
            gate_results=best_gates,
            E_total=best_E,
            E_components=energy_func.compute_full(x, best_y, best_gates),
            iterations=self.max_iterations,
            converged=False
        )
