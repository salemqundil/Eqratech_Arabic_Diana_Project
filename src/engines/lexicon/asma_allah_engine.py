import pandas as pd
from engines.base import BaseReconstructionEngine, EngineLayer
from reconstruction_utils import reconstruct_from_base_df


class AsmaAllahEngine(BaseReconstructionEngine):
    SHEET_NAME = 'أسماء الله الحسنى'
    LAYER = EngineLayer.LEXICON
    GROUP = "3.6"
    SUBGROUP = "3.6.1"
    GROUP_AR = "الدينية والمتخصصة"
    SUBGROUP_AR = "أسماء الله الحسنى"

    @classmethod
    def make_df(cls):
        names = [
            "الله","الرحمن","الرحيم","الملك","القدوس","السلام","المؤمن","المهيمن","العزيز","الجبار","المتكبر","الخالق"
        ]
        data = []
        for name in names:
            data.append({
                "الأداة": name,
                "القالب/التركيب": "مفرد/مركب",
                "الفونيمات": " ".join(list(str(name))),
                "الحركات": "",
                "شرط/سياق": "يستخدم كاسم إلهي",
                "الوظيفة النحوية": "اسم علم إلهي",
                "الوظيفة الدلالية": "دلالة على الذات الإلهية أو صفاتها",
                "الوظيفة الصرفية": "جامد غالبًا",
                "الوظيفة الصوتية": "اسم صوتي واضح",
                "الوظيفة الاشتقاقية": "جامد غالبًا",
                "ملاحظات": "اسم من أسماء الله الحسنى"
            })
        df = pd.DataFrame(data)
        return reconstruct_from_base_df(df)
