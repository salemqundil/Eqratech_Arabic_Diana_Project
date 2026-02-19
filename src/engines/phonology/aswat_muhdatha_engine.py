import pandas as pd
from engines.base import BaseReconstructionEngine, EngineLayer
from reconstruction_utils import reconstruct_from_base_df


class AswatMuhdathaEngine(BaseReconstructionEngine):
    SHEET_NAME = 'الأصوات المُحدثة'
    LAYER = EngineLayer.PHONOLOGY
    GROUP = "1.2"
    SUBGROUP = "1.2.1"
    GROUP_AR = "الأصوات المحدثة"
    SUBGROUP_AR = "الصوتيات المعاصرة"

    @classmethod
    def make_df(cls):
        sounds = ["هس", "حاحا", "طق", "تشيك تشيك", "كلك", "ووووو", "شششش", "طااخ", "بوم", "ترررن"]
        data = []
        for sound in sounds:
            data.append({
                "الأداة": sound,
                "القالب/التركيب": "مفرد/مركب",
                "الفونيمات": " ".join(list(str(sound))),
                "الحركات": "",
                "شرط/سياق": "يستخدم كاسم صوت",
                "الوظيفة النحوية": "اسم صوت",
                "الوظيفة الدلالية": "دلالة على صوت",
                "الوظيفة الصرفية": "جامد",
                "الوظيفة الصوتية": "اسم صوتي واضح",
                "الوظيفة الاشتقاقية": "جامد غالبًا",
                "ملاحظات": "اسم صوت محدث"
            })
        df = pd.DataFrame(data)
        return reconstruct_from_base_df(df)
