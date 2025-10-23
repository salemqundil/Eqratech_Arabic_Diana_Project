"""Detached and attached pronouns used in simple sentence generation demos."""

from __future__ import annotations

import pandas as pd

from base_reconstruction_engine import BaseReconstructionEngine
from reconstruction_utils import reconstruct_from_base_df


class PronounsEngine(BaseReconstructionEngine):
    SHEET_NAME = "OU,U,OO�US"

    @classmethod
    def make_df(cls) -> pd.DataFrame:
        data = [
            {
                "OU,O�O_OOc": "PRON_HUWA",
                "OU,U,OU,O\"/OU,O�O�U�USO\"": "detached",
                "OU,U?U^U+USU.OO�": "P R O N",
                "OU,O-O�U�OO�": "F F",
            },
            {
                "OU,O�O_OOc": "PRON_ANTI",
                "OU,U,OU,O\"/OU,O�O�U�USO\"": "detached",
                "OU,U?U^U+USU.OO�": "P R O N",
                "OU,O-O�U�OO�": "F K",
            },
            {
                "OU,O�O_OOc": "PRON_HUM",
                "OU,U,OU,O\"/OU,O�O�U�USO\"": "detached",
                "OU,U?U^U+USU.OO�": "P R O N",
                "OU,O-O�U�OO�": "F D",
            },
        ]
        df = pd.DataFrame(data)
        return reconstruct_from_base_df(df)

