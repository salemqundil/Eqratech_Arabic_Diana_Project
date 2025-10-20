from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import json

from src.normalize import strip_diacritics, attach_diacritics
from src.syllables import syllabify
from src.detectors import (
    is_detached_pronoun,
    match_attached_pronoun,
    is_particle,
    is_built_noun_other,
    tag_token,
)


def is_noun_muarab(token: str) -> bool:
    # Exclude built nouns and pronouns/particles
    if is_detached_pronoun(token) or match_attached_pronoun(token):
        return False
    if is_particle(token) or is_built_noun_other(token):
        return False
    # Exclude verbs via tagger heuristic
    tags = tag_token(token)
    pos = tags.get("pos")
    if pos == "verb":
        return False
    return True


def analyze(text: str) -> Tuple[List[Dict], Dict]:
    # Split on whitespace; keep diacritics in tokens
    words = [w for w in text.split() if w]
    N = len(words)

    rows: List[Dict] = []
    diac_counts_global: Dict[str, int] = {"F": 0, "K": 0, "D": 0, "S": 0}
    gate_counts_global: Dict[str, int] = {g: 0 for g in ("CV", "CVC", "CVV", "CVVC", "CVCC", "VC")}

    for w in words:
        if not is_noun_muarab(w):
            continue
        chars_with_diac, diac_seq = attach_diacritics(w)
        gates = syllabify([(ch, di or "") for ch, di in chars_with_diac])

        for d in diac_seq:
            if d in diac_counts_global:
                diac_counts_global[d] += 1
        for g in gates:
            if g in gate_counts_global:
                gate_counts_global[g] += 1

        # final diacritic (approximate case ending): last F/K/D/S if present
        final_diac = next((di for _ch, di in reversed(chars_with_diac) if di in ("F", "K", "D", "S")), None)

        rows.append({
            "word": w,
            "diacritics": diac_seq,
            "syllables": gates,
            "final_diac": final_diac,
        })

    summary = {
        "total_tokens": N,
        "noun_muarab_tokens": len(rows),
        "final_diac_%": _normalize_percent({k: 0 for k in ("F", "K", "D", "S")}, [r["final_diac"] for r in rows]),
        "diacritics_counts": diac_counts_global,
        "syllable_gates_counts": gate_counts_global,
    }
    return rows, summary


def _normalize_percent(base_counts: Dict[str, int], finals: List[str | None]) -> Dict[str, float]:
    counts = dict(base_counts)
    total = 0
    for f in finals:
        if f and f in counts:
            counts[f] += 1
            total += 1
    if total == 0:
        return {k: 0.0 for k in counts}
    return {k: round(100.0 * v / total, 3) for k, v in counts.items()}


def main() -> None:
    p = argparse.ArgumentParser(description="Compute mu'rab noun phoneme/diac/syllable stats from a UTF-8 Arabic text.")
    p.add_argument("--text", type=str, default="./data/quran-simple-enhanced.txt", help="Path to UTF-8 text file")
    p.add_argument("--out", type=str, default="./reports/noun_muarab", help="Output directory prefix")
    args = p.parse_args()

    text_path = Path(args.text)
    if not text_path.exists():
        print(f"Input file not found: {text_path}")
        return
    text = text_path.read_text(encoding="utf-8", errors="ignore")

    rows, summary = analyze(text)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows_path = out_dir / "noun_rows.csv"
    summary_path = out_dir / "noun_summary.json"

    # Minimal CSV write (no pandas dependency required here)
    import csv

    with open(rows_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["word", "diacritics", "syllables", "final_diac"])
        w.writeheader()
        for r in rows:
            w.writerow({
                "word": r["word"],
                "diacritics": " ".join(r["diacritics"]),
                "syllables": " ".join(r["syllables"]),
                "final_diac": r["final_diac"] or "",
            })

    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Saved:")
    print(rows_path)
    print(summary_path)


if __name__ == "__main__":
    main()
