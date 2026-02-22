# Hierarchical Engine Taxonomy

## Overview
Complete hierarchical classification of all 66 Arabic grammar engines organized by computational linguistics layers, functional groups, and semantic subgroups.

---

## Layer 1: PHONOLOGY (الصوتيات) - Sound Level

### Group 1.1: Core Phonemes
**Purpose**: Basic sound inventory and phonological units

#### Subgroup 1.1.1: Phoneme Inventory
- **PhonemesEngine** (`src/engines/phonology/phonemes_engine.py`)
  - Core consonants and vowels
  - Phonological features
  - IPA mappings

#### Subgroup 1.1.2: Sound Classifications
- **SoundEngine** (`src/engines/phonology/sound_engine.py`)
  - Sound categories
  - Phonetic descriptions
  - Articulatory features

### Group 1.2: Modern Phonology
**Purpose**: Contemporary Arabic pronunciation systems

#### Subgroup 1.2.1: Modern Sound Inventory
- **AswatMuhdathaEngine** (`src/engines/phonology/aswat_muhdatha_engine.py`)
  - Modern standard Arabic sounds
  - Dialectal variations
  - Contemporary phonetics

---

## Layer 2: MORPHOLOGY (الصرف) - Word Structure

### Group 2.1: Verbal Morphology
**Purpose**: Verb forms, derivations, and inflections

#### Subgroup 2.1.1: Basic Verb Forms
- **VerbsEngine** (`src/engines/morphology/verbs_engine.py`)
  - Trilateral verbs
  - Quadrilateral verbs
  - Forms I-X

#### Subgroup 2.1.2: Special Verb Forms
- **AfaalKhamsaEngine** (`src/engines/morphology/afaal_khamsa_engine.py`)
  - Five verbs (الأفعال الخمسة)
  - Dual/plural conjugations
  - Present tense variants

#### Subgroup 2.1.3: Voice Transformations
- **MabniMajhoolEngine** (`src/engines/morphology/mabni_majhool_engine.py`)
  - Passive voice (المبني للمجهول)
  - Voice alternations
  - Agent deletion patterns

### Group 2.2: Participial Forms
**Purpose**: Active and passive participles

#### Subgroup 2.2.1: Active Participles
- **ActiveParticipleEngine** (`src/engines/morphology/active_participle_engine.py`)
  - اسم الفاعل
  - Agent nouns
  - Pattern: فاعل

#### Subgroup 2.2.2: Passive Participles
- **PassiveParticipleEngine** (`src/engines/morphology/passive_participle_engine.py`)
  - اسم المفعول
  - Patient nouns
  - Pattern: مفعول

### Group 2.3: Derived Nouns (المشتقات)
**Purpose**: Nouns derived from roots

#### Subgroup 2.3.1: Instrument Nouns
- **IsmAlaEngine** (`src/engines/morphology/ism_ala_engine.py`)
  - اسم الآلة
  - Tool/instrument names
  - Patterns: مفعال، مفعل، مفعلة

#### Subgroup 2.3.2: Instance Nouns
- **IsmMarraEngine** (`src/engines/morphology/ism_marra_engine.py`)
  - اسم المرة
  - Single occurrence
  - Pattern: فَعْلَة

#### Subgroup 2.3.3: Manner Nouns
- **IsmHayaaEngine** (`src/engines/morphology/ism_hay_a_engine.py`)
  - اسم الهيئة
  - Manner of action
  - Pattern: فِعْلَة

#### Subgroup 2.3.4: Locative/Temporal Nouns
- **MimiNounsEngine** (`src/engines/morphology/mimi_nouns_engine.py`)
  - Nouns with مـ prefix
  - Place/time nouns
  - Patterns: مَفْعَل، مَفْعِل، مَفْعَلة

### Group 2.4: Adjectival Forms
**Purpose**: Quality and comparison adjectives

#### Subgroup 2.4.1: Basic Adjectives
- **AdjectiveEngine** (`src/engines/morphology/adjective_engine.py`)
  - الصفة
  - Quality descriptors
  - Multiple patterns

