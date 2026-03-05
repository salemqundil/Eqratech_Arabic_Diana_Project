"""
محرك أدوات النفي (Negation Tools Engine)
"""

import os
import pandas as pd
from base_reconstruction_engine import BaseReconstructionEngine
from reconstruction_utils import reconstruct_from_base_df


class NafiEngine(BaseReconstructionEngine):
    SHEET_NAME = 'أدوات النفي'
    
    @classmethod
    def make_df(cls):
        """Generate DataFrame for negation tools."""
        csv_path = os.path.join(os.path.dirname(__file__), 'tool_negatives.csv')
        
        if os.path.exists(csv_path):
            # Load from CSV
            df = pd.read_csv(csv_path, dtype=str).fillna('')
            
            # Map CSV columns to standard columns
            data = []
            for _, row in df.iterrows():
                name = row.get('name', '')
                meaning = row.get('meaning', '')
                definition = row.get('definition', '')
                notes = row.get('notes', '')
                
                data.append({
                    'الأداة': name,
                    'القالب/التركيب': 'أداة نفي',
                    'الفونيمات': '',
                    'الحركات': '',
                    'شرط/سياق': meaning,
                    'الوظيفة النحوية': 'أداة نفي',
                    'الوظيفة الدلالية': definition,
                    'الوظيفة الصرفية': 'حرف مبني',
                    'الوظيفة الصوتية': '',
                    'الوظيفة الاشتقاقية': 'غير مشتق',
                    'ملاحظات': notes
                })
            
            df = pd.DataFrame(data)
        else:
            # Fallback: create basic data
            data = [
                {'الأداة': 'لا', 'القالب/التركيب': 'أداة نفي', 'الفونيمات': 'ل ا', 'الحركات': 'فتحة سكون',
                 'شرط/سياق': 'نفي', 'الوظيفة النحوية': 'أداة نفي',
                 'الوظيفة الدلالية': 'نفي الحال', 'الوظيفة الصرفية': 'حرف مبني',
                 'الوظيفة الصوتية': '', 'الوظيفة الاشتقاقية': 'غير مشتق', 'ملاحظات': ''},
                {'الأداة': 'لم', 'القالب/التركيب': 'أداة نفي وجزم', 'الفونيمات': 'ل م', 'الحركات': 'فتحة سكون',
                 'شرط/سياق': 'نفي وجزم', 'الوظيفة النحوية': 'أداة نفي وجزم',
                 'الوظيفة الدلالية': 'نفي الماضي', 'الوظيفة الصرفية': 'حرف مبني',
                 'الوظيفة الصوتية': '', 'الوظيفة الاشتقاقية': 'غير مشتق', 'ملاحظات': ''},
                {'الأداة': 'لن', 'القالب/التركيب': 'أداة نفي ونصب', 'الفونيمات': 'ل ن', 'الحركات': 'فتحة سكون',
                 'شرط/سياق': 'نفي ونصب', 'الوظيفة النحوية': 'أداة نفي ونصب',
                 'الوظيفة الدلالية': 'نفي المستقبل', 'الوظيفة الصرفية': 'حرف مبني',
                 'الوظيفة الصوتية': '', 'الوظيفة الاشتقاقية': 'غير مشتق', 'ملاحظات': ''},
            ]
            df = pd.DataFrame(data)
        
        return reconstruct_from_base_df(df)
