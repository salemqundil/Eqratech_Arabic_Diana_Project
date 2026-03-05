# -*- coding: utf-8 -*-
"""
src/fvafk/c2b/root_resolver/heuristic.py

Fallback لاستخراج الجذر عندما يفشل MinimalCLI و WaznAdapter معاً.

...

الشدة `ّ` ليست حركة في سياقنا عند استخراج الجذر: هي علامة بنيوية تعني تضعيف الحرف
(تكراره). لذلك نحافظ عليها أثناء التجهيز ثم نوسّعها إلى تكرار حرف قبل استنتاج الجذر.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .roots_db import RootsDB

SHADDA = "\u0651"

# حروف الزيادة مرتبة بالأولوية
ZIYADA_GROUP1 = list("واي")       # حروف المد — أكثر شيوعاً كزيادة
ZIYADA_GROUP2 = list("مستألنه")   # بوادئ ولواحق شائعة
ZIYADA_LETTERS = set("سألتمونيها")

NO_ROOT_KINDS = frozenset({
    "particle", "operator", "demonstrative",
    "conjunction", "mabni", "name",
})

# لفظ الجلالة — لا جذر
_NO_ROOT_BARE = frozenset({"الله", "اللهم", "لله"})

_AJAMI_LETTERS = set("پچژگ")

# مستعارة من linguistic_data.py (MASAQ segmenter)
# أسماء تبدأ بحروف مضارعة — لا تُجرَّد بادئتها
NOUN_EXCEPTIONS = {
    'يوم', 'يد', 'يمين', 'يسار', 'يقين', 'يتيم', 'يهود', 'يوسف', 'يعقوب',
    'تراب', 'توبة', 'تجارة', 'تمر', 'تين', 'توراة', 'تابوت', 'تسع',
    'نسب', 'ناس', 'نار', 'نور', 'نبي', 'نفس', 'نعمة', 'نجم', 'نهر',
    'نساء', 'نزال', 'نعم',
    'أرض', 'أمر', 'أهل', 'أب', 'أم', 'أخ', 'أخت', 'إنسان', 'أمة',
    'أيام', 'آدم', 'إبراهيم',
}

# كلمات كاملة لا تُجرَّد — تُعاد كما هي إن كانت جذراً صحيحاً
FULL_WORD_EXCEPTIONS = {
    'نبي', 'علي', 'إلي', 'لدي', 'في', 'هي', 'أبي', 'أخي',
    'لعل', 'ليت', 'لكن', 'إلا', 'ألا', 'إنما', 'كأن', 'لأن',
    'بين', 'حين', 'أين', 'كيف', 'حيث', 'كلما', 'فيما', 'لما',
    'بما', 'عما', 'مما', 'إذا', 'إذ', 'ذا', 'ذاك', 'هذا', 'هذه',
    'هؤلاء', 'أولئك', 'ذلك', 'تلك',
    'أما', 'إما', 'أو', 'أم', 'عن', 'من', 'لن', 'لم', 'كي', 'قد',
    'هل', 'بل', 'لا', 'ما', 'سوف', 'أن', 'إن', 'أي',
    'أنا', 'أنت', 'أنتما', 'أنتم', 'أنتن', 'نحن', 'هو', 'هما', 'هم', 'هن',
    'الله', 'اللهم',
    'على', 'كان', 'بعد', 'أنفس', 'أنزل', 'بعض',
}


@dataclass
class HeuristicResult:
    root: str
    confidence: float
    reason: str


def _is_ajami(word: str) -> bool:
    return any(c in _AJAMI_LETTERS for c in word)


def _remove_diacritics_keep_shadda(text: str) -> str:
    """
    Remove Arabic harakat but KEEP shadda.
    We keep shadda because it is structural for gemination (doubling the consonant).
    """
    return "".join(
        c for c in text
        if not (
            (0x064B <= ord(c) <= 0x0650)  # tanwin + fatha/damma/kasra
            or ord(c) == 0x0652           # sukun
            or ord(c) == 0x0670           # superscript alef
        )
    )


def _expand_shadda(text: str) -> str:
    """
    Expand shadda by duplicating the previous base letter.

    Example:
      "شُحَّ" after stripping harakat (keep shadda) => "شحّ"
      expand => "شحح"
    """
    out: list[str] = []
    for ch in text:
        if ch == SHADDA:
            if out:
                out.append(out[-1])
            continue
        out.append(ch)
    return "".join(out)


def _strip_edges(letters: str, priority: List[str], roots_db: "RootsDB", depth: int = 0) -> Optional[str]:
    """
    يحذف من الأطراف فقط (أول حرف أو آخر حرف)
    إذا كان من حروف الزيادة ذات الأولوية.
    يعمل بشكل تكراري حتى يصل لـ 3 حروف موجودة في roots_db.
    """
    if depth > 6:
        return None
    if len(letters) < 3:
        return None
    if len(letters) == 3:
        return letters if roots_db.is_valid(letters) else None

    candidates = []

    # حذف من البداية
    if letters[0] in priority:
        candidates.append(letters[1:])

    # حذف من النهاية
    if letters[-1] in priority:
        candidates.append(letters[:-1])

    for candidate in candidates:
        if len(candidate) == 3:
            if roots_db.is_valid(candidate):
                return candidate
        elif len(candidate) > 3:
            result = _strip_edges(candidate, priority, roots_db, depth + 1)
            if result:
                return result

    return None


def _strip_ziyada(letters: str, roots_db: "RootsDB") -> Optional[str]:
    """يجرب تجريد الزيادة من الأطراف بمجموعتين."""
    # المجموعة 1: حروف المد أولاً
    result = _strip_edges(letters, ZIYADA_GROUP1, roots_db)
    if result:
        return result
    # المجموعة 2: باقي الزيادة
    result = _strip_edges(letters, ZIYADA_GROUP2, roots_db)
    return result


def heuristic_root(
    word: str,
    stripped: str,
    kind: str,
    roots_db: "RootsDB",
) -> HeuristicResult:
    """يستخرج الجذر بالطريقة الاستدلالية كـ fallback أخير."""

    # 1. أدوات وحروف وأسماء (لا جذر)
    if kind in NO_ROOT_KINDS:
        return HeuristicResult(root="", confidence=1.0, reason="no_root_particle")

    # 1b. لفظ الجلالة وأشكاله
    base = stripped if stripped and stripped.strip() else word

    # Keep shadda, then expand it to preserve gemination in the letters stream
    letters_raw = _remove_diacritics_keep_shadda(base).replace("-", "").strip()
    letters = _expand_shadda(letters_raw).replace(SHADDA, "")

    if letters in _NO_ROOT_BARE:
        return HeuristicResult(root="", confidence=1.0, reason="لفظ_الجلالة")

    # Conservative: prepositional clitic "بِـ" + hamza forms (e.g., بأنفسهم, بأنا)
    # These are not suitable for root guessing in heuristic mode.
    if letters.startswith("بأ") or letters.startswith("با"):
        return HeuristicResult(root="", confidence=0.90, reason="clitic_ba_hamza_compound")

    # 2. أعجمية
    if _is_ajami(word):
        return HeuristicResult(root="", confidence=0.9, reason="ajami_word")

    # 3. تحضير الحروف (base/letters قد تكون جاهزة من 1b)
    if not letters:
        base = stripped if stripped and stripped.strip() else word
        letters_raw = _remove_diacritics_keep_shadda(base).replace("-", "").strip()
        letters = _expand_shadda(letters_raw).replace(SHADDA, "")

    if not letters:
        return HeuristicResult(root="", confidence=0.0, reason="empty_input")

    # 3b. كلمة كاملة لا تُجرَّد
    if letters in FULL_WORD_EXCEPTIONS:
        return HeuristicResult(root="", confidence=0.9, reason="full_word_exception")

    # 3c. اسم يبدأ بحرف مضارعة — لا يُجرَّد
    if letters in NOUN_EXCEPTIONS:
        if roots_db.is_valid(letters):
            return HeuristicResult(root=letters, confidence=0.80, reason="noun_exception_verified")
        return HeuristicResult(root=letters, confidence=0.5, reason="noun_exception_unverified")

    # 4. 3 حروف مباشرة
    if len(letters) == 3:
        if roots_db.is_valid(letters):
            return HeuristicResult(root=letters, confidence=0.75, reason="three_letters_verified")
        return HeuristicResult(root=letters, confidence=0.4, reason="three_letters_unverified")

    # 5. أكثر من 3 → تجريد من الأطراف
    if len(letters) > 3:
        root = _strip_ziyada(letters, roots_db)
        if root:
            return HeuristicResult(root=root, confidence=0.55, reason="ziyada_stripped_verified")

    # 6. fallback أخير
    fallback = letters[:3]
    if roots_db.is_valid(fallback):
        return HeuristicResult(root=fallback, confidence=0.2, reason="first_three_verified")

    return HeuristicResult(root=fallback, confidence=0.1, reason="first_three_unverified")