"""
دالة طاقة المقطع E_syll(V | C_L, C_R, flags)
Syllable Energy Function

الكلفة التي نصغّرها لإيجاد الحركة الوسطى المثلى.
"""

import numpy as np
from typing import Dict, Optional
from theory.phonetic_space.feature_space import ConsonantSpace, VowelSpace
from theory.phonetic_space.projection import ProjectionPsi


class SyllableEnergy:
    """
    دالة الطاقة E_syll(V) للمقطع CVC
    
    E_syll(V) = d'(V, μ)² + H(V | C_L, C_R) + B(V)
    
    حيث:
    - d'(V, μ)²: المسافة المعدلة من μ (القرب الهندسي)
    - H(V): عقوبة الاقتصاد/OCP (ناعمة)
    - B(V): حاجز البقاء في F_V
    """
    
    def __init__(self, 
                 vowel_space: VowelSpace,
                 projection: ProjectionPsi,
                 alpha: float = 0.1,
                 barrier_strength: float = 10.0):
        """
        Args:
            vowel_space: فضاء الحركات F_V
            projection: دالة الإسقاط ψ
            alpha: معامل عقوبة الاقتصاد (≥ 0)
            barrier_strength: قوة الحاجز
        """
        self.V_space = vowel_space
        self.psi = projection
        self.alpha = alpha
        self.barrier_strength = barrier_strength
    
    def compute_metric(self, flags: Dict[str, float]) -> np.ndarray:
        """
        حساب مصفوفة المعيار W(flags)
        
        التفخيم يزيد الوزن على البعد الخلفي (backness)
        
        Args:
            flags: {'emphatic': value ∈ [0, 1], ...}
            
        Returns:
            W ≻ 0 (موجب التعريف)
        """
        emphatic = flags.get('emphatic', 0.0)
        
        # W weights the backness dimension more under emphatic influence.
        # V is represented as [backness, height].
        beta = 1.0 + 5.0 * emphatic  # β ∈ [1, 6]
        W = np.diag([beta, 1.0])
        return W
    
    def d_prime_squared(self, V: np.ndarray, mu: np.ndarray, 
                        W: np.ndarray) -> float:
        """
        d'(V, μ; W)² = (V - μ)ᵀ W (V - μ)
        
        المسافة المعدلة المربعة (quadratic form)
        """
        diff = V - mu
        return float(diff.T @ W @ diff)
    
    def similarity(self, C_L: np.ndarray, C_R: np.ndarray) -> float:
        """
        مؤشر التقارب المخرجي sim(C_L, C_R) ∈ [0, 1]
        
        كلما كان الصامتان أقرب → sim أعلى → عقوبة OCP أكبر
        """
        dist = self.psi.C_space.distance(C_L, C_R)
        # تحويل إلى تقارب: sim = exp(-d²)
        sim = np.exp(-dist**2)
        return float(sim)
    
    def H_economy(self, V: np.ndarray, C_L: np.ndarray, 
                  C_R: np.ndarray) -> float:
        """
        عقوبة الاقتصاد/OCP:
        H(V | C_L, C_R) = α · sim(C_L, C_R) · ||V||²
        
        إذا كان الصامتان متقاربين → نكافئ حركة أصغر (أقرب للمركز)
        """
        sim = self.similarity(C_L, C_R)
        v_norm_sq = np.linalg.norm(V)**2
        return self.alpha * sim * v_norm_sq
    
    def emphatic_bias(self, V: np.ndarray, flags: Dict[str, float]) -> float:
        """
        انحياز التفخيم: يدفع V[0] (backness) للموجب
        
        Bias = -β · emphatic · V[0]
        """
        emphatic = flags.get('emphatic', 0.0)
        beta = 12.0
        return -beta * emphatic * V[0]
    
    def B_barrier(self, V: np.ndarray) -> float:
        """
        حاجز البقاء في F_V (log-barrier)
        
        B(V) = -barrier_strength · Σ log(-g_j(V))
        حيث g_j(V) ≤ 0 هي قيود المثلث الصائتي
        
        Note: لوغاريتم يؤدي إلى ∞ عند الحافة
        """
        # Smooth-ish barrier/penalty around the triangle boundary.
        # Constraint (smoothed): |v0| + |v1| <= k
        # We smooth abs to keep the objective differentiable for optimizers.
        eps_abs = 1e-12
        smooth_abs0 = float(np.sqrt(V[0] * V[0] + eps_abs))
        smooth_abs1 = float(np.sqrt(V[1] * V[1] + eps_abs))
        sum_abs = smooth_abs0 + smooth_abs1
        margin = self.V_space.triangle_k - sum_abs

        # Outside the triangle: quadratic penalty (keeps optimizer stable).
        if margin <= 0.0:
            return 1e6 * (-(margin) + 1e-6) ** 2

        # Inside: log barrier (avoid log(0) with eps).
        eps = 1e-8
        return -self.barrier_strength * np.log(margin + eps)
    
    def __call__(self, V: np.ndarray, C_L: np.ndarray, C_R: np.ndarray,
                 flags: Dict[str, float]) -> float:
        """
        حساب الطاقة الكلية:
        E_syll(V) = d'(V, μ)² + H(V) + B(V)
        
        Args:
            V: الحركة المرشحة
            C_L: الصامت الأيسر
            C_R: الصامت الأيمن
            flags: أعلام التفخيم وغيرها
            
        Returns:
            الطاقة (قيمة عددية)
        """
        # 1. حساب μ (+ emphatic bias shift)
        mu = self.psi.compute_mu(C_L, C_R)
        emphatic = float(flags.get("emphatic", 0.0) or 0.0)
        if emphatic > 0:
            # Bias the target toward backness under emphatic influence.
            mu = self.V_space.project_to_triangle(mu + np.array([0.25 * emphatic, 0.0]))
        
        # 2. حساب W
        W = self.compute_metric(flags)
        
        # 3. الحد الأول: d'²
        term1 = self.d_prime_squared(V, mu, W)
        
        # 4. الحد الثاني: H (OCP)
        term2 = self.H_economy(V, C_L, C_R)
        
        # 5. الحد الثالث: B (barrier)
        term3 = self.B_barrier(V)
        
        # 6. الحد الرابع: emphatic bias
        term4 = self.emphatic_bias(V, flags)
        
        return term1 + term2 + term3 + term4
    
    def gradient(self, V: np.ndarray, C_L: np.ndarray, C_R: np.ndarray,
                 flags: Dict[str, float]) -> np.ndarray:
        """
        حساب التدرج ∇E_syll(V)
        
        للمصغِّر Gradient-based
        """
        mu = self.psi.compute_mu(C_L, C_R)
        emphatic = float(flags.get("emphatic", 0.0) or 0.0)
        if emphatic > 0:
            mu = self.V_space.project_to_triangle(mu + np.array([0.25 * emphatic, 0.0]))
        W = self.compute_metric(flags)
        sim = self.similarity(C_L, C_R)
        
        # ∇[d'²] = 2W(V - μ)
        grad_d = 2 * W @ (V - mu)
        
        # ∇[H] = 2α·sim·V
        grad_H = 2 * self.alpha * sim * V
        
        # ∇[B] (analytic for our triangle barrier/penalty)
        k = self.V_space.triangle_k
        eps_abs = 1e-12
        smooth_abs0 = float(np.sqrt(V[0] * V[0] + eps_abs))
        smooth_abs1 = float(np.sqrt(V[1] * V[1] + eps_abs))
        sum_abs = smooth_abs0 + smooth_abs1
        margin = k - sum_abs
        # d/dx sqrt(x^2+eps) = x/sqrt(x^2+eps)
        dabs0 = float(V[0] / smooth_abs0)
        dabs1 = float(V[1] / smooth_abs1)

        if margin <= 0.0:
            # penalty = 1e6 * (-(margin)+1e-6)^2, where margin = k - sum_abs
            t = (-(margin) + 1e-6)
            dpen_dsum = 2.0 * 1e6 * t  # d/d(sum_abs)
            grad_B = np.array([dpen_dsum * dabs0, dpen_dsum * dabs1])
        else:
            eps = 1e-8
            # barrier = -b log(margin+eps), d/d(sum_abs) = b/(margin+eps)
            dbar_dsum = self.barrier_strength / (margin + eps)
            grad_B = np.array([dbar_dsum * dabs0, dbar_dsum * dabs1])

        return grad_d + grad_H + grad_B