#### Subgroup 2.4.2: Comparative/Superlative
- **SuperlativeEngine** (`src/engines/morphology/superlative_engine.py`)
  - اسم التفضيل
  - Comparative forms (أفعل)
  - Elative patterns

#### Subgroup 2.4.3: Intensified Forms
- **MubalaghSighaEngine** (`src/engines/morphology/mubalagh_sigha_engine.py`)
  - صيغة المبالغة
  - Intensive adjectives
  - Patterns: فَعَّال، فَعُول، فَعِيل، etc.

### Group 2.5: Defective Nouns (الأسماء المعتلة)
**Purpose**: Nouns with weak radicals

#### Subgroup 2.5.1: Shortened Nouns
- **IsmMaqsorEngine** (`src/engines/morphology/ism_maqsor_engine.py`)
  - الاسم المقصور
  - Ending in alif maqsura
  - Declension patterns

#### Subgroup 2.5.2: Extended Nouns
- **IsmMamdodEngine** (`src/engines/morphology/ism_mamdod_engine.py`)
  - الاسم الممدود
  - Ending in hamza
  - Extension patterns

#### Subgroup 2.5.3: Deficient Nouns
- **IsmManqusEngine** (`src/engines/morphology/ism_manqus_engine.py`)
  - الاسم المنقوص
  - Ending in yaa
  - Truncation rules

### Group 2.6: Derivational Transformations
**Purpose**: Word formation processes

#### Subgroup 2.6.1: Relational Adjectives
- **NisbaEngine** (`src/engines/morphology/nisba_engine.py`)
  - النسبة
  - Relational suffix ـيّ
  - Attribution patterns

#### Subgroup 2.6.2: Diminutives
- **TasgheerEngine** (`src/engines/morphology/tasgheer_engine.py`)
  - التصغير
  - Diminutive forms
  - Patterns: فُعَيْل، فُعَيْعِل

#### Subgroup 2.6.3: Abstract Nouns
- **MasdarSinaiEngine** (`src/engines/morphology/masdar_sinai_engine.py`)
  - المصدر الصناعي
  - Abstract suffix ـيّة
  - Nominal abstractions

### Group 2.7: Construction Patterns
**Purpose**: Fixed morphological structures

#### Subgroup 2.7.1: Indeclinable Forms
- **BinaaEngine** (`src/engines/morphology/binaa_engine.py`)
  - المبني
  - Fixed forms
  - Non-inflectable words

#### Subgroup 2.7.2: Exclamatory Forms
- **TaajjubEngine** (`src/engines/morphology/taajjub_engine.py`)
  - التعجب
  - Exclamation patterns
  - أفعل التعجب

### Group 2.8: Grammatical Gender
**Purpose**: Gender classification and agreement

#### Subgroup 2.8.1: Gender Systems
- **GenderEngine** (`src/engines/morphology/gender_engine.py`)
  - Masculine/feminine
  - Gender markers
  - Agreement rules

### Group 2.9: Meta-Morphological
**Purpose**: Cross-engine morphological attributes

#### Subgroup 2.9.1: Shared Attributes
- **CommonAttributesEngine** (`src/engines/morphology/common_attributes_engine.py`)
  - Cross-engine properties
  - Morphological metadata
  - Feature matrices

---

## Layer 3: LEXICON (المعجم) - Vocabulary

### Group 3.1: Proper Nouns (الأعلام)
**Purpose**: Named entities and proper names

#### Subgroup 3.1.1: Person Names
- **A3lamAshkhasEngine** (`src/engines/lexicon/a3lam_ashkhas_engine.py`)
  - أعلام الأشخاص
  - Personal names
  - Historical figures

#### Subgroup 3.1.2: Place Names
- **A3lamAmakinEngine** (`src/engines/lexicon/a3lam_amakin_engine.py`)
  - أعلام الأماكن
  - Geographic locations
  - Cities and regions
  
- **PlaceEngine** (`src/engines/lexicon/place_engine.py`)
  - Generic place terms
  - Location vocabulary

