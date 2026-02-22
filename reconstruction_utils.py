import os
import re
import ast
import pandas as pd

from typing import Tuple, Dict, List


HARAKA_NAME_TO_MARK = {
    'فتحة': 'َ', 'الفتحة': 'َ', 'fatha': 'َ',
    'ضمة': 'ُ', 'الضمة': 'ُ', 'damma': 'ُ',
    'كسرة': 'ِ', 'الكسرة': 'ِ', 'kasra': 'ِ',
    'سكون': 'ْ', 'السكون': 'ْ', 'sukun': 'ْ',
    'شدة': 'ّ', 'الشدة': 'ّ', 'shadda': 'ّ',
    'تنوين فتح': 'ً', 'تنوين الفتح': 'ً', 'fathatan': 'ً',
    'تنوين ضم': 'ٌ', 'تنوين الضم': 'ٌ', 'dammatan': 'ٌ',
    'تنوين كسر': 'ٍ', 'تنوين الكسر': 'ٍ', 'kasratan': 'ٍ',
    'مد': 'ٰ', 'ألف خنجرية': 'ٰ', 'madd': 'ٰ'
}

LETTER_PATTERN = re.compile(r'[\u0621-\u064A\u0660-\u0669]')
HARAKA_PATTERN = re.compile(r'[\u064B-\u0652\u0670]')  # يشمل المد (ألف خنجرية)


def _full_unicode(token: str) -> str:
    t = str(token)
    if not t:
        return ''
    return ' '.join(f"U+{ord(ch):04X}" for ch in t)


def _full_utf8(token: str) -> str:
    t = str(token)
    if not t:
        return ''
    return ' '.join(str(ch.encode('utf-8')) for ch in t)


def load_maps() -> Tuple[Dict[str, str], Dict[str, str]]:
    """Load phoneme and harakat UTF-8 maps from their engines."""
    from phonemes_engine import PhonemesEngine
    from harakat_engine import حركات

    phoneme_df = PhonemesEngine.make_df_from_csv()
    phoneme_utf8_map = dict(zip(phoneme_df['الفونيمات'], phoneme_df['UTF-8']))

    harakat_df = حركات.make_df()
    haraka_symbol_col = None
    for cand in ['شكل الحركة', 'الحركات', 'الرمز']:
        if cand in harakat_df.columns:
            haraka_symbol_col = cand
            break
    if haraka_symbol_col is None:
        haraka_symbol_col = harakat_df.columns[0]
    if 'UTF-8' not in harakat_df.columns:
        harakat_df['UTF-8'] = harakat_df[haraka_symbol_col].apply(lambda h: str(str(h)[:1].encode('utf-8')) if h else '')
    harakat_utf8_map = dict(zip(harakat_df[haraka_symbol_col], harakat_df['UTF-8']))
    return phoneme_utf8_map, harakat_utf8_map


def _map_haraka_names_to_marks(tokens: List[str]) -> List[str]:
    out = []
    for t in tokens:
        t_clean = t.strip()
        if not t_clean:
            continue
        # تطبيع بعض الصيغ الشائعة (مسكون => سكون)
        if t_clean == 'مسكون':
            t_clean = 'سكون'
        mark = HARAKA_NAME_TO_MARK.get(t_clean, '')
        if mark:
            out.append(mark)
        elif HARAKA_PATTERN.match(t_clean):
            out.append(t_clean)
        # otherwise ignore unknown token
    return out


