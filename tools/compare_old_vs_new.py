"""
Phase 8.2 utility: compare CV patterns between engines.

Old  = engine="c2a"         (C1Encoder + C2a gates → CV from final segments)
New  = engine="phonology_v2" (Phonology V2 syllable lattice → CV)

This script prints a side-by-side table per Arabic token in the input.
"""

from __future__ import annotations

import argparse
from typing import Any, Dict, List, Optional, Tuple

from fvafk.c1.cv_pattern import analyze_text_for_cv_after_phonology
from fvafk.c2b.word_boundary import WordBoundaryDetector


def _one_word_cv(token: str, engine: str) -> Optional[Dict[str, str]]:
    r = analyze_text_for_cv_after_phonology(token, engine=engine)
    words = r.get("words") or []
    if not words:
        return None
    return words[0]  # single-token call => at most one result


def _format_row(cols: List[str], widths: List[int]) -> str:
    parts = []
    for c, w in zip(cols, widths):
        parts.append(c.ljust(w))
    return " | ".join(parts)


def compare_text(text: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    spans = WordBoundaryDetector().detect(text)
    rows: List[Dict[str, Any]] = []
    excluded: List[str] = []

    for sp in spans:
        tok = sp.token
        c2a = _one_word_cv(tok, "c2a")
        v2 = _one_word_cv(tok, "phonology_v2")

        if c2a is None and v2 is None:
            excluded.append(tok)
            continue

        rows.append(
            {
                "token": tok,
                "span": (sp.start, sp.end),
                "c2a": c2a,
                "phonology_v2": v2,
                "same": (c2a == v2),
            }
        )

    return rows, excluded


def main() -> int:
    p = argparse.ArgumentParser(description="Compare CV outputs: c2a vs phonology_v2.")
    p.add_argument("text", help="Arabic text (diacritized recommended)")
    args = p.parse_args()

    rows, excluded = compare_text(args.text)

    headers = ["token", "span", "c2a.cv", "c2a.cv_advanced", "v2.cv", "v2.cv_advanced", "same?"]
    data_rows: List[List[str]] = []
    for r in rows:
        c2a = r["c2a"] or {}
        v2 = r["phonology_v2"] or {}
        data_rows.append(
            [
                r["token"],
                f"{r['span'][0]}:{r['span'][1]}",
                c2a.get("cv", ""),
                c2a.get("cv_advanced", ""),
                v2.get("cv", ""),
                v2.get("cv_advanced", ""),
                "YES" if r["same"] else "NO",
            ]
        )

    widths = [len(h) for h in headers]
    for row in data_rows:
        widths = [max(w, len(cell)) for w, cell in zip(widths, row)]

    print(_format_row(headers, widths))
    print(_format_row(["-" * w for w in widths], widths))
    for row in data_rows:
        print(_format_row(row, widths))

    if excluded:
        print("\nExcluded/ignored tokens (no CV computed):")
        for t in excluded:
            print(f"- {t}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