#### Subgroup 3.1.3: Transferred Names
- **A3lamManqulaEngine** (`src/engines/lexicon/a3lam_manqula_engine.py`)
  - أعلام منقولة
  - Borrowed names
  - Foreign proper nouns

#### Subgroup 3.1.4: General Proper Nouns
- **ProperNounsEngine** (`src/engines/lexicon/proper_nouns_engine.py`)
  - Comprehensive proper noun list
  - All categories

### Group 3.2: Common Nouns
**Purpose**: Generic vocabulary items

#### Subgroup 3.2.1: Generic Vocabulary
- **GenericNounsEngine** (`src/engines/lexicon/generic_nouns_engine.py`)
  - Common nouns
  - Everyday vocabulary
  - General terms

### Group 3.3: Collective Nouns (الجنس)
**Purpose**: Collective and individual forms

#### Subgroup 3.3.1: Collective Forms
- **JinsJamiiEngine** (`src/engines/lexicon/jins_jamii_engine.py`)
  - اسم الجنس الجمعي
  - Collective nouns
  - Group terms

#### Subgroup 3.3.2: Individual Forms
- **JinsIfradiEngine** (`src/engines/lexicon/jins_ifradi_engine.py`)
  - اسم الجنس الإفرادي
  - Singulative nouns
  - Unit forms

### Group 3.4: Semantic Classes
**Purpose**: Ontological categories

#### Subgroup 3.4.1: Sentient Beings
- **KainatAqilaEngine** (`src/engines/lexicon/kainat_aqila_engine.py`)
  - الكائنات العاقلة
  - Rational beings
  - Humans and intelligent entities

#### Subgroup 3.4.2: Non-Sentient Entities
- **KainatGhairAqilaEngine** (`src/engines/lexicon/kainat_ghair_aqila_engine.py`)
  - الكائنات غير العاقلة
  - Non-rational beings
  - Animals, objects, phenomena

### Group 3.5: Number Names
**Purpose**: Numerical vocabulary

#### Subgroup 3.5.1: Number Terms
- **AdadNamesEngine** (`src/engines/lexicon/adad_names_engine.py`)
  - أسماء الأعداد
  - Cardinal numbers
  - Ordinal numbers

### Group 3.6: Religious/Specialized Terms
**Purpose**: Domain-specific vocabulary

#### Subgroup 3.6.1: Divine Names
- **AsmaAllahEngine** (`src/engines/lexicon/asma_allah_engine.py`)
  - أسماء الله الحسنى
  - 99 names of Allah
  - Divine attributes

#### Subgroup 3.6.2: Islamic Terminology
- **MusatalahatShariaEngine** (`src/engines/lexicon/musatalahat_sharia_engine.py`)
  - المصطلحات الشرعية
  - Sharia terms
  - Religious vocabulary

---

## Layer 4: SYNTAX (النحو) - Sentence Structure

### Group 4.1: Core Arguments
**Purpose**: Essential sentence constituents

#### Subgroup 4.1.1: Subject
- **FaelEngine** (`src/engines/syntax/fael_engine.py`)
  - الفاعل
  - Doer of action
  - Subject in verbal sentences

#### Subgroup 4.1.2: Object
- **MafoulBihEngine** (`src/engines/syntax/mafoul_bih_engine.py`)
  - المفعول به
  - Direct object
  - Patient of action

#### Subgroup 4.1.3: Passive Agent
- **NaebFaelEngine** (`src/engines/syntax/naeb_fael_engine.py`)
  - نائب الفاعل
  - Passive subject
  - Deputy agent

### Group 4.2: Adjuncts (الفضلات)
**Purpose**: Optional sentence elements

#### Subgroup 4.2.1: Absolute Object
- **MafoulMutlaqEngine** (`src/engines/syntax/mafoul_mutlaq_engine.py`)
  - المفعول المطلق
  - Cognate object
  - Source of infinitive

#### Subgroup 4.2.2: Object of Purpose
- **MafoulAjlihEngine** (`src/engines/syntax/mafoul_ajlih_engine.py`)
  - المفعول لأجله
  - Purpose complement
  - Reason/cause

