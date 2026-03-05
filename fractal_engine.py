"""
محرك الأنماط الكسيرية (Fractal Pattern Engine)
Fractal Pattern Engine for Arabic Text Analysis

This engine analyzes and generates fractal-like recursive patterns in Arabic text,
including morphological recursion, semantic patterns, and structural self-similarity.

In Arabic linguistics, fractal patterns can be found in:
- Root-pattern morphology (الاشتقاق)
- Recursive phrase structures
- Semantic field relationships
- Rhythmic and phonetic patterns

Author: Eqratech Arabic Diana Project
Date: 2025-12-15
"""

import pandas as pd
from typing import List, Dict, Tuple, Set
import re
from base_reconstruction_engine import BaseReconstructionEngine
from reconstruction_utils import reconstruct_from_base_df


class FractalPatternEngine(BaseReconstructionEngine):
    """
    محرك تحليل الأنماط الكسيرية في اللغة العربية
    Analyzes fractal (recursive, self-similar) patterns in Arabic text.
    """
    
    SHEET_NAME = 'الأنماط_الكسيرية'
    
    # Arabic root patterns (أوزان) that demonstrate fractal-like properties
    FRACTAL_PATTERNS = [
        {
            "pattern": "فَعَّلَ",
            "structure": "C1aC2C2aC3",
            "type": "تكرار صوتي",
            "example": "كَسَّرَ",
            "description": "تكرار الحرف الثاني يخلق بُنية متكررة"
        },
        {
            "pattern": "تَفَعَّلَ",
            "structure": "taC1aC2C2aC3",
            "type": "بناء متداخل",
            "example": "تَكَسَّرَ",
            "description": "بناء متداخل مع تكرار داخلي"
        },
        {
            "pattern": "اِفْتَعَلَ",
            "structure": "iC1taC2aC3",
            "type": "نمط افتعال",
            "example": "اِكْتَسَبَ",
            "description": "إدماج تاء الافتعال في البنية"
        },
        {
            "pattern": "اِسْتَفْعَلَ",
            "structure": "istaC1C2aC3",
            "type": "استفعال مركب",
            "example": "اِسْتَخْرَجَ",
            "description": "بناء ثلاثي مع زيادات متعددة"
        },
        {
            "pattern": "فَعْلَلَ",
            "structure": "C1aC2C3C4",
            "type": "رباعي مجرد",
            "example": "دَحْرَجَ",
            "description": "أصل رباعي مع تماثل صوتي"
        },
        {
            "pattern": "تَفَعْلَلَ",
            "structure": "taC1aC2C3C4",
            "type": "رباعي مزيد",
            "example": "تَدَحْرَجَ",
            "description": "رباعي مع زيادة تاء البناء"
        },
    ]
    
    # Recursive semantic patterns
    SEMANTIC_RECURSION = [
        {
            "root": "ك ت ب",
            "derivatives": ["كَاتِب", "مَكْتُوب", "كِتَاب", "مَكْتَب", "كُتَّاب"],
            "recursion_type": "اشتقاق متسلسل",
            "pattern_depth": 3
        },
        {
            "root": "ع ل م",
            "derivatives": ["عَالِم", "مَعْلُوم", "عِلْم", "تَعْلِيم", "مُعَلِّم"],
            "recursion_type": "اشتقاق معرفي",
            "pattern_depth": 3
        },
        {
            "root": "ق و ل",
            "derivatives": ["قَائِل", "مَقُول", "قَوْل", "مَقَال", "مِقْوَل"],
            "recursion_type": "اشتقاق كلامي",
            "pattern_depth": 2
        },
    ]
    
    @classmethod
    def make_df(cls):
        """Generate DataFrame with fractal pattern analysis."""
        rows = []
        
        # Add morphological fractal patterns
        for pattern_data in cls.FRACTAL_PATTERNS:
            pattern_name = pattern_data["pattern"]
            structure = pattern_data["structure"]
            pattern_type = pattern_data["type"]
            example = pattern_data["example"]
            description = pattern_data["description"]
            
            # Calculate recursion depth based on repeated elements
            recursion_depth = cls._calculate_recursion_depth(structure)
            
            rows.append({
                "الأداة": pattern_name,
                "القالب/التركيب": structure,
                "النوع": "نمط صرفي كسيري",
                "مثال": example,
                "الفونيمات": " ".join(list(pattern_name)),
                "الحركات": cls._extract_harakat(pattern_name),
                "عمق التكرار": recursion_depth,
                "الأثر الإعرابي": "حسب الموقع",
                "شرط/سياق": pattern_type,
                "الوظيفة النحوية": "فعل أو اسم مشتق",
                "الوظيفة الدلالية": description,
                "الوظيفة الصرفية": f"وزن {pattern_name}",
                "الوظيفة الصوتية": cls._analyze_phonetic_pattern(pattern_name),
                "الوظيفة الاشتقاقية": "نمط اشتقاقي متكرر",
                "ملاحظات": f"نمط كسيري من نوع: {pattern_type}"
            })
        
        # Add semantic recursion patterns
        for semantic_data in cls.SEMANTIC_RECURSION:
            root = semantic_data["root"]
            derivatives = semantic_data["derivatives"]
            recursion_type = semantic_data["recursion_type"]
            depth = semantic_data["pattern_depth"]
            
            # Create entries for each derivative showing the recursive relationship
            for idx, derivative in enumerate(derivatives):
                rows.append({
                    "الأداة": derivative,
                    "القالب/التركيب": f"مشتق من جذر: {root}",
                    "النوع": "نمط دلالي كسيري",
                    "مثال": derivative,
                    "الفونيمات": " ".join(list(derivative)),
                    "الحركات": cls._extract_harakat(derivative),
                    "عمق التكرار": depth,
                    "الأثر الإعرابي": "حسب الموقع",
                    "شرط/سياق": recursion_type,
                    "الوظيفة النحوية": cls._determine_grammatical_function(derivative),
                    "الوظيفة الدلالية": f"مشتق {idx + 1} من الجذر {root}",
                    "الوظيفة الصرفية": cls._determine_morphological_function(derivative),
                    "الوظيفة الصوتية": cls._analyze_phonetic_pattern(derivative),
                    "الوظيفة الاشتقاقية": f"اشتقاق متكرر - مستوى {idx + 1}",
                    "ملاحظات": f"جزء من سلسلة اشتقاقية كسيرية"
                })
        
        # Add compound recursive structures
        compound_structures = cls._generate_compound_recursive_structures()
        rows.extend(compound_structures)
        
        dataframe = pd.DataFrame(rows)
        return reconstruct_from_base_df(dataframe)
    
    @staticmethod
    def _calculate_recursion_depth(structure: str) -> int:
        """
        Calculate the recursion depth of a morphological structure.
        Depth is based on repeated elements and nested patterns.
        """
        # Count repeated consonants (C followed by number)
        consonant_pattern = re.findall(r'C\d', structure)
        unique_consonants = set(consonant_pattern)
        
        # If consonants repeat, increase depth
        depth = 1
        if len(consonant_pattern) > len(unique_consonants):
            depth += (len(consonant_pattern) - len(unique_consonants))
        
        # Check for prefixes (t, i, st, etc.)
        if structure.startswith('ta') or structure.startswith('ista'):
            depth += 1
        
        return depth
    
    @staticmethod
    def _extract_harakat(text: str) -> str:
        """Extract diacritical marks (harakat) from Arabic text."""
        harakat_pattern = re.compile(r'[\u064B-\u0652]')
        harakat = harakat_pattern.findall(text)
        return " ".join(harakat) if harakat else "بدون تشكيل"
    
    @staticmethod
    def _analyze_phonetic_pattern(text: str) -> str:
        """Analyze the phonetic pattern of the text."""
        # Remove diacritics for analysis
        clean_text = re.sub(r'[\u064B-\u0652]', '', text)
        
        length = len(clean_text)
        if length <= 3:
            return "قصير"
        elif length <= 5:
            return "متوسط"
        else:
            return "طويل"
    
    @staticmethod
    def _determine_grammatical_function(word: str) -> str:
        """Determine the grammatical function based on morphological markers."""
        # Simple heuristic based on common patterns
        if word.startswith("مُ") or word.startswith("مَ"):
            return "اسم مفعول أو اسم مكان"
        elif word.endswith("ِم") or word.endswith("َة"):
            return "اسم"
        elif "ـِـ" in word or "ـَـ" in word:
            return "فعل"
        else:
            return "اسم أو فعل"
    
    @staticmethod
    def _determine_morphological_function(word: str) -> str:
        """Determine morphological function."""
        if any(marker in word for marker in ["كَاتِب", "عَالِم", "قَائِل"]):
            return "اسم فاعل"
        elif any(marker in word for marker in ["مَكْتُوب", "مَعْلُوم"]):
            return "اسم مفعول"
        else:
            return "مشتق"
    
    @staticmethod
    def _generate_compound_recursive_structures() -> List[Dict]:
        """Generate compound structures showing recursive patterns."""
        structures = []
        
        # Nested phrase structures (التركيب المتداخل)
        nested_phrases = [
            {
                "phrase": "الكتاب الذي في البيت الذي في المدينة",
                "recursion_type": "تركيب متداخل",
                "nesting_level": 3,
                "description": "جملة موصولية متداخلة"
            },
            {
                "phrase": "قال أنه قال أنه سيأتي",
                "recursion_type": "تضمين متكرر",
                "nesting_level": 2,
                "description": "أفعال قولية متداخلة"
            },
        ]
        
        for phrase_data in nested_phrases:
            phrase = phrase_data["phrase"]
            recursion_type = phrase_data["recursion_type"]
            level = phrase_data["nesting_level"]
            description = phrase_data["description"]
            
            structures.append({
                "الأداة": phrase[:20] + "..." if len(phrase) > 20 else phrase,
                "القالب/التركيب": "تركيب جملي متداخل",
                "النوع": "نمط نحوي كسيري",
                "مثال": phrase,
                "الفونيمات": " ".join(phrase.split()[:3]),  # First 3 words
                "الحركات": "متنوع",
                "عمق التكرار": level,
                "الأثر الإعرابي": "جملة كاملة",
                "شرط/سياق": recursion_type,
                "الوظيفة النحوية": "جملة متداخلة",
                "الوظيفة الدلالية": description,
                "الوظيفة الصرفية": "تركيب جملي",
                "الوظيفة الصوتية": "طويل ومركب",
                "الوظيفة الاشتقاقية": "بنية نحوية متكررة",
                "ملاحظات": f"مستوى التداخل: {level}"
            })
        
        return structures


