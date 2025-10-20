"""BERT Training Script for Arabic Phoneme Processing (No pyarrow/no datasets)
- Pure PyTorch Dataset
- UTF-8 tokenizer via utf8_tokenizer.create_tokenizer
"""

import json
import os
import sys
from typing import Dict, List, Optional
import argparse

# Ensure proper UTF-8 encoding on Windows
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"


def check_dependencies() -> bool:
    """Check if essential packages are installed (no pyarrow/datasets)."""
    required = ["transformers", "torch", "pandas", "numpy", "tqdm"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print("ERROR: Missing required packages:", ", ".join(missing))
        print("\nPlease run:")
        print("  pip install -r requirements.txt")
        return False
    return True


def load_config(config_path: str) -> Dict:
    if not os.path.exists(config_path):
        print(f"ERROR: Configuration file not found: {config_path}")
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    print(f"[CONFIG] Loaded configuration from {config_path}")
    return cfg


class TinyTextDataset:
    """
    A simple PyTorch-style dataset:
      - holds a list of {"text": "..."} samples
      - returns dict with 'input_ids'/'attention_mask' prepared by tokenizer
    """

    def __init__(self, texts: List[str], tokenizer, max_length: int):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx: int):
        text = self.texts[idx]
        enc = self.tokenizer.encode(
            text,
            padding="max_length",
            truncation=True,
            max_length=self.max_length,
        )
        return {"input_ids": enc["input_ids"], "attention_mask": enc["attention_mask"]}


def prepare_dataset(config: Dict, text_path: Optional[str] = None):
    """
    Prepare a pair (train_texts, eval_texts) without 'datasets'.
    Priority:
      1) lines from a UTF-8 text file (cli --text or config['text_path']),
      2) optional CSV probes (fallback),
      3) tiny synthetic sample.
    """
    import pandas as pd

    print("\n[DATASET] Preparing training dataset...")
    data_dir = config.get("data_dir", "./data")
    os.makedirs(data_dir, exist_ok=True)

    if not text_path:
        text_path = config.get("text_path")

    texts: List[str] = []

    # (1) plain text file: one sample per line
    if text_path and os.path.exists(text_path):
        print(f"[DATASET] Loading UTF-8 text from {text_path}")
        try:
            with open(text_path, "r", encoding="utf-8") as f:
                for line in f:
                    t = line.strip()
                    if t:
                        texts.append(t)
        except Exception as e:
            print(f"[DATASET] Warning: Could not load {text_path}: {e}")

    # (2) CSV probes if still empty
    if not texts:
        for csv_file in [
            "الفونيمات.csv",
            "Phonemes.csv",
            "full_multilayer_grammar.csv",
            "full_multilayer_grammar1.csv",
        ]:
            if os.path.exists(csv_file):
                print(f"[DATASET] Loading CSV: {csv_file}")
                try:
                    df = pd.read_csv(csv_file, encoding="utf-8-sig")
                    candidates = ["الفونيمات", "phonemes", "الأداة", "text"]
                    col = next((c for c in candidates if c in df.columns), None)
                    if col:
                        vals = df[col].tolist()
                        for x in vals:
                            s = str(x).strip()
                            if s and s.lower() != "nan":
                                texts.append(s)
                        print(f"[DATASET] Loaded {len(texts)} samples from CSV")
                        break
                except Exception as e:
                    print(f"[DATASET] Warning: Could not load {csv_file}: {e}")

    # (3) synthetic fallback
    if not texts:
        print("[DATASET] No data found, creating a tiny synthetic set…")
        texts = [
            "ا ل ح م د ل ل ه",
            "م ر ح ب ا",
            "ك ي ف ح ا ل ك",
            "ش ك ر ا",
            "أ ه ل ا و س ه ل ا",
        ] * 20

    # split (80/20)
    from math import floor

    n = len(texts)
    n_tr = max(1, floor(0.8 * n))
    train_texts = texts[:n_tr]
    eval_texts = texts[n_tr:]
    return train_texts, eval_texts


