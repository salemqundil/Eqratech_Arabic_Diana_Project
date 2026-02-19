"""\nالملف: export_full_multilayer_grammar_minimal.py\n=============================================\nهذا هو سكربت "التجميع والتصدير" الرئيسي الذي يبني ملفاً واحداً متعدد الطبقات: full_multilayer_grammar.xlsx\nيحتوي على جميع الجداول (Sheets) المولَّدة من المحركات المختلفة (Engines) مرتبةً من الأدنى (الصوتي) إلى الأعلى (التركيبي).\n\nأقسام الشيتات بالترتيب المنطقي:\n1. الأساس الصوتي: \n   - الفونيمات: قائمة الوحدات الصوتية الأساسية (حروف / صوامت / صوائت) مع بيانات وصفية.\n   - الحركات: الحركات/الضبط (الفتحة، الضمة، الكسرة، السكون، الشدة، التنوين بأنواعه...) قبل إعادة الاختزال إلى ٨ حركات معيارية.\n2. الأدوات والحروف المبنية: (العطف، النفي، الجر، النصب، الجزم، الشرط، القصر، الاستفهام، التوكيد، النداء، الاستثناء، التحديد، جواب، تقديم، طباق، مقابلة، إيجاز/إطناب، سجـع، جناس، تشبيه، استعارة، اشتغال، ترادف ...).\n3. الأسماء بمستوياتها: (تعريف/نكرة، أسماء الإشارة، الضمائر، العدد وأسماء العدد، التثنية والجمع، جمع التكسير، الصيغ المشتقة: اسم فاعل، اسم مفعول، صفة، ميمي، اسم مرّة، هيئة، آلة، نسب، تصغير، مصدر صناعي، كناية، صيغ مبالغة، حال، تمييز، ... إضافةً إلى الأعلام، أسماء الجنس، أسماء الأمكنة، الأصوات، الكائنات العاقلة وغير العاقلة، أسماء الله الحسنى، المصطلحات الشرعية، الجنس اللغوي، المبتدأ والخبر، الأسماء المقصورة والممدودة والمنقوصة...).\n4. الأفعال ومُلحقاتها: الأفعال المجردة والمزيدة (التمهيد الحالي)، المبني للمجهول، الفاعل، نائب الفاعل، المفاعيل (به – مطلق – لأجله)، الأفعال الخمسة، الناسخ، الأسماء الموصولة، ...\n5. الجُمَل المُولَّدة: شيت تركيبي (جُمَل_مولدة) يُنشئ أمثلة جمل فعلية / اسمية / شبه جملة مدمجة مع بيانات صوتية واشتقاقية مستخلصة من الشيتات السابقة.\n\nكيف تتم معالجة وإنتاج أعمدة Unicode / UTF-8؟\n------------------------------------------\n1. كل محرك يُنشئ DataFrame مبدئي بعامود "الأداة" (قد يكون نصاً مُشكّلاً أو عدة كلمات).\n2. تمر الجداول عبر دالة إعادة البناء (reconstruct_from_base_df) داخل ملف reconstruction_utils التي تقوم بـ:\n   - الحفاظ على الفراغات الداخلية للأدوات المركبة (multi-word) بدون تفكيك غير مرغوب.\n   - تطبيع بعض أشكال الهمزة/الألف حسب القواعد الموضوعة.\n   - استنتاج الفونيمات والحركات إن كانت فارغة (أولاً من البيانات الجزئية، ثم من نمطية الحروف، ثم fallback تلقائي).\n   - توليد تمثيل Unicode كسلسلة رموز (U+....) لكل حرف.\n   - توليد عمود UTF-8 إما من النص المباشر أو (عند توفره) من تَمثيل بايتات مُخزَّن مُسبقاً (يتم فكّه آمنًا بـ ast.literal_eval إن كان محفوظاً في المصدر).\n   - إزالة أي بقايا تنسيقات غير صالحة مثل إدخالات نصية حرفية لكلمة "سكون" واستبدالها بالعلامة الحقيقية أو بحذفها حسب الحاجة.\n3. في حال تعذّر اشتقاق UTF-8 من المصدر يتم الترميز الحي (text.encode('utf-8')) وتحويل كل بايت إلى شكل سداسي (0xHH).\n4. تُعاد الأعمدة المشتقة (Unicode / UTF-8 / عدد الفونيمات ...) إلى الإطار النهائي قبل الكتابة.\n\nمكوّنات شيت الجُمَل المولَّدة (جُمَل_مولدة):\n- الأداة: الجملة الكاملة المُولَّدة.\n- القالب/التركيب: الوصف البنيوي (مثال: ضمير+فعل مضارع+ظرف).\n- النوع: فعلية / اسمية / شبه جملة.\n- مكوّنات: قائمة العناصر مع قيمها النصية.\n- UTF-8 للمكوّنات: ترميز كل عنصر فرعي.\n- الوظيفة الصوتية: ملخّص عددي للتشكيل وحروف المد في الجملة.\n- الوظيفة الاشتقاقية: تجميع لوصف اشتقاقي لكل مكوّن (مأخوذ من مصدره أو مُقدّر افتراضياً).\n\nلماذا هذا الترتيب مهم؟\n- لأن بعض الشيتات العليا (كالتركيب والجُمَل) تعتمد على سلامة الأعمدة المُولَّدة في الشيتات الصوتية والصرفية السابقة (الفونيمات والحركات) لضمان اتساق UTF-8 و Unicode عند إعادة الفتح أو الدمج.\n\nإضافة محرك جديد (خطوات مختصرة):\n1. أنشئ ملف engine جديد يرث من BaseReconstructionEngine ويعيد make_df() بـ DataFrame يحوي عامود "الأداة" على الأقل.\n2. استورد المحرك هنا وأضفه في القائمة المناسبة مع الحفاظ على الترتيب.\n3. شغّل هذا السكربت لإعادة توليد ملف Excel والتأكد من ظهور الشيت الجديد.\n\nملاحظة تنظيمية:\n- أي تعديل على منطق الاشتقاق أو إعادة البناء في reconstruction_utils سينعكس تلقائياً على كل الشيتات عند إعادة التوليد، ما يجعل النظام مركزياً وسهل التطوير المرحلي.\n"""
import pandas as pd
from engines.phonology.phonemes_engine import PhonemesEngine
from harakat_engine import حركات
from number_gender_suffixes_engine import التثنيةوالجمع
from brokenplural_templates_engine import BrokenPluralTemplatesEngine
from engines.syntax.demonstratives_engine import DemonstrativesEngine
from engines.syntax.istifham_engine import IstifhamEngine
from atf_engine import AtfEngine
from nafi_engine import NafiEngine
from jar_engine import JarEngine
from nasb_engine import NasbEngine
from jazm_engine import JazmEngine
from shart_engine import ShartEngine
from tawkid_engine import TawkidEngine
from nidha_engine import NidhaEngine
from engines.syntax.qasr_engine import QasrEngine
from ism_fiil_engine import IsmFiilEngine
from adad_engine import AdadEngine
from istithna_engine import IstithnaEngine
from tahdidh_engine import TahdidhEngine
from adverbs_engine import AdverbsEngine
from pronouns_engine import PronounsEngine
from verbs_engine import VerbsEngine
from nasikh_engine import NasikhEngine
from relatives_engine import RelativesEngine
from definiteness_engine import DefinitenessEngine
from engines.lexicon.generic_nouns_engine import GenericNounsEngine
from engines.lexicon.proper_nouns_engine import ProperNounsEngine
from engines.morphology.superlative_engine import SuperlativeEngine
from engines.morphology.passive_participle_engine import PassiveParticipleEngine
from engines.morphology.active_participle_engine import ActiveParticipleEngine
from engines.morphology.adjective_engine import AdjectiveEngine
from engines.morphology.mimi_nouns_engine import MimiNounsEngine
from time_engine import TimeEngine
from engines.lexicon.place_engine import PlaceEngine
from engines.phonology.sound_engine import SoundEngine
from engines.lexicon.adad_names_engine import AdadNamesEngine
from engines.lexicon.jins_jamii_engine import JinsJamiiEngine
from engines.lexicon.jins_ifradi_engine import JinsIfradiEngine
from engines.lexicon.a3lam_manqula_engine import A3lamManqulaEngine
from engines.lexicon.a3lam_amakin_engine import A3lamAmakinEngine
from engines.lexicon.a3lam_ashkhas_engine import A3lamAshkhasEngine
from engines.phonology.aswat_muhdatha_engine import AswatMuhdathaEngine
from engines.lexicon.kainat_ghair_aqila_engine import KainatGhairAqilaEngine
from engines.lexicon.kainat_aqila_engine import KainatAqilaEngine
from engines.lexicon.asma_allah_engine import AsmaAllahEngine
from engines.lexicon.asma_allah_murakkaba_engine import AsmaAllahMurakkabaEngine
from engines.lexicon.musatalahat_sharia_engine import MusatalahatShariaEngine
from engines.morphology.gender_engine import GenderEngine
from engines.morphology.ism_marra_engine import IsmMarraEngine
from engines.morphology.ism_hay_a_engine import IsmHayaaEngine
from engines.morphology.ism_ala_engine import IsmAlaEngine
from engines.syntax.tamyeez_engine import TamyeezEngine
from engines.syntax.haal_engine import HaalEngine
from engines.morphology.nisba_engine import NisbaEngine
from engines.morphology.tasgheer_engine import TasgheerEngine
from engines.rhetoric.kinaya_engine import KinayaEngine
from engines.morphology.mubalagh_sigha_engine import MubalaghSighaEngine
from engines.morphology.taajjub_engine import TaajjubEngine
from engines.syntax.jawab_engine import JawabEngine
from engines.morphology.masdar_sinai_engine import MasdarSinaiEngine
from engines.morphology.binaa_engine import BinaaEngine
from engines.syntax.mobtada_khabar_engine import MobtadaKhabarEngine
from engines.rhetoric.tashbih_engine import TashbihEngine
from engines.rhetoric.istiara_engine import IstiaraEngine
from engines.rhetoric.ishtighal_engine import IshtighalEngine
from engines.rhetoric.jinass_engine import JinassEngine
from engines.rhetoric.saja_engine import SajaEngine
from engines.rhetoric.tibaq_engine import TibaqEngine
from engines.rhetoric.muqabala_engine import MuqabalaEngine
from engines.rhetoric.ijaz_itnab_engine import IjazItnabEngine
from engines.syntax.taqdim_engine import TaqdimEngine
from engines.rhetoric.taraduf_engine import TaradufEngine
from engines.morphology.mabni_majhool_engine import MabniMajhoolEngine
from engines.syntax.fael_engine import FaelEngine
from engines.syntax.naeb_fael_engine import NaebFaelEngine
from engines.syntax.mafoul_bih_engine import MafoulBihEngine
from engines.syntax.mafoul_ajlih_engine import MafoulAjlihEngine
from engines.syntax.mafoul_mutlaq_engine import MafoulMutlaqEngine
from engines.morphology.afaal_khamsa_engine import AfaalKhamsaEngine
from engines.morphology.ism_maqsor_engine import IsmMaqsorEngine
from engines.morphology.ism_mamdod_engine import IsmMamdodEngine
from engines.morphology.ism_manqus_engine import IsmManqusEngine
from engines.morphology.common_attributes_engine import CommonAttributesEngine
from engines.generation.sentence_generation_engine import SentenceGenerationEngine

