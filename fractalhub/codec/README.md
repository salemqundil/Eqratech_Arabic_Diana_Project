# FractalHub Arabic Text Codec

A bidirectional encoder/decoder for Arabic text that converts between Unicode strings and integer token sequences, with support for both vowelled and unvowelled modes.

## Features

- **Two Modes**:
  - `vowelled`: Preserves all diacritics (harakat)
  - `unvowelled`: Strips diacritics for consonant-only text
  
- **Full Arabic Support**:
  - All Arabic letters including hamza variants (أ إ ؤ ئ ء)
  - Taa marbuta (ة)
  - Alif maqsura (ى)
  - All harakat (fatha, damma, kasra, sukun, shadda, tanwin)
  
- **Additional Features**:
  - Spaces and punctuation
  - Arabic and Latin numbers
  - Line breaks
  - Tag-based token classification

## Installation

```bash
# The codec is part of the FractalHub package
cd /path/to/Eqratech_Arabic_Diana_Project
```

## Usage

### Basic Example

```python
from fractalhub.codec import encode_text_to_tokens, decode_tokens_to_text

# Vowelled mode (preserves diacritics)
text_vowelled = "السَّلامُ عَلَيْكُمْ"
tokens = encode_text_to_tokens(text_vowelled, mode='vowelled')
decoded = decode_tokens_to_text(tokens, mode='vowelled')
assert decoded == text_vowelled  # ✓ PASS

# Unvowelled mode (strips diacritics)
text_unvowelled = "السلام عليكم"
tokens = encode_text_to_tokens(text_unvowelled, mode='unvowelled')
decoded = decode_tokens_to_text(tokens, mode='unvowelled')
assert decoded == text_unvowelled  # ✓ PASS
```

### Advanced Example

```python
from fractalhub.codec import (
    encode_text_to_tokens,
    decode_tokens_to_text,
    normalize_text,
    verify_roundtrip,
)

# Complex text with punctuation
text = "مَرْحَبًا بِكَ! كَيْفَ حَالُكَ؟"

# Verify roundtrip theorem
assert verify_roundtrip(text, mode='vowelled')

# Normalize text
normalized = normalize_text(text, mode='vowelled')

# Get token count
tokens = encode_text_to_tokens(text, mode='vowelled')
print(f"Token count: {len(tokens)}")
```

## The Roundtrip Theorem

The codec guarantees that:

```
decode(encode(text, mode), mode) == normalize(text, mode)
```

This means:
- **Vowelled mode**: All diacritics are preserved
- **Unvowelled mode**: Input is stripped of diacritics, output has no diacritics

## Token Encoding Specification

### Token Structure

Each token is a 32-bit integer with the following structure:

```
[3-bit tag][29-bit payload]
```

### Token Tags

| Tag | Type | Description |
|-----|------|-------------|
| 0 | T_POS | PositionToken (Arabic letter + diacritics) |
| 1 | T_SPACE | Space character |
| 2 | T_PUNCT | Punctuation |
| 3 | T_DIGIT | Numeric digit (0-9) |
| 4 | T_LATIN | Latin letter (A-Z) |
| 5 | T_NEWLINE | Line break |
| 6 | T_UNKNOWN | Unknown/unsupported character |

### PositionToken Payload (T_POS)

The 29-bit payload for PositionToken is structured as:

```
[consonant_code: 8 bits][vowel_code: 4 bits][shadda: 1 bit][tanwin: 2 bits][reserved: 14 bits]
```

- **consonant_code** (0-255): Unique ID for each Arabic letter
- **vowel_code** (0-15): 
  - 0 = none
  - 1 = sukun (ْ)
  - 2 = fatha (َ)
  - 3 = damma (ُ)
  - 4 = kasra (ِ)
- **shadda** (0-1): Presence of shadda (ّ)
- **tanwin** (0-3):
  - 0 = none
  - 1 = fathatan (ً)
  - 2 = dammatan (ٌ)
  - 3 = kasratan (ٍ)

## API Reference

### `encode_text_to_tokens(text: str, mode: str = 'vowelled') -> List[int]`

Encode Arabic text to integer token sequence.

**Parameters:**
- `text`: Input text (Arabic with optional diacritics)
- `mode`: `'vowelled'` or `'unvowelled'`

**Returns:** List of encoded integer tokens

### `decode_tokens_to_text(tokens: List[int], mode: str = 'vowelled') -> str`

Decode integer token sequence back to Arabic text.

**Parameters:**
- `tokens`: List of encoded integer tokens
- `mode`: `'vowelled'` or `'unvowelled'`

**Returns:** Decoded text string

### `normalize_text(text: str, mode: str = 'vowelled') -> str`

Normalize text according to mode.

**Parameters:**
- `text`: Input text
- `mode`: `'vowelled'` or `'unvowelled'`

**Returns:** Normalized text (with line endings unified, diacritics removed if unvowelled)

### `verify_roundtrip(text: str, mode: str = 'vowelled') -> bool`

Verify the roundtrip theorem for given text.

**Parameters:**
- `text`: Input text
- `mode`: `'vowelled'` or `'unvowelled'`

**Returns:** `True` if roundtrip is successful

## Testing

Run the comprehensive test suite:

```bash
cd /path/to/Eqratech_Arabic_Diana_Project
python3 -m pytest tests/test_fractalhub_codec.py -v
```

All 34 tests validate:
- Token encoding/decoding primitives
- Text normalization
- Roundtrip theorem (vowelled and unvowelled)
- Special cases (empty strings, punctuation, numbers)
- Complex real-world sentences
- Encoding consistency and determinism

## Examples

### Example 1: Vowelled Greeting

```python
text = "السَّلامُ عَلَيْكُمْ"
tokens = encode_text_to_tokens(text, mode='vowelled')
decoded = decode_tokens_to_text(tokens, mode='vowelled')
# Result: السَّلامُ عَلَيْكُمْ (identical to input)
```

### Example 2: Unvowelled Text

```python
text = "مرحبا بك"
tokens = encode_text_to_tokens(text, mode='unvowelled')
decoded = decode_tokens_to_text(tokens, mode='unvowelled')
# Result: مرحبا بك (no diacritics)
```

### Example 3: Converting Vowelled to Unvowelled

```python
text_vowelled = "الْحَمْدُ لِلَّهِ"
tokens = encode_text_to_tokens(text_vowelled, mode='unvowelled')
text_unvowelled = decode_tokens_to_text(tokens, mode='unvowelled')
# Result: الحمد لله (diacritics stripped)
```

## Performance

The codec is designed for efficiency:
- **Encoding**: O(n) where n is the number of characters
- **Decoding**: O(m) where m is the number of tokens
- **Memory**: Each token is a single 32-bit integer

## Integration with Coq

This codec maps directly to the PositionToken structure defined in the Coq formalization:

```coq
Record PositionToken := {
  consonant_code : nat;
  vowel_code : nat;
  has_shadda : bool;
  tanwin_type : nat;
}.
```

The Python implementation provides a practical bridge between formal verification and real-world text processing.

## License

Part of the Eqratech Arabic Diana Project.

## See Also

- [Coq Theory Files](../coq/theories/) - Formal verification of linguistic constraints
- [Graph Engine](../graph_engine.py) - Multi-layered linguistic analysis system
