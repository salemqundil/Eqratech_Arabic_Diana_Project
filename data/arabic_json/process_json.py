#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to extract الأمثلة from JSON file and add to CSV files
"""

import json
import csv
import re
import os

def remove_diacritics(text):
    """Remove Arabic diacritics (tashkeel) from text"""
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

def process_json_to_csv(json_path, csv_path, csv_no_tashkeel_path):
    """Process JSON file and create CSV files"""
    
    # Read JSON file
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Prepare data for CSV
    rows = []
    rows_no_tashkeel = []
    
    for item in data:
        amthila = item.get('الأمثلة', '').strip()
        
        # Skip empty entries
        if not amthila:
            continue
        
        # Add to rows with tashkeel
        rows.append([amthila])
        
        # Add to rows without tashkeel
        amthila_no_tashkeel = remove_diacritics(amthila)
        rows_no_tashkeel.append([amthila_no_tashkeel])
    
    # Write to CSV with tashkeel (overwrite existing)
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['الأمثلة'])  # Header
        writer.writerows(rows)
    
    # Write to CSV without tashkeel
    with open(csv_no_tashkeel_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['الأمثلة'])  # Header
        writer.writerows(rows_no_tashkeel)
    
    print(f"✓ Processed {len(rows)} entries")
    print(f"✓ Created {csv_path}")
    print(f"✓ Created {csv_no_tashkeel_path}")

if __name__ == '__main__':
    # File paths
    json_file = '2/المبنيات من الأسماء والأدوات /الفصل الأول/اسم الإستفهام/الاستفهام (أقسام أدوات الاستفهام).json'
    csv_file = 'test-corpus.csv'
    csv_no_tashkeel_file = 'test-corpus-no-tashkeel.csv'
    
    process_json_to_csv(json_file, csv_file, csv_no_tashkeel_file)

