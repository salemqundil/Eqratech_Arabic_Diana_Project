# نظام الأنواع الرسمي للمحرك اللغوي العربي
# Formal Type System for Arabic NLP Engine

**نظام محكم جامع مانع يحول القوانين اللغوية إلى قيود نوعية + براهين آلية**

---

## المحتويات

1. [نظرة عامة](#نظرة-عامة)
2. [المكونات الرئيسية](#المكونات-الرئيسية)
3. [القوانين القاطعة](#القوانين-القاطعة)
4. [الملفات](#الملفات)
5. [الاستخدام](#الاستخدام)
6. [الأمثلة](#الأمثلة)
7. [التكامل مع Maqam Theory](#التكامل-مع-maqam-theory)

---

## نظرة عامة

هذا النظام يوفر **إطار عمل رياضي صارم** لبناء المحركات اللغوية العربية مع ضمانات نوعية (Type safety) تمنع الأخطاء الشائعة:

### المشكلة

في المحركات اللغوية التقليدية:
- أدوات المعاني (من، لا، إلا...) قد تُعامل خطأً كـ "اسم" أو "فعل"
- المبنيات (هو، الذي...) قد تُعامل خطأً كـ "جذر" أو "صفة"
- تغيير نوع الجذر (جامد → صفة) بدون توثيق
- اختلاط بين "اللغة" و"المعرفة" و"العالم"

### الحل

نظام أنواع رسمي يحول القوانين اللغوية إلى:
1. **قواعد استنتاج رياضية** (Typing rules) - المواصفة
2. **سياسات JSON قابلة للتنفيذ** (Type policies) - التخصيص
3. **فاحصات Python آلية** (Type checkers) - التطبيق

**النتيجة:** أي انتهاك للقوانين = خطأ نوع (Type error) = ∞ cost = رفض تلقائي

---

## المكونات الرئيسية

### 1) الفضاءات (Spaces)

```
S₀: PhonoSpace     → فونيمات + حركات
S₁: SyllableSpace  → مقاطع + أوزان
S₂: MorphSpace     → جذر + وزن + جامد/مشتق
S₃: SyntaxSpace    → علاقات نحوية + عوامل
S₄: IrabSpace      → إعراب/بناء
S₅: SemSpace       → حكم J = (Subject, Predicate, Constraints, Scope)
S₆: EpistemicSpace → تصنيف (عقلي/سمعي/واقعي)
```

**قاعدة الفصل:** `S₅ ≠ S₆` → اللغة تُنتج J، العقل يُقيّمه

### 2) أنواع العقد (Node Types)

| نوع العقدة | القدرات | الممنوعات |
|-----------|---------|-----------|
| `RootNode(GenderRoot)` | `CAN_WRITE_SUBJECT` | `CAN_WRITE_PREDICATE` (إلا عبر Gate) |
| `RootNode(EventRoot)` | `CAN_WRITE_SUBJECT`, `CAN_WRITE_PREDICATE` | - |
| `RootNode(QualityRoot)` | `CAN_MODIFY` | `CAN_WRITE_SUBJECT` (إلا عبر Gate) |
| `Ma3aniToolNode` | `CAN_PRODUCE_SCOPE`, `CAN_PRODUCE_CONSTRAINT` | **`CAN_WRITE_SUBJECT`, `CAN_WRITE_PREDICATE`** |
| `MabniRefNode` | `CAN_PRODUCE_REF` | **`CAN_INSTANTIATE_ROOT`, `CAN_INSTANTIATE_QUALITY`** |

### 3) البوابات (Gates)

كل بوابة = تحويل محدد مع proof obligation:

```python
Ma3aniScopeGate: Ma3aniToolNode → ScopeOperatorNode
MabniRefGate:    MabniRefNode → RefNode
DerivationGate:  RootNode(K₁) → RootNode(K₂) + trace
PatternGate:     RootNode + Pattern → Stem + sem_signature
```

### 4) المتجهات (Vectors)

```python
v_phoneme ∈ ℝ^d    # (مخرج/صفة/جهر/تفخيم...)
v_syllable ∈ ℝ^s   # (type/weight/boundary)
v_pattern ∈ ℝ^k    # (semantic signature)
v_root ∈ ℝ^r       # (semantic core)
```

**قاعدة:** المتجه يدعم القيود، لا يقرر وحده

---

## القوانين القاطعة

### القانون 5.1: أدوات المعاني

```
∀ node ∈ nodes:
  if node.type = Ma3aniToolNode
  then ∀ writes:
    writes ∉ {J.subject, J.predicate}
```

**المعنى:** أدوات المعاني (من، لا، إلا...) **لا تكتب Subject أو Predicate**، فقط Scope و Constraints

**التطبيق:**
```python
if isinstance(node, Ma3aniToolNode):
    if node.writes_to in ["subject", "predicate"]:
        return ∞  # Type violation → Reject
```

**مثال:**
- ✓ من → ScopeOp(IF_THEN)
- ✗ من → Subject (Type Error!)

### القانون 5.2: المبنيات

```
∀ node ∈ nodes:
  if node.type = MabniRefNode
  then ∀ instantiations:
    instantiation.type ∉ {RootNode, QualityRoot}
```

**المعنى:** المبنيات (هو، الذي...) **لا تُعامل كجذر أو صفة**، فقط كـ Ref

**التطبيق:**
```python
if isinstance(node, MabniRefNode):
    if node.instantiation_type in ["Root", "Quality"]:
        return ∞  # Type violation → Reject
```

**مثال:**
- ✓ هو → RefNode (via MabniRefGate)
- ✗ هو → RootNode (Type Error!)

### القانون 5.3: الاشتقاق

```
∀ step:
  if change(root.kind from K₁ to K₂)
  then ∃ gate: gate.type = DerivationGate ∧ trace recorded
```

**المعنى:** تغيير نوع الجذر **يتطلب Gate + trace**

**مثال:**
- ✓ GenderRoot → QualityRoot (via DerivationGate)
- ✗ Direct kind change (Type Error!)

---

## الملفات

```
type_system/
├── TYPING_CALCULUS.md        # قواعد الاستنتاج الرياضية
├── type_policies.json         # سياسات JSON القابلة للتنفيذ
├── graph_schema.json          # مخطط الرسم الموحّد
├── type_system.py             # نظام الأنواع (Python)
├── validators.py              # فاحصات القوانين القاطعة
├── example_complete.py        # مثال: "من يكذب يعاقب"
├── man_yakdhib_yuaqab.json    # نتيجة المثال
└── README.md                  # هذا الملف
```

### الحجم الإجمالي

- **TYPING_CALCULUS.md**: 730 سطر (قواعد رياضية + براهين)
- **type_policies.json**: 550 سطر (سياسات قابلة للتنفيذ)
- **graph_schema.json**: 420 سطر (مخطط موحّد)
- **type_system.py**: 570 سطر (تطبيق Python)
- **validators.py**: 520 سطر (فاحصات آلية)
- **example_complete.py**: 450 سطر (مثال كامل)

**المجموع:** ~3,240 سطر من المواصفات والكود

---

## الاستخدام

### 1) بناء رسم بسيط

```python
from type_system import (
    Ma3aniToolNode, Ma3aniToolClass,
    Ma3aniScopeGate, TypeChecker,
    LinguisticJudgment
)

# Create nodes
ma3ani = Ma3aniToolNode(id="m1", tool_class=Ma3aniToolClass.NEG)

# Apply gate
gate = Ma3aniScopeGate()
scope_op = gate.apply(ma3ani)

# Build judgment
checker = TypeChecker()
J = LinguisticJudgment()

checker.register_node(ma3ani)
checker.register_node(scope_op)
checker.check_produce_scope(ma3ani, J, scope_op.id)

print(J)  # J(subj=None, pred=None, scope=1, constr=0)
```

### 2) فحص القوانين القاطعة

```python
from validators import GraphValidator

graph_data = {
    "nodes": [...],
    "edges": [...],
    "judgment": {...},
    "traces": [...]
}

validator = GraphValidator()
report = validator.validate_graph(graph_data)

if report.has_fatal_violations():
    print("✗ Graph rejected (type violations)")
    for v in report.violations:
        print(f"  {v}")
else:
    print("✓ Graph accepted (all type checks passed)")
```

### 3) حساب الطاقة

```python
from validators import compute_hard_gate_cost

# Hard gates (type checking)
hard_cost = compute_hard_gate_cost(graph_data)

if hard_cost == float('inf'):
    print("Candidate rejected (type violation)")
else:
    # Add soft terms
    soft_cost = compute_soft_penalties(graph_data)
    total_cost = hard_cost + soft_cost
    
    print(f"E(x, y) = {total_cost}")
```

---

## الأمثلة

### مثال 1: "من يكذب يعاقب" (صحيح)

```bash
python3 example_complete.py
```

**النتيجة:**
```
✓ All type checks passed
✓ INV_MA3ANI_5.1: Ma3aniToolNode did not write Subject/Predicate
Energy E(x, y): 1.0
Graph exported to: man_yakdhib_yuaqab.json
```

**البنية:**
```
من (Ma3aniToolNode)
  └─→ Ma3aniScopeGate
      └─→ ScopeOp(IF_THEN)
          └─→ J.scope

يكذب (EventRoot)
  └─→ J.predicate

يعاقب (EventRoot)
  └─→ CONDITION_IMPLIES → يكذب
```

### مثال 2: محاولة فاشلة (Ma3aniTool → Predicate)

```python
# محاولة: "من" تكتب Predicate
checker.check_write_predicate(ma3ani, J)

# النتيجة:
# TypeViolation: [INV_MA3ANI_5.1] Ma3aniToolNode cannot write Predicate
# Cost: ∞ → Rejected
```

### مثال 3: محاولة فاشلة (MabniRef → Root)

```python
# محاولة: "هو" كجذر
mabni = MabniRefNode(id="mb1", ref_type=RefType.PRONOUN)
checker.check_instantiate_root(mabni)

# النتيجة:
# TypeViolation: [INV_MABNI_5.2] MabniRefNode cannot be instantiated as Root
# Cost: ∞ → Rejected
```

---

## التكامل مع Maqam Theory

### دالة الطاقة

```
E(x, y) = ∑ HardGates(x, y) + ∑ SoftTerms(x, y)
```

حيث:
- **HardGates** = Type checking (إذا فشل → ∞)
- **SoftTerms** = Preference scoring (penalties محددة)

### التطبيق

```python
def E(x, y):
    # Hard gates (type checking)
    hard_cost = 0.0
    
    # قانون 5.1
    if Ma3aniToolNode_writes_Subject_or_Predicate(y):
        return ∞
    
    # قانون 5.2
    if MabniRefNode_instantiated_as_Root(y):
        return ∞
    
    # قانون 5.3
    if root_kind_change_without_gate(y):
        return ∞
    
    # Soft terms
    soft_cost = compute_soft_penalties(y)
    
    return hard_cost + soft_cost
```

### argmin مع Type Safety

```python
Y_admiss = {y : all type checks pass}
y⋆ = argmin_{y ∈ Y_admiss} E(x, y)
```

**الفائدة:** argmin يختار فقط من candidates صحيحة نوعيًا

---

## نظرية الصحة

**نظرية:**

إذا:
1. `Γ ⊢ graph : WellTyped`
2. `∀ gates in derivation: GateCorrect`
3. `INV-MA3ANI + INV-MABNI + INV-DERIVATION` محفوظة

إذن:
- ✓ `J.subject` يُنتج فقط من عقد لها `CanWriteSubject`
- ✓ `J.predicate` يُنتج فقط من عقد لها `CanWritePredicate`
- ✓ `Ma3aniToolNode` لا تكتب `Subject/Predicate` أبدًا
- ✓ `MabniRefNode` لا تُعامل كـ `Root/Adj` أبدًا
- ✓ كل تحويل جذر له `Gate + trace`

**البرهان:** بالاستقراء على steps of derivation (انظر TYPING_CALCULUS.md)

---

## خريطة المفاهيم

```
Typing Calculus (رياضي)
    ↓ تحويل
Type Policies (JSON)
    ↓ تطبيق
Type System (Python)
    ↓ فحص
Validators (آلي)
    ↓ استخدام
Graph + J (output)
    ↓ تقييم
Energy E(x, y)
    ↓ اختيار
argmin → y⋆
```

---

## الخلاصة

هذا النظام يوفر:

1. **مواصفة رياضية** (Typing Calculus)
2. **سياسات قابلة للتنفيذ** (JSON schemas)
3. **فاحصات آلية** (Python validators)
4. **أمثلة كاملة** (من يكذب يعاقب)
5. **تكامل مع Maqam Theory** (E(x, y) مع type safety)

**النتيجة:**
- لا مجال للالتباس أو الاستثناءات الخفية
- كل قانون = قاعدة نوع
- كل انتهاك = خطأ نوع = ∞
- البرهان = نجاح اشتقاق

---

## المراجع

- [TYPING_CALCULUS.md](TYPING_CALCULUS.md) - قواعد الاستنتاج الكاملة
- [type_policies.json](type_policies.json) - السياسات القابلة للتنفيذ
- [graph_schema.json](graph_schema.json) - المخطط الموحّد
- [type_system.py](type_system.py) - التطبيق Python
- [validators.py](validators.py) - الفاحصات الآلية
- [example_complete.py](example_complete.py) - المثال الكامل

---

**Version:** 1.0.0  
**Date:** 2026-02-04  
**Status:** ✓ Complete & Validated
