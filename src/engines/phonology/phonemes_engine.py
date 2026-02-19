"""
محرك الفونيمات
هذا الملف يتولى تحميل وبناء جدول الفونيمات من ملفات CSV ودمجها مع معلومات
مساعدة (مثل Unicode و UTF-8 و IPA). كما يحتوي على وظائف لبناء ملف
`full_multilayer_grammar.csv` من أربع ملفات إدخال وواجهة مطابقة مع ورقة
القواعد الكاملة.

تاريخ التحديث: 2025-09-16
"""

import os
from typing import Optional

import pandas as pd


_IPA_MAP = {
    'ء': "ʔ", 'أ': "a", 'إ': "i", 'ؤ': "ʔ", 'ئ': "ʔ", 'آ': "aː",
}
# extend map with common letters
_IPA_MAP.update({
    'ا': 'a', 'ب': 'b', 'ت': 't', 'ث': 'θ', 'ج': 'd͡ʒ', 'ح': 'ħ', 'خ': 'x',
    'د': 'd', 'ذ': 'ð', 'ر': 'r', 'ز': 'z', 'س': 's', 'ش': 'ʃ', 'ص': 'sˤ',
    'ض': 'dˤ', 'ط': 'tˤ', 'ظ': 'ðˤ', 'ع': 'ʕ', 'غ': 'ɣ', 'ف': 'f', 'ق': 'q',
    'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n', 'ه': 'h', 'و': 'w', 'ي': 'j', 'ى': 'a'
})


def _make_unicode_field(token: str) -> str:
    parts = str(token).split('/')
    return '/'.join(f"U+{ord(ch):04X}" for ch in parts)


def _make_utf8_field(token: str) -> str:
    parts = str(token).split('/')

    def esc(ch: str) -> str:
        return ''.join(f"\\x{b:02x}" for b in ch.encode('utf-8'))

    return "b'" + '/'.join(esc(ch) for ch in parts) + "'"


