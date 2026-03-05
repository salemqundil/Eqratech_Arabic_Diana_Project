import pandas as pd
import os
from pathlib import Path

class ComprehensiveSentenceGenerator:
    """
    مولد جمل شامل يستخدم جميع الـ engines المتاحة لإنتاج تشكيلات كاملة
    مع خوارزميات لاستثناء التراكيب غير الصحيحة نحوياً
    """
    
    def __init__(self):
        self.engines_data = {}
        self.sentences = []
        self.seen_sentences = set()
        self.MAX_SENTENCES = 5000  # زيادة الحد الأقصى للشمولية
        
    def load_all_engines(self):
        """تحميل جميع المحركات المتاحة"""
        print("[INFO] بدء تحميل جميع المحركات...")
        
        # قائمة المحركات المطلوبة
        engine_modules = [
            # النحو الأساسي
            ('فاعل', 'fael_engine', 'FaelEngine'),
            ('مفعول_به', 'mafoul_bih_engine', 'MafoulBihEngine'),
            ('مفعول_لأجله', 'mafoul_ajlih_engine', 'MafoulAjlihEngine'),
            ('مفعول_مطلق', 'mafoul_mutlaq_engine', 'MafoulMutlaqEngine'),
            ('نائب_فاعل', 'naeb_fael_engine', 'NaebFaelEngine'),
            ('مبتدأ_خبر', 'mobtada_khabar_engine', 'MobtadaKhabarEngine'),
            ('حال', 'haal_engine', 'HaalEngine'),
            ('تمييز', 'tamyeez_engine', 'TamyeezEngine'),
            ('نداء', 'nidha_engine', 'NidhaEngine'),
            ('استفهام', 'istifham_engine', 'IstifhamEngine'),
            ('استثناء', 'istithna_engine', 'IstithnaEngine'),
            ('شرط', 'shart_engine', 'ShartEngine'),
            
            # الضمائر والإشارة والموصولات
            ('أسماء_إشارة', 'demonstratives_engine', 'DemonstrativesEngine'),
            ('أسماء_موصولة', 'relatives_engine', 'RelativesEngine'),
            ('ضمائر', 'pronouns_engine', 'PronounsEngine'),
            
            # الأفعال والمشتقات
            ('أفعال', 'verbs_engine', 'VerbsEngine'),
            ('اسم_فاعل', 'active_participle_engine', 'ActiveParticipleEngine'),
            ('اسم_مفعول', 'passive_participle_engine', 'PassiveParticipleEngine'),
            ('أفعل_تفضيل', 'superlative_engine', 'SuperlativeEngine'),
            ('اسم_فعل', 'ism_fiil_engine', 'IsmFiilEngine'),
            
            # الظروف والأماكن والأزمنة
            ('أماكن', 'place_engine', 'PlaceEngine'),
            ('أزمنة', 'time_engine', 'TimeEngine'),
            ('ظروف', 'adverbs_engine', 'AdverbsEngine'),
            
            # التعريف والتنكير والجنس والعدد
            ('تعريف_تنكير', 'definiteness_engine', 'DefinitenessEngine'),
            ('جنس', 'gender_engine', 'GenderEngine'),
            ('عدد_جنس', 'number_gender_suffixes_engine', 'NumberGenderSuffixesEngine'),
            
            # الأدوات النحوية
            ('نواسخ', 'nasikh_engine', 'NasikhEngine'),
            ('جوازم', 'jazm_engine', 'JazmEngine'),
            ('نواصب', 'nasb_engine', 'NasbEngine'),
            ('قصر', 'qasr_engine', 'QasrEngine'),
            ('توكيد', 'tawkid_engine', 'TawkidEngine'),
            ('تحضيض', 'tahdidh_engine', 'TahdidhEngine'),
            
            # العطف والنفي وحروف الجر
            ('عطف', 'atf_engine', 'AtfEngine'),
            ('نفي', 'nafi_engine', 'NafiEngine'),
            ('جر', 'jar_engine', 'JarEngine'),
            
            # الأسماء والأدوات العامة
            ('أعلام_أشخاص', 'a3lam_ashkhas_engine', 'A3lamAshkhasEngine'),
            ('أعلام_أماكن', 'a3lam_amakin_engine', 'A3lamAmakinEngine'),
            ('أعلام_منقولة', 'a3lam_manqula_engine', 'A3lamManqulaEngine'),
            ('أسماء_عامة', 'generic_nouns_engine', 'GenericNounsEngine'),
            ('أسماء_ميمية', 'mimi_nouns_engine', 'MimiNounsEngine'),
            ('أدوات', 'particles_engine', 'ParticlesEngine'),
            
            # الأرقام والأعداد
            ('أعداد', 'adad_engine', 'AdadEngine'),
            ('أسماء_أعداد', 'adad_names_engine', 'AdadNamesEngine'),
            
            # الصفات والنعوت
            ('صفات', 'adjective_engine', 'AdjectiveEngine'),
            
            # أسماء الله والمصطلحات الشرعية
            ('أسماء_الله', 'asma_allah_engine', 'AsmaAllahEngine'),
            ('أسماء_الله_مركبة', 'asma_allah_murakkaba_engine', 'AsmaAllahMurakkabaEngine'),
            ('مصطلحات_شرعية', 'musatalahat_sharia_engine', 'MusatalahatShariaEngine'),
            
            # الكون والطبيعة
            ('كائنات_عاقلة', 'kainat_aqila_engine', 'KainatAqilaEngine'),
            ('كائنات_غير_عاقلة', 'kainat_ghair_aqila_engine', 'KainatGhairAqilaEngine'),
            ('جنس_إفرادي', 'jins_ifradi_engine', 'JinsIfradiEngine'),
            ('جنس_جمعي', 'jins_jamii_engine', 'JinsJamiiEngine'),
            
            # الصوتيات والفونيمات
            ('أصوات', 'sound_engine', 'SoundEngine'),
            ('فونيمات', 'phonemes_engine', 'PhonemesEngine'),
            ('أصوات_محدثة', 'aswat_muhdatha_engine', 'AswatMuhdathaEngine'),
            ('حركات', 'harakat_engine', 'HarakatEngine'),
            
            # قوالب الجمع
            ('قوالب_جمع_تكسير', 'brokenplural_templates_engine', 'BrokenPluralTemplatesEngine'),
        ]
        
        loaded_count = 0
        failed_count = 0
        
        for engine_name, module_name, class_name in engine_modules:
            try:
                # محاولة استيراد المحرك
                module = __import__(module_name)
                engine_class = getattr(module, class_name)
                
                # تحميل البيانات
                df = engine_class.make_df()
                if not dataframe.empty:
                    self.engines_data[engine_name] = df
                    loaded_count += 1
                    try:
                        print(f"[OK] تم تحميل {engine_name}: {len(df)} عنصر")
                    except UnicodeEncodeError:
                        print(f"[OK] Engine loaded: {engine_name} with {len(df)} items")
                else:
                    try:
                        print(f"[WARN] {engine_name}: فارغ")
                    except UnicodeEncodeError:
                        print(f"[WARN] Engine {engine_name}: empty")
                    
            except Exception as e:
                failed_count += 1
                try:
                    print(f"[FAIL] فشل تحميل {engine_name}: {str(e)}")
                except UnicodeEncodeError:
                    print(f"[FAIL] Failed to load engine {engine_name}: {str(e)}")
                # إنشاء محرك وهمي بسيط
                self.engines_data[engine_name] = pd.DataFrame()
        
        try:
            print(f"\n[SUMMARY] تم تحميل {loaded_count} محرك، فشل {failed_count} محرك")
        except UnicodeEncodeError:
            print(f"\n[SUMMARY] Loaded {loaded_count} engines, failed {failed_count} engines")
        return loaded_count > 0
    
    def get_tools(self, engine_name, limit=15):
        """استخراج الأدوات من محرك معين"""
        if engine_name not in self.engines_data:
            return []
        
        df = self.engines_data[engine_name]
        if dataframe.empty:
            return []
        
        # البحث عن العمود المناسب للأدوات
        possible_columns = ['الأداة', 'الكلمة', 'النص', 'العنصر']
        tool_column = None
        
        for col in possible_columns:
            if col in dataframe.columns:
                tool_column = col
                break
        
        if not tool_column:
            # استخدام العمود الأول كافتراضي
            tool_column = dataframe.columns[0]
        
        tools = []
        for item in df[tool_column].head(limit):
            if pd.notna(item):
                tool_str = str(item).strip()
                if tool_str and tool_str not in tools:
                    tools.append(tool_str)
        
        return tools
    
    def is_valid_combination(self, components):
        """فحص صحة التركيب النحوي"""
        labels = [comp[0] for comp in components]
        
        # قواعد استثناء التراكيب الخاطئة
        invalid_patterns = [
            # لا يجوز فاعل + نائب فاعل معاً
            ('فاعل', 'نائب_فاعل'),
            # لا يجوز مبتدأ + فاعل في جملة بسيطة
            ('مبتدأ', 'فاعل'),
            # لا يجوز استفهام + نفي في بعض الحالات
            ('استفهام', 'نفي'),
            # لا يجوز مفعول به بدون فعل متعدي
            # (يمكن تطوير هذا أكثر)
        ]
        
        # فحص الأنماط المحظورة
        for invalid in invalid_patterns:
            if all(label in labels for label in invalid):
                return False
        
        # فحص التوافق الدلالي
        # مثلاً: إذا كان هناك "كائنات_غير_عاقلة" فلا يجوز أن تكون فاعلاً لفعل عقلي
        if 'كائنات_غير_عاقلة' in labels and 'فاعل' in labels:
            # يمكن تطوير هذا أكثر بناءً على نوع الفعل
            pass
        
        return True
    
    def utf8_hex(self, text):
        """تحويل النص إلى UTF-8 hex"""
        try:
            return ' '.join(f"0x{b:02x}" for b in text.encode('utf-8'))
        except Exception:
            return ''
    
    def describe_phonology(self, text):
        """وصف صوتي للنص"""
        count_diacritics = sum(1 for c in text if '\u064B' <= c <= '\u0652')
        count_long_vowels = sum(1 for c in text if c in 'اوي')
        word_count = len(text.split())
        return f"كلمات:{word_count} تشكيل:{count_diacritics} مد:{count_long_vowels}"
    
    def add_sentence(self, sentence, pattern, stype, components):
        """إضافة جملة للمجموعة مع التحقق من التكرار والصحة"""
        sentence = sentence.strip()
        if not sentence or sentence in self.seen_sentences:
            return False
        
        if not self.is_valid_combination(components):
            return False
        
        if len(self.sentences) >= self.MAX_SENTENCES:
            return False
            
        self.seen_sentences.add(sentence)
        
        # بناء معلومات المكونات
        comp_strings = []
        comp_utf8 = []
        comp_morph = []
        
        for label, token in components:
            comp_strings.append(f"{label}={token}")
            comp_utf8.append(f"{label}:{self.utf8_hex(token)}")
            
            # تحديد الوظيفة الاشتقاقية
            morph_func = ""
            if 'فعل' in label:
                morph_func = 'فعل مشتق'
            elif 'اسم' in label or 'علم' in label:
                morph_func = 'اسم'
            elif 'حرف' in label or 'أداة' in label:
                morph_func = 'حرف مبني'
            elif 'ضمير' in label:
                morph_func = 'ضمير'
            elif 'ظرف' in label:
                morph_func = 'ظرف'
            else:
                morph_func = 'غير محدد'
            
            comp_morph.append(f"{label}:{morph_func}")
        
        # إضافة الجملة
        self.sentences.append({
            'الأداة': sentence,
            'القالب/التركيب': pattern,
            'النوع': stype,
            'مكوّنات': ' | '.join(comp_strings),
            'UTF-8 للمكوّنات': ' | '.join(comp_utf8),
            'الفونيمات': '',
            'الحركات': '',
            'شرط/سياق': 'توليد شامل',
            'الوظيفة النحوية': f'جملة {stype}',
            'الوظيفة الدلالية': 'مثال تركيبي شامل',
            'الوظيفة الصرفية': 'تركيب',
            'الوظيفة الصوتية': self.describe_phonology(sentence),
            'الوظيفة الاشتقاقية': ' | '.join(comp_morph),
            'ملاحظات': f'مولد من: {pattern}'
        })
        
        return True
    
    def generate_basic_verbal_sentences(self):
        """توليد الجمل الفعلية الأساسية"""
        try:
            print("[INFO] توليد الجمل الفعلية الأساسية...")
        except UnicodeEncodeError:
            print("[INFO] Generating basic verbal sentences...")
        
        فعلاء = self.get_tools('فاعل', 12)
        أفعال = self.get_tools('أفعال', 12)
        
        count = 0
        for فاعل in فعلاء:
            for فعل in أفعال:
                if self.add_sentence(f"{فاعل} {فعل}", 'فاعل+فعل', 'فعلية', 
                                   [('فاعل', فاعل), ('فعل', فعل)]):
                    count += 1
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        print(f"  ✓ تم توليد {count} جملة فعلية أساسية")
    
    def generate_transitive_sentences(self):
        """توليد الجمل الفعلية المتعدية"""
        print("[INFO] توليد الجمل الفعلية المتعدية...")
        
        فعلاء = self.get_tools('فاعل', 8)
        أفعال = self.get_tools('أفعال', 8)
        مفاعيل = self.get_tools('مفعول_به', 10)
        
        count = 0
        for فاعل in فعلاء:
            for فعل in أفعال:
                for مفعول in مفاعيل:
                    if self.add_sentence(f"{فاعل} {فعل} {مفعول}", 'فاعل+فعل+مفعول', 'فعلية', 
                                       [('فاعل', فاعل), ('فعل', فعل), ('مفعول به', مفعول)]):
                        count += 1
                    if len(self.sentences) >= self.MAX_SENTENCES:
                        break
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        print(f"  ✓ تم توليد {count} جملة فعلية متعدية")
    
    def generate_nominal_sentences(self):
        """توليد الجمل الاسمية"""
        print("[INFO] توليد الجمل الاسمية...")
        
        مبتدآت = self.get_tools('مبتدأ_خبر', 10) + self.get_tools('أسماء_عامة', 10)
        أخبار = self.get_tools('أسماء_عامة', 15) + self.get_tools('صفات', 10)
        
        count = 0
        for مبتدأ in مبتدآت:
            for خبر in أخبار:
                if مبتدأ != خبر:  # تجنب التكرار
                    if self.add_sentence(f"{مبتدأ} {خبر}", 'مبتدأ+خبر', 'اسمية', 
                                       [('مبتدأ', مبتدأ), ('خبر', خبر)]):
                        count += 1
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        print(f"  ✓ تم توليد {count} جملة اسمية")
    
    def generate_demonstrative_sentences(self):
        """توليد الجمل مع أسماء الإشارة"""
        print("[INFO] توليد الجمل مع أسماء الإشارة...")
        
        إشارات = self.get_tools('أسماء_إشارة', 8)
        أسماء = self.get_tools('أسماء_عامة', 12)
        
        count = 0
        for إشارة in إشارات:
            for اسم in أسماء:
                if self.add_sentence(f"{إشارة} {اسم}", 'إشارة+اسم', 'إشارية', 
                                   [('اسم إشارة', إشارة), ('مشار إليه', اسم)]):
                    count += 1
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        print(f"  ✓ تم توليد {count} جملة إشارية")
    
    def generate_interrogative_sentences(self):
        """توليد الجمل الاستفهامية"""
        print("[INFO] توليد الجمل الاستفهامية...")
        
        استفهامات = self.get_tools('استفهام', 6)
        فعلاء = self.get_tools('فاعل', 8)
        أفعال = self.get_tools('أفعال', 8)
        
        count = 0
        for استفهام in استفهامات:
            for فاعل in فعلاء:
                for فعل in أفعال:
                    if self.add_sentence(f"{استفهام} {فاعل} {فعل}", 'استفهام+فاعل+فعل', 'استفهامية', 
                                       [('استفهام', استفهام), ('فاعل', فاعل), ('فعل', فعل)]):
                        count += 1
                    if len(self.sentences) >= self.MAX_SENTENCES:
                        break
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        print(f"  ✓ تم توليد {count} جملة استفهامية")
    
    def generate_negative_sentences(self):
        """توليد الجمل المنفية"""
        print("[INFO] توليد الجمل المنفية...")
        
        نفيات = self.get_tools('نفي', 4)
        فعلاء = self.get_tools('فاعل', 8)
        أفعال = self.get_tools('أفعال', 8)
        
        count = 0
        for نفي in نفيات:
            for فاعل in فعلاء:
                for فعل in أفعال:
                    if self.add_sentence(f"{نفي} {فاعل} {فعل}", 'نفي+فاعل+فعل', 'منفية', 
                                       [('نفي', نفي), ('فاعل', فاعل), ('فعل', فعل)]):
                        count += 1
                    if len(self.sentences) >= self.MAX_SENTENCES:
                        break
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        print(f"  ✓ تم توليد {count} جملة منفية")
    
    def generate_prepositional_phrases(self):
        """توليد شبه الجمل (جار ومجرور)"""
        print("[INFO] توليد شبه الجمل...")
        
        جرور = self.get_tools('جر', 12)
        أسماء = self.get_tools('أسماء_عامة', 15)
        
        count = 0
        for جر in جرور:
            for اسم in أسماء:
                if self.add_sentence(f"{جر} {اسم}", 'جار+مجرور', 'شبه جملة', 
                                   [('حرف جر', جر), ('اسم مجرور', اسم)]):
                    count += 1
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        print(f"  ✓ تم توليد {count} شبه جملة")
    
    def generate_vocative_sentences(self):
        """توليد جمل النداء"""
        print("[INFO] توليد جمل النداء...")
        
        نداءات = self.get_tools('نداء', 5)
        أعلام = (self.get_tools('أعلام_أشخاص', 10) + 
                 self.get_tools('أعلام_أماكن', 5) + 
                 self.get_tools('أسماء_عامة', 8))
        
        count = 0
        for نداء in نداءات:
            for علم in أعلام:
                if self.add_sentence(f"{نداء} {علم}", 'نداء+منادى', 'ندائية', 
                                   [('أداة نداء', نداء), ('منادى', علم)]):
                    count += 1
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        print(f"  ✓ تم توليد {count} جملة ندائية")
    
    def generate_adverbial_sentences(self):
        """توليد الجمل مع الظروف"""
        print("[INFO] توليد الجمل مع الظروف...")
        
        فعلاء = self.get_tools('فاعل', 6)
        أفعال = self.get_tools('أفعال', 6)
        ظروف = (self.get_tools('ظروف', 10) + 
                self.get_tools('أزمنة', 8) + 
                self.get_tools('أماكن', 8))
        
        count = 0
        for فاعل in فعلاء:
            for فعل in أفعال:
                for ظرف in ظروف:
                    if self.add_sentence(f"{فاعل} {فعل} {ظرف}", 'فاعل+فعل+ظرف', 'فعلية ظرفية', 
                                       [('فاعل', فاعل), ('فعل', فعل), ('ظرف', ظرف)]):
                        count += 1
                    if len(self.sentences) >= self.MAX_SENTENCES:
                        break
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        print(f"  ✓ تم توليد {count} جملة ظرفية")
    
    def generate_participle_sentences(self):
        """توليد الجمل مع المشتقات"""
        print("[INFO] توليد الجمل مع المشتقات...")
        
        فعلاء = self.get_tools('فاعل', 6)
        مشتقات = (self.get_tools('اسم_فاعل', 8) + 
                  self.get_tools('اسم_مفعول', 8) + 
                  self.get_tools('أفعل_تفضيل', 6))
        
        count = 0
        for فاعل in فعلاء:
            for مشتق in مشتقات:
                if self.add_sentence(f"{فاعل} {مشتق}", 'فاعل+مشتق', 'اسمية', 
                                   [('مبتدأ', فاعل), ('خبر', مشتق)]):
                    count += 1
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        print(f"  ✓ تم توليد {count} جملة مع المشتقات")
    
    def generate_complex_sentences(self):
        """توليد الجمل المعقدة"""
        print("[INFO] توليد الجمل المعقدة...")
        
        # جمل مع عطف
        عطف = self.get_tools('عطف', 6)
        فعلاء = self.get_tools('فاعل', 5)
        أفعال = self.get_tools('أفعال', 5)
        
        count = 0
        for فاعل1 in فعلاء[:3]:
            for فعل1 in أفعال[:3]:
                for عاطف in عطف[:3]:
                    for فاعل2 in فعلاء[:3]:
                        for فعل2 in أفعال[:3]:
                            if فاعل1 != فاعل2 or فعل1 != فعل2:
                                sentence = f"{فاعل1} {فعل1} {عاطف} {فاعل2} {فعل2}"
                                if self.add_sentence(sentence, 'فاعل+فعل+عطف+فاعل+فعل', 'معطوفة', 
                                                   [('فاعل1', فاعل1), ('فعل1', فعل1), ('عطف', عاطف), 
                                                    ('فاعل2', فاعل2), ('فعل2', فعل2)]):
                                    count += 1
                            if len(self.sentences) >= self.MAX_SENTENCES:
                                break
                        if len(self.sentences) >= self.MAX_SENTENCES:
                            break
                    if len(self.sentences) >= self.MAX_SENTENCES:
                        break
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        print(f"  ✓ تم توليد {count} جملة معقدة")
    
    def generate_all_sentences(self):
        """توليد جميع أنواع الجمل"""
        print("\n=== بدء التوليد الشامل للجمل ===")
        
        # تحميل المحركات
        if not self.load_all_engines():
            print("[ERROR] فشل في تحميل المحركات")
            return pd.DataFrame()
        
        print(f"\n[INFO] بدء توليد الجمل (الحد الأقصى: {self.MAX_SENTENCES})")
        
        # توليد أنواع مختلفة من الجمل
        generation_methods = [
            self.generate_basic_verbal_sentences,
            self.generate_transitive_sentences,
            self.generate_nominal_sentences,
            self.generate_demonstrative_sentences,
            self.generate_interrogative_sentences,
            self.generate_negative_sentences,
            self.generate_prepositional_phrases,
            self.generate_vocative_sentences,
            self.generate_adverbial_sentences,
            self.generate_participle_sentences,
            self.generate_complex_sentences,
        ]
        
        for method in generation_methods:
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
            try:
                method()
            except Exception as e:
                print(f"[ERROR] خطأ في {method.__name__}: {str(e)}")
        
        print(f"\n=== انتهى التوليد: {len(self.sentences)} جملة ===")
        
        # تحويل إلى DataFrame
        if self.sentences:
            dataframe = pd.DataFrame(self.sentences)
            print(f"[SUCCESS] تم إنشاء DataFrame بـ {len(df)} صف و {len(dataframe.columns)} عمود")
            return df
        else:
            print("[WARNING] لم يتم توليد أي جمل")
            return pd.DataFrame()
    
    def save_to_excel(self, filename="comprehensive_sentences.xlsx"):
        """حفظ الجمل المولدة في ملف Excel"""
        df = self.generate_all_sentences()
        
        if not dataframe.empty:
            try:
                dataframe.to_excel(filename, index=False, sheet_name='جُمَل_مولدة_شاملة')
                print(f"[SUCCESS] تم حفظ {len(df)} جملة في {filename}")
                return True
            except Exception as e:
                print(f"[ERROR] فشل في الحفظ: {str(e)}")
                return False
        else:
            print("[ERROR] لا توجد جمل للحفظ")
            return False


# الاستخدام المباشر
if __name__ == "__main__":
    generator = ComprehensiveSentenceGenerator()
    generator.save_to_excel("comprehensive_multilayer_grammar.xlsx")