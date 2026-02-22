# syllabification.py

# -*- coding: utf-8 -*-

"""
Arabic syllabification (CV/CVC/CVV/CVVC/...) for your SegCode tape.

Input:

  segs: Sequence[SegCode] where each SegCode is (ch_id, v_id, diac_bits, role_id)

Assumptions:

  - Each SegCode represents ONE consonant letter with its vowel/diacritic info.

  - v_id is one of your vowel IDs: V_SUKUN, V_FATHA, V_DAMMA, V_KASRA, V_ALIF, V_WAW, V_YA

  - Long vowels are encoded as V_ALIF/V_WAW/V_YA on the consonant slot (axis-based design).

Output:

  List[Syllable] with start/end indices, shape, and feature ids.

You can plug this into Economy/Violations and Gate pipeline.

"""

from __future__ import annotations

from dataclasses import dataclass

from typing import List, Sequence, Tuple, Dict, Optional

# Simple vowel IDs (if zumar_ids is not available)
try:
    import zumar_ids as zid
    V_SUKUN = zid.V_SUKUN
    V_FATHA = zid.V_FATHA
    V_DAMMA = zid.V_DAMMA
    V_KASRA = zid.V_KASRA
    V_ALIF = zid.V_ALIF
    V_WAW = zid.V_WAW
    V_YA = zid.V_YA
    SYL_CV = zid.SYL_CV
    SYL_CVC = zid.SYL_CVC
    SYL_CVV = zid.SYL_CVV
    SYL_CVVC = getattr(zid, "SYL_CVVC", 3004)
except ImportError:
    # Fallback constants
    V_SUKUN = 0
    V_FATHA = 1
    V_DAMMA = 2
    V_KASRA = 3
    V_ALIF = 4
    V_WAW = 5
    V_YA = 6
    SYL_CV = 3001
    SYL_CVC = 3002
    SYL_CVV = 3003
    SYL_CVVC = 3004

# -------------------------

# Data structures

# -------------------------

@dataclass(frozen=True)
class SegCode:
    ch_id: int
    v_id: int
    diac_bits: int = 0
    role_id: int = 0

@dataclass(frozen=True)
class Syllable:
    start: int               # inclusive seg index
    end: int                 # inclusive seg index
    shape_id: int            # zid.SYL_CV / ...
    shape_str: str           # "CV", "CVC", ...
    onset: Tuple[int, ...]   # indices of consonants in onset
    nucleus: Tuple[int, ...] # indices of nucleus (1 consonant slot, but length info via vowel)
    coda: Tuple[int, ...]    # indices of consonants in coda

# -------------------------

# Helpers (vowel length)

# -------------------------

_SHORT_VOWELS = {V_FATHA, V_DAMMA, V_KASRA}
_LONG_VOWELS  = {V_ALIF, V_WAW, V_YA}
_SUKUN        = V_SUKUN

def vowel_length(v_id: int) -> int:
    """
    Returns:
      0 = no vowel (sukun)
      1 = short vowel
      2 = long vowel
    """
    if v_id == _SUKUN:
        return 0
    if v_id in _SHORT_VOWELS:
        return 1
    if v_id in _LONG_VOWELS:
        return 2
    # be strict
    raise ValueError(f"Unknown vowel id: {v_id}")

# -------------------------

# Syllable inventory mapping

# -------------------------

_SHAPE_TO_ID: Dict[str, int] = {
    "CV": SYL_CV,
    "CVC": SYL_CVC,
    "CVV": SYL_CVV,
    "CVVC": SYL_CVVC,
    # Optional (you can add more if your system supports)
    "CVCC": getattr(zid, "SYL_CVCC", 3005) if 'zid' in globals() else 3005,
    "CVVCC": getattr(zid, "SYL_CVVCC", 3006) if 'zid' in globals() else 3006,
}

# -------------------------

# Core syllabifier

# -------------------------

