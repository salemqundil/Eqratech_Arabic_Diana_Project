# fractal_balance_v2.py
# -*- coding: utf-8 -*-
#
# نسخة v2: تستخدم cv_pattern من word-2-cv.py بدل build_syllables القديمة
# النتيجة: معالجة أصح للهمزات والمد والأدوات القصيرة

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# ============================================================
# استيراد cv_pattern من word-2-cv.py
# ضع word-2-cv.py في نفس المجلد أو عدّل المسار
# ============================================================
import importlib.util, pathlib

_W2CV_PATH = pathlib.Path(__file__).parent / "word-2-cv.py"
_spec = importlib.util.spec_from_file_location("word2cv", _W2CV_PATH)
_w2cv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_w2cv)

cv_pattern           = _w2cv.cv_pattern
normalize_initial_hamza = _w2cv.normalize_initial_hamza
normalize_word       = _w2cv.normalize_word
follows_cv_law       = _w2cv.follows_cv_law


# ============================================================
# 1) نموذج بيانات المقطع (مبسّط — مبني من سلسلة CV)
# ============================================================

@dataclass
class Syllable:
    """
    مقطع مشتق من سلسلة CV:
      pattern : مثل CV / CVC / CVV / CVVC ...
      index   : ترتيبه في الكلمة
    """
    pattern: str
    index: int

    def to_signature(self) -> str:
        return f"{self.pattern}|i{self.index}"


@dataclass
class FractalBalanceResult:
    ok: bool
    reason: str
    cv_string: str                       # السلسلة الكاملة  e.g. "CVCVCV"
    center_index: Optional[int]          # رقم المقطع المركزي
    syllables: List[Syllable]
    lower_signature: Dict[str, Any]
    diff: Dict[str, Any]
    upper_projection: Dict[str, Any]
    sline_refs: Dict[str, str]


# ============================================================
# 2) تقسيم سلسلة CV إلى مقاطع
# ============================================================

def cv_to_syllables(cv: str) -> List[Syllable]:
    """
    يقسّم سلسلة CV إلى مقاطع بالقاعدة:
      كل مقطع يبدأ بـ C (أو V إذا كانت البداية بدون صامت)
      وينتهي عند أول C تالية تسبق V جديدة.

    أنماط شائعة: CV / CVC / CVV / CVVC / CCC... (حروف وصل)
    """
    syllables: List[Syllable] = []
    i = 0
    idx = 0
    n = len(cv)

    while i < n:
        start = i
        onset = ""
        nucleus = ""
        coda = ""

        # onset: صوامت بادئة
        while i < n and cv[i] == "C":
            onset += "C"
            i += 1

        # nucleus: حركات/مد
        while i < n and cv[i] == "V":
            nucleus += "V"
            i += 1

        # إذا لا توجد نواة: لا مقطع مستقل
        if not nucleus:
            i += 1  # تجاوز
            continue

        # coda: صامت واحد فقط إذا ما تبعه V مباشرة
        if i < n and cv[i] == "C":
            if not (i + 1 < n and cv[i + 1] == "V"):
                coda = "C"
                i += 1

        pattern = onset + nucleus + coda
        syllables.append(Syllable(pattern=pattern, index=idx))
        idx += 1

    return syllables


# ============================================================
# 3) التوقيع الأدنى (س.خط lower)
# ============================================================

def build_lower_signature(syllables: List[Syllable], center_index: int = 1) -> Dict[str, Any]:
    if not syllables:
        return {"ok": False, "reason": "empty"}
    if center_index < 0 or center_index >= len(syllables):
        return {"ok": False, "reason": "center_out_of_range"}

    center = syllables[center_index]
    prev_s = syllables[center_index - 1] if center_index - 1 >= 0 else None
    next_s = syllables[center_index + 1] if center_index + 1 < len(syllables) else None

    def shape(s: Optional[Syllable]) -> str:
        if not s:
            return "∅"
        c_count = s.pattern.count("C")
        v_count = s.pattern.count("V")
        return f"C{c_count}V{v_count}"

    return {
        "ok": True,
        "center_index": center_index,
        "prev":   prev_s.to_signature() if prev_s else None,
        "center": center.to_signature(),
        "next":   next_s.to_signature() if next_s else None,
        "lower_shapes": {
            "prev":   shape(prev_s),
            "center": shape(center),
            "next":   shape(next_s),
        },
        "sline": {
            "before_ref": f"S[{center_index-1}]" if prev_s else "∅",
            "center_ref": f"S[{center_index}]",
            "after_ref":  f"S[{center_index+1}]" if next_s else "∅",
            "down_ref":   f"Σlow[{center_index}]",
        },
    }


# ============================================================
# 4) الفروق البنيوية (diff)
# ============================================================

def diff_signature(lower_sig: Dict[str, Any]) -> Dict[str, Any]:
    if not lower_sig.get("ok"):
        return {"ok": False, "reason": "invalid_lower_sig"}

    def parse(shape: str) -> Tuple[int, int]:
        if shape == "∅":
            return (0, 0)
        c = int(shape.split("V")[0].replace("C", "") or 0)
        v = int(shape.split("V")[1] if "V" in shape else 0)
        return (c, v)

    p = parse(lower_sig["lower_shapes"]["prev"])
    c = parse(lower_sig["lower_shapes"]["center"])
    n = parse(lower_sig["lower_shapes"]["next"])

    return {
        "ok": True,
        "prev_vs_center": {"d_C": c[0]-p[0], "d_V": c[1]-p[1]},
        "center_vs_next": {"d_C": n[0]-c[0], "d_V": n[1]-c[1]},
        "continuity": {
            "has_prev":          lower_sig["lower_shapes"]["prev"] != "∅",
            "has_next":          lower_sig["lower_shapes"]["next"] != "∅",
            "center_has_nucleus": c[1] > 0,
        },
    }


