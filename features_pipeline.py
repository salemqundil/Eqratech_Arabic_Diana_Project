"""
Arabic diacritics-based feature extraction and simple analytics.

Outputs:
- <prefix>_features.csv: per-token features (length, diacritics counts, syllable histogram, tri-vowel code/name)
- <prefix>_mi_fisher.csv: feature MI/Fisher scores vs. a chosen label (default: tri_name)
- <prefix>_summary.json: aggregate stats (novelty, DFA alpha proxy, word count)

Ontology: tries to use project loader (phoneme_ontology.get_ontology). If unavailable,
falls back to reading a provided YAML path, otherwise uses safe defaults for a smoke run.
"""
from __future__ import annotations

import re
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Mapping

import numpy as np
import pandas as pd


# ---------- basic normalizers ----------
RE_DIAC = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")
RE_TATW = re.compile(r"\u0640")
RE_NON_AR = re.compile(r"[^\u0621-\u064A\s]")


def unify_letters(s: str) -> str:
    return (
        s.replace("أ", "ا")
        .replace("إ", "ا")
        .replace("آ", "ا")
        .replace("ٱ", "ا")
        .replace("ى", "ي")
        .replace("ؤ", "و")
        .replace("ئ", "ي")
        .replace("ة", "ه")
    )


def normalize_ar(s: str, keep_diac: bool) -> str:
    s = RE_TATW.sub("", s)
    if not keep_diac:
        s = RE_DIAC.sub("", s)
    s = unify_letters(s)
    s = RE_NON_AR.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# ---------- ontology loader (robust) ----------
def load_ontology(path: Optional[str] = None) -> Dict[str, Any]:
    """Load ontology.

    Prefers project loader (phoneme_ontology.get_ontology). If that fails,
    tries YAML at provided path. Otherwise returns a minimal default.
    """
    # Try project ontology loader first
    try:
        from phoneme_ontology import get_ontology  # type: ignore

        ont = get_ontology(path)
        return ont.raw if hasattr(ont, "raw") else {}
    except Exception:
        pass

    # Fallback: read YAML directly if a path is provided
    if path and Path(path).exists():
        try:
            import yaml  # type: ignore

            return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        except Exception:
            pass

    # Minimal default for smoke tests
    return {
        "diacritics": {
            "tri_past_patterns": [
                {"code": "FFF", "name": "fa3ala"},
                {"code": "FKF", "name": "fa3ila"},
                {"code": "FDF", "name": "fa3ula"},
            ]
        },
        "syllables": {"allowed_gates": ["CV", "CVC", "CVV", "CVVC", "CVCC", "VC"]},
        "labels": {
            "pos_subgroup": ["none", "verb", "particle"],
            "pattern_classes": ["fa3ala", "fa3ila", "fa3ula", "NA"],
        },
        "operators": {"i3rab": {"types": ["مبني", "معرب"]}},
    }


# ---------- labeling (rule-based) ----------
HMAP = {"َ": "F", "ِ": "K", "ُ": "D", "ْ": "S"}


def diacritics_seq(s_with: str) -> List[str]:
    return [HMAP[ch] if ch in HMAP else "-" for ch in s_with]


def _is_ar_letter(ch: str) -> bool:
    return bool(re.match(r"[\u0621-\u064A]", ch))


def syllables_greedy(word_with: str, gates: List[str]) -> List[str]:
    types: List[str] = []
    for ch in word_with:
        if ch in HMAP:
            types.append("V")
        elif _is_ar_letter(ch):
            types.append("C")
    i = 0
    out: List[str] = []
    while i < len(types):
        if types[i] == "C" and i + 1 < len(types) and types[i + 1] == "V":
            if i + 2 < len(types) and types[i + 2] == "C":
                out.append("CVC")
                i += 3
            elif i + 2 < len(types) and types[i + 2] == "V":
                out.append("CVV")
                i += 3
            else:
                out.append("CV")
                i += 2
        elif types[i] == "V" and i + 1 < len(types) and types[i + 1] == "C":
            out.append("VC")
            i += 2
        else:
            i += 1
    return [p for p in out if p in gates]


