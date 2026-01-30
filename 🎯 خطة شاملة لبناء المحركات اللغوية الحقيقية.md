---
title: خطة شاملة لبناء المحركات اللغوية الحقيقية
---
🎯 خطة شاملة لبناء المحركات اللغوية الحقيقية
📋 جدول المحتويات
تحليل الوضع الحالي
الأهداف المحددة
المنهجية والمعايير
الخطة التفصيلية
جدول التنفيذ

<a name="analysis"></a>
1️⃣ تحليل الوضع الحالي
✅ ما لدينا (من Main Branch):
YAML
النواة الأساسية:
  - FormCodecV2: ✅ عكوسية كاملة مع checksum
  - Trace System: ✅ نظام تتبع بالبوابات
  - Dictionary v02: ✅ قاموس YAML شامل
  - 3 مبرهنات: ✅ T_CODEC_REVERSIBLE, T_NO_C3_WITHOUT_C2, C1_IMMUTABILITY
  - 2 invariants: ✅ inv_double_sukun, inv_wasl_begin
  
الإثبات الرسمي (Coq):
  - Phases 1-3: ✅ مكتملة (109 اختبارات تمر)
  - 18 مبرهنة: ✅ معظمها مُثبت
  - OCaml Extraction: ✅ عامل
  - Python Bridge: ✅ متكامل

التوثيق:
  - COMPREHENSIVE_EVALUATION.md: ✅ 24,000+ كلمة
  - ENCODER_DECODER_PLAN.md: ✅ 15,000+ كلمة
  - FRACTAL_ENGINE_PLAN.md: ✅ 20,000+ كلمة
  - FRACTAL_SCIENTIFIC_ANALYSIS.md: ✅ 33,000+ حرف
❌ ما ينقصنا (يحتاج بناء):
YAML
البوابات الصوتية (10):
  ❌ GateSukun: فحص السكون وقيوده
  ❌ GateAssimilation: الإدغام الصوتي
  ❌ GateIdgham: إدغام التجويد
  ❌ GateDeletion: حذف الصوامت/الصوائت
  ❌ GateEpenthesis: إقحام أصوات
  ❌ GateHamza: قواعد الهمزة
  ❌ GateMadd: المد والتطويل
  ❌ GateWaqf: الوقف والابتداء
  ❌ GateTanwin: التنوين
  ❌ GateShadda: الشدة والتضعيف

المحلل الصرفي:
  ❌ تحديد حدود الكلمات (Word Boundary Detection)
  ❌ تحليل الأوزان (Pattern Analysis): فَعَل، فاعِل، مفعول...
  ❌ تصنيف نوع الكلمة (Word Kind): اسم/فعل/حرف
  ❌ تحليل الإعراب (I3rab): مبني/معرب
  ❌ استخراج الجذور (Root Extraction)
  ❌ تحديد الزوائد (Affix Identification)
  ❌ السمات الصرفية (Morphological Features): جنس/عدد/تعريف/حالة

المحلل النحوي:
  ❌ تحليل ترتيب VSO (Verb-Subject-Object)
  ❌ بناء الروابط الإسنادية (ISNADI): فعل→فاعل، مبتدأ→خبر
  ❌ بناء الروابط التضمينية (TADMINI): فعل متعدٍ→مفعول
  ❌ بناء الروابط التقييدية (TAQYIDI): اسم→نعت مع التطابق

القيود النحوية (5):
  ❌ لا فعل بلا فاعل (Verb-Subject)
  ❌ لا متعدٍ بلا مفعول (Transitive-Object)
  ❌ تطابق النعت والمنعوت (Adjective-Noun Agreement)
  ❌ السببية تتطلب أحداثاً (Causality-Events)
  ❌ المبني للمجهول يتطلب تغيير صيغة (Passive-Voice)

مكونات إضافية:
  ❌ استخراج الأحداث (Event Extraction)
  ❌ جرد 30 صامتاً (Consonant Inventory)
  ❌ إطار تحويل الإملاء (Orthography Framework)
  ❌ معالجة end-to-end (Full Pipeline)

<a name="goals"></a>
2️⃣ الأهداف المحددة (SMART Goals)
🎯 الهدف الرئيسي:
Code
بناء محركات لغوية عربية كاملة ومتكاملة مع الإثبات الرسمي في Coq،
مع معايير صناعية وأكاديمية عالية.
📊 أهداف قابلة للقياس:
المكون
الهدف القابل للقياس
معيار النجاح
البوابات الصوتية
10 بوابات مع منطق كامل
100+ اختبار يمر، تغطية 90%+
المحلل الصرفي
دقة 85%+ على corpus تجريبي
F1-score ≥ 0.85
المحلل النحوي
دقة 80%+ على تحليل الجمل
UAS ≥ 0.80
القيود النحوية
5 قيود مُطبقة بالكامل
0 violations على نصوص صحيحة
إثباتات Coq
50+ مبرهنة جديدة
100% مُثبتة (Qed)
الاختبارات
300+ اختبار شامل
95%+ نسبة نجاح
الأداء
معالجة 1000 كلمة/ثانية
<1ms لكل كلمة
التوثيق
50,000+ كلمة
تغطية 100%


<a name="methodology"></a>
3️⃣ المنهجية والمعايير
🏗️ المعايير المعمارية:
YAML
مبدأ الفصل الصارم (Strict Separation):
  C1: Signifier (الدال)
    - أشكال لغوية فقط
    - لا دلالات
    - عكوسية 100%
    
  C2: Processing (المعالجة)
    C2a: البوابات الصوتية
      - Segments → Syllables
      - قيود صوتية
    C2b: البوابات الصرفية-النحوية
      - Syllables → WordForms
      - الأوزان والروابط
    C2c: البوابات الدلالية
      - Accept/Reject decision
      - Evidence + Reality Link
      
  C3: Signified (المدلول)
    - معانٍ فقط
    - لا يُنتج بدون C2
    - Trace إلزامي

القاعدة الذهبية:
  - لا C3 بدون C2 صالح
  - لا C2 بدون C1 محفوظ
  - كل قرار له Epistemic State
🔬 المعايير الأكاديمية:
YAML
الإثبات الرسمي:
  - كل بوابة: مبرهنة Coq مطابقة
  - كل قيد: predicate قابل للإثبات
  - كل تحويل: عكوسية/preservation مُثبتة
  
الدقة اللغوية:
  - استناد لكتب النحو التقليدية (سيبويه، ابن عقيل...)
  - مقارنة مع اللسانيات الحديثة (McCarthy, Beesley...)
  - تغطية كل حالات الشذوذ
  
القياس الكمي:
  - Precision, Recall, F1-score
  - Confusion matrices
  - Corpus testing (Quran, Hadith, MSA)
🏭 المعايير الصناعية:
YAML
جودة الكود:
  - Type safety: mypy --strict
  - Test coverage: ≥90%
  - Documentation: docstrings كاملة
  - CI/CD: GitHub Actions
  
الأداء:
  - Profiling: cProfile, memory_profiler
  - Optimization: Cython للعمليات الحرجة
  - Caching: LRU caches للنتائج
  - Benchmarking: pytest-benchmark
  
التوافق:
  - Python 3.10+
  - Backward compatibility
  - Semantic versioning
  - API stability

<a name="plan"></a>
4️⃣ الخطة التفصيلية (6 مراحل)

📦 المرحلة 1: البنية التحتية (Week 1-2)
الهدف:
Code
بناء الأساس المعماري للمحركات اللغوية
المهام:
1.1 توسيع جرد الأصوات (Segment Inventory)
Python
# ملف: src/fvafk/c1/segment_inventory.py

@dataclass(frozen=True)
class ConsonantInventory:
    """30 صامتاً عربياً مع السمات الصوتية"""
    
    CONSONANTS = {
        # الشفوية (Labial)
        'ب': {'cid': 1, 'manner': 'stop', 'place': 'bilabial', 'voice': 'voiced'},
        'م': {'cid': 2, 'manner': 'nasal', 'place': 'bilabial', 'voice': 'voiced'},
        'ف': {'cid': 3, 'manner': 'fricative', 'place': 'labiodental', 'voice': 'voiceless'},
        'و': {'cid': 4, 'manner': 'approximant', 'place': 'labial-velar', 'voice': 'voiced'},
        
        # اللثوية (Dental/Alveolar)
        'ت': {'cid': 5, 'manner': 'stop', 'place': 'dental', 'voice': 'voiceless'},
        'د': {'cid': 6, 'manner': 'stop', 'place': 'dental', 'voice': 'voiced'},
        'ط': {'cid': 7, 'manner': 'stop', 'place': 'dental', 'voice': 'voiceless', 'emphatic': True},
        'ض': {'cid': 8, 'manner': 'stop', 'place': 'dental', 'voice': 'voiced', 'emphatic': True},
        'ث': {'cid': 9, 'manner': 'fricative', 'place': 'dental', 'voice': 'voiceless'},
        'ذ': {'cid': 10, 'manner': 'fricative', 'place': 'dental', 'voice': 'voiced'},
        'ظ': {'cid': 11, 'manner': 'fricative', 'place': 'dental', 'voice': 'voiced', 'emphatic': True},
        'ن': {'cid': 12, 'manner': 'nasal', 'place': 'alveolar', 'voice': 'voiced'},
        'ل': {'cid': 13, 'manner': 'lateral', 'place': 'alveolar', 'voice': 'voiced'},
        'ر': {'cid': 14, 'manner': 'trill', 'place': 'alveolar', 'voice': 'voiced'},
        
        # اللثوية الغارية (Post-alveolar)
        'س': {'cid': 15, 'manner': 'fricative', 'place': 'alveolar', 'voice': 'voiceless'},
        'ز': {'cid': 16, 'manner': 'fricative', 'place': 'alveolar', 'voice': 'voiced'},
        'ص': {'cid': 17, 'manner': 'fricative', 'place': 'alveolar', 'voice': 'voiceless', 'emphatic': True},
        'ش': {'cid': 18, 'manner': 'fricative', 'place': 'post-alveolar', 'voice': 'voiceless'},
        'ج': {'cid': 19, 'manner': 'affricate', 'place': 'post-alveolar', 'voice': 'voiced'},
        
        # الغارية (Palatal)
        'ي': {'cid': 20, 'manner': 'approximant', 'place': 'palatal', 'voice': 'voiced'},
        
        # الطبقية (Velar)
        'ك': {'cid': 21, 'manner': 'stop', 'place': 'velar', 'voice': 'voiceless'},
        'غ': {'cid': 22, 'manner': 'fricative', 'place': 'velar', 'voice': 'voiced'},
        'خ': {'cid': 23, 'manner': 'fricative', 'place': 'velar', 'voice': 'voiceless'},
        
        # اللهوية (Uvular)
        'ق': {'cid': 24, 'manner': 'stop', 'place': 'uvular', 'voice': 'voiceless'},
        
        # الحلقية (Pharyngeal)
        'ح': {'cid': 25, 'manner': 'fricative', 'place': 'pharyngeal', 'voice': 'voiceless'},
        'ع': {'cid': 26, 'manner': 'fricative', 'place': 'pharyngeal', 'voice': 'voiced'},
        
        # الحنجرية (Glottal)
        'ء': {'cid': 27, 'manner': 'stop', 'place': 'glottal', 'voice': 'voiceless'},
        'ه': {'cid': 28, 'manner': 'fricative', 'place': 'glottal', 'voice': 'voiceless'},
        
        # الحروف الإضافية
        'ة': {'cid': 29, 'manner': 'marker', 'place': 'none', 'voice': 'none'},  # تاء مربوطة
        'ى': {'cid': 30, 'manner': 'marker', 'place': 'none', 'voice': 'none'},  # ألف مقصورة
    }
    
    @classmethod
    def get_features(cls, consonant: str) -> FrozenSet[str]:
        """استخراج السمات الصوتية كـ frozenset"""
        info = cls.CONSONANTS.get(consonant, {})
        features = set()
        for key, value in info.items():
            if key != 'cid':
                if isinstance(value, bool) and value:
                    features.add(key)
                elif isinstance(value, str):
                    features.add(f"{key}:{value}")
        return frozenset(features)
