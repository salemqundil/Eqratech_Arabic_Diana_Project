#!/usr/bin/env python3
"""
Fix indentation issues in engine files after metadata insertion.
Converts tabs to spaces (4 spaces per tab).
"""

import os
from pathlib import Path

def fix_indentation(file_path: Path):
    """Fix mixed tabs/spaces indentation in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace tabs with 4 spaces
        fixed_content = content.replace('\t', '    ')
        
        if fixed_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✅ Fixed: {file_path}")
            return True
        else:
            print(f"⏭️  No tabs: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {file_path} - {e}")
        return False

def main():
    """Fix indentation in all engine files."""
    print("=" * 80)
    print("🔧 FIXING INDENTATION IN ENGINE FILES")
    print("=" * 80)
    print()
    
    src_engines = Path('src/engines')
    py_files = list(src_engines.rglob('*.py'))
    
    fixed = 0
    skipped = 0
    
    for py_file in py_files:
        if py_file.name == '__init__.py':
            continue
        
        if fix_indentation(py_file):
            fixed += 1
        else:
            skipped += 1
    
    print()
    print("=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"Total files processed: {len(py_files) - len(list(src_engines.rglob('__init__.py')))}")
    print(f"✅ Fixed: {fixed}")
    print(f"⏭️  Already OK: {skipped}")

if __name__ == '__main__':
    main()
