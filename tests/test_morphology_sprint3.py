"""
Sprint 3 Morphology Integration Tests
"""
import pytest
from fvafk.c2b.word_boundary_detector import WordBoundaryDetectorPlanB
from fvafk.c2b.pattern_catalog import PatternCatalog
from fvafk.c2b.root_extractor import RootExtractor
from fvafk.c2b.pattern_matcher import PatternMatcher

class TestMorphologyPipeline:
    """End-to-end morphology tests"""
    
    def test_full_pipeline_kitab(self):
        """Test: الكتاب -> root + pattern + boundaries"""
        text = "الكتاب"
        
        # 1. Detect boundaries
        detector = WordBoundaryDetectorPlanB()
        boundaries = detector.detect_boundaries(text)
        assert len(boundaries) == 1
        assert boundaries[0].text == "الكتاب"
        
        # 2. Extract root
        extractor = RootExtractor()
        root = extractor.extract("كتاب")
        assert root is not None
        assert root.letters == ("ك", "ت", "ب")
        
        # 3. Match pattern (TODO: implement pattern matching)
        # catalog = PatternCatalog.load_full_catalog()
        # matcher = PatternMatcher(catalog)
        # pattern = matcher.match("كتاب", root)
        # assert pattern.name == "VERBAL_NOUN"
    
    def test_corpus_sentence_parsing(self):
        """Test parsing gold corpus sentence"""
        # Load from gold corpus
        # Parse with full pipeline
        # Compare against gold annotations
        pass