class PhonemesEngine:
    @staticmethod
    def _find_phoneme_col(df: pd.DataFrame) -> str:
        for c in df.columns:
            if c.lower() in ('phoneme_char', 'phoneme_id', 'الفونيمات', 'الفونيم', 'phoneme'):
                return c
        return df.columns[-1]

    @staticmethod
    def _agg_first_nonempty(series: pd.Series) -> str:
        for v in series.astype(str):
            if v and str(v).strip() not in ('*', 'NULL'):
                return v
        return ''

    @staticmethod
    def build_from_input_files(
        semantic_csv: str,
        morphological_csv: str,
        syntactic_csv: str,
        phonetic_csv: str,
        out_csv: Optional[str] = None,
    ) -> pd.DataFrame:
        """Merge four input CSVs to produce `full_multilayer_grammar.csv`.

        Each input CSV is expected to include a column identifying the phoneme
        (heuristically detected). The function aggregates fields per phoneme.
        """
        for p in (semantic_csv, morphological_csv, syntactic_csv, phonetic_csv):
            if not os.path.exists(p):
                raise FileNotFoundError(f"Input CSV not found: {p}")

        sem_df = pd.read_csv(semantic_csv, dtype=str).fillna('')
        morph_df = pd.read_csv(morphological_csv, dtype=str).fillna('')
        synt_df = pd.read_csv(syntactic_csv, dtype=str).fillna('')
        phon_df = pd.read_csv(phonetic_csv, dtype=str).fillna('')

        sem_key = PhonemesEngine._find_phoneme_col(sem_df)
        morph_key = PhonemesEngine._find_phoneme_col(morph_df)
        synt_key = PhonemesEngine._find_phoneme_col(synt_df)
        phon_key = PhonemesEngine._find_phoneme_col(phon_df)

        sem_df = sem_df.rename(columns={sem_key: 'الفونيم'})
        morph_df = morph_df.rename(columns={morph_key: 'الفونيم'})
        synt_df = synt_df.rename(columns={synt_key: 'الفونيم'})
        phon_df = phon_df.rename(columns={phon_key: 'الفونيم'})

        all_phonemes = pd.Series(pd.concat([sem_df['الفونيم'], morph_df['الفونيم'], synt_df['الفونيم'], phon_df['الفونيم']]).unique())

        rows = []
        for p in all_phonemes:
            row = {'الفونيمات': p}

            sem_rows = sem_df[sem_df['الفونيم'] == p]
            morph_rows = morph_df[morph_df['الفونيم'] == p]
            synt_rows = synt_df[synt_df['الفونيم'] == p]
            phon_rows = phon_df[phon_df['الفونيم'] == p]

            # pick fields
            row['الوظيفة الدلالية'] = ''
            for col in sem_rows.columns:
                if col == 'الفونيم':
                    continue
                if col in ('الوظيفة الدلالية', 'description', 'function_typeنوع الوظيفة', 'description الوصف'):
                    row['الوظيفة الدلالية'] = PhonemesEngine._agg_first_nonempty(sem_rows[col])

            row['الوظيفة الصرفية'] = ''
            for col in morph_rows.columns:
                if col == 'الفونيم':
                    continue
                if col in ('الوظيفة الصرفية', 'function_typeنوع الوظيفة', 'description الوصف'):
                    row['الوظيفة الصرفية'] = PhonemesEngine._agg_first_nonempty(morph_rows[col])

            row['الوظيفة النحوية'] = ''
            for col in synt_rows.columns:
                if col == 'الفونيم':
                    continue
                if col in ('الوظيفة النحوية', 'category'):
                    row['الوظيفة النحوية'] = PhonemesEngine._agg_first_nonempty(synt_rows[col])

            row['الوظيفة الصوتية'] = ''
            row['ملاحظات'] = ''
            for col in phon_rows.columns:
                if col == 'الفونيم':
                    continue
                if col in ('الوظيفة الصوتية', 'description', 'category'):
                    row['الوظيفة الصوتية'] = PhonemesEngine._agg_first_nonempty(phon_rows[col])
                if col in ('ملاحظات', 'notes'):
                    row['ملاحظات'] = PhonemesEngine._agg_first_nonempty(phon_rows[col])

            # other fields
            row['الوظيفة الاشتقاقية'] = ''
            row['Unicode'] = _make_unicode_field(p)
            row['UTF-8'] = _make_utf8_field(p)
            row['IPA'] = _IPA_MAP.get(str(p)[0], '')
            row['المخرج'] = ''

            rows.append(row)

        out_df = pd.DataFrame(rows, columns=[
            'الفونيمات', 'الوظيفة النحوية', 'الوظيفة الدلالية', 'الوظيفة الصرفية',
            'الوظيفة الصوتية', 'الوظيفة الاشتقاقية', 'Unicode', 'UTF-8', 'IPA', 'المخرج', 'ملاحظات'
        ])

        if out_csv is None:
            out_csv = os.path.join(os.path.dirname(__file__), 'full_multilayer_grammar.csv')

        out_df.to_csv(out_csv, index=False, encoding='utf-8-sig')
        print(f"Built full_multilayer_grammar.csv with {len(out_df)} rows -> {out_csv}")
        return out_df


    @staticmethod
    def make_df_from_csv(csv_path: Optional[str] = None) -> pd.DataFrame:
        """Load phoneme table from CSV (prefer root CSV, fallback to data/)."""
        root_csv = os.path.join(os.path.dirname(__file__), 'الفونيمات.csv')
        data_csv = os.path.join(os.path.dirname(__file__), 'data', 'الفونيمات.csv')
        if csv_path is None:
            if os.path.exists(root_csv):
                csv_path = root_csv
            elif os.path.exists(data_csv):
                csv_path = data_csv
            else:
                csv_path = os.path.join(os.path.dirname(__file__), 'full_multilayer_grammar.csv')

    # تم حذف طباعة مسار ملف CSV بناءً على طلب المستخدم
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV not found: {csv_path}")

        df = pd.read_csv(csv_path, dtype=str).fillna('')
        print("[phonemes_engine] Sample from loaded phoneme data:")
        print(df.head())
        # ensure derived columns
        if 'Unicode' not in df.columns:
            df['Unicode'] = df['الفونيمات'].apply(_make_unicode_field)
        if 'UTF-8' not in df.columns:
            df['UTF-8'] = df['الفونيمات'].apply(_make_utf8_field)
        if 'IPA' not in df.columns:
            df['IPA'] = df['الفونيمات'].apply(lambda t: _IPA_MAP.get(str(t)[0], ''))

        return df

    @staticmethod
    def make_df() -> pd.DataFrame:
        """Compatibility shim for older callers that expect PhonemesEngine.make_df().

        Delegates to make_df_from_csv().
        """
        print("[phonemes_engine] make_df() compatibility shim -> make_df_from_csv")
        df = PhonemesEngine.make_df_from_csv()
        print("--- محتوى شيت الفونيمات ---")
        print(df)
        print("\n[Sample: أول 5 صفوف]")
        print(df.head())
        print("\n[Sample: آخر 5 صفوف]")
        print(df.tail())
        if len(df) > 10:
            print("\n[Sample: 5 صفوف عشوائية]")
            print(df.sample(5, random_state=42))
        return df

    @staticmethod
    def match_with_full_grammar(phonemes_csv: Optional[str] = None, grammar_csv: Optional[str] = None) -> pd.DataFrame:
        """Match a phonemes CSV (or default) with a full grammar CSV and mark matches.

        Returns a merged dataframe with a boolean 'matched' column.
        """
        phon_df = PhonemesEngine.make_df_from_csv(phonemes_csv)

        if grammar_csv is None:
            grammar_csv = os.path.join(os.path.dirname(__file__), 'full_multilayer_grammar.csv')

        print(f"[phonemes_engine] match_with_full_grammar: phonemes_csv={phonemes_csv} grammar_csv={grammar_csv}")
        if not os.path.exists(grammar_csv):
            raise FileNotFoundError(f"Grammar CSV not found: {grammar_csv}")

        gram_df = pd.read_csv(grammar_csv, dtype=str).fillna('')

        # normalize tokens for matching
        def norm(s: str) -> str:
            return ''.join(ch for ch in str(s) if ch.strip())

        phon_df['_norm'] = phon_df['الفونيمات'].apply(norm)
        gram_df['_norm'] = gram_df['الفونيمات'].apply(norm) if 'الفونيمات' in gram_df.columns else gram_df.iloc[:, 0].astype(str).apply(norm)

        merged = phon_df.merge(gram_df, how='left', on='_norm', suffixes=('_phoneme', '_grammar'))

        # compute matched robustly
        if 'الفونيمات_grammar' in merged.columns:
            merged['matched'] = merged['الفونيمات_grammar'].astype(bool)
        else:
            merged['matched'] = merged['_norm'].isin(gram_df['_norm'])

        # drop duplicate grammar columns that duplicate phoneme-side data
        for base in ['الفونيمات', 'الوظيفة النحوية', 'الوظيفة الدلالية', 'الوظيفة الصرفية', 'الوظيفة الصوتية', 'الوظيفة الاشتقاقية', 'Unicode', 'UTF-8', 'المخرج', 'ملاحظات', 'IPA']:
            gcol = f"{base}_grammar"
            if gcol in merged.columns:
                # if a phoneme-side column exists, prefer it and drop grammar variant
                if base in merged.columns:
                    try:
                        merged.drop(columns=[gcol], inplace=True)
                    except Exception:
                        pass

        return merged
