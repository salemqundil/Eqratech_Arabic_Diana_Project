"""
Tests for I3rab Parser (Sprint 4 - Task 4.1).

Author: Hussein Hiyassat
Date: 2026-02-21
Sprint: 4
"""

import pytest
from fvafk.c2b.syntax import I3rabParser, I3rabComponents


class TestI3rabParserTop5Types:
    """Test parsing of the Top 5 I3rab types."""

    def setup_method(self):
        self.parser = I3rabParser()

    def test_parse_mubtada(self):
        """Detect مبتدأ in typical I3rab text."""
        text = "مُبْتَدَأٌ مَرْفُوعٌ وَعَلَامَةُ رَفْعِهِ الضَّمَّةُ الظَّاهِرَةُ"
        comp = self.parser.parse(text)
        assert comp.i3rab_type == "مبتدأ"
        assert comp.i3rab_type_en == "mubtada"

    def test_parse_khabar(self):
        """Detect خبر in typical I3rab text."""
        text = "خَبَرٌ مَرْفُوعٌ وَعَلَامَةُ رَفْعِهِ الضَّمَّةُ"
        comp = self.parser.parse(text)
        assert comp.i3rab_type == "خبر"
        assert comp.i3rab_type_en == "khabar"

    def test_parse_fa_il(self):
        """Detect فاعل in typical I3rab text."""
        text = "فَاعِلٌ مَرْفُوعٌ وَعَلَامَةُ رَفْعِهِ الضَّمَّةُ الظَّاهِرَةُ"
        comp = self.parser.parse(text)
        assert comp.i3rab_type == "فاعل"
        assert comp.i3rab_type_en == "fa'il"

    def test_parse_maf_ul_bihi(self):
        """Detect مفعول به in typical I3rab text."""
        text = "مَفْعُولٌ بِهِ مَنْصُوبٌ وَعَلَامَةُ نَصْبِهِ الْفَتْحَةُ"
        comp = self.parser.parse(text)
        assert comp.i3rab_type == "مفعول به"
        assert comp.i3rab_type_en == "maf'ul_bihi"

    def test_parse_harf(self):
        """Detect حرف in typical I3rab text."""
        text = "حَرْفُ جَرٍّ مَبْنِيٌّ عَلَى الْكَسْرِ"
        comp = self.parser.parse(text)
        assert comp.i3rab_type == "حرف"
        assert comp.i3rab_type_en == "harf"


class TestI3rabParserCase:
    """Test case extraction."""

    def setup_method(self):
        self.parser = I3rabParser()

    def test_nominative_case(self):
        text = "مُبْتَدَأٌ مَرْفُوعٌ وَعَلَامَةُ رَفْعِهِ الضَّمَّةُ"
        comp = self.parser.parse(text)
        assert comp.case == "nominative"

    def test_accusative_case(self):
        text = "مَفْعُولٌ بِهِ مَنْصُوبٌ وَعَلَامَةُ نَصْبِهِ الْفَتْحَةُ"
        comp = self.parser.parse(text)
        assert comp.case == "accusative"

    def test_genitive_case(self):
        text = "مُضَافٌ إِلَيْهِ مَجْرُورٌ وَعَلَامَةُ جَرِّهِ الْكَسْرَةُ الظَّاهِرَةُ"
        comp = self.parser.parse(text)
        assert comp.case == "genitive"

    def test_case_from_corpus_example(self):
        """Genitive case from real corpus row."""
        text = (
            'اسْمٌ مَجْرُورٌ وَعَلَامَةُ جَرِّهِ الْكَسْرَةُ الظَّاهِرَةُ'
        )
        comp = self.parser.parse(text)
        assert comp.case == "genitive"


