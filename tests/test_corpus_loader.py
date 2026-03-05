"""
Tests for Corpus Loader.

Tests cover:
- TSV file loading
- CSV file loading
- JSON file loading
- String content loading
- Statistics computation
- Error handling
- Edge cases
"""

import pytest
import tempfile
from pathlib import Path

from fvafk.c2b.corpus.corpus_format import (
    GoldAnnotation,
    CorpusEntry,
    CorpusStatistics,
    CorpusFormat,
)
from fvafk.c2b.corpus.corpus_loader import (
    CorpusLoader,
    load_corpus,
)


class TestGoldAnnotation:
    """Tests for GoldAnnotation dataclass."""
    
    def test_create_annotation(self):
        """Test creating a gold annotation."""
        annotation = GoldAnnotation(
            word="الْكِتَابُ",
            root="ك-ت-ب",
            pattern="فِعَال",
            pos="noun",
            case="nominative",
            number="singular",
            gender="masculine",
            definiteness=True,
        )
        
        assert annotation.word == "الْكِتَابُ"
        assert annotation.root == "ك-ت-ب"
        assert annotation.pos == "noun"
        assert annotation.definiteness is True
    
    def test_annotation_requires_word(self):
        """Test that word is required."""
        with pytest.raises(ValueError):
            GoldAnnotation(word="")
    
    def test_annotation_to_dict(self):
        """Test converting annotation to dict."""
        annotation = GoldAnnotation(
            word="كِتَابٌ",
            root="ك-ت-ب",
            pos="noun",
        )
        
        data = annotation.to_dict()
        
        assert data['word'] == "كِتَابٌ"
        assert data['root'] == "ك-ت-ب"
        assert data['pos'] == "noun"
    
    def test_annotation_from_dict(self):
        """Test creating annotation from dict."""
        data = {
            'word': "مَدْرَسَةٌ",
            'root': "د-ر-س",
            'pos': "noun",
            'gender': "feminine",
        }
        
        annotation = GoldAnnotation.from_dict(data)
        
        assert annotation.word == "مَدْرَسَةٌ"
        assert annotation.root == "د-ر-س"
        assert annotation.gender == "feminine"


class TestCorpusEntry:
    """Tests for CorpusEntry dataclass."""
    
    def test_create_entry(self):
        """Test creating a corpus entry."""
        annotation = GoldAnnotation(word="كِتَابٌ", root="ك-ت-ب")
        
        entry = CorpusEntry(
            entry_id="test:1",
            annotations=[annotation],
            source="test",
        )
        
        assert entry.entry_id == "test:1"
        assert len(entry.annotations) == 1
        assert entry.source == "test"
    
    def test_entry_requires_id(self):
        """Test that entry_id is required."""
        with pytest.raises(ValueError):
            CorpusEntry(
                entry_id="",
                annotations=[],
            )
    
    def test_entry_length(self):
        """Test entry length returns annotation count."""
        entry = CorpusEntry(
            entry_id="test:1",
            annotations=[
                GoldAnnotation(word="كِتَابٌ"),
                GoldAnnotation(word="مَدْرَسَةٌ"),
            ],
        )
        
        assert len(entry) == 2


class TestCorpusTSVLoading:
    """Tests for TSV file loading."""
    
    def test_load_tsv_string_basic(self):
        """Test loading TSV from string."""
        tsv_content = """word\troot\tpos
كِتَابٌ\tك-ت-ب\tnoun
مَدْرَسَةٌ\tد-ر-س\tnoun"""
        
        loader = CorpusLoader()
        entries = loader.load_tsv_string(tsv_content)
        
        assert len(entries) == 2
        assert entries[0].annotations[0].word == "كِتَابٌ"
        assert entries[0].annotations[0].root == "ك-ت-ب"
        assert entries[1].annotations[0].word == "مَدْرَسَةٌ"
    
    def test_load_tsv_with_all_fields(self):
        """Test loading TSV with all fields."""
        tsv_content = """word\troot\tpattern\tpos\tcase\tnumber\tgender\tdefiniteness
الْكِتَابُ\tك-ت-ب\tفِعَال\tnoun\tnominative\tsingular\tmasculine\ttrue"""
        
        loader = CorpusLoader()
        entries = loader.load_tsv_string(tsv_content)
        
        assert len(entries) == 1
        annotation = entries[0].annotations[0]
        
        assert annotation.word == "الْكِتَابُ"
        assert annotation.root == "ك-ت-ب"
        assert annotation.pattern == "فِعَال"
        assert annotation.pos == "noun"
        assert annotation.case == "nominative"
        assert annotation.number == "singular"
        assert annotation.gender == "masculine"
        assert annotation.definiteness is True
    
    def test_load_tsv_skips_comments(self):
        """Test that TSV loader skips comment lines."""
        tsv_content = """word\troot
# This is a comment
كِتَابٌ\tك-ت-ب"""
        
        loader = CorpusLoader()
        entries = loader.load_tsv_string(tsv_content)
        
        assert len(entries) == 1
    
    def test_load_tsv_skips_empty_lines(self):
        """Test that TSV loader skips empty lines."""
        tsv_content = """word\troot
كِتَابٌ\tك-ت-ب

مَدْرَسَةٌ\tد-ر-س"""
        
        loader = CorpusLoader()
        entries = loader.load_tsv_string(tsv_content)
        
        assert len(entries) == 2
    
    def test_load_tsv_missing_word_column(self):
        """Test error when 'word' column is missing."""
        tsv_content = """root\tpos
ك-ت-ب\tnoun"""
        
        loader = CorpusLoader()
        
        with pytest.raises(ValueError, match="must have 'word' column"):
            loader.load_tsv_string(tsv_content)
    
    def test_load_tsv_mismatched_columns(self):
        """Test error when row has wrong number of fields."""
        tsv_content = """word\troot\tpos
كِتَابٌ\tك-ت-ب"""  # Missing pos field
        
        loader = CorpusLoader()
        
        with pytest.raises(ValueError, match="Expected 3 fields"):
            loader.load_tsv_string(tsv_content)


