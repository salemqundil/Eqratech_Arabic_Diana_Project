import pandas as pd
from base_reconstruction_engine import BaseReconstructionEngine
from reconstruction_utils import reconstruct_from_base_df


class A3lamManqulaEngine(BaseReconstructionEngine):
    SHEET_NAME = 'الأعلام المنقولة'

    @classmethod
    def make_df(cls):
        names = [
            "حامد", "شاكر", "رافع", "ناصر", "فاتح", "قاهر", "حازم", "جاسم", "مستنير", "متعاون", "متفوق", "منتصر", "منتظر", "مؤمن", "فاضلة", "ساجدة", "حامدة", "شاكرة", "راشدة", "فاطمة", "عالمة", "فائقة", "سامية", "هادي", "ساجد", "عابد", "زاهد", "راشد", "عاصم", "حافظ", "سالم"
        ]
        data = []
        for name in names:
            data.append({
                "الأداة": name,
                "القالب/التركيب": "مفرد/مركب حسب الاسم",
                "الفونيمات": " ".join(list(str(name))),
                "الحركات": "",
                "شرط/سياق": "يستخدم كاسم شخص أو صفة",
                "الوظيفة النحوية": "اسم علم",
                "الوظيفة الدلالية": "دلالة على شخص أو صفة",
                "الوظيفة الصرفية": "مشتق أو جامد",
                "الوظيفة الصوتية": "اسم صوتي واضح",
                "الوظيفة الاشتقاقية": "مشتق غالبًا",
                "ملاحظات": "اسم منقول من صفة أو فعل"
            })
        dataframe = pd.DataFrame(data)
        return reconstruct_from_base_df(dataframe)