1.2 نظام المقاطع (Syllable System)
Python
# ملف: src/fvafk/c2a/syllable.py

from enum import Enum, auto
from dataclasses import dataclass
from typing import List

class SyllableType(Enum):
    """6 أنواع مقاطع عربية"""
    CV = auto()      # قصير مفتوح: كَ
    CVV = auto()     # طويل مفتوح: كا، كو، كي
    CVC = auto()     # قصير مغلق: كَتْ
    CVVC = auto()    # طويل مغلق: كاتْ
    CVCC = auto()    # فائق الإغلاق: كَتْبْ
    CVVCC = auto()   # فائق الطول والإغلاق: كاتْبْ

@dataclass(frozen=True)
class Syllable:
    """مقطع صوتي مع قيود صارمة"""
    onset: List[Segment]       # بداية (صوامت)
    nucleus: Segment            # نواة (صائت - إلزامي)
    coda: List[Segment]         # نهاية (صوامت)
    type: SyllableType
    stress: bool = False
    boundary: BoundaryKind = BoundaryKind.NONE
    
    def __post_init__(self):
        # تحقق: النواة يجب أن تكون صائتاً
        if self.nucleus.kind != SegmentKind.VOWEL:
            raise ValueError(f"Nucleus must be vowel, got {self.nucleus}")
        
        # تحقق: onset/coda يجب أن تكون صوامت
        for seg in self.onset + self.coda:
            if seg.kind != SegmentKind.CONSONANT:
                raise ValueError(f"Onset/coda must be consonants, got {seg}")
    
    def is_open(self) -> bool:
        """مقطع مفتوح: لا نهاية"""
        return len(self.coda) == 0
    
    def is_closed(self) -> bool:
        """مقطع مغلق: له نهاية"""
        return len(self.coda) > 0
    
    def is_heavy(self) -> bool:
        """مقطع ثقيل: CVV أو CVC"""
        return self.type in {SyllableType.CVV, SyllableType.CVC, 
                            SyllableType.CVVC, SyllableType.CVCC, SyllableType.CVVCC}
1.3 إطار البوابات (Gate Framework)
Python
# ملف: src/fvafk/c2a/gate_framework.py

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from enum import Enum, auto

class GateStatus(Enum):
    ACCEPT = auto()
    REPAIR = auto()
    REJECT = auto()

@dataclass
class GateResult:
    """نتيجة تطبيق بوابة"""
    status: GateStatus
    output: C1                  # الناتج (قد يكون معدّلاً)
    reason: str                 # سبب القرار
    deltas: List[UnitDelta]     # التعديلات المقترحة
    epi_state: EpistemicState   # حالة المعرفة
    latency_ms: float           # زمن التنفيذ

class PhonologicalGate(ABC):
    """قالب عام لجميع البوابات الصوتية"""
    
    def __init__(self, gate_id: str, epistemic_level: str):
        self.gate_id = gate_id
        self.epistemic_level = epistemic_level  # YAQIN/ZANN/SHAKK
    
    @abstractmethod
    def precondition(self, c1: C1) -> bool:
        """شرط مسبق: هل يمكن تطبيق البوابة؟"""
        pass
    
    @abstractmethod
    def apply(self, c1: C1) -> C1:
        """تطبيق التحويل"""
        pass
    
    @abstractmethod
    def postcondition(self, c1_in: C1, c1_out: C1) -> bool:
        """شرط لاحق: هل الناتج صالح؟"""
        pass
    
    def run(self, c1: C1) -> GateResult:
        """تشغيل البوابة مع قياس الأداء"""
        import time
        start = time.time()
        
        # فحص الشرط المسبق
        if not self.precondition(c1):
            return GateResult(
                status=GateStatus.REJECT,
                output=c1,
                reason=f"{self.gate_id}: Precondition failed",
                deltas=[],
                epi_state=EpistemicState("Shakk", 0.3, [f"{self.gate_id}:PRECON_FAIL"]),
                latency_ms=(time.time() - start) * 1000
            )
        
        # تطبيق التحويل
        try:
            output = self.apply(c1)
        except Exception as e:
            return GateResult(
                status=GateStatus.REJECT,
                output=c1,
                reason=f"{self.gate_id}: Application failed: {e}",
                deltas=[],
                epi_state=EpistemicState("Shakk", 0.2, [f"{self.gate_id}:APPLY_ERROR"]),
                latency_ms=(time.time() - start) * 1000
            )
        
        # فحص الشرط اللاحق
        if not self.postcondition(c1, output):
            return GateResult(
                status=GateStatus.REJECT,
                output=c1,
                reason=f"{self.gate_id}: Postcondition failed",
                deltas=[],
                epi_state=EpistemicState("Shakk", 0.3, [f"{self.gate_id}:POSTCON_FAIL"]),
                latency_ms=(time.time() - start) * 1000
            )
        
        # نجاح
        deltas = self.compute_deltas(c1, output)
        status = GateStatus.REPAIR if deltas else GateStatus.ACCEPT
        
        return GateResult(
            status=status,
            output=output,
            reason=f"{self.gate_id}: Success",
            deltas=deltas,
            epi_state=EpistemicState(self.epistemic_level, 0.85, [f"{self.gate_id}:SUCCESS"]),
            latency_ms=(time.time() - start) * 1000
        )
    
    def compute_deltas(self, old: C1, new: C1) -> List[UnitDelta]:
        """حساب الفروقات بين الإدخال والإخراج"""
        # TODO: تنفيذ خوارزمية minimal edit distance
        pass
المخرجات:
 src/fvafk/c1/segment_inventory.py (30 صامتاً + 8 صوائت)
 src/fvafk/c2a/syllable.py (6 أنواع مقاطع)
 src/fvafk/c2a/gate_framework.py (قالب البوابات)
 tests/test_segment_inventory.py (20 اختبار)
 tests/test_syllable.py (25 اختبار)
 coq/theories/Syllable.v (مبرهنات المقاطع)
معيار النجاح:
Code
✅ 45+ اختبار يمر
✅ تغطية كود 90%+
✅ توثيق كامل
✅ مبرهنات Coq تُجمّع

🎵 المرحلة 2: البوابات الصوتية (Week 3-5)
الهدف:
Code
تنفيذ 10 بوابات صوتية بمنطق كامل مع إثباتات Coq
الترتيب:
Code
أسبوع 3: البوابات الأساسية (4)
  1. GateSukun
  2. GateShadda
  3. GateTanwin
  4. GateAssimilation

أسبوع 4: البوابات المتقدمة (3)
  5. GateIdgham
  6. GateHamza
  7. GateMadd

أسبوع 5: بوابات الوقف والحذف (3)
  8. GateWaqf
  9. GateDeletion
  10. GateEpenthesis
مثال تفصيلي: GateSukun
Python
# ملف: src/fvafk/c2a/gates/gate_sukun.py

class GateSukun(PhonologicalGate):
    """
    بوابة السكون: فحص القيود الصوتية للسكون
    
    القواعد:
    1. لا يجوز تتابع سكونين (double-sukun)
    2. السكون في بداية الكلمة ممنوع
    3. السكون قبل همزة الوصل يُحوّل لحركة
    
    Epistemic Level: ZANN (ظن) - 0.80
    """
    
    def __init__(self):
        super().__init__(
            gate_id="G_SUKUN",
            epistemic_level="Zann"
        )
        self.SUKUN = "\u0652"
    
    def precondition(self, c1: C1) -> bool:
        """
        شرط مسبق: يجب أن يحتوي النص على سكون واحد على الأقل
        """
        return any(
            u.kind == "DIAC" and u.text == self.SUKUN
            for u in c1
        )
    
    def apply(self, c1: C1) -> C1:
        """
        تطبيق قواعد السكون:
        1. كشف double-sukun
        2. إصلاح بتحويل السكون الأول لفتحة
        """
        output = list(c1)  # نسخة
        
        # البحث عن double-sukun
        i = 0
        while i < len(output) - 4:
            # نمط: LETTER SUKUN ... LETTER SUKUN
            if (output[i].kind == "LETTER" and
                i+1 < len(output) and output[i+1].kind == "DIAC" and output[i+1].text == self.SUKUN):
                
                # ابحث عن السكون الثاني
                j = i + 2
                while j < min(i + 8, len(output)):  # نافذة 8 وحدات
                    if (output[j].kind == "LETTER" and
                        j+1 < len(output) and output[j+1].kind == "DIAC" and output[j+1].text == self.SUKUN):
                        
                        # وجدنا double-sukun: أصلح الأول
                        FATHA = "\u064e"
                        output[i+1] = Unit(
                            uid=output[i+1].uid,
                            kind="DIAC",
                            text=FATHA
                        )
                        break
                    j += 1
            i += 1
        
        return output
    
    def postcondition(self, c1_in: C1, c1_out: C1) -> bool:
        """
        شرط لاحق: لا يوجد double-sukun في الناتج
        """
        return not self._has_double_sukun(c1_out)
    
    def _has_double_sukun(self, c1: C1) -> bool:
        """فحص وجود double-sukun"""
        for i in range(len(c1) - 4):
            if (c1[i].kind == "LETTER" and
                i+1 < len(c1) and c1[i+1].kind == "DIAC" and c1[i+1].text == self.SUKUN):
                
                for j in range(i+2, min(i+8, len(c1))):
                    if (c1[j].kind == "LETTER" and
                        j+1 < len(c1) and c1[j+1].kind == "DIAC" and c1[j+1].text == self.SUKUN):
                        return True
        return False