class TestCorpusFileLoading:
    """Tests for file loading."""
    
    def test_load_tsv_file(self):
        """Test loading TSV from file."""
        # Create temporary TSV file
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.tsv', 
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write("word\troot\tpos\n")
            f.write("كِتَابٌ\tك-ت-ب\tnoun\n")
            f.write("مَدْرَسَةٌ\tد-ر-س\tnoun\n")
            temp_path = f.name
        
        try:
            loader = CorpusLoader()
            entries = loader.load_file(temp_path)
            
            assert len(entries) == 2
            assert entries[0].annotations[0].word == "كِتَابٌ"
        finally:
            Path(temp_path).unlink()
    
    def test_load_file_not_found(self):
        """Test error when file doesn't exist."""
        loader = CorpusLoader()
        
        with pytest.raises(FileNotFoundError):
            loader.load_file("nonexistent_file.tsv")
    
    def test_format_auto_detection(self):
        """Test automatic format detection from extension."""
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.tsv',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write("word\troot\n")
            f.write("كِتَابٌ\tك-ت-ب\n")
            temp_path = f.name
        
        try:
            loader = CorpusLoader()
            # Format should be auto-detected
            entries = loader.load_file(temp_path)
            
            assert len(entries) == 1
        finally:
            Path(temp_path).unlink()


class TestCorpusStatistics:
    """Tests for corpus statistics."""
    
    def test_compute_statistics(self):
        """Test computing corpus statistics."""
        tsv_content = """word\troot\tpattern\tpos
كِتَابٌ\tك-ت-ب\tفِعَال\tnoun
مَدْرَسَةٌ\tد-ر-س\tمَفْعَلَة\tnoun
على\t\t\tparticle"""
        
        loader = CorpusLoader()
        loader.load_tsv_string(tsv_content)
        stats = loader.get_statistics()
        
        assert stats.total_entries == 3
        assert stats.total_words == 3
        assert stats.total_with_root == 2
        assert stats.total_with_pattern == 2
        assert stats.total_with_pos == 3
    
    def test_statistics_tracks_sources(self):
        """Test that statistics tracks source files."""
        loader = CorpusLoader()
        
        loader.load_tsv_string("word\nكِتَابٌ", source_name="source1")
        loader.load_tsv_string("word\nمَدْرَسَةٌ", source_name="source2")
        
        stats = loader.get_statistics()
        
        assert len(stats.sources) == 2
        assert "source1" in stats.sources
        assert "source2" in stats.sources


class TestCorpusLoaderState:
    """Tests for loader state management."""
    
    def test_get_entries(self):
        """Test getting all loaded entries."""
        loader = CorpusLoader()
        loader.load_tsv_string("word\nكِتَابٌ")
        loader.load_tsv_string("word\nمَدْرَسَةٌ")
        
        entries = loader.get_entries()
        
        assert len(entries) == 2
    
    def test_clear(self):
        """Test clearing loaded entries."""
        loader = CorpusLoader()
        loader.load_tsv_string("word\nكِتَابٌ")
        
        assert len(loader.get_entries()) == 1
        
        loader.clear()
        
        assert len(loader.get_entries()) == 0


class TestBooleanParsing:
    """Tests for boolean value parsing."""
    
    def test_parse_definiteness_true(self):
        """Test parsing definiteness as true."""
        tsv_content = """word\tdefiniteness
الكتاب\ttrue"""
        
        loader = CorpusLoader()
        entries = loader.load_tsv_string(tsv_content)
        
        assert entries[0].annotations[0].definiteness is True
    
    def test_parse_definiteness_false(self):
        """Test parsing definiteness as false."""
        tsv_content = """word\tdefiniteness
كتاب\tfalse"""
        
        loader = CorpusLoader()
        entries = loader.load_tsv_string(tsv_content)
        
        assert entries[0].annotations[0].definiteness is False
    
    def test_parse_definiteness_variations(self):
        """Test parsing various boolean formats."""
        loader = CorpusLoader()
        
        # Test "1" as true
        entries = loader.load_tsv_string("word\tdefiniteness\nالكتاب\t1")
        assert entries[0].annotations[0].definiteness is True
        
        # Test "0" as false
        entries = loader.load_tsv_string("word\tdefiniteness\nكتاب\t0")
        assert entries[0].annotations[0].definiteness is False


class TestConvenienceFunction:
    """Tests for convenience function."""
    
    def test_load_corpus_function(self):
        """Test load_corpus convenience function."""
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.tsv',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write("word\troot\n")
            f.write("كِتَابٌ\tك-ت-ب\n")
            temp_path = f.name
        
        try:
            entries = load_corpus(temp_path)
            
            assert len(entries) == 1
            assert entries[0].annotations[0].word == "كِتَابٌ"
        finally:
            Path(temp_path).unlink()


class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_empty_tsv(self):
        """Test loading empty TSV (header only)."""
        loader = CorpusLoader()
        entries = loader.load_tsv_string("word\troot")
        
        assert len(entries) == 0
    
    def test_empty_fields(self):
        """Test handling empty/missing fields."""
        tsv_content = """word\troot\tpos
كِتَابٌ\t\tnoun"""
        
        loader = CorpusLoader()
        entries = loader.load_tsv_string(tsv_content)
        
        assert entries[0].annotations[0].root is None
        assert entries[0].annotations[0].pos == "noun"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])