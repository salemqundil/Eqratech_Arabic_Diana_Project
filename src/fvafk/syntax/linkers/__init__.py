"""
Syntactic Linkers

This package contains linkers for different types of syntactic relations:
- ISNADI: مبتدأ/خبر relations
- TADMINI: فعل/فاعل/مفعول relations (future)
- TAQYIDI: موصوف/صفة relations (future)
"""

from .link import Link, LinkType
from .isnadi_linker import IsnadiLinker, find_isnadi_links

__all__ = [
    'Link',
    'LinkType',
    'IsnadiLinker',
    'find_isnadi_links',
]
