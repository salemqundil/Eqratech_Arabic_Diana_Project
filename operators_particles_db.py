"""
قاعدة بيانات الكلمات المبنية والأدوات النحوية
Database of Indeclinable Words and Grammatical Operators
"""
import json
import csv
import unicodedata
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass


def normalize_arabic(text: str) -> str:
    """
    تطبيع النص العربي - إعادة ترتيب التشكيل بطريقة موحدة
    Unicode Normalization Form C (NFC)
    """
    return unicodedata.normalize('NFC', text)


@dataclass
class SpecialWord:
    """معلومات الكلمة المبنية"""
    word: str
    grammatical_status: str
    number: str
    gender: str
    word_type: str
    category: str
    examples: str
    function: str
    syntactic_analysis: str
    semantic_analysis: str
    
    @property
    def is_mabni(self) -> bool:
        """هل الكلمة مبنية؟"""
        return "مبني" in self.grammatical_status


class SpecialWordsDatabase:
    """قاعدة بيانات الكلمات المبنية والأدوات النحوية"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.base_path = Path(__file__).parent.parent.parent.parent
        data_path = self.base_path / "data" / "arabic_json" / "2"
        self.data_dir = data_path / "المبنيات من الأسماء والأدوات "
        self.words_dict = {}
        self._load_all()
    
    def _get(self, item: dict, *keys):
        """محاولة الحصول على قيمة من عدة مفاتيح محتملة"""
        for key in keys:
            val = item.get(key, "").strip()
            if val:
                return val
        return ""
    
    def _add_entry(self, item: dict, category: str):
        """إضافة عنصر إلى قاعدة البيانات"""
        word = self._get(item, "الأداة")
        if not word:
            return 0
        
        # معالجة الكلمات المتعددة (مثل: الكلمة1 / الكلمة2)
        variants = [w.strip() for w in word.split('/')]
        
        count = 0
        for variant in variants:
            if not variant:
                continue
            
            special_word = SpecialWord(
                word=variant,
                grammatical_status=self._get(item, "الحالة النحوية"),
                number=self._get(item, "العدد", "الصيغة"),
                gender=self._get(item, "الجنس", "الجنس "),
                word_type=self._get(item, "النوع"),
                category=category,
                examples=self._get(item, "الأمثلة", "الأمثلة "),
                function=self._get(item, "عملها", "وظيفتها النحوية", "المعنى", "دلالته"),
                syntactic_analysis=self._get(item, "التحليل النحوي", "الموقع الإعرابي لما بعدها"),
                semantic_analysis=self._get(item, "التحليل الدلالي", "الملاحظات")
            )
            
            normalized = normalize_arabic(variant)
            if normalized not in self.words_dict:
                self.words_dict[normalized] = special_word
                count += 1
        
        return count
    
    def _load_all(self):
        """تحميل جميع الفئات"""
        self._load_relative_pronouns()
        self._load_demonstratives()
        self._load_pronouns()
        self._load_interrogatives()
        self._load_adverbs()
        self._load_verbal_nouns()
        self._load_connectors()
        self._load_operators_from_csv()
    
    def _load_relative_pronouns(self):
        """تحميل أسماء الموصول"""
        file_path = self.data_dir / "الفصل الأول" / "الاسم  الموصول" / "الاسم الموصول.json"
        
        if not file_path.exists():
            if self.verbose:
                print(f"File not found: {file_path}")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        count = sum(self._add_entry(item, "اسم موصول") for item in data)
        
        if self.verbose:
            print(f"Loaded {count} relative pronouns (اسم موصول)")
    
    def _load_demonstratives(self):
        """تحميل أسماء الإشارة"""
        file_path = self.data_dir / "الفصل الأول" / "اسم الإشارة" / "أسماء الإشارة.json"
        
        if not file_path.exists():
            if self.verbose:
                print(f"File not found: {file_path}")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        count = sum(self._add_entry(item, "اسم إشارة") for item in data)
        
        if self.verbose:
            print(f"Loaded {count} demonstratives (أسماء الإشارة)")
    
    def _load_pronouns(self):
        """تحميل الضمائر"""
        file_path = self.data_dir / "الفصل الثاني" / "الأسماء المبنية الضمائر (  الضمائر المنفصلة والمتصلة ).json"
        
        if not file_path.exists():
            if self.verbose:
                print(f"File not found: {file_path}")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        count = sum(self._add_entry(item, "ضمير") for item in data)
        
        if self.verbose:
            print(f"Loaded {count} pronouns (ضمائر)")
    
    def _load_interrogatives(self):
        """تحميل أسماء الاستفهام"""
        file_path = self.data_dir / "الفصل الأول" / "اسم الاستفهام" / "الاستفهام (أقسام أدوات الاستفهام).json"
        
        if not file_path.exists():
            if self.verbose:
                print(f"File not found: {file_path}")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        count = sum(self._add_entry(item, "أسماء الاستفهام") for item in data)
        
        if self.verbose:
            print(f"Loaded {count} interrogatives (أسماء الاستفهام)")
    
    def _load_adverbs(self):
        """تحميل الظروف المبنية"""
        file_path = self.data_dir / "الفصل الأول" / "الظروف المبنية" / "الظروف المبنية.json"
        
        if not file_path.exists():
            if self.verbose:
                print(f"File not found: {file_path}")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        count = sum(self._add_entry(item, "ظرف") for item in data)
        
        if self.verbose:
            print(f"Loaded {count} adverbs (ظروف مبنية)")
    
    def _load_verbal_nouns(self):
        """تحميل أسماء الأفعال"""
        file_path = self.data_dir / "الفصل الأول" / "اسم الفعل" / "اسم الفعل_.json"
        
        if not file_path.exists():
            if self.verbose:
                print(f"File not found: {file_path}")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        count = sum(self._add_entry(item, "اسم فعل") for item in data)
        
        if self.verbose:
            print(f"Loaded {count} verbal nouns (أسماء الأفعال)")
    
    def _load_connectors(self):
        """تحميل أدوات الربط من جميع الملفات"""
        connectors_dir = self.data_dir / "الفصل الأول" / "أدوات الربط" / "أدوات الربط"
        
        if not connectors_dir.exists():
            if self.verbose:
                print(f"Directory not found: {connectors_dir}")
            return
        
        total_count = 0
        for json_file in connectors_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                count = sum(self._add_entry(item, "أداة ربط") for item in data)
                total_count += count
            except Exception as e:
                if self.verbose:
                    print(f"Error loading {json_file}: {e}")
        
        if self.verbose:
            print(f"Loaded {total_count} connector entries (أدوات الربط)")
    
    def _load_operators_from_csv(self):
        """تحميل الأدوات النحوية من ملف CSV"""
        csv_path = self.base_path / "data" / "operators_catalog_split.csv"
        
        if not csv_path.exists():
            if self.verbose:
                print(f"CSV file not found: {csv_path}")
            return
        
        count = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                operator = row.get('Operator', '').strip()
                if not operator or operator == 'Operator':  # تخطي رؤوس مكررة
                    continue
                
                # تحديد الفئة من الاسم العربي
                arabic_group = row.get('Arabic Group Name', '').strip()
                
                # تحديد الحالة الإعرابية
                grammatical_status = "مبني"  # معظم الحروف والأدوات مبنية
                
                # Create SpecialWord entry
                special_word = SpecialWord(
                    word=operator,
                    grammatical_status=grammatical_status,
                    number="",
                    gender="",
                    word_type=row.get('Purpose/Usage', ''),
                    category=f"أداة نحوية - {arabic_group}" if arabic_group else "أداة نحوية",
                    examples=row.get('Example', ''),
                    function=row.get('Purpose/Usage', ''),
                    syntactic_analysis=row.get('Note', ''),
                    semantic_analysis=""
                )
                
                # Normalize and store
                normalized = normalize_arabic(operator)
                if normalized not in self.words_dict:
                    self.words_dict[normalized] = special_word
                    count += 1
        
        if self.verbose:
            print(f"Loaded {count} operators from CSV (أدوات نحوية)")
    
    def lookup(self, word: str) -> Optional[SpecialWord]:
        """البحث عن كلمة - مع تطبيع"""
        normalized_word = normalize_arabic(word)
        return self.words_dict.get(normalized_word)
    
    def should_skip_root_extraction(self, word: str) -> bool:
        """هل يجب تخطي استخراج الجذر؟"""
        special = self.lookup(word)
        return special is not None  # أي كلمة في قاعدة البيانات لا نستخرج جذرها
    
    def get_analysis(self, word: str) -> Optional[Dict]:
        """الحصول على التحليل الكامل"""
        special = self.lookup(word)
        if not special:
            return None
        
        return {
            "word": word,
            "category": special.category,
            "grammatical_status": special.grammatical_status,
            "is_mabni": special.is_mabni,
            "number": special.number,
            "gender": special.gender,
            "root": None
        }


_global_db = None


def get_special_words_db():
    """الحصول على قاعدة البيانات العامة"""
    global _global_db
    if _global_db is None:
        _global_db = SpecialWordsDatabase(verbose=False)
    return _global_db


if __name__ == "__main__":
    print("=" * 70)
    print("Testing Special Words Database (المبنيات) - All Categories")
    print("=" * 70)
    
    db = SpecialWordsDatabase(verbose=True)
    
    print(f"\nTotal unique words loaded: {len(db.words_dict)}")
    
    test_words = [
        "مَنْ",      # اسم موصول
        "مِنْ",      # حرف جر من CSV
        "الَّذِينَ",  # اسم موصول
        "الَّذِي",    # اسم موصول
        "هذا",       # اسم إشارة
        "هذه",       # اسم إشارة
        "هُوَ",      # ضمير
        "أَنَا",     # ضمير
        "حَيْثُ",    # ظرف
        "آمِينَ",    # اسم فعل
        "مَا",       # اسم موصول
        "لا",        # أداة ربط
        "إِنَّ",     # أداة توكيد من CSV
        "بِ",        # حرف جر من CSV
    ]
    
    print("\nTest Results:")
    print(f"{'Word':<20} {'Found?':<10} {'Category':<30} {'Status'}")
    print("─" * 70)
    
    for word in test_words:
        result = db.lookup(word)
        found = "✅ YES" if result else "❌ NO"
        category = result.category if result else "---"
        is_mabni = f"(مبني)" if result and result.is_mabni else ""
        print(f"{word:<20} {found:<10} {category:<30} {is_mabni}")