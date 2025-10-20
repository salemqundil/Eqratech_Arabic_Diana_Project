from __future__ import annotations

from collections import Counter
from typing import List

import matplotlib.pyplot as plt


def plot_diacritics(diac_sequences: List[List[str]], out_path: str | None = None) -> None:
    flat = [d for seq in diac_sequences for d in seq]
    c = Counter(flat)
    labels = ["F", "D", "K", "S"]
    values = [c.get(k, 0) for k in labels]
    plt.figure(figsize=(5, 3))
    plt.bar(labels, values)
    plt.title("Diacritics distribution")
    if out_path:
        plt.savefig(out_path, bbox_inches="tight")
    else:
        plt.show()


def plot_syllables(syllables: List[List[str]], out_path: str | None = None) -> None:
    flat = [s for seq in syllables for s in seq]
    allowed = ["CV", "CVC", "CVV", "CVVC", "CVCC", "VC"]
    c = Counter(flat)
    labels = allowed
    values = [c.get(k, 0) for k in labels]
    plt.figure(figsize=(6, 3))
    plt.bar(labels, values)
    plt.title("Syllable gates distribution")
    if out_path:
        plt.savefig(out_path, bbox_inches="tight")
    else:
        plt.show()
