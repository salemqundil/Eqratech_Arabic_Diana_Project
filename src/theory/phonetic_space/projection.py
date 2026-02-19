"""
دالة الإسقاط ψ: F_C → F_V
Projection function ψ: F_C → F_V

تحويل الصامت إلى "تأثيره الصائتي" (vocalic influence)
"""

import numpy as np
from typing import Tuple
from theory.phonetic_space.feature_space import ConsonantSpace, VowelSpace


class ProjectionPsi:
    """
    الإسقاط الفيزيائي ψ: F_C → F_V
    
    المبدأ: الصامت يفرض "منطقة هدف" للحركة المجاورة
    بناءً على سماته الفيزيائية (مكان النطق، التفخيم، إلخ)
    """
    
    def __init__(self, consonant_space: ConsonantSpace, vowel_space: VowelSpace):
        self.C_space = consonant_space
        self.V_space = vowel_space
        
        # الثوابت الفيزيائية (Lipschitz constants وغيرها)
        self.L = 2.0  # ثابت ليبتشيتز
    
    def psi(self, consonant: np.ndarray) -> np.ndarray:
        """
        ψ(C) = تأثير الصامت على الحيز الصائتي
        
        التطبيق الفيزيائي:
        - الصامت الخلفي → backness عالي في الحركة
        - الصامت الأمامي → frontness عالي
        - manner يؤثر على height قليلاً
        
        Args:
            consonant: متجه في F_C (بعد 2)
            
        Returns:
            نقطة في F_V (بعد 2)
        """
        place = consonant[0]  # [0, 1]
        manner = consonant[1] if len(consonant) > 1 else 0.5
        
        # تحويل خطّي بسيط (Lipschitz)
        # place ∈ [0, 1] → backness ∈ [-1, 1]
        backness = 2 * place - 1  # تحويل خطي
        
        # manner يؤثر على height بشكل أضعف
        height = 0.3 * (2 * manner - 1)
        
        v_raw = np.array([backness, height])
        
        # إسقاط على المثلث الصائتي
        return self.V_space.project_to_triangle(v_raw)
    
    def is_lipschitz(self, C1: np.ndarray, C2: np.ndarray) -> Tuple[bool, float]:
        """
        اختبار شرط ليبتشيتز:
        d(ψ(C1), ψ(C2)) ≤ L·d(C1, C2)
        
        Returns:
            (is_satisfied, ratio) حيث ratio = d(ψ(C1), ψ(C2)) / d(C1, C2)
        """
        d_consonants = self.C_space.distance(C1, C2)
        if d_consonants < 1e-10:
            return True, 0.0
        
        psi_C1 = self.psi(C1)
        psi_C2 = self.psi(C2)
        d_vowels = self.V_space.distance(psi_C1, psi_C2)
        
        ratio = d_vowels / d_consonants
        return ratio <= self.L, ratio
    
    def compute_mu(self, C_L: np.ndarray, C_R: np.ndarray) -> np.ndarray:
        """
        حساب μ = (ψ(C_L) + ψ(C_R)) / 2
        "نقطة الهدف" من الصامتين
        
        Args:
            C_L: الصامت الأيسر
            C_R: الصامت الأيمن
            
        Returns:
            μ في F_V (المتوسط)
        """
        psi_L = self.psi(C_L)
        psi_R = self.psi(C_R)
        mu = 0.5 * (psi_L + psi_R)
        
        # تأكد من البقاء في المثلث
        return self.V_space.project_to_triangle(mu)
