#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run morphology pipeline on the whole Quran and write one row per word to CSV.

Reads: data/quran-simple-clean.txt (format: sura|aya|verse_text per line)
Output: CSV with location first (sura, aya, word_index), then merged morphology
fields. Duplicate/similar columns removed (e.g. 'type' dropped, kept 'kind').

Usage (from repo root):
  PYTHONPATH=src python3 scripts/run_full_quran_analysis.py --output quran_analysis.csv
  PYTHONPATH=src python3 scripts/run_full_quran_analysis.py --quran data/quran-simple-clean.txt --output quran_analysis.csv
"""

import argparse
import csv
import sys
import unicodedata
from pathlib import Path


def _strip_diacritics(text: str) -> str:
    """Remove Arabic diacritics (combining marks)."""
    if not text:
        return ""
    return "".join(
        c for c in unicodedata.normalize("NFC", text)
        if unicodedata.category(c) != "Mn"
    )


# CSV columns: only these fields, in this order
FIELDNAMES = [
    "ID",
    "Sura_No",
    "Verse_No",
    "Word_No",
    "Segment_No",
    "Word",
    "Without_Diacritics",
    "Segmented_Word",
    "Morph_Tag",
    "Morph_Type",
    "Punctuation_Mark",
    "Invariable_Declinable",
    "Syntactic_Role",
    "Possessive_Construct",
    "Case_Mood",
    "Case_Mood_Marker",
    "Phrase",
    "Phrasal_Function",
    "Gloss",
]

DEFAULT_QURAN = Path(__file__).resolve().parent.parent / "data" / "quran-simple-clean.txt"


def parse_quran_line(line: str):
    """Parse one line: sura|aya|text. Returns (sura, aya, text) or None if invalid."""
    line = line.strip()
    if not line:
        return None
    parts = line.split("|", 2)
    if len(parts) < 3:
        return None
    try:
        sura = int(parts[0])
        aya = int(parts[1])
    except ValueError:
        return None
    return (sura, aya, parts[2].strip())


def build_row(
    sura: int,
    aya: int,
    word_index: int,
    w: dict,
    db,
    cv_pattern_fn,
    advanced_cv_pattern_fn,
    *,
    word_forms: list,
    isnadi_by_head: dict,
    isnadi_by_dep: dict,
) -> dict:
    """Build one CSV row for a word. Same logic as run_ayat_al_dayn_with_wazn_and_operators."""
    word = w.get("word", "")
    special = db.lookup(word)
    if not special:
        pair = db.lookup_with_prefix_stripping(word)
        if pair:
            special, _ = pair
    if not special:
        triple = db.lookup_with_clitic_stripping(word)
        if triple:
            special, _, _ = triple
    if special:
        op_analysis = db.get_analysis(special.word)
    else:
        op_analysis = None

    root = w.get("root")
    if isinstance(root, dict):
        root_str = root.get("formatted", "")
        root_type_str = root.get("type", "") or ""
    elif root and hasattr(root, "formatted"):
        root_str = root.formatted
        root_type_str = getattr(root, "root_type", "") or ""
        if hasattr(root_type_str, "name"):
            root_type_str = root_type_str.name
    else:
        root_str = ""
        root_type_str = ""

    pattern = w.get("pattern")
    if isinstance(pattern, dict):
        template = pattern.get("template", "") or ""
    elif pattern and hasattr(pattern, "template"):
        template = pattern.template or ""
    else:
        template = ""

    features = w.get("features") or {}
    case = features.get("case", "")
    number = features.get("number", "")
    gender = features.get("gender", "")
    definiteness = features.get("definite")
    if definiteness is not None:
        definiteness = "true" if definiteness else "false"
    else:
        definiteness = ""

    kind = w.get("kind", "")
    if op_analysis:
        category = op_analysis.get("category", "")
        grammatical_status = op_analysis.get("grammatical_status", "")
        is_mabni = "1" if op_analysis.get("is_mabni") else "0"
        function = getattr(special, "function", "") if special else ""
        syntactic_analysis = getattr(special, "syntactic_analysis", "") if special else ""
        semantic_analysis = getattr(special, "semantic_analysis", "") if special else ""
        examples = getattr(special, "examples", "") if special else ""
        word_type = getattr(special, "word_type", "") if special else ""
        if kind == "unknown":
            kind = "mabni"
            word_type = word_type or category or "mabni"
    else:
        category = ""
        grammatical_status = ""
        is_mabni = ""
        function = ""
        syntactic_analysis = ""
        semantic_analysis = ""
        examples = ""
        word_type = ""

    if kind == "operator" and w.get("operator"):
        op = w["operator"]
        if not category and op.get("category"):
            category = op.get("category", "")
        if not grammatical_status:
            grammatical_status = op.get("grammatical_status", "") or op.get("syntactic_analysis", "")
        if not function:
            function = op.get("function", "")
        if not syntactic_analysis:
            syntactic_analysis = op.get("syntactic_analysis", "") or op.get("grammatical_status", "")
        if not semantic_analysis:
            semantic_analysis = op.get("semantic_analysis", "")
        if not examples:
            examples = op.get("examples", "")
        if not word_type:
            word_type = op.get("word_type", "")
        if is_mabni == "" and op.get("is_mabni") is not None:
            is_mabni = "1" if op.get("is_mabni") else "0"

    pat = w.get("pattern")
    pat_cat = ""
    pat_type = ""
    if isinstance(pat, dict):
        pat_cat = (pat.get("category") or "").strip()
        pat_type = (pat.get("type") or "").strip()
    elif pat is not None and hasattr(pat, "pattern_type"):
        pat_type = getattr(pat.pattern_type, "value", str(pat.pattern_type))
        if hasattr(pat, "features") and isinstance(pat.features, dict):
            pat_cat = (pat.features.get("category") or "").strip()
    if not category:
        if kind == "verb":
            category = pat_cat or "verb"
        elif kind == "noun":
            category = pat_cat or "noun"
        elif kind == "name":
            category = "name"
        elif kind in ("particle", "demonstrative", "pronoun"):
            category = pat_cat or kind
        else:
            category = pat_cat or kind or ""
    if not word_type:
        word_type = pat_type or kind or ""

    try:
        cv = cv_pattern_fn(word) if word else ""
        cv_adv = advanced_cv_pattern_fn(word) if word else ""
    except Exception:
        cv = ""
        cv_adv = ""

    affixes = w.get("affixes") or {}
    prefix = affixes.get("prefix") or w.get("prefix", "") or ""
    suffix = affixes.get("suffix") or w.get("suffix", "") or ""
    if not prefix and w.get("operator", {}).get("prefix"):
        prefix = w["operator"]["prefix"]
    normalized = affixes.get("normalized") or w.get("normalized_word", "") or word
    stripped = affixes.get("stripped") or w.get("stripped_word", "") or ""
    stem = stripped or normalized or word
    if prefix is not None and not isinstance(prefix, str):
        prefix = str(prefix)
    if suffix is not None and not isinstance(suffix, str):
        suffix = str(suffix)
    prefix = prefix or ""
    suffix = suffix or ""

    i = word_index - 1
    head_links = isnadi_by_head.get(i, [])
    dep_links = isnadi_by_dep.get(i, [])
    all_links = head_links + dep_links
    if all_links:
        first = all_links[0]
        isnadi_role = first.get("role", "")
        isnadi_role_en = first.get("role_en", "")
        isnadi_relation = first.get("relation", "")
        isnadi_confidence = first.get("confidence", "")
        isnadi_reason = first.get("reason", "")
    else:
        isnadi_role = ""
        isnadi_role_en = ""
        isnadi_relation = ""
        isnadi_confidence = ""
        isnadi_reason = ""

    if i < len(word_forms):
        wf = word_forms[i]
        if not case and wf.get("case"):
            case = wf.get("case", "")

    # Requested schema fields (mapped from pipeline)
    without_diacritics = _strip_diacritics(word)
    segmented_word = normalized or word
    morph_tag = category or kind or ""
    morph_type = kind or ""
    invariable_declinable = "invariable" if is_mabni == "1" else ("declinable" if is_mabni == "0" else "")
    syntactic_role = syntactic_analysis or isnadi_role or ""
    case_mood = case or ""
    phrasal_function = function or ""
    gloss = semantic_analysis or ""

    return {
        "ID": 0,  # set in main
        "Sura_No": sura,
        "Verse_No": aya,
        "Word_No": word_index,
        "Segment_No": 1,
        "Word": word,
        "Without_Diacritics": without_diacritics,
        "Segmented_Word": segmented_word,
        "Morph_Tag": morph_tag,
        "Morph_Type": morph_type,
        "Punctuation_Mark": "",
        "Invariable_Declinable": invariable_declinable,
        "Syntactic_Role": syntactic_role,
        "Possessive_Construct": "",
        "Case_Mood": case_mood,
        "Case_Mood_Marker": "",
        "Phrase": "",
        "Phrasal_Function": phrasal_function,
        "Gloss": gloss,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--quran",
        type=Path,
        default=DEFAULT_QURAN,
        help=f"Quran text file (sura|aya|text per line). Default: {DEFAULT_QURAN}",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("quran_analysis.csv"),
        help="Output CSV file (default: quran_analysis.csv)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Process only first N verses (0 = all)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print progress per verse",
    )
    args = parser.parse_args()

    if not args.quran.exists():
        print(f"Quran file not found: {args.quran}", file=sys.stderr)
        return 1

    try:
        from fvafk.cli.main import MinimalCLI
        from fvafk.c2b.operators_particles_db import get_special_words_db
        from fvafk.c1.cv_pattern import cv_pattern, advanced_cv_pattern
    except ImportError as e:
        print(
            "Run from repo root with: PYTHONPATH=src python3 scripts/run_full_quran_analysis.py",
            file=sys.stderr,
        )
        print(f"Import error: {e}", file=sys.stderr)
        return 1

    cli = MinimalCLI(verbose=False, json_output=True)
    db = get_special_words_db()
    rows = []
    verse_count = 0

    with open(args.quran, encoding="utf-8") as f:
        for line in f:
            parsed = parse_quran_line(line)
            if not parsed:
                continue
            sura, aya, text = parsed
            if not text:
                continue
            if args.limit and verse_count >= args.limit:
                break
            verse_count += 1

            result = cli.run(
                text=text,
                verbose=False,
                morphology=True,
                multi_word=True,
            )
            words = result.get("c2b", {}).get("words") or []
            if not words:
                if args.verbose:
                    print(f"  {sura}:{aya} no words", file=sys.stderr)
                continue

            syntax = result.get("syntax") or {}
            word_forms = syntax.get("word_forms") or []
            isnadi_links = syntax.get("links", {}).get("isnadi") or []
            isnadi_by_head = {}
            isnadi_by_dep = {}
            for link in isnadi_links:
                head_id = link.get("head", {}).get("id", 0)
                dep_id = link.get("dependent", {}).get("id", 0)
                info = {
                    "role": link.get("type", ""),
                    "role_en": link.get("type_en", ""),
                    "confidence": link.get("confidence"),
                    "reason": link.get("reason", ""),
                }
                isnadi_by_head.setdefault(head_id, []).append({**info, "relation": "head"})
                isnadi_by_dep.setdefault(dep_id, []).append({**info, "relation": "dependent"})

            for idx, w in enumerate(words):
                row = build_row(
                    sura,
                    aya,
                    idx + 1,
                    w,
                    db,
                    cv_pattern,
                    advanced_cv_pattern,
                    word_forms=word_forms,
                    isnadi_by_head=isnadi_by_head,
                    isnadi_by_dep=isnadi_by_dep,
                )
                row["ID"] = len(rows) + 1
                rows.append(row)

            if args.verbose and verse_count % 500 == 0:
                print(f"  processed {verse_count} verses, {len(rows)} words", file=sys.stderr)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows ({verse_count} verses) to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
