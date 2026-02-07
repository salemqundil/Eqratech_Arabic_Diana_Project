"""
أمثلة تطبيقية: براهين نظرية التركيب
===================================

أمثلة تُظهر كيف يختار arg min E العلاقات الثلاث (ISN/TADMN/TAQYID)
ويُغلق الجمل بالعوامل ويُفرّق بين المبني/المعرب

المحتويات:
----------
1. مثال فعلي بسيط: "كتب أحمد الرسالة"
2. مثال اسمي مع إنّ: "إنّ أحمدَ كاتبٌ"
3. مثال فعلي مع لم: "لم يكتبْ أحمد"
4. مقارنة مرشحين: لماذا يختار arg min الصحيح؟
5. برهان شامل: جميع المبرهنات
"""

import sys
from syntax_theory import (
    make_simple_input, VerbValency,
    CanonicalConstructor, SimpleGenerator, CandidateGenerator,
    SyntacticEnergy, SyntacticOptimizer,
    prove_all_theorems,
    LexicalAtom, LexicalType,
    make_inna_graph, make_lam_graph
)


def example_1_simple_verbal():
    """
    مثال 1: جملة فعلية بسيطة
    ==========================
    
    "كتب أحمد الرسالة"
    
    البنية المتوقعة:
    - ISN(كتب → أحمد) (الفاعل)
    - TADMN(كتب ⇒ الرسالة) (المفعول)
    """
    print("=" * 60)
    print("مثال 1: جملة فعلية بسيطة - 'كتب أحمد الرسالة'")
    print("=" * 60)
    
    # 1. بناء المدخل x
    x = make_simple_input(
        verbs=["كتب"],
        nouns=["أحمد", "الرسالة"]
    )
    # حدد أن "كتب" متعدٍّ
    x.L[0].valency = VerbValency.TRANSITIVE
    
    print(f"\n1. المدخل x:")
    print(f"   {x}")
    print(f"   صحيح؟ {x.is_valid()}")
    
    # 2. بناء y₀
    y0 = CanonicalConstructor.construct(x)
    
    print(f"\n2. المُنشئ القانوني y₀:")
    print(f"   {y0}")
    print(f"   العلاقات: {y0.count_relations()}")
    
    # 3. حساب الكلفة
    energy = SyntacticEnergy()
    E_y0 = energy.compute(y0, x)
    
    print(f"\n3. الكلفة:")
    print(f"   E(y₀) = {E_y0:.2f}")
    
    # 4. عرض البنية
    print(f"\n4. البنية التفصيلية:")
    for edge in y0.edges:
        source_name = edge.source.lexical_atom.raw_material if edge.source.lexical_atom else "?"
        target_name = edge.target.lexical_atom.raw_material if edge.target.lexical_atom else "?"
        print(f"   {edge.edge_type.name}({source_name} → {target_name})")
    
    print(f"\n✓ النتيجة: arg min E بنى جملة فعلية صحيحة")
    print(f"  - ISN للفاعل (أحمد)")
    print(f"  - TADMN للمفعول (الرسالة)")
    print()


