# === BERT & CANINE Synergy Expansion ===
import os
from typing import List


def train_model_synergy(config_path: str):
    """Train a model (BERT or CANINE) using the given config."""
    # Placeholder: integrate with your actual training logic
    print(f"[SYNERGY] Training model with config: {config_path}")
    # ...call main() or training logic with config_path...


def evaluate_model_synergy(config_path: str):
    """Evaluate a model and save predictions."""
    print(f"[SYNERGY] Evaluating model with config: {config_path}")
    # ...call evaluation logic with config_path...


def load_predictions(pred_path: str) -> List[str]:
    """Load predictions from a file."""
    with open(pred_path, encoding="utf-8") as f:
        return [line.strip() for line in f]


def save_predictions(preds: List[str], out_path: str):
    """Save predictions to a file."""
    with open(out_path, "w", encoding="utf-8") as f:
        for p in preds:
            f.write(p + "\n")


def ensemble_predictions(bert_preds: List[str], canine_preds: List[str]) -> List[str]:
    """Simple ensemble: majority vote or fallback to CANINE if disagree."""
    final = []
    for b, c in zip(bert_preds, canine_preds):
        final.append(b if b == c else c)
    return final


def run_synergy_workflow():
    """Run BERT+CANINE training, evaluation, and ensemble."""
    bert_config = "config/training_config_bert.json"
    canine_config = "config/training_config_canine.json"
    train_model_synergy(bert_config)
    train_model_synergy(canine_config)
    evaluate_model_synergy(bert_config)
    evaluate_model_synergy(canine_config)
    bert_preds = load_predictions("output/bert/preds.txt")
    canine_preds = load_predictions("output/canine/preds.txt")
    final_preds = ensemble_predictions(bert_preds, canine_preds)
    save_predictions(final_preds, "output/ensemble/preds.txt")
    print("[SYNERGY] Ensemble predictions saved to output/ensemble/preds.txt")


# === End Synergy Expansion ===
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
    from canine_bert_synergy import CanineBertSynergyHelper

    # Import CANINE model (assume available as CanineForMaskedLM)
    try:
        from transformers import CanineConfig, CanineForMaskedLM
    except ImportError:
        print("ERROR: CANINE model not available in transformers. Please install a compatible version.")
        sys.exit(1)

    print("\n[MODEL] Creating BERT and CANINE models…")

    bert_config = BertConfig(
        vocab_size=len(tokenizer.vocab),
        hidden_size=768,
        num_hidden_layers=12,
        num_attention_heads=12,
        intermediate_size=3072,
        max_position_embeddings=config["training"]["max_seq_length"],
        pad_token_id=tokenizer.vocab.get(tokenizer.pad_token, 0),
    )
    bert_model = BertForMaskedLM(config=bert_config)
    print(f"[MODEL] BERT params: {sum(p.numel() for p in bert_model.parameters()):,}")

    canine_config = CanineConfig(
        vocab_size=len(tokenizer.vocab),
        hidden_size=768,
        num_hidden_layers=12,
        num_attention_heads=12,
        intermediate_size=3072,
        max_position_embeddings=config["training"]["max_seq_length"],
        pad_token_id=tokenizer.vocab.get(tokenizer.pad_token, 0),
    )
    canine_model = CanineForMaskedLM(config=canine_config)
    print(f"[MODEL] CANINE params: {sum(p.numel() for p in canine_model.parameters()):,}")

    synergy_helper = CanineBertSynergyHelper(canine_model, bert_model, fusion_mode="concat")
    return synergy_helper, canine_model, bert_model


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
    import torch

    print("\n[TRAINING] Coordinated CANINE-BERT training (separate optimizers/losses)…")

    synergy_helper, canine_model, bert_model = model
    max_len = config["training"]["max_seq_length"]
    train_ds = TinyTextDataset(train_texts, tokenizer, max_len)
    eval_ds = TinyTextDataset(eval_texts, tokenizer, max_len)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    synergy_helper.to(device)
    canine_model.to(device)
    bert_model.to(device)

    optimizer_canine = torch.optim.AdamW(canine_model.parameters(), lr=config["training"]["learning_rate"])
    optimizer_bert = torch.optim.AdamW(bert_model.parameters(), lr=config["training"]["learning_rate"])

    num_epochs = config["training"]["num_train_epochs"]
    batch_size = config["training"]["per_device_train_batch_size"]
    print(f"[TRAINING] Device: {'GPU' if torch.cuda.is_available() else 'CPU'}")

    for epoch in range(num_epochs):
        print(f"[EPOCH] {epoch+1}/{num_epochs}")
        synergy_helper.train()
        for i in range(0, len(train_ds), batch_size):
            batch = [train_ds[j] for j in range(i, min(i + batch_size, len(train_ds)))]
            input_ids = torch.stack([b["input_ids"] for b in batch]).to(device)
            attention_mask = torch.stack([b["attention_mask"] for b in batch]).to(device)
            labels = input_ids.clone()

            # Forward pass
            out = synergy_helper(input_ids, attention_mask=attention_mask, labels=labels)
            canine_loss = out["canine_out"].loss if hasattr(out["canine_out"], "loss") else None
            bert_loss = out["bert_out"].loss if hasattr(out["bert_out"], "loss") else None

            optimizer_canine.zero_grad()
            optimizer_bert.zero_grad()
            if canine_loss is not None:
                canine_loss.backward(retain_graph=True)
                optimizer_canine.step()
            if bert_loss is not None:
                bert_loss.backward()
                optimizer_bert.step()

        print(f"[TRAINING] Finished epoch {epoch+1}")

    # Save final models
    final_dir = os.path.join(config["output_dir"], "final_model")
    os.makedirs(final_dir, exist_ok=True)
    torch.save(canine_model.state_dict(), os.path.join(final_dir, "canine_model.pt"))
    torch.save(bert_model.state_dict(), os.path.join(final_dir, "bert_model.pt"))
    tokenizer.save_pretrained(final_dir)
    print(f"[TRAINING] Saved final CANINE and BERT models to {final_dir}")
    return None


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

    # Coordinated training disables curriculum for simplicity
    train_model(cfg, model, tokenizer, train_texts, eval_texts)
    # For future synergy expansion, call run_synergy_workflow() here if needed

    print("\n" + "=" * 70)
    print("Training Pipeline Completed Successfully!")
    print("=" * 70)
    print(f"\nModel saved to: {cfg['output_dir']}")
    print(f"Logs saved to : {cfg.get('logging',{}).get('log_dir','./logs')}")
    print("\nReuse:")
    print(
        f"  from transformers import BertForMaskedLM; m=BertForMaskedLM.from_pretrained('{cfg['output_dir']}/final_model')"
    )
    print(
        "  from utf8_tokenizer import UTF8CharTokenizer; tok=UTF8CharTokenizer.from_pretrained('{cfg['output_dir']}/final_model')"
    )
    print()


if __name__ == "__main__":
    main()
    # To run BERT+CANINE synergy workflow in future:
    # run_synergy_workflow()
