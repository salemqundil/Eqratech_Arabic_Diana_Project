"""
enrich_operators_catalog.py
============================
Enrichment pipeline for data/operators_catalog_split.csv.

Produces two outputs:
  data/operators_catalog_split_enriched.csv
  data/operators_catalog_split_enriched.jsonl

Usage (from repo root):
  python scripts/enrich_operators_catalog.py
  python scripts/enrich_operators_catalog.py --input data/operators_catalog_split.csv \
      --quran-i3rab data/i3rab/quran_i3rab.csv \
      --out-csv data/operators_catalog_split_enriched.csv \
      --out-jsonl data/operators_catalog_split_enriched.jsonl

No external dependencies beyond the Python standard library.
Diacritics (tashkil) are preserved in all output fields.
"""

import argparse
import csv
import json
import os
import re
import unicodedata
from typing import Optional

# ---------------------------------------------------------------------------
# Paths (defaults relative to repository root)
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
_DEFAULT_INPUT = os.path.join(_REPO_ROOT, "data", "operators_catalog_split.csv")
_DEFAULT_QURAN_I3RAB = os.path.join(_REPO_ROOT, "data", "i3rab", "quran_i3rab.csv")
_DEFAULT_OUT_CSV = os.path.join(_REPO_ROOT, "data", "operators_catalog_split_enriched.csv")
_DEFAULT_OUT_JSONL = os.path.join(_REPO_ROOT, "data", "operators_catalog_split_enriched.jsonl")

# ---------------------------------------------------------------------------
# Module references (fixed base list)
# ---------------------------------------------------------------------------
_BASE_MODULES = [
    "src/fvafk/c2b/operators_catalog.py::OperatorsCatalog",
    "scripts/run_complete_snapshot.py::detect_operator",
]
_SIGNATURES_MODULE = (
    "src/syntax_theory/operators/operator_signatures.py::OperatorFactory.SIGNATURES"
)

# ---------------------------------------------------------------------------
# Effect signatures
# ---------------------------------------------------------------------------
_PREPOSITION_GROUP_AR = "الجر فقط الدلالية"

# Keywords in Note that indicate oath particle
_OATH_KEYWORDS = ("حرف قسم",)


def get_effect_signature(row: dict) -> str:
    """
    Return a coarse effect signature string for a given operator row.

    Rules:
      - Group Arabic Name == _PREPOSITION_GROUP_AR  → "GEN"
        * Unless Note contains an oath keyword          → "OATH_GEN"
      - Otherwise                                       → ""
    """
    note = row.get("Note", "") or ""
    arabic_group = row.get("Arabic Group Name", "") or ""

    if arabic_group.strip() == _PREPOSITION_GROUP_AR:
        for kw in _OATH_KEYWORDS:
            if kw in note:
                return "OATH_GEN"
        return "GEN"

    return ""


# ---------------------------------------------------------------------------
# Universal Arabic usage descriptions
# ---------------------------------------------------------------------------
_USAGE_BY_SIG: dict[str, str] = {
    "GEN": "حَرْفُ جَرٍّ: يَجُرُّ الِاسْمَ بَعْدَهُ (يُكْسِبُهُ حَالَةَ الْجَرِّ).",
    "OATH_GEN": "حَرْفُ قَسَمٍ: يَجُرُّ الِاسْمَ بَعْدَهُ وَيُفِيدُ التَّوْكِيدَ.",
}


def get_usage_universal_ar(sig: str) -> str:
    """Return the universal Arabic usage description for the given signature."""
    return _USAGE_BY_SIG.get(sig, "")


# ---------------------------------------------------------------------------
# I'rab templates
# ---------------------------------------------------------------------------
_TEMPLATE_BY_SIG: dict[str, str] = {
    "GEN": (
        " حَرْفُ جَرٍّ مَبْنِيٌّ عَلَى الْكَسْرِ، وَ( {NOUN} ) :"
        " اسْمٌ مَجْرُورٌ وَعَلَامَةُ جَرِّهِ الْكَسْرَةُ الظَّاهِرَةُ."
    ),
    "OATH_GEN": " حَرْفُ قَسَمٍ، وَ( {NOUN} ) : اسْمٌ مَجْرُورٌ.",
}


def get_i3rab_template(sig: str) -> str:
    """Return the i'rab template string for the given signature."""
    return _TEMPLATE_BY_SIG.get(sig, "")


