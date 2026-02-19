# Phonology Layer (C2a)

طبقة الصوتيات في خط أنابيب FVAFK. تحتوي على بوابات (gates) قابلة للتدقيق والتتبع.

---

## Gate Order

الترتيب الحالي لتنفيذ البوابات:

1. **Sukun** — إصلاح تتابع السكون (double sukun)
2. **Shadda** — معالجة الشدة (gemination)
3. **Tanwin** — تطبيع التنوين
4. **Hamza** — قواعد الهمزة
5. **Wasl** — همزة الوصل
6. **Waqf** — أوضاع الوقف
7. **Idgham** — الإدغام
8. **Madd** — المد
9. **Assimilation** — الاستيعاب
10. **Deletion** — الحذف
11. **Epenthesis** — الإدراج

---

## GateResult (Canonical)

كل بوابة تُرجع بنية موحّدة:

| Field | Type | Description |
|-------|------|-------------|
| `status` | GateStatus | ACCEPT \| REPAIR \| REJECT |
| `input_units` | list | الوحدات الداخلة |
| `output_units` | list | الوحدات الخارجة |
| `delta` | GateDelta | التغييرات (changed, added, removed, notes) |
| `time_ms` | float | زمن التنفيذ بالميلي ثانية |
| `notes` | list[str] | ملاحظات (سبب الإصلاح أو الرفض) |

---

## Invariants (Property Tests)

يجب أن تحافظ البوابات على:

- **Non-empty output** — المخرجات لا تكون فارغة.
- **Consonant order preserved** — ترتيب الصوامت لا يتغير.
- **No CCC clusters** — لا يظهر ثلاثة صوامت متتالية بدون حركة.
- **No haraka without trigger** — لا تُنشأ حركة بدون سبب (إصلاح أو قاعدة).

---

## Adding a New Gate

1. إنشاء ملف في `src/fvafk/c2a/gates/gate_<name>.py`.
2. وراثة `BaseGate` (أو `PhonologicalGate`) وتعيين `gate_id`.
3. تنفيذ `apply(self, segments) -> GateResult`.
4. استخدام `self._result(...)` لبناء النتيجة.
5. إضافة البوابة إلى قائمة البوابات في الـ orchestrator.
6. إضافة اختبارات في `tests/test_gate_<name>.py` واختياريًا في `tests/test_gate_properties.py`.

---

## Trace

لتشغيل التتبع الصوتي:

- استيراد `PhonologyTrace` و `PhonologyTraceStep` من `fvafk.c2a.phonology_trace`.
- إنشاء `PhonologyTrace(input_text="...", output_text="...")`.
- استدعاء `orchestrator.run_with_trace(segments, trace)` بدل `run`.
- استخدام `trace.to_dict()` أو `trace.to_json()` أو `trace.format_summary()` للمخرجات.

الـ CLI يدعم خيار التتبع عند تفعيله (مثلاً `--trace` عند إضافته).

---

## Coq Skeletons

هياكل Coq للتحقق الرسمي (Sprint 2):

- `coq/Gates/GateSukun.v`
- `coq/Gates/GateShadda.v`
- `coq/Gates/GateTanwin.v`

كل ملف يحتوي على `Parameter` للبوابة و `Lemma ... Admitted.` للخصائص. التجميع: من جذر المستودع `coqc coq/Gates/GateSukun.v` (أو استخدام `_CoqProject`).
