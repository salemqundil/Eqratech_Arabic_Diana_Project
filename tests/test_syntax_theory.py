"""
اختبارات نظرية التركيب
=======================

اختبارات شاملة للتحقق من صحة جميع المكونات
"""

import sys


def test_structures():
    """اختبار الهياكل الأساسية"""
    print("=== اختبار الهياكل ===")
    
    from syntax_theory import (
        make_simple_input, VerbValency,
        make_token_node, LexicalAtom, LexicalType
    )
    
    # 1. بناء مدخل بسيط
    x = make_simple_input(verbs=["كتب"], nouns=["أحمد"])
    assert x.is_valid(), "المدخل يجب أن يكون صحيحًا"
    
    # 2. إنشاء عقدة
    atom = LexicalAtom(LexicalType.N, "أحمد")
    node = make_token_node(atom)
    assert node.lexical_atom == atom
    
    print("✓ الهياكل تعمل بشكل صحيح\n")


def test_relations():
    """اختبار العلاقات الثلاث"""
    print("=== اختبار العلاقات ===")
    
    from syntax_theory import (
        make_simple_isn_graph,
        LexicalAtom, LexicalType,
        RelationConstraints
    )
    
    # 1. إنشاء ISN
    verb = LexicalAtom(LexicalType.V, "كتب")
    subj = LexicalAtom(LexicalType.N, "أحمد")
    
    graph = make_simple_isn_graph(verb, subj)
    
    # 2. التحقق
    assert len(graph.get_isn_edges()) == 1, "يجب أن يوجد ISN واحد"
    assert graph.has_proposition(), "يجب أن يوجد حكم"
    assert RelationConstraints.must_have_proposition(graph)
    
    print("✓ العلاقات تعمل بشكل صحيح\n")


def test_operators():
    """اختبار العوامل"""
    print("=== اختبار العوامل ===")
    
    from syntax_theory import (
        make_inna_graph, make_lam_graph,
        LexicalAtom, LexicalType,
        CaseMarking, MoodMarking,
        OperatorConstraints
    )
    
    # 1. إنّ
    ism = LexicalAtom(LexicalType.N, "أحمد", requires_case=True)
    khabar = LexicalAtom(LexicalType.N, "كاتب", requires_case=True)
    
    y_inna = make_inna_graph(ism, khabar)
    
    # التحقق من الإعراب
    for token in y_inna.get_tokens():
        if token.lexical_atom and token.lexical_atom.raw_material == "أحمد":
            assert token.features.case == CaseMarking.ACC, "أحمد يجب أن يكون منصوبًا"
    
    # 2. لم
    verb = LexicalAtom(LexicalType.V, "يكتب")
    y_lam = make_lam_graph(verb)
    
    # التحقق من الصيغة
    for token in y_lam.get_tokens():
        if token.lexical_atom and token.lexical_atom.atom_type == LexicalType.V:
            assert token.features.mood == MoodMarking.JUSS, "يكتب يجب أن يكون مجزومًا"
    
    print("✓ العوامل تعمل بشكل صحيح\n")


def test_generators():
    """اختبار المُنشئ والمولد"""
    print("=== اختبار المُنشئ والمولد ===")
    
    from syntax_theory import (
        make_simple_input, VerbValency,
        CanonicalConstructor, SimpleGenerator
    )
    
    # 1. بناء مدخل
    x = make_simple_input(verbs=["كتب"], nouns=["أحمد", "الرسالة"])
    x.L[0].valency = VerbValency.TRANSITIVE
    
    # 2. بناء y₀
    y0 = CanonicalConstructor.construct(x)
    
    assert y0.has_proposition(), "y₀ يجب أن يحتوي حكمًا"
    assert len(y0.get_isn_edges()) >= 1, "y₀ يجب أن يحتوي ISN واحدًا على الأقل"
    
    # 3. توليد مرشحين
    y_correct, y_wrong = SimpleGenerator.generate_two_candidates(x)
    
    assert len(y_correct.get_tadmn_edges()) > len(y_wrong.get_tadmn_edges()), \
        "y_correct يجب أن يحتوي TADMN أكثر"
    
    print("✓ المُنشئ والمولد يعملان بشكل صحيح\n")