مبرهنة Coq المطابقة:
coq
(* ملف: coq/theories/Gates/GateSukun.v *)

Require Import Coq.Lists.List.
Require Import Base Layers Syllable.

(* تعريف السكون *)
Definition is_sukun (seg : Segment) : bool :=
  match seg with
  | Vowel SUKUN _ => true
  | _ => false
  end.

(* تعريف double-sukun *)
Fixpoint has_double_sukun (c1 : C1) : bool :=
  match c1 with
  | [] => false
  | s1 :: s2 :: rest =>
      if is_sukun s1 && is_sukun s2 then true
      else has_double_sukun (s2 :: rest)
  | _ => false
  end.

(* البوابة *)
Definition gate_sukun_precondition (c1 : C1) : bool :=
  existsb is_sukun c1.

Fixpoint gate_sukun_apply (c1 : C1) : C1 :=
  (* TODO: تنفيذ منطق التحويل *)
  c1.

Definition gate_sukun_postcondition (c1_in c1_out : C1) : bool :=
  negb (has_double_sukun c1_out).

(* المبرهنة الرئيسية *)
Theorem gate_sukun_eliminates_double_sukun :
  forall (c1 : C1),
    gate_sukun_precondition c1 = true ->
    let c1' := gate_sukun_apply c1 in
    gate_sukun_postcondition c1 c1' = true.
Proof.
  intros c1 Hpre.
  unfold gate_sukun_postcondition.
  (* TODO: إكمال الإثبات *)
Admitted.  (* سيتم إكماله *)
المخرجات لكل بوابة:
 ملف Python بمنطق كامل
 10+ اختبارات شاملة
 ملف Coq بمبرهنات
 توثيق مفصّل
معيار النجاح:
Code
✅ 100+ اختبار يمر (10 بوابات × 10 اختبارات)
✅ تغطية كود 85%+
✅ 10 مبرهنات Coq (على الأقل Admitted للبدء)
✅ أداء <500µs لكل بوابة

| Gate | Implementation status | Test coverage | Coq proof state | Next steps |
| --- | --- | --- | --- | --- |
| GateSukun | Complete; double-sukun repair logic ready | 12 targeted unit tests (seen in `tests/`) | Proof in `GateSukun.v` currently `Admitted` | Finalize Coq proof and add regression for multi-sukun |
| GateShadda | Logic ready | 10 tests | Proof skeleton drafted | Add stress cases for doubling and voice |
| GateTanwin | Rule set in place | 8 tests | Not started | Ensure assimilation matrix and proof coverage |
| GateAssimilation | Draft logic | 6 tests | Not started | Validate all assimilation pairs; capture invariants |
| GateIdgham | Partial implementation | 4 tests | Not started | Complete mapping for letters and prove invariants |
| GateHamza | OrthographyAdapter dependency | 5 tests | Not started | Integrate adapter before proving rules |
| GateMadd | Implemented | 10 tests | Outline done | Prove extension invariants |
| GateWaqf | Basic logic written | 6 tests | Not started | Cover initial/terminal cases for WAQF |
| GateDeletion | Drafted; hamza/teeth cases | 5 tests | Not started | Expand cases for weak verbs |
| GateEpenthesis | Conceptual | 0 tests | Not started | Define insertion schema, add tests |

🔤 المرحلة 3: المحلل الصرفي (Week 6-8)
الهدف:
Code
بناء محلل صرفي كامل بدقة 85%+
المكونات:
3.1 تحديد حدود الكلمات
Python
# ملف: src/fvafk/c2b/word_boundary.py

class WordBoundaryDetector:
    """
    كشف حدود الكلمات بناءً على:
    1. المسافات
    2. علامات الترقيم
    3. التنوين (نهاية كلمة)
    4. الوقف الإجباري
    """
    
    def detect_boundaries(self, syllables: List[Syllable]) -> List[Tuple[int, int]]:
        """
        إرجاع: [(start_idx, end_idx), ...]
        """
        boundaries = []
        current_start = 0
        
        for i, syl in enumerate(syllables):
            # نهاية كلمة: boundary == PAUSE أو PHRASE
            if syl.boundary in {BoundaryKind.PAUSE, BoundaryKind.PHRASE}:
                boundaries.append((current_start, i))
                current_start = i + 1
            
            # نهاية كلمة: تنوين في النواة
            elif self._has_tanwin(syl.nucleus):
                boundaries.append((current_start, i))
                current_start = i + 1
        
        # آخر كلمة
        if current_start < len(syllables):
            boundaries.append((current_start, len(syllables) - 1))
        
        return boundaries
    
    def _has_tanwin(self, nucleus: Segment) -> bool:
        """فحص وجود تنوين"""
        if nucleus.vk is None:
            return False
        return nucleus.vk in {
            VowelKind.TANWIN_FATH,
            VowelKind.TANWIN_DAMM,
            VowelKind.TANWIN_KASR
        }
3.2 تحليل الأوزان (Pattern Analysis)
Python
# ملف: src/fvafk/c2b/pattern_analyzer.py

from enum import Enum, auto

class PatternKind(Enum):
    # أوزان الأسماء
    JAMID = auto()           # جامد: كتاب، قلم
    MUSHTAQ = auto()         # مشتق: كاتب، مكتوب
    
    # أوزان الأفعال
    VERB_MUJARRAD = auto()   # مجرد: فَعَلَ
    VERB_MAZEED = auto()      # مزيد: أَفْعَلَ، فَعَّلَ، فاعَلَ...
    
    # المصادر
    MASDAR_QIYASI = auto()   # قياسي: كِتابة، إفْعال
    MASDAR_SAMA3I = auto()   # سماعي: قِتال، جِهاد

class PatternAnalyzer:
    """
    تحليل الوزن الصرفي للكلمة
    """
    
    # أوزان الفعل الثلاثي المجرد (6 أوزان)
    VERB_PATTERNS_3 = {
        'فَعَلَ': {'pattern': 'CaCaCa', 'kind': PatternKind.VERB_MUJARRAD},
        'فَعِلَ': {'pattern': 'CaCiCa', 'kind': PatternKind.VERB_MUJARRAD},
        'فَعُلَ': {'pattern': 'CaCuCa', 'kind': PatternKind.VERB_MUJARRAD},
    }
    
    # أوزان الفعل المزيد (أشهر 10 أوزان)
    VERB_PATTERNS_MAZEED = {
        'أَفْعَلَ': {'pattern': 'أCْCaCa', 'form': 4},
        'فَعَّلَ': {'pattern': 'CaC̃aCa', 'form': 2},  # C̃ = مضعف
        'فاعَلَ': {'pattern': 'CaaCaCa', 'form': 3},
        # ... المزيد
    }
    
    # أوزان اسم الفاعل
    PARTICIPLE_PATTERNS = {
        'فاعِل': {'pattern': 'CaaCiC', 'type': 'active'},
        'مُفْعِل': {'pattern': 'muCCiC', 'type': 'active'},
    }
    
    # أوزان اسم المفعول
    PASSIVE_PATTERNS = {
        'مَفْعول': {'pattern': 'maCCuuC', 'type': 'passive'},
        'مُفَعَّل': {'pattern': 'muCaC̃aC', 'type': 'passive'},
    }
    
    def analyze(self, syllables: List[Syllable]) -> Optional[PatternKind]:
        """
        تحليل وزن الكلمة من مقاطعها
        
        الخطوات:
        1. استخراج الجذر (Root Extraction)
        2. تحديد الزوائد (Affix Identification)
        3. مطابقة الوزن (Pattern Matching)
        """
        # استخراج الحروف الأصول
        root_consonants = self._extract_root_consonants(syllables)
        
        # مطابقة مع الأوزان المعروفة
        for pattern_name, pattern_info in self.VERB_PATTERNS_3.items():
            if self._matches_pattern(syllables, pattern_info['pattern']):
                return pattern_info['kind']
        
        # ... البحث في الأوزان الأخرى
        
        return None
    
    def _extract_root_consonants(self, syllables: List[Syllable]) -> List[str]:
        """
        استخراج الجذر (عادة 3 حروف)
        
        الزوائد المعروفة:
        - الألف في فاعِل
        - الميم في مَفْعول
        - التضعيف في فَعَّلَ
        - ... إلخ
        """
        consonants = []
        for syl in syllables:
            # استخراج الصوامت من onset + coda
            for seg in syl.onset + syl.coda:
                # تجاهل الزوائد المعروفة
                if not self._is_augment(seg):
                    consonants.append(seg.text)
        
        return consonants[:3]  # عادة 3 حروف أصلية
    
    def _is_augment(self, seg: Segment) -> bool:
        """فحص إن كان الحرف زائداً"""
        # الزوائد: همزة، ألف، ميم، تاء، نون، سين، ...
        AUGMENTS = {'أ', 'ا', 'م', 'ت', 'ن', 'س', 'ي', 'و'}
        return seg.text in AUGMENTS
3.3 تصنيف نوع الكلمة
Python
# ملف: src/fvafk/c2b/word_classifier.py

class WordKind(Enum):
    NOUN = auto()       # اسم
    VERB = auto()       # فعل
    PARTICLE = auto()   # حرف

