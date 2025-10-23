"""
Utility to split the CANINE/transformer corpus into train/validation/test partitions.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


DEFAULT_INPUT = Path("data/canine_training/canine_corpus.tsv")


@dataclass
class Record:
    rtype: str
    category: str
    subtype: str
    form: str


def read_corpus(path: Path, dedupe: bool) -> List[Record]:
    """
    Read TSV corpus and optionally deduplicate on the textual form.
    """
    seen = set()
    records: List[Record] = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            form = row["form"].strip()
            if not form:
                continue
            if dedupe:
                key = (row["type"], row["category"], row["subtype"], form)
                if key in seen:
                    continue
                seen.add(key)
            records.append(
                Record(
                    rtype=row["type"],
                    category=row["category"],
                    subtype=row["subtype"],
                    form=form,
                )
            )
    return records


def split_indices(n: int, ratios: Tuple[float, float, float]) -> Tuple[List[int], List[int], List[int]]:
    """
    Split indices into train/val/test according to ratios.
    """
    if n == 0:
        return [], [], []
    train_ratio, val_ratio, test_ratio = ratios
    total = train_ratio + val_ratio + test_ratio
    if total <= 0:
        raise ValueError("Sum of ratios must be positive.")
    train_n = int(round(n * train_ratio / total))
    val_n = int(round(n * val_ratio / total))
    train_n = min(train_n, n)
    val_n = min(val_n, n - train_n)
    test_n = n - train_n - val_n

    all_indices = list(range(n))
    train_idx = all_indices[:train_n]
    val_idx = all_indices[train_n : train_n + val_n]
    test_idx = all_indices[train_n + val_n :]
    return train_idx, val_idx, test_idx


def partition_records(
    records: List[Record],
    seed: int,
    ratios: Tuple[float, float, float],
    stratify_type: bool,
) -> Dict[str, List[Record]]:
    """
    Shuffle and split records, optionally stratified by record type.
    """
    rng = random.Random(seed)
    partitions = {"train": [], "val": [], "test": []}

    if stratify_type:
        buckets: Dict[str, List[Record]] = {}
        for rec in records:
            buckets.setdefault(rec.rtype, []).append(rec)
        for bucket_records in buckets.values():
            rng.shuffle(bucket_records)
            train_idx, val_idx, test_idx = split_indices(len(bucket_records), ratios)
            for idx in train_idx:
                partitions["train"].append(bucket_records[idx])
            for idx in val_idx:
                partitions["val"].append(bucket_records[idx])
            for idx in test_idx:
                partitions["test"].append(bucket_records[idx])
    else:
        shuffled = records[:]
        rng.shuffle(shuffled)
        train_idx, val_idx, test_idx = split_indices(len(shuffled), ratios)
        for idx in train_idx:
            partitions["train"].append(shuffled[idx])
        for idx in val_idx:
            partitions["val"].append(shuffled[idx])
        for idx in test_idx:
            partitions["test"].append(shuffled[idx])
    return partitions


def write_transformer_txt(partitions: Dict[str, List[Record]], out_dir: Path) -> None:
    """
    Write text-only files for transformer training (one form per line).
    """
    base = out_dir / "transformer"
    base.mkdir(parents=True, exist_ok=True)
    for split_name, records in partitions.items():
        path = base / f"{split_name}.txt"
        with path.open("w", encoding="utf-8") as f:
            for rec in records:
                f.write(rec.form + "\n")


def write_canine_tsv(partitions: Dict[str, List[Record]], out_dir: Path) -> None:
    """
    Write TSV files retaining categorical metadata for CANINE runs.
    """
    base = out_dir / "canine"
    base.mkdir(parents=True, exist_ok=True)
    header = ["type", "category", "subtype", "form"]
    for split_name, records in partitions.items():
        path = base / f"{split_name}.tsv"
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow(header)
            for rec in records:
                writer.writerow([rec.rtype, rec.category, rec.subtype, rec.form])


def write_summary(partitions: Dict[str, List[Record]], out_dir: Path, ratios: Tuple[float, float, float]) -> None:
    """
    Dump summary JSON with counts per split and per type.
    """
    summary = {
        "ratios": {
            "train": ratios[0],
            "val": ratios[1],
            "test": ratios[2],
        },
        "splits": {},
    }
    for split_name, records in partitions.items():
        type_counts: Dict[str, int] = {}
        for rec in records:
            type_counts[rec.rtype] = type_counts.get(rec.rtype, 0) + 1
        summary["splits"][split_name] = {
            "count": len(records),
            "type_breakdown": type_counts,
        }

    path = out_dir / "split_summary.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Split CANINE corpus into train/val/test.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Source TSV file.")
    parser.add_argument("--output-dir", type=Path, default=Path("data/canine_training/splits"), help="Output directory.")
    parser.add_argument("--train-ratio", type=float, default=0.8, help="Ratio for training set.")
    parser.add_argument("--val-ratio", type=float, default=0.1, help="Ratio for validation set.")
    parser.add_argument("--test-ratio", type=float, default=0.1, help="Ratio for test set.")
    parser.add_argument("--seed", type=int, default=1234, help="Random seed for shuffling.")
    parser.add_argument(
        "--stratify-type",
        action="store_true",
        help="Maintain the same proportion of record types (syllable/morph/augmented) across splits.",
    )
    parser.add_argument(
        "--dedupe",
        action="store_true",
        help="Remove duplicate records that share the same type/category/subtype/form tuple.",
    )
    args = parser.parse_args()

    records = read_corpus(args.input, dedupe=args.dedupe)
    if not records:
        raise SystemExit(f"No records found in {args.input}")

    partitions = partition_records(
        records,
        seed=args.seed,
        ratios=(args.train_ratio, args.val_ratio, args.test_ratio),
        stratify_type=args.stratify_type,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_transformer_txt(partitions, args.output_dir)
    write_canine_tsv(partitions, args.output_dir)
    write_summary(partitions, args.output_dir, (args.train_ratio, args.val_ratio, args.test_ratio))

    total = sum(len(v) for v in partitions.values())
    print("✅ Splits ready")
    print(f"  • Total records: {total}")
    for split_name in ("train", "val", "test"):
        cnt = len(partitions[split_name])
        print(f"  • {split_name}: {cnt}")
    print(f"  • Output: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
