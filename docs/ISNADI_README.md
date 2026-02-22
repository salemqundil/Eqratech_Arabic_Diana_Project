# ISNADI Linker - مبتدأ/خبر Detection

**Version:** 1.0.0  
**Author:** Hussein Hiyassat  
**Date:** 2025-02-13

---

## 📖 Overview

The ISNADI Linker identifies **nominal sentences** (الجملة الاسمية) and creates syntactic links between **مبتدأ** (subject) and **خبر** (predicate).

---

## 🎯 What is ISNADI?

**ISNADI** (إسنادي) is one of the three fundamental syntactic relations in Arabic:

```
1. ISNADI (إسنادي)   - Predication: مبتدأ ← خبر
2. TADMINI (تضميني)  - Valency: فعل ← فاعل/مفعول
3. TAQYIDI (تقييدي)  - Modification: موصوف ← صفة
```

This implementation focuses on **ISNADI**.

---

## 🔍 Detection Rules

### مبتدأ (Subject) must be:
- ✅ Noun (اسم)
- ✅ Nominative case (مرفوع)
- ✅ Usually definite (معرفة) - optional
- ✅ At beginning of sentence

### خبر (Predicate) must be:
- ✅ Noun or adjective
- ✅ Nominative case (مرفوع)
- ✅ Agrees with مبتدأ in number and gender

---

## 🚀 Quick Start

### Basic Usage

```python
from fvafk.c2b.word_form import WordForm, PartOfSpeech, Case, Span, Number
from fvafk.syntax.linkers import IsnadiLinker

# Example: الكتابُ مفيدٌ (The book is useful)
words = [
    WordForm(
        word_id=0,
        surface='الْكِتَابُ',
        span=Span(0, 10),
        pos=PartOfSpeech.NOUN,
        case=Case.NOMINATIVE,
        definiteness=True,
        number=Number.SINGULAR
    ),
    WordForm(
        word_id=1,
        surface='مُفِيدٌ',
        span=Span(11, 17),
        pos=PartOfSpeech.NOUN,
        case=Case.NOMINATIVE,
        number=Number.SINGULAR
    )
]

# Detect ISNADI links
linker = IsnadiLinker()
links = linker.find_links(words)

# Result
for link in links:
    print(link)
    # Output: Link(إسنادي: 0 ← 1)
    print(f"Confidence: {link.confidence}")
    print(f"Reason: {link.reason}")
```

---

## 📚 Examples

### Example 1: Simple Nominal Sentence
```python
# الكتابُ مفيدٌ
# The book is useful

words = [mubtada, khabar]
links = linker.find_links(words)
# → 1 ISNADI link
```

### Example 2: Feminine Agreement
```python
# الطالبةُ مجتهدةٌ
# The student (f) is diligent

# Both words feminine → high confidence
```

### Example 3: Dual Number
```python
# الطالبانِ مجتهدانِ
# The two students are diligent

# Both words dual → agreement detected
```

### Example 4: Plural
```python
# الطلابُ مجتهدونَ
# The students are diligent

# Both words plural → agreement detected
```

---

## ⚙️ Configuration

### Require Definiteness

```python
# Strict mode: مبتدأ must be definite
strict_linker = IsnadiLinker(require_definiteness=True)

# Lenient mode: allow indefinite مبتدأ (default)
lenient_linker = IsnadiLinker(require_definiteness=False)
```

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
pytest tests/syntax/test_isnadi_linker.py -v
```

### Test Coverage

- ✅ Simple nominal sentences
- ✅ Feminine agreement
- ✅ Dual number agreement
- ✅ Plural number agreement
- ✅ Case mismatch detection
- ✅ Number mismatch detection
- ✅ Indefinite مبتدأ handling

---

## 📊 Confidence Scoring

The linker calculates confidence based on:

| Feature | Impact | Weight |
|---------|--------|--------|
| Case agreement (both مرفوع) | High | Base |
| Number agreement | Medium | ×0.7 if mismatch |
| Gender agreement | Medium | ×0.7 if mismatch |
| Definite مبتدأ | Bonus | ×1.1 |

---

## 🔗 Link Structure

Each detected relation returns a `Link` object:

```python
Link(
    link_type=LinkType.ISNADI,     # إسنادي
    head_id=0,                      # مبتدأ (الكتاب)
    dependent_id=1,                 # خبر (مفيد)
    confidence=0.95,                # 0.0 to 1.0
    reason="case, number, gender agreement"
)
```

---

## 📝 API Reference

### IsnadiLinker

```python
class IsnadiLinker:
    def __init__(self, require_definiteness: bool = False)
    
    def find_links(self, words: List[WordForm]) -> List[Link]
```

### Convenience Function

```python
def find_isnadi_links(words: List[WordForm]) -> List[Link]
```

---

## 🎯 Integration Example

```python
# Full pipeline: C2B → WordForm → ISNADI
from fvafk.cli import run_pipeline
from fvafk.c2b.word_form_builder import build_word_forms
from fvafk.syntax.linkers import find_isnadi_links

# 1. Run C2B
c2b_output = run_pipeline("الكتاب مفيد")

# 2. Convert to WordForms
word_forms = build_word_forms(c2b_output['words'])

# 3. Find ISNADI links
links = find_isnadi_links(word_forms)

# 4. Display results
for link in links:
    mubtada = word_forms[link.head_id]
    khabar = word_forms[link.dependent_id]
    print(f"{mubtada.surface} (مبتدأ) ← {khabar.surface} (خبر)")
```

---

## 🚧 Limitations

### Current Version:
- ✅ Simple nominal sentences (مبتدأ + خبر)
- ✅ Single-word خبر only
- ❌ خبر جملة (sentence as predicate) - not yet
- ❌ خبر شبه جملة (prepositional phrase) - not yet
- ❌ Multi-word مبتدأ - not yet

### Future Enhancements:
- Support for خبر جملة
- Support for خبر شبه جملة  
- Handle كان and sisters
- Handle إن and sisters

---

## 🎓 Linguistic Background

### الجملة الاسمية (Nominal Sentence)

In Arabic grammar, a nominal sentence consists of:

1. **المبتدأ** - The subject (what you're talking about)
2. **الخبر** - The predicate (what you're saying about it)

**Examples:**
```
الكتابُ مفيدٌ        The book is useful
الطالبُ مجتهدٌ      The student is diligent  
السماءُ صافيةٌ       The sky is clear
```

Both must be in nominative case (مرفوع) and agree in number and gender.

---

## 🔬 Next Steps

After ISNADI:
1. **TADMINI Linker** - فعل/فاعل/مفعول relations
2. **TAQYIDI Linker** - موصوف/صفة relations
3. **Complete Syntax Tree** - Full sentence structure

---

## 📄 Files

```
src/fvafk/syntax/
├── __init__.py
└── linkers/
    ├── __init__.py
    ├── link.py                    # Link class
    ├── isnadi_linker.py          # ISNADI implementation
    └── test_isnadi_linker.py     # Tests (in tests/syntax/)
```

---

## ✨ Credits

**Author:** Hussein Hiyassat  
**Project:** FVAFK (Fractal Vowel-Aware Form Kit)  
**Date:** February 2025

---

**🎉 Ready to detect مبتدأ and خبر!**