class TestI3rabParserCaseMarkers:
    """Test case marker extraction."""

    def setup_method(self):
        self.parser = I3rabParser()

    def test_damma_marker(self):
        text = "مُبْتَدَأٌ مَرْفُوعٌ وَعَلَامَةُ رَفْعِهِ الضَّمَّةُ"
        comp = self.parser.parse(text)
        assert comp.case_marker == "الضمة"

    def test_fatha_marker(self):
        text = "مَنْصُوبٌ وَعَلَامَةُ نَصْبِهِ الْفَتْحَةُ"
        comp = self.parser.parse(text)
        assert comp.case_marker == "الفتحة"

    def test_kasra_marker(self):
        text = "مَجْرُورٌ وَعَلَامَةُ جَرِّهِ الْكَسْرَةُ"
        comp = self.parser.parse(text)
        assert comp.case_marker == "الكسرة"


class TestI3rabParserConfidence:
    """Test confidence scoring."""

    def setup_method(self):
        self.parser = I3rabParser()

    def test_high_confidence_with_all_fields(self):
        """All three fields detected → confidence == 1.0."""
        text = "مُبْتَدَأٌ مَرْفُوعٌ وَعَلَامَةُ رَفْعِهِ الضَّمَّةُ"
        comp = self.parser.parse(text)
        assert comp.confidence == 1.0

    def test_medium_confidence_type_and_case_only(self):
        """Type + case but no marker → confidence == 0.8."""
        text = "فَاعِلٌ مَرْفُوعٌ"
        comp = self.parser.parse(text)
        assert comp.confidence == 0.8

    def test_low_confidence_type_only(self):
        """Only type detected → confidence == 0.5."""
        text = "مُبْتَدَأٌ"
        comp = self.parser.parse(text)
        assert comp.confidence == 0.5

    def test_zero_confidence_empty_text(self):
        comp = self.parser.parse("")
        assert comp.confidence == 0.0

    def test_zero_confidence_unknown_text(self):
        """Text that matches nothing → confidence 0."""
        comp = self.parser.parse("نص غير معروف بدون تصنيف")
        assert comp.confidence == 0.0


class TestI3rabParserRawText:
    """Test raw text preservation."""

    def setup_method(self):
        self.parser = I3rabParser()

    def test_raw_text_preserved(self):
        text = "فَاعِلٌ مَرْفُوعٌ وَعَلَامَةُ رَفْعِهِ الضَّمَّةُ"
        comp = self.parser.parse(text)
        assert comp.raw_text == text

    def test_empty_raw_text(self):
        comp = self.parser.parse("")
        assert comp.raw_text == ""


class TestI3rabParserEdgeCases:
    """Test edge and real-corpus cases."""

    def setup_method(self):
        self.parser = I3rabParser()

    def test_la_mahall(self):
        """Detect لا محل له من الإعراب."""
        text = "حَرْفُ جَرٍّ مَبْنِيٌّ لَا مَحَلَّ لَهُ مِنَ الْإِعْرَابِ"
        comp = self.parser.parse(text)
        assert comp.mahall == "لا محل له من الإعراب"

    def test_fi_mahall_rafa(self):
        """Detect في محل رفع."""
        text = "فِعْلٌ مُضَارِعٌ فِي مَحَلِّ رَفْعٍ"
        comp = self.parser.parse(text)
        assert comp.mahall == "في محل رفع"

    def test_na_t(self):
        """Detect نعت in I3rab text."""
        text = "نَعْتٌ مَجْرُورٌ وَعَلَامَةُ جَرِّهِ الْكَسْرَةُ الظَّاهِرَةُ"
        comp = self.parser.parse(text)
        assert comp.i3rab_type == "نعت"

    def test_real_corpus_row_bismillah(self):
        """Reproduce first row of quran_i3rab.csv."""
        text = (
            '" الْبَاءُ " حَرْفُ جَرٍّ مَبْنِيٌّ عَلَى الْكَسْرِ، '
            'وَ( اسْمِ ) : اسْمٌ مَجْرُورٌ وَعَلَامَةُ جَرِّهِ الْكَسْرَةُ الظَّاهِرَةُ'
        )
        comp = self.parser.parse(text)
        # حرف should be detected (first match in text)
        assert comp.i3rab_type == "حرف"
        # Genitive should be extracted
        assert comp.case == "genitive"
