"""
reverse_superseg_engine.py
Arabic phonological combinatorics engine with CSV corpus integration and CLI.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Iterable, Callable, Optional
import math
import random
import re
import argparse
import csv
import json
from collections import Counter, defaultdict
import sys

# =========================
# Inventories & config
# =========================
AR_CONS = list("ءبتثجحخدذرزسشصضطظعغفقكلمنهوي") + ["أ", "إ", "آ", "ى", "ة", "ؤ", "ئ", "ڤ", "پ", "چ"]
LONG = ["ا", "و", "ي", "آ", "ى"]
SHORT = ["َ", "ُ", "ِ"]
TANWIN = ["ً", "ٌ", "ٍ"]
SHADDA, SUKUN = "ّ", "ْ"

ALLOWED_GATES = ("CV", "VC", "CVC", "CVV", "CVVC", "CVCC", "CCV", "VCC", "CVVCC", "CCVC", "V", "CCVV")

ARTIC_CLASSES: Dict[str, str] = {}
for c in "ءه":
    ARTIC_CLASSES[c] = "laryngeal"
for c in "عح":
    ARTIC_CLASSES[c] = "pharyngeal"
for c in "غخ":
    ARTIC_CLASSES[c] = "uvular"
for c in "قك":
    ARTIC_CLASSES[c] = "velar"
for c in "جشي":
    ARTIC_CLASSES[c] = "palatal"
for c in "بمفو":
    ARTIC_CLASSES[c] = "labial"
for c in "تثدذرزسصضطظنلر":
    ARTIC_CLASSES[c] = "coronal"

OBS_SYLL = {
    "CV": ["بَ", "كَ", "لَ", "مَ", "نَ", "رَ", "تَ", "سَ", "عَ", "فَ"],
    "CVC": ["بَت", "كَت", "لَم", "نَص", "رَح", "عَل", "فَت", "سَب", "حَس", "خَي"],
    "CVV": ["با", "كو", "لي", "نا", "رو", "سي", "عا", "فو", "حي", "خو"],
    "CVVC": ["مال", "باب", "كيت", "سور", "عين", "فيض", "خير", "نور", "حيل", "طيب"],
    "CVCC": ["مَهر", "بَنت", "كَتب", "جمع", "حزم", "شرف", "عقد", "فهم", "نظر", "حقق"],
}

VALID_WEIGHTS = {
    "ثلاثي": ["فَعَلَ", "فَعِلَ", "فَعُلَ", "فَعْلَ", "فِعْلَ", "فُعْلَ"],
    "رباعي": ["فَعْلَلَ", "فِعْلِلَ", "فُعْلُلَ", "فَعْلِلَ", "فِعْلَلَ"],
    "مزيد": ["أَفْعَلَ", "تَفَعَّلَ", "تَفاعَلَ", "انْفَعَلَ", "افْتَعَلَ", "افْعَلَّ"],
    "اسم": ["فَعِيل", "فَعُول", "مَفْعُل", "مَفْعِل", "فِعِّيل", "فُعُول"],
}

FORBIDDEN_WEIGHT_TRANSITIONS = {
    ("CVCC", "CV"),
}


# =========================
# Combinatorics: closed-form counts
# =========================
def C(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    num = 1
    den = 1
    for i in range(1, k + 1):
        num *= n - (k - i)
        den *= i
    return num // den


def P(n: int, k: int) -> int:
    res = 1
    for i in range(k):
        res *= n - i
    return res


def closed_form_counts(Cn: int, Vshort: int, Vlong: int) -> Dict[str, int]:
    return {
        "CV": Cn * Vshort,
        "VC": Vshort * Cn,
        "CVC": Cn * Vshort * Cn,
        "CVV": Cn * Vlong,
        "CVVC": Cn * Vlong * Cn,
        "CVCC": Cn * Vshort * Cn * Cn,
    }


# =========================
# Theoretical generators (per gate)
# =========================
def gen_C() -> Iterable[str]:
    for c in AR_CONS:
        if c not in LONG:
            yield c


def gen_V_short() -> Iterable[str]:
    for v in SHORT:
        yield v


def gen_V_long() -> Iterable[str]:
    for v in LONG:
        yield v


def generate_gate(gate: str, cap: Optional[int] = None) -> Iterable[str]:
    count = 0
    # Standard patterns
    if gate == "CV":
        for c in gen_C():
            for v in gen_V_short():
                yield c + v
                count += 1
                if cap and count >= cap:
                    return
    elif gate == "VC":
        for v in gen_V_short():
            for c in gen_C():
                yield v + c
                count += 1
                if cap and count >= cap:
                    return
    elif gate == "CVC":
        for c1 in gen_C():
            for v in gen_V_short():
                for c2 in gen_C():
                    yield c1 + v + c2
                    count += 1
                    if cap and count >= cap:
                        return
    elif gate == "CVV":
        for c in gen_C():
            for vl in gen_V_long():
                yield c + vl
                count += 1
                if cap and count >= cap:
                    return
    elif gate == "CVVC":
        for c1 in gen_C():
            for vl in gen_V_long():
                for c2 in gen_C():
                    yield c1 + vl + c2
                    count += 1
                    if cap and count >= cap:
                        return
    elif gate == "CVCC":
        for c1 in gen_C():
            for v in gen_V_short():
                for c2 in gen_C():
                    for c3 in gen_C():
                        yield c1 + v + c2 + c3
                        count += 1
                        if cap and count >= cap:
                            return
    # Extra patterns
    elif gate == "CCV":
        for c1 in gen_C():
            for c2 in gen_C():
                for v in gen_V_short():
                    yield c1 + c2 + v
                    count += 1
                    if cap and count >= cap:
                        return
    elif gate == "VCC":
        for v in gen_V_short():
            for c1 in gen_C():
                for c2 in gen_C():
                    yield v + c1 + c2
                    count += 1
                    if cap and count >= cap:
                        return
    elif gate == "CVVCC":
        for c1 in gen_C():
            for vl in gen_V_long():
                for c2 in gen_C():
                    for c3 in gen_C():
                        yield c1 + vl + c2 + c3
                        count += 1
                        if cap and count >= cap:
                            return
    elif gate == "CCVC":
        for c1 in gen_C():
            for c2 in gen_C():
                for v in gen_V_short():
                    for c3 in gen_C():
                        yield c1 + c2 + v + c3
                        count += 1
                        if cap and count >= cap:
                            return
    elif gate == "V":
        for v in gen_V_short():
            yield v
            count += 1
            if cap and count >= cap:
                return
    elif gate == "CCVV":
        for c1 in gen_C():
            for c2 in gen_C():
                for vl in gen_V_long():
                    yield c1 + c2 + vl
                    count += 1
                    if cap and count >= cap:
                        return
    else:
        return


# =========================
# Similarity (observational gate filter)
# =========================
def ngram_profile(s: str, n: int = 2) -> Counter:
    return Counter(s[i : i + n] for i in range(0, max(0, len(s) - n + 1)))


def jaccard_sim(a: str, b: str) -> float:
    A = set(a)
    B = set(b)
    if not A and not B:
        return 1.0
    return len(A & B) / max(1, len(A | B))


def bag_ngram_sim(x: str, obs: List[str], n: int = 2) -> float:
    if not obs:
        return 0.0
    px = ngram_profile(x, n)
    sims = []
    for o in obs:
        po = ngram_profile(o, n)
        inter = sum((px & po).values())
        total = sum(px.values()) + sum(po.values())
        sims.append(2 * inter / max(1, total))
    return sum(sims) / len(sims)


def filter_by_observation(theoretical: Dict[str, List[str]], threshold: float = 0.7) -> Dict[str, List[str]]:
    out = {}
    for gate, arr in theoretical.items():
        obs = OBS_SYLL.get(gate, [])
        out[gate] = [s for s in arr if bag_ngram_sim(s, obs, n=2) >= threshold]
    return out


# =========================
# Weight constraints (reverse)
# =========================
@dataclass
class WeightInfo:
    family: str
    weight: str
    gate_seq: str


def identify_weight_stub(form: str) -> Optional[WeightInfo]:
    cons = [c for c in form if c not in LONG + SHORT + TANWIN + [SUKUN, SHADDA]]
    if len(cons) == 3:
        return WeightInfo("ثلاثي", "فَعَلَ", "CVC")
    if len(cons) == 4:
        return WeightInfo("رباعي", "فَعْلَلَ", "CVCC")
    return None


def valid_weight_transition_stub(gates: List[str]) -> bool:
    for i in range(len(gates) - 1):
        if (gates[i], gates[i + 1]) in FORBIDDEN_WEIGHT_TRANSITIONS:
            return False
    return True


def apply_weight_constraints(forms: List[str]) -> List[str]:
    kept = []
    for f in forms:
        wi = identify_weight_stub(f)
        if not wi:
            continue
        if wi.family not in VALID_WEIGHTS:
            continue
        if not valid_weight_transition_stub([wi.gate_seq]):
            continue
        kept.append(f)
    return kept


# =========================
# OCP filters (reverse)
# =========================
FORBIDDEN_GEMINATION = {"بب", "تت", "ثث", "مم", "ڤڤ", "پپ", "چچ"}
SIMILAR_PLACE = {"بف", "فت", "ثس", "خش", "ڤف", "پت", "چش"}


def same_short_vowel_pair(a: str, b: str) -> bool:
    va = next((v for v in SHORT if v in a), None)
    vb = next((v for v in SHORT if v in b), None)
    return va is not None and va == vb


def segment_pairs(form: str) -> List[Tuple[str, str]]:
    segs = []
    i = 0
    while i < len(form) - 1:
        segs.append((form[i], form[i + 1]))
        i += 1
    return segs


def has_ocp_violation(form: str) -> bool:
    # Gemination without shadda, including borrowed phonemes
    for i in range(len(form) - 1):
        if form[i] == form[i + 1] and SHADDA not in form[i : i + 2]:
            return True
    # Shadda/sukun in more positions
    if form.startswith(SUKUN) or form.endswith(SUKUN):
        return True
    # Place assimilation
    for i in range(len(form) - 1):
        a, b = form[i], form[i + 1]
        if a in ARTIC_CLASSES and b in ARTIC_CLASSES:
            if ARTIC_CLASSES[a] == ARTIC_CLASSES[b] and same_short_vowel_pair(a, b):
                return True
    for a, b in segment_pairs(form):
        if (a + b) in SIMILAR_PLACE:
            return True
    return False


def apply_ocp_filter(forms: List[str]) -> List[str]:
    return [f for f in forms if not has_ocp_violation(f)]


# =========================
# Statistical filter (reverse)
# =========================
@dataclass
class StatModel:
    syll_freq: Dict[str, float]
    trans_freq: Dict[Tuple[str, str], float]


def syllables_of(form: str) -> List[str]:
    out = []
    buf = ""
    for ch in form:
        buf += ch
        if ch in SHORT or ch in LONG:
            out.append(buf)
            buf = ""
    if buf:
        out.append(buf)
    return out


def calc_prob(form: str, sm: StatModel) -> float:
    syls = syllables_of(form)
    if not syls:
        return 0.0
    p = 1.0
    for i, s in enumerate(syls):
        p *= sm.syll_freq.get(s, 1e-3)
        if i > 0:
            p *= sm.trans_freq.get((syls[i - 1], s), 1e-4)
    return p


def filter_by_probability(forms: List[str], sm: StatModel, threshold: float = 0.01) -> List[str]:
    return [f for f in forms if calc_prob(f, sm) >= threshold]


# =========================
# Corpus loader
# =========================
def load_corpus_stats(csv_path: str) -> StatModel:
    syll_freq = defaultdict(lambda: 1e-3)
    trans_freq = defaultdict(lambda: 1e-4)
    try:
        with open(csv_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                s = row.get("syllable")
                freq = float(row.get("freq", "0"))
                syll_freq[s] += freq
                # If transition columns exist
                if "prev" in row and "next" in row and "trans_freq" in row:
                    trans_freq[(row["prev"], row["next"])] += float(row["trans_freq"])
    except Exception as e:
        print(f"Corpus load error: {e}", file=sys.stderr)
    return StatModel(syll_freq, trans_freq)


# =========================
# Morphological constraint (reverse)
# =========================
def extract_root_stub(form: str) -> str:
    cons = [c for c in form if c not in LONG + SHORT + TANWIN + [SUKUN, SHADDA]]
    return "".join(cons[:3])


def identify_pattern_stub(form: str) -> str:
    wi = identify_weight_stub(form)
    return wi.weight if wi else "?"


def root_pattern_compatible_stub(root: str, pattern: str) -> bool:
    return (len(root) == 3 and "فع" in pattern) or (len(root) == 4 and "فعلل" in pattern)


def satisfies_derivational_constraints_stub(form: str) -> bool:
    return not any(v in form for v in ["ا" + t for t in TANWIN])


def apply_morphological_constraints(forms: List[str]) -> List[str]:
    kept = []
    for f in forms:
        root = extract_root_stub(f)
        pat = identify_pattern_stub(f)
        if not root_pattern_compatible_stub(root, pat):
            continue
        if not satisfies_derivational_constraints_stub(f):
            continue
        kept.append(f)
    return kept


# =========================
# Reverse pipeline
# =========================
@dataclass
class ReverseReport:
    theoretical: int
    after_syllabic: int
    after_weight: int
    after_ocp: int
    after_stat: int
    after_morph: int
    reduction_ratio: float


def generate_theoretical_pool(caps: Dict[str, int] | None = None) -> Dict[str, List[str]]:
    out = {}
    for gate in ALLOWED_GATES:
        cap = None if caps is None else caps.get(gate)
        out[gate] = list(generate_gate(gate, cap=cap))
    return out


def flatten_pool(pool: Dict[str, List[str]]) -> List[str]:
    return [x for arr in pool.values() for x in arr]


def reverse_engineer(
    pool: Dict[str, List[str]], stat: StatModel, obs_threshold=0.7, prob_threshold=0.01
) -> Tuple[List[str], ReverseReport]:
    syll_filtered = filter_by_observation(pool, threshold=obs_threshold)
    w_forms = apply_weight_constraints(flatten_pool(syll_filtered))
    ocp_forms = apply_ocp_filter(w_forms)
    stat_forms = filter_by_probability(ocp_forms, stat, threshold=prob_threshold)
    morph_forms = apply_morphological_constraints(stat_forms)
    rep = ReverseReport(
        theoretical=sum(len(v) for v in pool.values()),
        after_syllabic=sum(len(v) for v in syll_filtered.values()),
        after_weight=len(w_forms),
        after_ocp=len(ocp_forms),
        after_stat=len(stat_forms),
        after_morph=len(morph_forms),
        reduction_ratio=(sum(len(v) for v in pool.values()) - len(morph_forms))
        / max(1, sum(len(v) for v in pool.values())),
    )
    return morph_forms, rep


# =========================
# CLI
# =========================
def main():
    parser = argparse.ArgumentParser(description="Arabic phonological reverse combinatorics engine")
    parser.add_argument("--caps", type=str, help="Gate caps, e.g. CV=400,CVC=400")
    parser.add_argument("--obs-threshold", type=float, default=0.7)
    parser.add_argument("--prob-threshold", type=float, default=0.01)
    parser.add_argument("--csv", type=str, help="Corpus CSV file")
    parser.add_argument("--out-json", type=str, help="Output report JSON")
    parser.add_argument("--out-csv", type=str, help="Output filtered forms CSV")
    args = parser.parse_args()

    caps = None
    if args.caps:
        caps = {k: int(v) for k, v in (x.split("=") for x in args.caps.split(","))}
    stat = load_corpus_stats(args.csv) if args.csv else StatModel(defaultdict(lambda: 1e-3), defaultdict(lambda: 1e-4))
    pool = generate_theoretical_pool(caps)
    final_forms, report = reverse_engineer(
        pool, stat, obs_threshold=args.obs_threshold, prob_threshold=args.prob_threshold
    )

    if args.out_json:
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(report.__dict__, f, ensure_ascii=False, indent=2)
    if args.out_csv:
        with open(args.out_csv, "w", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["form"])
            for fform in final_forms:
                writer.writerow([fform])
    print("== Reverse report ==")
    print(report)
    print(f"Saved {len(final_forms)} forms.")


# Module API for programmatic use
def run_reverse_engineering(
    caps: Optional[Dict[str, int]] = None,
    csv_path: Optional[str] = None,
    obs_threshold: float = 0.7,
    prob_threshold: float = 0.01,
) -> Tuple[List[str], ReverseReport]:
    """
    Run the reverse engineering pipeline programmatically.
    """
    stat = load_corpus_stats(csv_path) if csv_path else StatModel(defaultdict(lambda: 1e-3), defaultdict(lambda: 1e-4))
    pool = generate_theoretical_pool(caps)
    return reverse_engineer(pool, stat, obs_threshold=obs_threshold, prob_threshold=prob_threshold)


if __name__ == "__main__":
    main()