class WordClassifier:
    """
    تصنيف الكلمة: اسم/فعل/حرف
    """
    
    # حروف معروفة (100+)
    PARTICLES = {
        # حروف الجر
        'من', 'إلى', 'عن', 'على', 'في', 'الباء', 'اللام', 'الكاف',
        # حروف العطف
        'و', 'ف', 'ثم', 'أو', 'بل', 'لكن',
        # حروف النصب
        'أن', 'لن', 'كي', 'حتى',
        # ... المزيد
    }
    
    def classify(self, word: str, pattern: Optional[PatternKind]) -> WordKind:
        """
        تصنيف بناءً على:
        1. القائمة المغلقة (للحروف)
        2. الوزن الصرفي
        3. السمات الصرفية (تنوين، إعراب)
        """
        # فحص القائمة المغلقة
        if word in self.PARTICLES:
            return WordKind.PARTICLE
        
        # فحص الوزن
        if pattern in {PatternKind.VERB_MUJARRAD, PatternKind.VERB_MAZEED}:
            return WordKind.VERB
        
        # الافتراض: اسم
        return WordKind.NOUN
المخرجات:
 src/fvafk/c2b/word_boundary.py + 15 اختبار
 src/fvafk/c2b/pattern_analyzer.py + 30 اختبار
 src/fvafk/c2b/word_classifier.py + 20 اختبار
 src/fvafk/c2b/root_extractor.py + 25 اختبار
 coq/theories/Morphology.v (10 مبرهنات)
 tests/test_morphology_corpus.py (اختبار على corpus)
معيار النجاح:
Code
✅ 90+ اختبار يمر
✅ F1-score ≥ 0.85 على corpus تجريبي (1000 كلمة)
✅ دقة تصنيف نوع الكلمة ≥ 90%
✅ دقة استخراج الجذور ≥ 80%


🔗 المرحلة 4: المحلل النحوي (Week 9-11)
الهدف:
Code
بناء محلل نحوي كامل مع 3 أنواع روابط + دقة 80%+

4.1 بناء الروابط الإسنادية (ISNADI)
Python
# ملف: src/fvafk/c2b/links_isnadi.py

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum, auto

class Rel3(Enum):
    """3 أنواع روابط فقط"""
    ISNADI = auto()    # إسنادي: فعل→فاعل، مبتدأ→خبر
    TADMINI = auto()   # تضميني: فعل متعدٍ→مفعول
    TAQYIDI = auto()   # تقييدي: اسم→نعت، اسم→مضاف إليه

@dataclass(frozen=True)
class Link:
    """رابط نحوي بين كلمتين"""
    rel: Rel3
    head: int          # رأس الرابط (index)
    dep: int           # ذيل الرابط (index)
    confidence: float  # ثقة القرار (0.0-1.0)

class IsnadiLinker:
    """
    بناء الروابط الإسنادية
    
    القواعد:
    1. الجملة الفعلية: فعل → فاعل (verb → subject)
    2. الجملة الاسمية: مبتدأ → خبر (mubtada → khabar)
    3. ترتيب VSO: Verb-Subject-Object
    """
    
    def build_links(self, wordforms: List[WordForm]) -> List[Link]:
        """
        بناء الروابط الإسنادية
        
        الخطوات:
        1. تحديد نوع الجملة (فعلية/اسمية)
        2. تحديد الفعل/المبتدأ
        3. البحث عن الفاعل/الخبر
        4. بناء الرابط
        """
        links = []
        
        # فحص الكلمة الأولى
        if not wordforms:
            return links
        
        first_word = wordforms[0]
        
        if first_word.word_kind == WordKind.VERB:
            # جملة فعلية: ابحث عن الفاعل
            links.extend(self._build_verbal_sentence_links(wordforms))
        
        elif first_word.word_kind == WordKind.NOUN:
            # جملة اسمية: ابحث عن الخبر
            links.extend(self._build_nominal_sentence_links(wordforms))
        
        return links
    
    def _build_verbal_sentence_links(self, wordforms: List[WordForm]) -> List[Link]:
        """
        جملة فعلية: VSO
        
        مثال: ذَهَبَ مُحَمَّدٌ
        verb=0, subject=1
        Link(ISNADI, head=0, dep=1)
        """
        links = []
        verb_idx = 0
        
        # ابحث عن أول اسم مرفوع (فاعل)
        for i in range(1, len(wordforms)):
            word = wordforms[i]
            
            if (word.word_kind == WordKind.NOUN and
                self._is_nominative(word)):
                
                # وجدنا الفاعل
                links.append(Link(
                    rel=Rel3.ISNADI,
                    head=verb_idx,
                    dep=i,
                    confidence=0.90
                ))
                break
        
        return links
    
    def _build_nominal_sentence_links(self, wordforms: List[WordForm]) -> List[Link]:
        """
        جملة اسمية: المبتدأ + الخبر
        
        مثال: مُحَمَّدٌ طالِبٌ
        mubtada=0, khabar=1
        Link(ISNADI, head=0, dep=1)
        """
        links = []
        
        if len(wordforms) < 2:
            return links
        
        mubtada_idx = 0
        khabar_idx = 1
        
        # تحقق: كلاهما مرفوع
        if (self._is_nominative(wordforms[mubtada_idx]) and
            self._is_nominative(wordforms[khabar_idx])):
            
            links.append(Link(
                rel=Rel3.ISNADI,
                head=mubtada_idx,
                dep=khabar_idx,
                confidence=0.85
            ))
        
        return links
    
    def _is_nominative(self, word: WordForm) -> bool:
        """فحص إن كانت ��لكلمة مرفوعة"""
        # علامات الرفع: ضمة، واو، ألف
        if 'case' in word.morph_flags:
            return word.morph_flags['case'] == 'nominative'
        
        # فحص من المقاطع الأخيرة
        if word.syllables:
            last_syl = word.syllables[-1]
            nucleus = last_syl.nucleus
            
            # ضمة في النواة الأخيرة
            if nucleus.vk == VowelKind.DAMMA:
                return True
            
            # تنوين ضم
            if nucleus.vk == VowelKind.TANWIN_DAMM:
                return True
        
        return False

4.2 بناء الروابط التضمينية (TADMINI)
Python
# ملف: src/fvafk/c2b/links_tadmini.py

class TadminiLinker:
    """
    بناء الروابط التضمينية: فعل متعدٍ → مفعول
    
    القواعد:
    1. الفعل المتعدي يحتاج مفعولاً (منصوب)
    2. الفعل اللازم لا ��حتاج مفعولاً
    3. بعض الأفعال تتعدى لمفعولين
    """
    
    # قائمة الأفعال المتعدية الشائعة
    TRANSITIVE_VERBS = {
        'كتب', 'قرأ', 'أكل', 'شرب', 'فتح', 'أخذ', 'ضرب',
        'علم', 'رأى', 'سمع', 'وجد', 'جعل', 'ظن',
        # ... المزيد (500+)
    }
    
    # أفعال تتعدى لمفعولين
    DITRANSITIVE_VERBS = {
        'أعطى', 'منح', 'وهب', 'علّم', 'أرى', 'ظن', 'حسب',
        # ... المزيد (50+)
    }
    
    def build_links(self, wordforms: List[WordForm], 
                    isnadi_links: List[Link]) -> List[Link]:
        """
        بناء الروابط التضمينية
        
        الخطوات:
        1. تحديد الفعل المتعدي
        2. البحث عن المفعول (منصوب)
        3. بناء الرابط
        """
        links = []
        
        # ابحث عن الأفعال
        for i, word in enumerate(wordforms):
            if word.word_kind == WordKind.VERB:
                
                # فحص إن كان متعدياً
                if self._is_transitive(word):
                    
                    # ابحث عن المفعول (اسم منصوب)
                    obj_idx = self._find_object(wordforms, i)
                    
                    if obj_idx is not None:
                        links.append(Link(
                            rel=Rel3.TADMINI,
                            head=i,
                            dep=obj_idx,
                            confidence=0.85
                        ))
        
        return links
    
    def _is_transitive(self, word: WordForm) -> bool:
        """فحص إن كان الفعل متعدياً"""
        # استخراج الجذر
        root = self._extract_root(word)
        
        # فحص القائمة
        if root in self.TRANSITIVE_VERBS:
            return True
        
        # قاعدة عامة: أوزان مزيدة عادة متعدية
        if word.pattern == PatternKind.VERB_MAZEED:
            return True
        
        return False
    
    def _find_object(self, wordforms: List[WordForm], 
                     verb_idx: int) -> Optional[int]:
        """البحث عن المفعول به"""
        # ابحث بعد الفعل
        for i in range(verb_idx + 1, len(wordforms)):
            word = wordforms[i]
            
            if (word.word_kind == WordKind.NOUN and
                self._is_accusative(word)):
                
                return i
        
        return None
    
    def _is_accusative(self, word: WordForm) -> bool:
        """فحص إن كانت الكلمة منصوبة"""
        if 'case' in word.morph_flags:
            return word.morph_flags['case'] == 'accusative'
        
        # فحص من المقاطع الأخيرة
        if word.syllables:
            last_syl = word.syllables[-1]
            nucleus = last_syl.nucleus
            
            # فتحة في النواة الأخيرة
            if nucleus.vk == VowelKind.FATHA:
                return True
            
            # تنوين فتح
            if nucleus.vk == VowelKind.TANWIN_FATH:
                return True
        
        return False
    
    def _extract_root(self, word: WordForm) -> str:
        """استخراج جذر الفعل"""
        # TODO: تنفيذ استخراج الجذر
        # حالياً: استخدام نص الكلمة مباشرة (تبسيط)
        text = ''.join(
            seg.text for syl in word.syllables
            for seg in syl.onset + [syl.nucleus] + syl.coda
            if seg.kind == SegmentKind.CONSONANT
        )
        return text[:3]  # أول 3 حروف أصلية

4.3 بناء الروابط التقييدية (TAQYIDI)
Python
# ملف: src/fvafk/c2b/links_taqyidi.py

