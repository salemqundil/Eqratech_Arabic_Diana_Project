# project_deleverables

وثيقة حيّة لمتابعة **تقدّم مشروع FVAFK** ومخرجاته (Deliverables) حسب خطة: `🎯 خطة شاملة لبناء المحركات اللغوية الحقيقية.md`.

> تحديث هذه الوثيقة يتم **باستمرار** كلما أُضيفت ميزة/اختبار/بيانات أو تغيّر سلوك الـ CLI.

---

## 1) تعريف سريع
- **الهدف**: بناء Pipeline عربي: C1 (ترميز/تطبيع + CV) → C2a (بوابات صوتية) → C2b (صرف: جذور/زوائد/أوزان/تصنيف أدوات) → (لاحقًا) نحو/دلالة/معنى.
- **واجهة الاستخدام الأساسية الآن**: `src/fvafk/cli/main.py` عبر:
  - `python -m fvafk.cli "نص" --json`
  - `python -m fvafk.cli "نص" --morphology --json`

---

## 2) خط الأساس الحالي (Baseline Snapshot)
- **الاختبارات**: `pytest` ✅ **229 passed** (آخر تحقق: 2026-02-05).
- **مخرجات CV في CLI**: `c1.cv_analysis.words` تحتوي فقط:
  - `cv`
  - `cv_advanced`
- **تحليل morphology متعدد الكلمات**: تلقائيًا عند وجود أكثر من token عربي (Plan A: `WordBoundaryDetector` مع spans) داخل `--morphology`.
- **تصنيف الأدوات/الحروف**: يتم قبل الجذر/الوزن، ويُرجع `kind: "operator"` مع metadata.

---

## 3) Deliverables حسب المراحل (من الخطة)

### المرحلة 1: البنية التحتية (C1)
**موجود/مسلّم**
- `src/fvafk/c1/segment_inventory.py`  
  - جرد الصوامت + سمات صوتية (على نمط الخطة).
- `src/fvafk/orthography_adapter.py`  
  - تطبيع كتابي مبسط (همزات/ألف وصل/تنوين/حركات).
- `src/fvafk/c1/encoder.py`  
  - `C1Encoder.encode(text) -> List[Segment]` (صامت/صائت).
- `src/fvafk/c1/form_codec_v2.py`
  - `FormCodecV2.encode/decode` تمثيل شكلي **عكوسي** (NFC) + tokens مع spans + checksum.
- `src/fvafk/c1/trace_v1.py`
  - Trace V1: `TraceStep` + diff tokens + `replay()` بسجل بوابات حتمية (بدون Coq حاليًا).
- `src/fvafk/c1/cv_pattern.py`
  - CV بسيط + CV متقدم (haraka-aware) + تسوية المد (VaVa→VA…).

**فجوات مقارنة بالخطة**
- لا توجد بعدُ **مبرهنات Coq** وقيود عكوسية رسمية كما في الخطة، لكن codec/trace أصبحا جاهزين للتثبيت لاحقًا.

---

### المرحلة 2: البوابات الصوتية (C2a)
**موجود/مسلّم**
- `src/fvafk/c2a/gate_framework.py`  
  - GateResult + orchestrator لتسلسل البوابات.
- `src/fvafk/c2a/syllable.py`  
  - `Segment` + `SyllableType`… (أساس).
- `src/fvafk/c2a/gates/*`
  - بوابات مثل: sukun/shadda/hamza/waqf/idgham/madd/tanwin/assimilation/deletion/epenthesis.

**ملاحظات**
- إطار C2a هنا أخف من “Gate framework” في الخطة (بدون epistemic state/constraints الثقيلة).

---

### المرحلة 3: الصرف (C2b)
**موجود/مسلّم**
- **Word boundaries (Plan A)**
  - `src/fvafk/c2b/word_boundary.py`
  - استخراج tokens من النص مع `start/end` spans (مع hook لخيار Plan B لاحقًا).
