"""
قاعدة بيانات الكلمات المبنية والأدوات النحوية
Database of Indeclinable Words and Grammatical Operators
"""
import json
import csv
import os
import unicodedata
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

# Common prefixes (conjunction/particle) that may attach to another operator in text
# e.g. وََلَا = وَ + لَا, فَإِن = فَ + إِنْ
_OPERATOR_PREFIXES = ("وَ", "فَ", "أَ", "لَ", "بِ", "كَ", "سَ")
# Attached pronoun suffixes (normalized) to try stripping for e.g. فَإِنَّهُ → إِنَّ
_ATTACHED_PRONOUN_SUFFIXES = ("هُ", "هَا", "كُمْ", "كُنَّ", "نَا", "نِي", "هُمْ", "هُنَّ", "كُمَا", "هِ", "هِي")
SUKUN = "\u0652"

# Categories that are always mabni: default grammatical_status to "مبني" when missing in JSON
_MABNI_CATEGORIES = frozenset({
    "اسم موصول", "اسم إشارة", "ضمير", "أسماء الاستفهام", "أداة شرط", "أداة نداء",
    "ظرف", "اسم فعل", "أداة ربط", "حرف عطف", "أداة نحوية", "name",
})


def _resolve_operators_csv(base_path: Path) -> Optional[Path]:
    """Prefer enriched catalog, then plain; respect FVAFK_OPERATORS_CSV."""
    env = os.environ.get("FVAFK_OPERATORS_CSV")
    if env:
        p = Path(env).expanduser()
        if p.exists():
            return p
    candidates = [
        base_path / "data" / "operators_catalog_split_enriched.csv",
        base_path / "data" / "operators_catalog_split.csv",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


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
        """هل الكلمة مبنية؟ (يُعتبر مبنياً إذا ورد لفظ مبني في الحالة النحوية مع التشكيل أو بدونه)"""
        gs = self.grammatical_status or ""
        if "مبني" in gs:
            return True
        # الحالة قد تكون مَبْنِيٌّ أو مَبْنِيَّةٌ etc.
        gs_base = "".join(c for c in gs if unicodedata.category(c) != "Mn")
        return "مبني" in gs_base


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
            
            gs = self._get(item, "الحالة النحوية")
            if not gs and category in _MABNI_CATEGORIES:
                gs = "مبني"
            special_word = SpecialWord(
                word=variant,
                grammatical_status=gs,
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
        # أدوات الشرط قبل الظروف حتى تُخزَّن إِذَا كـ أداة شرط (لا ظرف فقط) — انظر docs/DATA_SOURCE_ISSUES.md
        self._load_conditionals()
        # أدوات النداء من الملف (قواعد/بيانات فقط — لا كلمات مضمّنة في الكود)
        self._load_vocative()
        self._load_adverbs()
        self._load_verbal_nouns()
        self._load_connectors()
        self._load_conjunctions()
        self._load_operators_from_csv()
        self._load_extra_mabniyat()
    
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
        file_path = self.data_dir / "الفصل الأول" / "اسم الإستفهام" / "الاستفهام (أقسام أدوات الاستفهام).json"
        
        if not file_path.exists():
            if self.verbose:
                print(f"File not found: {file_path}")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        count = sum(self._add_entry(item, "أسماء الاستفهام") for item in data)
        # تسجيل صيغ أيّ + هم (استفهام): أَيُّهُمْ، أَيُّهُم
        _key_ayyu = normalize_arabic("أَيُّ")
        if _key_ayyu in self.words_dict:
            for variant in ("أَيُّهُمْ", "أَيُّهُم"):
                k = normalize_arabic(variant)
                if k not in self.words_dict:
                    self.words_dict[k] = self.words_dict[_key_ayyu]
                    count += 1
        if self.verbose:
            print(f"Loaded {count} interrogatives (أسماء الاستفهام)")

    def _load_conditionals(self):
        """تحميل أدوات الشرط من المبنيات من الحروف (حتى تُخزَّن إِذَا كأداة شرط قبل الظروف)."""
        data_path = self.base_path / "data" / "arabic_json" / "2"
        file_path = data_path / "المبنيات من الحروف" / "حروف الشرط" / "ادوات الشرط.json"
        if not file_path.exists():
            if self.verbose:
                print(f"File not found: {file_path}")
            return
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = 0
        for item in data:
            word = self._get(item, "الأداة")
            if not word:
                continue
            # ادوات الشرط.json uses: الأداة، وظيفتها النحوية، الإعراب، الأمثلة، الملاحظات
            mapped = {
                "الأداة": word,
                "الحالة النحوية": self._get(item, "الإعراب") or "مبني",
                "وظيفتها النحوية": self._get(item, "وظيفتها النحوية"),
                "الأمثلة": self._get(item, "الأمثلة"),
                "التحليل النحوي": self._get(item, "الإعراب"),
                "التحليل الدلالي": self._get(item, "الملاحظات "),
                "الملاحظات": self._get(item, "الملاحظات "),
            }
            count += self._add_entry(mapped, "أداة شرط")
        if self.verbose:
            print(f"Loaded {count} conditionals (أدوات الشرط)")

    def _load_vocative(self):
        """تحميل أدوات النداء من ملف البيانات (المبنيات من الحروف). القاعدة في الملف فقط."""
        data_path = self.base_path / "data" / "arabic_json" / "2"
        file_path = data_path / "المبنيات من الحروف" / "ادوات النداء" / "أدوات النداء.json"
        if not file_path.exists():
            if self.verbose:
                print(f"File not found: {file_path}")
            return
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = 0
        for item in data:
            word = self._get(item, "الأداة")
            if not word or len(word) < 2 or "،" in word:
                continue
            mapped = {
                "الأداة": word,
                "الحالة النحوية": self._get(item, "التحليل النحوي") or "مبني",
                "النوع": self._get(item, "النوع"),
                "الأمثلة": self._get(item, "الأمثلة ", "الأمثلة"),
                "التحليل النحوي": self._get(item, "التحليل النحوي"),
                "التحليل الدلالي": self._get(item, "التحليل الدلالي"),
                "وظيفتها النحوية": self._get(item, "الإستخدامات") or self._get(item, "النوع"),
            }
            count += self._add_entry(mapped, "أداة نداء")
        if self.verbose:
            print(f"Loaded {count} vocative particles (أدوات النداء)")

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

    def _load_conjunctions(self):
        """تحميل حروف العطف (وَ، فَ، أَوْ، أَمْ، ...) من المبنيات من الحروف."""
        data_path = self.base_path / "data" / "arabic_json" / "2"
        file_path = data_path / "المبنيات من الحروف" / "حروف العطف" / "حروف العطف.json"
        if not file_path.exists():
            if self.verbose:
                print(f"File not found: {file_path}")
            return
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        def add_atf(item):
            if not isinstance(item, dict) or not item.get("الأداة"):
                return 0
            if not self._get(item, "الحالة النحوية"):
                item = {**item, "الحالة النحوية": "مبني"}
            return self._add_entry(item, "حرف عطف")
        count = sum(add_atf(item) for item in data)
        if self.verbose:
            print(f"Loaded {count} conjunctions (حروف العطف)")
    
    def _load_operators_from_csv(self):
        """تحميل الأدوات النحوية من ملف CSV (يفضّل enriched ثم fallback إلى plain)."""
        csv_path = _resolve_operators_csv(self.base_path)
        if csv_path is None:
            if self.verbose:
                print("Operators CSV not found (tried FVAFK_OPERATORS_CSV, enriched, plain).")
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

    def _load_extra_mabniyat(self):
        """إضافة مبنيات إضافية (مركبة أو غير موجودة في JSON) لتكون معالجة واحدة في كل المشروع."""
        extras = [
            ("أَلَّا", "أداة مصدرية ونافية", "مبني", "أنْ + لا، تنصب المضارع وتنفي"),
            ("ذَلِكُمْ", "اسم إشارة", "مبني", "ذلك + كم، للإشارة إلى الجمع المخاطب"),
            ("أُولَئِكَ", "اسم إشارة", "مبني", "لإشارة البعيد جمع مذكر"),
            ("أُولَئِكُمْ", "اسم إشارة", "مبني", "أولئك + كم"),
        ]
        count = 0
        for word, category, gs, func in extras:
            normalized = normalize_arabic(word)
            if normalized in self.words_dict:
                continue
            self.words_dict[normalized] = SpecialWord(
                word=word,
                grammatical_status=gs,
                number="",
                gender="",
                word_type=category,
                category=category,
                examples="",
                function=func,
                syntactic_analysis="",
                semantic_analysis="",
            )
            count += 1
        if self.verbose and count:
            print(f"Loaded {count} extra mabniyat (أدوات إضافية)")
    
    def lookup(self, word: str) -> Optional[SpecialWord]:
        """البحث عن كلمة - مع تطبيع"""
        normalized_word = normalize_arabic(word)
        return self.words_dict.get(normalized_word)

    def lookup_with_prefix_stripping(
        self, word: str
    ) -> Optional[Tuple[SpecialWord, Optional[str]]]:
        """
        Look up word; if not found, try stripping common prefixes (وَ, فَ, …) and
        lookup the remainder. Also tries remainder + sukun (e.g. إِن → إِنْ).
        Returns (SpecialWord, stripped_prefix_or_None). So وَلَا → (لَا entry, "وَ"), فَإِن → (إِنْ entry, "فَ").
        """
        direct = self.lookup(word)
        if direct:
            return (direct, None)
        normalized = normalize_arabic(word)
        for prefix in _OPERATOR_PREFIXES:
            if normalized.startswith(prefix) and len(normalized) > len(prefix):
                remainder = normalized[len(prefix) :]
                found = self.words_dict.get(remainder)
                if not found and remainder:
                    found = self.words_dict.get(remainder + SUKUN)
                if found:
                    return (found, prefix)
        return None

    def lookup_with_clitic_stripping(
        self, word: str
    ) -> Optional[Tuple[SpecialWord, Optional[str], Optional[str]]]:
        """
        Look up word; if not found, try prefix stripping then suffix (attached pronoun) stripping.
        E.g. فَإِنَّهُ → strip فَ → إِنَّهُ → strip هُ → إِنَّ → lookup.
        Returns (SpecialWord, stripped_prefix_or_None, stripped_suffix_or_None) or None.
        """
        direct = self.lookup(word)
        if direct:
            return (direct, None, None)
        normalized = normalize_arabic(word)
        # Try suffix-only stripping (e.g. ذَلِكُمْ → ذَلِكَ)
        for suffix in _ATTACHED_PRONOUN_SUFFIXES:
            if normalized.endswith(suffix) and len(normalized) > len(suffix):
                stem = normalized[:-len(suffix)]
                found = self.words_dict.get(stem)
                if not found and stem:
                    found = self.words_dict.get(stem + SUKUN)
                if found:
                    return (found, None, suffix)
        for prefix in _OPERATOR_PREFIXES:
            if normalized.startswith(prefix) and len(normalized) > len(prefix):
                remainder = normalized[len(prefix):]
                found = self.words_dict.get(remainder)
                if not found and remainder:
                    found = self.words_dict.get(remainder + SUKUN)
                if found:
                    return (found, prefix, None)
                for suffix in _ATTACHED_PRONOUN_SUFFIXES:
                    if remainder.endswith(suffix) and len(remainder) > len(suffix):
                        stem = remainder[:-len(suffix)]
                        found = self.words_dict.get(stem)
                        if not found and stem:
                            found = self.words_dict.get(stem + SUKUN)
                        if found:
                            return (found, prefix, suffix)
        return None

    def should_skip_root_extraction(self, word: str) -> bool:
        """Rule 2 & 5: أي كلمة في قاعدة البيانات (بادئة، لاحقة، أو كليهما) لا نستخرج جذرها."""
        if self.lookup(word) is not None:
            return True
        if self.lookup_with_prefix_stripping(word) is not None:
            return True
        return self.lookup_with_clitic_stripping(word) is not None
    
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