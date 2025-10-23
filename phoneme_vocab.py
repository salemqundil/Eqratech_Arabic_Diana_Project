# Arabic Phoneme and Diacritic Vocabulary
# Generated for use in tokenizer/training pipelines

PHONEME_VOCAB = [
    "ء",
    "ا",
    "ب",
    "ت",
    "ث",
    "ج",
    "ح",
    "خ",
    "د",
    "ذ",
    "ر",
    "ز",
    "س",
    "ش",
    "ص",
    "ض",
    "ط",
    "ظ",
    "ع",
    "غ",
    "ف",
    "ق",
    "ك",
    "ل",
    "م",
    "ن",
    "ه",
    "و",
    "ي",
    "أ",
    "إ",
    "آ",
    "ى",
    "ة",
    "ؤ",
    "ئ",
    "ڤ",
    "پ",
    "چ",
]

DIACRITIC_VOCAB = ["َ", "ِ", "ُ", "ْ", "ّ", "ً", "ٌ", "ٍ"]

# Combined vocab for tokenizer
VOCAB = PHONEME_VOCAB + DIACRITIC_VOCAB

# For dictionary use
VOCAB_DICT = {ch: idx for idx, ch in enumerate(VOCAB)}

if __name__ == "__main__":
    print("Phoneme vocab:", PHONEME_VOCAB)
    print("Diacritic vocab:", DIACRITIC_VOCAB)
    print("Combined vocab:", VOCAB)
    print("Vocab dict:", VOCAB_DICT)
