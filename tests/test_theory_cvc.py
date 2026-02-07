"""
اختبارات النظرية الرياضية على مقاطع CVC
Tests for Mathematical Theory on CVC Syllables

اختبار كامل للمبرهنة على أمثلة حقيقية.
"""

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False
    # Mock pytest.fixture for standalone execution
    def pytest_fixture_mock(func):
        return func
    class pytest:
        fixture = staticmethod(pytest_fixture_mock)

import numpy as np
from theory.phonetic_space.feature_space import ConsonantSpace, VowelSpace
from theory.phonetic_space.projection import ProjectionPsi
from theory.minimizers.syllable_energy import SyllableEnergy
from theory.minimizers.optimizer import VowelOptimizer
from theory.proofs.existence_uniqueness import ExistenceUniquenessTheorem


class TestCVCTheory:
    """اختبارات المبرهنة على مقاطع CVC"""
    
    @pytest.fixture
    def setup_theory(self):
        """إعداد النظام النظري"""
        C_space = ConsonantSpace()
        V_space = VowelSpace()
        psi = ProjectionPsi(C_space, V_space)
        energy = SyllableEnergy(V_space, psi, alpha=0.1)
        optimizer = VowelOptimizer(energy, V_space)
        theorem = ExistenceUniquenessTheorem(energy, optimizer)
        
        return {
            'C_space': C_space,
            'V_space': V_space,
            'psi': psi,
            'energy': energy,
            'optimizer': optimizer,
            'theorem': theorem
        }
    
    def test_cvc_kataba_like(self, setup_theory):
        """
        مثال: مقطع مثل /ktb/ (ك ت ب)
        
        - ك: labial/front (place=0.2)
        - ب: labial/front (place=0.2)
        - متقاربان جدًا → OCP يفضل حركة صغيرة
        """
        sys = setup_theory
        
        # تعريف الصامتين
        C_k = np.array([0.2, 0.0])  # /k/ front stop
        C_b = np.array([0.2, 0.0])  # /b/ front stop
        
        flags = sys['C_space'].extract_flags(C_k)
        
        # برهان كامل
        result = sys['theorem'].prove_all(C_k, C_b, flags)
        
        # طباعة النتيجة
        print("\n" + "\n".join(result.proof_log))
        
        # التحقق
        assert result.existence, "يجب أن يوجد V*"
        assert result.uniqueness, "يجب أن يكون V* فريدًا"
        assert result.V_star is not None
        
        # التحقق من المنطقة (متوقع: a-like أو mid)
        region = sys['V_space'].get_vowel_region_name(result.V_star)
        print(f"\nالمنطقة المتوقعة: {region}")
        print(f"V* = {result.V_star}")
    
    def test_cvc_emphatic_shift(self, setup_theory):
        """
        مثال: مقطع مع صامت مفخم
        
        - ص: emphatic/back (place=0.8)
        - ب: front (place=0.2)
        - المتوقع: V* ينحاز نحو back (u-like)
        """
        sys = setup_theory
        
        # صامت مفخم
        C_saad = np.array([0.8, 0.0])  # /sˤ/ emphatic
        C_b = np.array([0.2, 0.0])      # /b/ plain
        
        flags = sys['C_space'].extract_flags(C_saad)
        print(f"\nأعلام التفخيم: {flags}")
        
        # حل
        V_star, E_min, success = sys['optimizer'].solve_numerical(C_saad, C_b, flags)
        
        assert success, "يجب أن ينجح المصغّر"
        
        region = sys['V_space'].get_vowel_region_name(V_star)
        print(f"\nV* = {V_star}")
        print(f"المنطقة: {region}")
        print(f"E_min = {E_min:.6f}")
        
        # التحقق من الانحياز: backness يجب أن يكون موجبًا
        assert V_star[0] > 0, "يجب أن ينحاز نحو back"
    
    def test_cvc_compare_plain_emphatic(self, setup_theory):
        """
        مقارنة: نفس الصامتين لكن مع/بدون تفخيم
        """
        sys = setup_theory
        
        C_L = np.array([0.5, 0.3])
        C_R = np.array([0.5, 0.3])
        
        # حالة عادية
        flags_plain = {'emphatic': 0.0, 'place': 0.5, 'manner': 0.3}
        V_plain, _, _ = sys['optimizer'].solve_numerical(C_L, C_R, flags_plain)
        
        # حالة مفخمة
        flags_emph = {'emphatic': 1.0, 'place': 0.8, 'manner': 0.3}
        V_emph, _, _ = sys['optimizer'].solve_numerical(C_L, C_R, flags_emph)
        
        print(f"\nبدون تفخيم: V = {V_plain} ({sys['V_space'].get_vowel_region_name(V_plain)})")
        print(f"مع تفخيم: V = {V_emph} ({sys['V_space'].get_vowel_region_name(V_emph)})")
        print(f"التحول: Δbackness = {V_emph[0] - V_plain[0]:+.3f}")
        
        # التحقق من الانحياز
        assert V_emph[0] > V_plain[0], "التفخيم يجب أن يزيد backness"
    
    def test_lipschitz_condition(self, setup_theory):
        """اختبار شرط ليبتشيتز على ψ"""
        sys = setup_theory
        
        # صامتان عشوائيان
        C1 = np.array([0.3, 0.4])
        C2 = np.array([0.7, 0.6])
        
        is_lip, ratio = sys['psi'].is_lipschitz(C1, C2)
        
        print(f"\nشرط ليبتشيتز: {is_lip}")
        print(f"النسبة: {ratio:.3f} (يجب أن تكون ≤ {sys['psi'].L})")
        
        assert is_lip, "يجب أن تحقق ψ شرط ليبتشيتز"
    
    def test_uniqueness_multiple_starts(self, setup_theory):
        """اختبار التفرد بنقاط بداية متعددة"""
        sys = setup_theory
        
        C_L = np.array([0.4, 0.5])
        C_R = np.array([0.6, 0.4])
        flags = {'emphatic': 0.5, 'place': 0.5, 'manner': 0.45}
        
        is_unique, max_dev = sys['optimizer'].verify_uniqueness(
            C_L, C_R, flags, n_trials=20
        )
        
        print(f"\nتفرد الحل: {is_unique}")
        print(f"أقصى انحراف: {max_dev:.2e}")
        
        assert is_unique, "الحل يجب أن يكون فريدًا"
        assert max_dev < 1e-2, "الانحراف يجب أن يكون صغيرًا جدًا"
    
    def test_full_theorem_proof(self, setup_theory):
        """برهان كامل على مثال واحد"""
        sys = setup_theory
        
        # مثال: صامتان متوسطان
        C_L = np.array([0.5, 0.5])
        C_R = np.array([0.5, 0.5])
        flags = {'emphatic': 0.3, 'place': 0.5, 'manner': 0.5}
        
        # البرهان الكامل
        result = sys['theorem'].prove_all(C_L, C_R, flags)
        
        # طباعة
        print("\n" + "="*60)
        print("\n".join(result.proof_log))
        print("="*60)
        
        # التحققات
        assert result.existence, "فشل برهان الوجود"
        assert result.uniqueness, "فشل برهان التفرد"
        assert result.V_star is not None
        assert result.E_min < np.inf
        
        print(f"\n✓ البرهان ناجح!")
        print(f"V* = {result.V_star}")
        print(f"E_min = {result.E_min:.6f}")


