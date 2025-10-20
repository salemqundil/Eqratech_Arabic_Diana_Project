from __future__ import annotations

from typing import List, Tuple

# Basic vowel markers produced by normalize.attach_diacritics
VOWELS = {"F", "D", "K"}


def syllabify(chars_with_diac: List[Tuple[str, str]]) -> List[str]:
    """Produce coarse syllables limited to six gates: CV, CVC, CVV, CVVC, CVCC, VC.

    Heuristics:
    - A nucleus is a consonant with a vowel diacritic F/K/D => forms CV with that consonant.
    - If next char is a long vowel letter (ا/و/ي) without its own diacritic => extend to CVV.
    - Closing consonants (without their own vowel) attach to form CVC/CVVC/CVCC.
    - Leading short vowels without a consonant fallback as VC.
    """
    out: List[str] = []
    i = 0
    n = len(chars_with_diac)

    def is_long_vowel(ch: str) -> bool:
        return ch in {"ا", "و", "ي"}

    while i < n:
        ch, di = chars_with_diac[i]
        # skip pure diac (shouldn't happen after attach) or spaces
        if ch.isspace():
            i += 1
            continue

        # VC case: diacritic on hamzat-wasl or stand-alone with no preceding base
        if di in VOWELS and (i == 0 or chars_with_diac[i - 1][1] in VOWELS):
            # treat as VC at this position
            syl = f"V{di}"
            out.append(syl.replace("F", "VC").replace("D", "VC").replace("K", "VC"))
            i += 1
            continue

        # CV nucleus
        if di in VOWELS:
            syl = "CV"
            j = i + 1
            # Optional long vowel to form CVV
            if j < n and is_long_vowel(chars_with_diac[j][0]) and not chars_with_diac[j][1]:
                syl = "CVV"
                j += 1
            # Closing consonants (no vowel)
            close = 0
            while j < n and close < 2 and chars_with_diac[j][1] == "":
                # stop if we hit whitespace
                if chars_with_diac[j][0].isspace():
                    break
                close += 1
                j += 1
            if close == 1:
                syl = syl + "C"  # CVC or CVVC
            elif close >= 2:
                syl = syl + "CC"  # CVCC or CVVCC -> clamp to CVCC
                syl = syl.replace("VVCC", "VVC")  # clamp
            out.append(syl)
            i = max(i + 1, j)
            continue

        # Consonant without vowel: try to attach to next nucleus or treat as onset
        i += 1

    return out
