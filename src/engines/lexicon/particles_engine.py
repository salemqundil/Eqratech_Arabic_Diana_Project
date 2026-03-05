import pandas as pd
from engines.base import BaseReconstructionEngine, EngineLayer
from reconstruction_utils import reconstruct_from_base_df


class ParticlesEngine(BaseReconstructionEngine):
    SHEET_NAME = 'الحروف'

    @classmethod
    def make_df(cls):
        particles = [
            ("إن", "حرف مشبه بالفعل", "توكيد"),
            ("أن", "حرف مشبه بالفعل", "توكيد"),
            ("لكن", "حرف مشبه بالفعل", "استدراك"),
            ("لعل", "حرف مشبه بالفعل", "ترجي"),
            ("ليت", "حرف مشبه بالفعل", "تمني"),
        ]
        rows = []
        for form, kind, function in particles:
            rows.append({
                "الأداة": form,
                "القالب/التركيب": kind,
                "الفونيمات": " ".join(list(form)),
                "الحركات": "",
                "شرط/سياق": function,
                "الوظيفة النحوية": kind,
                "الوظيفة الدلالية": function,
                "الوظيفة الصرفية": "حرف مبني",
                "الوظيفة الصوتية": "قصير",
                "الوظيفة الاشتقاقية": "غير مشتق",
                "ملاحظات": "حرف مشبه بالفعل"
            })
        df = pd.DataFrame(rows)
        return reconstruct_from_base_df(df)
