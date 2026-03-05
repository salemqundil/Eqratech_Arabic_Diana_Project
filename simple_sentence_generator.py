import pandas as pd
import sys
import os

# حل مشكلة الترميز
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'

class SimpleSentenceGenerator:
    """
    مولد جمل مبسط يتجنب مشاكل الترميز
    """
    
    def __init__(self):
        self.engines_data = {}
        self.sentences = []
        self.MAX_SENTENCES = 3000
        
    def safe_print(self, text):
        """طباعة آمنة تتجنب مشاكل الترميز"""
        try:
            print(text)
        except UnicodeEncodeError:
            # تحويل النص العربي إلى Latin
            print(text.encode('ascii', 'ignore').decode('ascii'))
    
    def load_basic_engines(self):
        """تحميل المحركات الأساسية بطريقة آمنة"""
        self.safe_print("[INFO] Loading basic engines...")
        
        basic_engines = [
            ('fael', 'fael_engine', 'FaelEngine'),
            ('verbs', 'verbs_engine', 'VerbsEngine'),
            ('pronouns', 'pronouns_engine', 'PronounsEngine'),
            ('adverbs', 'adverbs_engine', 'AdverbsEngine'),
            ('jar', 'jar_engine', 'JarEngine'),
            ('nafi', 'nafi_engine', 'NafiEngine'),
            ('atf', 'atf_engine', 'AtfEngine'),
            ('generic_nouns', 'generic_nouns_engine', 'GenericNounsEngine'),
            ('proper_nouns', 'proper_nouns_engine', 'ProperNounsEngine'),
            ('demonstratives', 'demonstratives_engine', 'DemonstrativesEngine'),
            ('istifham', 'istifham_engine', 'IstifhamEngine'),
            ('adjective', 'adjective_engine', 'AdjectiveEngine'),
            ('place', 'place_engine', 'PlaceEngine'),
            ('time', 'time_engine', 'TimeEngine'),
        ]
        
        loaded_count = 0
        
        for engine_name, module_name, class_name in basic_engines:
            try:
                # محاولة الاستيراد
                module = __import__(module_name)
                engine_class = getattr(module, class_name)
                
                # تحميل البيانات بطريقة آمنة
                try:
                    dataframe = engine_class.make_df()
                    if not dataframe.empty:
                        self.engines_data[engine_name] = dataframe
                        loaded_count += 1
                        self.safe_print(f"[OK] {engine_name}: {len(dataframe)} items")
                    else:
                        self.safe_print(f"[WARN] {engine_name}: empty")
                except Exception as inner_error:
                    self.safe_print(f"[SKIP] {engine_name}: data error - {str(inner_error)}")
                    self.engines_data[engine_name] = pd.DataFrame()
                    
            except ImportError:
                self.safe_print(f"[SKIP] {engine_name}: module not found")
                self.engines_data[engine_name] = pd.DataFrame()
            except Exception as error:
                self.safe_print(f"[FAIL] {engine_name}: {str(error)}")
                self.engines_data[engine_name] = pd.DataFrame()
        
        self.safe_print(f"[SUMMARY] Loaded {loaded_count} engines successfully")
        return loaded_count > 0
    
    def get_tools_safe(self, engine_name, limit=10):
        """استخراج الأدوات بطريقة آمنة"""
        if engine_name not in self.engines_data:
            return []
        
        dataframe = self.engines_data[engine_name]
        if dataframe.empty:
            return []
        
        # البحث عن العمود المناسب
        possible_columns = ['الأداة', 'الكلمة', 'النص', 'العنصر']
        tool_column = None
        
        for col in possible_columns:
            if col in dataframe.columns:
                tool_column = col
                break
        
        if not tool_column and len(dataframe.columns) > 0:
            tool_column = dataframe.columns[0]
        
        if not tool_column:
            return []
        
        tools = []
        try:
            for item in dataframe[tool_column].head(limit):
                if pd.notna(item):
                    tool_str = str(item).strip()
                    if tool_str and tool_str not in tools:
                        tools.append(tool_str)
        except Exception as error:
            self.safe_print(f"[ERROR] Error extracting tools from {engine_name}: {str(error)}")
            return []
        
        return tools
    
    def add_sentence_simple(self, sentence, pattern, stype, components):
        """إضافة جملة بطريقة مبسطة"""
        sentence = sentence.strip()
        if not sentence or len(self.sentences) >= self.MAX_SENTENCES:
            return False
        
        # بناء معلومات المكونات
        comp_strings = []
        for label, token in components:
            comp_strings.append(f"{label}={token}")
        
        self.sentences.append({
            'الأداة': sentence,
            'القالب/التركيب': pattern,
            'النوع': stype,
            'مكوّنات': ' | '.join(comp_strings),
            'UTF-8 للمكوّنات': '',
            'الفونيمات': '',
            'الحركات': '',
            'شرط/سياق': 'basic generation',
            'الوظيفة النحوية': f'sentence {stype}',
            'الوظيفة الدلالية': 'example',
            'الوظيفة الصرفية': 'structure',
            'الوظيفة الصوتية': f'words:{len(sentence.split())}',
            'الوظيفة الاشتقاقية': pattern,
            'ملاحظات': f'Generated from: {pattern}'
        })
        
        return True
    
    def generate_sentences_safe(self):
        """توليد الجمل بطريقة آمنة"""
        self.safe_print("\n=== Starting sentence generation ===")
        
        # تحميل المحركات
        if not self.load_basic_engines():
            self.safe_print("[ERROR] No engines loaded")
            return pd.DataFrame()
        
        self.safe_print(f"[INFO] Starting generation (max: {self.MAX_SENTENCES})")
        
        # 1. الجمل الفعلية الأساسية
        self.safe_print("[GEN] Basic verbal sentences...")
        fael_tools = self.get_tools_safe('fael', 15)
        verb_tools = self.get_tools_safe('verbs', 15)
        
        verbal_count = 0
        for fael in fael_tools:
            for verb in verb_tools:
                if self.add_sentence_simple(f"{fael} {verb}", 'fael+verb', 'verbal', 
                                          [('fael', fael), ('verb', verb)]):
                    verbal_count += 1
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        self.safe_print(f"  Generated {verbal_count} basic verbal sentences")
        
        # 2. الجمل الاسمية
        self.safe_print("[GEN] Nominal sentences...")
        noun_tools = self.get_tools_safe('generic_nouns', 15)
        adj_tools = self.get_tools_safe('adjective', 10)
        
        nominal_count = 0
        for noun in noun_tools[:10]:
            for adj in adj_tools[:10]:
                if noun != adj:
                    if self.add_sentence_simple(f"{noun} {adj}", 'noun+adj', 'nominal', 
                                              [('mubtada', noun), ('khabar', adj)]):
                        nominal_count += 1
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        self.safe_print(f"  Generated {nominal_count} nominal sentences")
        
        # 3. شبه الجمل
        self.safe_print("[GEN] Prepositional phrases...")
        jar_tools = self.get_tools_safe('jar', 10)
        
        prepositional_count = 0
        for jar in jar_tools:
            for noun in noun_tools[:10]:
                if self.add_sentence_simple(f"{jar} {noun}", 'jar+noun', 'prepositional', 
                                          [('jar', jar), ('majroor', noun)]):
                    prepositional_count += 1
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        self.safe_print(f"  Generated {prepositional_count} prepositional phrases")
        
        # 4. الجمل الاستفهامية
        self.safe_print("[GEN] Interrogative sentences...")
        istifham_tools = self.get_tools_safe('istifham', 8)
        
        interrogative_count = 0
        for istifham in istifham_tools:
            for fael in fael_tools[:8]:
                for verb in verb_tools[:8]:
                    if self.add_sentence_simple(f"{istifham} {fael} {verb}", 'istifham+fael+verb', 'interrogative', 
                                              [('istifham', istifham), ('fael', fael), ('verb', verb)]):
                        interrogative_count += 1
                    if len(self.sentences) >= self.MAX_SENTENCES:
                        break
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        self.safe_print(f"  Generated {interrogative_count} interrogative sentences")
        
        # 5. الجمل المنفية
        self.safe_print("[GEN] Negative sentences...")
        nafi_tools = self.get_tools_safe('nafi', 5)
        
        negative_count = 0
        for nafi in nafi_tools:
            for fael in fael_tools[:8]:
                for verb in verb_tools[:8]:
                    if self.add_sentence_simple(f"{nafi} {fael} {verb}", 'nafi+fael+verb', 'negative', 
                                              [('nafi', nafi), ('fael', fael), ('verb', verb)]):
                        negative_count += 1
                    if len(self.sentences) >= self.MAX_SENTENCES:
                        break
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        self.safe_print(f"  Generated {negative_count} negative sentences")
        
        # 6. الجمل مع أسماء الإشارة
        self.safe_print("[GEN] Demonstrative sentences...")
        demo_tools = self.get_tools_safe('demonstratives', 8)
        
        demonstrative_count = 0
        for demo in demo_tools:
            for noun in noun_tools[:10]:
                if self.add_sentence_simple(f"{demo} {noun}", 'demo+noun', 'demonstrative', 
                                          [('demonstrative', demo), ('noun', noun)]):
                    demonstrative_count += 1
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        self.safe_print(f"  Generated {demonstrative_count} demonstrative sentences")
        
        # 7. الجمل مع الظروف
        self.safe_print("[GEN] Adverbial sentences...")
        adv_tools = self.get_tools_safe('adverbs', 10)
        place_tools = self.get_tools_safe('place', 8)
        time_tools = self.get_tools_safe('time', 8)
        all_advs = adv_tools + place_tools + time_tools
        
        adverbial_count = 0
        for fael in fael_tools[:6]:
            for verb in verb_tools[:6]:
                for adv in all_advs[:12]:
                    if self.add_sentence_simple(f"{fael} {verb} {adv}", 'fael+verb+adv', 'adverbial', 
                                              [('fael', fael), ('verb', verb), ('adverb', adv)]):
                        adverbial_count += 1
                    if len(self.sentences) >= self.MAX_SENTENCES:
                        break
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        self.safe_print(f"  Generated {adverbial_count} adverbial sentences")
        
        # 8. الجمل مع العطف
        self.safe_print("[GEN] Conjunctive sentences...")
        atf_tools = self.get_tools_safe('atf', 6)
        
        conjunctive_count = 0
        for fael1 in fael_tools[:5]:
            for verb1 in verb_tools[:5]:
                for atf in atf_tools[:4]:
                    for fael2 in fael_tools[:5]:
                        for verb2 in verb_tools[:5]:
                            if fael1 != fael2 or verb1 != verb2:
                                sentence = f"{fael1} {verb1} {atf} {fael2} {verb2}"
                                if self.add_sentence_simple(sentence, 'fael+verb+atf+fael+verb', 'compound', 
                                                          [('fael1', fael1), ('verb1', verb1), ('atf', atf), 
                                                           ('fael2', fael2), ('verb2', verb2)]):
                                    conjunctive_count += 1
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
        
        self.safe_print(f"  Generated {conjunctive_count} conjunctive sentences")
        
        total_generated = (verbal_count + nominal_count + prepositional_count + 
                          interrogative_count + negative_count + demonstrative_count + 
                          adverbial_count + conjunctive_count)
        self.safe_print(f"\n=== Generation complete: {total_generated} sentences ===")
        
        if self.sentences:
            result_dataframe = pd.DataFrame(self.sentences)
            self.safe_print(f"[SUCCESS] Created DataFrame with {len(result_dataframe)} rows and {len(result_dataframe.columns)} columns")
            return result_dataframe
        else:
            self.safe_print("[WARNING] No sentences generated")
            return pd.DataFrame()
    
    def save_to_excel_safe(self, filename="safe_comprehensive_sentences.xlsx"):
        """حفظ الجمل بطريقة آمنة"""
        result_dataframe = self.generate_sentences_safe()
        
        if not result_dataframe.empty:
            try:
                result_dataframe.to_excel(filename, index=False, sheet_name='Generated_Sentences')
                self.safe_print(f"[SUCCESS] Saved {len(result_dataframe)} sentences to {filename}")
                return True
            except Exception as error:
                self.safe_print(f"[ERROR] Failed to save: {str(error)}")
                return False
        else:
            self.safe_print("[ERROR] No sentences to save")
            return False


# الاستخدام
if __name__ == "__main__":
    generator = SimpleSentenceGenerator()
    success = generator.save_to_excel_safe("comprehensive_arabic_sentences.xlsx")
    if success:
        print("\n=== SUCCESS: Comprehensive sentence generation completed! ===")
    else:
        print("\n=== FAILED: Could not complete sentence generation ===")