#### Subgroup 4.2.3: Circumstantial Complement
- **HaalEngine** (`src/engines/syntax/haal_engine.py`)
  - الحال
  - Manner/state
  - Circumstantial adjunct

#### Subgroup 4.2.4: Specification
- **TamyeezEngine** (`src/engines/syntax/tamyeez_engine.py`)
  - التمييز
  - Specifier
  - Disambiguation element

### Group 4.3: Nominal Sentences
**Purpose**: Non-verbal predication

#### Subgroup 4.3.1: Subject-Predicate
- **MobtadaKhabarEngine** (`src/engines/syntax/mobtada_khabar_engine.py`)
  - المبتدأ والخبر
  - Topic and comment
  - Nominal sentence structure

### Group 4.4: Interrogative Constructions
**Purpose**: Question formation

#### Subgroup 4.4.1: Question Particles
- **IstifhamEngine** (`src/engines/syntax/istifham_engine.py`)
  - الاستفهام
  - Interrogative tools
  - Question words

### Group 4.5: Stylistic Operations
**Purpose**: Word order variations and emphasis

#### Subgroup 4.5.1: Fronting
- **TaqdimEngine** (`src/engines/syntax/taqdim_engine.py`)
  - التقديم
  - Fronting/preposing
  - Topic shift

#### Subgroup 4.5.2: Restriction
- **QasrEngine** (`src/engines/syntax/qasr_engine.py`)
  - القصر
  - Restrictive particles
  - Exclusivity constructions

#### Subgroup 4.5.3: Governance Conflict
- **IshtighalEngine** (`src/engines/syntax/ishtighal_engine.py`)
  - الاشتغال
  - Competing governance
  - Object fronting with verb

### Group 4.6: Response Structures
**Purpose**: Answer and reply patterns

#### Subgroup 4.6.1: Answer Particles
- **JawabEngine** (`src/engines/syntax/jawab_engine.py`)
  - الجواب
  - Response markers
  - Answer constructions

---

## Layer 5: RHETORIC (البلاغة) - Figurative Language

### Group 5.1: Figures of Speech (المحسنات البديعية)
**Purpose**: Tropes and figurative expressions

#### Subgroup 5.1.1: Simile
- **TashbihEngine** (`src/engines/rhetoric/tashbih_engine.py`)
  - التشبيه
  - Comparison structures
  - Simile components

#### Subgroup 5.1.2: Metaphor
- **IstiaraEngine** (`src/engines/rhetoric/istiara_engine.py`)
  - الاستعارة
  - Metaphorical transfer
  - Figurative substitution

#### Subgroup 5.1.3: Metonymy
- **KinayaEngine** (`src/engines/rhetoric/kinaya_engine.py`)
  - الكناية
  - Indirect expression
  - Allusion patterns

### Group 5.2: Sound Patterns (المحسنات اللفظية)
**Purpose**: Phonological embellishments

#### Subgroup 5.2.1: Paronomasia
- **JinassEngine** (`src/engines/rhetoric/jinass_engine.py`)
  - الجناس
  - Wordplay
  - Phonetic similarity

#### Subgroup 5.2.2: Rhymed Prose
- **SajaEngine** (`src/engines/rhetoric/saja_engine.py`)
  - السجع
  - Prose rhyme
  - Rhythmic endings

### Group 5.3: Semantic Relations (المحسنات المعنوية)
**Purpose**: Meaning-based devices

#### Subgroup 5.3.1: Antithesis
- **TibaqEngine** (`src/engines/rhetoric/tibaq_engine.py`)
  - الطباق
  - Opposition
  - Contrasting pairs

#### Subgroup 5.3.2: Parallel Contrast
- **MuqabalaEngine** (`src/engines/rhetoric/muqabala_engine.py`)
  - المقابلة
  - Multiple contrasts
  - Parallel structures

#### Subgroup 5.3.3: Synonymy
- **TaradufEngine** (`src/engines/rhetoric/taraduf_engine.py`)
  - الترادف
  - Synonym usage
  - Lexical variation

### Group 5.4: Brevity and Expansion
**Purpose**: Text density control

