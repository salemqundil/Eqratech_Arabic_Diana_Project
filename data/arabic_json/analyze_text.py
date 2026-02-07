#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to perform morphological and syntactic analysis on Arabic texts
"""

import csv
import re
import sys
import os
from typing import List, Dict, Tuple

# Import masaq segmenter
sys.path.append('/Users/husseinhiyassat/masaq/masaq_engine')
try:
    from segmenter import ArabicSegmenter
    segmenter = ArabicSegmenter()
    MASQ_AVAILABLE = True
except ImportError:
    print("Warning: masaq segmenter not found, using basic analysis")
    MASQ_AVAILABLE = False
    segmenter = None

# Arabic question words and particles
QUESTION_WORDS = ['من', 'ما', 'ماذا', 'متى', 'أيان', 'أين', 'أنى', 'كم', 'كيف', 'أي', 'هل']
VERB_PREFIXES = ['أ', 'ت', 'ن', 'ي', 'ت', 'ي', 'ن']
VERB_SUFFIXES = ['ت', 'نا', 'تم', 'تن', 'وا', 'ن', 'ا', 'ي', 'ك', 'كم', 'كن', 'ه', 'ها', 'هم', 'هن']

def tokenize_arabic(text: str) -> List[str]:
    """Tokenize Arabic text into words"""
    # Remove punctuation except Arabic question mark
    text = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\s؟]', '', text)
    # Split by whitespace
    words = text.split()
    # Filter empty strings
    words = [w.strip() for w in words if w.strip()]
    return words

def detect_sentence_type(text: str) -> str:
    """Detect if sentence is nominal (اسمية) or verbal (فعلية)"""
    words = tokenize_arabic(text)
    if not words:
        return "غير محدد"
    
    # Check for question words at the beginning
    first_word = words[0]
    if first_word in QUESTION_WORDS:
        # Check if followed by a verb (verbal sentence)
        if len(words) > 1:
            second_word = words[1]
            # Simple heuristic: if second word starts with verb prefixes, it's likely a verb
            if any(second_word.startswith(prefix) for prefix in VERB_PREFIXES):
                return "فعلية"
        return "اسمية"
    
    # Check if sentence starts with a verb (common verb patterns)
    # Arabic verbs often start with certain letters
    verb_indicators = ['وضع', 'تعلم', 'انتهت', 'تسمع', 'يعقد', 'أصبحت', 'أعجبك', 'حضرت']
    for indicator in verb_indicators:
        if indicator in text:
            return "فعلية"
    
    # Default to nominal if starts with noun-like patterns
    return "اسمية"

def extract_basic_root(word: str) -> str:
    """Extract root using masaq segmenter if available, otherwise use basic method"""
    original_word = word
    
    # Remove question mark and punctuation
    word_clean = word.replace('؟', '').replace('?', '').strip()
    
    # Use masaq segmenter if available
    if MASQ_AVAILABLE and segmenter:
        try:
            result = segmenter.segment_word(word_clean)
            # Extract stem from segments
            for seg in result.get('Segments', []):
                if seg.get('Morph_Type') == 'Stem':
                    stem = seg.get('Segmented_Word', '')
                    if stem and len(stem) >= 2:
                        return stem
        except Exception:
            pass  # Fall back to basic method
    
    # Fallback to basic root extraction
    word = word_clean
    
    # Remove common prefixes (definite article, prepositions, etc.)
    prefixes = ['ال', 'و', 'ف', 'ب', 'ل', 'ك', 'ت', 'ن', 'ي', 'أ', 'ا']
    for prefix in sorted(prefixes, key=len, reverse=True):
        if word.startswith(prefix) and len(word) > len(prefix) + 2:
            word = word[len(prefix):]
            break
    
    # Remove common suffixes
    suffixes = ['ة', 'ات', 'ين', 'ون', 'ان', 'كم', 'كن', 'ها', 'هم', 'هن', 'ت', 'ا', 'ن']
    for suffix in sorted(suffixes, key=len, reverse=True):
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            word = word[:-len(suffix)]
            break
    
    # For very short words, return as is
    if len(word) <= 2:
        return original_word.replace('؟', '').replace('?', '').strip()
    
    # Try to extract 3-letter root (common in Arabic)
    if len(word) == 3:
        return word
    elif len(word) == 4:
        # Take first, second, and last
        return word[0] + word[1] + word[-1]
    elif len(word) == 5:
        # Take first, third, and last
        return word[0] + word[2] + word[-1]
    elif len(word) >= 6:
        # Take first, middle-ish, and last
        mid = len(word) // 2
        return word[0] + word[mid] + word[-1]
    
    return word[:3] if len(word) >= 3 else word

def classify_word_type(word: str) -> str:
    """Classify word as اسم (noun), فعل (verb), or حرف (particle)"""
    # Clean word from punctuation
    clean_word = word.replace('؟', '').replace('?', '').strip()
    
    if not clean_word:
        return "حرف"
    
    # Question words classification
    if clean_word in QUESTION_WORDS:
        if clean_word in ['هل']:
            return "حرف"
        else:
            return "اسم"
    
    # Common particles (prepositions and conjunctions)
    particles = ['في', 'من', 'إلى', 'على', 'عن', 'مع', 'ب', 'ل', 'ك', 'و', 'ف', 'ثم', 'لك', 'ذا', 'هذا', 'الذي']
    if clean_word in particles:
        return "حرف"
    
    # Check for verb patterns (common verb roots and forms)
    verb_patterns = ['وضع', 'تعلم', 'انته', 'سمع', 'عقد', 'صبح', 'عجب', 'حضر', 'أمر']
    for pattern in verb_patterns:
        if pattern in clean_word:
            return "فعل"
    
    # Check for verb prefixes (indicating present tense or imperative)
    verb_prefixes_indicators = ['ي', 'ت', 'ن', 'أ']
    if clean_word.startswith(tuple(verb_prefixes_indicators)) and len(clean_word) > 3:
        # Additional check: if it looks like a verb structure
        if not clean_word.startswith('ال'):  # Not a definite noun
            return "فعل"
    
    # Check for verb suffixes (indicating past tense or pronouns)
    verb_suffixes_indicators = ['ت', 'نا', 'تم', 'تن', 'وا', 'ا']
    if clean_word.endswith(tuple(verb_suffixes_indicators)) and len(clean_word) > 3:
        return "فعل"
    
    # Words ending with typical noun markers
    noun_markers = ['ة', 'ات', 'ين', 'ون']
    if any(clean_word.endswith(marker) for marker in noun_markers):
        return "اسم"
    
    # Default to noun
    return "اسم"

def analyze_text(text: str) -> Dict[str, any]:
    """Perform comprehensive analysis on Arabic text using masaq segmenter"""
    if not text or not text.strip():
        return {
            'word_count': 0,
            'sentence_type': 'غير محدد',
            'words': [],
            'roots': [],
            'word_types': [],
            'has_question_mark': False,
            'segments': []
        }
    
    # Tokenize
    words = tokenize_arabic(text)
    
    # Extract roots and segments using masaq if available
    roots = []
    segments_info = []
    
    if MASQ_AVAILABLE and segmenter:
        for word in words:
            try:
                # Segment the word
                result = segmenter.segment_word(word)
                segments_info.append(result)
                
                # Extract stem (root) from segments
                stem = None
                for seg in result.get('Segments', []):
                    if seg.get('Morph_Type') == 'Stem':
                        stem = seg.get('Segmented_Word', '')
                        break
                
                if stem and len(stem) >= 2:
                    roots.append(stem)
                else:
                    roots.append(extract_basic_root(word))
            except Exception:
                # Fallback to basic method
                roots.append(extract_basic_root(word))
                segments_info.append(None)
    else:
        # Use basic root extraction
        roots = [extract_basic_root(word) for word in words]
        segments_info = [None] * len(words)
    
    # Classify word types
    word_types = [classify_word_type(word) for word in words]
    
    # Detect sentence type
    sentence_type = detect_sentence_type(text)
    
    # Check for question mark
    has_question_mark = '؟' in text or '?' in text
    
    return {
        'word_count': len(words),
        'sentence_type': sentence_type,
        'words': ' | '.join(words),
        'roots': ' | '.join(roots),
        'word_types': ' | '.join(word_types),
        'has_question_mark': has_question_mark,
        'unique_roots_count': len(set(roots)),
        'segments': segments_info
    }

def process_csv(input_file: str, output_file: str):
    """Process CSV file and add analysis results"""
    
    # Read input CSV
    rows = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    
    # Analyze each row
    analyzed_rows = []
    for row in rows:
        adah = row.get('الأداة', '').strip()
        amthila = row.get('الأمثلة', '').strip()
        
        # Analyze the example text
        analysis = analyze_text(amthila)
        
        # Create new row with analysis
        new_row = {
            'الأداة': adah,
            'الأمثلة': amthila,
            'عدد_الكلمات': analysis['word_count'],
            'نوع_الجملة': analysis['sentence_type'],
            'الكلمات': analysis['words'],
            'الجذور': analysis['roots'],
            'أنواع_الكلمات': analysis['word_types'],
            'عدد_الجذور_المميزة': analysis['unique_roots_count'],
            'يحتوي_علامة_استفهام': 'نعم' if analysis['has_question_mark'] else 'لا'
        }
        
        analyzed_rows.append(new_row)
    
    # Write output CSV
    if analyzed_rows:
        fieldnames = list(analyzed_rows[0].keys())
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(analyzed_rows)
    
    print(f"✓ Processed {len(analyzed_rows)} entries")
    print(f"✓ Created {output_file}")

if __name__ == '__main__':
    input_file = 'test-corpus-no-tashkeel.csv'
    output_file = 'test-corpus-analyzed.csv'
    
    process_csv(input_file, output_file)

