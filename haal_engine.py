import pandas as pd
from base_reconstruction_engine import BaseReconstructionEngine
from reconstruction_utils import reconstruct_from_base_df

class HaalEngine(BaseReconstructionEngine):
    SHEET_NAME = 'الحال'

    @classmethod
    def make_df(cls):
        rows = [
            {"الأداة": "جاء زيدٌ ضاحكًا", "القالب/التركيب": "حال مفرد", "الفونيمات": "", "الحركات": "", "شرط/سياق": "يبين هيئة الفاعل", "الوظيفة النحوية": "حال", "الوظيفة الدلالية": "هيئة", "الوظيفة الصرفية": "اسم منصوب", "الوظيفة الصوتية": "ضاد مفخمة", "الوظيفة الاشتقاقية": "مشتق", "ملاحظات": "مثال"},
            {"الأداة": "أقبل الطلاب مسرعين", "القالب/التركيب": "حال جمع", "الفونيمات": "", "الحركات": "", "شرط/سياق": "يبين هيئة الفاعلين", "الوظيفة النحوية": "حال", "الوظيفة الدلالية": "هيئة", "الوظيفة الصرفية": "جمع", "الوظيفة الصوتية": "سكون في الوسط", "الوظيفة الاشتقاقية": "مشتق", "ملاحظات": "مثال"},
        ]
        dataframe = pd.DataFrame(rows)
        return reconstruct_from_base_df(dataframe)
