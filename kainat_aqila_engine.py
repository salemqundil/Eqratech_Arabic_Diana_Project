import pandas as pd
from base_reconstruction_engine import BaseReconstructionEngine
from reconstruction_utils import reconstruct_from_base_df


class KainatAqilaEngine(BaseReconstructionEngine):
    SHEET_NAME = 'الكائنات العاقلة'

    @classmethod
    def make_df(cls):
        names = ["رجل","جنين","سِقْط","مولود","مولودة","رضيع","رضيعة","فطيم","فطيمة","دارج","دارجة","طفل","طفلة","صبي","صبية","غلام","جارية","يافع","ناهِد","مراهق","معصر","حَدَث","فتاة","شاب","بكر","فتى","عروس","كهل","امرأة","شيخ","سيدة","هرم","عجوز"]
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
        dataframe = pd.DataFrame(data)
        return reconstruct_from_base_df(dataframe)
