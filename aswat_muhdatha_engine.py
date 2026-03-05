import pandas as pd
from base_reconstruction_engine import BaseReconstructionEngine
from reconstruction_utils import reconstruct_from_base_df


class AswatMuhdathaEngine(BaseReconstructionEngine):
    SHEET_NAME = 'الأصوات المُحدثة'

    @classmethod
    def make_df(cls):
        sounds = ["هس","حاحا","طق","تشيك تشيك","كلك","ووووو","شششش","طااخ","بوم","ترررن"]
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
        dataframe = pd.DataFrame(data)
        return reconstruct_from_base_df(dataframe)