class TaqyidiLinker:
    """
    بناء الروابط التقييدية: اسم → نعت/مضاف إليه
    
    القواعد:
    1. النعت: يطابق المنعوت في (إعراب، تعريف، عدد، جنس)
    2. المضاف إليه: مجرور دائماً
    3. الظرف: مكان/زمان
    """
    
    def build_links(self, wordforms: List[WordForm]) -> List[Link]:
        """
        بناء الروابط التقييدية
        
        الخطوات:
        1. تحديد الأسماء
        2. البحث عن النعت/المضاف إليه بعدها
        3. فحص التطابق
        4. بناء الرابط
        """
        links = []
        
        for i in range(len(wordforms) - 1):
            word = wordforms[i]
            next_word = wordforms[i + 1]
            
            if word.word_kind == WordKind.NOUN:
                
                # فحص النعت
                if self._is_adjective_of(next_word, word):
                    links.append(Link(
                        rel=Rel3.TAQYIDI,
                        head=i,
                        dep=i + 1,
                        confidence=0.80
                    ))
                
                # فحص المضاف إليه
                elif self._is_genitive_of(next_word, word):
                    links.append(Link(
                        rel=Rel3.TAQYIDI,
                        head=i,
                        dep=i + 1,
                        confidence=0.85
                    ))
        
        return links
    
    def _is_adjective_of(self, adjective: WordForm, noun: WordForm) -> bool:
        """
        فحص إن كانت الكلمة نعتاً للاسم
        
        شروط التطابق:
        1. الإعراب (رفع/نصب/جر)
        2. التعريف/التنكير
        3. العدد (مفرد/مثنى/جمع)
        4. الجنس (مذكر/مؤنث)
        """
        # 1. تطابق الإعراب
        noun_case = self._get_case(noun)
        adj_case = self._get_case(adjective)
        
        if noun_case != adj_case:
            return False
        
        # 2. تطابق التعريف
        noun_def = noun.morph_flags.get('definite', False)
        adj_def = adjective.morph_flags.get('definite', False)
        
        if noun_def != adj_def:
            return False
        
        # 3. تطابق العدد
        noun_num = noun.morph_flags.get('number', 'singular')
        adj_num = adjective.morph_flags.get('number', 'singular')
        
        if noun_num != adj_num:
            return False
        
        # 4. تطابق الجنس
        noun_gen = noun.morph_flags.get('gender', 'masculine')
        adj_gen = adjective.morph_flags.get('gender', 'masculine')
        
        if noun_gen != adj_gen:
            return False
        
        return True
    
    def _is_genitive_of(self, genitive: WordForm, noun: WordForm) -> bool:
        """
        فحص إن كانت الكلمة مضافاً إليه
        
        شروط:
        1. الاسم الأول (المضاف) بدون تنوين
        2. الاسم الثاني (المضاف إليه) مجرور
        """
        # 1. المضاف: لا تنوين
        if self._has_tanwin(noun):
            return False
        
        # 2. المضاف إليه: مجرور
        if not self._is_genitive(genitive):
            return False
        
        return True
    
    def _get_case(self, word: WordForm) -> Optional[str]:
        """استخراج حالة الإعراب"""
        return word.morph_flags.get('case', None)
    
    def _has_tanwin(self, word: WordForm) -> bool:
        """فحص وجود تنوين"""
        if word.syllables:
            last_syl = word.syllables[-1]
            nucleus = last_syl.nucleus
            return nucleus.vk in {
                VowelKind.TANWIN_FATH,
                VowelKind.TANWIN_DAMM,
                VowelKind.TANWIN_KASR
            }
        return False
    
    def _is_genitive(self, word: WordForm) -> bool:
        """فحص إن كانت الكلمة مجرورة"""
        if 'case' in word.morph_flags:
            return word.morph_flags['case'] == 'genitive'
        
        # فحص من المقاطع الأخيرة
        if word.syllables:
            last_syl = word.syllables[-1]
            nucleus = last_syl.nucleus
            
            # كسرة في النواة الأخيرة
            if nucleus.vk == VowelKind.KASRA:
                return True
            
            # تنوين كسر
            if nucleus.vk == VowelKind.TANWIN_KASR:
                return True
        
        return False

4.4 المحلل النحوي الكامل (Orchestrator)
Python
# ملف: src/fvafk/c2b/parser.py

class SyntacticParser:
    """
    المحلل النحوي الكامل: يدمج جميع أنواع الروابط
    
    المراحل:
    1. بناء الروابط الإسنادية (ISNADI)
    2. بناء الروابط التضمينية (TADMINI)
    3. بناء الروابط التقييدية (TAQYIDI)
    4. التحقق من القيود النحوية
    """
    
    def __init__(self):
        self.isnadi_linker = IsnadiLinker()
        self.tadmini_linker = TadminiLinker()
        self.taqyidi_linker = TaqyidiLinker()
    
    def parse(self, wordforms: List[WordForm]) -> Tuple[List[Link], List[str]]:
        """
        تحليل نحوي كامل
        
        إرجاع:
        - links: قائمة الروابط
        - errors: قائمة الأخطاء النحوية
        """
        links = []
        errors = []
        
        # 1. الروابط الإسنادية (أولاً)
        isnadi_links = self.isnadi_linker.build_links(wordforms)
        links.extend(isnadi_links)
        
        # 2. الروابط التضمينية
        tadmini_links = self.tadmini_linker.build_links(wordforms, isnadi_links)
        links.extend(tadmini_links)
        
        # 3. الروابط التقييدية
        taqyidi_links = self.taqyidi_linker.build_links(wordforms)
        links.extend(taqyidi_links)
        
        # 4. التحقق من القيود (المرحلة التالية)
        # errors = self._validate_constraints(wordforms, links)
        
        return links, errors
    
    def visualize(self, wordforms: List[WordForm], links: List[Link]) -> str:
        """
        تصوير بصري للتحليل النحوي
        
        مثال:
        ```
        ذَهَبَ    مُحَمَّدٌ    إِلَى    المَدْرَسَةِ
        verb      noun        prep     noun
          └─ISNADI─┘
               └──TADMINI────────┘
        ```
        """
        # TODO: تنفيذ التصوير البصري
        pass

المخرجات للمرحلة 4:
 src/fvafk/c2b/links_isnadi.py + 20 اختبار
 src/fvafk/c2b/links_tadmini.py + 20 اختبار
 src/fvafk/c2b/links_taqyidi.py + 25 اختبار
 src/fvafk/c2b/parser.py + 15 اختبار
 coq/theories/Syntax.v (15 مبرهنة)
 tests/test_parser_corpus.py (اختبار على corpus)
معيار النجاح:
Code
✅ 80+ اختبار يمر
✅ UAS (Unlabeled Attachment Score) ≥ 0.80
✅ LAS (Labeled Attachment Score) ≥ 0.75
✅ دقة تحديد نوع الرابط ≥ 85%

⚖️ المرحلة 5: القيود النحوية (Week 12-13)
الهدف:
Code
تطبيق 5 قيود نحوية بالكامل (بدون stubs)

5.1 القيد 1: لا فعل بلا فاعل
Python
# ملف: src/fvafk/c2b/constraints/verb_subject.py

class VerbSubjectConstraint:
    """
    القيد: لا فعل بلا فاعل (إلا في المبني للمجهول)
    
    القاعدة:
    - كل فعل يحتاج فاعلاً (رابط ISNADI)
    - استثناء: الفعل المبني للمجهول (يحتاج نائب فاعل)
    """
    
    def validate(self, wordforms: List[WordForm], 
                 links: List[Link]) -> List[ConstraintViolation]:
        """
        التحقق من القيد
        
        إرجاع: قائمة الانتهاكات
        """
        violations = []
        
        # ابحث عن الأفعال
        for i, word in enumerate(wordforms):
            if word.word_kind == WordKind.VERB:
                
                # فحص إن كان مبنياً للمجهول
                is_passive = self._is_passive_voice(word)
                
                # فحص وجود رابط ISNADI من الفعل
                has_subject = any(
                    link.rel == Rel3.ISNADI and link.head == i
                    for link in links
                )
                
                if not has_subject and not is_passive:
                    violations.append(ConstraintViolation(
                        constraint_id="NO_VERB_WITHOUT_SUBJECT",
                        word_idx=i,
                        message=f"الفعل '{self._get_word_text(word)}' يحتاج فاعلاً",
                        severity="ERROR"
                    ))
        
        return violations
    
    def _is_passive_voice(self, word: WordForm) -> bool:
        """فحص إن كان الفعل مبنياً للمجهول"""
        # علامات البناء للمجهول:
        # 1. ضم أول حرف في الماضي (ضُرِبَ)
        # 2. ضم أول حرف وفتح قبل الآخر في المضارع (يُضْرَب)
        
        if word.syllables:
            first_syl = word.syllables[0]
            nucleus = first_syl.nucleus
            
            # ضمة في المقطع الأول
            if nucleus.vk == VowelKind.DAMMA:
                return True
        
        return False
    
    def _get_word_text(self, word: WordForm) -> str:
        """استخراج نص الكلمة"""
        return ''.join(
            seg.text for syl in word.syllables
            for seg in syl.onset + [syl.nucleus] + syl.coda
        )

5.2 القيد 2: لا متعدٍ بلا مفعول
Python
# ملف: src/fvafk/c2b/constraints/transitive_object.py

class TransitiveObjectConstraint:
    """
    القيد: لا فعل متعدٍ بلا مفعول
    
    القاعدة:
    - كل فعل متعدٍ يحتاج مفعولاً (رابط TADMINI)
    """
    
    # قائمة الأفعال المتعدية (500+)
    TRANSITIVE_VERBS = {
        'كتب', 'قرأ', 'أكل', 'شرب', 'فتح', 'أخذ',
        # ... (يمكن تحميلها من ملف خارجي)
    }
    
    def validate(self, wordforms: List[WordForm], 
                 links: List[Link]) -> List[ConstraintViolation]:
        violations = []
        
        for i, word in enumerate(wordforms):
            if word.word_kind == WordKind.VERB:
                
                # فحص إن كان متعدياً
                if self._is_transitive(word):
                    
                    # فحص وجود رابط TADMINI من الفعل
                    has_object = any(
                        link.rel == Rel3.TADMINI and link.head == i
                        for link in links
                    )
                    
                    if not has_object:
                        violations.append(ConstraintViolation(
                            constraint_id="NO_TRANSITIVE_WITHOUT_OBJECT",
                            word_idx=i,
                            message=f"الفعل المتعدي '{self._get_word_text(word)}' يحتاج مفعولاً",
                            severity="ERROR"
                        ))
        
        return violations
    
    def _is_transitive(self, word: WordForm) -> bool:
        """فحص إن كان الفعل متعدياً"""
        root = self._extract_root(word)
        return root in self.TRANSITIVE_VERBS

5.3 القيد 3: تطابق النعت والمنعوت
Python
# ملف: src/fvafk/c2b/constraints/adjective_agreement.py

