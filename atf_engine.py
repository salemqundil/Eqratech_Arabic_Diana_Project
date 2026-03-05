"""
محرك حروف العطف (Coordinating Conjunctions Engine)
"""

import os
import pandas as pd
from base_reconstruction_engine import BaseReconstructionEngine
from reconstruction_utils import reconstruct_from_base_df


class AtfEngine(BaseReconstructionEngine):
    SHEET_NAME = 'حروف العطف'
    
    @classmethod
    def make_df(cls):
        """Generate DataFrame for coordinating conjunctions."""
        csv_path = os.path.join(os.path.dirname(__file__), 'coordinating_conjunctions.csv')
        
        if os.path.exists(csv_path):
            # Load from CSV
            df = pd.read_csv(csv_path, dtype=str).fillna('')
            
            # Map CSV columns to standard columns
            data = []
            for _, row in df.iterrows():
                letter = row.get('letter', '')
                example = row.get('example', '')
                usages = row.get('usages', '')
                notes = row.get('notes', '')
                
                data.append({
                    'الأداة': letter,
                    'القالب/التركيب': 'حرف عطف',
                    'الفونيمات': '',
                    'الحركات': '',
                    'شرط/سياق': usages,
                    'الوظيفة النحوية': 'حرف عطف',
                    'الوظيفة الدلالية': usages,
                    'الوظيفة الصرفية': 'حرف مبني',
                    'الوظيفة الصوتية': '',
                    'الوظيفة الاشتقاقية': 'غير مشتق',
                    'ملاحظات': notes
                })
            
            df = pd.DataFrame(data)
        else:
            # Fallback: create basic data
            data = [
                {'الأداة': 'و', 'القالب/التركيب': 'حرف عطف', 'الفونيمات': 'و', 'الحركات': 'فتحة',
                 'شرط/سياق': 'للمشاركة', 'الوظيفة النحوية': 'حرف عطف',
                 'الوظيفة الدلالية': 'مطلق الجمع', 'الوظيفة الصرفية': 'حرف مبني',
                 'الوظيفة الصوتية': '', 'الوظيفة الاشتقاقية': 'غير مشتق', 'ملاحظات': ''},
                {'الأداة': 'ف', 'القالب/التركيب': 'حرف عطف', 'الفونيمات': 'ف', 'الحركات': 'فتحة',
                 'شرط/سياق': 'للترتيب والتعقيب', 'الوظيفة النحوية': 'حرف عطف',
                 'الوظيفة الدلالية': 'الترتيب مع التعقيب', 'الوظيفة الصرفية': 'حرف مبني',
                 'الوظيفة الصوتية': '', 'الوظيفة الاشتقاقية': 'غير مشتق', 'ملاحظات': ''},
                {'الأداة': 'ثم', 'القالب/التركيب': 'حرف عطف', 'الفونيمات': 'ث م', 'الحركات': 'فتحة سكون',
                 'شرط/سياق': 'للترتيب مع التراخي', 'الوظيفة النحوية': 'حرف عطف',
                 'الوظيفة الدلالية': 'الترتيب مع التراخي', 'الوظيفة الصرفية': 'حرف مبني',
                 'الوظيفة الصوتية': '', 'الوظيفة الاشتقاقية': 'غير مشتق', 'ملاحظات': ''},
            ]
            df = pd.DataFrame(data)
        
        return reconstruct_from_base_df(df)
