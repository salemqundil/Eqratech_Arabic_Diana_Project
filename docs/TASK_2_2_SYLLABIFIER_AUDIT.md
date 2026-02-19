# Task 2.2: Syllabifier Audit & Unification

**Sprint 2, Week 3, Days 3-4**  
**Status:** Starting...

---

## 🔍 Current State

### Syllabifier Locations

**Main Syllabifier:**
- `src/fvafk/c2b/syllabifier.py` (16.2 KB)
  - Complete syllabifier implementation
  - Supports: CV, CVV, CVC, CVVC, CVCC, CVVCC
  - 562 lines of code

**Phonology V2:**
- `src/fvafk/phonology_v2/` (multiple files)
  - Context-driven VC classification
  - No duplicate syllabifier class found ✅

**Other References:**
- `src/fvafk/c1/cv_pattern.py` - CV pattern analysis
- `src/fvafk/c2a/gates/gate_epenthesis.py` - Uses syllabification

**Test Coverage:**
- `tests/test_syllabifier.py` - 39 tests ✅

---

## 📊 Audit Results

### ✅ Good News

1. **No Major Duplication**
   - Only ONE main syllabifier class (c2b/syllabifier.py)
   - Phonology V2 uses VC classification (complementary, not duplicate)
   - c1/cv_pattern.py provides analysis (not syllabification)

2. **Well Tested**
   - 39 syllabifier tests
   - All passing ✅

3. **Clear Purpose**
   - c2b/syllabifier.py - Main syllabification engine
   - phonology_v2 - Context-driven VC classification
   - Different but complementary!

### ⚠️ Areas for Improvement

1. **Documentation**
   - Syllabifier not clearly marked as "reference"
   - CV/CVV/CVC patterns not explicitly linked to theory
   - No clear link to FormCodecV2

2. **Integration**
   - Relationship with Phonology V2 not documented
   - No explicit tests comparing both approaches

3. **Location**
   - Currently in c2b/ but could be in c2a/ (phonology layer)
   - Or keep in c2b/ and document why

---

## 🎯 Task 2.2.1 Plan

### Option A: Keep as is + Document (Conservative) ⭐

**Action:**
1. Add comprehensive docstring to c2b/syllabifier.py
2. Document CV/CVV/CVC patterns explicitly
3. Add note about relationship with Phonology V2
4. Add link to FormCodecV2
5. Mark as "reference implementation"

**Pros:**
- No code changes
- No risk of breaking tests
- Quick (1-2 hours)

**Cons:**
- Doesn't move to c2a/ (where it logically belongs)

---

### Option B: Move to c2a/ + Refactor (Ambitious)

**Action:**
1. Move c2b/syllabifier.py → c2a/syllabifier.py
2. Update all imports
3. Integrate with gate framework
4. Run all tests

**Pros:**
- Logically correct location (phonology layer)
- Better architecture

**Cons:**
- More changes
- Risk of breaking tests
- Takes longer (3-4 hours)

---

## 💡 Recommendation

**Choose Option A (Conservative)** for Sprint 2:

**Reasons:**
1. ✅ Sprint 2 focus is "unification" not "relocation"
2. ✅ Safer (no breaking changes)
3. ✅ Faster (1-2 hours vs 3-4 hours)
4. ✅ Still achieves goal: "single source of truth"
5. ✅ Can relocate in Sprint 3 if needed

---

## ✅ Task 2.2.1 Action Items (Option A)

1. **Enhance c2b/syllabifier.py docstring**
   - Mark as reference implementation
   - Document CV/CVV/CVC taxonomy
   - Link to Phonology V2
   - Link to FormCodecV2

2. **Add README in c2b/**
   - Explain syllabifier purpose
   - Why it's in c2b/ (used by morphology)

3. **Update tests**
   - Add comments marking as reference
   - No code changes needed

**Estimated Time:** 1-2 hours

---

*Audit Date: 2026-02-15*  
*Decision: Option A (Conservative)*  
*Next: Implement Option A*