if __name__ == '__main__':
    # تشغيل اختبار واحد كمثال
    test_obj = TestCVCTheory()
    
    if not HAS_PYTEST:
        # تشغيل setup_theory بدون pytest
        from theory.phonetic_space.feature_space import ConsonantSpace, VowelSpace
        from theory.phonetic_space.projection import ProjectionPsi
        from theory.minimizers.syllable_energy import SyllableEnergy
        from theory.minimizers.optimizer import VowelOptimizer
        from theory.proofs.existence_uniqueness import ExistenceUniquenessTheorem
        
        C_space = ConsonantSpace()
        V_space = VowelSpace()
        psi = ProjectionPsi(C_space, V_space)
        energy = SyllableEnergy(V_space, psi, alpha=0.1)
        optimizer = VowelOptimizer(energy, V_space)
        theorem = ExistenceUniquenessTheorem(energy, optimizer)
        
        setup = {
            'C_space': C_space,
            'V_space': V_space,
            'psi': psi,
            'energy': energy,
            'optimizer': optimizer,
            'theorem': theorem
        }
    else:
        setup = test_obj.setup_theory()
    
    print("="*70)
    print("  مثال: برهان كامل على مقطع CVC")
    print("="*70)
    
    test_obj.test_full_theorem_proof(setup)