# ---------------------------------------------------------------------------
# Diacritics stripping (for matching only – NEVER used on output)
# ---------------------------------------------------------------------------
_ARABIC_DIACRITICS = re.compile(
    "[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06dc\u06df-\u06e4\u06e7\u06e8"
    "\u06ea-\u06ed]"
)


def strip_diacritics(text: str) -> str:
    """Strip Arabic diacritics for internal matching ONLY. Never use on output."""
    return _ARABIC_DIACRITICS.sub("", text)


# ---------------------------------------------------------------------------
# Quran i'rab evidence extraction
# ---------------------------------------------------------------------------
_GEN_KEYWORDS = ("مَجْرُورٌ", "جَرِّهِ", "الْكَسْرَةُ", "حَرْفُ جَرٍّ")
# For OATH_GEN we reuse the same genitive cue words
_SIG_KEYWORDS: dict[str, tuple] = {
    "GEN": _GEN_KEYWORDS,
    "OATH_GEN": _GEN_KEYWORDS,
}

MAX_EVIDENCE_PHRASES = 5
_SNIPPET_MAX_CHARS = 160
_AR_COMMA = "،"


def _extract_snippet(text: str, keywords: tuple) -> str:
    """
    Extract a short snippet from *text* that contains one of the keywords.

    Strategy:
    1. Split on Arabic comma ،
    2. Return the first clause that contains a keyword.
    3. If no clause matches, return the first _SNIPPET_MAX_CHARS characters.

    Diacritics in the returned snippet are preserved exactly as-is.
    """
    clauses = text.split(_AR_COMMA)
    for clause in clauses:
        clause_stripped = clause.strip()
        if any(kw in clause_stripped for kw in keywords):
            return clause_stripped
    # Fallback: first portion of text
    return text.strip()[:_SNIPPET_MAX_CHARS]