class AdjectiveAgreementConstraint:
    """
    القيد: تطابق النعت والمنعوت في 4 أوجه
    
    القاعدة:
    - النعت يطابق المنعوت في:
      1. الإعراب (رفع/نصب/جر)
      2. التعريف/��لتنكير
      3. العدد (مفرد/مثنى/جمع)
      4. الجنس (مذكر/مؤنث)
    """
    
    def validate(self, wordforms: List[WordForm], 
                 links: List[Link]) -> List[ConstraintViolation]:
        violations = []
        
        # ابحث عن روابط TAQYIDI (نعت)
        for link in links:
            if link.rel == Rel3.TAQYIDI:
                
                noun = wordforms[link.head]
                adjective = wordforms[link.dep]
                
                # فحص التطابق في 4 أوجه
                mismatches = self._check_agreement(noun, adjective)
                
                if mismatches:
                    violations.append(ConstraintViolation(
                        constraint_id="ADJECTIVE_NOUN_MISMATCH",
                        word_idx=link.dep,
                        message=f"عدم تطابق: {', '.join(mismatches)}",
                        severity="ERROR"
                    ))
        
        return violations
    
    def _check_agreement(self, noun: WordForm, 
                         adjective: WordForm) -> List[str]:
        """فحص التطابق في 4 أوجه"""
        mismatches = []
        
        # 1. الإعراب
        noun_case = noun.morph_flags.get('case')
        adj_case = adjective.morph_flags.get('case')
        if noun_case != adj_case:
            mismatches.append(f"الإعراب ({noun_case} ≠ {adj_case})")
        
        # 2. التعريف
        noun_def = noun.morph_flags.get('definite', False)
        adj_def = adjective.morph_flags.get('definite', False)
        if noun_def != adj_def:
            mismatches.append(f"التعريف ({noun_def} ≠ {adj_def})")
        
        # 3. العدد
        noun_num = noun.morph_flags.get('number')
        adj_num = adjective.morph_flags.get('number')
        if noun_num != adj_num:
            mismatches.append(f"العدد ({noun_num} ≠ {adj_num})")
        
        # 4. الجنس
        noun_gen = noun.morph_flags.get('gender')
        adj_gen = adjective.morph_flags.get('gender')
        if noun_gen != adj_gen:
            mismatches.append(f"الجنس ({noun_gen} ≠ {adj_gen})")
        
        return mismatches

5.4 القيد 4: السببية تتطلب أحداثاً
Python
# ملف: src/fvafk/c2b/constraints/causality_events.py

class CausalityEventsConstraint:
    """
    القيد: السببية تتطلب أحداثاً
    
    القاعدة:
    - إذا وُجدت علاقة سببية (cause → effect)
    - يجب أن يكون كلاهما حدثاً (event)
    """
    
    # أدوات السببية
    CAUSALITY_PARTICLES = {
        'لأن', 'لذلك', 'فـ', 'إذن', 'حتى', 'لـ', 'كي'
    }
    
    def validate(self, wordforms: List[WordForm], 
                 links: List[Link],
                 events: List[Event]) -> List[ConstraintViolation]:
        violations = []
        
        # ابحث عن أدوات السببية
        for i, word in enumerate(wordforms):
            word_text = self._get_word_text(word)
            
            if word_text in self.CAUSALITY_PARTICLES:
                
                # فحص وجود حدث قبل وبعد الأداة
                has_event_before = self._has_event_at(events, i - 1)
                has_event_after = self._has_event_at(events, i + 1)
                
                if not (has_event_before and has_event_after):
                    violations.append(ConstraintViolation(
                        constraint_id="CAUSALITY_WITHOUT_EVENTS",
                        word_idx=i,
                        message=f"الأداة السببية '{word_text}' تحتاج حدثين",
                        severity="WARNING"
                    ))
        
        return violations
    
    def _has_event_at(self, events: List[Event], word_idx: int) -> bool:
        """فحص وجود حدث عند الفهرس المحدد"""
        return any(event.word_idx == word_idx for event in events)

5.5 القيد 5: المبني للمجهول يتطلب تغيير صيغة
Python
# ملف: src/fvafk/c2b/constraints/passive_voice.py

class PassiveVoiceConstraint:
    """
    القيد: المبني للمجهول يتطلب تغيير صيغة
    
    القاعدة:
    - الفعل المبني للمجهول:
      1. ضم أول حرف في الماضي (ضُرِبَ)
      2. كسر ما قبل الآخر
    - يحتاج نائب فاعل (مرفوع)
    """
    
    def validate(self, wordforms: List[WordForm], 
                 links: List[Link]) -> List[ConstraintViolation]:
        violations = []
        
        for i, word in enumerate(wordforms):
            if word.word_kind == WordKind.VERB:
                
                # فحص إن كان مبنياً للمجهول
                if self._is_passive_voice(word):
                    
                    # فحص الصيغة الصرفية
                    if not self._has_passive_morphology(word):
                        violations.append(ConstraintViolation(
                            constraint_id="PASSIVE_WITHOUT_MORPHOLOGY",
                            word_idx=i,
                            message="الفعل المبني للمجهول يحتاج تغيير صيغة",
                            severity="ERROR"
                        ))
                    
                    # فحص وجود نائب فاعل (ISNADI)
                    has_deputy_subject = any(
                        link.rel == Rel3.ISNADI and link.head == i
                        for link in links
                    )
                    
                    if not has_deputy_subject:
                        violations.append(ConstraintViolation(
                            constraint_id="PASSIVE_WITHOUT_DEPUTY_SUBJECT",
                            word_idx=i,
                            message="الفعل المبني للمجهول يحتاج نائب فاعل",
                            severity="ERROR"
                        ))
        
        return violations
    
    def _is_passive_voice(self, word: WordForm) -> bool:
        """فحص إن كان الفعل مبنياً للمجهول"""
        # ضمة في المقطع الأول
        if word.syllables:
            first_syl = word.syllables[0]
            if first_syl.nucleus.vk == VowelKind.DAMMA:
                return True
        return False
    
    def _has_passive_morphology(self, word: WordForm) -> bool:
        """فحص وجود صيغة المبني للمجهول"""
        if len(word.syllables) < 2:
            return False
        
        # ضم الأول + كسر ما قبل الآخر
        first = word.syllables[0].nucleus
        penult = word.syllables[-2].nucleus if len(word.syllables) > 1 else None
        
        return (first.vk == VowelKind.DAMMA and
                penult is not None and 
                penult.vk == VowelKind.KASRA)

5.6 نظام التحقق الكامل
Python
# ملف: src/fvafk/c2b/constraint_validator.py

@dataclass
class ConstraintViolation:
    """انتهاك قيد نحوي"""
    constraint_id: str
    word_idx: int
    message: str
    severity: str  # ERROR | WARNING | INFO

class ConstraintValidator:
    """
    نظام التحقق من جميع القيود النحوية
    """
    
    def __init__(self):
        self.constraints = [
            VerbSubjectConstraint(),
            TransitiveObjectConstraint(),
            AdjectiveAgreementConstraint(),
            CausalityEventsConstraint(),
            PassiveVoiceConstraint(),
        ]
    
    def validate_all(self, wordforms: List[WordForm], 
                     links: List[Link],
                     events: List[Event]) -> Tuple[bool, List[ConstraintViolation]]:
        """
        التحقق من جميع القيود
        
        إرجاع:
        - is_valid: هل النص صحيح نحوياً؟
        - violations: قائمة الانتهاكات
        """
        all_violations = []
        
        for constraint in self.constraints:
            violations = constraint.validate(wordforms, links, events)
            all_violations.extend(violations)
        
        # فقط الأخطاء تجعل النص غير صحيح
        has_errors = any(v.severity == "ERROR" for v in all_violations)
        is_valid = not has_errors
        
        return is_valid, all_violations
    
    def generate_report(self, violations: List[ConstraintViolation]) -> str:
        """
        تقرير مفصّل عن الانتهاكات
        """
        if not violations:
            return "✅ النص صحيح نحوياً"
        
        report = f"⚠️ وُجد {len(violations)} انتهاك:\n\n"
        
        for i, v in enumerate(violations, 1):
            report += f"{i}. [{v.severity}] {v.constraint_id}\n"
            report += f"   الكلمة #{v.word_idx}: {v.message}\n\n"
        
        return report

المخرجات للمرحلة 5:
 5 ملفات constraints (واحد لكل قيد) + 50 اختبار
 src/fvafk/c2b/constraint_validator.py + 15 اختبار
 coq/theories/Constraints.v (10 مبرهنات)
 tests/test_constraints_corpus.py (اختبار على corpus)
معيار النجاح:
Code
✅ 65+ اختبار يمر
✅ دقة كشف الأخطاء ≥ 90%
✅ معدل false positives ≤ 10%
✅ 0 انتهاكات على نصوص صحيحة

| Constraint | Test artifacts | Metric target | Data source |
| --- | --- | --- | --- |
| لا فعل بلا فاعل | `tests/test_constraints_corpus.py` scenarios + corpus subject checks | 0 violations on valid sentences | Annotated active/passive sentences |
| لا متعدٍ بلا مفعول | Transitive verb cases | ≥95% detection of missing objects | `tests/` + targeted verbs dataset |
| تطابق النعت والمنعوت | Adjective/Noun agreement bench | 0 mismatches on annotated pairs | Grammar corpus (nouns/adjectives) |
| السببية تتطلب أحداثاً | EventExtractor-driven tests | Evidence coverage ≥90% | Causal corpus with particles (لأن، لذلك...) |
| المبني للمجهول يتطلب تغيير صيغة | Passive constructions + root checks | ≥90% detection accuracy | Passive voice dataset + root extractor output |

🔄 المرحلة 6: التكامل والتحسين (Week 14-16)
الهدف:
Code
تكامل جميع المكونات + اختبار end-to-end + تحسين الأداء

6.1 Pipeline الكامل
Python
# ملف: src/fvafk/pipeline/complete_pipeline.py