class FractalAnalyzer:
    """
    محلل الأنماط الكسيرية - أداة مساعدة
    Utility class for analyzing fractal patterns in custom text.
    """
    
    def __init__(self):
        """Initialize the fractal analyzer."""
        self.engine = FractalPatternEngine()
    
    def analyze_root_derivatives(self, root: str) -> pd.DataFrame:
        """
        Analyze all derivatives of a given Arabic root.
        
        Args:
            root: Arabic root (e.g., "ك ت ب")
            
        Returns:
            DataFrame with derivative analysis
        """
        # This is a simplified version - in production would use full morphological database
        results = []
        root_clean = root.replace(" ", "")
        
        # Common derivative patterns
        patterns = [
            ("فاعل", f"{root_clean[0]}ا{root_clean[1]}ِ{root_clean[2]}"),
            ("مفعول", f"م{root_clean[0]}{root_clean[1]}و{root_clean[2]}"),
            ("فعل", f"{root_clean}"),
        ]
        
        for pattern_name, _ in patterns:
            results.append({
                "الجذر": root,
                "الوزن": pattern_name,
                "النوع": "مشتق",
                "عمق_الاشتقاق": 1
            })
        
        return pd.DataFrame(results)
    
    def find_recursive_patterns(self, text: str) -> Dict:
        """
        Find recursive/repeating patterns in Arabic text.
        
        Args:
            text: Arabic text to analyze
            
        Returns:
            Dictionary with pattern analysis
        """
        words = text.split()
        
        # Find repeated words
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        repeated_words = {w: c for w, c in word_counts.items() if c > 1}
        
        # Find repeated roots (simplified - just look for word patterns)
        patterns = {}
        for word in words:
            if len(word) >= 3:
                # Simple pattern: first 3 letters
                pattern = word[:3]
                patterns[pattern] = patterns.get(pattern, 0) + 1
        
        return {
            "repeated_words": repeated_words,
            "pattern_frequency": patterns,
            "recursion_detected": len(repeated_words) > 0 or any(c > 1 for c in patterns.values())
        }
    
    def generate_fractal_report(self, text: str) -> pd.DataFrame:
        """
        Generate a comprehensive fractal pattern report for given text.
        
        Args:
            text: Arabic text to analyze
            
        Returns:
            DataFrame with comprehensive analysis
        """
        analysis = self.find_recursive_patterns(text)
        
        results = []
        for word, count in analysis['repeated_words'].items():
            results.append({
                "العنصر": word,
                "نوع_النمط": "تكرار كلمة",
                "عدد_التكرارات": count,
                "مستوى_الكسيرية": "عالي" if count > 2 else "متوسط"
            })
        
        return pd.DataFrame(results) if results else pd.DataFrame({
            "العنصر": ["لا يوجد"],
            "نوع_النمط": ["---"],
            "عدد_التكرارات": [0],
            "مستوى_الكسيرية": ["منخفض"]
        })


