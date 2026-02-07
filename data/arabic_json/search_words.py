#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to read first sentence from CSV, search each word in JSON files,
and print information if found
"""

import csv
import json
import os
import re
import sys
from pathlib import Path

# Import masaq segmenter
sys.path.append('/Users/husseinhiyassat/masaq/masaq_engine')
try:
    from segmenter import ArabicSegmenter
    segmenter = ArabicSegmenter()
    MASQ_AVAILABLE = True
except ImportError:
    print("Warning: masaq segmenter not found, using simple tokenization")
    MASQ_AVAILABLE = False
    segmenter = None

def remove_diacritics(text: str) -> str:
    """Remove Arabic diacritics (tashkeel) from text"""
    if not text:
        return text
    # Arabic diacritical marks
    diacritics = [
        '\u064B',  # Tanwin Fatha
        '\u064C',  # Tanwin Damma
        '\u064D',  # Tanwin Kasra
        '\u064E',  # Fatha
        '\u064F',  # Damma
        '\u0650',  # Kasra
        '\u0651',  # Shadda
        '\u0652',  # Sukun
        '\u0653',  # Madda above
        '\u0654',  # Hamza above
        '\u0655',  # Hamza below
        '\u0670',  # Superscript Alef
    ]
    for diacritic in diacritics:
        text = text.replace(diacritic, '')
    return text

def segment_arabic(text: str) -> list:
    """Segment Arabic text into words using masaq segmenter, returns list of tuples (original, stem)"""
    if not text:
        return []
    
    if MASQ_AVAILABLE and segmenter:
        print(f"✓ Using masaq segmenter for: {text[:50]}...")
        # Use masaq segmenter to segment each word
        words = text.split()
        segmented_words = []
        
        for word in words:
            # Remove punctuation except Arabic question mark
            word_clean = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF؟]', '', word)
            if not word_clean:
                continue
            
            # Segment the word using masaq
            try:
                result = segmenter.segment_word(word_clean)
                
                # Extract stem from segments
                stem = None
                for seg in result.get('Segments', []):
                    if seg.get('Morph_Type') == 'Stem':
                        stem = seg.get('Segmented_Word', '')
                        break
                
                # Use stem if found and valid, otherwise use word without diacritics
                word_no_diacritics = remove_diacritics(word_clean)
                if stem and len(stem) >= 2:
                    # Return tuple: (original_word, stem)
                    print(f"  Segmented: '{word_clean}' -> stem: '{stem}'")
                    segmented_words.append((word_no_diacritics, stem))
                else:
                    # Fallback: use word without diacritics
                    print(f"  No stem found for: '{word_clean}', using: '{word_no_diacritics}'")
                    if word_no_diacritics:
                        segmented_words.append((word_no_diacritics, word_no_diacritics))
            except Exception as e:
                # If segmentation fails, use simple tokenization
                print(f"  Error segmenting '{word_clean}': {e}")
                word_no_diacritics = remove_diacritics(word_clean)
                if word_no_diacritics:
                    segmented_words.append((word_no_diacritics, word_no_diacritics))
        
        return segmented_words
    else:
        print("⚠ Using simple tokenization (masaq not available)")
        # Fallback to simple tokenization
        text = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\s؟]', '', text)
        words = text.split()
        words = [w.strip().replace('؟', '').replace('?', '') for w in words if w.strip()]
        # Return as tuples for consistency
        return [(w, w) for w in words]

def search_word_in_json(word: str, json_path: str, context_words: list = None, full_sentence: str = None) -> list:
    """Search for word in a JSON file and return matching entries with context scoring"""
    results = []
    context_words = context_words or []
    full_sentence = full_sentence or ""
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both list and dict formats
        if isinstance(data, dict):
            data = [data]
        
        for item in data:
            if not isinstance(item, dict):
                continue
            
            # Search in all fields
            found_in_fields = {}
            context_score = 0
            has_full_sentence = False
            has_adah_field = False
            adah_matches_word = False
            
            for key, value in item.items():
                if isinstance(value, str):
                    # Search with and without diacritics
                    value_no_diacritics = remove_diacritics(value)
                    word_no_diacritics = remove_diacritics(word)
                    
                    # Check if word matches (with or without diacritics)
                    word_found = word in value or word_no_diacritics in value_no_diacritics
                    
                    # Check if word is in الأداة field and matches exactly
                    if key == 'الأداة' and word_found:
                        has_adah_field = True
                        # Remove diacritics from both for comparison
                        adah_value_clean = remove_diacritics(value.strip())
                        word_clean = remove_diacritics(word.strip())
                        
                        # Check if the word matches the الأداة value exactly
                        # First, check if the entire الأداة field is just the word (exact match)
                        if word_clean == adah_value_clean:
                            adah_matches_word = True
                            found_in_fields[key] = value
                        else:
                            # Split by common separators (comma, semicolon, etc.) to check each tool separately
                            # Also split by spaces to check individual words
                            adah_parts = re.split(r'[،,؛;\s]+', adah_value_clean)
                            
                            # Check for exact match in any part
                            for part in adah_parts:
                                part_clean = part.strip()
                                # Exact match - the word must be exactly the tool
                                if word_clean == part_clean:
                                    adah_matches_word = True
                                    found_in_fields[key] = value
                                    break
                                
                                # Check if word is at the start or end of the part (for compound tools)
                                # But only if the part is short (max 3 chars more than word) and word is significant
                                if len(part_clean) <= len(word_clean) + 3 and len(word_clean) >= 2:
                                    if part_clean.startswith(word_clean) or part_clean.endswith(word_clean):
                                        # Additional check: word should be a significant part (at least 70% of part)
                                        if len(word_clean) >= len(part_clean) * 0.7:
                                            adah_matches_word = True
                                            found_in_fields[key] = value
                                            break
                    # Only consider matches in الأداة field
                    # Other fields (الوصف، الأمثلة، etc.) are not relevant for word matching
                    # We only search in الأداة field to find the actual tool/word
                    
                    # Check context: if other words from sentence are also in this field
                    if context_words:
                        for ctx_word in context_words:
                            if ctx_word != word and ctx_word in value:
                                context_score += 1
                    
                    # Check if full sentence matches in الأمثلة field
                    if key == 'الأمثلة' and full_sentence:
                        # Remove diacritics from both for comparison
                        value_clean = ' '.join(remove_diacritics(value.replace('؟', '').replace('?', '')).split())
                        sentence_clean = ' '.join(remove_diacritics(full_sentence.replace('؟', '').replace('?', '')).split())
                        
                        # Check if sentences match (exact or most words match)
                        if value_clean == sentence_clean:
                            has_full_sentence = True
                        elif len(sentence_clean) > 0:
                            # Check if most words from sentence are in the example
                            sentence_words = set(sentence_clean.split())
                            example_words = set(value_clean.split())
                            common_words = sentence_words.intersection(example_words)
                            if len(common_words) >= len(sentence_words) * 0.7:  # 70% match
                                has_full_sentence = True
            
            # Only add to results if word is found in الأداة field
            # We only search in الأداة field to find the actual tool/word
            if found_in_fields and 'الأداة' in found_in_fields and adah_matches_word:
                result = {
                    'file': json_path,
                    'fields': found_in_fields,
                    'context_score': context_score,
                    'has_full_sentence': has_full_sentence,
                    'has_adah_field': has_adah_field,
                    'adah_matches_word': adah_matches_word
                }
                results.append(result)
    
    except (json.JSONDecodeError, UnicodeDecodeError, Exception) as e:
        # Skip files that can't be read
        pass
    
    return results

def search_word_in_all_json(word: str, base_dir: str, context_words: list = None, full_sentence: str = None) -> list:
    """Search for word in all JSON files in directory with context"""
    all_results = []
    context_words = context_words or []
    full_sentence = full_sentence or ""
    
    # Find all JSON files
    json_files = list(Path(base_dir).rglob('*.json'))
    
    for json_file in json_files:
        results = search_word_in_json(word, str(json_file), context_words, full_sentence)
        all_results.extend(results)
    
    # Sort by context relevance (highest priority first): 
    # 1. Word matches exactly in الأداة field AND has full sentence match
    # 2. Word matches in الأداة field
    # 3. Has full sentence in الأمثلة AND word is in الأداة
    # 4. Has الأداة field
    # 5. Higher context score (more words from sentence found)
    # Filter: Prefer results where word is in الأداة field
    results_with_adah = [r for r in all_results if r.get('adah_matches_word', False)]
    results_without_adah = [r for r in all_results if not r.get('adah_matches_word', False)]
    
    # If we have results with الأداة, use those first, then others
    if results_with_adah:
        all_results = results_with_adah + results_without_adah
    
    all_results.sort(key=lambda x: (
        x.get('adah_matches_word', False) and x.get('has_full_sentence', False),
        x.get('adah_matches_word', False),
        x.get('has_full_sentence', False),
        x.get('has_adah_field', False),
        x.get('context_score', 0)
    ), reverse=True)
    
    return all_results

def format_results(results: list) -> str:
    """Format search results for display"""
    if not results:
        return ""
    
    output = []
    seen_files = set()  # To avoid duplicate file entries
    
    for result in results:
        file_name = os.path.basename(result['file'])
        file_key = (file_name, tuple(sorted(result['fields'].keys())))
        
        if file_key not in seen_files:
            seen_files.add(file_key)
            output.append(f"  📄 ملف: {file_name}")
            
            for field, value in result['fields'].items():
                # Skip empty values
                if not value or not value.strip():
                    continue
                # Truncate long values
                if len(value) > 150:
                    value = value[:150] + "..."
                output.append(f"    • {field}: {value}")
            output.append("")
    
    return "\n".join(output)

def main():
    # Read all rows from CSV
    input_csv = 'test-corpus-no-tashkeel.csv'
    output_csv = 'test-corpus-analyzed.csv'
    
    # Delete old output file to start fresh
    if os.path.exists(output_csv):
        os.remove(output_csv)
    
    rows = []
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sentence = row.get('الأمثلة', '').strip()
            if sentence:
                rows.append(sentence)
    
    if not rows:
        print("لا توجد بيانات في الملف")
        return
    
    # Base directory for JSON files
    base_dir = '.'
    
    # Prepare output data
    output_rows = []
    
    # Process each row interactively
    for idx, sentence in enumerate(rows, 1):
        print(f"\n{'=' * 60}")
        print(f"السطر {idx}: {sentence}")
        print('=' * 60)
        
        # Tokenize into words using segmenter
        word_pairs = segment_arabic(sentence)
        
        # Store results for this sentence
        sentence_results = []
        
        # Get all words (original and stems) for context
        all_words = []
        for orig, stem in word_pairs:
            all_words.append(orig)
            if stem != orig:
                all_words.append(stem)
        
        # Search for each word with context (other words in sentence)
        for original_word, stem_word in word_pairs:
            # Try original word first, then stem
            search_words = [original_word]
            if stem_word != original_word and len(stem_word) >= 2:
                search_words.append(stem_word)
            
            found = False
            best_result = None
            
            for search_word in search_words:
                print(f"\n🔍 البحث عن: '{search_word}' (من '{original_word}')")
                print("-" * 60)
                
                # Pass context words (other words in the sentence) and full sentence for better matching
                results = search_word_in_all_json(search_word, base_dir, context_words=all_words, full_sentence=sentence)
                
                if results:
                    found = True
                    best_result = results[0]
                    print(format_results(results))
                    break
            
            if not found:
                print(f"  {original_word} (stem: {stem_word})")
            
            word = original_word  # Use original word for display
            
            if found and best_result:
                # Get the best matching file (first in sorted results)
                file_path = best_result['file']
                
                # Convert to relative path
                try:
                    rel_path = os.path.relpath(file_path, base_dir)
                except:
                    rel_path = file_path
                
                # Remove .json extension
                if rel_path.endswith('.json'):
                    rel_path = rel_path[:-5]  # Remove .json
                
                file_path_str = rel_path if rel_path else ""
                
                sentence_results.append({
                    'word': word,
                    'found': True,
                    'file_path': file_path_str
                })
            else:
                sentence_results.append({
                    'word': word,
                    'found': False,
                    'file_path': ""
                })
        
        # Store row data - each word in a separate row
        # First row: sentence with first word
        # Other rows: empty sentence column, just word and result
        for i, r in enumerate(sentence_results):
            word = r['word']
            if r['found']:
                file_path = r.get('file_path', '')
                if file_path and file_path.strip():
                    result = f"✓({file_path})"
                else:
                    result = "✓"
            else:
                result = "✗"
            
            # Debug: print what we're writing
            print(f"\n📝 معالجة: {word} -> {result}")
            
            # Add each word as a separate row
            # First word gets the sentence, others get empty string
            output_rows.append({
                'الأمثلة': sentence if i == 0 else '',
                'الكلمة': word,
                'نتائج_البحث': result
            })
        
        # Ask if user wants to continue to next row
        if idx < len(rows):
            while True:
                response = input(f"\nهل تريد الانتقال للسطر التالي؟ (نعم/لا): ").strip().lower()
                if response in ['نعم', 'ن', 'yes', 'y', '']:
                    break
                elif response in ['لا', 'ل', 'no', 'n']:
                    print("تم الإنهاء.")
                    break
                else:
                    print("الرجاء الإجابة بـ 'نعم' أو 'لا'")
            
            if response in ['لا', 'ل', 'no', 'n']:
                break
        else:
            print("\nتم الانتهاء من جميع السطور.")
    
    # Write all results to CSV at once
    if output_rows:
        try:
            with open(output_csv, 'w', encoding='utf-8', newline='') as f:
                fieldnames = ['الأمثلة', 'الكلمة', 'نتائج_البحث']
                writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
                writer.writeheader()
                for row in output_rows:
                    writer.writerow(row)
            
            print(f"\n✓ تم حفظ {len(output_rows)} سطر في {output_csv}")
        except Exception as e:
            print(f"\n✗ خطأ في كتابة CSV: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()

