# CLI Output Schema

Complete reference for FVAFK CLI JSON output structure.

---

## Overview

The CLI outputs a structured JSON object containing analysis results from all pipeline stages:
- **C1**: Encoding (units)
- **C2A**: Phonology (gates, syllables)
- **C2B**: Morphology (roots, patterns) - *optional with `--morphology`*
- **Syntax**: Links (ISNADI) - *optional with `--morphology`*
- **Stats**: Performance metrics

---

## Basic Structure
```json
{
  "input": "string",
  "c1": {...},
  "c2a": {...},
  "c2b": {...},      // only with --morphology
  "syntax": {...},    // only with --morphology
  "stats": {...}
}
```

---

## Field Descriptions

### `input`
- **Type:** `string`
- **Description:** Original input text
- **Example:** `"الْكِتَابُ"`

### `c1` (Encoding Layer)
- **Type:** `object`
- **Fields:**
  - `num_units`: Number of encoded units
  - `units`: Array of unit objects (with `--verbose`)
- **Example:**
```json
{
  "num_units": 8,
  "units": [
    {"text": "ا", "category": "LETTER"},
    {"text": "لْ", "category": "LETTER"}
  ]
}
```

### `c2a` (Phonology Layer)
- **Type:** `object`
- **Fields:**
  - `syllables`: Syllable count and structure
  - `gates`: Array of gate results
  - `cv_analysis`: CV pattern (with `--phonology-v2`)
- **Example:**
```json
{
  "syllables": {
    "count": 3,
    "pattern": "CVC-CV-CVC"
  },
  "gates": [
    {
      "gate_id": "sukun",
      "status": "REPAIR",
      "deltas": 2
    }
  ]
}
```

### `c2b` (Morphology Layer)
- **Type:** `object` or `null`
- **Present:** Only with `--morphology` flag
- **Fields:**
  - `words_count`: Number of words analyzed
  - `words`: Array of word analysis objects
- **Example:**
```json
{
  "words_count": 1,
  "words": [
    {
      "word": "الْكِتَابُ",
      "span": {"start": 0, "end": 10},
      "kind": "noun",
      "root": {
        "formatted": "ك ت ب",
        "type": "triliteral"
      },
      "pattern": {
        "template": "فِعَال",
        "type": "form_i"
      },
      "features": {
        "case": "nominative",
        "definite": true,
        "number": "singular"
      }
    }
  ]
}
```

### `syntax` (Syntax Layer)
- **Type:** `object` or `null`
- **Present:** Only with `--morphology` flag
- **Fields:**
  - `word_forms`: Array of WordForm objects
  - `links`: Object containing link arrays by type
    - `isnadi`: Array of ISNADI link objects
- **Example:**
```json
{
  "word_forms": [
    {
      "id": 0,
      "surface": "مُحَمَّدٌ",
      "bare": "محمد",
      "kind": "noun",
      "pos": "noun",
      "span": {"start": 0, "end": 9},
      "case": "nominative",
      "number": "singular",
      "gender": "masculine",
      "definiteness": "indefinite",
      "root": "ح م د",
      "pattern": "مُفَعَّل"
    },
    {
      "id": 1,
      "surface": "رَسُولُ",
      "bare": "رسول",
      "kind": "noun",
      "pos": "noun",
      "span": {"start": 10, "end": 17},
      "case": "nominative",
      "number": "singular",
      "gender": "masculine",
      "definiteness": "definite",
      "root": "ر س ل",
      "pattern": "فَعُول"
    }
  ],
  "links": {
    "isnadi": [
      {
        "type": "إسنادي",
        "type_en": "ISNADI",
        "head": {
          "id": 0,
          "surface": "مُحَمَّدٌ",
          "pos": "noun",
          "case": "مرفوع"
        },
        "dependent": {
          "id": 1,
          "surface": "رَسُولُ",
          "pos": "noun",
          "case": "مرفوع"
        },
        "confidence": 1.0,
        "reason": "ISNADI: case agreement, number agreement"
      }
    ]
  }
}
```

