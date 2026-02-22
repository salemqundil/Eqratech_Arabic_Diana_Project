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
        
        # W = diag(1, β) حيث β يزداد مع التفخيم
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
        if not self.V_space.is_in_vowel_triangle(V):
            # خارج المجال → عقوبة ضخمة
            return 1e10
        
        # حساب البعد من الحدود
        sum_abs = abs(V[0]) + abs(V[1])
        margin = self.V_space.triangle_k - sum_abs
        
        if margin < 1e-6:
            return 1e10
        
        # log-barrier
        return -self.barrier_strength * np.log(margin)
    
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
        # 1. حساب μ
        mu = self.psi.compute_mu(C_L, C_R)
        
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
        W = self.compute_metric(flags)
        sim = self.similarity(C_L, C_R)
        
        # ∇[d'²] = 2W(V - μ)
        grad_d = 2 * W @ (V - mu)
        
        # ∇[H] = 2α·sim·V
        grad_H = 2 * self.alpha * sim * V
        
        # ∇[emphatic_bias]
        emphatic = flags.get('emphatic', 0.0)
        beta = 12.0
        grad_bias = np.array([-beta * emphatic, 0.0])
        
        # ∇[B] (تقريب عددي أو تحليلي)
        # للبساطة نستخدم فرق محدود
        eps = 1e-6
        grad_B = np.zeros_like(V)
        B_curr = self.B_barrier(V)
        for i in range(len(V)):
            V_plus = V.copy()
            V_plus[i] += eps
            B_plus = self.B_barrier(V_plus)
            grad_B[i] = (B_plus - B_curr) / eps
        
        return grad_d + grad_H + grad_B + grad_bias