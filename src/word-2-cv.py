#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import csv
import sys
import unicodedata

# -----------------------------
# Harakat / marks
# -----------------------------
FATHA = "\u064e"
DAMMA = "\u064f"
KASRA = "\u0650"
SUKUN = "\u0652"
SHADDA = "\u0651"
TANWIN_FATH = "\u064b"
TANWIN_DAMM = "\u064c"
TANWIN_KASR = "\u064d"

SHORT_VOWELS = {FATHA, DAMMA, KASRA, TANWIN_FATH, TANWIN_DAMM, TANWIN_KASR}
ALL_MARKS = {FATHA, DAMMA, KASRA, SUKUN, SHADDA, TANWIN_FATH, TANWIN_DAMM, TANWIN_KASR}

# Long vowels
ALIF = "\u0627"
WAW = "\u0648"
YA = "\u064a"
ALIF_MAQSURA = "\u0649"

ALIF_MADDA = "\u0622"   # آ
ALIF_WASLA = "\u0671"   # ٱ

# -----------------------------
# Basic helpers
# -----------------------------
def is_arabic_letter(ch: str) -> bool:
    return ("\u0600" <= ch <= "\u06FF") and unicodedata.category(ch).startswith("L")

def normalize_word(w: str) -> str:
    w = unicodedata.normalize("NFC", str(w))
    w = w.replace("\u0640", "")  # tatweel
    return w.strip()

def strip_harakat_only(w: str) -> str:
    return "".join(ch for ch in w if not (unicodedata.combining(ch) and ch in ALL_MARKS))

def strip_all_marks(w: str) -> str:
    return "".join(ch for ch in w if not (unicodedata.combining(ch) and ch in ALL_MARKS))

def split_letters_and_marks(text: str):
    out = []
    base = None
    marks = []
    for ch in text:
        if unicodedata.combining(ch) != 0 and ch in ALL_MARKS:
            if base is not None:
                marks.append(ch)
            continue
        if base is not None:
            out.append((base, marks))
        base = ch
        marks = []
    if base is not None:
        out.append((base, marks))
    return out

def expand_shadda(units):
    expanded = []
    for letter, marks in units:
        if SHADDA in marks:
            second_marks = [m for m in marks if m != SHADDA]
            expanded.append((letter, [SUKUN]))       # first consonant
            expanded.append((letter, second_marks))  # second consonant with remaining marks
        else:
            expanded.append((letter, marks))
    return expanded

def has_any(marks, s):
    return any(m in s for m in marks)

# -----------------------------
# Missing-harakat normalization (your last correction)
# -----------------------------
def normalize_missing_harakat(word: str) -> str:
    """
    Fix cases where your source text lost harakat:
    - ولا -> وَلَا
    - لْيَ... -> لِيَ... (lam is kasra, not sukun)
    """
    w = normalize_word(word)

    if w == "ولا":
        return "و" + FATHA + "ل" + FATHA + "ا"   # وَلَا

    if w.startswith("ل" + SUKUN + "ي" + FATHA):
        return "ل" + KASRA + w[2:]  # replace "لْ" with "لِ"

    return w

# -----------------------------
# Exclusions (your request)
# -----------------------------
EXCLUDE_EXACT = {"حم", "دمت", "ص", "طس", "طسم", "طه", "عسق", "على", "ق"}
MUQATTAAT = {
    "الم", "المص", "الر", "المر", "كهيعص", "طه", "طسم", "طس", "يس",
    "حم", "حم عسق", "عسق", "ق", "ن", "ص"
}
MUQATTAAT_NOSPACE = {s.replace(" ", "") for s in MUQATTAAT}

def should_exclude(token: str) -> bool:
    w = normalize_word(token)
    bare = strip_harakat_only(w)
    bare_nospace = bare.replace(" ", "")

    if re.search(r"[A-Za-z]", w):
        return True
    if bare in EXCLUDE_EXACT:
        return True
    if len(bare) == 1 and is_arabic_letter(bare):
        return True
    if bare_nospace in MUQATTAAT_NOSPACE:
        return True
    return False

# -----------------------------
# Initial Hamza Normalization
# -----------------------------
WASL_NOUNS = {"اسم", "ابن", "ابنة", "امرؤ", "امرأة", "اثنان", "اثنتان", "ايم", "ايمن"}

