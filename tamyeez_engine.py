import pandas as pd
from base_reconstruction_engine import BaseReconstructionEngine
from reconstruction_utils import reconstruct_from_base_df

class TamyeezEngine(BaseReconstructionEngine):
    SHEET_NAME = 'التمييز'

    @classmethod
    def make_df(cls):
        rows = [
            {"الأداة": "طاب زيدٌ نفسًا", "القالب/التركيب": "تمييز ذات", "الفونيمات": "", "الحركات": "", "شرط/سياق": "تمييز يوضح المبهم من الذات", "الوظيفة النحوية": "تمييز", "الوظيفة الدلالية": "إزالة إبهام", "الوظيفة الصرفية": "اسم منصوب", "الوظيفة الصوتية": "تركيب", "الوظيفة الاشتقاقية": "مشتق", "ملاحظات": "مثال"},
            {"الأداة": "اشتريت عشرين كتابًا", "القالب/التركيب": "تمييز عدد", "الفونيمات": "", "الحركات": "", "شرط/سياق": "تمييز بعد عدد", "الوظيفة النحوية": "تمييز", "الوظيفة الدلالية": "بيان المعدود", "الوظيفة الصرفية": "اسم منصوب", "الوظيفة الصوتية": "تركيب", "الوظيفة الاشتقاقية": "مشتق", "ملاحظات": "مثال"},
        ]
        dataframe = pd.DataFrame(rows)
        return reconstruct_from_base_df(dataframe)
