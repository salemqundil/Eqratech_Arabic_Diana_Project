import pandas as pd
from engines.base import BaseReconstructionEngine, EngineLayer
from reconstruction_utils import reconstruct_from_base_df


class KainatGhairAqilaEngine(BaseReconstructionEngine):
    SHEET_NAME = 'الكائنات غير العاقلة'
    LAYER = EngineLayer.LEXICON
    GROUP = "3.5"
    SUBGROUP = "3.5.2"
    GROUP_AR = "التصنيفات الدلالية"
    SUBGROUP_AR = "الكائنات غير العاقلة"

    @classmethod
    def make_df(cls):
        names = ["أسد","نمر","فهد","ذئب","ثعلب","دب","فيل","جمل","حصان","بغل"]
        data = []
        for name in names:
            data.append({
                "الأداة": name,
                "القالب/التركيب": "مفرد/جمع",
                "الفونيمات": " ".join(list(str(name))),
                "الحركات": "",
                "شرط/سياق": "يستخدم كاسم كائن غير عاقل",
                "الوظيفة النحوية": "اسم كائن غير عاقل",
                "الوظيفة الدلالية": "دلالة على كائن غير عاقل",
                "الوظيفة الصرفية": "جامد غالبًا",
                "الوظيفة الصوتية": "اسم صوتي واضح",
                "الوظيفة الاشتقاقية": "جامد غالبًا",
                "ملاحظات": "اسم كائن غير عاقل"
            })
        df = pd.DataFrame(data)
        return reconstruct_from_base_df(df)
