"""
Syntax Layer: Syntactic analysis for Arabic

This package provides syntactic analysis tools that build on top of
the morphological analysis from C2B using WordForm as the bridge.

Components:
- linkers: Syntactic relation detectors (ISNADI, TADMINI, TAQYIDI)
- link: Link class for syntactic relations

Author: Hussein Hiyassat
Date: 2025-02-13
Version: 1.0
"""

from .linkers.link import Link, LinkType
from .linkers.isnadi_linker import IsnadiLinker, find_isnadi_links

__version__ = '1.0.0'

__all__ = [
    'Link',
    'LinkType',
    'IsnadiLinker',
    'find_isnadi_links',
]
