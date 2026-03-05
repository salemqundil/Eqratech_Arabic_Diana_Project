"""I3rab Corpus Loader - Load Quranic grammatical annotations.

Author: Hussein Hiyassat
Date: 2026-02-21
Sprint: 3 - Task 3.6
"""

import csv
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from ..corpus.corpus_format import GoldAnnotation, CorpusEntry


@dataclass
class I3rabParseResult:
    """Result of parsing an i3rab text."""
    case: Optional[str] = None
    pos: Optional[str] = None
    number: Optional[str] = None
    gender: Optional[str] = None
    raw_text: str = ""


class I3rabParser:
    """Parse Arabic grammatical annotations to extract features."""
    
    # Case markers
    CASE_PATTERNS = {
        'nominative': [
            r'مَرْفُوعٌ',
            r'رَفْعِهِ',
            r'الضَّمَّةُ',
        ],
        'accusative': [
            r'مَنْصُوبٌ',
            r'نَصْبِهِ',
            r'الْفَتْحَةُ',
        ],
        'genitive': [
            r'مَجْرُورٌ',
            r'جَرِّهِ',
            r'الْكَسْرَةُ',
        ],
    }
    
    # POS patterns
    POS_PATTERNS = {
        'noun': [
            r'اسْمٌ',
            r'مُبْتَدَأٌ',
            r'خَبَرٌ',
            r'فَاعِلٌ',
            r'مَفْعُولٌ',
            r'مُضَافٌ',
            r'نَعْتٌ',
        ],
        'verb': [
            r'فِعْلٌ',
            r'فِعْلُ',
        ],
        'particle': [
            r'حَرْفٌ',
            r'حَرْفُ',
        ],
    }
    
    # Number patterns
    NUMBER_PATTERNS = {
        'singular': [r'مُفْرَدٌ'],
        'dual': [r'مُثَنًّى', r'الْمُثَنَّى'],
        'plural': [r'جَمْعٌ', r'الْجَمْعِ'],
    }
    
    # Gender patterns
    GENDER_PATTERNS = {
        'masculine': [r'مُذَكَّرٌ'],
        'feminine': [r'مُؤَنَّثٌ'],
    }
    
    def parse(self, i3rab_text: str) -> I3rabParseResult:
        """Parse i3rab text to extract morphological features."""
        result = I3rabParseResult(raw_text=i3rab_text)
        
        result.case = self._extract_feature(i3rab_text, self.CASE_PATTERNS)
        result.pos = self._extract_feature(i3rab_text, self.POS_PATTERNS)
        result.number = self._extract_feature(i3rab_text, self.NUMBER_PATTERNS)
        result.gender = self._extract_feature(i3rab_text, self.GENDER_PATTERNS)
        
        return result
    
    def _extract_feature(self, text: str, patterns: Dict[str, List[str]]) -> Optional[str]:
        """Extract a feature using regex patterns."""
        for feature_value, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, text):
                    return feature_value
        return None


class I3rabLoader:
    """Load Quranic I3rab corpus from CSV."""
    
    def __init__(self, csv_path: Path):
        self.csv_path = Path(csv_path)
        self.parser = I3rabParser()
    
    def load(self) -> List[CorpusEntry]:
        """Load all entries from CSV."""
        entries = []
        
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            current_ayah_id = None
            current_annotations = []
            
            for row in reader:
                surah = row.get('﻿surah') or row.get('surah')
                ayah = row['ayah']
                word = row['word']
                i3rab = row['i3rab']
                
                ayah_id = f"quran:{surah}:{ayah}"
                
                # New ayah - save previous
                if current_ayah_id and ayah_id != current_ayah_id:
                    entries.append(CorpusEntry(
                        entry_id=current_ayah_id,
                        annotations=current_annotations
                    ))
                    current_annotations = []
                
                current_ayah_id = ayah_id
                
                # Parse i3rab
                parse_result = self.parser.parse(i3rab)
                
                # Create annotation
                annotation = GoldAnnotation(
                    word=word,
                    case=parse_result.case,
                    pos=parse_result.pos,
                    number=parse_result.number,
                    gender=parse_result.gender,
                )
                
                current_annotations.append(annotation)
            
            # Save last ayah
            if current_ayah_id and current_annotations:
                entries.append(CorpusEntry(
                    entry_id=current_ayah_id,
                    annotations=current_annotations
                ))
        
        return entries
    
    def load_surah(self, surah_num: int) -> List[CorpusEntry]:
        """Load a specific surah."""
        all_entries = self.load()
        return [e for e in all_entries if e.entry_id.startswith(f"quran:{surah_num}:")]
    
    def load_ayah(self, surah_num: int, ayah_num: int) -> Optional[CorpusEntry]:
        """Load a specific ayah."""
        ayah_id = f"quran:{surah_num}:{ayah_num}"
        all_entries = self.load()
        for entry in all_entries:
            if entry.entry_id == ayah_id:
                return entry
        return None
