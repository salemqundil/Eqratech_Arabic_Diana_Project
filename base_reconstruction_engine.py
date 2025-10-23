"""Common base class for reconstruction engines.

The historical code base expected every ``*_engine.py`` module to expose a
class that inherits from ``BaseReconstructionEngine`` and implements a
``SHEET_NAME`` attribute together with a ``make_df`` classmethod returning a
``pandas.DataFrame``.  During the repository rollback that scaffold went
missing which makes every import in the engine modules fail.  This file
restores a lightweight implementation that the existing engines can share.

The base class focuses on two responsibilities:

* provide a stable interface (`make_df`) that child classes implement; and
* offer a couple of helper hooks (sheet-name normalisation and column
  validation) so consumers such as ``Main_engine.collect_engines`` can rely on
  consistent behaviour without each engine re‑implementing the utilities.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, Iterable, Sequence

import pandas as pd


class BaseReconstructionEngine(ABC):
    """Interface shared by all reconstruction engines."""

    #: Friendly name used when exporting to Excel; subclasses override it.
    SHEET_NAME: ClassVar[str] = "Reconstruction"

    #: Optional set of columns that should be present in the produced DataFrame.
    #: Engines can override this to ensure downstream tools always see the same
    #: schema even if a particular engine instance omits a column.
    REQUIRED_COLUMNS: ClassVar[Sequence[str]] = ()

    @classmethod
    @abstractmethod
    def make_df(cls) -> pd.DataFrame:
        """Return a DataFrame representing the engine output."""

    # ---- convenience helpers -------------------------------------------------
    @classmethod
    def sheet_name(cls) -> str:
        """Return a safe Excel sheet name (<= 31 chars, non-empty)."""
        name = str(getattr(cls, "SHEET_NAME", "") or cls.__name__).strip()
        return name[:31] if name else cls.__name__[:31]

    @classmethod
    def ensure_required_columns(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure every column declared in ``REQUIRED_COLUMNS`` exists.

        Missing columns are added with empty-string values so downstream Excel
        exports do not fail.  The function returns the same DataFrame instance
        for fluency with ``return cls.ensure_required_columns(df)`` patterns.
        """
        missing: Iterable[str] = (
            col for col in cls.REQUIRED_COLUMNS if col not in df.columns
        )
        for col in missing:
            df[col] = ""
        return df