def create_model(config: Dict, tokenizer):
    from transformers import BertConfig, BertForMaskedLM

    print("\n[MODEL] Creating BERT model…")

    model_config = BertConfig(
        vocab_size=len(tokenizer.vocab),
        hidden_size=768,
        num_hidden_layers=12,
        num_attention_heads=12,
        intermediate_size=3072,
        max_position_embeddings=config["training"]["max_seq_length"],
        pad_token_id=tokenizer.vocab.get(tokenizer.pad_token, 0),
    )
    model = BertForMaskedLM(config=model_config)
    print(f"[MODEL] BERT params: {sum(p.numel() for p in model.parameters()):,}")
    return model


def prepare_tokenizer(config: Dict):
    from utf8_tokenizer import create_tokenizer

    print("\n[TOKENIZER] Building UTF-8 tokenizer…")
    tokenizer = create_tokenizer(config)

    # Save tokenizer
    tok_dir = config.get("tokenizer_dir", "./tokenizers")
    os.makedirs(tok_dir, exist_ok=True)
    tokenizer.save_pretrained(tok_dir)
    print(f"[TOKENIZER] Vocab size: {len(tokenizer.vocab)} (saved in {tok_dir})")
    return tokenizer


def train_model(config: Dict, model, tokenizer, train_texts: List[str], eval_texts: List[str]):
    from transformers import Trainer, TrainingArguments
    import torch

    print("\n[TRAINING] Starting…")

    # Dataset objects
    max_len = config["training"]["max_seq_length"]
    train_ds = TinyTextDataset(train_texts, tokenizer, max_len)
    eval_ds = TinyTextDataset(eval_texts, tokenizer, max_len)

    class CustomDataCollatorForMLM:
        def __init__(self, tokenizer, mlm_probability=0.15):
            self.tokenizer = tokenizer
            self.mlm_probability = mlm_probability
            self.pad_id = tokenizer.vocab[tokenizer.pad_token]
            self.cls_id = tokenizer.vocab[tokenizer.cls_token]
            self.sep_id = tokenizer.vocab[tokenizer.sep_token]
            self.mask_id = tokenizer.vocab[tokenizer.mask_token]

        def __call__(self, features):
            import torch

            input_ids = torch.tensor([f["input_ids"] for f in features], dtype=torch.long)
            attention_mask = torch.tensor([f["attention_mask"] for f in features], dtype=torch.long)
            labels = input_ids.clone()

            prob = torch.full(labels.shape, self.mlm_probability, dtype=torch.float32)
            special = (input_ids == self.pad_id) | (input_ids == self.cls_id) | (input_ids == self.sep_id)
            prob.masked_fill_(special, 0.0)

            masked = torch.bernoulli(prob).bool()
            labels[~masked] = -100

            # 80% [MASK]
            replace_mask = torch.bernoulli(torch.full(labels.shape, 0.8)).bool() & masked
            input_ids[replace_mask] = self.mask_id

            # 10% random token
            random_mask = torch.bernoulli(torch.full(labels.shape, 0.5)).bool() & masked & ~replace_mask
            rand_ids = torch.randint(len(self.tokenizer.vocab), labels.shape, dtype=torch.long)
            input_ids[random_mask] = rand_ids[random_mask]

            return {"input_ids": input_ids, "attention_mask": attention_mask, "labels": labels}

    # TrainingArguments (version-agnostic)
    log_dir = config.get("logging", {}).get("log_dir", "./logs")
    os.makedirs(log_dir, exist_ok=True)
    from inspect import signature

    ta_kwargs = dict(
        output_dir=config["output_dir"],
        num_train_epochs=config["training"]["num_train_epochs"],
        per_device_train_batch_size=config["training"]["per_device_train_batch_size"],
        per_device_eval_batch_size=config["training"]["per_device_eval_batch_size"],
        learning_rate=config["training"]["learning_rate"],
        warmup_steps=config["training"]["warmup_steps"],
        weight_decay=config["training"]["weight_decay"],
        logging_dir=log_dir,
        logging_steps=config["training"]["logging_steps"],
        save_steps=config["training"]["save_steps"],
        eval_steps=config["training"]["eval_steps"],
        save_total_limit=config["training"]["save_total_limit"],
        gradient_accumulation_steps=config["training"]["gradient_accumulation_steps"],
        load_best_model_at_end=True,
        report_to=[],
        fp16=torch.cuda.is_available(),
    )
    TA_params = signature(TrainingArguments.__init__).parameters
    if "evaluation_strategy" in TA_params:
        ta_kwargs["evaluation_strategy"] = "steps"
        ta_kwargs["save_strategy"] = "steps"

    args = TrainingArguments(**ta_kwargs)
    collator = CustomDataCollatorForMLM(tokenizer, mlm_probability=0.15)

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        data_collator=collator,
    )

    print(f"[TRAINING] Device: {'GPU' if torch.cuda.is_available() else 'CPU'}")
    trainer.train()

    # Save final
    final_dir = os.path.join(config["output_dir"], "final_model")
    os.makedirs(final_dir, exist_ok=True)
    trainer.save_model(final_dir)
    tokenizer.save_pretrained(final_dir)

    print(f"[TRAINING] Saved final model to {final_dir}")
    return trainer


