"""Root-to-pattern coverage utilities.

This module provides small helpers around Arabic roots and triliteral pattern
coverage derived from feature exports.

Expected CSV schemas:
- roots_lexicon.csv: columns [root, freq, notes]
- out_features.csv: columns [word, tri_name, ...]

Notes
- The default root extractor is a placeholder (first 3 letters after removing
  diacritics). Replace with a proper root extraction algorithm when available.
- CSV encoding defaults to utf-8-sig for Arabic compatibility.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

import pandas as pd

# Arabic diacritics (Harakat) and optional Tatweel
_DIACRITICS_RE = r"[\u064B-\u0652]"  # ً ٌ ٍ َ ُ ِ ْ ّ
tatweel = "\u0640"


def load_roots_lexicon(path_csv: str = "roots_lexicon.csv", encoding: str = "utf-8-sig") -> pd.DataFrame:
    """Load a simple roots lexicon CSV.

    Args:
        path_csv: Path to CSV with columns [root, freq, notes]
        encoding: CSV encoding (default utf-8-sig)

    Returns:
        DataFrame with normalized 'root' column (string, stripped).
        Empty DataFrame if file is missing.
    """
    p = Path(path_csv)
    if not p.exists():
        return pd.DataFrame(columns=["root", "freq", "notes"])

    df = pd.read_csv(p, encoding=encoding)
    if "root" not in df.columns:
        raise ValueError("roots_lexicon must contain a 'root' column")

    df["root"] = df["root"].astype(str).str.strip()
    return df


def build_root_pattern_coverage(
    features_csv: str = "out_features.csv",
    root_extractor: Optional[Callable[[str], str]] = None,
    encoding: str = "utf-8-sig",
) -> pd.DataFrame:
    """Build coverage table (root_guess, tri_name, count) from features CSV.

    Args:
        features_csv: Path to features CSV with at least [word, tri_name]
        root_extractor: Function mapping word->root string. Defaults to the
            first 3 letters after removing Arabic diacritics.
        encoding: CSV encoding (default utf-8-sig)

    Returns:
        DataFrame with columns [root_guess, tri_name, count] sorted by
        root_guess then descending count.
    """
    if root_extractor is None:
        def _default_root_extractor(w: str) -> str:
            return (w or "")[:3]

        root_extractor = _default_root_extractor

    df = pd.read_csv(features_csv, encoding=encoding)
    if "word" not in df.columns or "tri_name" not in df.columns:
        raise ValueError("features_csv must contain 'word' and 'tri_name' columns")

    # Remove diacritics and tatweel from words before extracting a naive root
    cleaned = (
        df["word"].astype(str)
        .str.replace(_DIACRITICS_RE, "", regex=True)
        .str.replace(tatweel, "", regex=False)
    )
    df["root_guess"] = cleaned.apply(root_extractor).astype(str).str.strip()

    cov = (
        df.groupby(["root_guess", "tri_name"]).size().reset_index(name="count")
        .sort_values(["root_guess", "count"], ascending=[True, False])
        .reset_index(drop=True)
    )
    return cov


def root_pattern_mask(root: str, tri_name: str, coverage_df: pd.DataFrame, min_count: int = 1) -> bool:
    """Allow/deny (root, tri_name) pair based on observed coverage.

    Args:
        root: Arabic root (or guessed root) string
        tri_name: Triliteral pattern name to check
        coverage_df: DataFrame from build_root_pattern_coverage()
        min_count: Minimum count threshold to allow

    Returns:
        True if the pair is observed with count >= min_count, else False.
    """
    if coverage_df.empty:
        return False
    if not {"root_guess", "tri_name", "count"}.issubset(coverage_df.columns):
        raise ValueError("coverage_df must contain columns: root_guess, tri_name, count")

    sub = coverage_df[(coverage_df["root_guess"] == root) & (coverage_df["tri_name"] == tri_name)]
    return (not sub.empty) and (int(sub["count"].iloc[0]) >= int(min_count))


__all__ = [
    "load_roots_lexicon",
    "build_root_pattern_coverage",
    "root_pattern_mask",
]


if __name__ == "__main__":
    # Lightweight demo: read CSV if present and print sample coverage
    import sys

    feats = sys.argv[1] if len(sys.argv) > 1 else "out_features.csv"
    try:
        cov = build_root_pattern_coverage(feats)
        print(cov.head(10))
    except FileNotFoundError:
        print(f"No such file: {feats}. Create a CSV with columns [word, tri_name].")
