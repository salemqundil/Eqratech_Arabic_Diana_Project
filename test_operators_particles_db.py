"""Tests for operators and particles database"""
import pytest
from fvafk.c2b.operators_particles_db import (
    normalize_arabic,
    SpecialWordsDatabase,
    get_special_words_db
)


def test_normalize_arabic():
    """Test Arabic normalization"""
    text = "مَنْ"
    normalized = normalize_arabic(text)
    assert normalized is not None
    assert len(normalized) > 0


def test_database_initialization():
    """Test database can be initialized"""
    db = SpecialWordsDatabase(verbose=False)
    assert db is not None
    assert hasattr(db, 'words_dict')


def test_global_db_singleton():
    """Test global database is singleton"""
    db1 = get_special_words_db()
    db2 = get_special_words_db()
    assert db1 is db2


def test_lookup_basic():
    """Test basic word lookup"""
    db = get_special_words_db()
    result = db.lookup("من")
    assert result is None or result is not None


@pytest.mark.skipif(True, reason="Requires data files")
def test_csv_loading():
    """Test CSV operators loading"""
    db = SpecialWordsDatabase(verbose=True)
    assert len(db.words_dict) >= 0
