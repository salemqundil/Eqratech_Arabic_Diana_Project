#!/usr/bin/env python3
"""
Populate LAYER, GROUP, and SUBGROUP metadata in all engine files.
Based on ENGINE_TAXONOMY.md classification.
"""

import os
from pathlib import Path

# Mapping: (file_path, LAYER, GROUP, SUBGROUP, GROUP_AR, SUBGROUP_AR)
ENGINE_METADATA = {
    # ============================================================================
    # LAYER 1: PHONOLOGY (3 engines)
    # ============================================================================
    'src/engines/phonology/phonemes_engine.py': (
        'EngineLayer.PHONOLOGY',
        '"1.1"',
        '"1.1.1"',
        '"الفونيمات الأساسية"',
        '"قائمة الفونيمات"'
    ),
    'src/engines/phonology/sound_engine.py': (
        'EngineLayer.PHONOLOGY',
        '"1.1"',
        '"1.1.1"',
        '"الفونيمات الأساسية"',
        '"قائمة الفونيمات"'
    ),
    'src/engines/phonology/aswat_muhdatha_engine.py': (
        'EngineLayer.PHONOLOGY',
        '"1.2"',
        '"1.2.1"',
        '"الأصوات المحدثة"',
        '"الصوتيات المعاصرة"'
    ),
    
    # ============================================================================
    # LAYER 2: MORPHOLOGY (22 engines)
    # ============================================================================
    
    # Group 2.1: Verbal Morphology
    'src/engines/morphology/verbs_engine.py': (
        'EngineLayer.MORPHOLOGY',
        '"2.1"',
        '"2.1.1"',
        '"صرف الأفعال"',
        '"الأفعال الأساسية"'
    ),
    'src/engines/morphology/afaal_khamsa_engine.py': (
        'EngineLayer.MORPHOLOGY',
        '"2.1"',
        '"2.1.1"',
        '"صرف الأفعال"',
        '"الأفعال الأساسية"'
    ),
    'src/engines/morphology/mabni_majhool_engine.py': (
        'EngineLayer.MORPHOLOGY',
        '"2.1"',
        '"2.1.2"',
        '"صرف الأفعال"',
        '"المبني للمجهول"'
    ),
    'src/engines/morphology/binaa_engine.py': (
        'EngineLayer.MORPHOLOGY',
        '"2.1"',
        '"2.1.3"',
        '"صرف الأفعال"',
        '"بناء الأفعال"'
    ),
    
    # Group 2.2: Participial Forms
    'src/engines/morphology/active_participle_engine.py': (
        'EngineLayer.MORPHOLOGY',
        '"2.2"',
        '"2.2.1"',
        '"صيغ المشاركة"',
        '"اسم الفاعل"'
    ),
    'src/engines/morphology/passive_participle_engine.py': (
        'EngineLayer.MORPHOLOGY',
        '"2.2"',
        '"2.2.2"',
        '"صيغ المشاركة"',
        '"اسم المفعول"'
    ),
    'src/engines/morphology/mubalagh_sigha_engine.py': (
        'EngineLayer.MORPHOLOGY',
        '"2.2"',
        '"2.2.3"',
        '"صيغ المشاركة"',
        '"صيغة المبالغة"'
    ),
    
    # Group 2.3: Derived Nouns
    'src/engines/morphology/masdar_sinai_engine.py': (
        'EngineLayer.MORPHOLOGY',
        '"2.3"',
        '"2.3.1"',
        '"الأسماء المشتقة"',
        '"المصادر الصناعية"'
    ),
    'src/engines/morphology/mimi_nouns_engine.py': (
        'EngineLayer.MORPHOLOGY',
        '"2.3"',
        '"2.3.2"',
        '"الأسماء المشتقة"',
        '"أسماء الآلة"'
    ),
    
    # Group 2.4: Comparative & Superlative
    'src/engines/morphology/superlative_engine.py': (
        'EngineLayer.MORPHOLOGY',
        '"2.4"',
        '"2.4.1"',
        '"المقارنة والتفضيل"',
        '"اسم التفضيل"'
    ),
    'src/engines/morphology/adjective_engine.py': (
        'EngineLayer.MORPHOLOGY',
        '"2.4"',
        '"2.4.2"',
        '"المقارنة والتفضيل"',
        '"الصفات"'
    ),
    'src/engines/morphology/ism_ala_engine.py': (
        'EngineLayer.MORPHOLOGY',
        '"2.4"',
        '"2.4.3"',
        '"المقارنة والتفضيل"',
        '"الصيغ الخاصة"'
    ),
    
    # Group 2.5: Defective Nouns
    'src/engines/morphology/ism_maqsor_engine.py': (
        'EngineLayer.MORPHOLOGY',
        '"2.5"',
        '"2.5.1"',
        '"الأسماء المعتلة"',
        '"الأسماء المقصورة"'
    ),
    'src/engines/morphology/ism_manqus_engine.py': (
        'EngineLayer.MORPHOLOGY',
        '"2.5"',
        '"2.5.2"',
        '"الأسماء المعتلة"',
        '"الأسماء المنقوصة"'
    ),
    'src/engines/morphology/ism_mamdod_engine.py': (
        'EngineLayer.MORPHOLOGY',
        '"2.5"',
        '"2.5.3"',
        '"الأسماء المعتلة"',
        '"الأسماء الممدودة"'
    ),
    
    # Group 2.6: Relational Morphology
    'src/engines/morphology/nisba_engine.py': (
        'EngineLayer.MORPHOLOGY',
        '"2.6"',
        '"2.6.1"',
        '"النسبة والإضافة"',
        '"النسبة"'
    ),
    
    # Group 2.9: Special Nouns
    'src/engines/morphology/ism_hay_a_engine.py': (
        'EngineLayer.MORPHOLOGY',
        '"2.9"',
        '"2.9.1"',
        '"الأسماء الخاصة"',
        '"أسماء الهيئة"'
    ),
    'src/engines/morphology/ism_marra_engine.py': (
        'EngineLayer.MORPHOLOGY',
        '"2.9"',
        '"2.9.2"',
        '"الأسماء الخاصة"',
        '"اسم المرة"'
    ),
    
    # ============================================================================
    # LAYER 3: LEXICON (15 engines)
    # ============================================================================
    
    # Group 3.1: Proper Nouns
    'src/engines/lexicon/a3lam_ashkhas_engine.py': (
        'EngineLayer.LEXICON',
        '"3.1"',
        '"3.1.1"',
        '"الأعلام"',
        '"أعلام الأشخاص"'
    ),
    'src/engines/lexicon/a3lam_amakin_engine.py': (
        'EngineLayer.LEXICON',
        '"3.1"',
        '"3.1.2"',
        '"الأعلام"',
        '"أعلام الأماكن"'
    ),
    'src/engines/lexicon/a3lam_manqula_engine.py': (
        'EngineLayer.LEXICON',
        '"3.1"',
        '"3.1.3"',
        '"الأعلام"',
        '"الأعلام المنقولة"'
    ),
    
    # Group 3.2: Common Nouns
    'src/engines/lexicon/generic_nouns_engine.py': (
        'EngineLayer.LEXICON',
        '"3.2"',
        '"3.2.1"',
        '"الأسماء الشائعة"',
        '"أسماء الجنس"'
    ),
    'src/engines/lexicon/place_engine.py': (
        'EngineLayer.LEXICON',
        '"3.2"',
        '"3.2.2"',
        '"الأسماء الشائعة"',
        '"أسماء المكان"'
    ),
    
    # Group 3.3: Number & Gender
    'src/engines/lexicon/adad_names_engine.py': (
        'EngineLayer.LEXICON',
        '"3.3"',
        '"3.3.1"',
        '"العدد والجنس"',
        '"أسماء الأعداد"'
    ),
    'src/engines/lexicon/gender_engine.py': (
        'EngineLayer.LEXICON',
        '"3.3"',
        '"3.3.2"',
        '"العدد والجنس"',
        '"التذكير والتأنيث"'
    ),
    
    # Group 3.4: Collective & Individual
    'src/engines/lexicon/jins_jamii_engine.py': (
        'EngineLayer.LEXICON',
        '"3.4"',
        '"3.4.1"',
        '"الجمعي والإفرادي"',
        '"جنس الجمع"'
    ),
    'src/engines/lexicon/jins_ifradi_engine.py': (
        'EngineLayer.LEXICON',
        '"3.4"',
        '"3.4.2"',
        '"الجمعي والإفرادي"',
        '"جنس الإفراد"'
    ),
    
    # Group 3.5: Semantic Classes
    'src/engines/lexicon/kainat_aqila_engine.py': (
        'EngineLayer.LEXICON',
        '"3.5"',
        '"3.5.1"',
        '"التصنيفات الدلالية"',
        '"الكائنات العاقلة"'
    ),
    'src/engines/lexicon/kainat_ghair_aqila_engine.py': (
        'EngineLayer.LEXICON',
        '"3.5"',
        '"3.5.2"',
        '"التصنيفات الدلالية"',
        '"الكائنات غير العاقلة"'
    ),
    
    # Group 3.6: Religious & Specialized
    'src/engines/lexicon/asma_allah_engine.py': (
        'EngineLayer.LEXICON',
        '"3.6"',
        '"3.6.1"',
        '"الدينية والمتخصصة"',
        '"أسماء الله الحسنى"'
    ),
    'src/engines/lexicon/musatalahat_sharia_engine.py': (
        'EngineLayer.LEXICON',
        '"3.6"',
        '"3.6.2"',
        '"الدينية والمتخصصة"',
        '"المصطلحات الشرعية"'
    ),
    'src/engines/lexicon/common_attributes_engine.py': (
        'EngineLayer.LEXICON',
        '"3.6"',
        '"3.6.3"',
        '"الدينية والمتخصصة"',
        '"الصفات الشائعة"'
    ),
    
    # ============================================================================
    # LAYER 4: SYNTAX (13 engines)
    # ============================================================================
    
    # Group 4.1: Core Arguments
    'src/engines/syntax/fael_engine.py': (
        'EngineLayer.SYNTAX',
        '"4.1"',
        '"4.1.1"',
        '"الأركان الأساسية"',
        '"الفاعل"'
    ),
    'src/engines/syntax/mafoul_bih_engine.py': (
        'EngineLayer.SYNTAX',
        '"4.1"',
        '"4.1.2"',
        '"الأركان الأساسية"',
        '"المفعول به"'
    ),
    'src/engines/syntax/naeb_fael_engine.py': (
        'EngineLayer.SYNTAX',
        '"4.1"',
        '"4.1.3"',
        '"الأركان الأساسية"',
        '"نائب الفاعل"'
    ),
    'src/engines/syntax/mobtada_khabar_engine.py': (
        'EngineLayer.SYNTAX',
        '"4.1"',
        '"4.1.4"',
        '"الأركان الأساسية"',
        '"المبتدأ والخبر"'
    ),
    
    # Group 4.2: Adjuncts
    'src/engines/syntax/mafoul_mutlaq_engine.py': (
        'EngineLayer.SYNTAX',
        '"4.2"',
        '"4.2.1"',
        '"المتممات"',
        '"المفعول المطلق"'
    ),
    'src/engines/syntax/mafoul_ajlih_engine.py': (
        'EngineLayer.SYNTAX',
        '"4.2"',
        '"4.2.2"',
        '"المتممات"',
        '"المفعول لأجله"'
    ),
    'src/engines/syntax/haal_engine.py': (
        'EngineLayer.SYNTAX',
        '"4.2"',
        '"4.2.3"',
        '"المتممات"',
        '"الحال"'
    ),
    'src/engines/syntax/tamyeez_engine.py': (
        'EngineLayer.SYNTAX',
        '"4.2"',
        '"4.2.4"',
        '"المتممات"',
        '"التمييز"'
    ),
    
    # Group 4.3: Interrogatives
    'src/engines/syntax/istifham_engine.py': (
        'EngineLayer.SYNTAX',
        '"4.3"',
        '"4.3.1"',
        '"الاستفهام"',
        '"أدوات الاستفهام"'
    ),
    'src/engines/syntax/jawab_engine.py': (
        'EngineLayer.SYNTAX',
        '"4.3"',
        '"4.3.2"',
        '"الاستفهام"',
        '"الجواب"'
    ),
    
    # Group 4.4: Stylistic Operations
    'src/engines/syntax/taqdim_engine.py': (
        'EngineLayer.SYNTAX',
        '"4.4"',
        '"4.4.1"',
        '"العمليات الأسلوبية"',
        '"التقديم"'
    ),
    'src/engines/syntax/ishtighal_engine.py': (
        'EngineLayer.SYNTAX',
        '"4.4"',
        '"4.4.2"',
        '"العمليات الأسلوبية"',
        '"اشتغال"'
    ),
    
    # Group 4.5: Exclamation
    'src/engines/syntax/taajjub_engine.py': (
        'EngineLayer.SYNTAX',
        '"4.5"',
        '"4.5.1"',
        '"التعجب"',
        '"التعجب"'
    ),
    
    # Group 4.6: Restriction
    'src/engines/syntax/qasr_engine.py': (
        'EngineLayer.SYNTAX',
        '"4.6"',
        '"4.6.1"',
        '"القصر والتخصيص"',
        '"القصر"'
    ),
    'src/engines/syntax/qasr_taqdim_engine.py': (
        'EngineLayer.SYNTAX',
        '"4.6"',
        '"4.6.2"',
        '"القصر والتخصيص"',
        '"قصر التقديم"'
    ),
    
    # ============================================================================
    # LAYER 5: RHETORIC (11 engines)
    # ============================================================================
    
    # Group 5.1: Figures of Speech
    'src/engines/rhetoric/tashbih_engine.py': (
        'EngineLayer.RHETORIC',
        '"5.1"',
        '"5.1.1"',
        '"الأساليب البيانية"',
        '"التشبيه"'
    ),
    'src/engines/rhetoric/istiara_engine.py': (
        'EngineLayer.RHETORIC',
        '"5.1"',
        '"5.1.2"',
        '"الأساليب البيانية"',
        '"الاستعارة"'
    ),
    'src/engines/rhetoric/kinaya_engine.py': (
        'EngineLayer.RHETORIC',
        '"5.1"',
        '"5.1.3"',
        '"الأساليب البيانية"',
        '"الكناية"'
    ),
    
    # Group 5.2: Sound Patterns
    'src/engines/rhetoric/jinass_engine.py': (
        'EngineLayer.RHETORIC',
        '"5.2"',
        '"5.2.1"',
        '"الأنماط الصوتية"',
        '"الجناس"'
    ),
    'src/engines/rhetoric/saja_engine.py': (
        'EngineLayer.RHETORIC',
        '"5.2"',
        '"5.2.2"',
        '"الأنماط الصوتية"',
        '"السجع"'
    ),
    
    # Group 5.3: Semantic Relations
    'src/engines/rhetoric/muqabala_engine.py': (
        'EngineLayer.RHETORIC',
        '"5.3"',
        '"5.3.1"',
        '"العلاقات الدلالية"',
        '"المقابلة"'
    ),
    
    # Group 5.4: Brevity & Expansion
    'src/engines/rhetoric/ijaz_itnab_engine.py': (
        'EngineLayer.RHETORIC',
        '"5.4"',
        '"5.4.1"',
        '"الإيجاز والإطناب"',
        '"الإيجاز والإطناب"'
    ),
}


