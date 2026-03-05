# I3rab Arabic-English Mappings

Reference for all Arabic↔English mappings used in the Syntax Layer.

## I3rab Type Mapping

| Arabic | English (code) | Syntactic Role |
|--------|---------------|----------------|
| مبتدأ | mubtada | subject |
| خبر | khabar | predicate |
| فاعل | fa'il | agent |
| مفعول به | maf'ul_bihi | object |
| حرف | harf | particle |
| مضاف إليه | mudaf_ilayhi | genitive_complement |
| نعت | na't | adjunct |
| مفعول مطلق | maf'ul_mutlaq | cognate_object |
| مفعول لأجله | maf'ul_lajlih | purpose |
| حال | hal | circumstantial |
| تمييز | tamyeez | specifier |
| بدل | badal | appositive |
| عطف | atf | conjunction |
| توكيد | tawkid | emphasis |
| نائب فاعل | na'ib_fa'il | passive_subject |
| اسم كان | ism_kana | subject |
| خبر كان | khabar_kana | predicate |
| اسم إن | ism_inna | subject |
| خبر إن | khabar_inna | predicate |
| مجرور | majrur | oblique |

## Case Mapping

| Arabic | English |
|--------|---------|
| مرفوع | nominative |
| منصوب | accusative |
| مجرور | genitive |

## Case Marker Mapping

| Arabic | English |
|--------|---------|
| الضمة | damma |
| الفتحة | fatha |
| الكسرة | kasra |
| الواو | waw |
| الياء | ya |
| الألف | alif |
| النون | nun |

## Mahall (Position Clause)

| Arabic | English |
|--------|---------|
| في محل رفع | in_nominative_position |
| في محل نصب | in_accusative_position |
| في محل جر | in_genitive_position |
| لا محل له من الإعراب | no_grammatical_position |

## Usage

```python
from fvafk.c2b.syntax.mappings import (
    I3RAB_TYPE_MAPPING,
    CASE_MAPPING,
    CASE_MARKER_MAPPING,
)

# Arabic → English
print(I3RAB_TYPE_MAPPING["مبتدأ"])   # mubtada
print(CASE_MAPPING["مرفوع"])         # nominative

# English → Arabic (reverse mapping)
from fvafk.c2b.syntax.mappings import I3RAB_TYPE_MAPPING_REVERSE
print(I3RAB_TYPE_MAPPING_REVERSE["mubtada"])  # مبتدأ
```
