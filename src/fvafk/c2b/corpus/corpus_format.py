"""
Corpus Format Definitions - Data structures for gold-standard annotations.

This module provides data structures for representing morphological
annotations in the gold corpus.

Author: Hussein Hiyassat
Date: 2026-02-19
Sprint: 3 - Task 3.4
"""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class CorpusFormat(str, Enum):
    """Supported corpus file formats."""
    TSV = "tsv"
    CSV = "csv"
    JSON = "json"


@dataclass
class GoldAnnotation:
    """
    Represents a gold-standard morphological annotation.
    
    This is the ground truth annotation for a single word,
    used to evaluate system performance.
    
    Attributes:
        word: Surface form of the word
        root: Root letters (e.g., "ك-ت-ب")
        pattern: Morphological pattern (e.g., "فِعَال")
        pos: Part of speech (noun, verb, particle, etc.)
        case: Grammatical case (nominative, accusative, genitive)
        number: Grammatical number (singular, dual, plural)
        gender: Grammatical gender (masculine, feminine)
        definiteness: Whether word is definite
        metadata: Additional annotations
        line_number: Source line number (for error reporting)
    
    Examples:
        >>> annotation = GoldAnnotation(
        ...     word="الْكِتَابُ",
        ...     root="ك-ت-ب",
        ...     pattern="فِعَال",
        ...     pos="noun",
        ...     case="nominative",
        ...     number="singular",
        ...     gender="masculine",
        ...     definiteness=True
        ... )
        >>> annotation.root
        'ك-ت-ب'
    """
    
    word: str
    root: Optional[str] = None
    pattern: Optional[str] = None
    pos: Optional[str] = None
    case: Optional[str] = None
    number: Optional[str] = None
    gender: Optional[str] = None
    definiteness: Optional[bool] = None
    metadata: Optional[dict] = None
    line_number: Optional[int] = None
    
    def __post_init__(self):
        """Validate annotation."""
        if not self.word or not self.word.strip():
            raise ValueError("word cannot be empty")
    
    def to_dict(self) -> dict:
        """
        Convert annotation to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'word': self.word,
            'root': self.root,
            'pattern': self.pattern,
            'pos': self.pos,
            'case': self.case,
            'number': self.number,
            'gender': self.gender,
            'definiteness': self.definiteness,
            'metadata': self.metadata,
            'line_number': self.line_number,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GoldAnnotation':
        """
        Create annotation from dictionary.
        
        Args:
            data: Dictionary with annotation fields
            
        Returns:
            GoldAnnotation instance
        """
        return cls(
            word=data['word'],
            root=data.get('root'),
            pattern=data.get('pattern'),
            pos=data.get('pos'),
            case=data.get('case'),
            number=data.get('number'),
            gender=data.get('gender'),
            definiteness=data.get('definiteness'),
            metadata=data.get('metadata'),
            line_number=data.get('line_number'),
        )


@dataclass
class CorpusEntry:
    """
    Represents a single corpus entry (may contain multiple words).
    
    Attributes:
        entry_id: Unique entry identifier
        annotations: List of word annotations
        source: Source file or corpus name
        metadata: Entry-level metadata (e.g., sentence info)
    
    Examples:
        >>> entry = CorpusEntry(
        ...     entry_id="quran:1:1:1",
        ...     annotations=[
        ...         GoldAnnotation(word="بِسْمِ", root="س-م-و", pos="noun")
        ...     ],
        ...     source="quran"
        ... )
        >>> len(entry.annotations)
        1
    """
    
    entry_id: str
    annotations: List[GoldAnnotation]
    source: Optional[str] = None
    metadata: Optional[dict] = None
    
    def __post_init__(self):
        """Validate entry."""
        if not self.entry_id:
            raise ValueError("entry_id cannot be empty")
        if not isinstance(self.annotations, list):
            raise ValueError("annotations must be a list")
    
    def __len__(self) -> int:
        """Return number of annotations."""
        return len(self.annotations)
    
    def to_dict(self) -> dict:
        """
        Convert entry to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'entry_id': self.entry_id,
            'annotations': [a.to_dict() for a in self.annotations],
            'source': self.source,
            'metadata': self.metadata,
        }


@dataclass
class CorpusStatistics:
    """
    Statistics about a loaded corpus.
    
    Attributes:
        total_entries: Total number of entries
        total_words: Total number of word annotations
        total_with_root: Number of words with root annotation
        total_with_pattern: Number of words with pattern annotation
        total_with_pos: Number of words with POS annotation
        sources: List of source files/corpora
    """
    
    total_entries: int = 0
    total_words: int = 0
    total_with_root: int = 0
    total_with_pattern: int = 0
    total_with_pos: int = 0
    sources: List[str] = None
    
    def __post_init__(self):
        """Initialize sources list."""
        if self.sources is None:
            self.sources = []
    
    def to_dict(self) -> dict:
        """Convert statistics to dictionary."""
        return {
            'total_entries': self.total_entries,
            'total_words': self.total_words,
            'total_with_root': self.total_with_root,
            'total_with_pattern': self.total_with_pattern,
            'total_with_pos': self.total_with_pos,
            'sources': self.sources,
        }