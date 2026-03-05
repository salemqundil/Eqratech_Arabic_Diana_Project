import os
import pandas as pd
from engines.base import BaseReconstructionEngine, EngineLayer
from reconstruction_utils import reconstruct_from_base_df


class DemonstrativesEngine(BaseReconstructionEngine):
    SHEET_NAME = 'أسماء الإشارة'

    @classmethod
    def make_df(cls):
        csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "demonstrative_pronouns.csv")
        if not os.path.exists(csv_path):
            csv_path = "demonstrative_pronouns.csv"
        try:
            df_pronouns = pd.read_csv(csv_path)
        except Exception:
            df_pronouns = pd.DataFrame(columns=["الأداة", "النوع", "العدد", "القرب/البعد"])
        rows = []
        for _, row in df_pronouns.iterrows():
            form = str(row.get("الأداة", ""))
            ptype = str(row.get("النوع", ""))
            number = str(row.get("العدد", ""))
            distance = str(row.get("القرب/البعد", ""))
            rows.append({
                "الأداة": form,
                "القالب/التركيب": f"اسم إشارة - {ptype} - {number}",
                "الفونيمات": " ".join(list(form)),
                "الحركات": "",
                "الأثر الإعرابي": "مبني في محل حسب موقعه",
                "شرط/سياق": distance,
                "الوظيفة النحوية": "اسم إشارة",
                "الوظيفة الدلالية": f"للدلالة على {distance}",
                "الوظيفة الصرفية": "اسم مبني",
                "الوظيفة الصوتية": "وضوح صوتي",
                "الوظيفة الاشتقاقية": "غير مشتق",
                "ملاحظات": f"{ptype} {number} {distance}"
            })
        df = pd.DataFrame(rows)
        return reconstruct_from_base_df(df)
