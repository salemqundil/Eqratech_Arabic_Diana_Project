"""Tests for mabniyat processing rules (قواعد المعالجة للمبنيات)."""

import pytest
from fvafk.c2b.mabni_rules import (
    MabniResult,
    classify_mabni,
    should_skip_root_extraction,
    case_for_mabni,
    agreement_from_mabni,
)


def test_classify_mabni_returns_result():
    r = classify_mabni("هذا")
    assert isinstance(r, MabniResult)
    assert r.i3rab_status in ("مبني", "معرب")


def test_classify_mabni_mu3rab_word():
    r = classify_mabni("كِتَاب")
    assert r.is_mabni is False
    assert r.i3rab_status == "معرب"
    assert r.category is None


def test_should_skip_root_extraction_accepts_word():
    # Should not raise; returns bool. If DB has مبنيات, prefixed forms should skip root.
    out = should_skip_root_extraction("لَا")
    assert isinstance(out, bool)


def test_case_for_mabni_returns_none():
    r = MabniResult(is_mabni=True, i3rab_status="مبني", category="حرف")
    assert case_for_mabni(r) is None


def test_case_for_mabni_ignores_mu3rab():
    r = MabniResult(is_mabni=False, i3rab_status="معرب")
    assert case_for_mabni(r) is None


def test_agreement_from_mabni():
    r = MabniResult(
        is_mabni=True,
        i3rab_status="مبني",
        category="اسم إشارة",
        number="مفرد",
        gender="مذكر",
    )
    d = agreement_from_mabni(r)
    assert d["number"] == "مفرد"
    assert d["gender"] == "مذكر"


def test_agreement_from_mabni_mu3rab():
    r = MabniResult(is_mabni=False, i3rab_status="معرب")
    d = agreement_from_mabni(r)
    assert d["number"] is None
    assert d["gender"] is None


def test_mabni_result_to_dict():
    r = MabniResult(
        is_mabni=True,
        i3rab_status="مبني",
        category="ضمير",
        number="جمع",
        gender="مذكر",
        stripped_prefix="وَ",
    )
    d = r.to_dict()
    assert d["is_mabni"] is True
    assert d["i3rab_status"] == "مبني"
    assert d["category"] == "ضمير"
    assert d["stripped_prefix"] == "وَ"
