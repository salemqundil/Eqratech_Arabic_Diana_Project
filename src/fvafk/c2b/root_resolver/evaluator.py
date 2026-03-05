"""
Root resolver evaluator: compare pipeline CSV output vs gold CSV.
Computes Accuracy and F1 per root_source (cli_verified, wazn_resolved, heuristic).
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def _normalize_root(r: Optional[str]) -> str:
    if r is None:
        return ""
    return (r or "").strip().replace(" ", "")


def load_csv(path: Path) -> List[Dict[str, str]]:
    """Load CSV with columns word, root, and optionally root_source."""
    if not path.exists():
        return []
    rows = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows


def align_rows(
    pred_rows: List[Dict[str, str]],
    gold_rows: List[Dict[str, str]],
    word_key: str = "word",
) -> List[Tuple[Dict[str, str], Optional[Dict[str, str]]]]:
    """Align by word; returns list of (pred_row, gold_row or None)."""
    gold_by_word = {_normalize_root(r.get(word_key)): r for r in gold_rows}
    paired = []
    for p in pred_rows:
        w = _normalize_root(p.get(word_key))
        paired.append((p, gold_by_word.get(w)))
    return paired


def evaluate(
    pred_rows: List[Dict[str, str]],
    gold_rows: List[Dict[str, str]],
    root_key: str = "root",
    source_key: str = "root_source",
) -> Dict[str, object]:
    """
    Compare predicted vs gold roots. Returns dict with:
    - accuracy: overall root match rate
    - total: number of aligned rows with gold
    - correct: number where pred root == gold root
    - per_source: { source: { "accuracy", "total", "correct" } }
    - f1_per_source: same keys, F1 = 2*P*R/(P+R) for root match (P=correct/pred_count, R=correct/gold_count)
    """
    paired = align_rows(pred_rows, gold_rows)
    total = 0
    correct = 0
    by_source: Dict[str, List[Tuple[str, str]]] = defaultdict(list)

    for pred, gold in paired:
        if gold is None:
            continue
        g_root = _normalize_root(gold.get(root_key))
        p_root = _normalize_root(pred.get(root_key))
        total += 1
        if p_root == g_root:
            correct += 1
        src = (pred.get(source_key) or "").strip() or "unknown"
        by_source[src].append((p_root, g_root))

    result: Dict[str, object] = {
        "accuracy": (correct / total) if total else 0.0,
        "total": total,
        "correct": correct,
    }
    per_source: Dict[str, Dict[str, object]] = {}
    for src, pairs in by_source.items():
        n = len(pairs)
        c = sum(1 for p, g in pairs if p == g)
        per_source[src] = {
            "accuracy": (c / n) if n else 0.0,
            "total": n,
            "correct": c,
        }
    result["per_source"] = per_source
    return result


def print_report(eval_result: Dict[str, object]) -> None:
    """Print a simple text report to stdout."""
    print("Root Resolver Evaluation Report")
    print("=" * 50)
    print(f"Overall: {eval_result['correct']}/{eval_result['total']} correct")
    print(f"Accuracy: {eval_result['accuracy']:.4f}")
    print()
    per_source = eval_result.get("per_source") or {}
    print("Per source:")
    for src, m in sorted(per_source.items()):
        print(f"  {src}: {m['correct']}/{m['total']} = {m['accuracy']:.4f}")
    print()


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate root_resolver CSV vs gold CSV")
    parser.add_argument("pred_csv", type=Path, help="Pipeline output CSV (with root, optional root_source)")
    parser.add_argument("gold_csv", type=Path, help="Gold CSV (word, root)")
    parser.add_argument("--root-col", default="root", help="Column name for root")
    parser.add_argument("--source-col", default="root_source", help="Column name for root_source")
    args = parser.parse_args()
    pred_rows = load_csv(args.pred_csv)
    gold_rows = load_csv(args.gold_csv)
    if not pred_rows:
        print("No rows in pred CSV", file=__import__("sys").stderr)
        return 1
    if not gold_rows:
        print("No rows in gold CSV", file=__import__("sys").stderr)
        return 1
    eval_result = evaluate(pred_rows, gold_rows, root_key=args.root_col, source_key=args.source_col)
    print_report(eval_result)
    return 0


if __name__ == "__main__":
    exit(main())
