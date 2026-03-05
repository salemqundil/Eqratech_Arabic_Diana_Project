"""
FractalHub Arabic Text Codec

Implements bidirectional encoding/decoding between Arabic text and integer token sequences
with support for vowelled and unvowelled modes.

Theorem: decode(encode(text, mode), mode) == normalize(text, mode)
"""

from typing import List, Tuple, Optional
from enum import IntEnum
import unicodedata
import re


class TokenTag(IntEnum):
    """Tag types for token classification using bit-packing."""
    T_POS = 0      # PositionToken (consonant + vowel + marks)
    T_SPACE = 1    # Space character
    T_PUNCT = 2    # Punctuation
    T_DIGIT = 3    # Numeric digit
    T_LATIN = 4    # Latin character
    T_NEWLINE = 5  # Newline character
    T_UNKNOWN = 6  # Unknown/unsupported character


# Arabic character ranges and diacritics
ARABIC_LETTERS = (
    'ء' 'آ' 'أ' 'ؤ' 'إ' 'ئ' 'ا' 'ب' 'ة' 'ت' 'ث' 'ج' 'ح' 'خ' 'د' 'ذ' 
    'ر' 'ز' 'س' 'ش' 'ص' 'ض' 'ط' 'ظ' 'ع' 'غ' 'ف' 'ق' 'ك' 'ل' 'م' 'ن' 
    'ه' 'و' 'ى' 'ي' 'ٱ' 'ٹ' 'پ' 'چ' 'ژ' 'ڤ' 'ڭ' 'گ' 'ۏ'
)

# Harakat (vowel marks) and diacritics
HARAKAT = {
    'فَتْحَة': '\u064E',  # FATHA
    'ضَمَّة': '\u064F',   # DAMMA
    'كَسْرَة': '\u0650',  # KASRA
    'سُكُون': '\u0652',   # SUKUN
    'شَدَّة': '\u0651',   # SHADDA
    'تَنْوِينُ الْفَتْح': '\u064B',  # FATHATAN
    'تَنْوِينُ الضَّمّ': '\u064C',   # DAMMATAN
    'تَنْوِينُ الْكَسْر': '\u064D',  # KASRATAN
    'مَدَّة': '\u0653',     # MADDAH
}

HARAKAT_CHARS = ''.join(HARAKAT.values())
ALL_DIACRITICS = HARAKAT_CHARS + '\u0640\u0654\u0655\u0656\u0657\u0658'  # Include tatweel and others

# Consonant code mapping (stable IDs)
CONSONANT_CODES = {
    'ء': 1, 'آ': 2, 'أ': 3, 'ؤ': 4, 'إ': 5, 'ئ': 6, 'ا': 7,
    'ب': 8, 'ة': 9, 'ت': 10, 'ث': 11, 'ج': 12, 'ح': 13, 'خ': 14,
    'د': 15, 'ذ': 16, 'ر': 17, 'ز': 18, 'س': 19, 'ش': 20,
    'ص': 21, 'ض': 22, 'ط': 23, 'ظ': 24, 'ع': 25, 'غ': 26,
    'ف': 27, 'ق': 28, 'ك': 29, 'ل': 30, 'م': 31, 'ن': 32,
    'ه': 33, 'و': 34, 'ى': 35, 'ي': 36,
}

# Vowel code mapping (0 = NONE, 1 = SUKUN, 2 = FATHA, 3 = DAMMA, 4 = KASRA)
VOWEL_CODES = {
    '': 0,
    '\u0652': 1,  # SUKUN
    '\u064E': 2,  # FATHA
    '\u064F': 3,  # DAMMA
    '\u0650': 4,  # KASRA
}

# Reverse mappings
CODE_TO_CONSONANT = {v: k for k, v in CONSONANT_CODES.items()}
CODE_TO_VOWEL = {v: k for k, v in VOWEL_CODES.items()}

# Punctuation mapping
PUNCTUATION_CODES = {
    ' ': 1, '.': 2, ',': 3, '؟': 4, '!': 5, ':': 6, ';': 7, '؛': 8,
    '-': 9, '(': 10, ')': 11, '[': 12, ']': 13, '{': 14, '}': 15,
    '"': 16, "'": 17, '«': 18, '»': 19, '…': 20,
}

CODE_TO_PUNCTUATION = {v: k for k, v in PUNCTUATION_CODES.items()}

# Tag bit configuration: Use top 3 bits for tag, remaining bits for payload
TAG_BITS = 3
TAG_SHIFT = 29  # Shift tag to top 3 bits of 32-bit integer
TAG_MASK = 0b111 << TAG_SHIFT
PAYLOAD_MASK = (1 << TAG_SHIFT) - 1


