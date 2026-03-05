#!/usr/bin/env python3
"""
Clean and unify awzan_merged_final.csv
- Remove duplicates
- Sort by wazn (الوزن)
- Normalize Arabic text
- Ensure consistent encoding (UTF-8)
"""

import csv
from pathlib import Path
from typing import List, Dict
import unicodedata

def normalize_arabic(text: str) -> str:
    """Normalize Arabic text to NFC form"""
    if not text:
        return ""
    # Normalize to NFC (Canonical Composition)
    normalized = unicodedata.normalize('NFC', text.strip())
    return normalized

def clean_csv(input_path: Path, output_path: Path):
    """Clean and unify the CSV file"""
    
    # Read all rows
    rows: List[Dict[str, str]] = []
    seen_wazn = set()
    duplicates = 0
    
    print(f"📖 قراءة الملف: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        print(f"الأعمدة: {fieldnames}")
        
        for i, row in enumerate(reader, 1):
            # Normalize all fields
            normalized_row = {
                key: normalize_arabic(value) 
                for key, value in row.items()
            }
            
            wazn = normalized_row.get('الوزن', '').strip()
            
            # Skip empty wazn
            if not wazn:
                print(f"⚠️  السطر {i}: وزن فارغ - تم التخطي")
                continue
            
            # Skip duplicates
            if wazn in seen_wazn:
                duplicates += 1
                print(f"⚠️  السطر {i}: وزن مكرر '{wazn}' - تم التخطي")
                continue
            
            seen_wazn.add(wazn)
            rows.append(normalized_row)
    
    print(f"\n📊 الإحصائيات:")
    print(f"  الأوزان الفريدة: {len(rows)}")
    print(f"  المكررات المحذوفة: {duplicates}")
    
    # Sort by wazn (Arabic alphabetical)
    print(f"\n🔤 ترتيب الأوزان...")
    rows.sort(key=lambda x: x.get('الوزن', ''))
    
    # Write to output
    print(f"\n💾 حفظ الملف: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, row in enumerate(rows, 1):
            # Re-add serial number
            row['ser'] = str(i)
            writer.writerow(row)
    
    print(f"\n✅ تم! عدد الأوزان النهائي: {len(rows)}")
    
    return len(rows)

if __name__ == '__main__':
    # Paths
    project_root = Path(__file__).resolve().parents[1]
    input_csv = project_root / 'data' / 'awzan_merged_final.csv'
    backup_csv = project_root / 'data' / 'awzan_merged_final.csv.backup'
    temp_csv = project_root / 'data' / 'awzan_merged_final.csv.tmp'
    
    # Check input exists
    if not input_csv.exists():
        print(f"❌ الملف غير موجود: {input_csv}")
        exit(1)
    
    # Backup original
    print(f"💾 نسخ احتياطي: {backup_csv}")
    import shutil
    shutil.copy2(input_csv, backup_csv)
    
    # Clean and save to temp
    count = clean_csv(input_csv, temp_csv)
    
    # Replace original
    print(f"\n🔄 استبدال الملف الأصلي...")
    shutil.move(temp_csv, input_csv)
    
    print(f"\n🎉 انتهى! الملف النظيف: {input_csv}")
    print(f"   النسخة الاحتياطية: {backup_csv}")
