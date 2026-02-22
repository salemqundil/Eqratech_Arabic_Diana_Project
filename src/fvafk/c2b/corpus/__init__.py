"""Corpus loading package for gold-standard annotations."""

from .corpus_format import (
    GoldAnnotation,
    CorpusEntry,
    CorpusStatistics,
    CorpusFormat,
)
from .corpus_loader import (
    CorpusLoader,
    load_corpus,
)

__all__ = [
    'GoldAnnotation',
    'CorpusEntry',
    'CorpusStatistics',
    'CorpusFormat',
    'CorpusLoader',
    'load_corpus',
]
