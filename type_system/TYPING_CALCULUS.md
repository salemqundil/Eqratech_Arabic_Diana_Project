# نظام الأنواع الرسمي | Formal Typing Calculus
## للمحرك اللغوي العربي مع قوانين قاطعة

**الهدف:** تحويل القوانين اللغوية إلى قواعد استنتاج (Inference rules) قابلة للبرهنة آليًا.

---

## 0) أساسيات النظام

### البيئة Γ (Context)

```
Γ = typing environment mapping nodes to types
Γ ⊢ e : T     "في البيئة Γ، التعبير e له النوع T"
```

### الأنواع الأساسية (Base Types)

```
T ::= TokenNode
    | RootNode(RootKind)
    | Ma3aniToolNode
    | MabniRefNode
    | PatternGateNode
    | ScopeOperator
    | RefNode
    | SubjectTerm
    | PredicateTerm
    | ConstraintTerm
```

### أنواع الجذور (Root Kinds)

```
RootKind ::= GenderRoot      (جامد/اسم جنس)
           | EventRoot       (فعل/حدث)
           | QualityRoot     (صفة)
```

### القدرات (Capabilities)

```
Cap ::= CanWriteSubject
      | CanWritePredicate
      | CanProduceScope
      | CanProduceConstraint
      | CanProduceRef
      | CanInstantiateRoot
```

---

## 1) قواعد التصنيف الأساسية (Typing Rules)

### [T-TOKEN] تصنيف Token

```
surface ∈ Surface
tags ∈ Tags
─────────────────────────────────
Γ ⊢ Token(surface, tags) : TokenNode
```

### [T-ROOT] تصنيف الجذر

```
radicals = [r₁, r₂, r₃]
kind ∈ {GenderRoot, EventRoot, QualityRoot}
─────────────────────────────────────────────
Γ ⊢ Root(radicals, kind) : RootNode(kind)
```

### [T-MA3ANI-TOOL] تصنيف أداة المعاني

```
tool_class ∈ {NEG, COND, EXCEPT, ONLY, EMPHASIS, ...}
surface ∈ Ma3aniSurfaces
───────────────────────────────────────────────────────
Γ ⊢ Ma3aniTool(tool_class) : Ma3aniToolNode
```

### [T-MABNI-REF] تصنيف المبني الإحالي

```
ref_type ∈ {PRONOUN, DEMONSTRATIVE, RELATIVE}
─────────────────────────────────────────────
Γ ⊢ MabniRef(ref_type) : MabniRefNode
```

---

## 2) قواعد القدرات (Capability Rules)

### [CAP-MA3ANI] قدرات أدوات المعاني

```
Γ ⊢ n : Ma3aniToolNode
────────────────────────────────────────────────
Γ ⊢ n : CanProduceScope
Γ ⊢ n : CanProduceConstraint
Γ ⊬ n : CanWriteSubject      (ممنوع!)
Γ ⊬ n : CanWritePredicate    (ممنوع!)
```

**هذا القانون القاطع 5.1**

### [CAP-MABNI] قدرات المبنيات

```
Γ ⊢ n : MabniRefNode
─────────────────────────────────────────────
Γ ⊢ n : CanProduceRef
Γ ⊬ n : CanInstantiateRoot     (ممنوع!)
Γ ⊬ n : CanInstantiateQuality  (ممنوع!)
```

**هذا القانون القاطع 5.2**

### [CAP-ROOT] قدرات الجذور

```
Γ ⊢ n : RootNode(kind)
kind ∈ {GenderRoot, EventRoot}
────────────────────────────────
Γ ⊢ n : CanWriteSubject
```

```
Γ ⊢ n : RootNode(EventRoot)
───────────────────────────────
Γ ⊢ n : CanWritePredicate
```

```
Γ ⊢ n : RootNode(QualityRoot)
───────────────────────────────────
Γ ⊢ n : CanModify
Γ ⊬ n : CanWriteSubject (إلا عبر Gate)
```

---

## 3) قواعد البناء الدلالي (Semantic Construction Rules)

### [BUILD-SUBJECT] بناء المسند إليه

```
Γ ⊢ n : CanWriteSubject
Γ ⊢ term : SubjectTerm
─────────────────────────────────
Γ ⊢ J.subject ← n.produce(term) : Valid
```

```
Γ ⊢ n : Ma3aniToolNode
Γ ⊬ n : CanWriteSubject
─────────────────────────────────
Γ ⊢ J.subject ← n.produce(_) : ⟂ (Type Error!)
```

### [BUILD-PREDICATE] بناء المسند

```
Γ ⊢ n : CanWritePredicate
Γ ⊢ term : PredicateTerm
─────────────────────────────────
Γ ⊢ J.predicate ← n.produce(term) : Valid
```

```
Γ ⊢ n : Ma3aniToolNode
Γ ⊬ n : CanWritePredicate
─────────────────────────────────
Γ ⊢ J.predicate ← n.produce(_) : ⟂ (Type Error!)
```