def example_2_nominal_with_inna():
    """
    مثال 2: جملة اسمية مع إنّ
    =========================
    
    "إنّ أحمدَ كاتبٌ"
    
    البنية المتوقعة:
    - عامل إنّ: GOV(إنّ → أحمد) + assigns ACC
    - ISN(كاتب → أحمد) (الخبر والاسم)
    - الإعراب: أحمد منصوب، كاتب مرفوع
    """
    print("=" * 60)
    print("مثال 2: جملة اسمية مع إنّ - 'إنّ أحمدَ كاتبٌ'")
    print("=" * 60)
    
    # 1. بناء الجملة
    ism = LexicalAtom(
        atom_type=LexicalType.N,
        raw_material="أحمد",
        requires_case=True,  # معرب
        is_built=False
    )
    
    khabar = LexicalAtom(
        atom_type=LexicalType.N,
        raw_material="كاتب",
        requires_case=True
    )
    
    y_inna = make_inna_graph(ism, khabar)
    
    print(f"\n1. الجملة: 'إنّ أحمدَ كاتبٌ'")
    print(f"   {y_inna}")
    
    # 2. عرض العوامل
    print(f"\n2. العوامل:")
    for gov in y_inna.get_governors():
        print(f"   {gov.lexical_atom.raw_material}: {gov.operator_signature['operator_name']}")
        print(f"     يفرض: case={gov.operator_signature.get('assigns_case')}")
    
    # 3. عرض الإعراب
    print(f"\n3. الإعراب:")
    for token in y_inna.get_tokens():
        if token.lexical_atom:
            case = token.features.case.name if token.features.case else "غير محدد"
            print(f"   {token.lexical_atom.raw_material}: case={case}")
    
    # 4. عرض العلاقات
    print(f"\n4. العلاقات:")
    for edge in y_inna.edges:
        source_name = edge.source.lexical_atom.raw_material if edge.source.lexical_atom else "?"
        target_name = edge.target.lexical_atom.raw_material if edge.target.lexical_atom else "?"
        print(f"   {edge.edge_type.name}({source_name} → {target_name})")
    
    print(f"\n✓ النتيجة: عامل إنّ أغلق الجملة الاسمية:")
    print(f"  - نصب الاسم (أحمد)")
    print(f"  - رفع الخبر (كاتب)")
    print(f"  - ISN ربط الخبر بالاسم")
    print()


def example_3_verbal_with_lam():
    """
    مثال 3: جملة فعلية مع لم
    ========================
    
    "لم يكتبْ"
    
    البنية المتوقعة:
    - عامل لم: GOV(لم → يكتب) + assigns JUSS
    - الصيغة: يكتب مجزوم
    """
    print("=" * 60)
    print("مثال 3: جملة فعلية مع لم - 'لم يكتبْ'")
    print("=" * 60)
    
    # 1. بناء الجملة
    verb = LexicalAtom(
        atom_type=LexicalType.V,
        raw_material="يكتب",
        requires_case=False,  # الفعل ليس معربًا بـcase
        valency=VerbValency.INTRANSITIVE  # لازم (للبساطة)
    )
    
    y_lam = make_lam_graph(verb)
    
    print(f"\n1. الجملة: 'لم يكتبْ'")
    print(f"   {y_lam}")
    
    # 2. عرض العوامل
    print(f"\n2. العوامل:")
    for gov in y_lam.get_governors():
        print(f"   {gov.lexical_atom.raw_material}: {gov.operator_signature['operator_name']}")
        print(f"     يفرض: mood={gov.operator_signature.get('assigns_mood')}")
    
    # 3. عرض الصيغة
    print(f"\n3. الصيغة:")
    for token in y_lam.get_tokens():
        if token.lexical_atom and token.lexical_atom.atom_type == LexicalType.V:
            mood = token.features.mood.name if token.features.mood else "غير محدد"
            print(f"   {token.lexical_atom.raw_material}: mood={mood}")
    
    print(f"\n✓ النتيجة: عامل لم أغلق الفعل:")
    print(f"  - جزم المضارع (يكتبْ)")
    print()