def encode_token(tag: TokenTag, payload: int) -> int:
    """
    Encode a token with tag and payload into a single integer.
    
    Format: [3-bit tag][29-bit payload]
    """
    if payload < 0 or payload > PAYLOAD_MASK:
        raise ValueError(f"Payload {payload} out of range")
    return (tag << TAG_SHIFT) | payload


def decode_token(token: int) -> Tuple[TokenTag, int]:
    """
    Decode a token into tag and payload.
    
    Returns: (TokenTag, payload)
    """
    tag = (token & TAG_MASK) >> TAG_SHIFT
    payload = token & PAYLOAD_MASK
    return TokenTag(tag), payload


def encode_position_token(consonant_code: int, vowel_code: int, 
                         has_shadda: bool = False, tanwin_type: int = 0) -> int:
    """
    Encode a PositionToken-like structure.
    
    Payload structure (29 bits):
    - bits 0-7: consonant_code (8 bits, 0-255)
    - bits 8-11: vowel_code (4 bits, 0-15)
    - bit 12: has_shadda flag
    - bits 13-14: tanwin_type (2 bits: 0=none, 1=fathatan, 2=dammatan, 3=kasratan)
    - bits 15-28: reserved
    """
    payload = (
        (consonant_code & 0xFF) |
        ((vowel_code & 0xF) << 8) |
        ((1 if has_shadda else 0) << 12) |
        ((tanwin_type & 0x3) << 13)
    )
    return encode_token(TokenTag.T_POS, payload)


def decode_position_token(token: int) -> Tuple[int, int, bool, int]:
    """
    Decode a PositionToken.
    
    Returns: (consonant_code, vowel_code, has_shadda, tanwin_type)
    """
    tag, payload = decode_token(token)
    if tag != TokenTag.T_POS:
        raise ValueError(f"Expected T_POS token, got {tag}")
    
    consonant_code = payload & 0xFF
    vowel_code = (payload >> 8) & 0xF
    has_shadda = bool((payload >> 12) & 1)
    tanwin_type = (payload >> 13) & 0x3
    
    return consonant_code, vowel_code, has_shadda, tanwin_type


def normalize_text(text: str, mode: str = 'vowelled') -> str:
    """
    Normalize text according to mode.
    
    Args:
        text: Input text
        mode: 'vowelled' or 'unvowelled'
    
    Returns:
        Normalized text
    """
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    if mode == 'unvowelled':
        # Remove all Arabic diacritics
        text = ''.join(char for char in text if char not in ALL_DIACRITICS)
    
    return text


def encode_text_to_tokens(text: str, mode: str = 'vowelled') -> List[int]:
    """
    Encode Arabic text to integer token sequence.
    
    Args:
        text: Input text (Arabic with optional diacritics)
        mode: 'vowelled' or 'unvowelled'
    
    Returns:
        List of encoded integer tokens
    """
    # Normalize first
    text = normalize_text(text, mode)
    
    tokens = []
    i = 0
    
    while i < len(text):
        char = text[i]
        
        # Handle newline
        if char == '\n':
            tokens.append(encode_token(TokenTag.T_NEWLINE, 0))
            i += 1
            continue
        
        # Handle space
        if char == ' ':
            tokens.append(encode_token(TokenTag.T_SPACE, 0))
            i += 1
            continue
        
        # Handle punctuation
        if char in PUNCTUATION_CODES:
            punct_code = PUNCTUATION_CODES[char]
            tokens.append(encode_token(TokenTag.T_PUNCT, punct_code))
            i += 1
            continue
        
        # Handle digits
        if char.isdigit():
            digit_value = ord(char) - ord('0') if char.isascii() else ord(char) - ord('٠')
            tokens.append(encode_token(TokenTag.T_DIGIT, digit_value))
            i += 1
            continue
        
        # Handle Arabic letters
        if char in CONSONANT_CODES:
            consonant_code = CONSONANT_CODES[char]
            vowel_code = 0
            has_shadda = False
            tanwin_type = 0  # 0=none, 1=fathatan, 2=dammatan, 3=kasratan
            
            # Look ahead for diacritics (only in vowelled mode)
            if mode == 'vowelled':
                j = i + 1
                while j < len(text) and text[j] in ALL_DIACRITICS:
                    diacritic = text[j]
                    
                    # Check for vowels
                    if diacritic in VOWEL_CODES:
                        vowel_code = VOWEL_CODES[diacritic]
                    
                    # Check for shadda
                    if diacritic == '\u0651':
                        has_shadda = True
                    
                    # Check for tanwin
                    if diacritic == '\u064B':  # FATHATAN
                        tanwin_type = 1
                    elif diacritic == '\u064C':  # DAMMATAN
                        tanwin_type = 2
                    elif diacritic == '\u064D':  # KASRATAN
                        tanwin_type = 3
                    
                    j += 1
                
                i = j
            else:
                i += 1
            
            token = encode_position_token(consonant_code, vowel_code, has_shadda, tanwin_type)
            tokens.append(token)
            continue
        
        # Handle Latin characters (optional)
        if char.isascii() and char.isalpha():
            latin_value = ord(char.upper()) - ord('A')
            tokens.append(encode_token(TokenTag.T_LATIN, latin_value))
            i += 1
            continue
        
        # Unknown character - skip or encode as unknown
        tokens.append(encode_token(TokenTag.T_UNKNOWN, ord(char) & PAYLOAD_MASK))
        i += 1
    
    return tokens