def main():
    df_phonemes = PhonemesEngine.make_df()
    df_common_attributes = CommonAttributesEngine.make_df()
    # تعديل اسم العمود من 'phonemes' إلى 'الفونيمات' في الصفات المشتركة
    if 'engine' in df_common_attributes.columns:
        df_common_attributes['engine'] = df_common_attributes['engine'].replace('phonemes', 'الفونيمات')
    # مبدئياً نكتب نسخة الحركات الكاملة (قد تحتوي أعمدة إضافية) ثم سنعيد بناء الشيت لاحقاً ليقتصر على 8 حركات أساسية.
    harakat_full_df = حركات.make_df()
    # ترتيب الشيتات: 1) الفونيمات 2) الحركات 3) الحروف/الأدوات المبنية 4) الأسماء 5) الأفعال
    dfs = {}
    # 1) الفونيمات ثم الحركات
    dfs["الفونيمات"] = df_phonemes
    dfs["الحركات"] = harakat_full_df
    # 2) المبنيات (الحروف والأدوات/الأساليب المبنية)
    for name, fn in [
        ("العطف", AtfEngine.make_df),
        ("النفي", NafiEngine.make_df),
        ("الجر", JarEngine.make_df),
        ("النصب", NasbEngine.make_df),
        ("الجزم", JazmEngine.make_df),
        ("الشرط", ShartEngine.make_df),
        ("الاستفهام", IstifhamEngine.make_df),
        ("التوكيد", TawkidEngine.make_df),
        ("النداء", NidhaEngine.make_df),
        (QasrEngine.SHEET_NAME, QasrEngine.make_df),
        (IstithnaEngine.SHEET_NAME, IstithnaEngine.make_df),
        (TahdidhEngine.SHEET_NAME, TahdidhEngine.make_df),
        (JawabEngine.SHEET_NAME, JawabEngine.make_df),
        (TaqdimEngine.SHEET_NAME, TaqdimEngine.make_df),
        (TibaqEngine.SHEET_NAME, TibaqEngine.make_df),
        (MuqabalaEngine.SHEET_NAME, MuqabalaEngine.make_df),
        (IjazItnabEngine.SHEET_NAME, IjazItnabEngine.make_df),
        (SajaEngine.SHEET_NAME, SajaEngine.make_df),
        (JinassEngine.SHEET_NAME, JinassEngine.make_df),
        (TashbihEngine.SHEET_NAME, TashbihEngine.make_df),
        (IstiaraEngine.SHEET_NAME, IstiaraEngine.make_df),
        (IshtighalEngine.SHEET_NAME, IshtighalEngine.make_df),
        (TaradufEngine.SHEET_NAME, TaradufEngine.make_df),
    ]:
        dfs[name] = fn()
    # 3) الأسماء (كل ما هو اسم/مصادر/نعوت…)
    for name, fn in [
        ("التعريف_النكرة_المعرفة", DefinitenessEngine.make_df),
        ("اسم_الإشارة", DemonstrativesEngine.make_df),
        ("الضمائر", PronounsEngine.make_df),
        ("أسماء_الأعداد", AdadNamesEngine.make_df),
        ("العدد", AdadEngine.make_df),
        ("التثنيةوالجمع", التثنيةوالجمع.make_df),
        ("جمع_التكسير", BrokenPluralTemplatesEngine.make_df),
        (SuperlativeEngine.SHEET_NAME, SuperlativeEngine.make_df),
        (PassiveParticipleEngine.SHEET_NAME, PassiveParticipleEngine.make_df),
        (ActiveParticipleEngine.SHEET_NAME, ActiveParticipleEngine.make_df),
        (AdjectiveEngine.SHEET_NAME, AdjectiveEngine.make_df),
        (MimiNounsEngine.SHEET_NAME, MimiNounsEngine.make_df),
        (IsmMarraEngine.SHEET_NAME, IsmMarraEngine.make_df),
        (IsmHayaaEngine.SHEET_NAME, IsmHayaaEngine.make_df),
        (IsmAlaEngine.SHEET_NAME, IsmAlaEngine.make_df),
        (NisbaEngine.SHEET_NAME, NisbaEngine.make_df),
        (TasgheerEngine.SHEET_NAME, TasgheerEngine.make_df),
        (MasdarSinaiEngine.SHEET_NAME, MasdarSinaiEngine.make_df),
        (KinayaEngine.SHEET_NAME, KinayaEngine.make_df),
        (MubalaghSighaEngine.SHEET_NAME, MubalaghSighaEngine.make_df),
        (HaalEngine.SHEET_NAME, HaalEngine.make_df),
        (TamyeezEngine.SHEET_NAME, TamyeezEngine.make_df),
        (GenericNounsEngine.SHEET_NAME, GenericNounsEngine.make_df),
        (ProperNounsEngine.SHEET_NAME, ProperNounsEngine.make_df),
        (PlaceEngine.SHEET_NAME, PlaceEngine.make_df),
        (SoundEngine.SHEET_NAME, SoundEngine.make_df),
        (JinsJamiiEngine.SHEET_NAME, JinsJamiiEngine.make_df),
        (JinsIfradiEngine.SHEET_NAME, JinsIfradiEngine.make_df),
        (A3lamManqulaEngine.SHEET_NAME, A3lamManqulaEngine.make_df),
        (A3lamAmakinEngine.SHEET_NAME, A3lamAmakinEngine.make_df),
        (A3lamAshkhasEngine.SHEET_NAME, A3lamAshkhasEngine.make_df),
        (KainatGhairAqilaEngine.SHEET_NAME, KainatGhairAqilaEngine.make_df),
        (KainatAqilaEngine.SHEET_NAME, KainatAqilaEngine.make_df),
        (AsmaAllahEngine.SHEET_NAME, AsmaAllahEngine.make_df),
        (AsmaAllahMurakkabaEngine.SHEET_NAME, AsmaAllahMurakkabaEngine.make_df),
        (MusatalahatShariaEngine.SHEET_NAME, MusatalahatShariaEngine.make_df),
        (GenderEngine.SHEET_NAME, GenderEngine.make_df),
        (MobtadaKhabarEngine.SHEET_NAME, MobtadaKhabarEngine.make_df),
        ("الصفات المشتركة", lambda: df_common_attributes),
        (IsmMaqsorEngine.SHEET_NAME, IsmMaqsorEngine.make_df),
        (IsmMamdodEngine.SHEET_NAME, IsmMamdodEngine.make_df),
        (IsmManqusEngine.SHEET_NAME, IsmManqusEngine.make_df),
    ]:
        dfs[name] = fn()
    # 4) الأفعال
    for name, fn in [
        ("الأفعال", VerbsEngine.make_df),
        (MabniMajhoolEngine.SHEET_NAME, MabniMajhoolEngine.make_df),
        (FaelEngine.SHEET_NAME, FaelEngine.make_df),
        (NaebFaelEngine.SHEET_NAME, NaebFaelEngine.make_df),
        (MafoulBihEngine.SHEET_NAME, MafoulBihEngine.make_df),
        (MafoulAjlihEngine.SHEET_NAME, MafoulAjlihEngine.make_df),
        (MafoulMutlaqEngine.SHEET_NAME, MafoulMutlaqEngine.make_df),
        (AfaalKhamsaEngine.SHEET_NAME, AfaalKhamsaEngine.make_df),
        (NasikhEngine.SHEET_NAME, NasikhEngine.make_df),
        (RelativesEngine.SHEET_NAME, RelativesEngine.make_df),
        (SentenceGenerationEngine.SHEET_NAME, SentenceGenerationEngine.make_df),
    ]:
        dfs[name] = fn()

    # حفظ جميع البيانات في ملف إكسل
    target_excel = "full_multilayer_grammar.xlsx"
    with pd.ExcelWriter(target_excel) as writer:
        for sheet_name, df in dfs.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"--- سامبل من شيت: {sheet_name} ---")
            print(df.head(3))
            print("------------------------------\n")

    # بعد كتابة كل الشيتات نعيد بناء شيت الحركات ليحتوي فقط 8 حركات أساسية بالأعمدة المطلوبة (الاسم، النوع، أثرها ... إلخ)
    try:
        حركات.rebuild_sheet_from_excel(src_excel=target_excel, sheet_name='الحركات')
    except Exception as e:
        print(f"[WARN] فشل إعادة بناء شيت الحركات: {e}")

# Entry point to run main when script is executed directly  
if __name__ == "__main__":
    main()