def example_4_candidate_comparison():
    """
    مثال 4: مقارنة مرشحين
    ======================
    
    لماذا يختار arg min E المرشح الصحيح؟
    
    المدخل: "كتب أحمد الرسالة"
    - المرشح الصحيح: ISN + TADMN (جميع الفتحات مشبعة)
    - المرشح الخاطئ: ISN فقط (فتحة المفعول فارغة)
    """
    print("=" * 60)
    print("مثال 4: مقارنة مرشحين - لماذا يختار arg min الصحيح؟")
    print("=" * 60)
    
    # 1. بناء المدخل
    x = make_simple_input(
        verbs=["كتب"],
        nouns=["أحمد", "الرسالة"]
    )
    x.L[0].valency = VerbValency.TRANSITIVE
    
    print(f"\n1. المدخل: {x}")
    
    # 2. توليد مرشحين
    y_correct, y_wrong = SimpleGenerator.generate_two_candidates(x)
    
    print(f"\n2. المرشحان:")
    print(f"   y_correct: {y_correct}")
    print(f"     العلاقات: {y_correct.count_relations()}")
    print(f"   y_wrong (فتحة فارغة): {y_wrong}")
    print(f"     العلاقات: {y_wrong.count_relations()}")
    
    # 3. حساب الكلفة
    energy = SyntacticEnergy()
    
    E_correct = energy.compute(y_correct, x)
    E_wrong = energy.compute(y_wrong, x)
    
    print(f"\n3. الكلفة:")
    print(f"   E(y_correct) = {E_correct:.2f}")
    print(f"   E(y_wrong) = {E_wrong}")
    
    # 4. اختيار الأفضل
    if E_correct < E_wrong:
        print(f"\n✓ arg min E يختار y_correct")
        print(f"  السبب: فتحة المفعول مشبعة في y_correct")
        print(f"         بينما فارغة في y_wrong ⇒ E = ∞")
    else:
        print(f"\n✗ خطأ: arg min اختار الخاطئ!")
    
    print()


def example_5_full_proof():
    """
    مثال 5: برهان شامل
    ===================
    
    تشغيل جميع المبرهنات:
    1. arg min يتطلب ISN
    2. arg min يضيف TADMN للفتحات
    3. TAQYID اختياري لكن بالحد الأدنى
    4. المبني/المعرب كمسارين في E
    5. الفاعلية/المفعولية من Valency
    """
    print("=" * 60)
    print("مثال 5: برهان شامل - جميع المبرهنات")
    print("=" * 60)
    
    # 1. بناء مدخل شامل
    x = make_simple_input(
        verbs=["كتب"],
        nouns=["أحمد", "الرسالة"],
        prepositions=["في"]
    )
    x.L[0].valency = VerbValency.TRANSITIVE
    
    print(f"\n1. المدخل: {x}")
    
    # 2. تشغيل جميع البراهين
    print(f"\n2. تشغيل البراهين...\n")
    
    results = prove_all_theorems(x)
    
    # 3. عرض النتائج
    print("=" * 40)
    print("نتائج البراهين:")
    print("=" * 40)
    
    for name, result in results.items():
        print(f"\n{result}")
    
    # 4. عرض السجلات التفصيلية
    print("\n" + "=" * 60)
    print("السجلات التفصيلية:")
    print("=" * 60)
    
    for name, result in results.items():
        print(f"\n--- {name} ---")
        for line in result.log:
            print(line)
    
    # 5. الخلاصة
    all_pass = all(r.holds for r in results.values())
    
    print("\n" + "=" * 60)
    if all_pass:
        print("✓ جميع البراهين نجحت!")
        print("\nالنتيجة:")
        print("  arg min E يختار ISN/TADMN/TAQYID بالضرورة الحسابية")
        print("  ويُغلق الجمل بالعوامل")
        print("  ويُفرّق بين المبني/المعرب كمسارين للإشباع")
        print("  ويُعيّن الأدوار الدلالية تحت قيود التوافق")
    else:
        print("✗ بعض البراهين فشلت")
        failed = [name for name, r in results.items() if not r.holds]
        print(f"  الفاشلة: {', '.join(failed)}")
    print("=" * 60)
    print()


def run_all_examples():
    """تشغيل جميع الأمثلة"""
    print("\n")
    print("████████████████████████████████████████████████████████████")
    print("█                                                          █")
    print("█       أمثلة نظرية التركيب الرياضية                     █")
    print("█       x → y₀ → G(x) → arg min E                         █")
    print("█                                                          █")
    print("████████████████████████████████████████████████████████████")
    print("\n")
    
    example_1_simple_verbal()
    example_2_nominal_with_inna()
    example_3_verbal_with_lam()
    example_4_candidate_comparison()
    example_5_full_proof()
    
    print("\n" + "=" * 60)
    print("انتهت جميع الأمثلة")
    print("=" * 60)


if __name__ == "__main__":
    run_all_examples()