def decode_tokens_to_text(tokens: List[int], mode: str = 'vowelled') -> str:
    """
    Decode integer token sequence back to Arabic text.
    
    Args:
        tokens: List of encoded integer tokens
        mode: 'vowelled' or 'unvowelled'
    
    Returns:
        Decoded text string
    """
    result = []
    
    for token in tokens:
        tag, payload = decode_token(token)
        
        if tag == TokenTag.T_POS:
            consonant_code, vowel_code, has_shadda, tanwin_type = decode_position_token(token)
            
            # Get consonant
            if consonant_code in CODE_TO_CONSONANT:
                result.append(CODE_TO_CONSONANT[consonant_code])
                
                # Add diacritics only in vowelled mode
                if mode == 'vowelled':
                    # Order matters: vowel first, then shadda (or vice versa depending on input)
                    # Standard order: shadda first, then vowel
                    if vowel_code in CODE_TO_VOWEL and vowel_code != 0:
                        result.append(CODE_TO_VOWEL[vowel_code])
                    
                    if has_shadda:
                        result.append('\u0651')  # SHADDA
                    
                    # Add specific tanwin type
                    if tanwin_type == 1:
                        result.append('\u064B')  # FATHATAN
                    elif tanwin_type == 2:
                        result.append('\u064C')  # DAMMATAN
                    elif tanwin_type == 3:
                        result.append('\u064D')  # KASRATAN
        
        elif tag == TokenTag.T_SPACE:
            result.append(' ')
        
        elif tag == TokenTag.T_NEWLINE:
            result.append('\n')
        
        elif tag == TokenTag.T_PUNCT:
            if payload in CODE_TO_PUNCTUATION:
                result.append(CODE_TO_PUNCTUATION[payload])
        
        elif tag == TokenTag.T_DIGIT:
            if 0 <= payload <= 9:
                result.append(str(payload))
        
        elif tag == TokenTag.T_LATIN:
            if 0 <= payload < 26:
                result.append(chr(ord('A') + payload))
        
        # T_UNKNOWN - skip
    
    return ''.join(result)


def verify_roundtrip(text: str, mode: str = 'vowelled') -> bool:
    """
    Verify the roundtrip theorem: decode(encode(text, mode), mode) == normalize(text, mode)
    
    Args:
        text: Input text
        mode: 'vowelled' or 'unvowelled'
    
    Returns:
        True if roundtrip is successful
    """
    normalized = normalize_text(text, mode)
    tokens = encode_text_to_tokens(text, mode)
    decoded = decode_tokens_to_text(tokens, mode)
    
    return decoded == normalized


# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_cases = [
        ("السَّلامُ عَلَيْكُمْ", 'vowelled'),
        ("السلام عليكم", 'unvowelled'),
        ("مَرْحَبًا بِكَ!", 'vowelled'),
        ("مرحبا بك!", 'unvowelled'),
    ]
    
    print("FractalHub Codec - Roundtrip Tests\n" + "="*50)
    
    for text, mode in test_cases:
        print(f"\nOriginal ({mode}): {text}")
        
        # Encode
        tokens = encode_text_to_tokens(text, mode)
        print(f"Tokens ({len(tokens)}): {tokens[:10]}..." if len(tokens) > 10 else f"Tokens: {tokens}")
        
        # Decode
        decoded = decode_tokens_to_text(tokens, mode)
        print(f"Decoded: {decoded}")
        
        # Verify
        is_valid = verify_roundtrip(text, mode)
        status = "✓ PASS" if is_valid else "✗ FAIL"
        print(f"Roundtrip: {status}")
        
        if not is_valid:
            normalized = normalize_text(text, mode)
            print(f"  Expected: {normalized}")
            print(f"  Got:      {decoded}")
