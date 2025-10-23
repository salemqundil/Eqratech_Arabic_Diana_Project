import pandas as pd
import sys
import os

class StaticSentenceGenerator:
    """
    مولد جمل يستخدم بيانات ثابتة لتجنب مشاكل المحركات
    """
    
    def __init__(self):
        self.sentences = []
        self.MAX_SENTENCES = 5000
        
    def get_static_data(self):
        """الحصول على بيانات ثابتة للتوليد"""
        data = {
            # فاعل
            'fael': ['أحمد', 'فاطمة', 'الرجل', 'المرأة', 'الطالب', 'الطالبة', 'الولد', 'البنت', 
                    'المعلم', 'المعلمة', 'الطبيب', 'الممرضة', 'الكاتب', 'القارئ', 'الباحث'],
            
            # أفعال
            'verbs': ['كتب', 'قرأ', 'درس', 'علم', 'جلس', 'قام', 'ذهب', 'جاء', 'أكل', 'شرب', 
                     'نام', 'استيقظ', 'سافر', 'وصل', 'فهم', 'تعلم', 'عمل', 'ساعد', 'لعب', 'مشى'],
            
            # مفعول به
            'mafool': ['الكتاب', 'الدرس', 'القلم', 'الورقة', 'الطعام', 'الماء', 'الرسالة', 'الخبر',
                      'الحقيقة', 'العلم', 'الفن', 'اللغة', 'القصة', 'الشعر', 'المقال'],
            
            # أسماء عامة
            'nouns': ['البيت', 'المدرسة', 'الحديقة', 'المكتبة', 'السوق', 'المسجد', 'الشارع', 
                     'الجامعة', 'المستشفى', 'المتحف', 'المطعم', 'الفندق', 'المطار', 'المحطة'],
            
            # صفات
            'adjectives': ['جميل', 'كبير', 'صغير', 'طويل', 'قصير', 'ذكي', 'نشيط', 'مجتهد', 
                          'سعيد', 'حزين', 'جديد', 'قديم', 'سريع', 'بطيء', 'قوي', 'ضعيف'],
            
            # حروف جر
            'jar': ['في', 'إلى', 'من', 'على', 'عن', 'مع', 'بدون', 'ضد', 'حول', 'تحت', 'فوق', 'أمام', 'خلف'],
            
            # أدوات نفي
            'nafi': ['لا', 'ما', 'لم', 'لن', 'ليس'],
            
            # أدوات استفهام
            'istifham': ['هل', 'ماذا', 'متى', 'أين', 'كيف', 'لماذا', 'مَن', 'ما'],
            
            # أدوات عطف
            'atf': ['و', 'أو', 'لكن', 'بل', 'ثم'],
            
            # أسماء إشارة
            'demonstratives': ['هذا', 'هذه', 'ذلك', 'تلك', 'هؤلاء', 'أولئك'],
            
            # ظروف
            'adverbs': ['اليوم', 'أمس', 'غداً', 'الآن', 'صباحاً', 'مساءً', 'هنا', 'هناك', 'بسرعة', 'ببطء'],
            
            # أعلام
            'proper_nouns': ['محمد', 'علي', 'خديجة', 'عائشة', 'مكة', 'المدينة', 'القاهرة', 'بغداد', 'دمشق'],
            
            # نداء
            'nida': ['يا', 'أيّ', 'أيّتها'],
        }
        return data
    
    def add_sentence(self, sentence, pattern, stype, components):
        """إضافة جملة للمجموعة"""
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
            'شرط/سياق': 'static generation',
            'الوظيفة النحوية': f'جملة {stype}',
            'الوظيفة الدلالية': 'مثال تطبيقي',
            'الوظيفة الصرفية': 'تركيب',
            'الوظيفة الصوتية': f'كلمات:{len(sentence.split())}',
            'الوظيفة الاشتقاقية': pattern,
            'ملاحظات': f'مولد من نمط: {pattern}'
        })
        
        return True
    
    def generate_comprehensive_sentences(self):
        """توليد مجموعة شاملة من الجمل"""
        print("\n=== بدء التوليد الشامل للجمل ===")
        
        data = self.get_static_data()
        
        # 1. الجمل الفعلية الأساسية (فاعل + فعل)
        print("[1] الجمل الفعلية الأساسية...")
        count1 = 0
        for fael in data['fael']:
            for verb in data['verbs']:
                if self.add_sentence(f"{fael} {verb}", 'فاعل+فعل', 'فعلية', 
                                   [('فاعل', fael), ('فعل', verb)]):
                    count1 += 1
                if len(self.sentences) >= self.MAX_SENTENCES: break
            if len(self.sentences) >= self.MAX_SENTENCES: break
        print(f"   توليد {count1} جملة فعلية أساسية")
        
        # 2. الجمل الفعلية المتعدية (فاعل + فعل + مفعول)
        print("[2] الجمل الفعلية المتعدية...")
        count2 = 0
        for fael in data['fael'][:10]:  # تحديد العدد لتجنب التجاوز
            for verb in data['verbs'][:10]:
                for mafool in data['mafool'][:10]:
                    if self.add_sentence(f"{fael} {verb} {mafool}", 'فاعل+فعل+مفعول', 'فعلية متعدية', 
                                       [('فاعل', fael), ('فعل', verb), ('مفعول به', mafool)]):
                        count2 += 1
                    if len(self.sentences) >= self.MAX_SENTENCES: break
                if len(self.sentences) >= self.MAX_SENTENCES: break
            if len(self.sentences) >= self.MAX_SENTENCES: break
        print(f"   توليد {count2} جملة فعلية متعدية")
        
        # 3. الجمل الاسمية (مبتدأ + خبر)
        print("[3] الجمل الاسمية...")
        count3 = 0
        for mubtada in data['nouns'][:12]:
            for khabar in data['adjectives'][:12]:
                if self.add_sentence(f"{mubtada} {khabar}", 'مبتدأ+خبر', 'اسمية', 
                                   [('مبتدأ', mubtada), ('خبر', khabar)]):
                    count3 += 1
                if len(self.sentences) >= self.MAX_SENTENCES: break
            if len(self.sentences) >= self.MAX_SENTENCES: break
        print(f"   توليد {count3} جملة اسمية")
        
        # 4. الجمل الاستفهامية
        print("[4] الجمل الاستفهامية...")
        count4 = 0
        for istifham in data['istifham'][:6]:
            for fael in data['fael'][:8]:
                for verb in data['verbs'][:8]:
                    if self.add_sentence(f"{istifham} {fael} {verb}", 'استفهام+فاعل+فعل', 'استفهامية', 
                                       [('استفهام', istifham), ('فاعل', fael), ('فعل', verb)]):
                        count4 += 1
                    if len(self.sentences) >= self.MAX_SENTENCES: break
                if len(self.sentences) >= self.MAX_SENTENCES: break
            if len(self.sentences) >= self.MAX_SENTENCES: break
        print(f"   توليد {count4} جملة استفهامية")
        
        # 5. الجمل المنفية
        print("[5] الجمل المنفية...")
        count5 = 0
        for nafi in data['nafi']:
            for fael in data['fael'][:10]:
                for verb in data['verbs'][:10]:
                    if self.add_sentence(f"{nafi} {fael} {verb}", 'نفي+فاعل+فعل', 'منفية', 
                                       [('نفي', nafi), ('فاعل', fael), ('فعل', verb)]):
                        count5 += 1
                    if len(self.sentences) >= self.MAX_SENTENCES: break
                if len(self.sentences) >= self.MAX_SENTENCES: break
            if len(self.sentences) >= self.MAX_SENTENCES: break
        print(f"   توليد {count5} جملة منفية")
        
        # 6. شبه الجمل (جار + مجرور)
        print("[6] شبه الجمل...")
        count6 = 0
        for jar in data['jar']:
            for noun in data['nouns']:
                if self.add_sentence(f"{jar} {noun}", 'جار+مجرور', 'شبه جملة', 
                                   [('حرف جر', jar), ('مجرور', noun)]):
                    count6 += 1
                if len(self.sentences) >= self.MAX_SENTENCES: break
            if len(self.sentences) >= self.MAX_SENTENCES: break
        print(f"   توليد {count6} شبه جملة")
        
        # 7. جمل النداء
        print("[7] جمل النداء...")
        count7 = 0
        for nida in data['nida']:
            for name in data['proper_nouns']:
                if self.add_sentence(f"{nida} {name}", 'نداء+منادى', 'ندائية', 
                                   [('أداة نداء', nida), ('منادى', name)]):
                    count7 += 1
                if len(self.sentences) >= self.MAX_SENTENCES: break
            if len(self.sentences) >= self.MAX_SENTENCES: break
        print(f"   توليد {count7} جملة ندائية")
        
        # 8. جمل الإشارة
        print("[8] جمل الإشارة...")
        count8 = 0
        for demo in data['demonstratives']:
            for noun in data['nouns'][:12]:
                if self.add_sentence(f"{demo} {noun}", 'إشارة+اسم', 'إشارية', 
                                   [('اسم إشارة', demo), ('مشار إليه', noun)]):
                    count8 += 1
                if len(self.sentences) >= self.MAX_SENTENCES: break
            if len(self.sentences) >= self.MAX_SENTENCES: break
        print(f"   توليد {count8} جملة إشارية")
        
        # 9. الجمل الظرفية
        print("[9] الجمل الظرفية...")
        count9 = 0
        for fael in data['fael'][:8]:
            for verb in data['verbs'][:8]:
                for adv in data['adverbs'][:10]:
                    if self.add_sentence(f"{fael} {verb} {adv}", 'فاعل+فعل+ظرف', 'ظرفية', 
                                       [('فاعل', fael), ('فعل', verb), ('ظرف', adv)]):
                        count9 += 1
                    if len(self.sentences) >= self.MAX_SENTENCES: break
                if len(self.sentences) >= self.MAX_SENTENCES: break
            if len(self.sentences) >= self.MAX_SENTENCES: break
        print(f"   توليد {count9} جملة ظرفية")
        
        # 10. الجمل المعطوفة
        print("[10] الجمل المعطوفة...")
        count10 = 0
        for fael1 in data['fael'][:6]:
            for verb1 in data['verbs'][:6]:
                for atf in data['atf'][:4]:
                    for fael2 in data['fael'][:6]:
                        for verb2 in data['verbs'][:6]:
                            if fael1 != fael2 or verb1 != verb2:  # تجنب التكرار
                                sentence = f"{fael1} {verb1} {atf} {fael2} {verb2}"
                                if self.add_sentence(sentence, 'فاعل+فعل+عطف+فاعل+فعل', 'معطوفة', 
                                                   [('فاعل1', fael1), ('فعل1', verb1), ('عطف', atf), 
                                                    ('فاعل2', fael2), ('فعل2', verb2)]):
                                    count10 += 1
                            if len(self.sentences) >= self.MAX_SENTENCES: break
                        if len(self.sentences) >= self.MAX_SENTENCES: break
                    if len(self.sentences) >= self.MAX_SENTENCES: break
                if len(self.sentences) >= self.MAX_SENTENCES: break
            if len(self.sentences) >= self.MAX_SENTENCES: break
        print(f"   توليد {count10} جملة معطوفة")
        
        # 11. الجمل المركبة (جار+مجرور مع فعل)
        print("[11] الجمل المركبة...")
        count11 = 0
        for fael in data['fael'][:6]:
            for verb in data['verbs'][:6]:
                for jar in data['jar'][:8]:
                    for noun in data['nouns'][:8]:
                        sentence = f"{fael} {verb} {jar} {noun}"
                        if self.add_sentence(sentence, 'فاعل+فعل+جار+مجرور', 'مركبة', 
                                           [('فاعل', fael), ('فعل', verb), ('جار', jar), ('مجرور', noun)]):
                            count11 += 1
                        if len(self.sentences) >= self.MAX_SENTENCES: break
                    if len(self.sentences) >= self.MAX_SENTENCES: break
                if len(self.sentences) >= self.MAX_SENTENCES: break
            if len(self.sentences) >= self.MAX_SENTENCES: break
        print(f"   توليد {count11} جملة مركبة")
        
        # 12. جمل متنوعة (إشارة + اسم + صفة)
        print("[12] جمل وصفية...")
        count12 = 0
        for demo in data['demonstratives'][:4]:
            for noun in data['nouns'][:8]:
                for adj in data['adjectives'][:8]:
                    sentence = f"{demo} {noun} {adj}"
                    if self.add_sentence(sentence, 'إشارة+اسم+صفة', 'وصفية', 
                                       [('إشارة', demo), ('موصوف', noun), ('صفة', adj)]):
                        count12 += 1
                    if len(self.sentences) >= self.MAX_SENTENCES: break
                if len(self.sentences) >= self.MAX_SENTENCES: break
            if len(self.sentences) >= self.MAX_SENTENCES: break
        print(f"   توليد {count12} جملة وصفية")
        
        total = count1 + count2 + count3 + count4 + count5 + count6 + count7 + count8 + count9 + count10 + count11 + count12
        print(f"\n=== انتهى التوليد: {total} جملة إجمالية ===")
        
        return pd.DataFrame(self.sentences) if self.sentences else pd.DataFrame()
    
    def save_comprehensive_excel(self, filename="comprehensive_arabic_sentences.xlsx"):
        """حفظ الجمل الشاملة في Excel"""
        try:
            df = self.generate_comprehensive_sentences()
            
            if not df.empty:
                df.to_excel(filename, index=False, sheet_name='الجمل_المولدة_الشاملة')
                print(f"\n✅ تم حفظ {len(df)} جملة في {filename}")
                
                # إحصائيات
                print(f"\n📊 الإحصائيات:")
                print(f"   • إجمالي الجمل: {len(df)}")
                print(f"   • الأعمدة: {len(df.columns)}")
                
                # أنواع الجمل
                types = df['النوع'].value_counts()
                print(f"   • أنواع الجمل:")
                for stype, count in types.items():
                    print(f"     - {stype}: {count}")
                
                return True
            else:
                print("❌ لم يتم توليد أي جمل")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في الحفظ: {str(e)}")
            return False


# الاستخدام المباشر
if __name__ == "__main__":
    print("🚀 بدء مولد الجمل العربية الشامل...")
    generator = StaticSentenceGenerator()
    success = generator.save_comprehensive_excel("comprehensive_arabic_grammar.xlsx")
    
    if success:
        print("\n🎉 تم إكمال توليد الجمل الشاملة بنجاح!")
    else:
        print("\n💥 فشل في إكمال التوليد!")