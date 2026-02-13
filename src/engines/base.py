"""
Base Engine Infrastructure
===========================
Foundation classes for all Arabic grammar engines following computational linguistics theory.

Architecture Layers (bottom-up):
1. Phonology: Sound units, phonemes, prosody
2. Morphology: Word structure, inflection, derivation
3. Lexicon: Vocabulary, semantic classes
4. Syntax: Sentence structure, grammatical relations
5. Rhetoric: Figurative language, discourse patterns
6. Generation: Sentence construction from components
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import pandas as pd
from enum import Enum


class EngineLayer(Enum):
    """Linguistic processing layers in hierarchical order"""
    PHONOLOGY = 1      # الصوتيات: phonemes, harakat, sounds
    MORPHOLOGY = 2     # الصرف: word forms, patterns, inflections
    LEXICON = 3        # المعجم: vocabulary, proper nouns, semantic classes
    SYNTAX = 4         # النحو: grammatical relations, sentence structure
    RHETORIC = 5       # البلاغة: figurative language, discourse
    GENERATION = 6     # التوليد: sentence production


class BaseReconstructionEngine(ABC):
    """
    Abstract base class for all grammar engines.
    
    Every engine must:
    1. Define a unique SHEET_NAME (for Excel export)
    2. Specify its EngineLayer
    3. Implement make_df() returning pandas DataFrame
    4. Use Arabic column names (e.g., 'الأداة', 'الفونيمات', 'الحركات')
    
    Optional hierarchical metadata:
    - GROUP: Functional group (e.g., "2.1" for Verbal Morphology)
    - SUBGROUP: Semantic subgroup (e.g., "2.1.1" for Basic Verb Forms)
    - GROUP_AR: Arabic group name (e.g., "الأفعال")
    - SUBGROUP_AR: Arabic subgroup name (e.g., "الأفعال الأساسية")
    
    The DataFrame will be post-processed by reconstruction_utils.reconstruct_from_base_df()
    to fill Unicode, UTF-8, and derive missing phonological data.
    """
    
    SHEET_NAME: str = "UnnamedEngine"
    LAYER: EngineLayer = EngineLayer.LEXICON
    GROUP: Optional[str] = None
    SUBGROUP: Optional[str] = None
    GROUP_AR: Optional[str] = None
    SUBGROUP_AR: Optional[str] = None
    
    @classmethod
    @abstractmethod
    def make_df(cls) -> pd.DataFrame:
        """
        Generate the engine's DataFrame.
        
        Returns:
            pd.DataFrame with at minimum these columns:
                - 'الأداة': The linguistic tool/item (word, phrase, particle)
                - Additional domain-specific columns
                
        The DataFrame will be normalized by reconstruction_utils automatically.
        """
        pass
    
    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """Return engine metadata for cataloging and ordering"""
        metadata = {
            'name': cls.__name__,
            'sheet_name': cls.SHEET_NAME,
            'layer': cls.LAYER.name,
            'layer_order': cls.LAYER.value,
            'module': cls.__module__
        }
        
        # Add hierarchical classification if available
        if cls.GROUP:
            metadata['group'] = cls.GROUP
            metadata['group_ar'] = cls.GROUP_AR or ''
        if cls.SUBGROUP:
            metadata['subgroup'] = cls.SUBGROUP
            metadata['subgroup_ar'] = cls.SUBGROUP_AR or ''
            
        return metadata
    
    @classmethod
    def get_hierarchy(cls) -> str:
        """
        Return full hierarchical path.
        
        Returns:
            String like "Layer 2 → Group 2.1 → Subgroup 2.1.1"
        """
        parts = [f"Layer {cls.LAYER.value} ({cls.LAYER.name})"]
        if cls.GROUP:
            group_label = f"Group {cls.GROUP}"
            if cls.GROUP_AR:
                group_label += f" ({cls.GROUP_AR})"
            parts.append(group_label)
        if cls.SUBGROUP:
            subgroup_label = f"Subgroup {cls.SUBGROUP}"
            if cls.SUBGROUP_AR:
                subgroup_label += f" ({cls.SUBGROUP_AR})"
            parts.append(subgroup_label)
        return " → ".join(parts)
    
    @classmethod
    def validate_df(cls, df: pd.DataFrame) -> tuple[bool, List[str]]:
        """
        Validate DataFrame structure.
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        if df.empty:
            errors.append("DataFrame is empty")
        
        if 'الأداة' not in df.columns:
            errors.append("Required column 'الأداة' is missing")
        
        # Check for duplicate sheet names across engines
        if len(cls.SHEET_NAME) > 31:
            errors.append(f"SHEET_NAME too long (Excel limit 31 chars): {cls.SHEET_NAME}")
        
        return (len(errors) == 0, errors)


class PhonologyEngine(BaseReconstructionEngine):
    """Base class for phonological engines (sounds, phonemes, prosody)"""
    LAYER = EngineLayer.PHONOLOGY


class MorphologyEngine(BaseReconstructionEngine):
    """Base class for morphological engines (word forms, patterns)"""
    LAYER = EngineLayer.MORPHOLOGY


class LexiconEngine(BaseReconstructionEngine):
    """Base class for lexical engines (vocabulary, proper nouns)"""
    LAYER = EngineLayer.LEXICON


class SyntaxEngine(BaseReconstructionEngine):
    """Base class for syntactic engines (grammatical relations)"""
    LAYER = EngineLayer.SYNTAX


class RhetoricEngine(BaseReconstructionEngine):
    """Base class for rhetorical engines (figurative language)"""
    LAYER = EngineLayer.RHETORIC


class GenerationEngine(BaseReconstructionEngine):
    """Base class for sentence generation engines"""
    LAYER = EngineLayer.GENERATION