def syllabify_arabic(segs: Sequence[SegCode]) -> List[Syllable]:
    """
    Deterministic Arabic syllabification over SegCode tape.
    We treat each SegCode as a consonant slot C with:
      - v_id = 0   => consonant in coda (or onset cluster handling if needed)
      - v_id short => nucleus is on this consonant (CV or CVC)
      - v_id long  => nucleus long (CVV or CVVC)
    Basic constraints assumed:
      - Arabic syllable must have a vowel nucleus (short or long).
      - Coda can be 0, 1, or (optionally) 2 consonants depending on your choice.
      - We default to max coda = 1 (Classical-friendly). You can switch to 2.
    Returns list of syllables with indices and shape.
    """
    out: List[Syllable] = []
    n = len(segs)
    i = 0

    # Utility: find next nucleus (a consonant slot with vowel_length>0)
    def next_nucleus(start: int) -> Optional[int]:
        for k in range(start, n):
            if vowel_length(segs[k].v_id) > 0:
                return k
        return None

    while i < n:
        nuc = next_nucleus(i)
        if nuc is None:
            # trailing consonants with sukun only: attach to last coda if exists, else error syllable
            if not out:
                raise ValueError("No nucleus found in tape; cannot syllabify.")
            
            # attach remaining to last coda (optionally allow up to 2)
            last = out[-1]
            extra = tuple(range(i, n))
            
            # rebuild last with extended coda if allowed
            new_coda = last.coda + extra
            shape = last.shape_str + ("C" * len(extra))
            shape_id = _SHAPE_TO_ID.get(shape, last.shape_id)
            
            out[-1] = Syllable(
                start=last.start,
                end=n - 1,
                shape_id=shape_id,
                shape_str=shape,
                onset=last.onset,
                nucleus=last.nucleus,
                coda=new_coda,
            )
            break

        # Onset: everything before nucleus up to nuc (Arabic typically allows 1 onset; but clitics can create clusters)
        # We keep onset cluster as all consonants from i..nuc-1.
        onset_idx = tuple(range(i, nuc))
        nucleus_idx = (nuc,)
        vlen = vowel_length(segs[nuc].v_id)

        # Decide coda: lookahead after nucleus
        coda_idx: Tuple[int, ...] = ()
        end = nuc

        # After nucleus, if next consonant has sukun, it can be coda.
        # But if the consonant after that is also sukun, you can choose whether to allow CVCC.
        j = nuc + 1
        if j < n and vowel_length(segs[j].v_id) == 0:
            # candidate coda1
            coda1 = j
            # check if next after coda1 begins a new syllable nucleus
            j2 = j + 1
            if j2 < n and vowel_length(segs[j2].v_id) == 0:
                # two consecutive consonants after nucleus
                # Option A (default): keep only one coda (CVC / CVVC) and leave next consonant for onset of next syllable
                # Option B: allow CVCC/CVVCC if you want
                ALLOW_TWO_CODA = False
                if ALLOW_TWO_CODA:
                    coda_idx = (coda1, j2)
                    end = j2
                    i = j2 + 1
                else:
                    coda_idx = (coda1,)
                    end = coda1
                    i = coda1 + 1
            else:
                # single consonant after nucleus; if next is nucleus, keep coda1 in current syllable
                coda_idx = (coda1,)
                end = coda1
                i = coda1 + 1
        else:
            # open syllable
            end = nuc
            i = nuc + 1

        # Build shape string
        # onset cluster counts as "C" repeated; nucleus is V or VV; coda is C repeated
        onset_C = "C" * len(onset_idx) if onset_idx else "C"  # Arabic normally at least 1 onset; nucleus slot itself provides that
        
        # BUT our representation uses consonant slot at nucleus too; so onset should exclude nucleus.
        onset_C = "C" * len(onset_idx)
        nuc_V = "V" if vlen == 1 else "VV"
        coda_C = "C" * len(coda_idx)

        # If onset is empty, the nucleus consonant is the onset consonant in the orthographic slot.
        # So force onset to "C".
        shape = ("C" if len(onset_idx) == 0 else onset_C) + nuc_V + coda_C
        shape_id = _SHAPE_TO_ID.get(shape)

        if shape_id is None:
            # fall back to closest known
            if shape.startswith("C") and "VV" in shape and shape.endswith("C"):
                shape_id = _SHAPE_TO_ID.get("CVVC", SYL_CVVC)
            elif shape.startswith("C") and "VV" in shape:
                shape_id = _SHAPE_TO_ID.get("CVV", SYL_CVV)
            elif shape.endswith("C"):
                shape_id = _SHAPE_TO_ID.get("CVC", SYL_CVC)
            else:
                shape_id = _SHAPE_TO_ID.get("CV", SYL_CV)

        out.append(
            Syllable(
                start=(onset_idx[0] if onset_idx else nuc),
                end=end,
                shape_id=shape_id,
                shape_str=shape,
                onset=onset_idx if onset_idx else (nuc,),   # if no explicit onset, treat nucleus consonant as onset carrier
                nucleus=nucleus_idx,
                coda=coda_idx,
            )
        )

    return out

# -------------------------

# Example usage (debug)

# -------------------------

if __name__ == "__main__":
    # Example: كَتَبَ (C a, C a, C a) => syllables: CV.CV.CV or CVC.CV depending on analysis.
    # With our SegCode-per-letter, each letter has a vowel; no sukun codas => CV CV CV.
    
    # Simple character mapping for testing
    AR_CHAR_TO_ID = {
        "ك": 1, "ت": 2, "ب": 3, "ا": 4, "ل": 5, "م": 6, "ن": 7, "ر": 8, "س": 9, "ع": 10
    }
    
    segs = [
        SegCode(ch_id=AR_CHAR_TO_ID["ك"], v_id=V_FATHA),
        SegCode(ch_id=AR_CHAR_TO_ID["ت"], v_id=V_FATHA),
        SegCode(ch_id=AR_CHAR_TO_ID["ب"], v_id=V_FATHA),
    ]
    
    print("Testing syllabification for: كَتَبَ")
    print("=" * 60)
    
    syls = syllabify_arabic(segs)
    for i, s in enumerate(syls, 1):
        print(f"Syllable {i}: {s.shape_str}")
        print(f"  Start: {s.start}, End: {s.end}")
        print(f"  Onset: {s.onset}, Nucleus: {s.nucleus}, Coda: {s.coda}")
        print()
    
    # Test with long vowel
    print("\nTesting with long vowel: كَتَاب")
    print("=" * 60)
    segs2 = [
        SegCode(ch_id=AR_CHAR_TO_ID["ك"], v_id=V_FATHA),
        SegCode(ch_id=AR_CHAR_TO_ID["ت"], v_id=V_FATHA),
        SegCode(ch_id=AR_CHAR_TO_ID["ا"], v_id=V_ALIF),  # long vowel
        SegCode(ch_id=AR_CHAR_TO_ID["ب"], v_id=V_SUKUN),
    ]
    
    syls2 = syllabify_arabic(segs2)
    for i, s in enumerate(syls2, 1):
        print(f"Syllable {i}: {s.shape_str}")
        print(f"  Start: {s.start}, End: {s.end}")
        print(f"  Onset: {s.onset}, Nucleus: {s.nucleus}, Coda: {s.coda}")
        print()

