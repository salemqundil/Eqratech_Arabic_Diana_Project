# Arabic NLP Engine Hierarchy - Visual Guide

## 🎯 Complete 3-Level Taxonomy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   6-LAYER COMPUTATIONAL LINGUISTICS MODEL                │
│                         (66 Engines Total)                               │
└─────────────────────────────────────────────────────────────────────────┘

🔷 LAYER 1: PHONOLOGY (الصوتيات) - 3 Engines
│
├─ 📦 Group 1.1: Core Phonemes (الفونيمات الأساسية)
│   └─ 1.1.1: Phoneme Inventory (قائمة الفونيمات)
│       ├─ PhonemesEngine
│       └─ SoundEngine
│
└─ 📦 Group 1.2: Modern Sounds (الأصوات المحدثة)
    └─ 1.2.1: Contemporary Phonology (الصوتيات المعاصرة)
        └─ AswatMuhdathaEngine

═══════════════════════════════════════════════════════════════════════════

🔷 LAYER 2: MORPHOLOGY (الصرف) - 22 Engines
│
├─ 📦 Group 2.1: Verbal Morphology (صرف الأفعال)
│   ├─ 2.1.1: Basic Verbs (الأفعال الأساسية)
│   │   ├─ VerbsEngine
│   │   └─ AfaalKhamsaEngine
│   ├─ 2.1.2: Passive Voice (المبني للمجهول)
│   │   └─ MabniMajhoolEngine
│   └─ 2.1.3: Verb Constructions (بناء الأفعال)
│       └─ BinaaEngine
│
├─ 📦 Group 2.2: Participial Forms (صيغ المشاركة)
│   ├─ 2.2.1: Active Participle (اسم الفاعل)
│   │   └─ ActiveParticipleEngine
│   ├─ 2.2.2: Passive Participle (اسم المفعول)
│   │   └─ PassiveParticipleEngine
│   └─ 2.2.3: Intensive Participle (صيغة المبالغة)
│       └─ MubalaghSighaEngine
│
├─ 📦 Group 2.3: Derived Nouns (الأسماء المشتقة)
│   ├─ 2.3.1: Verbal Nouns (المصادر الصناعية)
│   │   └─ MasdarSinaiEngine
│   └─ 2.3.2: Instrumental Nouns (أسماء الآلة)
│       └─ MimiNounsEngine
│
├─ 📦 Group 2.4: Comparative & Superlative (المقارنة والتفضيل)
│   ├─ 2.4.1: Elative Forms (اسم التفضيل)
│   │   └─ SuperlativeEngine
│   ├─ 2.4.2: Adjectives (الصفات)
│   │   └─ AdjectiveEngine
│   └─ 2.4.3: Specific Forms (الصيغ الخاصة)
│       └─ IsmAlaEngine
│
├─ 📦 Group 2.5: Defective Nouns (الأسماء المعتلة)
│   ├─ 2.5.1: Shortened Nouns (الأسماء المقصورة)
│   │   └─ IsmMaqsorEngine
│   ├─ 2.5.2: Deficient Nouns (الأسماء المنقوصة)
│   │   └─ IsmManqusEngine
│   └─ 2.5.3: Extended Nouns (الأسماء الممدودة)
│       └─ IsmMamdodEngine
│
├─ 📦 Group 2.6: Relational Morphology (النسبة والإضافة)
│   └─ 2.6.1: Relative Adjectives (النسبة)
│       └─ NisbaEngine
│
├─ 📦 Group 2.7: Pluralization (الجمع)
│   └─ 2.7.1: Broken Plurals (جمع التكسير)
│       └─ BrokenPluralsEngine (inferred)
│
├─ 📦 Group 2.8: Diminutives & Augmentatives (التصغير والتكبير)
│   └─ 2.8.1: Diminutive Forms (التصغير)
│       └─ DiminutiveEngine (pending)
│
└─ 📦 Group 2.9: Special Nouns (الأسماء الخاصة)
    ├─ 2.9.1: Shape Nouns (أسماء الهيئة)
    │   └─ IsmHayaEngine
    └─ 2.9.2: Instance Nouns (اسم المرة)
        └─ IsmMarraEngine

═══════════════════════════════════════════════════════════════════════════

