"""
Enhanced Sentence Generation Engine with Full Engine Coverage
===========================================================

يشمل جميع المحركات المتاحة مع خوارزميات استثناء لضمان التوافق النحوي
"""

import pandas as pd
from base_reconstruction_engine import BaseReconstructionEngine
from reconstruction_utils import reconstruct_from_base_df

# استيراد جميع المحركات المطلوبة للتوليد الشامل
from atf_engine import AtfEngine
from nafi_engine import NafiEngine
from jar_engine import JarEngine
from pronouns_engine import PronounsEngine
from adverbs_engine import AdverbsEngine
from proper_nouns_engine import ProperNounsEngine
from generic_nouns_engine import GenericNounsEngine
from qasr_engine import QasrEngine
from verbs_engine import VerbsEngine

# محركات إضافية مهمة
from demonstratives_engine import DemonstrativesEngine
from fael_engine import FaelEngine
from mafoul_bih_engine import MafoulBihEngine
from mafoul_ajlih_engine import MafoulAjlihEngine
from mafoul_mutlaq_engine import MafoulMutlaqEngine
from haal_engine import HaalEngine
from tamyeez_engine import TamyeezEngine
from istifham_engine import IstifhamEngine
from nasikh_engine import NasikhEngine
from nidha_engine import NidhaEngine
from adad_engine import AdadEngine
from adjective_engine import AdjectiveEngine
from relatives_engine import RelativesEngine
from shart_engine import ShartEngine
from afaal_khamsa_engine import AfaalKhamsaEngine
from mabni_majhool_engine import MabniMajhoolEngine
from mobtada_khabar_engine import MobtadaKhabarEngine