#### Subgroup 5.4.1: Conciseness/Prolixity
- **IjazItnabEngine** (`src/engines/rhetoric/ijaz_itnab_engine.py`)
  - الإيجاز والإطناب
  - Brevity vs. expansion
  - Information density

### Group 5.5: Complex Rhetorical Structures
**Purpose**: Multi-level stylistic operations

#### Subgroup 5.5.1: Combined Restriction-Fronting
- **QasrTaqdimEngine** (`src/engines/rhetoric/qasr_taqdim_engine.py`)
  - القصر والتقديم
  - Restriction with fronting
  - Complex emphasis

---

## Layer 6: GENERATION (التوليد) - Sentence Production

### Group 6.1: Dynamic Generation
**Purpose**: Rule-based sentence construction

#### Subgroup 6.1.1: Basic Generation
- **SentenceGenerationEngine** (`src/engines/generation/sentence_generation_engine.py`)
  - Basic sentence production
  - Component composition
  - Multi-engine integration

#### Subgroup 6.1.2: Enhanced Generation
- **EnhancedSentenceGenerationEngine** (`src/engines/generation/enhanced_sentence_generation_engine.py`)
  - Advanced generation
  - Linguistic constraints
  - Sophisticated composition

### Group 6.2: Static Generation
**Purpose**: Template-based production

#### Subgroup 6.2.1: Template-Based
- **StaticSentenceGenerator** (`src/engines/generation/static_sentence_generator.py`)
  - Fixed patterns
  - Pre-defined templates
  - Self-contained generation

---

## Hierarchical Statistics

### By Layer
- **Layer 1 (Phonology)**: 3 engines in 2 groups
- **Layer 2 (Morphology)**: 22 engines in 9 groups
- **Layer 3 (Lexicon)**: 15 engines in 6 groups
- **Layer 4 (Syntax)**: 13 engines in 6 groups
- **Layer 5 (Rhetoric)**: 11 engines in 5 groups
- **Layer 6 (Generation)**: 3 engines in 2 groups

### Total
- **6 Layers**
- **30 Groups**
- **66 Engines**

---

## Navigation Index

### Quick Access by Arabic Term

#### الصرف (Morphology)
- الأفعال (Verbs): Group 2.1
- المشتقات (Derived forms): Group 2.3
- الصفات (Adjectives): Group 2.4
- الأسماء المعتلة (Defective nouns): Group 2.5

#### المعجم (Lexicon)
- الأعلام (Proper nouns): Group 3.1
- الجنس (Collective): Group 3.3
- الكائنات (Beings): Group 3.4

#### النحو (Syntax)
- الفاعل (Subject): Subgroup 4.1.1
- المفعول (Object): Subgroup 4.1.2
- المبتدأ والخبر (Nominal): Subgroup 4.3.1

#### البلاغة (Rhetoric)
- التشبيه (Simile): Subgroup 5.1.1
- الاستعارة (Metaphor): Subgroup 5.1.2
- الجناس (Paronomasia): Subgroup 5.2.1
- الطباق (Antithesis): Subgroup 5.3.1

---

## Usage in Code

### Import by Layer
```python
from engines.phonology import PhonemesEngine  # Layer 1, Group 1.1
from engines.morphology import ActiveParticipleEngine  # Layer 2, Group 2.2
from engines.lexicon import ProperNounsEngine  # Layer 3, Group 3.1
from engines.syntax import FaelEngine  # Layer 4, Group 4.1
from engines.rhetoric import TashbihEngine  # Layer 5, Group 5.1
from engines.generation import SentenceGenerationEngine  # Layer 6, Group 6.1
```

### Query by Group
```python
from engines.base import EngineLayer

# Get all morphology engines
morphology_engines = [e for e in all_engines if e.LAYER == EngineLayer.MORPHOLOGY]

# Filter by group (would need group metadata added to base class)
verbal_morphology = [e for e in morphology_engines if e.GROUP == "2.1"]
```

---

**Version**: 2.0.0  
**Last Updated**: 2026-02-03  
**Total Engines**: 66  
**Taxonomy Depth**: 3 levels (Layer → Group → Subgroup)