def reconstruct_from_base_df(base_df: pd.DataFrame) -> pd.DataFrame:
    phoneme_utf8_map, harakat_utf8_map = load_maps()

    required_cols = ["الأداة", "الفونيمات", "الحركات", "Unicode", "UTF-8", "عدد الفونيمات",
                     "نوع الحركة الأولى", "UTF-8 للحروف", "UTF-8 للحركات"]
    for c in required_cols:
        if c not in base_df.columns:
            base_df[c] = ''

    rows = []
    base_order = list(base_df.columns)

    for _, row in base_df.iterrows():
        # لا نستخدم strip() حتى لا نفقد المسافات الداخلية/النهائية في التعابير المركبة
        raw_tool_val = row.get('الأداة', '')
        tool_existing = str(raw_tool_val) if raw_tool_val is not None else ''
        phoneme_seq = str(row.get('الفونيمات', '')).strip()
        haraka_seq = str(row.get('الحركات', '')).strip()

        phonemes_list = [p for p in phoneme_seq.split() if p]
        harakat_tokens = [h for h in haraka_seq.split() if h]
        # حوّل أسماء الحركات إلى رموز
        harakat_list = _map_haraka_names_to_marks(harakat_tokens)

        # إذا كان النص الأصلي مركباً (يحتوي على مسافة) فقد نحتاج لاستنتاج الفونيمات/الحركات دون تغيير الأداة المعروضة
        multi_word = (' ' in tool_existing)
        if (not phonemes_list or not harakat_list) and tool_existing:
            inferred_letters = [ch for ch in tool_existing if LETTER_PATTERN.match(ch)]
            inferred_harakat = [ch for ch in tool_existing if HARAKA_PATTERN.match(ch)]
            if not phonemes_list:
                phonemes_list = inferred_letters
            if not harakat_list:
                harakat_list = inferred_harakat

        # إلغاء تعبئة الحركات تلقائياً بكلمة "سكون" لأنها سببت ظهور نص حرفي (مسكون...) داخل عمود الأداة.
        # نترك الحركات فارغة إذا لم تُذكر أو يمكن لاحقاً استنتاجها بشكل أكثر دقة (مثلاً عبر قاموس صرفي).
        # ملاحظة: لو أردنا تعبئة سكون فعلي يمكن استعمال الرمز 'ْ' لاحقاً وليس الكلمة.

        # إعادة التركيب بالاعتماد على UTF-8 المخزن لكل فونيم/حركة لضمان أن الناتج مشتق فعلياً من الترميز
        reconstructed = ''
        for i, letter in enumerate(phonemes_list):
            # احصل على تمثيل UTF-8 كسلسلة (مثل b'\xd8\xb9') ثم حوّله إلى بايتات ثم فك ترميزه
            mapped_bytes_str = phoneme_utf8_map.get(letter, '')
            decoded_letter = letter
            if mapped_bytes_str and mapped_bytes_str.startswith("b'"):
                try:
                    bval = ast.literal_eval(mapped_bytes_str)  # آمن مقارنةً بـ eval
                    if isinstance(bval, (bytes, bytearray)):
                        decoded_letter = bval.decode('utf-8')
                except Exception:
                    decoded_letter = letter  # في حالة الفشل نستعمل الحرف الأصلي
            reconstructed += decoded_letter
            if i < len(harakat_list):
                haraka_symbol = harakat_list[i]
                mapped_haraka_bytes = harakat_utf8_map.get(haraka_symbol, '')
                decoded_haraka = haraka_symbol
                if mapped_haraka_bytes and mapped_haraka_bytes.startswith("b'"):
                    try:
                        hb = ast.literal_eval(mapped_haraka_bytes)
                        if isinstance(hb, (bytes, bytearray)):
                            decoded_haraka = hb.decode('utf-8')
                    except Exception:
                        decoded_haraka = haraka_symbol
                reconstructed += decoded_haraka
        if len(harakat_list) > len(phonemes_list):
            reconstructed += ''.join(harakat_list[len(phonemes_list):])
        # الحفاظ على النص الأصلي المركب كما هو في عمود "الأداة" حتى لو استنتجنا فونيمات/حركات في الخلفية
        if multi_word:
            reconstructed = tool_existing or reconstructed
        elif not reconstructed:
            reconstructed = tool_existing

        phoneme_count = len(phonemes_list)
        first_haraka = harakat_list[0] if harakat_list else ''

        unicode_val = _full_unicode(reconstructed)
        utf8_val = _full_utf8(reconstructed)
        utf8_letters_seq = ','.join(phoneme_utf8_map.get(ch, str(ch.encode('utf-8'))) for ch in phonemes_list)
        utf8_harakat_seq = ','.join(harakat_utf8_map.get(h, str(h.encode('utf-8'))) for h in harakat_list)

        new_row = {c: row.get(c, '') for c in base_order}
        # عيّن القيم المعاد بناؤها في الأعمدة الأساسية
        # نملأ أعمدة الفونيمات/الحركات إذا أمكن الاستنتاج (مع الحفاظ على حالة التعابير المركبة ذات المسافات فارغة كما هي)
        if phonemes_list:
            new_row['الفونيمات'] = ' '.join(phonemes_list)
        else:
            new_row['الفونيمات'] = new_row.get('الفونيمات', '')
        if harakat_list:
            new_row['الحركات'] = ' '.join(harakat_list)
        else:
            new_row['الحركات'] = new_row.get('الحركات', '')
        new_row['الأداة'] = reconstructed
        new_row['Unicode'] = unicode_val
        new_row['UTF-8'] = utf8_val
        new_row['عدد الفونيمات'] = phoneme_count if phoneme_count else new_row.get('عدد الفونيمات', '')
        new_row['نوع الحركة الأولى'] = first_haraka or new_row.get('نوع الحركة الأولى', '')
        new_row['UTF-8 للحروف'] = utf8_letters_seq
        new_row['UTF-8 للحركات'] = utf8_harakat_seq
        rows.append(new_row)

    out_df = pd.DataFrame(rows)
    if 'الأداة' in out_df.columns:
        out_df.drop_duplicates(subset=['الأداة'], inplace=True)

    # تعبئة الفراغات في الفونيمات والحركات بعد إعادة التركيب (خاصة للمحركات الجديدة)
    def _derive_phonemes_from_tool(tool: str) -> str:
        letters = [ch for ch in str(tool) if LETTER_PATTERN.match(ch)]
        return ' '.join(letters)
    def _derive_harakat_from_tool(tool: str) -> str:
        marks = [ch for ch in str(tool) if HARAKA_PATTERN.match(ch)]
        return ' '.join(marks)
    if 'الفونيمات' in out_df.columns:
        mask_empty_ph = out_df['الفونيمات'].astype(str).str.strip() == ''
        out_df.loc[mask_empty_ph, 'الفونيمات'] = out_df.loc[mask_empty_ph, 'الأداة'].apply(_derive_phonemes_from_tool)
    if 'الحركات' in out_df.columns:
        mask_empty_h = out_df['الحركات'].astype(str).str.strip() == ''
        out_df.loc[mask_empty_h, 'الحركات'] = out_df.loc[mask_empty_h, 'الأداة'].apply(_derive_harakat_from_tool)
        # تعبئة الحركات تلقائياً (نمط افتراضي: فتحة لكل حرف عدا الأخير سكون) إذا بقيت فارغة تماماً (أي لا حركات حقيقية مستخرجة)
        still_empty = out_df['الحركات'].astype(str).str.strip() == ''
        def _auto_harakat(ph_seq: str) -> str:
            tokens = [p for p in str(ph_seq).split() if p]
            if not tokens:
                return ''
            if len(tokens) == 1:
                return 'سكون'
            return ' '.join(['فتحة'] * (len(tokens)-1) + ['سكون'])
        out_df.loc[still_empty, 'الحركات'] = out_df.loc[still_empty, 'الفونيمات'].apply(_auto_harakat)

    ordered = []
    for c in base_order:
        if c in out_df.columns and c not in ordered:
            ordered.append(c)
    for c in ["عدد الفونيمات", "نوع الحركة الأولى", "UTF-8 للحروف", "UTF-8 للحركات"]:
        if c in out_df.columns and c not in ordered:
            ordered.append(c)
    for c in out_df.columns:
        if c not in ordered:
            ordered.append(c)
    return out_df[ordered]


def load_input_csv(csv_path: str) -> pd.DataFrame:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"لم يتم العثور على ملف الإدخال: {csv_path}")
    try:
        return pd.read_csv(csv_path, dtype=str).fillna('')
    except Exception:
        return pd.read_csv(csv_path, dtype=str, encoding='utf-8-sig').fillna('')
