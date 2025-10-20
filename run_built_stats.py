from __future__ import annotations

import argparse
import random
from pathlib import Path
from typing import List

import numpy as np

from src.normalize import tokenize_text, attach_diacritics
from src.syllables import syllabify
from src.detectors import tag_token
from src.stats import TokenFeatures, features_to_df, compute_built_stats, save_reports


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute rule-based built stats from an Arabic UTF-8 text.")
    parser.add_argument("--text", type=str, default="./data/quran-simple-enhanced.txt", help="Path to UTF-8 text file")
    parser.add_argument("--out", type=str, default="./reports/built_quran", help="Output directory for reports")
    parser.add_argument("--no-plots", action="store_true", help="Skip matplotlib plots")
    args = parser.parse_args()

    random.seed(42)
    np.random.seed(42)

    text_path = Path(args.text)
    if not text_path.exists():
        # Fallback tiny sample
        sample = "وَٱلْفَجْرِ وَلَيَالٍ عَشْرٍ إِنَّ رَبَّكَ لَبِٱلْمِرْصَادِ"
        text = sample
    else:
        text = load_text(text_path)

    tokens = tokenize_text(text)
    rows: List[TokenFeatures] = []
    diac_sequences: List[List[str]] = []
    syll_all: List[List[str]] = []

    for tok in tokens:
        chars_with_diac, diac_seq = attach_diacritics(tok)
        syls = syllabify(chars_with_diac)
        tags = tag_token(tok)
        rows.append(TokenFeatures(
            word=tok,
            pos=tags.get("pos"),
            i3rab=tags.get("i3rab"),
            pron_type=tags.get("pron_type"),
            pron_form=tags.get("pron_form"),
            verb_form=tags.get("verb_form"),
            verb_built_type=tags.get("verb_built_type"),
            diacritics=diac_seq,
            syllables=syls,
        ))
        diac_sequences.append(diac_seq)
        syll_all.append(syls)

    df = features_to_df(rows)
    summary, counts, examples = compute_built_stats(df)
    out_dir = Path(args.out)
    save_reports(out_dir, df, summary, counts, examples)

    if not args.no_plots:
        try:
            from src.plots import plot_diacritics, plot_syllables

            plot_diacritics(diac_sequences, str(out_dir / "diacritics.png"))
            plot_syllables(syll_all, str(out_dir / "syllables.png"))
        except Exception:
            # plotting is optional; ignore in minimal environments
            pass

    print("Saved:")
    print(out_dir / "out_features.csv")
    print(out_dir / "built_stats_summary.csv")
    print(out_dir / "built_stats_counts.csv")
    print(out_dir / "built_stats_examples.json")


if __name__ == "__main__":
    main()
