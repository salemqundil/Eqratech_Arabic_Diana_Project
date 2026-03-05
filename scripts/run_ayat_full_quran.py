#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full Quran pipeline: تحليل القرآن كاملاً — نفس منطق run_ayat_al_dayn_with_wazn_and_operators
مع تحسين استخراج الجذر (RootResolver: cli_verified → wazn_resolved → heuristic).

يدمج:
  - البنية والأعمدة من run_ayat_al_dayn_with_wazn_and_operators-old.py
  - تحسين الجذر من run_ayat_al_dayn_with_wazn_and_operators.py (RootResolver + أوزان + roots_db)

Input: --input (default data/quran-simple-clean.txt). أسطر بصيغة sura|aya|verse_text.

Usage (from repo root):
  PYTHONPATH=src python3 scripts/run_ayat_full_quran.py --input data/quran-simple-clean.txt --output out.csv
  PYTHONPATH=src python3 scripts/run_ayat_full_quran.py --output full_quran.csv --show-root-source
"""

import argparse
import csv
import sys
from pathlib import Path

DEFAULT_INPUT = Path("data/quran-simple-clean.txt")
DEFAULT_PATTERNS = Path("data/awzan_merged_final.csv")
DEFAULT_ROOTS = Path("data/arabic_roots.csv")


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


def read_input(path: Path):
    """
    Read input file. If lines look like sura|aya|text, return list of (sura, aya, text).
    Otherwise return [(0, 0, full_content)] so the whole file is one block.
    """
    text = path.read_text(encoding="utf-8")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return [(0, 0, "")]
    parsed = []
    for ln in lines:
        p = parse_quran_line(ln)
        if p is None:
            # Not Quran format: treat entire file as one text
            return [(0, 0, text.strip())]
        parsed.append(p)
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Input text file (default: {DEFAULT_INPUT}). Use sura|aya|text per line for Quran.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("out.csv"),
        help="Output CSV file (default: out.csv)",
    )
    parser.add_argument(
        "--patterns",
        type=Path,
        default=DEFAULT_PATTERNS,
        help=f"Awzan CSV for RootResolver (default: {DEFAULT_PATTERNS})",
    )
    parser.add_argument(
        "--roots",
        type=Path,
        default=DEFAULT_ROOTS,
        help=f"Roots CSV for RootsDB (default: {DEFAULT_ROOTS})",
    )
    parser.add_argument(
        "--show-root-source",
        action="store_true",
        default=False,
        help="Add root_source/root_wazn/root_confidence columns to output CSV",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Input file not found: {args.input}", file=sys.stderr)
        return 1

    try:
        from fvafk.cli.main import MinimalCLI
        from fvafk.c2b.operators_particles_db import get_special_words_db
        from fvafk.c2b.special_words_catalog import get_special_words_catalog
        from fvafk.c1.cv_pattern import cv_pattern, advanced_cv_pattern
    except ImportError as e:
        print(
            "Run from repo root with: PYTHONPATH=src python3 scripts/run_ayat_full_quran.py ...",
            file=sys.stderr,
        )
        print(f"Import error: {e}", file=sys.stderr)
        return 1

    # بناء الـ resolver — اختياري: لو الملفات غير موجودة نكمل بدونه
    resolver = None
    if args.patterns.exists() and args.roots.exists():
        try:
            from fvafk.c2b.root_resolver.resolver import RootResolver
            print(f"[resolver] patterns CSV: {args.patterns}", file=sys.stderr)
            resolver = RootResolver.build(
                patterns_csv=args.patterns,
                roots_csv=args.roots,
            )
            n_pat = getattr(getattr(resolver, "_wazn", None), "patterns_count", 0)
            n_roots = len(getattr(resolver, "_db", []))
            print(f"[resolver] loaded: {n_pat} patterns, {n_roots} roots", file=sys.stderr)
        except Exception as e:
            print(f"[resolver] failed to load, using CLI roots only: {e}", file=sys.stderr)
    else:
        missing = [p for p in [args.patterns, args.roots] if not p.exists()]
        print(f"[resolver] skipped — missing: {missing}", file=sys.stderr)

    verses = read_input(args.input)
    cli = MinimalCLI(verbose=False, json_output=True)
    db = get_special_words_db()
    catalog = get_special_words_catalog()

    # تصحيح stripped الناقص من CLI لأفعال شائعة (نزّلنا→نزل، قلنا→قول)
    def _bare(t):
        return "".join(
            c for c in (t or "").replace("-", "").strip()
            if not (0x064B <= ord(c) <= 0x0652 or ord(c) == 0x0670)
        ).strip()

    # تصحيح stripped (مفتاح = word_bare). أفعال مجزومة/معتل ناقص من imperative_rules JSON
    STRIPPED_CORRECTIONS = {
        "نزلنا": "نزل", "نزّلنا": "نزل", "ينزل": "نزل",
        "قلنا": "قول", "قولنا": "قول", "قل": "قول", "يقل": "قول",
        "يوم": "يوم",
        "موت": "موت",
        "تولوا": "ولي",
        "بينا": "بين",
    }
    try:
        from fvafk.c2b.imperative_rules import get_defective_imperative_stems
        STRIPPED_CORRECTIONS = {**STRIPPED_CORRECTIONS, **get_defective_imperative_stems()}
    except Exception:
        STRIPPED_CORRECTIONS.update({"تر": "رأي", "تك": "كون", "يك": "كون", "هب": "وهب"})

    fieldnames = [
        "sura",
        "aya",
        "word_index",
        "word",
        "cv",
        "cv_advanced",
        "root",
        "root_type",
        "category",
        "is_mabni",
        "kind",
        "type",
        "template",
        "prefix",
        "suffix",
        "case",
        "number",
        "gender",
        "definiteness",
        "grammatical_status",
        "function",
        "word_type",
        "stem",
        "normalized",
        "stripped",
        "syntactic_analysis",
        "semantic_analysis",
        "examples",
        "compound_operator",
        "isnadi_role",
        "isnadi_role_en",
        "isnadi_relation",
        "isnadi_confidence",
        "isnadi_reason",
    ]
    if args.show_root_source:
        fieldnames += ["root_source", "root_wazn", "root_confidence"]

    rows = []
    for sura, aya, text in verses:
        if not text:
            continue
        result = cli.run(
            text=text,
            verbose=False,
            morphology=True,
            multi_word=True,
        )
        words = result.get("c2b", {}).get("words") or []
        if not words:
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

        for i, w in enumerate(words):
            word = w.get("word", "")
            # Operator/particle from DB (prefix stripping e.g. وَاللَّهُ; clitic stripping e.g. فَإِنَّهُ)
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

            # Rule-based category/type from morphology (kind + pattern)
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

            # CV patterns
            try:
                cv = cv_pattern(word) if word else ""
                cv_adv = advanced_cv_pattern(word) if word else ""
            except Exception:
                cv = ""
                cv_adv = ""

            # Prefix/suffix from affixes or operator
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

            # أسماء golden_name (لا جذر) — لا نمرّر للـ resolver
            root_source = ""
            root_wazn = ""
            root_confidence = ""
            catalog_info = catalog.classify(word) if word else None
            if catalog_info and catalog_info.get("kind") == "excluded_name":
                root_str = ""
                if args.show_root_source:
                    root_source = "no_root"
                    root_confidence = "1.00"
            elif resolver is not None:
                # تصحيح stripped المعروف ناقصاً من CLI
                word_bare = _bare(word)
                use_stripped = STRIPPED_CORRECTIONS.get(word_bare, stripped)
                resolved = resolver.resolve(
                    word=word,
                    stripped=use_stripped,
                    cli_root=root_str,
                    kind=kind,
                    show_source=args.show_root_source,
                )
                # resolve() always returns canonicalized root; use as-is for CSV
                root_str = resolved.root_formatted or resolved.root or ""
                if args.show_root_source:
                    root_source = resolved.source
                    root_wazn = resolved.wazn
                    root_confidence = f"{resolved.confidence:.2f}" if resolved.confidence else ""

            # Isnadi for this word index
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

            row = {
                "sura": sura,
                "aya": aya,
                "word_index": i + 1,
                "word": word,
                "cv": cv,
                "cv_advanced": cv_adv,
                "root": root_str,
                "root_type": root_type_str,
                "category": category,
                "is_mabni": is_mabni,
                "kind": kind,
                "type": kind,
                "template": template,
                "prefix": prefix,
                "suffix": suffix,
                "case": case,
                "number": number,
                "gender": gender,
                "definiteness": definiteness,
                "grammatical_status": grammatical_status,
                "function": function,
                "word_type": word_type or kind,
                "stem": stem,
                "normalized": normalized,
                "stripped": stripped,
                "syntactic_analysis": syntactic_analysis,
                "semantic_analysis": semantic_analysis,
                "examples": examples,
                "compound_operator": "",
                "isnadi_role": isnadi_role,
                "isnadi_role_en": isnadi_role_en,
                "isnadi_relation": isnadi_relation,
                "isnadi_confidence": str(isnadi_confidence) if isnadi_confidence else "",
                "isnadi_reason": isnadi_reason,
            }
            if args.show_root_source:
                row["root_source"] = root_source
                row["root_wazn"] = root_wazn
                row["root_confidence"] = root_confidence
            rows.append(row)

    if not rows:
        print("No words produced from input.", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