- **Root extraction + hamza normalization + affix tracking**
  - `src/fvafk/c2b/root_extractor.py`
  - `RootExtractionResult` يعيد: `root`, `normalized_word`, `stripped_word`, `prefix`, `suffix`.
- **Pattern matching + تحميل قاعدة أوزان خارجية**
  - `src/fvafk/c2b/pattern_matcher.py`
  - `src/fvafk/c2b/awzan_loader.py` يقرأ `data/awzan_merged_final.csv` (مع fallback إلى `awzan-claude-atwah.csv`) ويضيف قوالب.
  - مطابقة CV المتقدم (إذا توفر في القالب) + `confidence`.
- **PatternAnalyzer (طبقة مستقلة)**
  - `src/fvafk/c2b/pattern_analyzer.py` (واجهة ثابتة فوق `PatternMatcher`)
- **WordClassifier (طبقة مستقلة)**
  - `src/fvafk/c2b/word_classifier.py` (operator/pronoun/verb/noun)
- **Feature extraction (V1)**
  - `src/fvafk/c2b/features.py` (definiteness/number/gender/case + pronouns/clitics)
- **Operators/Particles classification (closed class)**
  - `src/fvafk/c2b/operators_catalog.py`
  - يدعم stripping diacritics + peeling prefixes + compound matching.

**بيانات مرتبطة**
- `data/awzan_merged_final.csv` (مصدر الأوزان الحالي)
- `awzan-claude-atwah.csv` (مصدر قديم/احتياطي)
- `operators_catalog_split.csv` (مصدر الأدوات/الحروف؛ يُبحث عنه عبر env/مسارات افتراضية)

**فجوات مقارنة بالخطة**
- Word boundary من **المقاطع/stream** كما في الخطة (Plan B): **غير منفذ** (الموجود الآن Plan A من النص مع spans).
- PatternAnalyzer/WordClassifier **موجودان** لكنهما ليسا مبنيين على syllables/قيود C2a كما في الخطة.
- **السمات العميقة** (إعراب دقيق/زمن/شخص للفعل/اتساق نحوي…) ما زالت **غير مكتملة** (الموجود الآن V1 heuristics فقط).

---

### المرحلة 4: النحو (C2b Syntax) + الروابط الثلاثية
**موجود/مسلّم (أساس بنيوي)**
- `src/fvafk/node_schema.py`  
  - Node schema + case/mood/join + RelationType.
- `src/fvafk/energy_evaluation.py`
  - Infinity gates / energy evaluation لتصفية المرشحين.

**غير مكتمل**
- parser/linkers (ISNADI/TADMINI/TAQYIDI) على مستوى الجملة + validator قيود الخطة.
- ربط مخرجات C2b الحالية (root/pattern/operator) مباشرة إلى Node candidates.

---

### المرحلة 5: C2c (Semantic Gate) + المرحلة 6: Meaning + Corpus Evaluation
**غير منفذ**
- لا يوجد TraceC2 فعلي ولا corpus scoring/F1 كما في الخطة.

---

## 4) نقاط محورية تم حلّها (Key Fixes Done)
- **Hamza normalization للجذور** في `root_extractor.py`.
- **الزوائد**: إرجاع prefix/suffix صراحة في `RootExtractionResult`.
- **CV advanced**: تسوية المد (VaVa→VA, ViVi→VI, VoVo→VO) + تقليل خرج CLI إلى `cv` و`cv_advanced`.
- **تصنيف الأدوات/الحروف**: short-circuit قبل الصرف داخل CLI.
- **حدود كلمات Plan A**: استخراج tokens مع spans وتصفية العلامات غير الحرفية.
- **تصنيف مبدئي للكلمات**: operator/pronoun/verb/noun + ميزات V1 (definiteness/number/gender/case + clitics).
- **إصلاح اختبارات المشروع**: توحيد استيراد `fvafk.*` داخل الاختبارات + تحديث mapping للوزن `فُعُل`.

---

## 5) القائمة الحالية: ما اكتمل / ما هو التالي