def normalize_initial_hamza(word: str) -> str:
    """
    If word starts with bare 'ا' (no hamza), decide:
      - wasl  -> convert to 'ٱ'
      - qat'  -> convert to 'أ'
    """
    w = normalize_word(word)
    bare = strip_all_marks(w)
    if not bare:
        return w

    if bare[0] in {"أ", "إ", "آ", ALIF_WASLA}:
        return w
    if bare[0] != "ا":
        return w

    is_wasl = False
    if bare.startswith("ال"):
        is_wasl = True
    elif bare.startswith(("است", "ان", "افت", "اف")):
        is_wasl = True
    else:
        for n in WASL_NOUNS:
            if bare.startswith(n):
                is_wasl = True
                break

    idx = w.find("ا")
    if idx == -1:
        return w

    return w[:idx] + (ALIF_WASLA if is_wasl else "أ") + w[idx + 1 :]

# -----------------------------
# CV generator
# -----------------------------
def cv_pattern(word: str) -> str:
    """
    - WRITTEN harakat only
    - Shadda => CC
    - Madd letters => V only if previous has matching written haraka
    - Initial (ٱ/أ/إ/آ) => force starting CV (C+V) and remove that letter unit
    """
    w = normalize_word(word)
    units = expand_shadda(split_letters_and_marks(w))

    out = []
    prev_marks = []

    first_idx = None
    for i, (ch, _m) in enumerate(units):
        if is_arabic_letter(ch):
            first_idx = i
            break

    if first_idx is not None:
        first_letter = units[first_idx][0]
        if first_letter in {ALIF_WASLA, "أ", "إ", "آ"}:
            out.extend(["C", "V"])
            units = units[:first_idx] + units[first_idx + 1 :]

    for letter, marks in units:
        if not is_arabic_letter(letter):
            prev_marks = marks
            continue

        is_madd = False
        if letter == ALIF:
            is_madd = has_any(prev_marks, {FATHA, TANWIN_FATH})
        elif letter == WAW:
            is_madd = has_any(prev_marks, {DAMMA, TANWIN_DAMM})
        elif letter == YA or letter == ALIF_MAQSURA:
            is_madd = has_any(prev_marks, {KASRA, TANWIN_KASR})

        if letter == ALIF_MADDA:
            out.append("C")
        elif is_madd:
            out.append("V")
        else:
            out.append("C")
            if has_any(marks, SHORT_VOWELS):
                out.append("V")

        prev_marks = marks

    return "".join(out)

# -----------------------------
# CV-law validator
# -----------------------------
def follows_cv_law(cv: str):
    if not cv:
        return False, "empty_cv"
    if len(cv) < 2 or cv[0] != "C" or cv[1] != "V":
        return False, "does_not_start_with_CV"

    i = 0
    while True:
        k = None
        for j in range(i + 2, len(cv) - 1):
            if cv[j] == "C" and cv[j + 1] == "V":
                k = j
                break
        if k is None:
            return True, "ok"
        i = k

# -----------------------------
# TXT tokenization
# -----------------------------
ARABIC_TOKEN_RE = re.compile(r"[\u0600-\u06FF]+", re.UNICODE)

def extract_unique_words(txt_path: str):
    unique = set()
    with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            for m in ARABIC_TOKEN_RE.finditer(line):
                w = normalize_word(m.group(0))
                if w:
                    unique.add(w)
    return sorted(unique)

def write_csv(rows, out_path, header):
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(header)
        for r in rows:
            wr.writerow(r)

# -----------------------------
# Main
# -----------------------------
def main():
    if len(sys.argv) != 2:
        print("Usage: python3 one_shot_word2cv.py /path/to/input.txt")
        sys.exit(1)

    input_txt = sys.argv[1]
    words = extract_unique_words(input_txt)

    working = []
    notworking = []
    excluded = []

    for w in words:
        if should_exclude(w):
            excluded.append((w,))
            continue

        w_norm = normalize_initial_hamza(w)
        w_norm = normalize_missing_harakat(w_norm)  # ✅ THIS WAS MISSING
        cv = cv_pattern(w_norm)
        ok, reason = follows_cv_law(cv)

        if ok:
            working.append((w, w_norm, cv))
        else:
            notworking.append((w, w_norm, cv, reason))

    write_csv(working, "cv-working.csv", ["word_original", "word_normalized", "cv"])
    write_csv(notworking, "cv-notworking.csv", ["word_original", "word_normalized", "cv", "reason"])
    write_csv(excluded, "cv-excluded.csv", ["word"])

    print(f"Unique words: {len(words)}")
    print(f"Excluded: {len(excluded)} -> cv-excluded.csv")
    print(f"Working: {len(working)} -> cv-working.csv")
    print(f"Not working: {len(notworking)} -> cv-notworking.csv")

if __name__ == "__main__":
    main()
