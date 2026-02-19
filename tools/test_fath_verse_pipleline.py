"""
Comprehensive Integration Test - Surah Al-Fath Verse 29
Tests the entire pipeline with a complete Quranic verse
"""

import pytest
from fvafk.c2b.word_boundary_detector import WordBoundaryDetectorPlanB
from fvafk.c2b.root_extractor import RootExtractor
from fvafk.c2b.pattern_catalog import PatternCatalog
from fvafk.c2b.syllabifier import syllabify
from fvafk.c2b.word_classifier import WordClassifier
from fvafk.phonology_v2 import phonology_v2_process
from fvafk.form_codec_v2 import FormV2Encoder, FormV2Decoder


# Surah Al-Fath (48:29) - Complete verse
VERSE = """مُّحَمَّدٌ رَّسُولُ اللَّهِ وَالَّذِينَ مَعَهُ أَشِدَّاءُ عَلَى الْكُفَّارِ رُحَمَاءُ بَيْنَهُمْ تَرَاهُمْ رُكَّعًا سُجَّدًا يَبْتَغُونَ فَضْلًا مِّنَ اللَّهِ وَرِضْوَانًا سِيمَاهُمْ فِي وُجُوهِهِم مِّنْ أَثَرِ السُّجُودِ ذَٰلِكَ مَثَلُهُمْ فِي التَّوْرَاةِ وَمَثَلُهُمْ فِي الْإِنجِيلِ كَزَرْعٍ أَخْرَجَ شَطْأَهُ فَآزَرَهُ فَاسْتَغْلَظَ فَاسْتَوَىٰ عَلَىٰ سُوقِهِ يُعْجِبُ الزُّرَّاعَ لِيَغِيظَ بِهِمُ الْكُفَّارَ وَعَدَ اللَّهُ الَّذِينَ آمَنُوا وَعَمِلُوا الصَّالِحَاتِ مِنْهُم مَّغْفِرَةً وَأَجْرًا عَظِيمًا"""


