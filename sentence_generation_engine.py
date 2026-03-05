import pandas as pd
from base_reconstruction_engine import BaseReconstructionEngine
from atf_engine import AtfEngine
from nafi_engine import NafiEngine
from jar_engine import JarEngine
from pronouns_engine import PronounsEngine
from adverbs_engine import AdverbsEngine
from proper_nouns_engine import ProperNounsEngine
from qasr_engine import QasrEngine
from generic_nouns_engine import GenericNounsEngine
from reconstruction_utils import reconstruct_from_base_df

class SentenceGenerationEngine(BaseReconstructionEngine):
    SHEET_NAME = 'جُمَل_مولدة'

    @classmethod
    def make_df(cls):
        # الحصول على أول/أولَيْن من كل محرك لتوليد أمثلة متنوعة
        def first(df, i=0):
            return dataframe.iloc[i]['الأداة'] if (not dataframe.empty and i < len(df)) else ''
        def phon_utf_map(df):
            # يعيد قائمة من tuples (tool, utf8)
            out = []
            if not dataframe.empty and 'الأداة' in dataframe.columns:
                for _, r in dataframe.head(5).iterrows():
                    out.append((r['الأداة'], r.get('UTF-8', '')))
            return out

        dfs = {
            'conj': AtfEngine.make_df(),
            'neg': NafiEngine.make_df(),
            'prep': JarEngine.make_df(),
            'pron': PronounsEngine.make_df(),
            'zarf': AdverbsEngine.make_df(),
            'prop': ProperNounsEngine.make_df(),
            'qasr': QasrEngine.make_df(),
            'nouns': GenericNounsEngine.make_df(),
        }

        # أدوات ومفردات جاهزة من المحركات
        neg = first(dfs['neg'])
        conj = first(dfs['conj'])
        # انتقاء حرف جر محدد: "في" من سطر ظرفية
        prep_df = dfs['prep']
        prep_row = prep_df[prep_df['القالب/التركيب'] == 'ظرفية'] if 'القالب/التركيب' in prep_df.columns else pd.DataFrame()
        prep_fi = prep_row.iloc[0]['الأداة'] if not prep_row.empty else first(prep_df)
        # ظروف وأعلام
        z_yawm = ''
        z_ams = ''
        z_huna = ''
        z_hunak = ''
        if not dfs['zarf'].empty:
            def pick_z(name):
                dfz = dfs['zarf']
                m = dfz[dfz['الأداة'] == name] if 'الأداة' in dfz.columns else pd.DataFrame()
                return m.iloc[0]['الأداة'] if not m.empty else ''
            z_yawm = pick_z('اليوم') or first(dfs['zarf'])
            z_ams = pick_z('أَمْسِ') or first(dfs['zarf'], 1) or z_yawm
            z_huna = pick_z('هُنَا') or first(dfs['zarf'], 2) or z_yawm
            z_hunak = pick_z('هُنَاك') or first(dfs['zarf'], 3) or z_huna
        pron_df = dfs['pron']
        pron_huwa = ''
        pron_anta = ''
        if not pron_df.empty:
            def pick_p(name):
                mp = pron_df[pron_df['الأداة'] == name] if 'الأداة' in pron_df.columns else pd.DataFrame()
                return mp.iloc[0]['الأداة'] if not mp.empty else ''
            pron_huwa = pick_p('هُوَ') or first(pron_df)
            pron_anta = pick_p('أَنْتَ') or first(pron_df, 1) or pron_huwa
        prop_df = dfs['prop']
        prop_name = first(prop_df) if not prop_df.empty else ''
        qasr_tool = first(dfs['qasr'])
        nouns_df = dfs['nouns']
        # قوائم مختارة
        def take_tokens(df, limit=8):
            if dataframe.empty or 'الأداة' not in dataframe.columns:
                return []
            vals = [x for x in df['الأداة'].head(limit).tolist() if isinstance(x, str) and x.strip()]
            return vals
        pron_list = take_tokens(pron_df, limit=6)
        prop_list = take_tokens(prop_df, limit=8)
        zarf_list = take_tokens(dfs['zarf'], limit=8)
        nouns_list = take_tokens(nouns_df, limit=10)
        neg_list = take_tokens(dfs['neg'], limit=5)
        conj_list = take_tokens(dfs['conj'], limit=3)
        # مجموعة من حروف الجر المستهدفة حسب القالب/التركيب
        def pick_prep_by_pattern(pat):
            if prep_df.empty:
                return ''
            if 'القالب/التركيب' in prep_df.columns:
                row = prep_df[prep_df['القالب/التركيب'] == pat]
                if not row.empty:
                    return row.iloc[0]['الأداة']
            return ''
        preps = [
            prep_fi,
            pick_prep_by_pattern('انتهاء الغاية'),  # إلى
            pick_prep_by_pattern('ابتداء الغاية'),   # من
            pick_prep_by_pattern('استعلاء'),        # على
            pick_prep_by_pattern('مجاوزة'),         # عن
            pick_prep_by_pattern('استعانة/سببية'),  # ب
        ]
        preps = [p for p in preps if p]

        # أفعال حقيقية مُشكّلة للاستخدام داخل المُولِّد
        verbs = {
            'past': 'كَتَبَ',
            'present': 'يَكْتُبُ',
            'imperative': 'اِقْرَأْ',
        }

        sentences = []

        def utf8_hex(s: str) -> str:
            try:
                return ' '.join(f"0x{b:02x}" for b in s.encode('utf-8'))
            except Exception:
                return ''

        def describe_phonology(text: str) -> str:
            # يحسب ملخصاً صوتياً بسيطاً يعتمد على التشكيل وحروف المد
            d = {
                'fatha': 0, 'damma': 0, 'kasra': 0,
                'sukun': 0, 'shadda': 0,
                'tanween_fath': 0, 'tanween_damm': 0, 'tanween_kasr': 0,
                'madda': 0, 'sup_alef': 0,
                'alef': 0, 'waw': 0, 'ya': 0,
            }
            for ch in text:
                oc = ord(ch)
                if oc == 0x064E: d['fatha'] += 1  # فتحة
                elif oc == 0x064F: d['damma'] += 1  # ضمة
                elif oc == 0x0650: d['kasra'] += 1  # كسرة
                elif oc == 0x0652: d['sukun'] += 1  # سكون
                elif oc == 0x0651: d['shadda'] += 1  # شدة
                elif oc == 0x064B: d['tanween_fath'] += 1  # تنوين فتح
                elif oc == 0x064C: d['tanween_damm'] += 1  # تنوين ضم
                elif oc == 0x064D: d['tanween_kasr'] += 1  # تنوين كسر
                elif oc == 0x0653: d['madda'] += 1  # مدة فوقية
                elif oc == 0x0670: d['sup_alef'] += 1  # ألف خنجرية
                elif oc == 0x0627: d['alef'] += 1  # ألف
                elif oc == 0x0648: d['waw'] += 1  # واو
                elif oc == 0x064A: d['ya'] += 1   # ياء
            words = len([w for w in text.split() if w])
            return (
                f"عدد الكلمات: {words}؛ فتحة: {d['fatha']}؛ ضمة: {d['damma']}؛ كسرة: {d['kasra']}؛ "
                f"سكون: {d['sukun']}؛ شدة: {d['shadda']}؛ تنوين (فتح/ضم/كسر): {d['tanween_fath']}/{d['tanween_damm']}/{d['tanween_kasr']}؛ "
                f"مدة: {d['madda']}؛ ألف خنجرية: {d['sup_alef']}؛ حروف مد (ا/و/ي): {d['alef']}/{d['waw']}/{d['ya']}"
            )

        def add_sentence(sentence, pattern, stype, components):
            comp_utf = []
            comp_morph = []
            for label, token in components:
                # ابحث عن UTF-8 لكل مكوّن بالمرور على الداتا فريم المناسبة
                utf_val = ''
                morph_val = ''
                for key, dfv in dfs.items():
                    if 'الأداة' in dfv.columns:
                        match = dfv[dfv['الأداة'] == token]
                        if not match.empty:
                            utf_val = match.iloc[0].get('UTF-8', '')
                            morph_val = match.iloc[0].get('الوظيفة الاشتقاقية', '') if 'الوظيفة الاشتقاقية' in match.columns else ''
                            break
                if not utf_val and token:
                    utf_val = utf8_hex(token)
                comp_utf.append(f"{label}:{utf_val}")
                # اشتقاق افتراضي إن لم يُعثر عليه في المصدر
                if not morph_val:
                    lbl = (label or '').strip()
                    if 'فعل' in lbl:
                        if token == verbs.get('past'):
                            morph_val = 'فعل ثلاثي مجرد (ماض)'
                        elif token == verbs.get('present'):
                            morph_val = 'فعل ثلاثي مجرد (مضارع)'
                        elif token == verbs.get('imperative'):
                            morph_val = 'فعل ثلاثي مجرد (أمر)'
                        else:
                            morph_val = 'فعل'
                    elif 'ضمير' in lbl:
                        morph_val = 'أصلي غير مشتق'
                    elif 'حرف' in lbl or 'قصر' in lbl or 'نفي' in lbl or 'عطف' in lbl:
                        morph_val = 'حرف/أداة مبنية (غير مشتقة)'
                    elif 'علم' in lbl:
                        morph_val = 'اسم علم (غالبًا غير مشتق)'
                    elif 'ظرف' in lbl:
                        morph_val = 'اسم مبني/معرب بحسب السياق (غالبًا غير مشتق)'
                    elif 'اسم' in lbl:
                        morph_val = 'اسم (جامد/مشتق بحسب الأصل)'
                comp_morph.append(f"{label}:{morph_val}" if morph_val else f"{label}:")
            sound_profile = describe_phonology(sentence)
            sentences.append({
                'الأداة': sentence.strip(),
                'القالب/التركيب': pattern,
                'النوع': stype,
                'مكوّنات': ' | '.join(f"{lbl}={tok}" for lbl, tok in components),
                'UTF-8 للمكوّنات': ' | '.join(comp_utf),
                'الفونيمات': '',
                'الحركات': '',
                'شرط/سياق': 'توليد آلي',
                'الوظيفة النحوية': f'جملة {stype}',
                'الوظيفة الدلالية': 'مثال تركيبي',
                'الوظيفة الصرفية': 'تركيب',
                'الوظيفة الصوتية': sound_profile,
                'الوظيفة الاشتقاقية': ' | '.join(comp_morph),
                'ملاحظات': 'مولد'
            })

        # مولد واسع بنقطة توقف معقولة
        MAX_SENTENCES = 600
        seen = set()

        def push(sent, pat, stype, comps):
            s = ' '.join(str(x) for x in sent.split() if x)
            if not s or s in seen:
                return
            seen.add(s)
            add_sentence(s, pat, stype, comps)

        # فعلية: ضمائر × مضارع × ظروف
        for pr in pron_list:
            for zv in zarf_list[:5]:
                push(f"{pr} {verbs['present']} {zv}", 'ضمير+فعل مضارع+ظرف', 'فعلية', [('ضمير', pr), ('فعل', verbs['present']), ('ظرف', zv)])
                if len(seen) >= MAX_SENTENCES: break
            if len(seen) >= MAX_SENTENCES: break

        # فعلية: أعلام × ماض × ظروف
        for pn in prop_list:
            for zv in zarf_list[:4]:
                push(f"{pn} {verbs['past']} {zv}", 'علم+فعل ماض+ظرف', 'فعلية', [('علم', pn), ('فعل', verbs['past']), ('ظرف', zv)])
                if len(seen) >= MAX_SENTENCES: break
            if len(seen) >= MAX_SENTENCES: break

        # فعلية: نفي + ضمير + مضارع + اسم
        for ng in neg_list[:3]:
            for pr in pron_list[:4]:
                for nn in nouns_list[:6]:
                    push(f"{ng} {pr} {verbs['present']} {nn}", 'نفي+ضمير+مضارع+اسم', 'فعلية', [('نفي', ng), ('ضمير', pr), ('فعل', verbs['present']), ('اسم', nn)])
                    if len(seen) >= MAX_SENTENCES: break
                if len(seen) >= MAX_SENTENCES: break
            if len(seen) >= MAX_SENTENCES: break

        # فعلية: فعل أمر + ضمير مخاطب
        for pr in [pron_anta] + [p for p in pron_list if p != pron_anta][:2]:
            push(f"{verbs['imperative']} {pr}", 'فعل أمر+ضمير', 'فعلية', [('فعل', verbs['imperative']), ('ضمير', pr)])
            if len(seen) >= MAX_SENTENCES: break

        # فعلية مركبة: ضمير + مضارع + اسم + جار ومجرور
        for pr in pron_list[:4]:
            for nn in nouns_list[:5]:
                for pp in preps[:3]:
                    for zv in zarf_list[:3]:
                        push(f"{pr} {verbs['present']} {nn} {pp} {zv}", 'ضمير+مضارع+اسم+جار+ظرف', 'فعلية', [('ضمير', pr), ('فعل', verbs['present']), ('اسم', nn), ('حرف جر', pp), ('اسم مجرور/ظرف', zv)])
                        if len(seen) >= MAX_SENTENCES: break
                    if len(seen) >= MAX_SENTENCES: break
                if len(seen) >= MAX_SENTENCES: break
            if len(seen) >= MAX_SENTENCES: break

        # اسمية: علم + اسم (خبر)
        for pn in prop_list[:6]:
            for nn in nouns_list[:6]:
                push(f"{pn} {nn}", 'مبتدأ (علم)+خبر (اسم)', 'اسمية', [('مبتدأ', pn), ('خبر', nn)])
                if len(seen) >= MAX_SENTENCES: break
            if len(seen) >= MAX_SENTENCES: break

        # اسمية بالقصر
        if qasr_tool:
            for pn in prop_list[:4]:
                for nn in nouns_list[:4]:
                    push(f"{qasr_tool} {pn} {nn}", 'قصر+مبتدأ+خبر', 'اسمية', [('قصر', qasr_tool), ('مبتدأ', pn), ('خبر', nn)])
                    if len(seen) >= MAX_SENTENCES: break
                if len(seen) >= MAX_SENTENCES: break

        # شبه جملة: حروف جر × أسماء/ظروف
        for pp in preps:
            for nn in (nouns_list[:6] + zarf_list[:4]):
                push(f"{pp} {nn}", 'جار+مجرور/ظرف', 'شبه جملة', [('حرف جر', pp), ('اسم/ظرف', nn)])
                if len(seen) >= MAX_SENTENCES: break
            if len(seen) >= MAX_SENTENCES: break

        # عطف: حرف عطف + جملة فعلية قصيرة
        for cj in conj_list:
            for pn in prop_list[:3]:
                for zv in zarf_list[:2]:
                    clause = f"{pn} {verbs['past']} {zv}"
                    push(f"{cj} {clause}", 'عطف+جملة فعلية', 'فعلية', [('عطف', cj), ('جملة', clause)])
                    if len(seen) >= MAX_SENTENCES: break
                if len(seen) >= MAX_SENTENCES: break
            if len(seen) >= MAX_SENTENCES: break

        # توسعة الجمل الاسمية: مبتدأ (ضمير/علم/اسم) + خبر (اسم/ظرف/شبه جملة)
        # 1) ضمير + اسم
        for pr in pron_list[:5]:
            for nn in nouns_list[:8]:
                push(f"{pr} {nn}", 'مبتدأ (ضمير)+خبر (اسم)', 'اسمية', [('مبتدأ', pr), ('خبر', nn)])
                if len(seen) >= MAX_SENTENCES: break
            if len(seen) >= MAX_SENTENCES: break
        # 2) علم + ظرف
        for pn in prop_list[:8]:
            for zv in [z_huna, z_hunak, z_yawm, z_ams]:
                if zv:
                    push(f"{pn} {zv}", 'مبتدأ (علم)+خبر (ظرف)', 'اسمية', [('مبتدأ', pn), ('خبر', zv)])
                    if len(seen) >= MAX_SENTENCES: break
            if len(seen) >= MAX_SENTENCES: break
        # 3) اسم + اسم (خبر مفرد)
        for i, n1 in enumerate(nouns_list[:10]):
            for j, n2 in enumerate(nouns_list[:10]):
                if i == j:
                    continue
                push(f"{n1} {n2}", 'مبتدأ (اسم)+خبر (اسم)', 'اسمية', [('مبتدأ', n1), ('خبر', n2)])
                if len(seen) >= MAX_SENTENCES: break
            if len(seen) >= MAX_SENTENCES: break
        # 4) قصر + علم + ظرف
        if qasr_tool:
            for pn in prop_list[:6]:
                for zv in [z_huna, z_hunak]:
                    if zv:
                        push(f"{qasr_tool} {pn} {zv}", 'قصر+مبتدأ+خبر (ظرف)', 'اسمية', [('قصر', qasr_tool), ('مبتدأ', pn), ('خبر', zv)])
                        if len(seen) >= MAX_SENTENCES: break
                if len(seen) >= MAX_SENTENCES: break
        # 5) نفي + علم + ظرف
        for ng in neg_list[:3]:
            for pn in prop_list[:6]:
                for zv in [z_huna, z_hunak]:
                    if zv:
                        push(f"{ng} {pn} {zv}", 'نفي+مبتدأ+خبر (ظرف)', 'اسمية', [('نفي', ng), ('مبتدأ', pn), ('خبر', zv)])
                        if len(seen) >= MAX_SENTENCES: break
                if len(seen) >= MAX_SENTENCES: break
            if len(seen) >= MAX_SENTENCES: break

        # توسعة شبه الجملة (جار ومجرور):
        # 1) حروف جر × أسماء جنس
        for pp in preps:
            for nn in nouns_list[:10]:
                push(f"{pp} {nn}", 'جار+مجرور', 'شبه جملة', [('حرف جر', pp), ('اسم مجرور', nn)])
                if len(seen) >= MAX_SENTENCES: break
            if len(seen) >= MAX_SENTENCES: break
        # 2) من/إلى + هنا/هناك
        # اختيار دقيق لـ "من" و"إلى"
        prep_min = ''
        prep_ila = ''
        if 'القالب/التركيب' in prep_df.columns and not prep_df.empty:
            row_min = prep_df[prep_df['القالب/التركيب'] == 'ابتداء الغاية']
            row_ila = prep_df[prep_df['القالب/التركيب'] == 'انتهاء الغاية']
            prep_min = row_min.iloc[0]['الأداة'] if not row_min.empty else ''
            prep_ila = row_ila.iloc[0]['الأداة'] if not row_ila.empty else ''
        for zv in [z_huna, z_hunak]:
            if zv and prep_min:
                push(f"{prep_min} {zv}", 'جار+ظرف مكان', 'شبه جملة', [('حرف جر', prep_min), ('ظرف مكان', zv)])
            if zv and prep_ila:
                push(f"{prep_ila} {zv}", 'جار+ظرف مكان', 'شبه جملة', [('حرف جر', prep_ila), ('ظرف مكان', zv)])
            if len(seen) >= MAX_SENTENCES: break
        # 3) تركيب مركب: جار+مجرور + جار+ظرف (قصير)
        for pp in preps[:3]:
            for nn in nouns_list[:4]:
                for zv in [z_huna, z_hunak]:
                    if zv:
                        push(f"{pp} {nn} {prep_fi} {zv}", 'جار+مجرور+جار+ظرف', 'شبه جملة', [('حرف جر', pp), ('اسم مجرور', nn), ('حرف جر', prep_fi), ('ظرف', zv)])
                        if len(seen) >= MAX_SENTENCES: break
                if len(seen) >= MAX_SENTENCES: break
            if len(seen) >= MAX_SENTENCES: break

        return reconstruct_from_base_df(pd.DataFrame(sentences))