class CompletePipeline:
    """
    المعالجة الكاملة: نص → معنى
    
    المراحل:
    C1: Text → Segments
    C2a: Segments → Syllables (10 phonological gates)
    C2b: Syllables → WordForms + Links (morphology + syntax)
    C2c: Accept/Reject decision (semantic gates)
    C3: Meaning (if accepted)
    """
    
    def __init__(self):
        # C1: Text adapter
        self.codec = FormCodecV2(UnitDictionary())
        
        # C2a: Phonological gates (10)
        self.phono_gates = [
            GateSukun(),
            GateShadda(),
            GateTanwin(),
            GateAssimilation(),
            GateIdgham(),
            GateHamza(),
            GateMadd(),
            GateWaqf(),
            GateDeletion(),
            GateEpenthesis(),
        ]
        
        # C2a: Syllabifier
        self.syllabifier = Syllabifier()
        
        # C2b: Morphological analyzer
        self.word_boundary_detector = WordBoundaryDetector()
        self.pattern_analyzer = PatternAnalyzer()
        self.word_classifier = WordClassifier()
        
        # C2b: Syntactic parser
        self.parser = SyntacticParser()
        
        # C2b: Constraint validator
        self.constraint_validator = ConstraintValidator()
        
        # C2c: Semantic gates
        self.semantic_gate = SemanticGate()
        
        # Statistics
        self.stats = PipelineStatistics()
    
    def process(self, text: str, prior: PriorInfo) -> ProcessingResult:
        """
        معالجة كاملة من نص إلى معنى
        
        المراحل:
        1. C1: تحويل النص لـ segments
        2. C2a: تطبيق البوابات الصوتية
        3. C2a: تقطيع لمقاطع
        4. C2b: تحليل صرفي
        5. C2b: تحليل نحوي
        6. C2b: التحقق من القيود
        7. C2c: قرار القبول/الرفض
        8. C3: توليد المعنى (إن قُبل)
        """
        import time
        start_time = time.time()
        
        result = ProcessingResult()
        
        try:
            # ========== C1 ==========
            c1_start = time.time()
            
            # تحويل النص لـ units
            units, payload, checksum = self.codec.encode_with_header(text)
            
            # التحقق من العكوسية (T_CODEC_REVERSIBLE)
            decoded = self.codec.decode_with_header(payload, checksum)
            assert decoded == text, "Codec reversibility failed!"
            
            result.c1_units = units
            result.c1_time_ms = (time.time() - c1_start) * 1000
            
            # ========== C2a: Phonological Gates ==========
            c2a_start = time.time()
            
            # تطبيق البوابات الصوتية
            current_units = units
            for gate in self.phono_gates:
                gate_result = gate.run(current_units)
                
                result.gate_results.append(gate_result)
                
                if gate_result.status == GateStatus.REJECT:
                    result.accept = False
                    result.reject_reason = gate_result.reason
                    return result
                
                current_units = gate_result.output
            
            # تقطيع لمقاطع
            syllables = self.syllabifier.syllabify(current_units)
            if syllables is None:
                result.accept = False
                result.reject_reason = "Syllabification failed"
                return result
            
            result.syllables = syllables
            result.c2a_time_ms = (time.time() - c2a_start) * 1000
            
            # ========== C2b: Morphology ==========
            c2b_start = time.time()
            
            # تحديد حدود الكلمات
            word_boundaries = self.word_boundary_detector.detect_boundaries(syllables)
            
            # تحليل كل كلمة
            wordforms = []
            for start_idx, end_idx in word_boundaries:
                word_syls = syllables[start_idx:end_idx+1]
                
                # تحليل الوزن
                pattern = self.pattern_analyzer.analyze(word_syls)
                
                # تصنيف نوع الكلمة
                word_text = self._syllables_to_text(word_syls)
                word_kind = self.word_classifier.classify(word_text, pattern)
                
                # بناء WordForm
                wordform = WordForm(
                    syllables=word_syls,
                    word_kind=word_kind,
                    i3rab=I3rabKind.MU3RAB,  # TODO: تحديد دقيق
                    pattern=pattern if pattern else PatternKind.JAMID,
                    root_gate=RootGateKind.JAMID_ROOT,  # TODO
                    morph_flags=self._extract_morph_flags(word_syls)
                )
                
                wordforms.append(wordform)
            
            result.wordforms = wordforms
            
            # ========== C2b: Syntax ==========
            
            # تحليل نحوي
            links, parse_errors = self.parser.parse(wordforms)
            result.links = links
            
            # التحقق من القيود
            events = []  # TODO: استخراج الأحداث
            is_valid, violations = self.constraint_validator.validate_all(
                wordforms, links, events
            )
            
            result.constraint_violations = violations
            result.c2b_time_ms = (time.time() - c2b_start) * 1000
            
            # ========== C2c: Semantic Gate ==========
            c2c_start = time.time()
            
            # بناء TraceC2
            trace = TraceC2(
                syllables=syllables,
                wordforms=wordforms,
                links=links,
                prior=prior,
                evidence=EvidenceWeight(score=1.0, parts=[]),
                conflict=ConflictResolutionRule(strategy="max_evidence"),
                scope=ScopeRule(quantifier_scope={}),
                reality=RealityLink(truth_ok=True, reference_ok=True, reality_tests=[]),
                events=events,
                accept=is_valid and not parse_errors,
                reject_reason=None if is_valid else "Constraint violations"
            )
            
            result.trace = trace
            result.accept = trace.accept
            result.reject_reason = trace.reject_reason
            result.c2c_time_ms = (time.time() - c2c_start) * 1000
            
            # ========== C3: Meaning ==========
            if trace.accept:
                c3_start = time.time()
                
                meaning = Meaning(
                    trace=trace,
                    payload={
                        "text": text,
                        "wordforms": [self._wordform_to_dict(wf) for wf in wordforms],
                        "links": [self._link_to_dict(link) for link in links],
                    }
                )
                
                result.meaning = meaning
                result.c3_time_ms = (time.time() - c3_start) * 1000
            
            # ========== Statistics ==========
            result.total_time_ms = (time.time() - start_time) * 1000
            
            self.stats.record(result)
            
        except Exception as e:
            result.accept = False
            result.reject_reason = f"Pipeline error: {e}"
            result.exception = e
        
        return result
    
    def _syllables_to_text(self, syllables: List[Syllable]) -> str:
        """تحويل مقاطع لنص"""
        return ''.join(
            seg.text for syl in syllables
            for seg in syl.onset + [syl.nucleus] + syl.coda
        )
    
    def _extract_morph_flags(self, syllables: List[Syllable]) -> Dict[str, Any]:
        """استخراج السمات الصرفية"""
        # TODO: تنفيذ استخراج دقيق
        return {
            'case': 'nominative',
            'definite': False,
            'number': 'singular',
            'gender': 'masculine',
        }
    
    def _wordform_to_dict(self, wf: WordForm) -> Dict:
        """تحويل WordForm لـ dict"""
        return {
            'text': self._syllables_to_text(wf.syllables),
            'kind': wf.word_kind.name,
            'pattern': wf.pattern.name,
        }
    
    def _link_to_dict(self, link: Link) -> Dict:
        """تحويل Link لـ dict"""
        return {
            'rel': link.rel.name,
            'head': link.head,
            'dep': link.dep,
            'confidence': link.confidence,
        }

@dataclass
class ProcessingResult:
    """نتيجة المعالجة الكاملة"""
    # C1
    c1_units: List[Unit] = field(default_factory=list)
    c1_time_ms: float = 0.0
    
    # C2a
    gate_results: List[GateResult] = field(default_factory=list)
    syllables: List[Syllable] = field(default_factory=list)
    c2a_time_ms: float = 0.0
    
    # C2b
    wordforms: List[WordForm] = field(default_factory=list)
    links: List[Link] = field(default_factory=list)
    constraint_violations: List[ConstraintViolation] = field(default_factory=list)
    c2b_time_ms: float = 0.0
    
    # C2c
    trace: Optional[TraceC2] = None
    c2c_time_ms: float = 0.0
    
    # C3
    meaning: Optional[Meaning] = None
    c3_time_ms: float = 0.0
    
    # Decision
    accept: bool = True
    reject_reason: Optional[str] = None
    exception: Optional[Exception] = None
    
    # Total
    total_time_ms: float = 0.0

6.2 اختبار Corpus شامل
Python
# ملف: tests/test_complete_corpus.py

import pytest
from pathlib import Path

