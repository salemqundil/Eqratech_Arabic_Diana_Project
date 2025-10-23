"""Negation (nafi) particles for sentence generation."""

from __future__ import annotations

import pandas as pd

from base_reconstruction_engine import BaseReconstructionEngine
from reconstruction_utils import reconstruct_from_base_df


class NafiEngine(BaseReconstructionEngine):
    SHEET_NAME = "O+U?US"

    @classmethod
    def make_df(cls) -> pd.DataFrame:
        data = [
            {
                "OU,O�O_OOc": "NEG_LA",
                "OU,U,OU,O\"/OU,O�O�U�USO\"": "simple",
                "OU,U?U^U+USU.OO�": "N E G",
                "OU,O-O�U�OO�": "F F",
            },
            {
                "OU,O�O_OOc": "NEG_MA",
                "OU,U,OU,O\"/OU,O�O�U�USO\"": "perfective",
                "OU,U?U^U+USU.OO�": "N E G",
                "OU,O-O�U�OO�": "F D",
            },
            {
                "OU,O�O_OOc": "NEG_LAM",
                "OU,U,OU,O\"/OU,O�O�U�USO\"": "jussive",
                "OU,U?U^U+USU.OO�": "N E G",
                "OU,O-O�U�OO�": "F S",
            },
        ]
        df = pd.DataFrame(data)
        return reconstruct_from_base_df(df)

