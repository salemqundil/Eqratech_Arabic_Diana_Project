# الوضع الحالي للمشروع — Current Situation

وثيقة مختصرة تصف حالة المشروع بعد تنفيذ خطة root_resolver والـ pipeline المتصل بالقرآن.

---

## 1. الهدف العام

- **Pipeline عربي متعدد الطبقات**: C1 (ترميز/CV) → C2a (بوابات صوتية) → **C2b** (صرف: جذور، أوزان، أدوات، إعراب).
- **التطبيق العملي الحالي**: تحليل القرآن آيةً آية من `data/quran-simple-clean.txt` وتصدير CSV بكلمة/آية/سورة، مع **تحسين استخراج الجذر** عبر `root_resolver` (CLI + أوزان + مرجع جذور).
- **معيار النجاح**: root_resolver موثوق؛ التحقق عبر تحليل القرآن CSV، مع هدف أن تكون نسبة الـ heuristic أقل من 10%.

تفاصيل الأسئلة والأجوبة السابقة: [docs/ANSWERS_BEFORE_PLAN.md](ANSWERS_BEFORE_PLAN.md).

---

## 2. مراحل fvafk (الحالة الحالية)

| المرحلة | الحالة | ملاحظة |
|---------|--------|--------|
| C1 | منفذ | ترميز، تطبيع، CV (بسيط ومتقدم). |
| C2a | منفذ | بوابات صوتية (sukun, shadda, hamza, waqf, …). |
| C2b | منفذ | صرف: حدود كلمات، استخراج جذر، أوزان، أدوات، مبنيات، سمات، ISNADI. **تحسين الجذر**: `root_resolver` مدمج في السكريبت الرئيسي. |
| C2c | غير منفذ | بوابات دلالية (في الخطة فقط). |
| C3 | غير منفذ | مدلول/معنى (في الخطة فقط). |

---

## 3. root_resolver — المكونات والبيانات

### 3.1 البنية

```
src/fvafk/c2b/root_resolver/
├── __init__.py          # تصدير: RootsDB, resolve_root, evaluate, load_csv, print_report
├── roots_db.py          # قراءة data/arabic_roots.csv، is_valid_root، to_hyphen_form
├── wazn_matcher.py      # منطق المطابقة (Unit, split_units, try_match, best_hit, get_fal_indices)
├── wazn_adapter.py      # match_wazn، extract_root_from_wazn (ف/ع/ل من النافذة)
├── heuristic.py         # Fallback: تجريد بادئات/لواحق، consonantal root، ثقة منخفضة
├── resolver.py          # resolve_root: استراتيجية B (cli_verified → wazn_resolved → heuristic)
├── evaluator.py         # مقارنة CSV مخرجات vs gold، Accuracy و per-source
└── coordinating_conjunctions.py   # كود قديم (بوابة أوزان كاملة + main)
```

### 3.2 البيانات

| الملف | الاستخدام |
|-------|-----------|
| `data/arabic_roots.csv` | قائمة جذور مرجعية (~5183)، عمود واحد `root` (بدون شرطة). يُستخدم في `RootsDB` للتحقق من صحة الجذر. |
| `data/awzan_merged_final.csv` | أوزان للمطابقة (عمود الوزن). يُحمَّل في السكريبت ويمرَّر إلى `resolve_root` كـ `patterns`. |

### 3.3 استراتيجية الحل (B-strategy)

1. **cli_verified**: إذا كان الجذر من الـ CLI موجوداً في `roots_db` والكلمة ليست أداة (operator/particle/demonstrative) → نعتمده بثقة عالية.
2. **wazn_resolved**: مطابقة الوزن على الكلمة، استخراج ف/ع/ل من النافذة؛ إذا كان الجذر المستخرج في `roots_db` → نعتمده.
3. **heuristic**: Fallback (تجريد بادئات/لواحق شائعة، consonantal root) بثقة منخفضة.

---

## 4. التكامل مع الـ Pipeline

- **السكريبت الرئيسي**: `scripts/run_ayat_al_dayn_with_wazn_and_operators.py`
  - الإدخال: `--input` (افتراضي `data/quran-simple-clean.txt`)، أسطر بصيغة `sura|aya|text`.
  - يتم تحميل `RootsDB()` و `patterns` من `data/awzan_merged_final.csv`.
  - لكل كلمة: بعد حساب `stripped` و `kind` يُستدعى `resolve_root(word, stripped, cli_root, kind, patterns, roots_db, show_source=args.show_root_source)` ويُستخدم `resolved["root"]` كـ `root_str` في الصف.
  - **علم اختياري**: `--show-root-source` يملأ أعمدة: `root_source`, `root_wazn`, `root_confidence` في الـ CSV.

