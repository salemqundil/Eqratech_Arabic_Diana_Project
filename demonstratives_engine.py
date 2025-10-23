
# إعادة كتابة الكود ليقرأ Phonemes.csv وHarakat.csv مباشرة ويولّد جميع التركيبات الممكنة من 3 حروف و3 حركات
import pandas as pd
import os

class DemonstrativesEngine:
    @staticmethod
    def make_df():
        # قراءة ملفات CSV مباشرة
        phonemes_path = r"C:\Users\user\Downloads\Cam_Eqraatech\Diana\Phonemes.csv"
        harakat_path = r"C:\Users\user\Downloads\Cam_Eqraatech\Diana\Harakat.csv"
        phonemes_df = pd.read_csv(phonemes_path, encoding='utf-8')
        harakat_df = pd.read_csv(harakat_path, encoding='utf-8')

        # قائمة أسماء الإشارة الحقيقية مع التشكيل (يمكنك تعديلها أو زيادتها)
        demonstratives = [
            ("هٰذَا", ["ه", "ذ", "ا"], ["َ", "ْ", "َ"]),
            ("هٰذِهِ", ["ه", "ذ", "ه"], ["َ", "ْ", "ِ"]),
            ("هٰؤُلَاءِ", ["ه", "ء", "ل", "ا", "ء"], ["َ", "ْ", "ُ", "َ", "ِ"]),
            ("ذٰلِكَ", ["ذ", "ل", "ك"], ["َ", "ِ", "َ"]),
            ("تِلْكَ", ["ت", "ل", "ك"], ["ِ", "ْ", "َ"]),
            ("أُولَئِكَ", ["ء", "و", "ل", "ا", "ء", "ك"], ["ُ", "ْ", "َ", "ِ", "َ", "َ"]),
            ("هَذَانِ", ["ه", "ذ", "ا", "ن"], ["َ", "َ", "َ", "ِ"]),
            ("هَاتَانِ", ["ه", "ت", "ا", "ن"], ["َ", "َ", "َ", "ِ"]),
            ("هَؤُلَاءِ", ["ه", "ء", "ل", "ا", "ء"], ["َ", "ْ", "ُ", "َ", "ِ"]),
            ("أُولَئِكَ", ["ء", "و", "ل", "ا", "ء", "ك"], ["ُ", "ْ", "َ", "ِ", "َ", "َ"])
        ]
        phoneme_utf8 = {str(row['الفونيمات']).strip(): str(row['UTF-8']).strip() for _, row in phonemes_df.iterrows() if 'الفونيمات' in row and 'UTF-8' in row and len(str(row['الفونيمات']).strip()) == 1}
        haraka_utf8 = {str(row['الحركة']).strip(): str(row['UTF-8']).strip() for _, row in harakat_df.iterrows() if 'الحركة' in row and 'UTF-8' in row and len(str(row['الحركة']).strip()) == 1}
        phoneme_makhraj = {str(row['الفونيمات']).strip(): str(row['المخرج']).strip() if 'المخرج' in row else '' for _, row in phonemes_df.iterrows() if 'الفونيمات' in row and len(str(row['الفونيمات']).strip()) == 1}

        columns = [
            'اسم الاشارة', 'الوظيفة النحوية', 'الوظيفة الدلالية', 'الوظيفة الصرفية', 'الوظيفة الصوتية', 'الوظيفة الاشتقاقية',
            'Unicode', 'UTF-8', 'المخرج', 'ملاحظات',
            'الأثر الإعرابي', 'شرط/سياق',
            'الفونيمات', 'عدد الفونيمات', 'الحركات'
        ]
        data = []
        for name, phonemes_list, harakats_list in demonstratives:
            phonemes = ' '.join(phonemes_list)
            harakats = ' '.join(harakats_list)
            unicode_val = ' '.join([f"U+{ord(l):04X}" for l in phonemes_list])
            utf8_letters = ' '.join([phoneme_utf8.get(l, 'غير متوفر') for l in phonemes_list])
            utf8_harakat = ' '.join([haraka_utf8.get(h, 'غير متوفر') for h in harakats_list])
            utf8_full = utf8_letters + ' ' + utf8_harakat
            makhraj = '،'.join([phoneme_makhraj.get(l, 'غير متوفر') for l in phonemes_list])
            row = {
                'اسم الاشارة': name,
                'الوظيفة النحوية': 'اسم إشارة يُستخدم للدلالة على المشار إليه في الجملة',
                'الوظيفة الدلالية': f'إشارة إلى {name}',
                'الوظيفة الصرفية': 'مبني على السكون/الفتح حسب السياق',
                'الوظيفة الصوتية': f'تتكون من الفونيمات: {phonemes} والحركات: {harakats}',
                'الوظيفة الاشتقاقية': 'غير مشتق، يُركب من الحروف والحركات',
                'Unicode': unicode_val,
                'UTF-8': utf8_full,
                'المخرج': makhraj,
                'ملاحظات': f'اسم إشارة حقيقي: {name}',
                'الأثر الإعرابي': 'مبني دائماً في محل رفع أو نصب أو جر حسب موقعه',
                'شرط/سياق': 'يستخدم للإشارة في سياقات متعددة حسب الحاجة',
                'الفونيمات': phonemes,
                'عدد الفونيمات': len(phonemes_list),
                'الحركات': harakats
            }
            print(f"اسم الاشارة: {name}")
            print(f"  الفونيمات: {phonemes}")
            print(f"  الحركات: {harakats}")
            print(f"  Unicode: {unicode_val}")
            print(f"  UTF-8: {utf8_full}")
            print(f"  المخرج: {makhraj}")
            print(f"  ---")
            data.append(row)
        df = pd.DataFrame(data, columns=columns)
        print("\n--- DataFrame الناتج ---")
        print(df)
        return df

    @staticmethod
    def export_to_excel():
        df = DemonstrativesEngine.make_df()
        out_path = r"C:\Users\user\Downloads\Cam_Eqraatech\Diana\full_multilayer_grammar.xlsx"
        # إذا كان الملف موجوداً، نضيف الشيت، وإلا ننشئ ملف جديد
        if os.path.exists(out_path):
            with pd.ExcelWriter(out_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name='اسم_الإشارة', index=False)
        else:
            with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='اسم_الإشارة', index=False)
