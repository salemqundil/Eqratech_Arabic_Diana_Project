"""Simple conjunction (ʔaṭf) engine used by the sentence generator."""

from __future__ import annotations

import pandas as pd

from base_reconstruction_engine import BaseReconstructionEngine
from reconstruction_utils import reconstruct_from_base_df


class AtfEngine(BaseReconstructionEngine):
    SHEET_NAME = "O+O�O�"

    @classmethod
    def make_df(cls) -> pd.DataFrame:
        data = [
            {
                "OU,O�O_OOc": "CONJ_WAW",
                "OU,U,OU,O\"/OU,O�O�U�USO\"": "coord",
                "OU,U?U^U+USU.OO�": "C O N J",
                "OU,O-O�U�OO�": "F F F F",
            },
            {
                "OU,O�O_OOc": "CONJ_THUMMA",
                "OU,U,OU,O\"/OU,O�O�U�USO\"": "seq",
                "OU,U?U^U+USU.OO�": "C O N J",
                "OU,O-O�U�OO�": "F K F",
            },
            {
                "OU,O�O_OOc": "CONJ_AW",
                "OU,U,OU,O\"/OU,O�O�U�USO\"": "choice",
                "OU,U?U^U+USU.OO�": "C O N J",
                "OU,O-O�U�OO�": "F S",
            },
        ]
        df = pd.DataFrame(data)
        return reconstruct_from_base_df(df)