- **تشغيل من جذر المشروع**:
  ```bash
  PYTHONPATH=src python3 scripts/run_ayat_al_dayn_with_wazn_and_operators.py --input data/quran-simple-clean.txt --output out.csv
  ```
  مع تتبع المصدر:
  ```bash
  PYTHONPATH=src python3 scripts/run_ayat_al_dayn_with_wazn_and_operators.py --show-root-source --output out.csv
  ```

---

## 5. التقييم (evaluator)

- **الملف**: `src/fvafk/c2b/root_resolver/evaluator.py`
- **الوظائف**: `load_csv`, `align_rows` (حسب `word`), `evaluate` (دقة إجمالية + per-source), `print_report`.
- **استخدام من سطر الأوامر**:
  ```bash
  python -m fvafk.c2b.root_resolver.evaluator <pred_csv> <gold_csv> [--root-col root] [--source-col root_source]
  ```
- **المطلوب للتقييم الرسمي**: CSV مخرجات السكريبت (مع `--show-root-source`) + ملف gold (مثلاً آية الدَّيْن مُصحَّحة يدوياً) له نفس أعمدة `word` و `root` على الأقل.

---

## 6. الاختبارات (pytest)

- **الإعداد**: `pytest.ini` يحدد `testpaths = tests` و `pythonpath = src .`.
- **ملاحظة**: يجب تشغيل pytest **من جذر المشروع** حتى يُكتشَف مجلد `tests/`:
  ```bash
  cd /path/to/Eqratech_Hussein_Hiyassat_Project
  pytest -q
  ```
  من مجلد فرعي (مثل `src/`) بدون تمرير المسار يعطي "collected 0 items".

- **حالة الاختبارات**: توجد عشرات الملفات تحت `tests/` (مثل `tests/c2b/test_root_extractor.py`). لا توجد حالياً وحدة اختبار مخصصة لـ `root_resolver` (roots_db، wazn_adapter، resolver، evaluator)؛ يمكن إضافتها لاحقاً.

---

## 7. ما تم تنفيذه وما بقي

| البند | الحالة |
|-------|--------|
| root_resolver (roots_db, wazn_matcher, wazn_adapter, heuristic, resolver) | منفذ ومدمج في السكريبت |
| أعمدة root_source / root_wazn / root_confidence في CSV | منفذ (عند استخدام --show-root-source) |
| evaluator (Accuracy، per-source، تقرير) | منفذ؛ جاهز للاستخدام مع gold CSV |
| تشغيل على آية الدَّيْن ثم البقرة ثم القرآن كاملاً | يُجرى يدوياً؛ لم يُنفَّذ كجزء من الكود |
| gold set لآية الدَّيْن (تصحيح يدوي) | غير موجود في المستودع؛ مطلوب للتقييم الرسمي |
| وحدة اختبارات لـ root_resolver | غير مضافة |
| هدف heuristic &lt; 10% | يُقاس بعد تشغيل القرآن كاملاً وإحصاء المصادر |

---

## 8. البيانات اللغوية (linguistic_data)

- **المصدر**: `data/linguistic/` — ملفات CSV و JSON (ثوابت صوتية، قوائم صرفية، مركبات خاصة، أوزان، تطبيق وسوم).
- **الاستخدام**: `from fvafk.linguistic_data import IMPERFECT_CHARS, NOUN_EXCEPTIONS, SPECIAL_COMPOUNDS, ...`
- **توافق السيجمنتر**: مع `PYTHONPATH=src` يمكن استيراد نفس الأسماء من `linguistic_data`: `from linguistic_data import ...` (الملف `src/linguistic_data.py` يعيد التصدير من `fvafk.linguistic_data`).

---

## 9. مراجع سريعة

- أسئلة وأجوبة قبل الخطة: [docs/ANSWERS_BEFORE_PLAN.md](ANSWERS_BEFORE_PLAN.md)
- قاعدة القواعد فقط (بدون معرفة خارجية): [docs/RULE_BASED.md](RULE_BASED.md)
- مخرجات المشروع وتوصيف C2b: [project_deleverables.md](../project_deleverables.md) / [docs/project_deleverables.md](project_deleverables.md)
- القواعد والبيانات فقط: [RULE_BASED.md](RULE_BASED.md) (يتضمن مصدر البيانات اللغوية).
