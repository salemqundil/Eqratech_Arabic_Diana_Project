"""
Tests for I3rab Loader.

Author: Hussein Hiyassat
Date: 2026-02-21
Sprint: 3 - Task 3.6
"""

import pytest
import unicodedata
from pathlib import Path
from fvafk.c2b.evaluation import I3rabParser, I3rabParseResult, I3rabLoader
from fvafk.c2b.corpus import GoldAnnotation, CorpusEntry


def remove_diacritics(text: str) -> str:
    """Remove Arabic diacritics for comparison."""
    return ''.join(c for c in text if unicodedata.category(c) != 'Mn')


class TestI3rabParser:
    """Test I3rab text parser."""
    
    def test_parse_nominative_noun(self):
        """Test parsing nominative noun."""
        parser = I3rabParser()
        text = "مُبْتَدَأٌ مَرْفُوعٌ وَعَلَامَةُ رَفْعِهِ الضَّمَّةُ الظَّاهِرَةُ"
        
        result = parser.parse(text)
        
        assert result.case == "nominative"
        assert result.pos == "noun"
        assert result.raw_text == text
    
    def test_parse_genitive_noun(self):
        """Test parsing genitive noun."""
        parser = I3rabParser()
        text = "اسْمُ الْجَلَالَةِ مُضَافٌ إِلَيْهِ مَجْرُورٌ وَعَلَامَةُ جَرِّهِ الْكَسْرَةُ"
        
        result = parser.parse(text)
        
        assert result.case == "genitive"
        assert result.pos == "noun"
    
    def test_parse_accusative_noun(self):
        """Test parsing accusative noun."""
        parser = I3rabParser()
        text = "مَفْعُولٌ بِهِ مَنْصُوبٌ وَعَلَامَةُ نَصْبِهِ الْفَتْحَةُ"
        
        result = parser.parse(text)
        
        assert result.case == "accusative"
        assert result.pos == "noun"
    
    def test_parse_particle(self):
        """Test parsing particle."""
        parser = I3rabParser()
        text = "حَرْفُ جَرٍّ مَبْنِيٌّ عَلَى الْكَسْرِ"
        
        result = parser.parse(text)
        
        assert result.pos == "particle"
    
    def test_parse_verb(self):
        """Test parsing verb."""
        parser = I3rabParser()
        text = "فِعْلٌ مَاضٍ مَبْنِيٌّ عَلَى الْفَتْحِ"
        
        result = parser.parse(text)
        
        assert result.pos == "verb"
    
    def test_parse_no_match(self):
        """Test parsing with no matches."""
        parser = I3rabParser()
        text = "some random text"
        
        result = parser.parse(text)
        
        assert result.case is None
        assert result.pos is None
        assert result.number is None
        assert result.gender is None


class TestI3rabLoader:
    """Test I3rab corpus loader."""
    
    @pytest.fixture
    def csv_path(self):
        """Path to the I3rab CSV file."""
        return Path("data/i3rab/quran_i3rab.csv")
    
    def test_loader_initialization(self, csv_path):
        """Test loader initialization."""
        if not csv_path.exists():
            pytest.skip("I3rab CSV not found")
        
        loader = I3rabLoader(csv_path)
        assert loader.csv_path == csv_path
        assert isinstance(loader.parser, I3rabParser)
    
    def test_load_ayah_1_1(self, csv_path):
        """Test loading Al-Fatiha 1:1 (Bismillah)."""
        if not csv_path.exists():
            pytest.skip("I3rab CSV not found")
        
        loader = I3rabLoader(csv_path)
        entry = loader.load_ayah(1, 1)
        
        assert entry is not None
        assert entry.entry_id == "quran:1:1"
        assert len(entry.annotations) == 4
        
        # First word: بِسْمِ (genitive noun)
        word1_base = remove_diacritics(entry.annotations[0].word)
        assert word1_base == "بسم"
        assert entry.annotations[0].case == "genitive"
        assert entry.annotations[0].pos == "noun"
        
        # Second word: اللَّهِ (genitive noun)
        word2_base = remove_diacritics(entry.annotations[1].word)
        assert word2_base == "الله"
        assert entry.annotations[1].case == "genitive"
        assert entry.annotations[1].pos == "noun"
    
    def test_load_ayah_1_2(self, csv_path):
        """Test loading Al-Fatiha 1:2 (Alhamdulillah)."""
        if not csv_path.exists():
            pytest.skip("I3rab CSV not found")
        
        loader = I3rabLoader(csv_path)
        entry = loader.load_ayah(1, 2)
        
        assert entry is not None
        assert entry.entry_id == "quran:1:2"
        
        # First word: الْحَمْدُ (nominative)
        word1_base = remove_diacritics(entry.annotations[0].word)
        assert word1_base == "الحمد"
        assert entry.annotations[0].case == "nominative"
        assert entry.annotations[0].pos == "noun"
    
    def test_load_surah_1(self, csv_path):
        """Test loading entire Al-Fatiha."""
        if not csv_path.exists():
            pytest.skip("I3rab CSV not found")
        
        loader = I3rabLoader(csv_path)
        entries = loader.load_surah(1)
        
        assert len(entries) == 7  # Al-Fatiha has 7 ayahs
        assert all(e.entry_id.startswith("quran:1:") for e in entries)
    
    def test_load_nonexistent_ayah(self, csv_path):
        """Test loading non-existent ayah."""
        if not csv_path.exists():
            pytest.skip("I3rab CSV not found")
        
        loader = I3rabLoader(csv_path)
        entry = loader.load_ayah(999, 999)
        
        assert entry is None
    
    def test_annotations_are_gold_annotations(self, csv_path):
        """Test that annotations are GoldAnnotation instances."""
        if not csv_path.exists():
            pytest.skip("I3rab CSV not found")
        
        loader = I3rabLoader(csv_path)
        entry = loader.load_ayah(1, 1)
        
        assert all(isinstance(ann, GoldAnnotation) for ann in entry.annotations)
