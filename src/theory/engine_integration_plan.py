"""
خطة ربط النظرية الرياضية بجميع المحركات
Plan to Connect Mathematical Theory to All Engines

هذا الملف يحدد كيفية تطبيق arg min E على كل محرك.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class EngineTheoreticalMapping:
    """خريطة ربط محرك بالنظرية الرياضية"""
    engine_name: str
    layer: str
    applies_theory: bool  # هل يطبق النظرية؟
    theory_input: str  # المدخلات من النظرية
    theory_output: str  # المخرجات
    implementation_status: str  # حالة التطبيق
    notes: str


# ═══════════════════════════════════════════════════════════════════
# LAYER 1: PHONOLOGY (الصوتيات)
# ═══════════════════════════════════════════════════════════════════

PHONOLOGY_MAPPINGS = [
    EngineTheoreticalMapping(
        engine_name="PhonemesEngine",
        layer="PHONOLOGY",
        applies_theory=True,
        theory_input="Raw phonetic features",
        theory_output="F_C (consonant space) definition",
        implementation_status="FOUNDATIONAL",
        notes="يوفر السمات الفيزيائية الأساسية لبناء F_C"
    ),
    EngineTheoreticalMapping(
        engine_name="SoundEngine",
        layer="PHONOLOGY",
        applies_theory=True,
        theory_input="Phoneme sequences",
        theory_output="Feature vectors in F",
        implementation_status="FOUNDATIONAL",
        notes="تحويل الفونيمات إلى متجهات سمات"
    ),
    EngineTheoreticalMapping(
        engine_name="AswatMuhdathaEngine",
        layer="PHONOLOGY",
        applies_theory=True,
        theory_input="Modern sounds",
        theory_output="Extended F_C",
        implementation_status="PENDING",
        notes="إضافة أصوات حديثة إلى F_C"
    ),
]

# ═══════════════════════════════════════════════════════════════════
# LAYER 2: MORPHOLOGY (الصرف)
# ═══════════════════════════════════════════════════════════════════

MORPHOLOGY_MAPPINGS = [
    # Group 2.1: Verbal Morphology
    EngineTheoreticalMapping(
        engine_name="VerbsEngine",
        layer="MORPHOLOGY",
        applies_theory=True,
        theory_input="Root consonants (C₁C₂C₃)",
        theory_output="Full verb with vowels via arg min E",
        implementation_status="HIGH_PRIORITY",
        notes="""
        التطبيق:
        1. خذ الجذر: ك-ت-ب
        2. Pattern: CaCaCa
        3. لكل مقطع CV: حل V* = arg min E_syll(V | C_left, C_right)
        4. النتيجة: كَتَبَ (بدون جدول حركات)
        """
    ),
    EngineTheoreticalMapping(
        engine_name="AfaalKhamsaEngine",
        layer="MORPHOLOGY",
        applies_theory=True,
        theory_input="Root + prefix constraints",
        theory_output="Conjugated verb forms",
        implementation_status="HIGH_PRIORITY",
        notes="الأفعال الخمسة: يَكْتُبُونَ، تَكْتُبُونَ، ... (vowels من arg min)"
    ),
    
    # Group 2.2: Participial Forms
    EngineTheoreticalMapping(
        engine_name="ActiveParticipleEngine",
        layer="MORPHOLOGY",
        applies_theory=True,
        theory_input="Root C₁C₂C₃",
        theory_output="/CaCiC/ pattern with vowels",
        implementation_status="HIGH_PRIORITY",
        notes="""
        مثال: ك-ت-ب → كَاتِب
        - المقطع الأول /ka/: C=ك, V من arg min (مع تطويل)
        - المقطع الثاني /ti/: V من arg min
        - المقطع الثالث /b/: C فقط
        """
    ),
    EngineTheoreticalMapping(
        engine_name="PassiveParticipleEngine",
        layer="MORPHOLOGY",
        applies_theory=True,
        theory_input="Root C₁C₂C₃",
        theory_output="/maCCuC/ pattern",
        implementation_status="MEDIUM_PRIORITY",
        notes="مَكْتُوب: الضمة من arg min (انحياز u-like)"
    ),
    
    # Group 2.4: Comparative & Superlative
    EngineTheoreticalMapping(
        engine_name="SuperlativeEngine",
        layer="MORPHOLOGY",
        applies_theory=True,
        theory_input="Root + comparative context",
        theory_output="/aCCaC/ or /CuCCa/ patterns",
        implementation_status="MEDIUM_PRIORITY",
        notes="أَكْبَر، كُبْرَى: الحركات من minimization"
    ),
    
    # ... (باقي المحركات الصرفية)
]

# ═══════════════════════════════════════════════════════════════════
# LAYER 3: LEXICON (المعجم)
# ═══════════════════════════════════════════════════════════════════

LEXICON_MAPPINGS = [
    EngineTheoreticalMapping(
        engine_name="AsmaAllahEngine",
        layer="LEXICON",
        applies_theory=False,  # أسماء ثابتة
        theory_input="N/A",
        theory_output="Fixed divine names",
        implementation_status="NO_THEORY",
        notes="أسماء الله ثابتة لغويًا - لا تُولَّد"
    ),
    EngineTheoreticalMapping(
        engine_name="ProperNounsEngine",
        layer="LEXICON",
        applies_theory=False,
        theory_input="N/A",
        theory_output="Fixed proper names",
        implementation_status="NO_THEORY",
        notes="الأعلام لا تخضع لتوليد رياضي"
    ),
    # معظم المحركات المعجمية لا تطبق النظرية (بيانات ثابتة)
]

# ═══════════════════════════════════════════════════════════════════
# LAYER 4: SYNTAX (النحو)
# ═══════════════════════════════════════════════════════════════════

SYNTAX_MAPPINGS = [
    EngineTheoreticalMapping(
        engine_name="FaelEngine",
        layer="SYNTAX",
        applies_theory=True,
        theory_input="Subject word structure",
        theory_output="Case vowels (ُ، َ، ِ) via arg min",
        implementation_status="HIGH_PRIORITY",
        notes="""
        التطبيق:
        الفاعل: كَاتِبٌ → كَاتِبُ (الضمة من arg min)
        السياق النحوي يُعدّل flags في E_syll
        """
    ),
    EngineTheoreticalMapping(
        engine_name="MafoulBihEngine",
        layer="SYNTAX",
        applies_theory=True,
        theory_input="Object word structure",
        theory_output="Accusative vowel (َ) via arg min",
        implementation_status="HIGH_PRIORITY",
        notes="المفعول به: الفتحة من minimization مع flags خاصة"
    ),
    # ... (باقي المحركات النحوية)
]

# ═══════════════════════════════════════════════════════════════════
# LAYER 5: RHETORIC (البلاغة)
# ═══════════════════════════════════════════════════════════════════

RHETORIC_MAPPINGS = [
    EngineTheoreticalMapping(
        engine_name="TashbihEngine",
        layer="RHETORIC",
        applies_theory=False,
        theory_input="N/A",
        theory_output="Simile patterns",
        implementation_status="NO_THEORY",
        notes="البلاغة: تحليل نمطي لا توليد رياضي"
    ),
    # معظم المحركات البلاغية تحليلية وليست توليدية
]

# ═══════════════════════════════════════════════════════════════════
# LAYER 6: GENERATION (التوليد)
# ═══════════════════════════════════════════════════════════════════

GENERATION_MAPPINGS = [
    EngineTheoreticalMapping(
        engine_name="SentenceGenerationEngine",
        layer="GENERATION",
        applies_theory=True,
        theory_input="Sentence structure + word roots",
        theory_output="Complete sentence with all vowels",
        implementation_status="ULTIMATE_GOAL",
        notes="""
        التطبيق النهائي:
        1. Structure: Subject + Verb + Object
        2. لكل كلمة: توليد من root + pattern
        3. لكل مقطع في الكلمة: V* من arg min E
        4. النتيجة: جملة كاملة بدون جداول لغوية
        """
    ),
]

# ═══════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════

ALL_MAPPINGS = (
    PHONOLOGY_MAPPINGS +
    MORPHOLOGY_MAPPINGS +
    LEXICON_MAPPINGS +
    SYNTAX_MAPPINGS +
    RHETORIC_MAPPINGS +
    GENERATION_MAPPINGS
)


def get_theory_applicable_engines() -> List[EngineTheoreticalMapping]:
    """المحركات التي تطبق النظرية الرياضية"""
    return [m for m in ALL_MAPPINGS if m.applies_theory]


def get_priority_engines() -> Dict[str, List[EngineTheoreticalMapping]]:
    """المحركات مرتبة حسب الأولوية"""
    high = [m for m in ALL_MAPPINGS if m.implementation_status == "HIGH_PRIORITY"]
    medium = [m for m in ALL_MAPPINGS if m.implementation_status == "MEDIUM_PRIORITY"]
    foundational = [m for m in ALL_MAPPINGS if m.implementation_status == "FOUNDATIONAL"]
    
    return {
        "foundational": foundational,  # يجب تطبيقها أولاً
        "high": high,
        "medium": medium
    }


def print_implementation_roadmap():
    """طباعة خريطة الطريق"""
    priorities = get_priority_engines()
    applicable = get_theory_applicable_engines()
    
    print("=" * 70)
    print("خريطة تطبيق النظرية الرياضية على المحركات")
    print("=" * 70)
    print()
    
    print(f"إجمالي المحركات: {len(ALL_MAPPINGS)}")
    print(f"القابلة لتطبيق النظرية: {len(applicable)}")
    print(f"غير قابلة (بيانات ثابتة): {len(ALL_MAPPINGS) - len(applicable)}")
    print()
    
    print("=" * 70)
    print("الأولويات:")
    print("=" * 70)
    
    for priority_name, engines in priorities.items():
        if engines:
            print(f"\n🎯 {priority_name.upper()} ({len(engines)} محركات):")
            for eng in engines:
                print(f"   • {eng.engine_name} ({eng.layer})")
                if eng.notes:
                    notes_short = eng.notes.split('\n')[0][:60]
                    print(f"     → {notes_short}...")
    
    print()
    print("=" * 70)
    print("الخطوات التالية:")
    print("=" * 70)
    print("""
    1. ✅ بناء الإطار النظري (مكتمل)
    2. ⏳ تطبيق على FOUNDATIONAL engines (SoundEngine، PhonemesEngine)
    3. ⏳ تطبيق على HIGH_PRIORITY (VerbsEngine، ActiveParticipleEngine)
    4. ⏳ توسع على باقي المحركات
    5. ⏳ Integration test: جملة كاملة من arg min E فقط
    """)


if __name__ == '__main__':
    print_implementation_roadmap()
    
    print("\n" + "=" * 70)
    print("تفاصيل محركات HIGH PRIORITY:")
    print("=" * 70)
    
    high_p = get_priority_engines()['high']
    for eng in high_p:
        print(f"\n{'─' * 70}")
        print(f"📦 {eng.engine_name}")
        print(f"{'─' * 70}")
        print(f"Layer: {eng.layer}")
        print(f"Input: {eng.theory_input}")
        print(f"Output: {eng.theory_output}")
        print(f"\nNotes:\n{eng.notes}")