### `stats` (Performance Metrics)
- **Type:** `object`
- **Fields:**
  - `c1_time_ms`: C1 execution time
  - `c2a_time_ms`: C2A execution time
  - `c2b_time_ms`: C2B execution time (if applicable)
  - `total_time_ms`: Total pipeline time
  - `gates_count`: Number of gates executed
- **Example:**
```json
{
  "c1_time_ms": 2.5,
  "c2a_time_ms": 15.3,
  "c2b_time_ms": 8.7,
  "total_time_ms": 26.5,
  "gates_count": 11
}
```

---

## Complete Examples

### Example 1: Basic (no morphology)

**Command:**
```bash
fvafk "كِتَابٌ" --json
```

**Output:**
```json
{
  "input": "كِتَابٌ",
  "c1": {
    "num_units": 5
  },
  "c2a": {
    "syllables": {
      "count": 2
    },
    "gates": [...]
  },
  "stats": {
    "c1_time_ms": 1.2,
    "c2a_time_ms": 10.5,
    "total_time_ms": 11.7,
    "gates_count": 11
  }
}
```

### Example 2: With Morphology and Syntax

**Command:**
```bash
fvafk "مُحَمَّدٌ رَسُولُ اللَّهِ" --morphology --json
```

**Output:**
```json
{
  "input": "مُحَمَّدٌ رَسُولُ اللَّهِ",
  "c1": {
    "num_units": 23
  },
  "c2a": {
    "syllables": {
      "count": 8
    },
    "gates": [...]
  },
  "c2b": {
    "words_count": 3,
    "words": [
      {
        "word": "مُحَمَّدٌ",
        "kind": "noun",
        "root": {
          "formatted": "ح م د",
          "type": "triliteral"
        },
        "pattern": {
          "template": "مُفَعَّل",
          "type": "passive_participle"
        }
      },
      {
        "word": "رَسُولُ",
        "kind": "noun",
        "root": {
          "formatted": "ر س ل",
          "type": "triliteral"
        }
      },
      {
        "word": "اللَّهِ",
        "kind": "noun"
      }
    ]
  },
  "syntax": {
    "word_forms": [
      {
        "id": 0,
        "surface": "مُحَمَّدٌ",
        "pos": "noun",
        "case": "nominative"
      },
      {
        "id": 1,
        "surface": "رَسُولُ",
        "pos": "noun",
        "case": "nominative"
      },
      {
        "id": 2,
        "surface": "اللَّهِ",
        "pos": "noun",
        "case": "genitive"
      }
    ],
    "links": {
      "isnadi": [
        {
          "type": "إسنادي",
          "type_en": "ISNADI",
          "head": {
            "id": 0,
            "surface": "مُحَمَّدٌ",
            "pos": "noun",
            "case": "مرفوع"
          },
          "dependent": {
            "id": 1,
            "surface": "رَسُولُ",
            "pos": "noun",
            "case": "مرفوع"
          },
          "confidence": 1.0,
          "reason": "ISNADI: case agreement, number agreement"
        }
      ]
    }
  },
  "stats": {
    "c1_time_ms": 3.5,
    "c2a_time_ms": 18.2,
    "c2b_time_ms": 12.8,
    "total_time_ms": 34.5,
    "gates_count": 11
  }
}
```

---

## CLI Flags Reference

| Flag | Effect |
|------|--------|
| `--json` | Output JSON (default: human-readable) |
| `--morphology` | Enable C2B + Syntax layers |
| `--multi-word` | Analyze each word separately |
| `--phonology-v2` | Use Phonology V2 engine |
| `--phonology-v2-details` | Include syllabification details |
| `--phonology-v2-witnesses` | Include Phonology V2 witnesses |
| `--verbose` | Include detailed unit/segment info |

---

## Version

- **Document Version:** 1.0
- **Pipeline Version:** 0.1.0
- **Last Updated:** 2026-02-01

---

## See Also

- [README.md](../README.md) - General overview
- [ENHANCED_ROADMAP.md](../ENHANCED_ROADMAP.md) - Development plan
- [CLI Usage Examples](../README.md#usage)
