# Hierarchical Engine Organization - Quick Reference

## ✨ What's New

The project now has a **3-level hierarchical taxonomy** for all 66 grammar engines:

```
Layer (1-6)
  └─ Group (e.g., 2.1)
      └─ Subgroup (e.g., 2.1.1)
          └─ Engines
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **[ENGINE_TAXONOMY.md](ENGINE_TAXONOMY.md)** | Complete 3-level hierarchy with all 66 engines organized by Layer → Group → Subgroup |
| **[ENGINE_MANIFEST.md](ENGINE_MANIFEST.md)** | Architecture overview and proven components |
| **[.github/copilot-instructions.md](.github/copilot-instructions.md)** | AI agent guide with updated hierarchy information |

---

## 🛠️ Hierarchy Explorer Tool

Use `engine_hierarchy.py` to navigate and visualize the structure:

### View Full Tree
```bash
python engine_hierarchy.py
```

### Filter by Layer
```bash
python engine_hierarchy.py --layer 2          # Show morphology only
python engine_hierarchy.py --layer 4          # Show syntax only
```

### Search Engines
```bash
python engine_hierarchy.py --search "فاعل"    # Search by Arabic term
python engine_hierarchy.py --search "Active"  # Search by English name
```

### Show Statistics
```bash
python engine_hierarchy.py --stats
```

Output:
```
Total Engines: 66
By Layer:
  Layer 1 (PHONOLOGY): 3 engines
  Layer 2 (MORPHOLOGY): 22 engines
  Layer 3 (LEXICON): 15 engines
  Layer 4 (SYNTAX): 13 engines
  Layer 5 (RHETORIC): 11 engines
  Layer 6 (GENERATION): 3 engines (pending)
```

### Export to JSON
```bash
python engine_hierarchy.py --export json
```

---

## 🏗️ Engine Structure with Hierarchy

New engines should define hierarchical metadata:

```python
from engines.base import MorphologyEngine, EngineLayer

class MyNewEngine(MorphologyEngine):
    SHEET_NAME = "اسم_قصير"
    LAYER = EngineLayer.MORPHOLOGY
    GROUP = "2.1"                    # Functional group
    SUBGROUP = "2.1.3"               # Semantic subgroup
    GROUP_AR = "الأفعال"              # Arabic group name
    SUBGROUP_AR = "الأفعال الخاصة"     # Arabic subgroup name
    
    @classmethod
    def make_df(cls):
        # Implementation
        pass
```

---

## 📊 Hierarchy Summary

### 6 Layers
1. **Phonology** (الصوتيات) - 3 engines
2. **Morphology** (الصرف) - 22 engines
3. **Lexicon** (المعجم) - 15 engines
4. **Syntax** (النحو) - 13 engines
5. **Rhetoric** (البلاغة) - 11 engines
6. **Generation** (التوليد) - 3 engines

### 30 Functional Groups
Each layer has 2-9 groups organizing engines by function.

### 66+ Subgroups
Fine-grained semantic classification within groups.

---

## 🔍 Quick Navigation

### Find Engine by Arabic Term

| Term | Layer | Location |
|------|-------|----------|
| الفاعل | Syntax | Group 4.1.1 (Core Arguments → Subject) |
| اسم الفاعل | Morphology | Group 2.2.1 (Participial Forms → Active) |
| التشبيه | Rhetoric | Group 5.1.1 (Figures of Speech → Simile) |
| الاستعارة | Rhetoric | Group 5.1.2 (Figures of Speech → Metaphor) |
| الفونيمات | Phonology | Group 1.1.1 (Core Phonemes → Inventory) |

### Find Layer by Number

| Layer | Name | Arabic | Groups |
|-------|------|--------|--------|
| 1 | Phonology | الصوتيات | 2 |
| 2 | Morphology | الصرف | 9 |
| 3 | Lexicon | المعجم | 6 |
| 4 | Syntax | النحو | 6 |
| 5 | Rhetoric | البلاغة | 5 |
| 6 | Generation | التوليد | 2 |

---

## 🎯 Example Queries

### Show all morphology engines
```bash
python engine_hierarchy.py --layer 2
```

### Find engines with "مفعول" (object)
```bash
python engine_hierarchy.py --search "مفعول"
```

### Export complete hierarchy
```bash
python engine_hierarchy.py --export json
# Creates: engine_hierarchy.json
```

---

## 🔗 Integration with Code

### Query by Metadata
```python
from engines.phonology import PhonemesEngine

# Get engine metadata
metadata = PhonemesEngine.get_metadata()
print(metadata['group'])      # "1.1"
print(metadata['subgroup'])   # "1.1.1"

# Get full hierarchy path
print(PhonemesEngine.get_hierarchy())
# Output: "Layer 1 (PHONOLOGY) → Group 1.1 → Subgroup 1.1.1"
```

### Filter Engines by Group
```python
from engines.base import EngineLayer

# Get all engines from a layer
morphology_engines = [
    e for e in all_engines 
    if e.LAYER == EngineLayer.MORPHOLOGY
]

# Filter by group
verbal_morphology = [
    e for e in morphology_engines 
    if hasattr(e, 'GROUP') and e.GROUP == "2.1"
]
```

---

## 📝 Notes

- **Backward Compatibility**: Root-level `*_engine.py` files still work
- **Preferred Path**: Use `src/engines/` imports for new code
- **Generation Layer**: Temporarily disabled in some tools due to dependencies (being fixed)
- **Documentation**: [ENGINE_TAXONOMY.md](ENGINE_TAXONOMY.md) is the authoritative source

---

**Version**: 2.0.0  
**Last Updated**: 2026-02-03  
**Total Classification Depth**: 3 levels (Layer → Group → Subgroup)