### [BUILD-SCOPE] بناء النطاق

```
Γ ⊢ n : CanProduceScope
Γ ⊢ op : ScopeOperator
─────────────────────────────────
Γ ⊢ J.scope ← n.produce(op) : Valid
```

### [BUILD-CONSTRAINT] بناء القيد

```
Γ ⊢ n : CanProduceConstraint
Γ ⊢ c : ConstraintTerm
─────────────────────────────────
Γ ⊢ J.constraints ← n.add(c) : Valid
```

### [BUILD-REF] بناء المرجع

```
Γ ⊢ n : MabniRefNode
Γ ⊢ n : CanProduceRef
─────────────────────────────────
Γ ⊢ Ref(n) : RefNode
```

```
Γ ⊢ n : MabniRefNode
Γ ⊬ n : CanInstantiateRoot
─────────────────────────────────
Γ ⊢ Root(n) : ⟂ (Type Error!)
```

---

## 4) قواعد البوابات (Gate Rules)

### [GATE-PATTERN] بوابة الوزن

```
Γ ⊢ r : RootNode(kind)
Γ ⊢ p : PatternGate
compatible(kind, p.target_kind)
────────────────────────────────────
Γ ⊢ apply(p, r) : Stem(p.sem_sig)
```

### [GATE-DERIVE] بوابة الاشتقاق (تحويل نوع الجذر)

```
Γ ⊢ r : RootNode(GenderRoot)
Γ ⊢ gate : DeriveToQualityGate
───────────────────────────────────────────
Γ ⊢ apply(gate, r) : RootNode(QualityRoot)
+ trace(derivation)
```

**بدون Gate، لا يسمح:**

```
Γ ⊢ r : RootNode(GenderRoot)
Γ ⊬ gate : DeriveGate
───────────────────────────────────
Γ ⊢ treat_as(r, QualityRoot) : ⟂ (Violation!)
```

### [GATE-MA3ANI-SCOPE] بوابة أداة المعاني → Scope

```
Γ ⊢ m : Ma3aniToolNode
Γ ⊢ m.tool_class = COND
────────────────────────────────────
Γ ⊢ apply(Ma3aniScopeGate, m) : ScopeOperator(IF_THEN)
```

### [GATE-MABNI-REF] بوابة المبني → Ref

```
Γ ⊢ mb : MabniRefNode
────────────────────────────────────
Γ ⊢ apply(MabniRefGate, mb) : RefNode
+ edges(COREFERS | RESTRICTED_BY)
```

---

## 5) قواعد الحواف (Edge Rules)

### [EDGE-MODIFIES] حافة التعديل (صفة → موصوف)

```
Γ ⊢ adj : RootNode(QualityRoot)
Γ ⊢ noun : RootNode(GenderRoot)
syntax_adjacent(adj, noun)
────────────────────────────────────
Γ ⊢ MODIFIES(adj, noun) : Valid
+ sem_constraint: Restrictor(adj) applied_to Ref(noun)
```

### [EDGE-GOVERNS] حافة العمل (عامل → معمول)

```
Γ ⊢ gov : Operator
Γ ⊢ dep : Term
gov.arity includes dep.role
────────────────────────────────────
Γ ⊢ GOVERNS(gov, dep) : Valid
```

### [EDGE-COREFERS] حافة الإحالة

```
Γ ⊢ ref : RefNode
Γ ⊢ ante : RootNode | RefNode
binding_domain(ref, ante)
────────────────────────────────────
Γ ⊢ COREFERS(ref, ante) : Valid
```

---

## 6) قوانين الحفظ (Invariant Preservation)

### [INV-MA3ANI] حفظ قانون أدوات المعاني

```
∀ step in derivation:
  if Γ ⊢ n : Ma3aniToolNode
  then ∀ writes in step:
    writes ∉ {J.subject, J.predicate}
────────────────────────────────────
derivation is sound
```

إذا خُرق: `⟂` (Proof fails)

### [INV-MABNI] حفظ قانون المبنيات

```
∀ step in derivation:
  if Γ ⊢ n : MabniRefNode
  then ∀ instantiations in step:
    instantiation.type ≠ RootNode
    instantiation.type ≠ QualityRoot
────────────────────────────────────
derivation is sound
```

إذا خُرق: `⟂` (Proof fails)

### [INV-DERIVE] حفظ قانون الاشتقاق

```
∀ step in derivation:
  if change(r.kind from K₁ to K₂):
    ∃ gate in step: gate.type = DerivationGate
    + trace(gate_application)
────────────────────────────────────
derivation is sound
```

---

## 7) نظرية الصحة (Soundness Theorem)

**نظرية:**

إذا:
1. `Γ ⊢ graph : WellTyped`
2. `∀ gates in derivation: GateCorrect`
3. `INV-MA3ANI + INV-MABNI + INV-DERIVE` محفوظة