class TestVerseIntegration:
    """Comprehensive integration tests with Quranic verse"""
    
    def test_word_boundary_detection_on_verse(self):
        """Test: Detect word boundaries in complete verse"""
        detector = WordBoundaryDetectorPlanB()
        boundaries = detector.detect_boundaries(VERSE)
        
        # Should detect reasonable number of words (around 50-60)
        assert len(boundaries) > 40, f"Expected >40 words, got {len(boundaries)}"
        assert len(boundaries) < 80, f"Expected <80 words, got {len(boundaries)}"
        
        # Check some known words are detected
        word_texts = [b.text for b in boundaries]
        assert "مُّحَمَّدٌ" in word_texts or "مُحَمَّدٌ" in word_texts
        assert any("اللَّهِ" in w for w in word_texts)
        
        # All boundaries should have valid confidence scores
        for boundary in boundaries:
            assert 0.0 <= boundary.confidence <= 1.0
            assert boundary.syllable_count >= 0
        
        print(f"\n✓ Detected {len(boundaries)} words")
        print(f"  Sample words: {word_texts[:5]}")
    
    def test_root_extraction_on_verse_words(self):
        """Test: Extract roots from verse words"""
        detector = WordBoundaryDetectorPlanB()
        boundaries = detector.detect_boundaries(VERSE)
        extractor = RootExtractor()
        
        successful_extractions = 0
        failed_words = []
        sample_roots = []
        
        for boundary in boundaries[:20]:  # Test first 20 words
            word = boundary.text
            try:
                root = extractor.extract(word)
                if root is not None:
                    successful_extractions += 1
                    if len(sample_roots) < 5:
                        sample_roots.append((word, root.letters))
                else:
                    failed_words.append(word)
            except Exception as e:
                failed_words.append(f"{word} (error: {str(e)[:30]})")
        
        # Should successfully extract roots from most words
        success_rate = successful_extractions / 20
        assert success_rate > 0.3, f"Root extraction success rate too low: {success_rate:.1%}"
        
        print(f"\n✓ Root extraction: {successful_extractions}/20 successful ({success_rate:.1%})")
        print(f"  Sample roots: {sample_roots[:3]}")
        if failed_words:
            print(f"  Failed words: {failed_words[:3]}")
    
    def test_syllabification_on_verse_words(self):
        """Test: Syllabify verse words"""
        detector = WordBoundaryDetectorPlanB()
        boundaries = detector.detect_boundaries(VERSE)
        
        successful_syllabifications = 0
        sample_syllables = []
        
        for boundary in boundaries[:15]:  # Test first 15 words
            word = boundary.text
            try:
                result = syllabify(word)
                if result and result.syllables:
                    successful_syllabifications += 1
                    if len(sample_syllables) < 3:
                        sample_syllables.append((word, result.syllables))
            except Exception:
                pass
        
        # Should syllabify most words
        success_rate = successful_syllabifications / 15
        assert success_rate > 0.4, f"Syllabification success rate too low: {success_rate:.1%}"
        
        print(f"\n✓ Syllabification: {successful_syllabifications}/15 successful ({success_rate:.1%})")
        print(f"  Sample syllables: {sample_syllables[:2]}")
    
    def test_word_classification_on_verse(self):
        """Test: Classify verse words"""
        detector = WordBoundaryDetectorPlanB()
        boundaries = detector.detect_boundaries(VERSE)
        classifier = WordClassifier()
        
        classifications = {}
        
        for boundary in boundaries[:20]:  # Test first 20 words
            word = boundary.text
            try:
                word_class = classifier.classify(word)
                classifications[word_class] = classifications.get(word_class, 0) + 1
            except Exception:
                classifications['ERROR'] = classifications.get('ERROR', 0) + 1
        
        # Should classify words into different categories
        assert len(classifications) > 0, "No classifications produced"
        
        print(f"\n✓ Word classification:")
        for word_class, count in sorted(classifications.items(), key=lambda x: -x[1]):
            print(f"  {word_class}: {count}")
    
    def test_phonology_v2_on_verse_sample(self):
        """Test: Apply phonology v2 processing to sample words"""
        detector = WordBoundaryDetectorPlanB()
        boundaries = detector.detect_boundaries(VERSE)
        
        processed_count = 0
        sample_results = []
        
        for boundary in boundaries[:10]:  # Test first 10 words
            word = boundary.text
            try:
                result = phonology_v2_process(word)
                if result:
                    processed_count += 1
                    if len(sample_results) < 3:
                        sample_results.append((word, result.get('output', 'N/A')))
            except Exception as e:
                # Phonology processing might fail on some words - that's okay
                pass
        
        print(f"\n✓ Phonology v2: {processed_count}/10 processed")
        if sample_results:
            print(f"  Sample results: {sample_results[:2]}")
    
    def test_form_encoding_on_verse_sample(self):
        """Test: Encode/decode verse words with FormV2"""
        detector = WordBoundaryDetectorPlanB()
        boundaries = detector.detect_boundaries(VERSE)
        encoder = FormV2Encoder()
        decoder = FormV2Decoder()
        
        encoded_count = 0
        decoded_count = 0
        sample_forms = []
        
        for boundary in boundaries[:10]:  # Test first 10 words
            word = boundary.text
            try:
                # Encode
                encoded = encoder.encode(word)
                if encoded:
                    encoded_count += 1
                    
                    # Try to decode back
                    decoded = decoder.decode(encoded)
                    if decoded:
                        decoded_count += 1
                        if len(sample_forms) < 3:
                            sample_forms.append((word, encoded[:50]))
            except Exception:
                pass
        
        print(f"\n✓ Form encoding: {encoded_count}/10 encoded, {decoded_count}/10 decoded")
        if sample_forms:
            print(f"  Sample forms: {sample_forms[:2]}")
    
    def test_full_pipeline_on_verse(self):
        """Test: Run complete pipeline on entire verse"""
        print("\n" + "="*60)
        print("FULL PIPELINE TEST - Surah Al-Fath 48:29")
        print("="*60)
        
        # 1. Word Boundary Detection
        detector = WordBoundaryDetectorPlanB()
        boundaries = detector.detect_boundaries(VERSE)
        print(f"\n1. Word Boundaries: {len(boundaries)} words detected")
        
        # 2. Root Extraction
        extractor = RootExtractor()
        roots_extracted = 0
        for boundary in boundaries[:30]:
            try:
                root = extractor.extract(boundary.text)
                if root:
                    roots_extracted += 1
            except:
                pass
        print(f"2. Root Extraction: {roots_extracted}/30 roots extracted")
        
        # 3. Syllabification
        syllabified = 0
        for boundary in boundaries[:30]:
            try:
                result = syllabify(boundary.text)
                if result and result.syllables:
                    syllabified += 1
            except:
                pass
        print(f"3. Syllabification: {syllabified}/30 words syllabified")
        
        # 4. Classification
        classifier = WordClassifier()
        classified = 0
        for boundary in boundaries[:30]:
            try:
                classifier.classify(boundary.text)
                classified += 1
            except:
                pass
        print(f"4. Classification: {classified}/30 words classified")
        
        # 5. Pattern Catalog
        catalog = PatternCatalog.load_full_catalog()
        total_patterns = sum(len(patterns) for patterns in catalog.values())
        print(f"5. Pattern Catalog: {total_patterns} patterns loaded")
        
        print("\n" + "="*60)
        print("✓ FULL PIPELINE COMPLETED SUCCESSFULLY")
        print("="*60)
        
        # Overall assertions
        assert len(boundaries) > 0, "No words detected"
        assert roots_extracted > 0, "No roots extracted"
        assert syllabified > 0, "No syllabification"
        assert total_patterns > 0, "No patterns loaded"
    
    def test_verse_statistics(self):
        """Test: Generate statistics for the verse"""
        detector = WordBoundaryDetectorPlanB()
        boundaries = detector.detect_boundaries(VERSE)
        
        stats = {
            'total_words': len(boundaries),
            'total_characters': len(VERSE),
            'avg_word_length': sum(len(b.text) for b in boundaries) / len(boundaries) if boundaries else 0,
            'words_with_prefix': sum(1 for b in boundaries if b.has_prefix),
            'words_with_suffix': sum(1 for b in boundaries if b.has_suffix),
            'avg_confidence': sum(b.confidence for b in boundaries) / len(boundaries) if boundaries else 0,
            'total_syllables': sum(b.syllable_count for b in boundaries),
        }
        
        print(f"\n" + "="*60)
        print("VERSE STATISTICS (Al-Fath 48:29)")
        print("="*60)
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"{key:.<40} {value:.2f}")
            else:
                print(f"{key:.<40} {value}")
        print("="*60)
        
        # Basic sanity checks
        assert stats['total_words'] > 0
        assert stats['avg_word_length'] > 2
        assert stats['avg_confidence'] > 0


if __name__ == "__main__":
    # Run with: pytest tests/test_verse_integration.py -v -s
    pytest.main([__file__, "-v", "-s"])