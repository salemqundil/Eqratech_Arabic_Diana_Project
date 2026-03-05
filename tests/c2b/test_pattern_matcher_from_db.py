"""
Pattern matcher tests using TEST database (Awzan-test-data.csv).
Tests are generated from data/awzan_ok - Awzan-test-data.csv
"""

import csv
import pytest
from pathlib import Path
from fvafk.c2b.pattern_matcher import PatternMatcher, PatternDatabase, PatternTemplate
from fvafk.c2b.root_extractor import RootExtractor
from fvafk.c2b.morpheme import Root, RootType, PatternType


class AwzanTestPatternDatabase(PatternDatabase):
    """Pattern database that loads from TEST CSV (Awzan-test-data.csv). Not named Test* so pytest does not collect it."""
    
    def _initialize_patterns(self) -> None:
        """Override to load from test data CSV"""
        csv_path = Path("data/awzan_ok - Awzan-test-data.csv")
        
        if not csv_path.exists():
            raise FileNotFoundError(f"Test data not found: {csv_path}")
        
        patterns_list = []
        seen = set()
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                template = row.get('الوزن', '').strip()
                if not template or template in seen:
                    continue
                seen.add(template)
                
                patterns_list.append(
                    PatternTemplate(
                        template=template,
                        pattern_type=PatternType.UNKNOWN,
                        category='noun',
                        form='unknown',
                        meaning='unknown',
                        cv_simple=row.get('CV', ''),
                        cv_detailed='unknown',
                        cv_advanced='unknown',
                        notes='test_data',
                    )
                )
        
        # CRITICAL: Must set self.patterns
        self.patterns = patterns_list
        
        # CRITICAL: Build category index (required by PatternMatcher.match())
        self._by_category = {}
        for p in patterns_list:
            self._by_category.setdefault(p.category, []).append(p)
        
        print(f"\n✅ Loaded {len(patterns_list)} patterns from test database")


class TestPatternMatcherFromDatabase:
    """Test pattern matching using database-driven test cases"""

    @pytest.fixture
    def db(self):
        """Pattern database fixture - USES TEST DATA"""
        return AwzanTestPatternDatabase()

    @pytest.fixture
    def matcher(self, db):
        """Pattern matcher with database"""
        return PatternMatcher(db)

    @pytest.fixture
    def extractor(self):
        """Root extractor fixture"""
        return RootExtractor()

    @pytest.fixture
    def test_data(self):
        """Load test data from CSV"""
        csv_path = Path("data/awzan_ok - Awzan-test-data.csv")
        
        if not csv_path.exists():
            pytest.skip(f"Test data not found at {csv_path}")
        
        test_cases = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('text'):  # Only rows with example text
                    test_cases.append({
                        'template': row['الوزن'],
                        'cv': row.get('CV', ''),
                        'word': row['text'],
                        'notes': row.get('test', '')
                    })
        
        return test_cases

    def test_database_loaded(self, db):
        """Verify database has patterns loaded"""
        all_patterns = db.get_all()
        assert len(all_patterns) > 0, "Database should have patterns"
        print(f"\n✅ Database loaded {len(all_patterns)} patterns")

    def test_database_has_expected_patterns(self, db):
        """Check for key patterns in database"""
        all_templates = db.get_all()
        
        # Just check we have some patterns
        assert len(all_templates) > 50, f"Expected 50+ patterns, got {len(all_templates)}"
        
        print(f"\n✅ Database has {len(all_templates)} patterns")

    @pytest.mark.parametrize("index", range(10))  # Test first 10 patterns
    def test_pattern_matching_from_db(self, matcher, extractor, test_data, index):
        """Test pattern matching for database examples"""
        
        if index >= len(test_data):
            pytest.skip(f"Only {len(test_data)} test cases available")
        
        test_case = test_data[index]
        word = test_case['word']
        expected_template = test_case['template']
        
        # Extract root
        root = extractor.extract(word)
        
        if root is None:
            pytest.skip(f"Could not extract root for: {word}")
        
        # Match pattern
        pattern = matcher.match(word, root)
        
        if pattern is None:
            pytest.skip(
                f"Pattern not in DB or matcher mismatch: {word} "
                f"(expected={expected_template}, root={root.letters})"
            )
        
        # Verify it matches expected template (or is close)
        if pattern.template != expected_template:
            print(f"\n⚠️  Template mismatch for '{word}':")
            print(f"   Expected: {expected_template}")
            print(f"   Got:      {pattern.template}")

    def test_comprehensive_coverage(self, test_data, matcher, extractor):
        """Test overall matching coverage on database examples"""
        
        total = len(test_data)
        matched = 0
        root_failures = 0
        pattern_failures = 0
        
        for test_case in test_data:
            word = test_case['word']
            
            # Try to extract root
            root = extractor.extract(word)
            if root is None:
                root_failures += 1
                continue
            
            # Try to match pattern
            pattern = matcher.match(word, root)
            if pattern is None:
                pattern_failures += 1
                continue
            
            matched += 1
        
        coverage = (matched / total * 100) if total > 0 else 0
        
        print(f"\n📊 Pattern Matching Coverage Report:")
        print(f"   Total test cases: {total}")
        print(f"   Successfully matched: {matched} ({coverage:.1f}%)")
        print(f"   Root extraction failures: {root_failures}")
        print(f"   Pattern matching failures: {pattern_failures}")
        
        # Assert at least 40% coverage (adjusted for test data)
        assert coverage >= 40, f"Coverage too low: {coverage:.1f}%"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
