import pandas as pd
import os
from engines.base import BaseReconstructionEngine, EngineLayer
from reconstruction_utils import reconstruct_from_base_df


class IstifhamEngine(BaseReconstructionEngine):
    SHEET_NAME = 'الاستفهام'
    LAYER = EngineLayer.SYNTAX
    GROUP = "4.3"
    SUBGROUP = "4.3.1"
    GROUP_AR = "الاستفهام"
    SUBGROUP_AR = "أدوات الاستفهام"
    INPUT_CSV = r"C:\Users\user\Downloads\Cam_Eqraatech\Diana\full_multilayer_grammar_الاستفهام.csv"

    @classmethod
    def make_df(cls):
        if not os.path.exists(cls.INPUT_CSV):
            raise FileNotFoundError(f"لم يتم العثور على ملف الإدخال: {cls.INPUT_CSV}")
        try:
            base_df = pd.read_csv(cls.INPUT_CSV, dtype=str).fillna('')
        except Exception:
            base_df = pd.read_csv(cls.INPUT_CSV, dtype=str, encoding='utf-8-sig').fillna('')
        return reconstruct_from_base_df(base_df)

if __name__ == '__main__':
    IstifhamEngine.make_df()