def tri_vowel_pattern(word_with: str) -> str:
    seq = [HMAP[ch] for ch in word_with if ch in HMAP][:3]
    return "".join(seq) if len(seq) == 3 else ""


def tri_name_from_code(code: str, tri_list: List[Mapping[str, Any]]) -> str:
    for item in tri_list:
        if isinstance(item, Mapping) and item.get("code") == code:
            name = item.get("name", "NA")
            return str(name) if name is not None else "NA"
    return "NA"


# ---------- feature builder ----------
def build_features(text_with: str, onto: Dict[str, Any]) -> pd.DataFrame:
    tokens = [w for w in text_with.split() if w.strip()]
    gates = onto.get("syllables", {}).get("allowed_gates", [])
    tri_list = onto.get("diacritics", {}).get("tri_past_patterns", [])
    pos_space = onto.get("labels", {}).get("pos_subgroup", ["none"])  # noqa: F841
    i3_types = (
        onto.get("operators", {}).get("i3rab", {}).get("types", ["معرب"]) or ["معرب"]
    )

    rows: List[Dict[str, Any]] = []
    for w in tokens:
        dseq = diacritics_seq(w)
        tri_code = tri_vowel_pattern(w)
        tri_name = tri_name_from_code(tri_code, tri_list)
        sylls = syllables_greedy(w, gates)

        # histogram over configured gates
        key_index = {k: i for i, k in enumerate(gates)}
        hist = np.zeros(len(gates), dtype=np.float32)
        for s in sylls:
            if s in key_index:
                hist[key_index[s]] += 1
        hs = float(hist.sum()) or 1.0
        hist = hist / hs

        # placeholder POS/I'rab (to be replaced by your precise rules)
        pos = "none"
        i3 = i3_types[0]

        rows.append(
            {
                "word": w,
                "len": len(w),
                "d_F": dseq.count("F"),
                "d_K": dseq.count("K"),
                "d_D": dseq.count("D"),
                "d_S": dseq.count("S"),
                "syl_hist": hist.tolist(),
                "tri_code": tri_code,
                "tri_name": tri_name,
                "pos": pos,
                "i3rab": i3,
            }
        )
    return pd.DataFrame(rows)


# ---------- MI / Fisher against labels ----------
def compute_mi_fisher(df: pd.DataFrame, gates: List[str], label_col: str = "tri_name") -> pd.DataFrame:
    # expand syllable histogram columns
    syl_cols = [f"syl_{g}" for g in gates]
    syl_mat = np.vstack(df["syl_hist"].to_numpy()) if len(df) else np.zeros((0, len(gates)))
    syl_df = pd.DataFrame(syl_mat, columns=syl_cols)
    X = pd.concat([df[["d_F", "d_K", "d_D", "d_S", "len"]].reset_index(drop=True), syl_df], axis=1)
    y = df[label_col].astype("category").cat.codes.values if label_col in df.columns else np.zeros(len(df))

    try:
        from sklearn.feature_selection import mutual_info_classif, f_classif  # type: ignore

        mi = mutual_info_classif(X.values, y, discrete_features=False, random_state=42)
        f_vals, f_p = f_classif(X.values, y)
        result = pd.DataFrame({"feature": X.columns, "MI": mi, "Fisher": f_vals, "p": f_p})
        return result.sort_values("MI", ascending=False)
    except Exception as e:
        # Graceful fallback if sklearn is unavailable
        return pd.DataFrame({
            "feature": list(X.columns),
            "MI": [np.nan] * X.shape[1],
            "Fisher": [np.nan] * X.shape[1],
            "p": [np.nan] * X.shape[1],
            "note": [f"sklearn unavailable: {type(e).__name__}"] * X.shape[1],
        })


# ---------- SSM / Novelty / DFA (on F/K/D/S) ----------
def diac_time_series(text_with: str) -> np.ndarray:
    seq = [HMAP[ch] for ch in text_with if ch in HMAP]
    mapper = {"F": 0, "K": 1, "D": 2, "S": 3}
    return np.array([mapper[x] for x in seq], dtype=int)


