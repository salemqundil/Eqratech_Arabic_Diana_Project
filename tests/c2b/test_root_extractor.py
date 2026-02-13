"""Tests for RootExtractor."""

import pytest

from fvafk.c2b.morpheme import RootType
from fvafk.c2b.root_extractor import RootExtractor


class TestRootExtractorBasic:
    def test_simple_trilateral(self):
        extractor = RootExtractor()
        root = extractor.extract("كَتَبَ")
        assert root is not None
        assert root.letters == ("ك", "ت", "ب")
        assert root.root_type == RootType.TRILATERAL

    def test_without_diacritics(self):
        extractor = RootExtractor()
        root = extractor.extract("كتب")
        assert root is not None
        assert root.letters == ("ك", "ت", "ب")

    def test_with_definite_article(self):
        extractor = RootExtractor()
        root = extractor.extract("الكِتَاب")
        assert root is not None
        assert root.letters == ("ك", "ت", "ب")

    def test_active_participle(self):
        extractor = RootExtractor()
        root = extractor.extract("كَاتِب")
        assert root is not None
        assert root.letters == ("ك", "ت", "ب")

    def test_passive_participle(self):
        extractor = RootExtractor()
        root = extractor.extract("مَكْتُوب")
        assert root is not None
        assert root.letters == ("ك", "ت", "ب")


class TestRootExtractorWeakRoots:
    def test_hollow_root(self):
        extractor = RootExtractor()
        root = extractor.extract("قَالَ")
        assert root is not None
        assert len(root.letters) == 3

    def test_defective_root(self):
        extractor = RootExtractor()
        root = extractor.extract("رَمَى")
        assert root is not None
        assert len(root.letters) == 3


class TestRootExtractorDoubled:
    def test_doubled_root(self):
        extractor = RootExtractor()
        root = extractor.extract("مَرَّ")
        assert root is not None
        assert len(root.letters) == 3


class TestRootExtractorQuadrilateral:
    def test_quadrilateral_root(self):
        extractor = RootExtractor()
        root = extractor.extract("دَحْرَجَ")
        assert root is not None
        assert len(root.letters) == 4
        assert root.root_type == RootType.QUADRILATERAL


class TestRootExtractorComplexAffixes:
    def test_multiple_prefixes(self):
        extractor = RootExtractor()
        root = extractor.extract("والكِتَاب")
        assert root is not None
        assert root.letters == ("ك", "ت", "ب")

    def test_multiple_suffixes(self):
        extractor = RootExtractor()
        root = extractor.extract("كَاتِبُونَ")
        assert root is not None
        assert root.letters == ("ك", "ت", "ب")

    def test_form_x(self):
        extractor = RootExtractor()
        root = extractor.extract("اسْتَكْتَبَ")
        assert root is not None
        assert root.letters == ("ك", "ت", "ب")


class TestRootExtractorNormalization:
    def test_hamza_normalization(self):
        extractor = RootExtractor()
        root1 = extractor.extract("أَكَلَ")
        root2 = extractor.extract("اكل")
        assert root1 is not None
        assert root2 is not None
        assert root1.letters == root2.letters

    def test_hamza_carrier_normalization(self):
        extractor = RootExtractor()

        root = extractor.extract("مُؤْمِنُونَ")
        assert root is not None
        assert root.letters == ("ا", "م", "ن")

        root = extractor.extract("أَكَلَ")
        assert root is not None
        assert root.letters[0] == "ا"

        root = extractor.extract("إِيمَانٌ")
        assert root is not None
        assert root.letters[0] == "ا"
        assert "م" in root.letters
        assert "إ" not in root.letters

        root = extractor.extract("خَطِيئَة")
        assert root is not None
        assert "ئ" not in root.letters
        assert "ي" in root.letters


    def test_alif_maqsurah(self):
        extractor = RootExtractor()
        root = extractor.extract("رَمَى")
        assert root is not None
        assert len(root.letters) == 3