class EnhancedSentenceGenerationEngine(BaseReconstructionEngine):
    """محرك توليد الجمل المحسّن - يستخدم جميع المحركات المتاحة مع التحقق من التوافق"""
    
    SHEET_NAME = 'جُمَل_مولدة_محسّنة'

    @classmethod
    def make_df(cls):
        """توليد مجموعة شاملة من الجمل باستخدام جميع المحركات"""
        
        # تحميل جميع المحركات
        engines = {
            'verbs': VerbsEngine.make_df(),
            'nouns': GenericNounsEngine.make_df(), 
            'proper_nouns': ProperNounsEngine.make_df(),
            'pronouns': PronounsEngine.make_df(),
            'demonstratives': DemonstrativesEngine.make_df(),
            'adjectives': AdjectiveEngine.make_df(),
            'adverbs': AdverbsEngine.make_df(),
            'prepositions': JarEngine.make_df(),
            'conjunctions': AtfEngine.make_df(),
            'negation': NafiEngine.make_df(),
            'interrogatives': IstifhamEngine.make_df(),
            'relatives': RelativesEngine.make_df(),
            'conditionals': ShartEngine.make_df(),
            'vocatives': NidhaEngine.make_df(),
            'numbers': AdadEngine.make_df(),
            'fael': FaelEngine.make_df(),
            'mafoul_bih': MafoulBihEngine.make_df(),
            'mafoul_ajlih': MafoulAjlihEngine.make_df(),
            'mafoul_mutlaq': MafoulMutlaqEngine.make_df(),
            'haal': HaalEngine.make_df(),
            'tamyeez': TamyeezEngine.make_df(),
            'nasikh': NasikhEngine.make_df(),
            'qasr': QasrEngine.make_df(),
            'afaal_khamsa': AfaalKhamsaEngine.make_df(),
            'mabni_majhool': MabniMajhoolEngine.make_df(),
            'mobtada_khabar': MobtadaKhabarEngine.make_df(),
        }
        
        # استخراج العينات من كل محرك
        samples = {}
        for key, df in engines.items():
            if not dataframe.empty and 'الأداة' in dataframe.columns:
                samples[key] = df['الأداة'].dropna().head(20).tolist()
            else:
                samples[key] = []
        
        sentences = []
        MAX_SENTENCES = 2000  # زيادة العدد لشمولية أكبر
        
        def add_sentence(text, pattern, sentence_type, components, is_valid=True):
            """إضافة جملة مع التحقق من الصحة"""
            if not is_valid or not text.strip():
                return
            
            # حساب الخصائص الصوتية
            sound_profile = cls._describe_phonology(text)
            
            # تحديد الوظيفة الاشتقاقية
            morph_function = cls._derive_morphological_function(components)
            
            sentences.append({
                'الأداة': text.strip(),
                'القالب/التركيب': pattern,
                'النوع': sentence_type,
                'مكوّنات': ' | '.join(f"{label}={token}" for label, token in components),
                'UTF-8 للمكوّنات': cls._get_utf8_components(components),
                'الفونيمات': '',
                'الحركات': '',
                'شرط/سياق': 'توليد آلي محسّن',
                'الوظيفة النحوية': f'جملة {sentence_type}',
                'الوظيفة الدلالية': cls._semantic_function(sentence_type, pattern),
                'الوظيفة الصرفية': 'تركيب',
                'الوظيفة الصوتية': sound_profile,
                'الوظيفة الاشتقاقية': morph_function,
                'ملاحظات': 'مولد محسّن'
            })
        
        # 1. الجمل الفعلية الشاملة
        cls._generate_verbal_sentences(samples, add_sentence, MAX_SENTENCES // 3)
        
        # 2. الجمل الاسمية المتنوعة  
        cls._generate_nominal_sentences(samples, add_sentence, MAX_SENTENCES // 3)
        
        # 3. الجمل المعقدة والتراكيب المركبة
        cls._generate_complex_sentences(samples, add_sentence, MAX_SENTENCES // 3)
        
        return reconstruct_from_base_df(pd.DataFrame(sentences))
    
    @classmethod
    def _generate_verbal_sentences(cls, samples, add_func, max_count):
        """توليد الجمل الفعلية بأنماط متنوعة"""
        count = 0
        
        # 1. فعل + فاعل + مفعول به
        for verb in samples['verbs'][:15]:
            for fael in samples['fael'][:10]:
                for mafoul in samples['mafoul_bih'][:8]:
                    if cls._check_compatibility('verbal', [verb, fael, mafoul]):
                        sentence = f"{verb} {fael} {mafoul}"
                        add_func(sentence, 'فعل+فاعل+مفعول_به', 'فعلية',
                               [('فعل', verb), ('فاعل', fael), ('مفعول به', mafoul)])
                        count += 1
                        if count >= max_count: return
        
        # 2. فعل + فاعل + مفعول مطلق
        for verb in samples['verbs'][:10]:
            for fael in samples['fael'][:8]:
                for mutlaq in samples['mafoul_mutlaq'][:6]:
                    if cls._check_compatibility('verbal', [verb, fael, mutlaq]):
                        sentence = f"{verb} {fael} {mutlaq}"
                        add_func(sentence, 'فعل+فاعل+مفعول_مطلق', 'فعلية',
                               [('فعل', verb), ('فاعل', fael), ('مفعول مطلق', mutlaq)])
                        count += 1
                        if count >= max_count: return
        
        # 3. فعل + فاعل + حال
        for verb in samples['verbs'][:10]:
            for fael in samples['fael'][:8]:
                for haal in samples['haal'][:6]:
                    if cls._check_compatibility('verbal', [verb, fael, haal]):
                        sentence = f"{verb} {fael} {haal}"
                        add_func(sentence, 'فعل+فاعل+حال', 'فعلية',
                               [('فعل', verb), ('فاعل', fael), ('حال', haal)])
                        count += 1
                        if count >= max_count: return
        
        # 4. الأفعال الخمسة
        for afaal in samples['afaal_khamsa'][:8]:
            for fael in samples['fael'][:6]:
                if cls._check_compatibility('afaal_khamsa', [afaal, fael]):
                    sentence = f"{afaal} {fael}"
                    add_func(sentence, 'أفعال_خمسة+فاعل', 'فعلية',
                           [('فعل من الأفعال الخمسة', afaal), ('فاعل', fael)])
                    count += 1
                    if count >= max_count: return
        
        # 5. المبني للمجهول
        for majhool in samples['mabni_majhool'][:8]:
            for fael in samples['fael'][:6]:  # نائب فاعل
                if cls._check_compatibility('passive', [majhool, fael]):
                    sentence = f"{majhool} {fael}"
                    add_func(sentence, 'فعل_مبني_للمجهول+نائب_فاعل', 'فعلية',
                           [('فعل مبني للمجهول', majhool), ('نائب فاعل', fael)])
                    count += 1
                    if count >= max_count: return
    
    @classmethod 
    def _generate_nominal_sentences(cls, samples, add_func, max_count):
        """توليد الجمل الاسمية بتراكيب متقدمة"""
        count = 0
        
        # 1. مبتدأ + خبر (أساسي)
        for mobtada in samples['mobtada_khabar'][:10]:
            for khabar in samples['mobtada_khabar'][10:20]:
                if cls._check_compatibility('nominal', [mobtada, khabar]):
                    sentence = f"{mobtada} {khabar}"
                    add_func(sentence, 'مبتدأ+خبر', 'اسمية',
                           [('مبتدأ', mobtada), ('خبر', khabar)])
                    count += 1
                    if count >= max_count: return
        
        # 2. اسم إشارة + اسم + صفة
        for demonstrative in samples['demonstratives'][:8]:
            for noun in samples['nouns'][:8]:
                for adjective in samples['adjectives'][:6]:
                    if cls._check_compatibility('demonstrative', [demonstrative, noun, adjective]):
                        sentence = f"{demonstrative} {noun} {adjective}"
                        add_func(sentence, 'اسم_إشارة+اسم+صفة', 'اسمية',
                               [('اسم إشارة', demonstrative), ('اسم', noun), ('صفة', adjective)])
                        count += 1
                        if count >= max_count: return
        
        # 3. النواسخ (كان وأخواتها، إن وأخواتها)
        for nasikh in samples['nasikh'][:6]:
            for ism in samples['nouns'][:8]:
                for khabar in samples['adjectives'][:6]:
                    if cls._check_compatibility('nasikh', [nasikh, ism, khabar]):
                        sentence = f"{nasikh} {ism} {khabar}"
                        add_func(sentence, 'ناسخ+اسم+خبر', 'اسمية',
                               [('ناسخ', nasikh), ('اسم الناسخ', ism), ('خبر الناسخ', khabar)])
                        count += 1
                        if count >= max_count: return
        
        # 4. أعداد + معدود
        for number in samples['numbers'][:8]:
            for noun in samples['nouns'][:8]:
                if cls._check_compatibility('numerical', [number, noun]):
                    sentence = f"{number} {noun}"
                    add_func(sentence, 'عدد+معدود', 'اسمية',
                           [('عدد', number), ('معدود', noun)])
                    count += 1
                    if count >= max_count: return
    
    @classmethod
    def _generate_complex_sentences(cls, samples, add_func, max_count):
        """توليد التراكيب المعقدة والجمل المركبة"""
        count = 0
        
        # 1. جمل الاستفهام
        for interrogative in samples['interrogatives'][:6]:
            for verb in samples['verbs'][:8]:
                for noun in samples['nouns'][:6]:
                    if cls._check_compatibility('interrogative', [interrogative, verb, noun]):
                        sentence = f"{interrogative} {verb} {noun}"
                        add_func(sentence, 'استفهام+فعل+اسم', 'استفهامية',
                               [('أداة استفهام', interrogative), ('فعل', verb), ('اسم', noun)])
                        count += 1
                        if count >= max_count: return
        
        # 2. جمل الشرط
        for conditional in samples['conditionals'][:4]:
            for verb1 in samples['verbs'][:6]:
                for verb2 in samples['verbs'][:6]:
                    if cls._check_compatibility('conditional', [conditional, verb1, verb2]):
                        sentence = f"{conditional} {verb1} {verb2}"
                        add_func(sentence, 'شرط+فعل_الشرط+جواب_الشرط', 'شرطية',
                               [('أداة شرط', conditional), ('فعل الشرط', verb1), ('جواب الشرط', verb2)])
                        count += 1
                        if count >= max_count: return
        
        # 3. النداء
        for nida in samples['vocatives'][:4]:
            for noun in samples['nouns'][:8]:
                if cls._check_compatibility('vocative', [nida, noun]):
                    sentence = f"{nida} {noun}"
                    add_func(sentence, 'نداء+منادى', 'ندائية',
                           [('أداة نداء', nida), ('منادى', noun)])
                    count += 1
                    if count >= max_count: return
        
        # 4. الجمل الموصولة
        for relative in samples['relatives'][:4]:
            for verb in samples['verbs'][:6]:
                for pronoun in samples['pronouns'][:4]:
                    if cls._check_compatibility('relative', [relative, verb, pronoun]):
                        sentence = f"{relative} {verb} {pronoun}"
                        add_func(sentence, 'اسم_موصول+صلة_الموصول', 'موصولية',
                               [('اسم موصول', relative), ('فعل', verb), ('ضمير', pronoun)])
                        count += 1
                        if count >= max_count: return
    
    @classmethod
    def _check_compatibility(cls, pattern_type, components):
        """خوارزمية التحقق من التوافق النحوي"""
        if not components or any(not comp.strip() for comp in components):
            return False
            
        # قواعد الاستثناء حسب نوع النمط
        if pattern_type == 'verbal':
            # التحقق من تطابق الفعل مع الفاعل في الجنس والعدد
            verb, fael = components[0], components[1]
            if cls._is_feminine_noun(fael) and not cls._is_feminine_verb(verb):
                return False
            
        elif pattern_type == 'nominal':
            # التحقق من تطابق المبتدأ والخبر
            mobtada, khabar = components[0], components[1]
            if cls._is_definite(mobtada) and cls._is_indefinite(khabar):
                return True  # هذا صحيح نحوياً
                
        elif pattern_type == 'demonstrative':
            # اسم الإشارة يجب أن يتطابق مع الاسم في الجنس والعدد
            demonstrative, noun = components[0], components[1]
            if 'هذه' in demonstrative and not cls._is_feminine_noun(noun):
                return False
                
        elif pattern_type == 'numerical':
            # قواعد الأعداد معقدة - نبسطها
            number, noun = components[0], components[1]
            if any(x in number for x in ['ثلاثة', 'أربعة', 'خمسة']) and cls._is_feminine_noun(noun):
                return True
                
        return True  # افتراضياً صحيح إذا لم تنطبق قواعد الاستثناء
    
    @classmethod
    def _is_feminine_noun(cls, noun):
        """تحديد إذا كان الاسم مؤنث"""
        return noun.endswith('ة') or noun in ['فاطمة', 'عائشة', 'زينب', 'مريم']
    
    @classmethod
    def _is_feminine_verb(cls, verb):
        """تحديد إذا كان الفعل مؤنث"""
        return 'ت' in verb[-2:] or verb.startswith('ت')
    
    @classmethod
    def _is_definite(cls, noun):
        """تحديد إذا كان الاسم معرفة"""
        return noun.startswith('ال') or noun in ['محمد', 'أحمد', 'علي', 'فاطمة']
    
    @classmethod
    def _is_indefinite(cls, noun):
        """تحديد إذا كان الاسم نكرة"""
        return not cls._is_definite(noun)
    
    @classmethod
    def _describe_phonology(cls, text):
        """وصف الخصائص الصوتية للنص"""
        # نفس المنطق من المحرك الأصلي
        d = {'fatha': 0, 'damma': 0, 'kasra': 0, 'sukun': 0, 'shadda': 0}
        for ch in text:
            oc = ord(ch)
            if oc == 0x064E: d['fatha'] += 1
            elif oc == 0x064F: d['damma'] += 1  
            elif oc == 0x0650: d['kasra'] += 1
            elif oc == 0x0652: d['sukun'] += 1
            elif oc == 0x0651: d['shadda'] += 1
        
        words = len([w for w in text.split() if w])
        return f"كلمات: {words}؛ فتحة: {d['fatha']}؛ ضمة: {d['damma']}؛ كسرة: {d['kasra']}"
    
    @classmethod
    def _derive_morphological_function(cls, components):
        """اشتقاق الوظيفة المورفولوجية من المكونات"""
        morph_parts = []
        for label, token in components:
            if 'فعل' in label:
                morph_parts.append(f"{label}:ثلاثي مجرد")
            elif 'اسم' in label or 'فاعل' in label:
                morph_parts.append(f"{label}:اسم جامد/مشتق")
            else:
                morph_parts.append(f"{label}:مبني")
        return ' | '.join(morph_parts)
    
    @classmethod
    def _semantic_function(cls, sentence_type, pattern):
        """تحديد الوظيفة الدلالية"""
        if 'استفهام' in sentence_type:
            return 'طلب الفهم'
        elif 'شرط' in sentence_type:
            return 'ربط شرطي'
        elif 'نداء' in sentence_type:
            return 'طلب الإقبال'
        else:
            return 'إخبار أو وصف'
    
    @classmethod
    def _get_utf8_components(cls, components):
        """تحويل المكونات إلى UTF-8"""
        utf8_parts = []
        for label, token in components:
            try:
                utf8_hex = ' '.join(f"0x{b:02x}" for b in token.encode('utf-8'))
                utf8_parts.append(f"{label}:{utf8_hex}")
            except:
                utf8_parts.append(f"{label}:")
        return ' | '.join(utf8_parts)