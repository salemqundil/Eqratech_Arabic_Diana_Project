"""
FractalHub Codec Package

Provides bidirectional encoding/decoding between Arabic text and integer token sequences.
"""

from .fractalhub_codec import (
    encode_text_to_tokens,
    decode_tokens_to_text,
    normalize_text,
    verify_roundtrip,
    TokenTag,
    encode_position_token,
    decode_position_token,
)

__all__ = [
    'encode_text_to_tokens',
    'decode_tokens_to_text',
    'normalize_text',
    'verify_roundtrip',
    'TokenTag',
    'encode_position_token',
    'decode_position_token',
]

__version__ = '1.0.0'
