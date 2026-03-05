"""
محرك الضمائر (Pronouns Engine)
"""

import os
import pandas as pd
from base_reconstruction_engine import BaseReconstructionEngine
from reconstruction_utils import reconstruct_from_base_df


class PronounsEngine(BaseReconstructionEngine):
    SHEET_NAME = 'الضمائر'
    
    @classmethod
    def make_df(cls):
        """Generate DataFrame for pronouns."""
        csv_path = os.path.join(os.path.dirname(__file__), 'demonstrative_pronouns.csv')
        
        if os.path.exists(csv_path):
            # Load from CSV
            df = pd.read_csv(csv_path, dtype=str).fillna('')
            
            # Map CSV columns to standard columns
            data = []
            for _, row in df.iterrows():
                name = row.get('name', '')
                gender = row.get('gender', '')
                number = row.get('number_classification', '')
                semantic = row.get('semantic_analysis', '')
                example = row.get('example', '')
                
                data.append({
                    'الأداة': name,
                    'القالب/التركيب': f'ضمير {gender} {number}',
                    'الفونيمات': '',
                    'الحركات': '',
                    'شرط/سياق': semantic,
                    'الوظيفة النحوية': 'ضمير',
                    'الوظيفة الدلالية': semantic,
                    'الوظيفة الصرفية': 'مبني',
                    'الوظيفة الصوتية': '',
                    'الوظيفة الاشتقاقية': 'غير مشتق',
                    'ملاحظات': example
                })
            
            df = pd.DataFrame(data)
        else:
            # Fallback: create basic data
            data = [
                {'الأداة': 'هو', 'القالب/التركيب': 'ضمير منفصل', 'الفونيمات': 'ه و', 'الحركات': 'ضمة سكون',
                 'شرط/سياق': 'للغائب المذكر', 'الوظيفة النحوية': 'ضمير منفصل',
                 'الوظيفة الدلالية': 'للغائب المذكر المفرد', 'الوظيفة الصرفية': 'مبني',
                 'الوظيفة الصوتية': '', 'الوظيفة الاشتقاقية': 'غير مشتق', 'ملاحظات': ''},
                {'الأداة': 'هي', 'القالب/التركيب': 'ضمير منفصل', 'الفونيمات': 'ه ي', 'الحركات': 'كسرة سكون',
                 'شرط/سياق': 'للغائبة المؤنثة', 'الوظيفة النحوية': 'ضمير منفصل',
                 'الوظيفة الدلالية': 'للغائبة المؤنثة المفردة', 'الوظيفة الصرفية': 'مبني',
                 'الوظيفة الصوتية': '', 'الوظيفة الاشتقاقية': 'غير مشتق', 'ملاحظات': ''},
                {'الأداة': 'أنا', 'القالب/التركيب': 'ضمير منفصل', 'الفونيمات': 'أ ن ا', 'الحركات': 'فتحة فتحة سكون',
                 'شرط/سياق': 'للمتكلم', 'الوظيفة النحوية': 'ضمير منفصل',
                 'الوظيفة الدلالية': 'للمتكلم المفرد', 'الوظيفة الصرفية': 'مبني',
                 'الوظيفة الصوتية': '', 'الوظيفة الاشتقاقية': 'غير مشتق', 'ملاحظات': ''},
            ]
            df = pd.DataFrame(data)
        
        return reconstruct_from_base_df(df)