def test_energy():
    """اختبار دالة الكلفة"""
    print("=== اختبار دالة الكلفة ===")
    
    from syntax_theory import (
        make_simple_input, VerbValency,
        SimpleGenerator, SyntacticEnergy
    )
    
    # 1. بناء مدخل
    x = make_simple_input(verbs=["كتب"], nouns=["أحمد", "الرسالة"])
    x.L[0].valency = VerbValency.TRANSITIVE
    
    # 2. توليد مرشحين
    y_correct, y_wrong = SimpleGenerator.generate_two_candidates(x)
    
    # 3. حساب الكلفة
    energy = SyntacticEnergy()
    
    E_correct = energy.compute(y_correct, x)
    E_wrong = energy.compute(y_wrong, x)
    
    assert E_correct < E_wrong, "الصحيح يجب أن تكون كلفته أقل"
    assert E_wrong == float('inf'), "الخاطئ يجب أن يكون ∞"
    
    print(f"  E(y_correct) = {E_correct:.2f}")
    print(f"  E(y_wrong) = {E_wrong}")
    print("✓ دالة الكلفة تعمل بشكل صحيح\n")


def test_proofs():
    """اختبار البراهين"""
    print("=== اختبار البراهين ===")
    
    from syntax_theory import (
        make_simple_input, VerbValency,
        prove_all_theorems
    )
    
    # 1. بناء مدخل
    x = make_simple_input(verbs=["كتب"], nouns=["أحمد", "الرسالة"])
    x.L[0].valency = VerbValency.TRANSITIVE
    
    # 2. تشغيل البراهين
    results = prove_all_theorems(x)
    
    # 3. التحقق
    assert 'requires_isn' in results, "برهان ISN يجب أن يكون موجودًا"
    assert 'requires_tadmn' in results, "برهان TADMN يجب أن يكون موجودًا"
    
    assert results['requires_isn'].holds, "برهان ISN يجب أن ينجح"
    assert results['requires_tadmn'].holds, "برهان TADMN يجب أن ينجح"
    
    print(f"  عدد البراهين: {len(results)}")
    passed = sum(1 for r in results.values() if r.holds)
    print(f"  الناجحة: {passed}/{len(results)}")
    print("✓ البراهين تعمل بشكل صحيح\n")


def test_full_pipeline():
    """اختبار المسار الكامل"""
    print("=== اختبار المسار الكامل ===")
    
    from syntax_theory import (
        make_simple_input, VerbValency,
        CanonicalConstructor, CandidateGenerator,
        SyntacticOptimizer
    )
    
    # 1. المدخل
    x = make_simple_input(verbs=["كتب"], nouns=["أحمد", "الرسالة"])
    x.L[0].valency = VerbValency.TRANSITIVE
    
    print(f"  المدخل: {x}")
    
    # 2. y₀
    y0 = CanonicalConstructor.construct(x)
    print(f"  y₀: {y0}")
    
    # 3. G(x)
    candidates = CandidateGenerator.generate(x, max_modifications=1)
    print(f"  عدد المرشحين: {len(candidates)}")
    
    # 4. arg min E
    optimizer = SyntacticOptimizer()
    y_star = optimizer.solve(x, candidates)
    
    print(f"  y*: {y_star}")
    
    # التحقق
    assert y_star.has_proposition(), "y* يجب أن يحتوي حكمًا"
    
    print("✓ المسار الكامل يعمل بشكل صحيح\n")


def run_all_tests():
    """تشغيل جميع الاختبارات"""
    print("\n" + "=" * 60)
    print("اختبارات نظرية التركيب")
    print("=" * 60 + "\n")
    
    tests = [
        test_structures,
        test_relations,
        test_operators,
        test_generators,
        test_energy,
        test_proofs,
        test_full_pipeline
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ فشل: {test.__name__}")
            print(f"  {e}\n")
            failed += 1
    
    print("=" * 60)
    print(f"النتائج: {passed} نجح، {failed} فشل")
    print("=" * 60)
    
    if failed == 0:
        print("\n✅ جميع الاختبارات نجحت!\n")
        return 0
    else:
        print(f"\n❌ {failed} اختبار(ات) فشل\n")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
