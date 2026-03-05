"""
Base class for all reconstruction engines.

All engine classes should inherit from this base class and implement:
- SHEET_NAME: class attribute defining the Excel sheet name
- make_df(): class method that returns a pandas DataFrame
"""

import pandas as pd
from abc import ABC, abstractmethod


class BaseReconstructionEngine(ABC):
    """Base class for reconstruction engines that generate grammar data."""
    
    SHEET_NAME = 'Base'  # Override in subclasses
    
    @classmethod
    @abstractmethod
    def make_df(cls) -> pd.DataFrame:
        """Generate and return a DataFrame for this engine.
        
        Returns:
            pd.DataFrame: DataFrame containing the grammar data for this engine
        """
        pass
