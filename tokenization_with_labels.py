"""
Tokenization with Labels Utility

This module provides various methods to add labels to tokenized data for supervised learning.
It demonstrates different approaches for integrating labels from various sources.

Usage Examples:
    1. Labels in a separate file (CSV, JSON, TXT)
    2. Labels embedded in the same file with data
    3. Labels derived from data structure or metadata
"""

import json
import csv
from typing import List, Dict, Union, Tuple
from pathlib import Path


class TokenizationWithLabels:
    """
    A utility class for tokenizing text data and associating labels for supervised learning.
    """
    
    def __init__(self, tokenizer=None):
        """
        Initialize the tokenization utility.
        
        Args:
            tokenizer: Optional tokenizer object (e.g., from transformers library)
                      If None, uses simple whitespace tokenization
        """
        self.tokenizer = tokenizer
    
    def tokenize_with_labels_from_separate_file(
        self, 
        data_file: str, 
        labels_file: str,
        data_column: str = None,
        label_column: str = None
    ) -> List[Dict[str, Union[str, List, int]]]:
        """
        Tokenize data and add labels from a separate file.
        
        This method is useful when you have:
        - Data in one file (e.g., quran_data.txt or quran_data.csv)
        - Labels in another file (e.g., labels.txt or labels.csv)
        
        Both files should have the same number of lines/rows.
        
        Args:
            data_file: Path to the data file
            labels_file: Path to the labels file
            data_column: Column name if data_file is CSV (optional)
            label_column: Column name if labels_file is CSV (optional)
            
        Returns:
            List of dictionaries with 'text', 'tokens', and 'label' keys
            
        Example:
            >>> tokenizer = TokenizationWithLabels()
            >>> result = tokenizer.tokenize_with_labels_from_separate_file(
            ...     'quran_data.txt', 
            ...     'labels.txt'
            ... )
        """
        # Read data
        data_lines = self._read_file(data_file, data_column)
        
        # Read labels
        label_lines = self._read_file(labels_file, label_column)
        
        # Verify matching lengths
        if len(data_lines) != len(label_lines):
            raise ValueError(
                f"Data and labels files have different lengths: "
                f"{len(data_lines)} vs {len(label_lines)}"
            )
        
        # Tokenize and combine
        tokenized_data = []
        for text, label in zip(data_lines, label_lines):
            tokens = self._tokenize_text(text)
            tokenized_data.append({
                'text': text,
                'tokens': tokens,
                'label': label
            })
        
        return tokenized_data
    
    def tokenize_with_embedded_labels(
        self, 
        data_file: str,
        text_column: str,
        label_column: str,
        file_format: str = 'csv'
    ) -> List[Dict[str, Union[str, List, int]]]:
        """
        Tokenize data where labels are in the same file as the text.
        
        This method is useful when you have a structured file (CSV, JSON, etc.)
        with both text and labels in different columns/fields.
        
        Args:
            data_file: Path to the data file
            text_column: Name of the column/field containing text
            label_column: Name of the column/field containing labels
            file_format: Format of the file ('csv', 'json', 'tsv')
            
        Returns:
            List of dictionaries with 'text', 'tokens', and 'label' keys
            
        Example:
            >>> tokenizer = TokenizationWithLabels()
            >>> result = tokenizer.tokenize_with_embedded_labels(
            ...     'quran_with_labels.csv',
            ...     text_column='verse',
            ...     label_column='category'
            ... )
        """
        data_path = Path(data_file)
        tokenized_data = []
        
        if file_format == 'csv' or file_format == 'tsv':
            delimiter = '\t' if file_format == 'tsv' else ','
            with open(data_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                for row in reader:
                    text = row[text_column]
                    label = row[label_column]
                    tokens = self._tokenize_text(text)
                    tokenized_data.append({
                        'text': text,
                        'tokens': tokens,
                        'label': label
                    })
        
        elif file_format == 'json':
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    text = item[text_column]
                    label = item[label_column]
                    tokens = self._tokenize_text(text)
                    tokenized_data.append({
                        'text': text,
                        'tokens': tokens,
                        'label': label
                    })
        
        return tokenized_data
    
    def tokenize_with_label_mapping(
        self,
        data_file: str,
        label_mapping: Dict[int, Union[str, int]],
        data_column: str = None
    ) -> List[Dict[str, Union[str, List, int]]]:
        """
        Tokenize data and assign labels based on line/row index.
        
        This method is useful when you have a mapping of line numbers to labels.
        
        Args:
            data_file: Path to the data file
            label_mapping: Dictionary mapping line index to label
            data_column: Column name if data_file is CSV (optional)
            
        Returns:
            List of dictionaries with 'text', 'tokens', and 'label' keys
            
        Example:
            >>> tokenizer = TokenizationWithLabels()
            >>> label_map = {0: 'meccan', 1: 'medinan', 2: 'meccan', ...}
            >>> result = tokenizer.tokenize_with_label_mapping(
            ...     'quran_data.txt',
            ...     label_map
            ... )
        """
        # Read data
        data_lines = self._read_file(data_file, data_column)
        
        # Tokenize and add labels
        tokenized_data = []
        for idx, text in enumerate(data_lines):
            tokens = self._tokenize_text(text)
            label = label_mapping.get(idx, None)
            tokenized_data.append({
                'text': text,
                'tokens': tokens,
                'label': label
            })
        
        return tokenized_data
    
    def tokenize_with_pattern_based_labels(
        self,
        data_file: str,
        label_function,
        data_column: str = None
    ) -> List[Dict[str, Union[str, List, int]]]:
        """
        Tokenize data and assign labels based on a pattern or function.
        
        This method is useful when labels can be derived from the text itself
        using rules, patterns, or custom logic.
        
        Args:
            data_file: Path to the data file
            label_function: Function that takes text and returns a label
            data_column: Column name if data_file is CSV (optional)
            
        Returns:
            List of dictionaries with 'text', 'tokens', and 'label' keys
            
        Example:
            >>> def get_label(text):
            ...     # Derive label from text properties
            ...     return 'long' if len(text) > 100 else 'short'
            >>> 
            >>> tokenizer = TokenizationWithLabels()
            >>> result = tokenizer.tokenize_with_pattern_based_labels(
            ...     'quran_data.txt',
            ...     get_label
            ... )
        """
        # Read data
        data_lines = self._read_file(data_file, data_column)
        
        # Tokenize and add labels
        tokenized_data = []
        for text in data_lines:
            tokens = self._tokenize_text(text)
            label = label_function(text)
            tokenized_data.append({
                'text': text,
                'tokens': tokens,
                'label': label
            })
        
        return tokenized_data
    
    def _read_file(self, file_path: str, column: str = None) -> List[str]:
        """
        Read lines from a file.
        
        Args:
            file_path: Path to the file
            column: Column name if file is CSV (optional)
            
        Returns:
            List of text lines
        """
        path = Path(file_path)
        
        if path.suffix == '.csv':
            with open(path, 'r', encoding='utf-8') as f:
                if column:
                    reader = csv.DictReader(f)
                    return [row[column] for row in reader]
                else:
                    reader = csv.reader(f)
                    return [row[0] if row else '' for row in reader]
        
        elif path.suffix == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if column and isinstance(data, list) and isinstance(data[0], dict):
                    return [item[column] for item in data]
                return data if isinstance(data, list) else [str(data)]
        
        else:  # Assume plain text file
            with open(path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
    
    def _tokenize_text(self, text: str) -> List[str]:
        """
        Tokenize a text string.
        
        Args:
            text: Input text to tokenize
            
        Returns:
            List of tokens
        """
        if self.tokenizer:
            # Use provided tokenizer (e.g., from transformers)
            return self.tokenizer.tokenize(text)
        else:
            # Simple whitespace tokenization
            return text.split()
    
    def save_tokenized_data(
        self,
        tokenized_data: List[Dict],
        output_file: str,
        format: str = 'json'
    ):
        """
        Save tokenized data with labels to a file.
        
        Args:
            tokenized_data: List of tokenized data dictionaries
            output_file: Path to output file
            format: Output format ('json' or 'csv')
        """
        output_path = Path(output_file)
        
        if format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(tokenized_data, f, ensure_ascii=False, indent=2)
        
        elif format == 'csv':
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['text', 'tokens', 'label'])
                for item in tokenized_data:
                    writer.writerow([
                        item['text'],
                        ' '.join(item['tokens']),
                        item['label']
                    ])


def create_example_data_files():
    """
    Create example data files to demonstrate the different label integration methods.
    This function generates sample files that show how data and labels can be organized.
    """
    examples_dir = Path('examples')
    examples_dir.mkdir(exist_ok=True)
    
    # Example 1: Separate files
    with open(examples_dir / 'quran_data_example.txt', 'w', encoding='utf-8') as f:
        f.write('بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ\n')
        f.write('الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ\n')
        f.write('الرَّحْمَٰنِ الرَّحِيمِ\n')
    
    with open(examples_dir / 'labels_example.txt', 'w', encoding='utf-8') as f:
        f.write('basmala\n')
        f.write('praise\n')
        f.write('attribute\n')
    
    # Example 2: Embedded labels (CSV)
    with open(examples_dir / 'quran_with_labels_example.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['verse', 'category', 'surah'])
        writer.writerow(['بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ', 'basmala', 'al-fatiha'])
        writer.writerow(['الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ', 'praise', 'al-fatiha'])
        writer.writerow(['الرَّحْمَٰنِ الرَّحِيمِ', 'attribute', 'al-fatiha'])
    
    # Example 3: JSON format
    json_data = [
        {'verse': 'بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ', 'category': 'basmala', 'surah': 'al-fatiha'},
        {'verse': 'الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ', 'category': 'praise', 'surah': 'al-fatiha'},
        {'verse': 'الرَّحْمَٰنِ الرَّحِيمِ', 'category': 'attribute', 'surah': 'al-fatiha'}
    ]
    
    with open(examples_dir / 'quran_with_labels_example.json', 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    print(f"Example data files created in {examples_dir}")


if __name__ == '__main__':
    # Demonstrate usage
    print("Creating example data files...")
    create_example_data_files()
    
    print("\nExample usage demonstrations:\n")
    
    # Example 1: Separate files
    print("1. Tokenization with labels from separate files:")
    tokenizer = TokenizationWithLabels()
    try:
        result = tokenizer.tokenize_with_labels_from_separate_file(
            'examples/quran_data_example.txt',
            'examples/labels_example.txt'
        )
        print(f"   - Tokenized {len(result)} items")
        print(f"   - Sample: {result[0]}\n")
    except Exception as e:
        print(f"   Error: {e}\n")
    
    # Example 2: Embedded labels (CSV)
    print("2. Tokenization with embedded labels (CSV):")
    try:
        result = tokenizer.tokenize_with_embedded_labels(
            'examples/quran_with_labels_example.csv',
            text_column='verse',
            label_column='category'
        )
        print(f"   - Tokenized {len(result)} items")
        print(f"   - Sample: {result[0]}\n")
    except Exception as e:
        print(f"   Error: {e}\n")
    
    # Example 3: Embedded labels (JSON)
    print("3. Tokenization with embedded labels (JSON):")
    try:
        result = tokenizer.tokenize_with_embedded_labels(
            'examples/quran_with_labels_example.json',
            text_column='verse',
            label_column='category',
            file_format='json'
        )
        print(f"   - Tokenized {len(result)} items")
        print(f"   - Sample: {result[0]}\n")
    except Exception as e:
        print(f"   Error: {e}\n")