🔷 LAYER 3: LEXICON (المعجم) - 15 Engines
│
├─ 📦 Group 3.1: Proper Nouns (الأعلام)
│   ├─ 3.1.1: Personal Names (أعلام الأشخاص)
│   │   └─ A3lamAshkhasEngine
│   ├─ 3.1.2: Place Names (أعلام الأماكن)
│   │   └─ A3lamAmakinEngine
│   └─ 3.1.3: Transferred Names (الأعلام المنقولة)
│       └─ A3lamManqulaEngine
│
├─ 📦 Group 3.2: Common Nouns (الأسماء الشائعة)
│   ├─ 3.2.1: Generic Nouns (أسماء الجنس)
│   │   └─ GenericNounsEngine
│   └─ 3.2.2: Place Nouns (أسماء المكان)
│       └─ PlaceEngine
│
├─ 📦 Group 3.3: Number & Gender (العدد والجنس)
│   ├─ 3.3.1: Number Names (أسماء الأعداد)
│   │   └─ AdadNamesEngine
│   └─ 3.3.2: Gender Classification (التذكير والتأنيث)
│       └─ GenderEngine
│
├─ 📦 Group 3.4: Collective & Individual (الجمعي والإفرادي)
│   ├─ 3.4.1: Collective Genus (جنس الجمع)
│   │   └─ JinsJamiiEngine
│   └─ 3.4.2: Individual Genus (جنس الإفراد)
│       └─ JinsIfradiEngine
│
├─ 📦 Group 3.5: Semantic Classes (التصنيفات الدلالية)
│   ├─ 3.5.1: Sentient Beings (الكائنات العاقلة)
│   │   └─ KainatAqilaEngine
│   └─ 3.5.2: Non-Sentient Entities (الكائنات غير العاقلة)
│       └─ KainatGhairAqilaEngine
│
└─ 📦 Group 3.6: Religious & Specialized (الدينية والمتخصصة)
    ├─ 3.6.1: Divine Names (أسماء الله الحسنى)
    │   └─ AsmaAllahEngine
    ├─ 3.6.2: Religious Terminology (المصطلحات الشرعية)
    │   └─ MusatalahatShariaEngine
    └─ 3.6.3: Common Attributes (الصفات الشائعة)
        └─ CommonAttributesEngine

═══════════════════════════════════════════════════════════════════════════

🔷 LAYER 4: SYNTAX (النحو) - 13 Engines
│
├─ 📦 Group 4.1: Core Arguments (الأركان الأساسية)
│   ├─ 4.1.1: Subject (الفاعل)
│   │   └─ FaelEngine
│   ├─ 4.1.2: Object (المفعول به)
│   │   └─ MafoulBihEngine
│   ├─ 4.1.3: Passive Agent (نائب الفاعل)
│   │   └─ NaebFaelEngine
│   └─ 4.1.4: Predicate & Subject (المبتدأ والخبر)
│       └─ MobtadaKhabarEngine
│
├─ 📦 Group 4.2: Adjuncts (المتممات)
│   ├─ 4.2.1: Absolute Object (المفعول المطلق)
│   │   └─ MafoulMutlaqEngine
│   ├─ 4.2.2: Causative Object (المفعول لأجله)
│   │   └─ MafoulAjlihEngine
│   ├─ 4.2.3: Circumstantial (الحال)
│   │   └─ HaalEngine
│   └─ 4.2.4: Specification (التمييز)
│       └─ TamyeezEngine
│
├─ 📦 Group 4.3: Interrogatives (الاستفهام)
│   ├─ 4.3.1: Question Particles (أدوات الاستفهام)
│   │   └─ IstifhamEngine
│   └─ 4.3.2: Response Constructions (الجواب)
│       └─ JawabEngine
│
├─ 📦 Group 4.4: Stylistic Operations (العمليات الأسلوبية)
│   ├─ 4.4.1: Fronting (التقديم)
│   │   └─ TaqdimEngine
│   └─ 4.4.2: Exceptional Subject (اشتغال)
│       └─ IshtighalEngine
│
├─ 📦 Group 4.5: Exclamation & Wonder (التعجب)
│   └─ 4.5.1: Exclamation (التعجب)
│       └─ TaajjubEngine
│
└─ 📦 Group 4.6: Restriction & Limitation (القصر والتخصيص)
    ├─ 4.6.1: Restriction (القصر)
    │   └─ QasrEngine
    └─ 4.6.2: Restriction by Fronting (قصر التقديم)
        └─ QasrTaqdimEngine

═══════════════════════════════════════════════════════════════════════════

🔷 LAYER 5: RHETORIC (البلاغة) - 11 Engines
│
├─ 📦 Group 5.1: Figures of Speech (الأساليب البيانية)
│   ├─ 5.1.1: Simile (التشبيه)
│   │   └─ TashbihEngine
│   ├─ 5.1.2: Metaphor (الاستعارة)
│   │   └─ IstiaraEngine
│   └─ 5.1.3: Metonymy (الكناية)
│       └─ KinayaEngine
│
├─ 📦 Group 5.2: Sound Patterns (الأنماط الصوتية)
│   ├─ 5.2.1: Paronomasia (الجناس)
│   │   └─ JinassEngine
│   └─ 5.2.2: Rhymed Prose (السجع)
│       └─ SajaEngine
│
├─ 📦 Group 5.3: Semantic Relations (العلاقات الدلالية)
│   ├─ 5.3.1: Antithesis (المقابلة)
│   │   └─ MuqabalaEngine
│   └─ 5.3.2: Synonymy & Paraphrase (الترادف والإطناب)
│       └─ ItnabEngine (part of IjazItnabEngine)
│
├─ 📦 Group 5.4: Brevity & Expansion (الإيجاز والإطناب)
│   └─ 5.4.1: Conciseness & Elaboration (الإيجاز والإطناب)
│       └─ IjazItnabEngine
│
└─ 📦 Group 5.5: Advanced Rhetorical Devices (البلاغة المتقدمة)
    └─ 5.5.1: Additional Devices
        └─ (Other rhetoric engines)

