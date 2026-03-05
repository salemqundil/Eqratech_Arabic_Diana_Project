"""
محرك الحركات
يوفر هذا الملف وظيفة لتحميل بيانات الحركات العربية من ملف CSV.
"""

import os
import pandas as pd


class حركات:
    """محرك لتحميل ومعالجة بيانات الحركات العربية."""
    
    @staticmethod
    def make_df(csv_path: str = None) -> pd.DataFrame:
        """تحميل جدول الحركات من ملف CSV.
        
        Args:
            csv_path: مسار ملف CSV. إذا لم يحدد، يستخدم الملف الافتراضي.
            
        Returns:
            pd.DataFrame: إطار بيانات يحتوي على معلومات الحركات
        """
        if csv_path is None:
            # البحث عن ملف الحركات في المجلد الحالي
            base_dir = os.path.dirname(__file__)
            
            # محاولة الملفات المحتملة بالترتيب
            possible_files = [
                os.path.join(base_dir, 'Harakat.csv'),
                os.path.join(base_dir, 'الحركات.csv'),
                os.path.join(base_dir, 'الحركات_كامل.csv'),
            ]
            
            for f in possible_files:
                if os.path.exists(f):
                    csv_path = f
                    break
            
            if csv_path is None:
                # إنشاء DataFrame فارغ بالأعمدة المطلوبة
                return pd.DataFrame(columns=[
                    'الحركات', 'شكل الحركة', 'نوع الوظيفة', 'الوظيفة',
                    'نوع العلامة', 'Unicode', 'UTF-8', 'الوصف'
                ])
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"ملف الحركات غير موجود: {csv_path}")
        
        # تحميل CSV
        try:
            df = pd.read_csv(csv_path, dtype=str).fillna('')
        except Exception:
            # محاولة مع ترميز مختلف
            df = pd.read_csv(csv_path, dtype=str, encoding='utf-8-sig').fillna('')
        
        return df
