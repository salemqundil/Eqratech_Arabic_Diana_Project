"""
مقارنة محركات توليد الجمل - تقرير شامل
=====================================

هذا التقرير يقارن بين المحرك الحالي والمحرك المحسّن
"""

def compare_engines():
    print("=" * 80)
    print("مقارنة محركات توليد الجمل")
    print("=" * 80)
    
    print("\n🔍 المحرك الحالي (sentence_generation_engine.py)")
    print("-" * 50)
    
    current_engines = [
        'atf_engine (العطف)',
        'nafi_engine (النفي)', 
        'jar_engine (حروف الجر)',
        'pronouns_engine (الضمائر)',
        'adverbs_engine (الظروف)',
        'proper_nouns_engine (أسماء العلم)',
        'generic_nouns_engine (الأسماء العامة)',
        'qasr_engine (القصر)',
        'verbs_engine (الأفعال)',
        'base_reconstruction_engine (المحرك الأساسي)'
    ]
    
    print(f"📊 عدد المحركات المستخدمة: {len(current_engines)}")
    print("المحركات المستخدمة:")
    for i, engine in enumerate(current_engines, 1):
        print(f"  {i:2d}. {engine}")
    
    print("\n📈 أنماط الجمل المولدة:")
    current_patterns = [
        "ضمير + فعل مضارع + ظرف",
        "علم + فعل ماض + ظرف", 
        "نفي + ضمير + مضارع + اسم",
        "فعل أمر + ضمير",
        "علم + اسم (خبر)",
        "قصر + مبتدأ + خبر",
        "جار + مجرور/ظرف",
        "عطف + جملة فعلية"
    ]
    print(f"  عدد الأنماط: {len(current_patterns)}")
    for pattern in current_patterns:
        print(f"  • {pattern}")
    
    print("\n⚙️ خوارزميات التحقق: لا توجد")
    print("📊 العدد الأقصى للجمل: 600")
    
    print("\n" + "=" * 80)
    print("🚀 المحرك المحسّن (enhanced_sentence_generation_engine.py)")
    print("-" * 50)
    
    enhanced_engines = [
        'verbs_engine (الأفعال)',
        'generic_nouns_engine (الأسماء العامة)',
        'proper_nouns_engine (أسماء العلم)', 
        'pronouns_engine (الضمائر)',
        'demonstratives_engine (أسماء الإشارة)',
        'adjective_engine (الصفات)',
        'adverbs_engine (الظروف)',
        'jar_engine (حروف الجر)',
        'atf_engine (العطف)',
        'nafi_engine (النفي)',
        'istifham_engine (الاستفهام)',
        'relatives_engine (الأسماء الموصولة)',
        'shart_engine (الشرط)', 
        'nidha_engine (النداء)',
        'adad_engine (الأعداد)',
        'fael_engine (الفاعل)',
        'mafoul_bih_engine (المفعول به)',
        'mafoul_ajlih_engine (المفعول لأجله)',
        'mafoul_mutlaq_engine (المفعول المطلق)',
        'haal_engine (الحال)',
        'tamyeez_engine (التمييز)',
        'nasikh_engine (النواسخ)',
        'qasr_engine (القصر)',
        'afaal_khamsa_engine (الأفعال الخمسة)',
        'mabni_majhool_engine (المبني للمجهول)',
        'mobtada_khabar_engine (المبتدأ والخبر)'
    ]
    
    print(f"📊 عدد المحركات المستخدمة: {len(enhanced_engines)}")
    print("المحركات الجديدة المضافة:")
    new_engines = [e for e in enhanced_engines if e not in [eng.split(' ')[0] for eng in current_engines]]
    for i, engine in enumerate(new_engines, 1):
        print(f"  {i:2d}. {engine}")
    
    print("\n📈 أنماط الجمل المولدة (محسّن):")
    enhanced_patterns = [
        # فعلية
        "فعل + فاعل + مفعول به",
        "فعل + فاعل + مفعول مطلق", 
        "فعل + فاعل + حال",
        "أفعال خمسة + فاعل",
        "فعل مبني للمجهول + نائب فاعل",
        
        # اسمية  
        "مبتدأ + خبر",
        "اسم إشارة + اسم + صفة",
        "ناسخ + اسم + خبر", 
        "عدد + معدود",
        
        # معقدة
        "استفهام + فعل + اسم",
        "شرط + فعل الشرط + جواب الشرط",
        "نداء + منادى", 
        "اسم موصول + صلة الموصول"
    ]
    print(f"  عدد الأنماط: {len(enhanced_patterns)}")
    for pattern in enhanced_patterns:
        print(f"  • {pattern}")
    
    print("\n⚙️ خوارزميات التحقق:")
    compatibility_rules = [
        "تطابق الفعل مع الفاعل في الجنس والعدد",
        "تطابق المبتدأ والخبر", 
        "تطابق اسم الإشارة مع الاسم",
        "قواعد الأعداد والمعدود",
        "التحقق من التعريف والتنكير",
        "فلترة الجمل غير المتوافقة نحوياً"
    ]
    for rule in compatibility_rules:
        print(f"  ✓ {rule}")
        
    print("\n📊 العدد الأقصى للجمل: 2000")
    
    print("\n" + "=" * 80)
    print("📊 ملخص المقارنة")
    print("-" * 50)
    
    comparison = [
        ("عدد المحركات", len(current_engines), len(enhanced_engines)),
        ("أنماط الجمل", len(current_patterns), len(enhanced_patterns)), 
        ("خوارزميات التحقق", 0, len(compatibility_rules)),
        ("العدد الأقصى للجمل", 600, 2000),
        ("تغطية المحركات (%)", f"{len(current_engines)/89*100:.1f}%", f"{len(enhanced_engines)/89*100:.1f}%")
    ]
    
    for metric, current, enhanced in comparison:
        print(f"{metric:25s} | {str(current):>10s} | {str(enhanced):>10s}")
    
    print("\n🎯 التحسينات الرئيسية:")
    improvements = [
        f"زيادة {len(enhanced_engines) - len(current_engines)} محرك جديد",
        f"إضافة {len(enhanced_patterns) - len(current_patterns)} نمط جملة جديد",
        "خوارزميات التحقق من التوافق النحوي", 
        "دعم التراكيب المعقدة (استفهام، شرط، نداء)",
        "دعم المفاعيل والحال والتمييز",
        "دعم النواسخ والأفعال الخمسة",
        "زيادة العدد الأقصى للجمل بـ 233%"
    ]
    
    for i, improvement in enumerate(improvements, 1):
        print(f"  {i}. {improvement}")
    
    print("\n💡 التوصيات:")
    recommendations = [
        "استخدام المحرك المحسّن للحصول على تنويع أكبر",
        "تطبيق خوارزميات التحقق لضمان الصحة النحوية",
        "توسيع قواعد التوافق لتشمل حالات أكثر تعقيداً", 
        "إضافة محركات إضافية (البلاغة، الصرف المتقدم)",
        "تطوير واجهة تفاعلية لاختيار أنماط الجمل"
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")

if __name__ == "__main__":
    compare_engines()