class TestCompleteCorpus:
    """
    اختبار شامل على corpus حقيقي
    
    Corpus:
    - 100 آية من القرآن
    - 50 حديث نبوي
    - 50 جملة MSA
    """
    
    @pytest.fixture
    def pipeline(self):
        return CompletePipeline()
    
    @pytest.fixture
    def quran_corpus(self):
        """تحميل آيات قرآنية"""
        corpus_file = Path(__file__).parent / "data" / "quran_100.txt"
        with open(corpus_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    
    @pytest.fixture
    def hadith_corpus(self):
        """تحميل أحاديث"""
        corpus_file = Path(__file__).parent / "data" / "hadith_50.txt"
        with open(corpus_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    
    def test_quran_corpus_processing(self, pipeline, quran_corpus):
        """معالجة 100 آية قرآنية"""
        results = []
        
        for i, ayah in enumerate(quran_corpus, 1):
            result = pipeline.process(ayah, PriorInfo())
            results.append(result)
            
            # تحقق أساسي
            assert result.c1_units, f"Ayah {i}: No C1 units"
            assert result.syllables, f"Ayah {i}: No syllables"
            assert result.wordforms, f"Ayah {i}: No wordforms"
        
        # إحصائيات
        accept_rate = sum(1 for r in results if r.accept) / len(results)
        avg_time = sum(r.total_time_ms for r in results) / len(results)
        
        print(f"\n📊 Quran Corpus Statistics:")
        print(f"  Processed: {len(results)} ayahs")
        print(f"  Accept rate: {accept_rate:.2%}")
        print(f"  Avg time: {avg_time:.2f}ms")
        
        # معيار النجاح
        assert accept_rate >= 0.85, f"Accept rate too low: {accept_rate:.2%}"
        assert avg_time <= 50.0, f"Processing too slow: {avg_time:.2f}ms"
    
    def test_morphology_accuracy(self, pipeline, quran_corpus):
        """دقة التحليل الصرفي"""
        # TODO: يحتاج gold-standard annotations
        pass
    
    def test_syntax_accuracy(self, pipeline, quran_corpus):
        """دقة التحليل النحوي"""
        # TODO: يحتاج gold-standard annotations
        pass

### Evidence, PriorInfo & CLI deliverables
- **SemanticGate evidence composition**: combine `gate_results`, `wordforms`, `links`, and `events` into a single `EvidenceWeight` object with fields `{phonology:30%, morphology:25%, syntax:25%, events:10%, context:10%}`; documented in `docs/SEMANTIC_GATE.md`.
- **PriorInfo shape**: include `expected_register`, `topic`, `conversation_id`, `memory_terms` so `TraceC2` can compare against evidence history; add helper builder `PriorInfo.from_metadata()` and log its values in CLI JSON output.
- **RealityLink & Accept criteria**: each `ProcessingResult` stores `reality_tests` (list of `RealityTest` ids) and sets `accept` only if `evidence.score >= 0.5`, `scope_ok`, `truth_ok`, and `reference_ok` are true.
- **CLI module** (`python -m fvafk.cli`): Accepts `--verbose`, `--json`, `--coq-verify`; prints JSON containing gate decisions, events, links, violations, evidence score, and final accept/reject reason (matches docs/CLI.md sample).
- **Property-based tests**: Hypothesis scenarios for idempotence, preservation, and reversibility; results written to `tests/results/property_{id}.json` for CI tracking.
- **Documentation outputs**: produce `docs/TRACE.md` (trace format), `docs/EVIDENCE.md` (weights & falsifiability), `docs/CLI.md` (CLI schema with sample JSON) as part of week 16 deliverables.

6.3 تحسين الأداء
Python
# ملف: src/fvafk/optimization/caching.py

from functools import lru_cache
from typing import Tuple

class PerformanceOptimizer:
    """
    تحسينات الأداء:
    1. Caching للنتائج المكررة
    2. Batch processing
    3. Parallel processing (optional)
    """
    
    @staticmethod
    @lru_cache(maxsize=10000)
    def cached_syllabify(units_tuple: Tuple[Unit, ...]) -> Tuple[Syllable, ...]:
        """تقطيع لمقاطع مع cache"""
        # تحويل tuple → list
        units = list(units_tuple)
        
        # تقطيع
        syllables = Syllabifier().syllabify(units)
        
        # تحويل list → tuple (للـ cache)
        return tuple(syllables) if syllables else ()
    
    @staticmethod
    @lru_cache(maxsize=5000)
    def cached_pattern_analysis(syllables_tuple: Tuple[Syllable, ...]) -> Optional[PatternKind]:
        """تحليل وزن مع cache"""
        syllables = list(syllables_tuple)
        return PatternAnalyzer().analyze(syllables)
    
    @staticmethod
    def batch_process(pipeline: CompletePipeline, 
                     texts: List[str],
                     batch_size: int = 32) -> List[ProcessingResult]:
        """معالجة دفعات (batch)"""
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            
            for text in batch:
                result = pipeline.process(text, PriorInfo())
                results.append(result)
        
        return results

المخرجات للمرحلة 6:
 src/fvafk/pipeline/complete_pipeline.py + 10 اختبار
 tests/test_complete_corpus.py (100 آية + 50 حديث)
 src/fvafk/optimization/caching.py + 5 اختبارات
 docs/PERFORMANCE_REPORT.md (تقرير الأداء)
 docs/ACCURACY_REPORT.md (تقرير الدقة)
 examples/complete_demo.py (demo شامل)
معيار النجاح:
Code
✅ معالجة 1000 كلمة في <1 ثانية
✅ معدل القبول ≥ 85% على corpus
✅ دقة صرفية ≥ 85% (F1-score)
✅ دقة نحوية ≥ 80% (UAS)
✅ استهلاك ذاكرة <500MB لـ1000 جملة

<a name="timeline"></a>
📅 جدول التنفيذ الكامل (16 أسبوع)
Code
Week 1-2:   المرحلة 1 - البنية التحتية
            ├─ Segment inventory (30 صامتاً)
            ├─ Syllable system (6 أنواع)
            └─ Gate framework

Week 3-5:   المرحلة 2 - البوابات الصوتية
            ├─ Week 3: 4 بوابات أساسية
            ├─ Week 4: 3 بوابات متقدمة
            └─ Week 5: 3 بوابات وقف/حذف

Week 6-8:   المرحلة 3 - المحلل الصرفي
            ├─ Word boundary detection
            ├─ Pattern analysis
            ├─ Word classification
            └─ Root extraction

Week 9-11:  المرحلة 4 - المحلل النحوي
            ├─ ISNADI links (إسنادي)
            ├─ TADMINI links (تضميني)
            └─ TAQYIDI links (تقييدي)

Week 12-13: المرحلة 5 - القيود النحوية
            ├─ 5 قيود مُطبقة بالكامل
            └─ Constraint validator

Week 14-16: المرحلة 6 - التكامل والتحسين
            ├─ Complete pipeline
            ├─ Corpus testing
            ├─ Performance optimization
            └─ Documentation

📊 ملخص المخرجات النهائية
YAML
الكود:
  Python: ~15,000 أسطر
    - src/fvafk/c1/: 500 سطر
    - src/fvafk/c2a/: 4,000 سطر (10 بوابات)
    - src/fvafk/c2b/: 8,000 سطر (صرف + نحو + قيود)
    - src/fvafk/c2c/: 1,000 سطر
    - src/fvafk/pipeline/: 1,500 سطر
  
  Coq: ~3,000 سطر
    - 50 مبرهنة جديدة
    - جميعها مُثبتة (Qed)

الاختبارات:
  - 300+ اختبار وحدة
  - 50 اختبار تكامل
  - 20 اختبار property-based
  - Corpus: 100 آية + 50 حديث + 50 MSA

التوثيق:
  - 50,000+ كلمة
  - 10 ملفات markdown
  - تغطية 100%

الأداء:
  - معالجة: 1000 كلمة/ثانية
  - دقة صرفية: 85%+
  - دقة نحوية: 80%+
  - استهلاك ذاكرة: <500MB


1. إضافة C2c Layer كمرحلة منفصلة
Python
المرحلة 2.5: C2c - Semantic Gates (Week 5.5-6.5)

الأهداف:
  - Evidence model: 5 مصادر (linguistic 30%, logic 30%, world 20%, memory 15%, bias 5%)
  - Falsifiability protocol: كل Meaning لديه List[FailureTest]
  - Reality link: فصل truth/reference/reality
  - Accept threshold: evidence.score >= 0.5 AND scope_ok AND truth_ok AND reference_ok

المكونات:
  - EvidenceWeight: حساب الأوزان
  - FalsifiabilityProtocol: بروتوكول الاختبار
  - RealityLink: truth_ok, reference_ok, reality_tests
  - SemanticGate: القرار النهائي

معايير النجاح:
  ✅ 30+ اختبار يمر
  ✅ دقة قرار القبول/الرفض ≥ 90%
  ✅ معدل false positives ≤ 5%

2. إضافة OrthographyAdapter في المرحلة 1
Python
المرحلة 1: البنية التحتية (محدّثة)

إضافة:
  - OrthographyAdapter: تحويل مكتوب→منطوق
    - همزة الوصل: ٱ → ا مع kasra
    - تاء مربوطة: ة → ت/ه حسب السياق
    - ألف مقصورة: ى → ي
    - تنوين: ـٌ ـٍ ـً → نون ساكنة في الوقف
    - يوجد داخل `src/fvafk/orthography_adapter.py` باعتباره وحدة عامة ضمن `fvafk`

3. إضافة Amil-Sign Rules في المرحلة 5
Python
المرحلة 5: القيود النحوية (محدّثة)

إضافة قيد سادس:
  6. Amil-Sign Rules (AملSignConstraint)
     - لا إعراب بدون عامل (no i3rab without operator)
     - لا عامل بدون رابط (no operator without link)

4. إضافة Event Extraction
Python
المرحلة 4: المحلل النحوي (محدّثة)

إضافة مكون:
  - EventExtractor: استخراج الأحداث من الأفعال
    - تحديد نوع الحدث (past, present, future)
    - تحديد المشاركين (participants)
    - تحديد الزمن والمكان

### Event Extraction Schema
| Field | Description | Source Signals | Evaluation |
| --- | --- | --- | --- |
| `event_type` | Temporal classification (past/present/future) | Verb pattern (mood/tense), time particles (سوف، قد) | Accuracy vs. annotated 1000+ sentences |
| `participants` | Subject/object roles associated with event | ISNADI/TADMINI links, case markers, pronoun resolution | F1 for participant extraction ≥ 0.80 |
| `time_ref` | Temporal anchoring phrase | Prepositional/time adverbs + orthography adapter output | Precision on annotated clause boundaries |
| `place_ref` | Locative phrase or prepositional object | TAQYIDI links + prepositions | Recall on location mentions ≥ 0.75 |
| `certainty` | Evidence level (Epistemic state) | SemanticGate evidence weights | Matches QA requirements in C2c |

Events feed the constraint validator and SemanticGate decision layers; align the schema with `tests/test_complete_corpus.py` or new event-annotated corpus slices.

5. إضافة CLI في المرحلة 6
Python
المرحلة 6: التكامل (محدّثة)

إضافة:
  - CLI Module: python -m fvafk.cli
    - معالجة من سطر الأوامر
    - خيارات: --verbose, --json, --coq-verify
    - إخراج منسق

6. إضافة Property-Based Tests
Python
المرحلة 6: التكامل (محدّثة)

إضافة:
  - Property tests (Hypothesis):
    - Idempotence: process(process(x)) == process(x)
    - Preservation: well-formed(x) → well-formed(process(x))
    - Reversibility: decode(encode(x)) == x

7. إضافة Documentation Files
Python
المرحلة 6: التكامل (محدّثة)

إضافة ملفات:
  - docs/SPEC.md: Type system, constraints, formal semantics
  - docs/ARCHITECTURE.md: Layer separation rationale
  - docs/GATES.md: All gates with pre/post conditions
  - docs/FAILABILITY.md: Falsifiability protocol
  - docs/EXAMPLES.md: 7 examples with processing traces
  - docs/EVALUATION_UPDATED_2026.md: Metrics and progress

📊 الجدول الزمني المحدّث
Code
Week 1-2:     المرحلة 1 - البنية التحتية + OrthographyAdapter
Week 3-5:     المرحلة 2 - البوابات الصوتية (10)
Week 5.5-6.5: المرحلة 2.5 - C2c Semantic Gates (جديد)
Week 6.5-8:   المرحلة 3 - المحلل الصرفي + Affix identification
Week 9-11:    المرحلة 4 - المحلل النحوي + Event extraction
Week 12-13:   المرحلة 5 - القيود النحوية (6 قيود)
Week 14-17:   المرحلة 6 - التكامل + CLI + Property tests + Docs

الإجمالي: 17 أسبوعاً (بدلاً من 16)



