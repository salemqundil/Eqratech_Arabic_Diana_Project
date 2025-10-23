"""Preposition (ḥurūf al-jarr) engine providing a few canonical patterns."""

from __future__ import annotations

import pandas as pd

from base_reconstruction_engine import BaseReconstructionEngine
from reconstruction_utils import reconstruct_from_base_df


class JarEngine(BaseReconstructionEngine):
    SHEET_NAME = "OO3O�O1"

    _ROWS = [
        ("PREP_FI", "O,O�U?USOc"),
        ("PREP_MIN", "OO\"O�O_OO� OU,O�OUSOc"),
        ("PREP_ILA", "OU+O�U�OO� OU,O�OUSOc"),
        ("PREP_THUMMA", "OO3O�O1U,OO�"),
        ("PREP_HATTA", "OO3O�O1OU+Oc/O3O\"O\"USOc"),
        ("PREP_LAM", "U.O�OU^O�Oc"),
    ]

    @classmethod
    def make_df(cls) -> pd.DataFrame:
        base_rows = []
        for tool, pattern in cls._ROWS:
            base_rows.append(
                {
                    "OU,O�O_OOc": tool,
                    "OU,U,OU,O\"/OU,O�O�U�USO\"": pattern,
                    "OU,U?U^U+USU.OO�": "P R E P",
                    "OU,O-O�U�OO�": "F F",
                }
            )
        df = pd.DataFrame(base_rows)
        return reconstruct_from_base_df(df)