class TestRootExtractorAffixes:
    def test_affix_identification(self):
        extractor = RootExtractor()

        context = extractor.extract_with_affixes("والِكِتَاب")
        assert context.prefix == "وال"
        assert context.stripped_word == "كتاب"
        assert context.root is not None
        assert context.root.letters == ("ك", "ت", "ب")

        context = extractor.extract_with_affixes("كَاتِبُونَ")
        assert context.suffix == "ون"
        assert context.root is not None
        assert context.root.letters == ("ك", "ت", "ب")

class TestRootExtractorValidation:
    def test_empty_string(self):
        extractor = RootExtractor()
        root = extractor.extract("")
        assert root is None

    def test_short_string(self):
        extractor = RootExtractor()
        root = extractor.extract("اب")
        assert root is None or len(root.letters) < 3

    def test_known_roots(self):
        known = {"ك-ت-ب", "ق-ر-أ"}
        extractor = RootExtractor(known_roots=known)
        root = extractor.extract("كَتَبَ")
        assert root is not None


class TestRootExtractorRealWorld:
    def test_quran_example_1(self):
        extractor = RootExtractor()
        root = extractor.extract("كِتَابٌ")
        assert root is not None
        assert root.letters == ("ك", "ت", "ب")

    def test_quran_example_2(self):
        extractor = RootExtractor()
        root = extractor.extract("مُؤْمِنُونَ")
        assert root is not None
        assert len(root.letters) == 3

    def test_quran_example_3(self):
        extractor = RootExtractor()
        root = extractor.extract("الرَّحْمَٰنِ")
        assert root is not None
        assert len(root.letters) == 3

    def test_quran_exception_vision_verb_with_pronoun(self):
        extractor = RootExtractor()
        context = extractor.extract_with_affixes("تَرَاهُمْ")
        assert context.root is not None
        # رأى/يرى/ترى -> ر-أ-ي (stored as ر-ا-ي after hamza normalization)
        assert context.root.letters == ("ر", "أ", "ي")
        assert context.suffix == "هم"

    def test_tanwin_does_not_segment_as_na(self):
        extractor = RootExtractor()
        context = extractor.extract_with_affixes("وَرِضْوَانًا")
        assert "نا" not in (context.suffix or "").split("+")

    def test_sima_no_split_only_peel_pronoun(self):
        extractor = RootExtractor()
        context = extractor.extract_with_affixes("سِيمَاهُمْ")
        assert context.suffix == "هم"
        # do not strip "س" or "سي" from سيما
        assert context.stripped_word.startswith("سيما")

    def test_lam_ta3leel_segments_before_imperfect(self):
        extractor = RootExtractor()
        ctx = extractor.extract_with_affixes("لِيَغِيظَ")
        assert ctx.root is not None
        assert ctx.root.letters == ("غ", "ي", "ظ")
        assert "ل" in (ctx.prefix or "").split("+")

    def test_istawa_stripped_has_three_letters(self):
        extractor = RootExtractor()
        ctx = extractor.extract_with_affixes("فَاسْتَوَىٰ")
        assert ctx.root is not None
        assert ctx.root.letters == ("س", "و", "ي")
        assert ctx.stripped_word == "سوي"

    def test_wa_clitic_strips_before_past_plural(self):
        extractor = RootExtractor()
        ctx = extractor.extract_with_affixes("وَعَمِلُوا")
        assert "و" in (ctx.prefix or "").split("+")
        assert ctx.stripped_word == "عمل"
        assert ctx.suffix == "وا"

    def test_wujoohihim_does_not_split_h_before_hum(self):
        extractor = RootExtractor()
        ctx = extractor.extract_with_affixes("وُجُوهِهِم")
        assert ctx.suffix == "هم"
        assert ctx.stripped_word == "وجوه"

    def test_fadlan_does_not_strip_fa_as_clitic(self):
        extractor = RootExtractor()
        ctx = extractor.extract_with_affixes("فَضْلًا")
        assert ctx.root is not None
        assert ctx.root.letters == ("ف", "ض", "ل")
        assert (ctx.prefix or "") == ""
        assert ctx.stripped_word == "فضل"

    def test_azeeman_strips_tanwin_support_alif(self):
        extractor = RootExtractor()
        ctx = extractor.extract_with_affixes("عَظِيمًا")
        assert ctx.root is not None
        assert ctx.root.letters == ("ع", "ظ", "م")
        assert ctx.stripped_word == "عظيم"