### ✅ مكتمل الآن
- Pipeline عملي عبر CLI (C1→C2a→C2b).
- CV analysis minimal output.
- Word boundaries (Plan A) + spans.
- Root extraction مع حالات همزة/شدة/زوائد.
- Pattern matcher مع قاعدة بيانات awzan.
- PatternAnalyzer + WordClassifier layers (Plan A).
- Feature extraction V1 داخل `c2b.features`.
- Operators classification من CSV.
- C1: `FormCodecV2` + `Trace V1` (replayable trace).
- اختبارات شاملة تمر (228).

### ⏳ التالي (أعلى أولوية حسب الخطة)
- **اشتقاق سمات صرفية/نحوية** من الوزن والزوائد (مثل: number/gender/case، وضمائر مثل `هُمْ`).
- توحيد طبقة “تصنيف الكلمة” (noun/verb/particle/pronoun) بدل الاقتصار على operators فقط.
- تجهيز “WordForm” وسيط يربط: token → (operator|root|pattern|features) لاستخدامه في المرحلة النحوية.

### 📌 لاحقًا
- بناء روابط ISNADI/TADMINI/TAQYIDI وربطها بـ node_schema/energy_evaluation.
- Semantic gate + meaning + corpus tests.

---

## 6) سجل التحديثات (Changelog)

### 2026-02-05
- إضافة أوزان جمع تكسير عالية التأثير:
  - `فُعَّل` → `BROKEN_PLURAL_FU33AL` (مثل: رُكَّع، سُجَّد)
  - `فُعَلَاء/فُعَلَاءُ` → `BROKEN_PLURAL_FU3ALAA` (مثل: رُحَمَاء)
- تحسينات قبل CV fallback في CLI لإصلاح أوزان قرآنية شائعة:
  - `يَبْتَغُونَ` يُعامل كـ Form VIII (افتعل) ويُرجّع قالب `يَفْتَعِلُونَ`.
- حماية جذور جمع (…اء) من إدخال الهمزة كحرف جذر:
  - `أَشِدَّاءُ`: `ش-د-ء` → `ش-د-د` + وسم الوزن كـ `فُعَلَاءُ`.
- مزامنة `pattern.category` مع `kind` (verb/noun) لتقليل عدم الاتساق في الخرج.
- تأكيد: `pytest` ✅ 229 passed.

### 2026-02-04
- إنشاء وثيقة `project_deleverables.md` كوثيقة حيّة للتقدم.
- إصلاح استيرادات بعض الاختبارات من `src.fvafk` إلى `fvafk` لتعمل مع `pytest.ini (pythonpath=src)`.
- إصلاح mapping وزن `فُعُل` ليصنف كـ `BROKEN_PLURAL_FUUL`.
- إضافة Plan A لـ C2b:
  - `word_boundary.py` (tokens+spans + hook لخيار Plan B)
  - `pattern_analyzer.py`, `word_classifier.py`, `features.py`
  - اختبارات جديدة لـ boundaries/classifier/features
- تحسينات كبيرة على segmentation/POS/CV بعد مراجعات `out.txt` (آية سورة الفتح 29):
  - تصحيح `kind` لأفعال صعبة مثل: `فَآزَرَهُ`, `فَاسْتَغْلَظَ`, `فَاسْتَوَىٰ`.
  - إصلاح clitic `وَ/فَ` بحيث ينفصل في مثل `وَعَمِلُوا` (prefix=و، stripped=عمل).
  - منع تفكيك `وُجُوهِهِم` إلى `ه+هم` (صار suffix=هم، stripped=وجوه).
  - كسر تجمعات CCC التي كانت تظهر في CV (إزالة `CCC` من `c1.cv_analysis` لنفس الآية).
- إضافة C1 الرسمي (Plan-aligned):
  - `FormCodecV2` (reversible encode/decode)
  - `Trace V1` (TraceStep + replay + token diffs)
- تأكيد: `pytest` ✅ 225 passed.

