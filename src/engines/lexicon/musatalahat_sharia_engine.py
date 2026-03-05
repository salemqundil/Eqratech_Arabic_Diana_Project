import pandas as pd
from engines.base import BaseReconstructionEngine, EngineLayer
from reconstruction_utils import reconstruct_from_base_df


class MusatalahatShariaEngine(BaseReconstructionEngine):
    SHEET_NAME = 'المصطلحات الشرعية'
    LAYER = EngineLayer.LEXICON
    GROUP = "3.6"
    SUBGROUP = "3.6.2"
    GROUP_AR = "الدينية والمتخصصة"
    SUBGROUP_AR = "المصطلحات الشرعية"

    @classmethod
    def make_df(cls):
        names = ["الصلاة","الصوم","الزكاة","الحج","الطلاق","العقد","العبد","المؤمن","المسلم","المحسن","الدابّة","النكاح","الربا","العبد"]
        data = []
        for name in names:
            data.append({
                "الأداة": name,
                "القالب/التركيب": "مفرد/مركب",
                "الفونيمات": " ".join(list(str(name))),
                "الحركات": "",
                "شرط/سياق": "يستخدم في السياق الشرعي فقط",
                "الوظيفة النحوية": "اسم مصطلح شرعي",
                "الوظيفة الدلالية": "دلالة على مفهوم شرعي جامد",
                "الوظيفة الصرفية": "جامد غالبًا",
                "الوظيفة الصوتية": "اسم صوتي واضح",
                "الوظيفة الاشتقاقية": "جامد غالبًا",
                "ملاحظات": "مصطلح شرعي جامد لا يقبل الاشتقاق غالبًا"
            })
        df = pd.DataFrame(data)
        return reconstruct_from_base_df(df)