def curriculum_training(config: Dict, model, tokenizer, train_texts, eval_texts):
    cur = config.get("curriculum_training", {})
    if not cur.get("enabled", False):
        print("[CURRICULUM] Disabled → standard training")
        return train_model(config, model, tokenizer, train_texts, eval_texts)

    print("\n[CURRICULUM] Starting curriculum…")
    stages = cur.get("stages", [])
    if not stages:
        print("[CURRICULUM] No stages → single run")
        return train_model(config, model, tokenizer, train_texts, eval_texts)

    trainer = None
    for i, st in enumerate(stages, 1):
        print(f"[CURRICULUM] Stage {i}/{len(stages)}: {st['name']}")
        scfg = json.loads(json.dumps(config))  # deep copy
        scfg["training"]["max_seq_length"] = st["max_length"]
        scfg["training"]["num_train_epochs"] = st["epochs"]
        scfg["output_dir"] = f"{config['output_dir']}/stage_{i}_{st['name']}"
        trainer = train_model(scfg, model, tokenizer, train_texts, eval_texts)
        model = trainer.model
    print("[CURRICULUM] Done.")
    return trainer


def main():
    parser = argparse.ArgumentParser(description="Train BERT for Arabic phoneme (no datasets/pyarrow)")
    parser.add_argument("--config", type=str, default="config/training_config.json")
    parser.add_argument("--skip-deps-check", action="store_true")
    parser.add_argument("--text", type=str, default=None)
    args = parser.parse_args()

    print("=" * 70)
    print("BERT Training for Arabic Phoneme Processing (No datasets)")
    print("=" * 70)

    if not args.skip_deps_check and not check_dependencies():
        print("\nInstall deps, then re-run.")
        return

    cfg = load_config(args.config)
    tokenizer = prepare_tokenizer(cfg)

    train_texts, eval_texts = prepare_dataset(cfg, text_path=args.text)
    model = create_model(cfg, tokenizer)

    if cfg.get("curriculum_training", {}).get("enabled", False):
        curriculum_training(cfg, model, tokenizer, train_texts, eval_texts)
    else:
        train_model(cfg, model, tokenizer, train_texts, eval_texts)

    print("\n" + "=" * 70)
    print("Training Pipeline Completed Successfully!")
    print("=" * 70)
    print(f"\nModel saved to: {cfg['output_dir']}")
    print(f"Logs saved to : {cfg.get('logging',{}).get('log_dir','./logs')}")
    print("\nReuse:")
    print(f"  from transformers import BertForMaskedLM; m=BertForMaskedLM.from_pretrained('{cfg['output_dir']}/final_model')")
    print("  from utf8_tokenizer import UTF8CharTokenizer; tok=UTF8CharTokenizer.from_pretrained('{cfg['output_dir']}/final_model')")
    print()


if __name__ == "__main__":
    main()