═══════════════════════════════════════════════════════════════════════════

🔷 LAYER 6: GENERATION (التوليد) - 3 Engines
│
├─ 📦 Group 6.1: Dynamic Generation (التوليد الديناميكي)
│   ├─ 6.1.1: Rule-Based Generation (التوليد القائم على القواعد)
│   │   └─ SentenceGenerationEngine
│   └─ 6.1.2: Enhanced Generation (التوليد المحسن)
│       └─ EnhancedSentenceGenerationEngine
│
└─ 📦 Group 6.2: Static Generation (التوليد الثابت)
    └─ 6.2.1: Template-Based (القوالب الجاهزة)
        └─ StaticSentenceGenerator

═══════════════════════════════════════════════════════════════════════════
```

## 📊 Statistics Summary

| Layer | Engines | Groups | Subgroups |
|-------|---------|--------|-----------|
| 1. Phonology | 3 | 2 | 2 |
| 2. Morphology | 22 | 9 | 20 |
| 3. Lexicon | 15 | 6 | 15 |
| 4. Syntax | 13 | 6 | 13 |
| 5. Rhetoric | 11 | 5 | 8 |
| 6. Generation | 3 | 2 | 3 |
| **TOTAL** | **66** | **30** | **61+** |

---

## 🎯 Navigation Patterns

### By Linguistic Level (Bottom-Up)
```
Sound → Word Structure → Vocabulary → Grammar → Style → Composition
  1   →       2         →     3      →    4    →   5   →      6
```

### By Complexity (Simple → Complex)
```
Phonemes → Morphemes → Lexemes → Phrases → Discourse → Sentences
```

### By Dependencies
```
Layer N depends on Layer N-1 (lower layers provide foundation)
Example: Syntax (4) requires Lexicon (3) requires Morphology (2)
```

---

## 🔍 Quick Search Index

### Find by Arabic Term

| Arabic Term | English | Layer | Group.Subgroup |
|-------------|---------|-------|----------------|
| الفونيمات | Phonemes | 1 | 1.1.1 |
| الفاعل | Subject | 4 | 4.1.1 |
| اسم الفاعل | Active Participle | 2 | 2.2.1 |
| اسم المفعول | Passive Participle | 2 | 2.2.2 |
| التشبيه | Simile | 5 | 5.1.1 |
| الاستعارة | Metaphor | 5 | 5.1.2 |
| المبني للمجهول | Passive Voice | 2 | 2.1.2 |
| الاستفهام | Interrogative | 4 | 4.3.1 |
| الجناس | Paronomasia | 5 | 5.2.1 |
| أسماء الله | Divine Names | 3 | 3.6.1 |

### Find by English Term

| English Term | Arabic | Layer | Group.Subgroup |
|--------------|--------|-------|----------------|
| Subject | الفاعل | 4 | 4.1.1 |
| Object | المفعول به | 4 | 4.1.2 |
| Verbs | الأفعال | 2 | 2.1.1 |
| Adjectives | الصفات | 2 | 2.4.2 |
| Proper Nouns | الأعلام | 3 | 3.1.x |
| Metaphor | الاستعارة | 5 | 5.1.2 |
| Paronomasia | الجناس | 5 | 5.2.1 |

---

## 🛠️ CLI Commands Reference

```bash
# Show this hierarchy
python engine_hierarchy.py

# Filter by layer
python engine_hierarchy.py --layer 1    # Phonology only
python engine_hierarchy.py --layer 2    # Morphology only
python engine_hierarchy.py --layer 5    # Rhetoric only

# Search engines
python engine_hierarchy.py --search "فاعل"
python engine_hierarchy.py --search "Participle"

# Export
python engine_hierarchy.py --export json

# Statistics
python engine_hierarchy.py --stats
```

---

## 📚 Related Documentation

- **[ENGINE_TAXONOMY.md](ENGINE_TAXONOMY.md)** - Complete textual hierarchy with details
- **[HIERARCHY_README.md](HIERARCHY_README.md)** - Quick reference guide
- **[ENGINE_MANIFEST.md](ENGINE_MANIFEST.md)** - Architecture overview
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** - AI agent guidance

---

**Architecture Version**: 2.0.0  
**Total Depth**: 3 levels (Layer → Group → Subgroup)  
**Last Updated**: 2026-02-03