def main():
    """Main function to demonstrate fractal pattern engine."""
    print("=" * 70)
    print("محرك الأنماط الكسيرية في اللغة العربية")
    print("Arabic Fractal Pattern Engine")
    print("=" * 70)
    
    # Generate the main dataframe
    engine = FractalPatternEngine()
    dataframe = engine.make_df()
    
    print("\n📊 عينة من الأنماط الكسيرية المحللة:")
    print("-" * 70)
    print(dataframe[['الأداة', 'النوع', 'عمق التكرار', 'الوظيفة الدلالية']].head(10).to_string())
    
    print(f"\n✓ إجمالي الأنماط: {len(dataframe)}")
    print(f"✓ أنواع الأنماط: {dataframe['النوع'].nunique()}")
    
    # Demonstrate the analyzer
    print("\n" + "=" * 70)
    print("🔍 تحليل نص مخصص:")
    print("-" * 70)
    
    analyzer = FractalAnalyzer()
    sample_text = "الكتاب الكبير في المكتبة الكبيرة يحتوي على كتب كثيرة"
    
    patterns = analyzer.find_recursive_patterns(sample_text)
    print(f"\nالنص: {sample_text}")
    print(f"\nالكلمات المتكررة: {patterns['repeated_words']}")
    print(f"الأنماط المكتشفة: {len(patterns['pattern_frequency'])}")
    print(f"تم اكتشاف تكرار كسيري: {'نعم' if patterns['recursion_detected'] else 'لا'}")
    
    # Generate report
    report_df = analyzer.generate_fractal_report(sample_text)
    print("\n📈 تقرير التكرار:")
    print(report_df.to_string())
    
    # Save to Excel
    try:
        dataframe.to_excel("fractal_patterns_analysis.xlsx", index=False, sheet_name='الأنماط_الكسيرية')
        print(f"\n✓ تم حفظ التحليل في: fractal_patterns_analysis.xlsx")
    except Exception as error:
        print(f"\n⚠ تعذر الحفظ: {str(error)}")
    
    print("\n" + "=" * 70)
    print("✓ اكتمل تحليل الأنماط الكسيرية")
    print("=" * 70)


if __name__ == "__main__":
    main()
