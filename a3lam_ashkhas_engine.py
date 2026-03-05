import pandas as pd
from base_reconstruction_engine import BaseReconstructionEngine
from reconstruction_utils import reconstruct_from_base_df


class A3lamAshkhasEngine(BaseReconstructionEngine):
    SHEET_NAME = 'أعلام الأشخاص'

    @classmethod
    def make_df(cls):
        names = [
            "زيد", "عمرو", "مريم", "خديجة", "سعد", "سلمى", "آدم", "حواء", "يوسف", "يعقوب", "إسماعيل", "إبراهيم", "لقمان"
        ]
        data = []
        for name in names:
            data.append({
                "الأداة": name,
                "القالب/التركيب": "مفرد/مركب حسب الاسم",
                "الفونيمات": " ".join(list(str(name))),
                "الحركات": "",
                "شرط/سياق": "يستخدم كاسم شخص",
                "الوظيفة النحوية": "اسم علم شخص",
                "الوظيفة الدلالية": "دلالة على شخص",
                "الوظيفة الصرفية": "جامد غالبًا",
                "الوظيفة الصوتية": "اسم صوتي واضح",
                "الوظيفة الاشتقاقية": "جامد غالبًا",
                "ملاحظات": "اسم شخص معروف"
            })
        dataframe = pd.DataFrame(data)
        return reconstruct_from_base_df(dataframe)