إذن:
- `J.subject` يُنتج فقط من عقد لها `CanWriteSubject` ✓
- `J.predicate` يُنتج فقط من عقد لها `CanWritePredicate` ✓
- `Ma3aniToolNode` لا تكتب `Subject/Predicate` أبدًا ✓
- `MabniRefNode` لا تُعامل كـ `Root/Adj` أبدًا ✓
- كل تحويل جذر له `Gate + trace` ✓

**البرهان:** بالاستقراء على steps of derivation.
- Base: الأنواع الأولية صحيحة (من قواعد [T-*])
- Step: كل gate تحفظ الأنواع (من قواعد [GATE-*])
- Invariants: محفوظة في كل خطوة (من قواعد [INV-*])

∎

---

## 8) أمثلة: اشتقاقات صحيحة وفاشلة

### مثال 1: اشتقاق صحيح (من يكذب يعاقب)

```
Step 1:
  Γ ⊢ Token("من") : TokenNode
  Γ ⊢ Ma3aniTool(COND) : Ma3aniToolNode
  [T-MA3ANI-TOOL]

Step 2:
  Γ ⊢ Ma3aniTool : CanProduceScope
  Γ ⊢ apply(Ma3aniScopeGate, Ma3aniTool) : ScopeOp(IF_THEN)
  Γ ⊢ J.scope ← IF_THEN : Valid
  [CAP-MA3ANI, GATE-MA3ANI-SCOPE, BUILD-SCOPE]

Step 3:
  Γ ⊢ Root(["ك","ذ","ب"], EventRoot) : RootNode(EventRoot)
  Γ ⊢ RootNode(EventRoot) : CanWritePredicate
  Γ ⊢ J.predicate ← Root.produce("يكذب") : Valid
  [T-ROOT, CAP-ROOT, BUILD-PREDICATE]

✓ All type checks pass
✓ INV-MA3ANI satisfied (tool did not write subject/predicate)
```

### مثال 2: اشتقاق فاشل (محاولة أداة كتابة Predicate)

```
Step 1:
  Γ ⊢ Ma3aniTool(NEG) : Ma3aniToolNode

Step 2 (محاولة):
  Γ ⊢ Ma3aniTool : Ma3aniToolNode
  Γ ⊬ Ma3aniTool : CanWritePredicate  [CAP-MA3ANI forbids this]
  Γ ⊢ J.predicate ← Ma3aniTool.produce(_) : ⟂

✗ Type error at step 2
✗ Derivation fails
```

### مثال 3: اشتقاق فاشل (محاولة مبني كجذر)

```
Step 1:
  Γ ⊢ MabniRef("هو", PRONOUN) : MabniRefNode

Step 2 (محاولة):
  Γ ⊢ MabniRef : MabniRefNode
  Γ ⊬ MabniRef : CanInstantiateRoot  [CAP-MABNI forbids this]
  Γ ⊢ Root(MabniRef) : ⟂

✗ Type error at step 2
✗ Derivation fails
```

---

## 9) ربط مع نظام Maqam Theory

في Maqam Theory، الطاقة E تحوي:

```
E(x, y) = ∑ HardGates(x, y) + ∑ SoftTerms(x, y)
```

**الربط:**

- HardGates = Type checking rules (إذا فشلت → ∞)
- SoftTerms = Preference scoring

**مثال:**

```python
def HardGate_Ma3ani(y):
    for node in y.nodes:
        if node.type == "Ma3aniToolNode":
            if node.writes_to in ["subject", "predicate"]:
                return ∞  # Type violation
    return 0  # Type check passed

def E(x, y):
    hard_cost = HardGate_Ma3ani(y)
    if hard_cost == ∞:
        return ∞  # Reject immediately
    
    soft_cost = ...  # Continue with soft preferences
    return hard_cost + soft_cost
```

---

## 10) خلاصة النظام

| قانون | صيغة رياضية | Proof obligation |
|-------|-------------|------------------|
| **5.1: أدوات المعاني** | `Γ ⊢ Ma3aniTool : CanProduceScope` <br> `Γ ⊬ Ma3aniTool : CanWrite{Subj,Pred}` | Type check at J construction |
| **5.2: المبنيات** | `Γ ⊢ MabniRef : CanProduceRef` <br> `Γ ⊬ MabniRef : CanInstantiate{Root,Adj}` | Type check at instantiation |
| **الاشتقاق** | `change(Root.kind) ⇒ ∃ DerivationGate` | Trace validation |
| **الصحة** | `WellTyped + GateCorrect ⇒ Invariants` | Induction proof |

**الفائدة:**
- كل قانون = قاعدة نوع (Typing rule)
- كل انتهاك = خطأ نوع (Type error) = `⟂`
- البرهان = نجاح اشتقاق (Successful derivation)
- لا مجال للالتباس أو الاستثناءات الخفية

---

## التالي

الآن سأحول هذه القواعد إلى:
1. **JSON Type Policies** (executable schemas)
2. **Python Implementation** مع type checkers
3. **Graph Schema** مع validators

هل تريد المضي قدمًا في التنفيذ؟