def load_quran_i3rab_phrases(quran_i3rab_path: str, sig: str) -> list:
    """
    Load up to MAX_EVIDENCE_PHRASES deduplicated short phrases from
    quran_i3rab.csv whose i3rab column contains a keyword matching *sig*.

    Returns a list of strings (preserving original diacritics).
    """
    keywords = _SIG_KEYWORDS.get(sig)
    if not keywords:
        return []

    phrases = []
    seen: set = set()

    with open(quran_i3rab_path, encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            i3rab_text = row.get("i3rab", "") or ""
            if not any(kw in i3rab_text for kw in keywords):
                continue
            snippet = _extract_snippet(i3rab_text, keywords)
            if snippet and snippet not in seen:
                seen.add(snippet)
                phrases.append(snippet)
            if len(phrases) >= MAX_EVIDENCE_PHRASES:
                break

    return phrases


# ---------------------------------------------------------------------------
# Module list computation
# ---------------------------------------------------------------------------
def _load_operator_signatures_keys() -> set:
    """
    Load the bare (diacritic-stripped) keys from OperatorFactory.SIGNATURES
    at runtime, so we can decide whether to attach the module reference.

    Returns a set of diacritic-stripped strings.
    Returns an empty set if the module cannot be loaded.
    """
    src_path = os.path.join(_REPO_ROOT, "src")
    try:
        import sys

        inserted = False
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
            inserted = True
        try:
            from syntax_theory.operators.operator_signatures import OperatorFactory  # type: ignore[import]

            raw_keys = set(OperatorFactory.SIGNATURES.keys())
            return {strip_diacritics(k) for k in raw_keys}
        finally:
            if inserted and src_path in sys.path:
                sys.path.remove(src_path)
    except Exception:
        return set()


# Cache so we only load once
_OPERATOR_SIG_KEYS: Optional[set] = None


def get_project_modules(operator: str) -> list:
    """
    Return the list of project module references for the given operator.

    Diacritics are stripped ONLY for membership testing; they are never
    written back to any output field.
    """
    global _OPERATOR_SIG_KEYS
    if _OPERATOR_SIG_KEYS is None:
        _OPERATOR_SIG_KEYS = _load_operator_signatures_keys()

    modules = list(_BASE_MODULES)  # copy
    bare = strip_diacritics(operator.strip())
    if bare in _OPERATOR_SIG_KEYS:
        modules.append(_SIGNATURES_MODULE)
    return modules


# ---------------------------------------------------------------------------
# Main enrichment logic
# ---------------------------------------------------------------------------
def enrich_row(row: dict, quran_phrases_cache: dict) -> dict:
    """
    Compute and attach the five new fields to *row* (in-place copy).
    *quran_phrases_cache* is a dict sig → list[str] built once per run.
    """
    sig = get_effect_signature(row)
    phrases = quran_phrases_cache.get(sig, [])
    modules = get_project_modules(row.get("Operator", "") or "")

    enriched = dict(row)
    enriched["project_usage_universal_ar"] = get_usage_universal_ar(sig)
    enriched["project_i3rab_template"] = get_i3rab_template(sig)
    enriched["project_effect_signature"] = sig
    enriched["project_quran_evidence_phrases"] = phrases
    enriched["project_modules"] = modules
    return enriched


def build_quran_phrases_cache(quran_i3rab_path: str) -> dict:
    """Pre-load evidence phrases for each known signature."""
    cache: dict = {}
    for sig in ("GEN", "OATH_GEN"):
        cache[sig] = load_quran_i3rab_phrases(quran_i3rab_path, sig)
    cache[""] = []
    return cache


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------
_INPUT_COLS = [
    "Group Number",
    "Arabic Group Name",
    "English Group Name",
    "Operator",
    "Purpose/Usage",
    "Example",
    "Note",
]
_NEW_COLS = [
    "project_usage_universal_ar",
    "project_i3rab_template",
    "project_effect_signature",
    "project_quran_evidence_phrases",
    "project_modules",
]
_ALL_COLS = _INPUT_COLS + _NEW_COLS

_PHRASE_SEP = " | "


def read_input_csv(path: str) -> list:
    """Read the input CSV (robust to BOM)."""
    rows = []
    with open(path, encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rows.append(row)
    return rows


def write_enriched_csv(rows: list, path: str) -> None:
    """
    Write enriched rows to CSV.
    project_quran_evidence_phrases is serialized as phrases joined by _PHRASE_SEP.
    project_modules is a semicolon-separated string.
    """
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=_ALL_COLS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            out = dict(row)
            phrases = out.get("project_quran_evidence_phrases", [])
            out["project_quran_evidence_phrases"] = _PHRASE_SEP.join(phrases)
            modules = out.get("project_modules", [])
            out["project_modules"] = "; ".join(modules)
            writer.writerow(out)


def write_enriched_jsonl(rows: list, path: str) -> None:
    """
    Write enriched rows to JSONL.
    project_quran_evidence_phrases stays as a JSON array.
    project_modules stays as a JSON array.
    """
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for row in rows:
            obj = {col: row.get(col, "") for col in _INPUT_COLS}
            obj["project_usage_universal_ar"] = row.get("project_usage_universal_ar", "")
            obj["project_i3rab_template"] = row.get("project_i3rab_template", "")
            obj["project_effect_signature"] = row.get("project_effect_signature", "")
            # arrays in JSONL
            obj["project_quran_evidence_phrases"] = row.get(
                "project_quran_evidence_phrases", []
            )
            obj["project_modules"] = row.get("project_modules", [])
            fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Enrich operators_catalog_split.csv with project-specific fields."
    )
    parser.add_argument(
        "--input",
        default=_DEFAULT_INPUT,
        help="Path to input CSV (default: %(default)s)",
    )
    parser.add_argument(
        "--quran-i3rab",
        default=_DEFAULT_QURAN_I3RAB,
        help="Path to quran_i3rab.csv (default: %(default)s)",
    )
    parser.add_argument(
        "--out-csv",
        default=_DEFAULT_OUT_CSV,
        help="Path for enriched CSV output (default: %(default)s)",
    )
    parser.add_argument(
        "--out-jsonl",
        default=_DEFAULT_OUT_JSONL,
        help="Path for enriched JSONL output (default: %(default)s)",
    )
    args = parser.parse_args()

    print(f"Reading input: {args.input}")
    input_rows = read_input_csv(args.input)

    print(f"Loading Quran i3rab evidence: {args.quran_i3rab}")
    phrases_cache = build_quran_phrases_cache(args.quran_i3rab)

    print("Enriching rows …")
    enriched_rows = [enrich_row(row, phrases_cache) for row in input_rows]

    print(f"Writing CSV: {args.out_csv}")
    write_enriched_csv(enriched_rows, args.out_csv)

    print(f"Writing JSONL: {args.out_jsonl}")
    write_enriched_jsonl(enriched_rows, args.out_jsonl)

    print("Done.")


if __name__ == "__main__":
    main()
