import pandas as pd
from base_reconstruction_engine import BaseReconstructionEngine
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
        for particle_form, particle_kind, particle_function in particles:
            rows.append({
                "الأداة": particle_form,
                "القالب/التركيب": particle_kind,
                "الفونيمات": " ".join(list(particle_form)),
                "الحركات": "",
                "شرط/سياق": particle_function,
                "الوظيفة النحوية": particle_kind,
                "الوظيفة الدلالية": particle_function,
                "الوظيفة الصرفية": "حرف مبني",
                "الوظيفة الصوتية": "قصير",
                "الوظيفة الاشتقاقية": "غير مشتق",
                "ملاحظات": "حرف مشبه بالفعل"
            })
        dataframe = pd.DataFrame(rows)
        return reconstruct_from_base_df(dataframe)
