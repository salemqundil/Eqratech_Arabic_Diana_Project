import pandas as pd
from base_reconstruction_engine import BaseReconstructionEngine
from reconstruction_utils import reconstruct_from_base_df


class MusatalahatShariaEngine(BaseReconstructionEngine):
    SHEET_NAME = 'المصطلحات الشرعية'

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
        dataframe = pd.DataFrame(data)
        return reconstruct_from_base_df(dataframe)
