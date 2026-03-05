"""
محرك تحليل المقاطع الصوتية العربية
Arabic Syllable Analyzer Engine

This module analyzes Arabic text and breaks it down into phonetic syllables.
It supports various syllable patterns in Arabic phonology.

Common Arabic syllable patterns:
- CV: consonant + short vowel (صَ)
- CVV: consonant + long vowel (صا، صو، صي)
- CVC: consonant + short vowel + consonant (صَدْ)
- CVVC: consonant + long vowel + consonant (صود)
- CVCC: consonant + short vowel + two consonants (صَدْق)

Author: Eqratech Arabic Diana Project
Date: 2025-12-15
"""

import re
from typing import List, Tuple, Dict
import pandas as pd


class SyllableAnalyzer:
    """
    محلل المقاطع الصوتية للنصوص العربية
    Analyzes Arabic text and breaks it into phonetic syllables.
    """
    
    # Arabic diacritics (harakat)
    FATHA = '\u064E'  # َ
    DAMMA = '\u064F'  # ُ
    KASRA = '\u0650'  # ِ
    SUKUN = '\u0652'  # ْ
    SHADDA = '\u0651'  # ّ
    TANWIN_FATH = '\u064B'  # ً
    TANWIN_DAMM = '\u064C'  # ٌ
    TANWIN_KASR = '\u064D'  # ٍ
    MADD = '\u0653'  # ٓ
    
    # Long vowels
    ALIF = 'ا'
    WAW = 'و'
    YAA = 'ي'
    ALIF_MAQSURA = 'ى'
    
    # Pattern for Arabic letters (consonants)
    ARABIC_LETTERS = re.compile(r'[\u0621-\u064A]')
    
    # Pattern for diacritics
    DIACRITICS = re.compile(r'[\u064B-\u0652]')
    
    def __init__(self):
        """Initialize the syllable analyzer."""
        self.short_vowels = {self.FATHA, self.DAMMA, self.KASRA}
        self.long_vowels = {self.ALIF, self.WAW, self.YAA, self.ALIF_MAQSURA}
        self.tanwin = {self.TANWIN_FATH, self.TANWIN_DAMM, self.TANWIN_KASR}
        
    def remove_diacritics(self, text: str) -> str:
        """
        Remove all diacritics from Arabic text.
        
        Args:
            text: Arabic text with diacritics
            
        Returns:
            Text without diacritics
        """
        return self.DIACRITICS.sub('', text)
    
    def has_diacritics(self, text: str) -> bool:
        """Check if text contains diacritics."""
        return bool(self.DIACRITICS.search(text))
    
    def extract_syllables_with_diacritics(self, word: str) -> List[Dict[str, str]]:
        """
        Extract syllables from a fully vocalized (with harakat) Arabic word.
        
        Args:
            word: Fully vocalized Arabic word
            
        Returns:
            List of syllable dictionaries with type and structure
        """
        syllables = []
        current_syllable = ""
        syllable_type = ""
        
        i = 0
        while i < len(word):
            char = word[i]
            
            # Skip non-Arabic characters
            if not self.ARABIC_LETTERS.match(char) and char not in self.long_vowels:
                i += 1
                continue
            
            # Start building a syllable with a consonant
            if self.ARABIC_LETTERS.match(char):
                current_syllable = char
                i += 1
                
                # Check for diacritics after consonant
                if i < len(word):
                    next_char = word[i]
                    
                    # Short vowel (CV)
                    if next_char in self.short_vowels:
                        current_syllable += next_char
                        syllable_type = "CV"
                        i += 1
                        
                        # Check for long vowel after short vowel (CVV)
                        if i < len(word) and word[i] in self.long_vowels:
                            current_syllable += word[i]
                            syllable_type = "CVV"
                            i += 1
                            
                            # Check for consonant with sukun (CVVC)
                            if i < len(word) and self.ARABIC_LETTERS.match(word[i]):
                                if i + 1 < len(word) and word[i + 1] == self.SUKUN:
                                    current_syllable += word[i] + word[i + 1]
                                    syllable_type = "CVVC"
                                    i += 2
                        
                        # Check for consonant with sukun (CVC)
                        elif i < len(word) and self.ARABIC_LETTERS.match(word[i]):
                            if i + 1 < len(word) and word[i + 1] == self.SUKUN:
                                current_syllable += word[i] + word[i + 1]
                                syllable_type = "CVC"
                                i += 2
                                
                                # Check for another consonant with sukun (CVCC)
                                if i < len(word) and self.ARABIC_LETTERS.match(word[i]):
                                    if i + 1 < len(word) and word[i + 1] == self.SUKUN:
                                        current_syllable += word[i] + word[i + 1]
                                        syllable_type = "CVCC"
                                        i += 2
                    
                    # Sukun (consonant without vowel - part of previous syllable or cluster)
                    elif next_char == self.SUKUN:
                        current_syllable += next_char
                        syllable_type = "C"
                        i += 1
                    
                    # Shadda (gemination)
                    elif next_char == self.SHADDA:
                        current_syllable += next_char
                        i += 1
                        # Get the vowel after shadda
                        if i < len(word) and word[i] in self.short_vowels:
                            current_syllable += word[i]
                            syllable_type = "CCV"  # Geminated consonant with vowel
                            i += 1
                
                syllables.append({
                    'syllable': current_syllable,
                    'type': syllable_type,
                    'length': len(self.remove_diacritics(current_syllable))
                })
                current_syllable = ""
                syllable_type = ""
        
        return syllables
    
    def extract_syllables_simple(self, word: str) -> List[str]:
        """
        Extract syllables from unvocalized Arabic word using simple heuristics.
        
        Args:
            word: Arabic word without diacritics
            
        Returns:
            List of syllables (approximation)
        """
        # Remove any existing diacritics
        clean_word = self.remove_diacritics(word)
        syllables = []
        current = ""
        
        for i, char in enumerate(clean_word):
            if not self.ARABIC_LETTERS.match(char) and char not in self.long_vowels:
                continue
                
            current += char
            
            # Check if this forms a complete syllable
            # Simple heuristic: consonant + vowel or consonant + consonant
            if char in self.long_vowels:
                syllables.append(current)
                current = ""
            elif i + 1 < len(clean_word):
                next_char = clean_word[i + 1]
                if next_char in self.long_vowels:
                    continue  # Wait for the vowel
                else:
                    # Two consonants in a row - end syllable
                    if len(current) >= 2:
                        syllables.append(current)
                        current = ""
            else:
                # Last character
                syllables.append(current)
                current = ""
        
        if current:
            syllables.append(current)
        
        return syllables
    
    def analyze_word(self, word: str) -> Dict:
        """
        Analyze a single word and return detailed syllable information.
        
        Args:
            word: Arabic word (with or without diacritics)
            
        Returns:
            Dictionary with analysis results
        """
        has_harakat = self.has_diacritics(word)
        
        if has_harakat:
            syllables = self.extract_syllables_with_diacritics(word)
            syllable_count = len(syllables)
            syllable_types = [s['type'] for s in syllables]
            syllable_text = [s['syllable'] for s in syllables]
        else:
            syllable_text = self.extract_syllables_simple(word)
            syllable_count = len(syllable_text)
            syllable_types = ['CV' for _ in syllable_text]  # Approximate
            syllables = [{'syllable': s, 'type': 'CV', 'length': len(s)} for s in syllable_text]
        
        return {
            'word': word,
            'has_diacritics': has_harakat,
            'syllable_count': syllable_count,
            'syllables': syllables,
            'syllable_types': syllable_types,
            'syllable_text': syllable_text,
            'pattern': '-'.join(syllable_types)
        }
    
    def analyze_text(self, text: str) -> pd.DataFrame:
        """
        Analyze entire text and return results as DataFrame.
        
        Args:
            text: Arabic text (can be multiple words)
            
        Returns:
            DataFrame with analysis for each word
        """
        # Split text into words
        words = text.strip().split()
        
        results = []
        for word in words:
            if not word.strip():
                continue
            
            analysis = self.analyze_word(word)
            results.append({
                'الكلمة': word,
                'عدد المقاطع': analysis['syllable_count'],
                'المقاطع': ' + '.join(analysis['syllable_text']),
                'أنواع المقاطع': analysis['pattern'],
                'مُشَكَّلة': 'نعم' if analysis['has_diacritics'] else 'لا',
                'التفاصيل': str(analysis['syllables'])
            })
        
        return pd.DataFrame(results)
    
    def analyze_surah_fatiha(self) -> pd.DataFrame:
        """
        Analyze Surah Al-Fatiha as an example.
        
        Returns:
            DataFrame with syllable analysis
        """
        # Surah Al-Fatiha with full diacritics
        fatiha_lines = [
            "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
            "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
            "الرَّحْمَٰنِ الرَّحِيمِ",
            "مَالِكِ يَوْمِ الدِّينِ",
            "إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ",
            "اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ",
            "صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ"
        ]
        
        all_results = []
        for verse_num, verse in enumerate(fatiha_lines, 1):
            verse_analysis = self.analyze_text(verse)
            verse_analysis.insert(0, 'رقم الآية', verse_num)
            all_results.append(verse_analysis)
        
        return pd.concat(all_results, ignore_index=True)
    
    def save_analysis_to_excel(self, dataframe: pd.DataFrame, filename: str = "syllable_analysis.xlsx"):
        """
        Save analysis results to Excel file.
        
        Args:
            dataframe: Analysis results
            filename: Output filename
        """
        dataframe.to_excel(filename, index=False, sheet_name='تحليل المقاطع')
        print(f"✓ تم حفظ التحليل في: {filename}")
        print(f"  عدد الكلمات المحللة: {len(dataframe)}")


