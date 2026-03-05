# -*- coding: utf-8 -*-
"""
قواعد فعل الأمر — تحميل من arabic_json واستخدامها في استخراج الجذر.
إسناد فعل الأمر والمعتل الناقص (تر→رأي، تك/يك→كون، هب→وهب، قل/يقل→قول).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

# مسار الملف: data/arabic_json/2/المبنيات من الأفعال/الأفعال المبنية /إسناد فعل الأمر والمعتل الناقص.json
_BASE = Path(__file__).resolve().parent.parent.parent.parent
_IMPERATIVE_JSON = (
    _BASE
    / "data"
    / "arabic_json"
    / "2"
    / "المبنيات من الأفعال"
    / "الأفعال المبنية "
    / "إسناد فعل الأمر والمعتل الناقص.json"
)

_imperative_cache: Dict[str, Any] | None = None


def load_imperative_rules() -> Dict[str, Any]:
    """
    تحميل قواعد فعل الأمر من JSON (مرة واحدة، مع تخزين مؤقت).
    الإرجاع: dict يحتوي على title, description, building_rules, defective_imperative_stems, notes.
    """
    global _imperative_cache
    if _imperative_cache is not None:
        return _imperative_cache
    if not _IMPERATIVE_JSON.exists():
        _imperative_cache = {
            "title": "",
            "description": "",
            "building_rules": [],
            "defective_imperative_stems": {},
            "notes": [],
        }
        return _imperative_cache
    with open(_IMPERATIVE_JSON, encoding="utf-8") as f:
        _imperative_cache = json.load(f)
    return _imperative_cache


def get_building_rules() -> List[Dict[str, Any]]:
    """قواعد بناء فعل الأمر (الحالة، علامة البناء، الأمثلة، الوصف)."""
    data = load_imperative_rules()
    return data.get("building_rules", [])


def get_defective_imperative_stems() -> Dict[str, str]:
    """
    جذور المجزوم المعتل الناقص: مفتاح = صيغة مجردة (تر، تك، هب، قل، ...)، قيمة = الجذر (رأي، كون، وهب، قول).
    للاستخدام في STRIPPED_CORRECTIONS أو في الـ resolver.
    """
    data = load_imperative_rules()
    return dict(data.get("defective_imperative_stems", {}))
