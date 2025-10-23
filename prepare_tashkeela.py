"""
prepare_tashkeela.py
Downloads Tashkeela dataset from HuggingFace, strips diacritics, splits, and exports to CSV/Parquet.
Best practices: robust column detection, error handling, manual split fallback, progress logging.
"""

import os
from datasets import load_dataset
import regex as re
import random

# Configurable parameters
DS_ID = "community-datasets/tashkeela"  # Or "EmanKhater/Tashkeela"
CSV_DIR = "data/tashkeela_csv"
PARQUET_DIR = "data/tashkeela_parquet"
SPLIT_RATIOS = {"train": 0.9, "validation": 0.05, "test": 0.05}
SHARDS = 10
SEED = 1337


def strip_diac(s):
    return AR_DIAC.sub("", s)


def detect_column(ds):
    # Handles Dataset, DatasetDict, IterableDataset
    if hasattr(ds, "column_names") and ds.column_names:
        if isinstance(ds.column_names, dict):
            colnames = list(ds.column_names.values())[0]
        else:
            colnames = ds.column_names
    else:
        colnames = ["text"]
    return "text" if "text" in colnames else colnames[0]


def manual_split(ds, ratios, seed=SEED):
    # Shuffle and split indices manually
    n = len(ds)
    idxs = list(range(n))
    random.seed(seed)
    random.shuffle(idxs)
    train_end = int(ratios["train"] * n)
    val_end = train_end + int(ratios["validation"] * n)
    train_idxs = idxs[:train_end]
    val_idxs = idxs[train_end:val_end]
    test_idxs = idxs[val_end:]
    return {"train": ds.select(train_idxs), "validation": ds.select(val_idxs), "test": ds.select(test_idxs)}


def export_splits(splits, csv_dir, parquet_dir, shards):
    os.makedirs(csv_dir, exist_ok=True)
    os.makedirs(parquet_dir, exist_ok=True)
    for name, d in splits.items():
        print(f"Exporting {name} split...")
        n = len(d)
        for i in range(shards):
            shard = d.shard(num_shards=shards, index=i)
            out_csv = f"{csv_dir}/{name}_{i:02}.csv"
            print(f"  Writing {out_csv} ({len(shard)} rows)...")
            shard.to_csv(out_csv)
        out_parquet = f"{parquet_dir}/{name}.parquet"
        print(f"  Writing {out_parquet} ({n} rows)...")
        d.to_parquet(out_parquet)


def main():
    print(f"Loading dataset: {DS_ID}")
    try:
        ds = load_dataset(DS_ID, split="train")
    except Exception as e:
        print(f"ERROR: Could not load dataset: {e}")
        return
    col = detect_column(ds)
    print(f"Detected column: {col}")
    try:
        ds = ds.rename_column(col, "text_diac")
    except Exception as e:
        print(f"ERROR: Could not rename column: {e}")
        return
    print("Stripping diacritics...")
    try:
        ds = ds.map(lambda ex: {"text_raw": strip_diac(ex["text_diac"])})
    except Exception as e:
        print(f"ERROR: Could not strip diacritics: {e}")
        return

    print("Splitting dataset into train/validation/test...")
    try:
        if hasattr(ds, "train_test_split"):
            tmp = ds.train_test_split(test_size=SPLIT_RATIOS["validation"] + SPLIT_RATIOS["test"], seed=SEED)
            val_test = tmp["test"].train_test_split(
                test_size=SPLIT_RATIOS["test"] / (SPLIT_RATIOS["validation"] + SPLIT_RATIOS["test"]), seed=SEED
            )
            splits = {"train": tmp["train"], "validation": val_test["train"], "test": val_test["test"]}
        else:
            splits = manual_split(ds, SPLIT_RATIOS, seed=SEED)
    except Exception as e:
        print(f"ERROR: Could not split dataset: {e}")
        return

    export_splits(splits, CSV_DIR, PARQUET_DIR, SHARDS)
    print("Done! Files saved in data/tashkeela_csv and data/tashkeela_parquet.")


if __name__ == "__main__":
    # Regex for Arabic diacritics
    AR_DIAC = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")
    main()