def update_engine_file(file_path: str, layer: str, group: str, subgroup: str, group_ar: str, subgroup_ar: str):
    """Add or update LAYER, GROUP, SUBGROUP metadata in an engine file."""
    
    full_path = Path(file_path)
    if not full_path.exists():
        print(f"⚠️  File not found: {file_path}")
        return False
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find class definition (with or without parentheses)
        import re
        class_match = re.search(r'class\s+(\w+)(?:\([^)]+\))?:', content)
        if not class_match:
            print(f"⚠️  No class found in {file_path}")
            return False
        
        class_name = class_match.group(1)
        class_start = class_match.end()
        
        # Find SHEET_NAME (it should exist after class definition)
        sheet_name_match = re.search(r'\n\s+SHEET_NAME\s*=', content[class_start:])
        if not sheet_name_match:
            print(f"⚠️  No SHEET_NAME found in {file_path}")
            return False
        
        # Insert metadata after SHEET_NAME line
        sheet_name_line_end = class_start + sheet_name_match.end()
        # Find end of SHEET_NAME line
        next_newline = content.find('\n', sheet_name_line_end)
        if next_newline == -1:
            next_newline = len(content)
        
        insertion_point = next_newline + 1
        
        # Check if metadata already exists
        has_layer = 'LAYER =' in content[insertion_point:insertion_point+500]
        has_group = 'GROUP =' in content[insertion_point:insertion_point+500]
        
        if has_layer and has_group:
            print(f"✓ {file_path} - already has metadata (skipping)")
            return True
        
        # Create metadata block
        indent = '    '
        metadata = f'''{indent}LAYER = {layer}
{indent}GROUP = {group}
{indent}SUBGROUP = {subgroup}
{indent}GROUP_AR = {group_ar}
{indent}SUBGROUP_AR = {subgroup_ar}
'''
        
        # Insert metadata
        new_content = content[:insertion_point] + metadata + content[insertion_point:]
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ {file_path} - added metadata")
        return True
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False


def main():
    """Update all engine files with hierarchical metadata."""
    print("=" * 80)
    print("🔧 POPULATING ENGINE HIERARCHY METADATA")
    print("=" * 80)
    print()
    
    total = len(ENGINE_METADATA)
    updated = 0
    skipped = 0
    failed = 0
    
    for file_path, (layer, group, subgroup, group_ar, subgroup_ar) in ENGINE_METADATA.items():
        result = update_engine_file(file_path, layer, group, subgroup, group_ar, subgroup_ar)
        if result is True:
            if "already has" in str(result):
                skipped += 1
            else:
                updated += 1
        elif result is False:
            failed += 1
    
    print()
    print("=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"Total engines: {total}")
    print(f"✅ Updated: {updated}")
    print(f"⏭️  Skipped (already has metadata): {skipped}")
    print(f"❌ Failed: {failed}")
    print()
    print("Run 'python engine_hierarchy.py --stats' to verify the hierarchy.")


if __name__ == '__main__':
    main()
