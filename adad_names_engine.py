import pandas as pd
from base_reconstruction_engine import BaseReconstructionEngine
from reconstruction_utils import reconstruct_from_base_df


class AdadNamesEngine(BaseReconstructionEngine):
    SHEET_NAME = 'أسماء الأعداد'

    @classmethod
    def make_df(cls):
        data = []
        names = [
            "واحد", "واحدة", "اثنان", "اثنتان", "اثنين", "اثنتين", "ثلاثة", "ثلاث", "أربع", "أربعة", "خمس", "خمسة", "ست", "ستة", "سبع", "سبعة", "ثماني", "ثمانية", "تسع", "تسعة", "عشر", "عشرة"
        ]
        for name in names:
            data.append({
                "الأداة": name,
                "القالب/التركيب": "اسم عدد",
                "الفونيمات": " ".join([c for c in name]),
                "الحركات": "-",
                "الأثر الإعرابي": "حسب الموقع",
                "شرط/سياق": "يدل على العدد",
                "عدد الفونيمات": len(name.replace(" ", "")),
                "الحالة الإعرابية": "حسب الموقع",
                "الوظيفة النحوية": "اسم عدد",
                "الوظيفة الدلالية": "يدل على العدد",
                "الوظيفة الصرفية": "اسم جامد",
                "الوظيفة الصوتية": "لا يوجد",
                "الوظيفة الاشتقاقية": "غير مشتق",
                "ملاحظات": "يستخدم للدلالة على العدد"
            })
        dataframe = pd.DataFrame(data)
        return reconstruct_from_base_df(dataframe)
