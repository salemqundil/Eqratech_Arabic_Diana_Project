from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pandas as pd


@dataclass
class TokenFeatures:
    word: str
    pos: str | None
    i3rab: str | None
    pron_type: str | None
    pron_form: str | None
    verb_form: str | None
    verb_built_type: str | None
    diacritics: List[str]
    syllables: List[str]


def features_to_df(rows: Iterable[TokenFeatures]) -> pd.DataFrame:
    recs = []
    for r in rows:
        recs.append({
            "word": r.word,
            "pos": r.pos,
            "i3rab": r.i3rab,
            "pron_type": r.pron_type,
            "pron_form": r.pron_form,
            "verb_form": r.verb_form,
            "verb_built_type": r.verb_built_type,
            "diacritics": r.diacritics,
            "syllables": r.syllables,
        })
    return pd.DataFrame.from_records(recs)


def compute_built_stats(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, List[str]]]:
    # Count categories
    built_mask = (df["pos"] == "pronoun") | (df["pos"] == "particle") | ((df["pos"] == "verb") & (df["verb_built_type"].notna()))
    total = len(df)
    built_total = int(built_mask.sum())

    counts = Counter()
    counts.update(df.loc[df["pos"] == "pronoun", "pos"].tolist())
    counts.update(df.loc[df["pos"] == "particle", "pos"].tolist())
    counts.update(df.loc[(df["pos"] == "verb") & (df["verb_built_type"].notna()), "verb_built_type"].fillna("verb").tolist())

    counts_df = pd.DataFrame({"category": list(counts.keys()), "count": list(counts.values())})
    summary_df = pd.DataFrame({
        "metric": ["tokens", "built_tokens", "built_ratio"],
        "value": [total, built_total, (built_total / total) if total else 0.0],
    })

    # Examples
    examples: Dict[str, List[str]] = {
        "pronoun": df.loc[df["pos"] == "pronoun", "word"].head(12).tolist(),
        "particle": df.loc[df["pos"] == "particle", "word"].head(12).tolist(),
        "verb_built": df.loc[(df["pos"] == "verb") & (df["verb_built_type"].notna()), "word"].head(12).tolist(),
    }

    return summary_df, counts_df, examples


def save_reports(out_dir: Path, df: pd.DataFrame, summary: pd.DataFrame, counts: pd.DataFrame, examples: Dict[str, List[str]]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "out_features.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(out_dir / "built_stats_summary.csv", index=False, encoding="utf-8-sig")
    counts.to_csv(out_dir / "built_stats_counts.csv", index=False, encoding="utf-8-sig")
    (out_dir / "built_stats_examples.json").write_text(json.dumps(examples, ensure_ascii=False, indent=2), encoding="utf-8")
