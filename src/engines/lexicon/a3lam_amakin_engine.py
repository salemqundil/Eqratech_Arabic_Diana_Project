import pandas as pd
from engines.base import BaseReconstructionEngine, EngineLayer
from reconstruction_utils import reconstruct_from_base_df


class A3lamAmakinEngine(BaseReconstructionEngine):
    SHEET_NAME = 'أعلام الأماكن'
    LAYER = EngineLayer.LEXICON
    GROUP = "3.1"
    SUBGROUP = "3.1.2"
    GROUP_AR = "الأعلام"
    SUBGROUP_AR = "أعلام الأماكن"

    @classmethod
    def make_df(cls):
        names = [
            "مكة", "المدينة", "دمشق", "بغداد", "القاهرة", "الإسكندرية", "الأردن", "فلسطين", "اليمن", "عدن", "حمص", "حلب", "العراق", "إيران", "جرش", "عجلون", "الكرك"
        ]
        data = []
        for name in names:
            data.append({
                "الأداة": name,
                "القالب/التركيب": "مفرد/مركب حسب الاسم",
                "الفونيمات": " ".join(list(str(name))),
                "الحركات": "",
                "شرط/سياق": "يستخدم كاسم مكان",
                "الوظيفة النحوية": "اسم علم مكان",
                "الوظيفة الدلالية": "دلالة على مكان",
                "الوظيفة الصرفية": "جامد غالبًا",
                "الوظيفة الصوتية": "اسم صوتي واضح",
                "الوظيفة الاشتقاقية": "جامد غالبًا",
                "ملاحظات": "اسم مكان معروف"
            })
        df = pd.DataFrame(data)
        return reconstruct_from_base_df(df)
