"""
Minimal training smoke test.

Purpose: Verify that transformers+torch work with the custom UTF-8 tokenizer and a tiny in-memory dataset
without requiring HuggingFace datasets (and thus avoiding pyarrow on Windows).
"""
from __future__ import annotations

import os
from typing import List, Dict

os.environ.setdefault("PYTHONIOENCODING", "utf-8")


def main():
    from transformers import BertConfig, BertForMaskedLM
    import torch
    from utf8_tokenizer import create_tokenizer

    # Tiny config
    max_len = 32
    texts = [
        "ا ل ح م د ل ل ه",
        "م ر ح ب ا",
        "ك ي ف ح ا ل ك",
        "ش ك ر ا",
        "أ ه ل ا و س ه ل ا",
    ]

    # Tokenizer (use default config loading path)
    tokenizer = create_tokenizer({
        "tokenizer_dir": "./tokenizers",
        "training": {"max_seq_length": max_len}
    })

    # Minimal BERT config
    cfg = BertConfig(
        vocab_size=tokenizer.vocab_size,
        hidden_size=128,
        num_hidden_layers=2,
        num_attention_heads=2,
        intermediate_size=256,
        max_position_embeddings=max_len,
        pad_token_id=tokenizer.vocab.get(tokenizer.pad_token, 0),
    )
    model = BertForMaskedLM(cfg)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Encode data
    def encode_batch(batch_texts: List[str]) -> Dict[str, torch.Tensor]:
        input_ids, attention_mask = [], []
        for t in batch_texts:
            # Our UTF8PhonemeTokenizer supports these kwargs (HuggingFace-like)
            enc = tokenizer.encode(t, padding=True, truncation=True, max_length=max_len)
            input_ids.append(enc["input_ids"])
            attention_mask.append(enc["attention_mask"])
        return {
            "input_ids": torch.tensor(input_ids, dtype=torch.long, device=device),
            "attention_mask": torch.tensor(attention_mask, dtype=torch.long, device=device),
        }

    batch = encode_batch(texts)
    labels = batch["input_ids"].clone()

    # Create a simple random masking
    mlm_probability = 0.15
    mask_token_id = tokenizer.vocab[tokenizer.mask_token]
    special_ids = {
        tokenizer.vocab.get(tokenizer.pad_token, -1),
        tokenizer.vocab.get(tokenizer.cls_token, -1),
        tokenizer.vocab.get(tokenizer.sep_token, -1),
    }

    probability_matrix = torch.full(labels.shape, mlm_probability, device=device)
    special_mask = torch.zeros_like(labels, dtype=torch.bool)
    for sid in special_ids:
        if sid >= 0:
            special_mask |= (labels == sid)
    probability_matrix.masked_fill_(special_mask, 0.0)

    masked_indices = torch.bernoulli(probability_matrix).bool()
    labels[~masked_indices] = -100
    indices_replaced = torch.bernoulli(torch.full(labels.shape, 0.8, device=device)).bool() & masked_indices
    batch["input_ids"][indices_replaced] = mask_token_id

    # Optimizer
    optim = torch.optim.AdamW(model.parameters(), lr=5e-4)

    model.train()
    out = model(**batch, labels=labels)
    loss = out.loss
    loss.backward()
    optim.step()

    print("SMOKE OK | device:", device, "loss:", float(loss.detach().cpu()))


if __name__ == "__main__":
    main()
