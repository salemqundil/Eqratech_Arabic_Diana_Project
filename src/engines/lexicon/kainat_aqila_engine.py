import pandas as pd
from engines.base import BaseReconstructionEngine, EngineLayer
from reconstruction_utils import reconstruct_from_base_df


class KainatAqilaEngine(BaseReconstructionEngine):
    SHEET_NAME = 'الكائنات العاقلة'
    LAYER = EngineLayer.LEXICON
    GROUP = "3.5"
    SUBGROUP = "3.5.1"
    GROUP_AR = "التصنيفات الدلالية"
    SUBGROUP_AR = "الكائنات العاقلة"

    @classmethod
    def make_df(cls):
        names = ["رجل","جنين","سِقْط","مولود","مولودة","رضيع","رضيعة","فطيم","فطيمة","دارج","دارجة","طفل","طفلة"]
        data = []
        for name in names:
            data.append({
                "الأداة": name,
                "القالب/التركيب": "مفرد/جمع",
                "الفونيمات": " ".join(list(str(name))),
                "الحركات": "",
                "شرط/سياق": "يستخدم كاسم كائن عاقل",
                "الوظيفة النحوية": "اسم كائن عاقل",
                "الوظيفة الدلالية": "دلالة على كائن عاقل",
                "الوظيفة الصرفية": "جامد غالبًا",
                "الوظيفة الصوتية": "اسم صوتي واضح",
                "الوظيفة الاشتقاقية": "جامد غالبًا",
                "ملاحظات": "اسم كائن عاقل"
            })
        df = pd.DataFrame(data)
        return reconstruct_from_base_df(df)
