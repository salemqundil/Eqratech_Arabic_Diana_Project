import pandas as pd
import sys
import os
import importlib

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
            ('fael', 'engines.syntax.fael_engine', 'FaelEngine'),
            ('verbs', 'engines.morphology.verbs_engine', 'VerbsEngine'),
            ('pronouns', 'pronouns_engine', 'PronounsEngine'),
            ('adverbs', 'adverbs_engine', 'AdverbsEngine'),
            ('jar', 'jar_engine', 'JarEngine'),
            ('nafi', 'nafi_engine', 'NafiEngine'),
            ('atf', 'atf_engine', 'AtfEngine'),
            ('generic_nouns', 'engines.lexicon.generic_nouns_engine', 'GenericNounsEngine'),
            ('proper_nouns', 'engines.lexicon.proper_nouns_engine', 'ProperNounsEngine'),
            ('demonstratives', 'engines.syntax.demonstratives_engine', 'DemonstrativesEngine'),
            ('istifham', 'engines.syntax.istifham_engine', 'IstifhamEngine'),
            ('adjective', 'engines.morphology.adjective_engine', 'AdjectiveEngine'),
            ('place', 'engines.lexicon.place_engine', 'PlaceEngine'),
            ('time', 'time_engine', 'TimeEngine'),
        ]
        
        loaded_count = 0
        
        for engine_name, module_name, class_name in basic_engines:
            try:
                # محاولة الاستيراد
                module = importlib.import_module(module_name)
                engine_class = getattr(module, class_name)
                
                # تحميل البيانات بطريقة آمنة
                try:
                    df = engine_class.make_df()
                    if not df.empty:
                        self.engines_data[engine_name] = df
                        loaded_count += 1
                        self.safe_print(f"[OK] {engine_name}: {len(df)} items")
                    else:
                        self.safe_print(f"[WARN] {engine_name}: empty")
                except Exception as inner_e:
                    self.safe_print(f"[SKIP] {engine_name}: data error - {str(inner_e)}")
                    self.engines_data[engine_name] = pd.DataFrame()
                    
            except ImportError:
                self.safe_print(f"[SKIP] {engine_name}: module not found")
                self.engines_data[engine_name] = pd.DataFrame()
            except Exception as e:
                self.safe_print(f"[FAIL] {engine_name}: {str(e)}")
                self.engines_data[engine_name] = pd.DataFrame()
        
        self.safe_print(f"[SUMMARY] Loaded {loaded_count} engines successfully")
        return loaded_count > 0
    
    def get_tools_safe(self, engine_name, limit=10):
        """استخراج الأدوات بطريقة آمنة"""
        if engine_name not in self.engines_data:
            return []
        
        df = self.engines_data[engine_name]
        if df.empty:
            return []
        
        # البحث عن العمود المناسب
        possible_columns = ['الأداة', 'الكلمة', 'النص', 'العنصر']
        tool_column = None
        
        for col in possible_columns:
            if col in df.columns:
                tool_column = col
                break
        
        if not tool_column and len(df.columns) > 0:
            tool_column = df.columns[0]
        
        if not tool_column:
            return []
        
        tools = []
        try:
            for item in df[tool_column].head(limit):
                if pd.notna(item):
                    tool_str = str(item).strip()
                    if tool_str and tool_str not in tools:
                        tools.append(tool_str)
        except Exception as e:
            self.safe_print(f"[ERROR] Error extracting tools from {engine_name}: {str(e)}")
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
        
        count1 = 0
        for fael in fael_tools:
            for verb in verb_tools:
                if self.add_sentence_simple(f"{fael} {verb}", 'fael+verb', 'verbal', 
                                          [('fael', fael), ('verb', verb)]):
                    count1 += 1
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        self.safe_print(f"  Generated {count1} basic verbal sentences")
        
        # 2. الجمل الاسمية
        self.safe_print("[GEN] Nominal sentences...")
        noun_tools = self.get_tools_safe('generic_nouns', 15)
        adj_tools = self.get_tools_safe('adjective', 10)
        
        count2 = 0
        for noun in noun_tools[:10]:
            for adj in adj_tools[:10]:
                if noun != adj:
                    if self.add_sentence_simple(f"{noun} {adj}", 'noun+adj', 'nominal', 
                                              [('mubtada', noun), ('khabar', adj)]):
                        count2 += 1
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        self.safe_print(f"  Generated {count2} nominal sentences")
        
        # 3. شبه الجمل
        self.safe_print("[GEN] Prepositional phrases...")
        jar_tools = self.get_tools_safe('jar', 10)
        
        count3 = 0
        for jar in jar_tools:
            for noun in noun_tools[:10]:
                if self.add_sentence_simple(f"{jar} {noun}", 'jar+noun', 'prepositional', 
                                          [('jar', jar), ('majroor', noun)]):
                    count3 += 1
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        self.safe_print(f"  Generated {count3} prepositional phrases")
        
        # 4. الجمل الاستفهامية
        self.safe_print("[GEN] Interrogative sentences...")
        istifham_tools = self.get_tools_safe('istifham', 8)
        
        count4 = 0
        for istifham in istifham_tools:
            for fael in fael_tools[:8]:
                for verb in verb_tools[:8]:
                    if self.add_sentence_simple(f"{istifham} {fael} {verb}", 'istifham+fael+verb', 'interrogative', 
                                              [('istifham', istifham), ('fael', fael), ('verb', verb)]):
                        count4 += 1
                    if len(self.sentences) >= self.MAX_SENTENCES:
                        break
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        self.safe_print(f"  Generated {count4} interrogative sentences")
        
        # 5. الجمل المنفية
        self.safe_print("[GEN] Negative sentences...")
        nafi_tools = self.get_tools_safe('nafi', 5)
        
        count5 = 0
        for nafi in nafi_tools:
            for fael in fael_tools[:8]:
                for verb in verb_tools[:8]:
                    if self.add_sentence_simple(f"{nafi} {fael} {verb}", 'nafi+fael+verb', 'negative', 
                                              [('nafi', nafi), ('fael', fael), ('verb', verb)]):
                        count5 += 1
                    if len(self.sentences) >= self.MAX_SENTENCES:
                        break
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        self.safe_print(f"  Generated {count5} negative sentences")
        
        # 6. الجمل مع أسماء الإشارة
        self.safe_print("[GEN] Demonstrative sentences...")
        demo_tools = self.get_tools_safe('demonstratives', 8)
        
        count6 = 0
        for demo in demo_tools:
            for noun in noun_tools[:10]:
                if self.add_sentence_simple(f"{demo} {noun}", 'demo+noun', 'demonstrative', 
                                          [('demonstrative', demo), ('noun', noun)]):
                    count6 += 1
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        self.safe_print(f"  Generated {count6} demonstrative sentences")
        
        # 7. الجمل مع الظروف
        self.safe_print("[GEN] Adverbial sentences...")
        adv_tools = self.get_tools_safe('adverbs', 10)
        place_tools = self.get_tools_safe('place', 8)
        time_tools = self.get_tools_safe('time', 8)
        all_advs = adv_tools + place_tools + time_tools
        
        count7 = 0
        for fael in fael_tools[:6]:
            for verb in verb_tools[:6]:
                for adv in all_advs[:12]:
                    if self.add_sentence_simple(f"{fael} {verb} {adv}", 'fael+verb+adv', 'adverbial', 
                                              [('fael', fael), ('verb', verb), ('adverb', adv)]):
                        count7 += 1
                    if len(self.sentences) >= self.MAX_SENTENCES:
                        break
                if len(self.sentences) >= self.MAX_SENTENCES:
                    break
            if len(self.sentences) >= self.MAX_SENTENCES:
                break
        
        self.safe_print(f"  Generated {count7} adverbial sentences")
        
        # 8. الجمل مع العطف
        self.safe_print("[GEN] Conjunctive sentences...")
        atf_tools = self.get_tools_safe('atf', 6)
        
        count8 = 0
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
                                    count8 += 1
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
        
        self.safe_print(f"  Generated {count8} conjunctive sentences")
        
        total_generated = count1 + count2 + count3 + count4 + count5 + count6 + count7 + count8
        self.safe_print(f"\n=== Generation complete: {total_generated} sentences ===")
        
        if self.sentences:
            df = pd.DataFrame(self.sentences)
            self.safe_print(f"[SUCCESS] Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
            return df
        else:
            self.safe_print("[WARNING] No sentences generated")
            return pd.DataFrame()
    
    def save_to_excel_safe(self, filename="safe_comprehensive_sentences.xlsx"):
        """حفظ الجمل بطريقة آمنة"""
        df = self.generate_sentences_safe()
        
        if not df.empty:
            try:
                df.to_excel(filename, index=False, sheet_name='Generated_Sentences')
                self.safe_print(f"[SUCCESS] Saved {len(df)} sentences to {filename}")
                return True
            except Exception as e:
                self.safe_print(f"[ERROR] Failed to save: {str(e)}")
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