# ============================================================
# 5) الإسقاط الأعلى (upper projection)
# ============================================================

def infer_upper_projection(lower_sig: Dict[str, Any], diff_sig: Dict[str, Any]) -> Dict[str, Any]:
    if not (lower_sig.get("ok") and diff_sig.get("ok")):
        return {"ok": False, "reason": "invalid_inputs"}

    cont = diff_sig["continuity"]
    balanced = bool(cont["has_prev"] and cont["has_next"] and cont["center_has_nucleus"])

    return {
        "ok": True,
        "has_triplet_balance": balanced,
        "weight_candidate":    balanced,
        "class_hint": "WEIGHT_CANDIDATE" if balanced else "UNDER_WEIGHT",
        "sline_upper": {
            "up_ref":       f"Σup[{lower_sig['center_index']}]",
            "center_anchor": lower_sig["sline"]["center_ref"],
            "before_link":   lower_sig["sline"]["before_ref"],
            "after_link":    lower_sig["sline"]["after_ref"],
        },
        "proof_notes": [
            "الحد الأدنى للتوازن: مركز + سابق + لاحق",
            "المركز بلا نواة لا يشكّل مقطعاً مستقلاً",
            "ما دون الثلاثية → طبقة الوظائف/الإحالة",
        ],
    }


# ============================================================
# 6) الدالة الرئيسية
# ============================================================

def fractal_min_balance(text: str, *, return_debug: bool = True) -> FractalBalanceResult:
    """
    سلسلة القرار الكاملة (v2):
      1) normalize_word + normalize_initial_hamza  (من word-2-cv)
      2) cv_pattern                                (من word-2-cv)
      3) cv_to_syllables
      4) بدء من المقطع الثاني (index=1)
      5) lower_signature → diff → upper_projection
    """
    norm = normalize_initial_hamza(normalize_word(text))
    cv   = cv_pattern(norm)
    sylls = cv_to_syllables(cv)

    _empty = lambda r: FractalBalanceResult(
        ok=False, reason=r, cv_string=cv,
        center_index=None, syllables=sylls,
        lower_signature={"ok": False, "reason": r},
        diff={"ok": False, "reason": r},
        upper_projection={"ok": False, "reason": r},
        sline_refs={},
    )

    if not cv:
        return _empty("cv_empty")

    if len(sylls) < 2:
        return _empty("لا يوجد مقطع ثانٍ؛ البنية دون الحد الأدنى.")

    center_index = 1
    lower  = build_lower_signature(sylls, center_index)
    diff   = diff_signature(lower)
    upper  = infer_upper_projection(lower, diff)

    ok     = bool(upper.get("has_triplet_balance"))
    reason = (
        "تحقق الاتزان الفراكتالي الأدنى (ثلاثية: قبل/مركز/بعد)."
        if ok else
        "لم يتحقق الاتزان الفراكتالي الأدنى."
    )

    sline_refs: Dict[str, str] = {}
    if lower.get("ok"):
        sline_refs.update(lower.get("sline", {}))
    if upper.get("ok"):
        sline_refs.update(upper.get("sline_upper", {}))

    if return_debug:
        lower["debug"] = {
            "normalized":      norm,
            "cv_string":       cv,
            "syllables_count": len(sylls),
            "syllables":       [s.to_signature() for s in sylls],
        }

    return FractalBalanceResult(
        ok=ok, reason=reason, cv_string=cv,
        center_index=center_index, syllables=sylls,
        lower_signature=lower, diff=diff,
        upper_projection=upper, sline_refs=sline_refs,
    )


# ============================================================
# 7) طباعة نتيجة
# ============================================================

def pretty(res: FractalBalanceResult) -> None:
    print("=" * 65)
    print(f"CV     : {res.cv_string}")
    print(f"SYLLS  : {[s.to_signature() for s in res.syllables]}")
    print(f"OK     : {res.ok}")
    print(f"CLASS  : {res.upper_projection.get('class_hint', '-')}")
    print(f"REASON : {res.reason}")
    print("=" * 65)


# ============================================================
# 8) اختبار سريع
# ============================================================

if __name__ == "__main__":
    samples = [
        # أدوات — يجب أن تكون UNDER_WEIGHT
        ("إِلَى",    "حرف جر"),
        ("أَنْ",     "حرف مصدري"),
        ("كَانَ",    "فعل ناقص - مقطعان"),
        ("وَلَا",    "أداة"),
        ("هُوَ",     "ضمير"),
        ("مَا",      "أداة"),
        ("لَا",      "أداة"),
        ("أَوْ",     "حرف عطف"),
        ("مِنْ",     "حرف جر"),
        # أفعال — يجب أن تكون WEIGHT_CANDIDATE
        ("كَتَبَ",   "ثلاثي مجرد"),
        ("فَعَلَ",   "ثلاثي مجرد"),
        ("دَحْرَجَ", "رباعي مجرد"),
        ("اللَّهُ",  "لفظ الجلالة"),
        ("مُسَمًّى", "اسم مفعول"),
        ("يَسْتَطِيعُ", "فعل مزيد"),
    ]

    for word, desc in samples:
        r = fractal_min_balance(word)
        mark = "✅" if r.ok else "⚪"
        hint = r.upper_projection.get("class_hint", "-")
        print(f"{mark} {word:15} | {hint:18} | CV: {r.cv_string:15} | {desc}")
