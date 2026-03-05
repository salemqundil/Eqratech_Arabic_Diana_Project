import pandas as pd
from engines.base import BaseReconstructionEngine, EngineLayer
from reconstruction_utils import reconstruct_from_base_df


class A3lamManqulaEngine(BaseReconstructionEngine):
    SHEET_NAME = 'الأعلام المنقولة'
    LAYER = EngineLayer.LEXICON
    GROUP = "3.1"
    SUBGROUP = "3.1.3"
    GROUP_AR = "الأعلام"
    SUBGROUP_AR = "الأعلام المنقولة"

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
        df = pd.DataFrame(data)
        return reconstruct_from_base_df(df)
