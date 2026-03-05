"""
قواعد المعالجة للمبنيات (Mabniyat Processing Rules)
----------------------------------------------------
Module that applies the six canonical rules for processing indeclinable words (المبنيات)
and exposes a single entry point for classification and rule application.

القواعد الست (The six rules):
1) لا إعراب ظاهر — المبنى لا يغيّر حركة آخره؛ لا نستنتج حالة إعرابية من حركة الآخر.
2) لا استخراج جذر صرفي — تخطي استخراج الجذر لأي كلمة في قاعدة المبنيات.
3) المحل الإعرابي من السياق — إن وُجد إعراب للمبني فهو محل إعرابي (في محل رفع/نصب/جر) فقط.
4) التطابق (عدد/جنس) من نوع المبنى — من حقول القاعدة (العدد، الجنس) وليس من الحركة.
5) إمكانية الالتصاق — البحث مع نزع البادئات (وَ، فَ، …) لمعرفة الكلمة المبنية.
6) التصنيف النحوي — التعامل مع المبنى كحرف أو اسم مبني أو ضمير دون إعراب ظاهر.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

# Lazy import to avoid circular dependency; callers pass db or we use get_special_words_db
def _get_db():
    from .operators_particles_db import get_special_words_db
    return get_special_words_db()


@dataclass(frozen=True)
class MabniResult:
    """Result of mabni classification and rule application."""
    is_mabni: bool
    i3rab_status: str  # "مبني" or "معرب"
    category: Optional[str] = None
    number: Optional[str] = None
    gender: Optional[str] = None
    grammatical_status: Optional[str] = None
    stripped_prefix: Optional[str] = None  # if found via prefix stripping (Rule 5)
    raw_entry: Optional[Dict[str, Any]] = None  # full DB entry if needed

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_mabni": self.is_mabni,
            "i3rab_status": self.i3rab_status,
            "category": self.category,
            "number": self.number,
            "gender": self.gender,
            "grammatical_status": self.grammatical_status,
            "stripped_prefix": self.stripped_prefix,
        }


# Rule 2 + 5: use DB lookup with prefix stripping so prefixed mabniyat are still skipped for root
def should_skip_root_extraction(word: str, db: Optional[Any] = None) -> bool:
    """Rule 2 & 5: Skip root extraction for any word that is mabni (including with prefix)."""
    db = db or _get_db()
    direct = db.lookup(word)
    if direct is not None:
        return True
    pair = db.lookup_with_prefix_stripping(word)
    return pair is not None


# Main entry: classify word as mabni/mu3rab and return result for rule application
def classify_mabni(word: str, db: Optional[Any] = None) -> MabniResult:
    """
    Classify word as مبني or معرب using operators_particles_db.
    Uses direct lookup and lookup_with_prefix_stripping (Rule 5).
    Returns MabniResult with is_mabni, i3rab_status, and optional category/number/gender (Rule 4).
    """
    db = db or _get_db()
    if not word or not word.strip():
        return MabniResult(is_mabni=False, i3rab_status="معرب")

    direct = db.lookup(word)
    if direct is not None:
        return MabniResult(
            is_mabni=True,
            i3rab_status="مبني",
            category=direct.category,
            number=direct.number or None,
            gender=direct.gender or None,
            grammatical_status=direct.grammatical_status or None,
            stripped_prefix=None,
            raw_entry=None,
        )

    pair = db.lookup_with_prefix_stripping(word)
    if pair is not None:
        special, prefix = pair
        return MabniResult(
            is_mabni=True,
            i3rab_status="مبني",
            category=special.category,
            number=special.number or None,
            gender=special.gender or None,
            grammatical_status=special.grammatical_status or None,
            stripped_prefix=prefix,
            raw_entry=None,
        )

    return MabniResult(is_mabni=False, i3rab_status="معرب")


# Rule 1: For features — do not infer case from vowel when is_mabni is True
def case_for_mabni(mabni_result: MabniResult) -> Optional[str]:
    """
    Rule 1 & 3: Mabniyat have no visible case from vowel; mahall from context only.
    Returns None so downstream does not set case from token.
    """
    if not mabni_result.is_mabni:
        return None
    return None  # explicit: no case from form for mabni


# Rule 4: Number/gender from DB when mabni
def agreement_from_mabni(mabni_result: MabniResult) -> Dict[str, Optional[str]]:
    """Rule 4: Return number and gender from mabni type (DB), not from case."""
    if not mabni_result.is_mabni:
        return {"number": None, "gender": None}
    return {
        "number": mabni_result.number,
        "gender": mabni_result.gender,
    }
