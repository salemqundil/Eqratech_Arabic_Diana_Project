"""
Corpus Loader - Load gold-standard morphological annotations.

This module provides the CorpusLoader class for loading and parsing
morphological annotation files in various formats (TSV, CSV, JSON).

Author: Hussein Hiyassat
Date: 2026-02-19
Sprint: 3 - Task 3.4
"""

import csv
import json
from pathlib import Path
from typing import List, Optional, Iterator, Union
from .corpus_format import (
    GoldAnnotation,
    CorpusEntry,
    CorpusStatistics,
    CorpusFormat,
)


class CorpusLoader:
    """
    Load gold-standard morphological corpus files.
    
    Supports multiple formats:
    - TSV (Tab-Separated Values)
    - CSV (Comma-Separated Values)
    - JSON (JSON Lines or array format)
    
    Examples:
        >>> loader = CorpusLoader()
        >>> entries = loader.load_file("corpus.tsv")
        >>> len(entries)
        100
        >>> stats = loader.get_statistics()
        >>> stats.total_words
        500
    """
    
    # Required TSV/CSV columns
    REQUIRED_COLUMNS = {'word'}
    
    # Optional TSV/CSV columns
    OPTIONAL_COLUMNS = {
        'root', 'pattern', 'pos', 'case', 
        'number', 'gender', 'definiteness'
    }
    
    def __init__(self):
        """Initialize the loader."""
        self._entries: List[CorpusEntry] = []
        self._statistics: Optional[CorpusStatistics] = None
    
    def load_file(
        self, 
        filepath: Union[str, Path],
        format: Optional[CorpusFormat] = None,
        source_name: Optional[str] = None
    ) -> List[CorpusEntry]:
        """
        Load corpus from file.
        
        Args:
            filepath: Path to corpus file
            format: File format (auto-detected if None)
            source_name: Name for source tracking
            
        Returns:
            List of CorpusEntry objects
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If format is unsupported or file is invalid
            
        Examples:
            >>> loader = CorpusLoader()
            >>> entries = loader.load_file("data/corpus.tsv")
            >>> entries[0].annotations[0].word
            'الْكِتَابُ'
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"Corpus file not found: {filepath}")
        
        # Auto-detect format from extension
        if format is None:
            format = self._detect_format(filepath)
        
        # Use filename as source if not provided
        if source_name is None:
            source_name = filepath.stem
        
        # Load based on format
        if format == CorpusFormat.TSV:
            entries = self._load_tsv(filepath, source_name)
        elif format == CorpusFormat.CSV:
            entries = self._load_csv(filepath, source_name)
        elif format == CorpusFormat.JSON:
            entries = self._load_json(filepath, source_name)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        # Update internal state
        self._entries.extend(entries)
        self._statistics = None  # Invalidate cached statistics
        
        return entries
    
    def load_tsv_string(
        self,
        content: str,
        source_name: str = "string"
    ) -> List[CorpusEntry]:
        """
        Load corpus from TSV string content.
        
        Args:
            content: TSV string content
            source_name: Name for source tracking
            
        Returns:
            List of CorpusEntry objects
            
        Examples:
            >>> loader = CorpusLoader()
            >>> tsv = "word\\troot\\tpos\\nكِتَابٌ\\tك-ت-ب\\tnoun"
            >>> entries = loader.load_tsv_string(tsv)
            >>> entries[0].annotations[0].word
            'كِتَابٌ'
        """
        lines = content.strip().split('\n')
        entries = self._parse_tsv_lines(lines, source_name)
        # Update internal state
        self._entries.extend(entries)
        self._statistics = None
        return entries
    
    def get_statistics(self) -> CorpusStatistics:
        """
        Get corpus statistics.
        
        Returns:
            CorpusStatistics object
            
        Examples:
            >>> loader = CorpusLoader()
            >>> loader.load_file("corpus.tsv")
            >>> stats = loader.get_statistics()
            >>> stats.total_entries > 0
            True
        """
        if self._statistics is None:
            self._statistics = self._compute_statistics()
        return self._statistics
    
    def get_entries(self) -> List[CorpusEntry]:
        """
        Get all loaded entries.
        
        Returns:
            List of all CorpusEntry objects
        """
        return self._entries
    
    def clear(self):
        """Clear all loaded entries."""
        self._entries = []
        self._statistics = None
    
    def _detect_format(self, filepath: Path) -> CorpusFormat:
        """Detect file format from extension."""
        suffix = filepath.suffix.lower()
        
        if suffix == '.tsv':
            return CorpusFormat.TSV
        elif suffix == '.csv':
            return CorpusFormat.CSV
        elif suffix in {'.json', '.jsonl'}:
            return CorpusFormat.JSON
        else:
            raise ValueError(f"Cannot detect format from extension: {suffix}")
    
    def _load_tsv(self, filepath: Path, source_name: str) -> List[CorpusEntry]:
        """Load TSV file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return self._parse_tsv_lines(lines, source_name)
    
    def _load_csv(self, filepath: Path, source_name: str) -> List[CorpusEntry]:
        """Load CSV file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        return self._parse_csv_rows(rows, source_name)
    
    def _load_json(self, filepath: Path, source_name: str) -> List[CorpusEntry]:
        """Load JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError("JSON file must contain a list of entries")
        
        return self._parse_json_data(data, source_name)
    
    def _parse_tsv_lines(
        self, 
        lines: List[str], 
        source_name: str
    ) -> List[CorpusEntry]:
        """Parse TSV format lines."""
        if not lines:
            return []
        
        # Parse header
        header = lines[0].strip().split('\t')
        
        # Validate header
        if 'word' not in header:
            raise ValueError("TSV must have 'word' column")
        
        entries = []
        
        for line_num, line in enumerate(lines[1:], start=2):
            line = line.strip()
            if not line or line.startswith('#'):
                continue  # Skip empty lines and comments
            
            fields = line.split('\t')
            
            if len(fields) != len(header):
                raise ValueError(
                    f"Line {line_num}: Expected {len(header)} fields, "
                    f"got {len(fields)}"
                )
            
            # Build annotation dict
            data = dict(zip(header, fields))
            
            # Convert definiteness string to boolean
            if 'definiteness' in data:
                data['definiteness'] = self._parse_bool(data['definiteness'])
            
            # Create annotation
            annotation = GoldAnnotation(
                word=data['word'],
                root=data.get('root') or None,
                pattern=data.get('pattern') or None,
                pos=data.get('pos') or None,
                case=data.get('case') or None,
                number=data.get('number') or None,
                gender=data.get('gender') or None,
                definiteness=data.get('definiteness'),
                line_number=line_num,
            )
            
            # Create entry (one annotation per entry in TSV)
            entry = CorpusEntry(
                entry_id=f"{source_name}:{line_num}",
                annotations=[annotation],
                source=source_name,
            )
            
            entries.append(entry)
        
        return entries
    
    def _parse_csv_rows(
        self, 
        rows: List[dict], 
        source_name: str
    ) -> List[CorpusEntry]:
        """Parse CSV format rows (similar to TSV)."""
        entries = []
        
        for idx, row in enumerate(rows, start=2):
            if 'word' not in row:
                raise ValueError("CSV must have 'word' column")
            
            # Convert definiteness
            if 'definiteness' in row:
                row['definiteness'] = self._parse_bool(row['definiteness'])
            
            annotation = GoldAnnotation(
                word=row['word'],
                root=row.get('root') or None,
                pattern=row.get('pattern') or None,
                pos=row.get('pos') or None,
                case=row.get('case') or None,
                number=row.get('number') or None,
                gender=row.get('gender') or None,
                definiteness=row.get('definiteness'),
                line_number=idx,
            )
            
            entry = CorpusEntry(
                entry_id=f"{source_name}:{idx}",
                annotations=[annotation],
                source=source_name,
            )
            
            entries.append(entry)
        
        return entries
    
    def _parse_json_data(
        self, 
        data: List[dict], 
        source_name: str
    ) -> List[CorpusEntry]:
        """Parse JSON format data."""
        entries = []
        
        for idx, item in enumerate(data, start=1):
            # Handle both single annotation and entry formats
            if 'annotations' in item:
                # Entry format
                entry = CorpusEntry(
                    entry_id=item.get('entry_id', f"{source_name}:{idx}"),
                    annotations=[
                        GoldAnnotation.from_dict(a) 
                        for a in item['annotations']
                    ],
                    source=item.get('source', source_name),
                    metadata=item.get('metadata'),
                )
            else:
                # Single annotation format
                annotation = GoldAnnotation.from_dict(item)
                entry = CorpusEntry(
                    entry_id=f"{source_name}:{idx}",
                    annotations=[annotation],
                    source=source_name,
                )
            
            entries.append(entry)
        
        return entries
    
    def _compute_statistics(self) -> CorpusStatistics:
        """Compute statistics for loaded corpus."""
        stats = CorpusStatistics()
        
        stats.total_entries = len(self._entries)
        
        sources = set()
        
        for entry in self._entries:
            if entry.source:
                sources.add(entry.source)
            
            for annotation in entry.annotations:
                stats.total_words += 1
                
                if annotation.root:
                    stats.total_with_root += 1
                if annotation.pattern:
                    stats.total_with_pattern += 1
                if annotation.pos:
                    stats.total_with_pos += 1
        
        stats.sources = sorted(sources)
        
        return stats
    
    def _parse_bool(self, value: str) -> bool:
        """Parse boolean from string."""
        if isinstance(value, bool):
            return value
        
        value_lower = str(value).lower().strip()
        
        if value_lower in {'true', '1', 'yes', 't', 'y'}:
            return True
        elif value_lower in {'false', '0', 'no', 'f', 'n', ''}:
            return False
        else:
            raise ValueError(f"Cannot parse boolean from: {value}")


def load_corpus(filepath: Union[str, Path]) -> List[CorpusEntry]:
    """
    Convenience function to load corpus from file.
    
    Args:
        filepath: Path to corpus file
        
    Returns:
        List of CorpusEntry objects
        
    Examples:
        >>> entries = load_corpus("data/corpus.tsv")
        >>> len(entries) > 0
        True
    """
    loader = CorpusLoader()
    return loader.load_file(filepath)