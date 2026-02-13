"""
فضاء السمات الفيزيائية F (Physical Feature Space)

لا قوائم لغوية - فقط فضاء هندسي مع مسافة d.
No linguistic lists - only geometric space with distance d.
"""

import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class PhysicalConstraints:
    """قيود فيزيائية (لا لغوية) - Physical constraints (not linguistic)"""
    min_bounds: np.ndarray  # الحدود الدنيا
    max_bounds: np.ndarray  # الحدود العليا
    
    def is_valid(self, point: np.ndarray) -> bool:
        """هل النقطة داخل الحدود الفيزيائية؟"""
        return np.all(point >= self.min_bounds) and np.all(point <= self.max_bounds)


class FeatureSpace:
    """
    فضاء السمات العام F
    General Feature Space F
    
    البعد n = 2 للبداية:
    - البعد الأول (dim 0): frontness/backness (أمامي/خلفي) ∈ [-1, 1]
    - البعد الثاني (dim 1): openness/height (انفتاح/ارتفاع) ∈ [-1, 1]
    
    Note: لا نسمي "a, i, u" - هذه مناطق في F فقط.
    """
    
    def __init__(self, dim: int = 2):
        """
        Args:
            dim: عدد الأبعاد (dimension)
        """
        self.dim = dim
        self.constraints = PhysicalConstraints(
            min_bounds=np.full(dim, -1.0),
            max_bounds=np.full(dim, 1.0)
        )
    
    def distance(self, u: np.ndarray, v: np.ndarray, 
                 metric: Optional[np.ndarray] = None) -> float:
        """
        المسافة d(u, v) أو d'(u, v; flags) مع معيار معدل
        
        Args:
            u, v: نقاط في F
            metric: مصفوفة المعيار W (إن كانت None نستخدم الإقليدية)
            
        Returns:
            المسافة (الجذر التربيعي للصيغة التربيعية)
        """
        diff = u - v
        if metric is None:
            # المسافة الإقليدية العادية
            return np.linalg.norm(diff)
        else:
            # المسافة المعدلة: sqrt((u-v)^T W (u-v))
            return np.sqrt(diff.T @ metric @ diff)
    
    def is_compact(self, region_bounds: Tuple[np.ndarray, np.ndarray]) -> bool:
        """
        هل المنطقة مدمجة (compact)؟
        
        في R^n المحدود المغلق = مدمج (Heine-Borel)
        """
        min_b, max_b = region_bounds
        is_bounded = np.all(np.isfinite(min_b)) and np.all(np.isfinite(max_b))
        is_closed = True  # نفترضها مغلقة بالتعريف
        return is_bounded and is_closed


class ConsonantSpace(FeatureSpace):
    """
    فضاء الصوامت F_C ⊂ F
    
    سمات الصامت (فيزيائية فقط):
    - البعد 0: place of articulation (مكان النطق) ∈ [0, 1]
      (0=labial أمامي، 1=uvular خلفي)
    - البعد 1: manner (طريقة النطق) ∈ [0, 1]
      (0=stop انفجاري، 1=fricative احتكاكي)
    
    + سمات إضافية (flags):
    - emphatic (تفخيم/استعلاء): binary أو continuous ∈ [0, 1]
    """
    
    def __init__(self):
        super().__init__(dim=2)
        # نضيف حقل للسمات الثنائية/الإضافية
        self.feature_names = ['place', 'manner']
    
    def extract_flags(self, consonant: np.ndarray) -> dict:
        """
        استخراج الأعلام (flags) من سمات الصامت
        
        هنا نضع قاعدة فيزيائية بسيطة:
        - إذا كان place > 0.6 (خلفي) → emphatic tendency عالية
        """
        place = consonant[0]
        manner = consonant[1] if len(consonant) > 1 else 0.0
        
        # تفخيم = دالة ناعمة من الخلفية
        emphatic = max(0.0, (place - 0.4) / 0.6)  # ∈ [0, 1]
        
        return {
            'emphatic': emphatic,
            'place': place,
            'manner': manner
        }


class VowelSpace(FeatureSpace):
    """
    فضاء الحركات F_V ⊂ F
    
    نفس البعدين لكن بحدود مختلفة قليلاً:
    - البعد 0: frontness/backness ∈ [-1, 1]
      (-1 = front أمامي، +1 = back خلفي)
    - البعد 1: height (ارتفاع) ∈ [-1, 1]
      (-1 = low منخفض/مفتوح، +1 = high مرتفع/مغلق)
    
    المنطقة المثلثية الصائتية تُعرَّف كقيود محدبة:
    |v[1]| + |v[0]| ≤ k (مثلث تقريبي)
    """
    
    def __init__(self):
        super().__init__(dim=2)
        self.feature_names = ['backness', 'height']
        # قيود إضافية للمثلث الصائتي
        self.triangle_k = 1.5  # معامل المثلث
    
    def is_in_vowel_triangle(self, v: np.ndarray) -> bool:
        """
        هل v داخل المثلث الصائتي؟
        
        القيد: |v[0]| + |v[1]| ≤ k
        """
        return (abs(v[0]) + abs(v[1])) <= self.triangle_k
    
    def project_to_triangle(self, v: np.ndarray) -> np.ndarray:
        """إسقاط نقطة على المثلث الصائتي (أقرب نقطة صالحة)"""
        if self.is_in_vowel_triangle(v):
            return v.copy()
        
        # إسقاط بسيط: تصغير بنسبة
        norm = abs(v[0]) + abs(v[1])
        scale = self.triangle_k / (norm + 1e-10)
        return v * scale
    
    def get_vowel_region_name(self, v: np.ndarray) -> str:
        """
        (للتصحيح فقط - ليس جزءاً من النظرية!)
        نسمي المناطق بأسماء توضيحية:
        """
        back, height = v[0], v[1]
        
        # المناطق التقريبية
        if height > 0.4:  # high
            if back < -0.3:
                return "i-like (front-high)"
            elif back > 0.3:
                return "u-like (back-high)"
            else:
                return "high-central"
        elif height < -0.4:  # low
            return "a-like (low/open)"
        else:
            return "mid"
