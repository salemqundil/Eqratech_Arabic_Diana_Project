"""
أمثلة توضيحية للنظرية على مقاطع CVC عربية
Demonstration Examples for CVC Syllables

أمثلة واقعية تُظهر البرهان والانحياز.
"""

import numpy as np
import sys
sys.path.insert(0, 'src')

from theory.phonetic_space.feature_space import ConsonantSpace, VowelSpace
from theory.phonetic_space.projection import ProjectionPsi
from theory.minimizers.syllable_energy import SyllableEnergy
from theory.minimizers.optimizer import VowelOptimizer
from theory.proofs.existence_uniqueness import ExistenceUniquenessTheorem


def example_1_kataba():
    """
    مثال 1: مقطع /ktb/ (كَتَبَ)
    
    - ك /k/: velar stop (place=0.7, back)
    - ت /t/: dental stop (place=0.3, front)
    - المتوقع: حركة وسطى (a-like)
    """
    print("\n" + "="*70)
    print("مثال 1: مقطع /ktb/ (كَتَبَ)")
    print("="*70)
    
    C_space = ConsonantSpace()
    V_space = VowelSpace()
    psi = ProjectionPsi(C_space, V_space)
    energy = SyllableEnergy(V_space, psi, alpha=0.05)
    optimizer = VowelOptimizer(energy, V_space)
    
    # الصامتان
    C_k = np.array([0.7, 0.0])  # /k/ velar (back)
    C_t = np.array([0.3, 0.0])  # /t/ dental (front)
    
    flags = C_space.extract_flags(C_k)
    print(f"\nالصامت الأيسر /k/: place={C_k[0]:.2f} (خلفي)")
    print(f"الصامت الأيمن /t/: place={C_t[0]:.2f} (أمامي)")
    print(f"أعلام: {flags}")
    
    # الحل
    V_star, E_min, success = optimizer.solve_numerical(C_k, C_t, flags)
    
    print(f"\nالحركة المثلى V* = [{V_star[0]:+.3f}, {V_star[1]:+.3f}]")
    print(f"  backness = {V_star[0]:+.3f} (سالب=أمامي، موجب=خلفي)")
    print(f"  height = {V_star[1]:+.3f} (سالب=منخفض، موجب=مرتفع)")
    print(f"الطاقة E_min = {E_min:.6f}")
    print(f"المنطقة: {V_space.get_vowel_region_name(V_star)}")
    print(f"نجح المصغِّر: {success}")


def example_2_emphatic_comparison():
    """
    مثال 2: مقارنة مقطع عادي مع مفخم
    
    - الحالة 1: /ktb/ عادي
    - الحالة 2: /ṣṭb/ مفخم (ص ط)
    """
    print("\n" + "="*70)
    print("مثال 2: مقارنة مقطع عادي/مفخم")
    print("="*70)
    
    C_space = ConsonantSpace()
    V_space = VowelSpace()
    psi = ProjectionPsi(C_space, V_space)
    energy = SyllableEnergy(V_space, psi, alpha=0.05)
    optimizer = VowelOptimizer(energy, V_space)
    
    # حالة 1: عادية
    C_k = np.array([0.6, 0.0])
    C_t = np.array([0.3, 0.0])
    flags_plain = {'emphatic': 0.0, 'place': 0.45, 'manner': 0.0}
    
    V_plain, E_plain, _ = optimizer.solve_numerical(C_k, C_t, flags_plain)
    
    # حالة 2: مفخمة (ص /sˤ/ + ط /tˤ/)
    C_saad = np.array([0.9, 0.6])  # /ṣ/ pharyngealized
    C_taa_heavy = np.array([0.8, 0.0])  # /ṭ/ emphatic
    flags_emph = C_space.extract_flags(C_saad)
    
    V_emph, E_emph, _ = optimizer.solve_numerical(C_saad, C_taa_heavy, flags_emph)
    
    print("\nالحالة 1 - عادية (/ktb/):")
    print(f"  V = [{V_plain[0]:+.3f}, {V_plain[1]:+.3f}]")
    print(f"  المنطقة: {V_space.get_vowel_region_name(V_plain)}")
    print(f"  E = {E_plain:.6f}")
    
    print("\nالحالة 2 - مفخمة (/ṣṭb/):")
    print(f"  V = [{V_emph[0]:+.3f}, {V_emph[1]:+.3f}]")
    print(f"  المنطقة: {V_space.get_vowel_region_name(V_emph)}")
    print(f"  E = {E_emph:.6f}")
    print(f"  emphatic flag = {flags_emph['emphatic']:.2f}")
    
    print("\nالتحول (Shift):")
    print(f"  Δbackness = {V_emph[0] - V_plain[0]:+.3f}")
    print(f"  Δheight = {V_emph[1] - V_plain[1]:+.3f}")
    
    if V_emph[0] > V_plain[0]:
        print("  ✓ انحياز التفخيم: يتحرك نحو back (خلفي)")
    else:
        print("  ⚠ لا يوجد انحياز واضح")


def example_3_full_proof():
    """
    مثال 3: برهان كامل على مقطع واحد
    """
    print("\n" + "="*70)
    print("مثال 3: برهان كامل (وجود + تفرد + انحياز)")
    print("="*70)
    
    C_space = ConsonantSpace()
    V_space = VowelSpace()
    psi = ProjectionPsi(C_space, V_space)
    energy = SyllableEnergy(V_space, psi, alpha=0.1)
    optimizer = VowelOptimizer(energy, V_space)
    theorem = ExistenceUniquenessTheorem(energy, optimizer)
    
    # صامتان مختلفان
    C_L = np.array([0.4, 0.5])
    C_R = np.array([0.7, 0.3])
    flags = {'emphatic': 0.4, 'place': 0.55, 'manner': 0.4}
    
    # البرهان
    result = theorem.prove_all(C_L, C_R, flags)
    
    # طباعة
    print("\n" + "\n".join(result.proof_log))


def example_4_lipschitz_test():
    """
    مثال 4: اختبار شرط ليبتشيتز
    """
    print("\n" + "="*70)
    print("مثال 4: اختبار شرط ليبتشيتز على ψ")
    print("="*70)
    
    C_space = ConsonantSpace()
    V_space = VowelSpace()
    psi = ProjectionPsi(C_space, V_space)
    
    # عدة أزواج من الصوامت
    test_pairs = [
        (np.array([0.2, 0.3]), np.array([0.8, 0.7])),
        (np.array([0.5, 0.5]), np.array([0.6, 0.6])),
        (np.array([0.0, 0.0]), np.array([1.0, 1.0])),
    ]
    
    print(f"\nثابت ليبتشيتز L = {psi.L}")
    print("\nالاختبارات:")
    
    for i, (C1, C2) in enumerate(test_pairs, 1):
        is_lip, ratio = psi.is_lipschitz(C1, C2)
        status = "✓" if is_lip else "✗"
        print(f"{i}. C1={C1}, C2={C2}")
        print(f"   d(ψ(C1),ψ(C2)) / d(C1,C2) = {ratio:.3f}")
        print(f"   {status} {ratio:.3f} ≤ {psi.L}")


if __name__ == '__main__':
    example_1_kataba()
    example_2_emphatic_comparison()
    example_3_full_proof()
    example_4_lipschitz_test()
    
    print("\n" + "="*70)
    print("✓ جميع الأمثلة اكتملت بنجاح")
    print("="*70)
