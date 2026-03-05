"""
محرك حروف الجر (Prepositions Engine)
"""

import os
import pandas as pd
from base_reconstruction_engine import BaseReconstructionEngine
from reconstruction_utils import reconstruct_from_base_df


class JarEngine(BaseReconstructionEngine):
    SHEET_NAME = 'حروف الجر'
    
    @classmethod
    def make_df(cls):
        """Generate DataFrame for prepositions."""
        csv_path = os.path.join(os.path.dirname(__file__), 'preposition_meanings.csv')
        
        if os.path.exists(csv_path):
            # Load from CSV
            df = pd.read_csv(csv_path, dtype=str).fillna('')
            
            # Map CSV columns to standard columns
            data = []
            for _, row in df.iterrows():
                preposition = row.get('preposition', '')
                meaning = row.get('meaning', '')
                example = row.get('example', '')
                
                data.append({
                    'الأداة': preposition,
                    'القالب/التركيب': 'حرف جر',
                    'الفونيمات': '',
                    'الحركات': '',
                    'شرط/سياق': meaning,
                    'الوظيفة النحوية': 'حرف جر',
                    'الوظيفة الدلالية': meaning,
                    'الوظيفة الصرفية': 'حرف مبني',
                    'الوظيفة الصوتية': '',
                    'الوظيفة الاشتقاقية': 'غير مشتق',
                    'ملاحظات': example
                })
            
            df = pd.DataFrame(data)
        else:
            # Fallback: create basic data
            data = [
                {'الأداة': 'من', 'القالب/التركيب': 'حرف جر', 'الفونيمات': 'م ن', 'الحركات': 'فتحة سكون',
                 'شرط/سياق': 'ابتداء الغاية', 'الوظيفة النحوية': 'حرف جر',
                 'الوظيفة الدلالية': 'ابتداء الغاية الزمانية أو المكانية', 'الوظيفة الصرفية': 'حرف مبني',
                 'الوظيفة الصوتية': '', 'الوظيفة الاشتقاقية': 'غير مشتق', 'ملاحظات': ''},
                {'الأداة': 'إلى', 'القالب/التركيب': 'حرف جر', 'الفونيمات': 'إ ل ى', 'الحركات': 'كسرة فتحة سكون',
                 'شرط/سياق': 'انتهاء الغاية', 'الوظيفة النحوية': 'حرف جر',
                 'الوظيفة الدلالية': 'انتهاء الغاية الزمانية أو المكانية', 'الوظيفة الصرفية': 'حرف مبني',
                 'الوظيفة الصوتية': '', 'الوظيفة الاشتقاقية': 'غير مشتق', 'ملاحظات': ''},
                {'الأداة': 'في', 'القالب/التركيب': 'حرف جر', 'الفونيمات': 'ف ي', 'الحركات': 'كسرة سكون',
                 'شرط/سياق': 'ظرفية', 'الوظيفة النحوية': 'حرف جر',
                 'الوظيفة الدلالية': 'الظرفية المكانية أو الزمانية', 'الوظيفة الصرفية': 'حرف مبني',
                 'الوظيفة الصوتية': '', 'الوظيفة الاشتقاقية': 'غير مشتق', 'ملاحظات': ''},
            ]
            df = pd.DataFrame(data)
        
        return reconstruct_from_base_df(df)