def main():
    """Main function to demonstrate syllable analysis."""
    print("=" * 60)
    print("محرك تحليل المقاطع الصوتية العربية")
    print("Arabic Syllable Analyzer Engine")
    print("=" * 60)
    
    analyzer = SyllableAnalyzer()
    
    # Example 1: Analyze Surah Al-Fatiha
    print("\n📖 تحليل سورة الفاتحة:")
    print("-" * 60)
    fatiha_df = analyzer.analyze_surah_fatiha()
    print(fatiha_df.to_string())
    
    # Save to Excel
    analyzer.save_analysis_to_excel(fatiha_df, "surah_fatiha_syllables.xlsx")
    
    # Example 2: Analyze custom text
    print("\n\n📝 مثال آخر - تحليل نص مخصص:")
    print("-" * 60)
    custom_text = "الْحَمْدُ لِلَّهِ"
    custom_df = analyzer.analyze_text(custom_text)
    print(custom_df.to_string())
    
    # Example 3: Analyze word by word
    print("\n\n🔍 تحليل تفصيلي لكلمة:")
    print("-" * 60)
    word = "الْحَمْدُ"
    analysis = analyzer.analyze_word(word)
    print(f"الكلمة: {word}")
    print(f"عدد المقاطع: {analysis['syllable_count']}")
    print(f"المقاطع: {analysis['syllable_text']}")
    print(f"النمط: {analysis['pattern']}")
    print(f"\nتفاصيل المقاطع:")
    for i, syl in enumerate(analysis['syllables'], 1):
        print(f"  {i}. {syl['syllable']} - نوع: {syl['type']}")
    
    print("\n" + "=" * 60)
    print("✓ اكتمل التحليل بنجاح!")
    print("=" * 60)


if __name__ == "__main__":
    main()
