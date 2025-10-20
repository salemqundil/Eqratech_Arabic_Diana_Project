"""UTF-8 Tokenizer for Arabic Phonemes

This module implements a custom tokenizer for Arabic phoneme processing,
utilizing UTF-8 encoding for proper handling of Arabic characters.
"""

from typing import List, Dict, Optional, Union
import json
import os


class UTF8PhonemeTokenizer:
    """
    UTF-8 based tokenizer for Arabic phonemes.
    
    This tokenizer handles Arabic text at the phoneme level, properly encoding
    characters in UTF-8 format for BERT model training.
    """
    
    def __init__(
        self,
        vocab_file: Optional[str] = None,
        unk_token: str = "[UNK]",
        sep_token: str = "[SEP]",
        pad_token: str = "[PAD]",
        cls_token: str = "[CLS]",
        mask_token: str = "[MASK]",
        max_length: int = 512
    ):
        """
        Initialize the UTF-8 Phoneme Tokenizer.
        
        Args:
            vocab_file: Path to vocabulary file (optional)
            unk_token: Unknown token
            sep_token: Separator token
            pad_token: Padding token
            cls_token: Classification token
            mask_token: Mask token for MLM
            max_length: Maximum sequence length
        """
        self.unk_token = unk_token
        self.sep_token = sep_token
        self.pad_token = pad_token
        self.cls_token = cls_token
        self.mask_token = mask_token
        self.max_length = max_length
        
        # Initialize vocabulary
        self.vocab = {}
        self.inverse_vocab = {}
        
        # Add special tokens first
        self.special_tokens = [
            self.pad_token,
            self.unk_token,
            self.cls_token,
            self.sep_token,
            self.mask_token
        ]
        
        for idx, token in enumerate(self.special_tokens):
            self.vocab[token] = idx
            self.inverse_vocab[idx] = token
        
        # Load vocabulary if provided
        if vocab_file and os.path.exists(vocab_file):
            self.load_vocab(vocab_file)
    
    def build_vocab_from_phonemes(self, phonemes_csv: Optional[str] = None) -> None:
        """
        Build vocabulary from phonemes CSV file.
        
        Args:
            phonemes_csv: Path to phonemes CSV file
        """
        try:
            # Try to include ontology symbols/sets first (best-effort, independent of pandas)
            try:
                from phoneme_ontology import get_ontology
                ont = get_ontology()
                for item in ont.phoneme_inventory():
                    sym = str(item.get('symbol', '')).strip()
                    if sym and sym not in self.vocab:
                        self._add_to_vocab(sym)
                for ch in ont.functional_sets().get('mudari_prefix', []):
                    if ch and ch not in self.vocab:
                        self._add_to_vocab(ch)
                for ch in ont.functional_sets().get('ten_augments', []):
                    if ch and ch not in self.vocab:
                        self._add_to_vocab(ch)
            except Exception:
                # Ontology is optional; ignore if missing
                pass

            import pandas as pd
            
            # Try to load phonemes from the existing phonemes_engine
            if phonemes_csv is None:
                # Look for phonemes CSV in the current directory
                possible_paths = [
                    'الفونيمات.csv',
                    'Phonemes.csv',
                    'full_multilayer_grammar.csv'
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        phonemes_csv = path
                        break
            
            if phonemes_csv and os.path.exists(phonemes_csv):
                df = pd.read_csv(phonemes_csv, encoding='utf-8-sig')
                
                # Extract phonemes from the DataFrame
                if 'الفونيمات' in df.columns:
                    phoneme_col = 'الفونيمات'
                elif 'phonemes' in df.columns:
                    phoneme_col = 'phonemes'
                else:
                    phoneme_col = df.columns[0]
                
                # Add each phoneme to vocabulary
                for phoneme in df[phoneme_col].dropna().unique():
                    phoneme_str = str(phoneme).strip()
                    if phoneme_str and phoneme_str not in self.vocab:
                        # Split compound phonemes by '/'
                        parts = phoneme_str.split('/')
                        for part in parts:
                            if part and part not in self.vocab:
                                self._add_to_vocab(part)
                        
                        # Also add the full compound phoneme
                        if '/' in phoneme_str:
                            self._add_to_vocab(phoneme_str)
                
                # Also add individual characters for character-level tokenization
                for phoneme in df[phoneme_col].dropna():
                    for char in str(phoneme):
                        if char.strip() and char not in self.vocab:
                            self._add_to_vocab(char)
            
            print(f"[UTF8PhonemeTokenizer] Built vocabulary with {len(self.vocab)} tokens")
            
        except Exception as e:
            print(f"[UTF8PhonemeTokenizer] Warning: Could not build vocab from CSV: {e}")
            print("[UTF8PhonemeTokenizer] Using basic Arabic character vocabulary")
            self._build_basic_arabic_vocab()
    
    def _build_basic_arabic_vocab(self) -> None:
        """Build a basic Arabic character vocabulary."""
        # Arabic letters (Alef to Ya)
        arabic_letters = [
            'ا', 'أ', 'إ', 'آ', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 
            'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ',
            'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'ه', 'و', 'ي', 'ى', 'ة'
        ]
        
        # Arabic diacritics (Harakat)
        arabic_diacritics = [
            'َ', 'ً', 'ُ', 'ٌ', 'ِ', 'ٍ', 'ْ', 'ّ', 'ٰ'
        ]
        
        # Add all to vocabulary
        for char in arabic_letters + arabic_diacritics:
            if char not in self.vocab:
                self._add_to_vocab(char)
        
        # Add common punctuation
        for char in [' ', '.', '،', '؛', '؟', '!', '-', '/', '(', ')']:
            if char not in self.vocab:
                self._add_to_vocab(char)
    
    def _add_to_vocab(self, token: str) -> None:
        """Add a token to the vocabulary."""
        if token not in self.vocab:
            idx = len(self.vocab)
            self.vocab[token] = idx
            self.inverse_vocab[idx] = token
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into phoneme tokens.
        
        Args:
            text: Input text string
            
        Returns:
            List of tokens
        """
        if not text:
            return []
        
        tokens = []
        
        # Split by spaces first to handle words
        words = text.split()
        
        for word in words:
            # For each word, split into individual characters
            # This handles Arabic characters properly in UTF-8
            for char in word:
                if char in self.vocab:
                    tokens.append(char)
                else:
                    tokens.append(self.unk_token)
        
        return tokens
    
    def encode(
        self,
        text: str,
        add_special_tokens: bool = True,
        max_length: Optional[int] = None,
        padding: bool = False,
        truncation: bool = True
    ) -> Dict[str, List[int]]:
        """
        Encode text to token IDs.
        
        Args:
            text: Input text
            add_special_tokens: Whether to add CLS and SEP tokens
            max_length: Maximum sequence length
            padding: Whether to pad to max_length
            truncation: Whether to truncate to max_length
            
        Returns:
            Dictionary with 'input_ids' and 'attention_mask'
        """
        # Tokenize
        tokens = self.tokenize(text)
        
        # Add special tokens
        if add_special_tokens:
            tokens = [self.cls_token] + tokens + [self.sep_token]
        
        # Convert to IDs
        input_ids = [self.vocab.get(token, self.vocab[self.unk_token]) for token in tokens]
        
        # Handle max length
        if max_length is None:
            max_length = int(self.max_length)
        else:
            max_length = int(max_length)
        
        # Truncate if necessary
        if truncation and len(input_ids) > max_length:
            input_ids = input_ids[:max_length]
        
        # Create attention mask
        attention_mask = [1] * len(input_ids)
        
        # Pad if necessary
        if padding and len(input_ids) < max_length:
            pad_length = max_length - len(input_ids)
            input_ids += [self.vocab[self.pad_token]] * pad_length
            attention_mask += [0] * pad_length
        
        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask
        }
    
    def _decode_single(self, token_ids: List[int], skip_special_tokens: bool = True) -> str:
        """Decode a single sequence of token IDs back to text."""
        tokens: List[str] = []
        for idx in token_ids:
            if idx in self.inverse_vocab:
                token = self.inverse_vocab[idx]
                if skip_special_tokens and token in self.special_tokens:
                    continue
                tokens.append(token)
        return ''.join(tokens)

    def decode(self, token_ids: Union[List[int], List[List[int]]], skip_special_tokens: bool = True) -> Union[str, List[str]]:
        """
        Decode token IDs back to text.
        
        Args:
            token_ids: Token IDs to decode
            skip_special_tokens: Whether to skip special tokens
            
        Returns:
            Decoded text string or list of strings
        """
        # Handle batch decoding
        if isinstance(token_ids[0], list):
            return [self._decode_single(ids, skip_special_tokens) for ids in token_ids]  # type: ignore[index]

        # Decode single sequence
        return self._decode_single(token_ids, skip_special_tokens)  # type: ignore[arg-type]
    
    def save_vocab(self, save_path: str) -> None:
        """Save vocabulary to disk.

        Writes a JSON file. Primary format is a dict containing keys:
        - 'vocab': token->id mapping
        - 'special_tokens': dict of special token strings
        - 'max_length': int

        For compatibility, if downstream tools expect just a flat mapping,
        they can read the 'vocab' field. Our load_vocab also accepts a flat
        mapping file written by older variants.
        """
        vocab_dir = os.path.dirname(save_path)
        if vocab_dir:
            os.makedirs(vocab_dir, exist_ok=True)

        vocab_data = {
            'vocab': self.vocab,
            'special_tokens': {
                'unk_token': self.unk_token,
                'sep_token': self.sep_token,
                'pad_token': self.pad_token,
                'cls_token': self.cls_token,
                'mask_token': self.mask_token,
            },
            'max_length': self.max_length,
        }

        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(vocab_data, f, ensure_ascii=False, indent=2)

        print(f"[UTF8PhonemeTokenizer] Vocabulary saved to {save_path}")
    
    def save_pretrained(self, save_directory: str) -> None:
        """
        Save tokenizer to directory (for HuggingFace compatibility).
        
        Args:
            save_directory: Directory to save tokenizer
        """
        os.makedirs(save_directory, exist_ok=True)
        vocab_path = os.path.join(save_directory, 'vocab.json')
        self.save_vocab(vocab_path)
        # Also write a lightweight tokenizer config for convenience
        cfg = {
            "tokenizer_class": self.__class__.__name__,
            "special_tokens": {
                "unk_token": self.unk_token,
                "sep_token": self.sep_token,
                "pad_token": self.pad_token,
                "cls_token": self.cls_token,
                "mask_token": self.mask_token,
            },
            "max_length": int(self.max_length),
            "vocab_file": "vocab.json",
        }
        with open(os.path.join(save_directory, 'utf8_tokenizer.json'), 'w', encoding='utf-8') as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)

    @classmethod
    def from_pretrained(cls, load_directory: str) -> "UTF8PhonemeTokenizer":
        """Load tokenizer from a directory produced by save_pretrained."""
        vocab_path = os.path.join(load_directory, 'vocab.json')
        # Optional: read config to override max_length/special tokens if needed
        cfg_path = os.path.join(load_directory, 'utf8_tokenizer.json')
        special: Dict[str, str] = {}
        max_len: Optional[int] = None
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                special = cfg.get('special_tokens', {}) or {}
                ml = cfg.get('max_length')
                if isinstance(ml, int):
                    max_len = ml
            except Exception:
                pass
        tok = cls(
            vocab_file=vocab_path if os.path.exists(vocab_path) else None,
            unk_token=special.get('unk_token', '[UNK]'),
            sep_token=special.get('sep_token', '[SEP]'),
            pad_token=special.get('pad_token', '[PAD]'),
            cls_token=special.get('cls_token', '[CLS]'),
            mask_token=special.get('mask_token', '[MASK]'),
            max_length=max_len if max_len is not None else 512,
        )
        # If vocab_file missing, attempt to load from flat/structured anyway
        if os.path.exists(vocab_path):
            tok.load_vocab(vocab_path)
        return tok

# Alias for backward compatibility with earlier notebook text
class UTF8CharTokenizer(UTF8PhonemeTokenizer):
    pass
    
    def load_vocab(self, vocab_file: str) -> None:
        """
        Load vocabulary from file.
        
        Args:
            vocab_file: Path to vocabulary file
        """
        with open(vocab_file, 'r', encoding='utf-8') as f:
            vocab_data = json.load(f)

        # Support both structured and flat vocab files
        if isinstance(vocab_data, dict) and 'vocab' in vocab_data:
            self.vocab = {str(k): int(v) for k, v in vocab_data['vocab'].items()}
            if 'special_tokens' in vocab_data:
                special = vocab_data['special_tokens']
                self.unk_token = special.get('unk_token', self.unk_token)
                self.sep_token = special.get('sep_token', self.sep_token)
                self.pad_token = special.get('pad_token', self.pad_token)
                self.cls_token = special.get('cls_token', self.cls_token)
                self.mask_token = special.get('mask_token', self.mask_token)
            if 'max_length' in vocab_data:
                try:
                    self.max_length = int(vocab_data['max_length'])
                except Exception:
                    pass
        else:
            # Assume flat mapping token->id
            self.vocab = {str(k): int(v) for k, v in vocab_data.items()}

        # Rebuild inverse vocab
        self.inverse_vocab = {int(v): k for k, v in self.vocab.items()}

        print(f"[UTF8PhonemeTokenizer] Vocabulary loaded from {vocab_file} ({len(self.vocab)} tokens)")
    
    @property
    def vocab_size(self) -> int:
        """Get vocabulary size."""
        return len(self.vocab)
    
    def __len__(self) -> int:
        """Get vocabulary size."""
        return self.vocab_size
    
    def __call__(self, text: Union[str, List[str]], **kwargs) -> Dict:
        """
        Tokenizer call method for compatibility with HuggingFace.
        
        Args:
            text: Input text or list of texts
            **kwargs: Additional encoding arguments
            
        Returns:
            Encoded outputs
        """
        if isinstance(text, str):
            return self.encode(text, **kwargs)
        else:
            # Batch encoding
            return {
                'input_ids': [self.encode(t, **kwargs)['input_ids'] for t in text],
                'attention_mask': [self.encode(t, **kwargs)['attention_mask'] for t in text]
            }
    
    def pad(self, encoded_inputs, padding=True, max_length=None, return_tensors=None, **kwargs):
        """
        Pad encoded inputs to the same length.
        
        Args:
            encoded_inputs: Dictionary with 'input_ids' and optionally 'attention_mask'
            padding: Whether to pad
            max_length: Maximum length to pad to
            return_tensors: Type of tensors to return ('pt' for PyTorch)
            **kwargs: Additional arguments (ignored for compatibility)
            
        Returns:
            Padded inputs
        """
        if max_length is None:
            max_length = self.max_length
        
        # Handle batch padding
        if isinstance(encoded_inputs, dict) and 'input_ids' in encoded_inputs:
            input_ids = encoded_inputs['input_ids']
            attention_mask = encoded_inputs.get('attention_mask', None)
            
            # If input_ids is a list of lists (batch)
            if isinstance(input_ids[0], list):
                padded_ids = []
                padded_masks = []
                
                for idx, ids in enumerate(input_ids):
                    if len(ids) < max_length:
                        pad_length = max_length - len(ids)
                        padded_ids.append(ids + [self.vocab[self.pad_token]] * pad_length)
                        if attention_mask:
                            padded_masks.append(attention_mask[idx] + [0] * pad_length)
                        else:
                            padded_masks.append([1] * len(ids) + [0] * pad_length)
                    else:
                        padded_ids.append(ids[:max_length])
                        if attention_mask:
                            padded_masks.append(attention_mask[idx][:max_length])
                        else:
                            padded_masks.append([1] * max_length)
                
                result = {
                    'input_ids': padded_ids,
                    'attention_mask': padded_masks
                }
            else:
                # Single sequence
                if len(input_ids) < max_length:
                    pad_length = max_length - len(input_ids)
                    result = {
                        'input_ids': input_ids + [self.vocab[self.pad_token]] * pad_length,
                        'attention_mask': (attention_mask or [1] * len(input_ids)) + [0] * pad_length
                    }
                else:
                    result = {
                        'input_ids': input_ids[:max_length],
                        'attention_mask': (attention_mask or [1] * len(input_ids))[:max_length]
                    }
            
            # Convert to tensors if requested
            if return_tensors == 'pt':
                import torch
                result = {k: torch.tensor(v) for k, v in result.items()}
            
            return result
        
        return encoded_inputs


def create_tokenizer(config: Optional[Dict] = None) -> UTF8PhonemeTokenizer:
    """
    Factory function to create a UTF-8 Phoneme Tokenizer.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        UTF8PhonemeTokenizer instance
    """
    if config is None:
        config = {}
    
    tokenizer_config = config.get('tokenizer', {})
    special_tokens = tokenizer_config.get('special_tokens', {})
    
    tokenizer = UTF8PhonemeTokenizer(
        unk_token=special_tokens.get('unk_token', '[UNK]'),
        sep_token=special_tokens.get('sep_token', '[SEP]'),
        pad_token=special_tokens.get('pad_token', '[PAD]'),
        cls_token=special_tokens.get('cls_token', '[CLS]'),
        mask_token=special_tokens.get('mask_token', '[MASK]'),
        max_length=config.get('training', {}).get('max_seq_length', 512)
    )
    
    # Build vocabulary from phonemes
    tokenizer.build_vocab_from_phonemes()

    # Optionally seed additional texts (ensure demo chars/tokens are present)
    cfg_dict: Dict = config if isinstance(config, dict) else {}
    seed_texts = cfg_dict.get('seed_texts')
    if isinstance(seed_texts, list):
        for text in seed_texts:
            for ch in str(text):
                if ch and ch.strip() and ch not in tokenizer.vocab:
                    tokenizer._add_to_vocab(ch)
    
    return tokenizer


if __name__ == '__main__':
    # Test the tokenizer
    print("Testing UTF-8 Phoneme Tokenizer...")
    
    tokenizer = UTF8PhonemeTokenizer()
    tokenizer.build_vocab_from_phonemes()
    
    # Test encoding
    test_text = "مَرْحَبًا بِكَ"
    print(f"\nTest text: {test_text}")
    
    encoded = tokenizer.encode(test_text, padding=True, max_length=20)
    print(f"Encoded IDs: {encoded['input_ids'][:10]}...")
    print(f"Attention mask: {encoded['attention_mask'][:10]}...")
    
    # Test decoding
    decoded = tokenizer.decode(encoded['input_ids'])
    print(f"Decoded text: {decoded}")
    
    # Save vocabulary
    save_path = 'tokenizers/vocab.json'
    tokenizer.save_vocab(save_path)
    print(f"\nVocabulary size: {tokenizer.vocab_size}")