def ssm(seq: np.ndarray, win: int = 32) -> np.ndarray:
    # simple self-similarity using sliding cosine on rolling windows
    if len(seq) < win:
        return np.eye(len(seq), dtype=float)
    from numpy.lib.stride_tricks import sliding_window_view as swv

    X = swv(seq, win)  # (T, win)
    Xn = X - X.mean(axis=1, keepdims=True)
    Xn /= (Xn.std(axis=1, keepdims=True) + 1e-9)
    return (Xn @ Xn.T) / float(win)


def novelty_from_ssm(M: np.ndarray, k: int = 8) -> np.ndarray:
    T = M.shape[0]
    nov = np.zeros(T, dtype=float)
    for t in range(k, max(k, T - k)):
        A = M[t - k : t, t - k : t]
        B = M[t + 1 : t + k + 1, t + 1 : t + k + 1]
        nov[t] = A.sum() + B.sum() - M[t - k : t, t + 1 : t + k + 1].sum() - M[t + 1 : t + k + 1, t - k : t].sum()
    if nov.size:
        nov -= nov.min()
        mx = nov.max() or 1.0
        nov /= mx
    return nov


def dfa_alpha(seq: np.ndarray, min_win: int = 8, max_win: int = 128) -> float:
    # very small DFA proxy
    x = seq.astype(float)
    if x.size == 0:
        return float("nan")
    x -= x.mean()
    y = np.cumsum(x)
    scales = np.unique(np.logspace(np.log10(min_win), np.log10(max_win), num=8, dtype=int))
    F: List[tuple[int, float]] = []
    for s in scales:
        k = len(y) // s
        if k < 2:
            continue
        RMS: List[float] = []
        for i in range(k):
            seg = y[i * s : (i + 1) * s]
            t = np.arange(s)
            p = np.polyfit(t, seg, 1)
            fit = np.polyval(p, t)
            RMS.append(float(np.sqrt(((seg - fit) ** 2).mean())))
        if RMS:
            F.append((s, float(np.mean(RMS))))
    if len(F) < 2:
        return float("nan")
    s, a = zip(*F)
    return float(np.polyfit(np.log(s), np.log(a), 1)[0])


# ---------- main pipeline ----------
def run_pipeline(
    text_path: str = "text.txt",
    onto_path: Optional[str] = None,
    out_prefix: str = "report",
    onto: Optional[Dict[str, Any]] = None,
):
    onto_dict = onto if onto is not None else load_ontology(onto_path)

    text_raw = Path(text_path).read_text(encoding="utf-8")
    text_with = normalize_ar(text_raw, keep_diac=True)

    df = build_features(text_with, onto_dict)
    gates = onto_dict.get("syllables", {}).get("allowed_gates", [])
    mi_tbl = compute_mi_fisher(df, gates, label_col="tri_name")

    # rhythm/fractal features over the whole diacritics stream
    series = diac_time_series(text_with)
    M = ssm(series, win=32)
    novelty = novelty_from_ssm(M, k=8)
    alpha = dfa_alpha(series, 8, 128)

    # save artifacts
    Path(f"{out_prefix}_features.csv").write_text(df.to_csv(index=False), encoding="utf-8")
    Path(f"{out_prefix}_mi_fisher.csv").write_text(mi_tbl.to_csv(index=False), encoding="utf-8")
    with open(f"{out_prefix}_summary.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "dfa_alpha": float(alpha) if alpha == alpha else None,  # NaN check
                "novelty_mean": float(novelty.mean()) if novelty.size else None,
                "n_words": int(df.shape[0]),
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    return df, mi_tbl, alpha


if __name__ == "__main__":
    # مثال سريع:
    # 1) ضع نصك في text.txt
    # 2) استعمل الأنطولوجيا المدمجة (config/phoneme_ontology.yaml) أو مرّر واحدة مخصصة
    # 3) شغّل:
    #    python features_pipeline.py
    sample_text = "مُحَمَّدٌ رَسُولُ اللَّهِ"
    Path("text.txt").write_text(sample_text, encoding="utf-8")

    # استخدم الأنطولوجيا الافتراضية إن تعذر التحميل
    df, mi, a = run_pipeline("text.txt", onto_path=None, out_prefix="out")
    print("rows:", len(df), "features cols:", list(df.columns))
