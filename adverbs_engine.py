"""Time and place adverbs (ẓurūf) consumed by the sentence generator."""

from __future__ import annotations

import pandas as pd

from base_reconstruction_engine import BaseReconstructionEngine
from reconstruction_utils import reconstruct_from_base_df


class AdverbsEngine(BaseReconstructionEngine):
    SHEET_NAME = "OU,O�O�O�"

    _TOOLS = [
        "OU,USU^U.",  # today
        "O�UZU.U'O3U?",  # yesterday
        "U�U?U+UZO",  # here
        "U�U?U+UZOU�",  # there
        "OU,OO3O�U�U?",  # fallback generic
    ]

    @classmethod
    def make_df(cls) -> pd.DataFrame:
        rows = []
        for tool in cls._TOOLS:
            rows.append(
                {
                    "OU,O�O_OOc": tool,
                    "OU,U,OU,O\"/OU,O�O�U�USO\"": "adverb",
                    "OU,U?U^U+USU.OO�": "Z A R F",
                    "OU,O-O�U�OO�": "F F",
                }
            )
        df = pd.DataFrame(rows)
        return reconstruct_from_base_df(df)

