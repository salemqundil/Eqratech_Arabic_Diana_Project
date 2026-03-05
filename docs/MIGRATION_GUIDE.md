## MIGRATION GUIDE — الانتقال إلى Phonology V2

هذا الدليل يشرح **كيف تستخدم Phonology V2** داخل مشروع FVAFK، وما الذي تغيّر في الـCLI وواجهات الـPython.

### 1) ما هو Phonology V2؟
- **Phonology V1 / C2a**: يعتمد على بوابات (Tajweed-like gates) تعمل على تسلسل `Segment`s.
- **Phonology V2**: محرك تقطيع مقطعي (Syllable lattice) ينتج:
  - `cv_pattern` (مثل `CVCVVC`)
  - `syllabification` (مثل `كِ.تاب (CV.CVVC)`)
  - **witnesses** (اختياري): “شهود” تشرح لماذا اعتُبرت بعض الحروف صوائت/صوامت (خصوصًا ا/و/ي).

الملفات الأساسية موجودة هنا: `src/fvafk/phonology_v2/`.

---

### 2) CLI: كيف أفعّل Phonology V2؟

#### 2.1 تفعيل Phonology V2 لِـ CV analysis

```bash
PYTHONPATH=src python -m fvafk.cli "كِتَاب" --json --phonology-v2
```

ستلاحظ أن `c1.cv_analysis.engine` تصبح `phonology_v2`.

#### 2.2 إظهار تفاصيل التقطيع المقطعي (syllabification)

```bash
PYTHONPATH=src python -m fvafk.cli "كِتَاب" --json --phonology-v2 --phonology-v2-details
```

ستظهر النتائج تحت:
- `c2a.phonology_v2.words[]`

#### 2.3 تفعيل witnesses (شهود القرارات)

> ملاحظة مهمة: **الشهود تظهر فقط مع `--phonology-v2-details`**.

```bash
PYTHONPATH=src python -m fvafk.cli "كِتَاب" --json --phonology-v2 --phonology-v2-details --phonology-v2-witnesses
```

ستجد `witnesses` كقائمة عناصر، مثل:
- `grapheme`: الحرف (مثلاً `ا`)
- `role`: الدور (`C`, `V_SHORT`, `V_LONG`, …)
- `witness`: سبب القرار (مثل `LONG_BY_NUCLEUS_NEED`)
- `need_nucleus` / `force_onset_c`: إشارات سياقية داخل المصنّف

---

### 3) Python API: كيف أستخدم المحول (Adapter)؟

Phonology V2 مصمّم ليكون “drop-in” عبر `PhonologyV2Adapter`:

```python
from fvafk.phonology_v2.phonology_adapter import PhonologyV2Adapter

adapter = PhonologyV2Adapter()
r = adapter.analyze_word("كِتَاب")

assert r["success"] is True
print(r["cv_pattern"])        # CVCVVC
print(r["syllabification"])   # كِ.تاب (CV.CVVC)
print(r.get("witnesses", [])) # قد تكون موجودة حسب إعدادات الـadapter/التصدير
```

**ملاحظة**: الـCLI هو الذي يقرر تضمين `witnesses` في JSON عند تفعيل `--phonology-v2-witnesses`.

---

### 4) اختلافات مهمة عن V1

- **إخراج CV**:
  - ما زال يظهر تحت `c1.cv_analysis.words[]`، لكن `engine` قد تكون `phonology_v2`.
- **التفاصيل**:
  - التفاصيل الموسعة (التقطيع/الشهود) تُضاف في `c2a.phonology_v2` فقط عندما تفعل `--phonology-v2-details`.
- **الاسماء المستبعدة**:
  - الـCLI قد يستبعد أسماء/رموز معينة من التحليل (حسب `should_exclude` + special catalog)؛ هذا يظهر في `excluded_names`.

---

### 5) اختبار سريع للتأكد (Regression)

يوجد اختبار يضمن أن witnesses لم تعد فارغة:
- `tests/test_phonology_v2_witnesses.py`

تشغيله:

```bash
PYTHONPATH=src pytest -q tests/test_phonology_v2_witnesses.py
```

