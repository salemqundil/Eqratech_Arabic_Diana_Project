"""
prover.py — Explainable proof layer (XAI).

Collects all analysis results and produces a ProofReport
with structured claims, premises, and reasoning steps.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .models import (
    BuiltinAnalysis, Claim, MorphAnalysis, NormalizedText,
    ProofReport, SLineGraph, SyllableAnalysis, WeightAnalysis,
)


def prove_min_weight(
    weight_analysis: WeightAnalysis,
    threshold: int = 3,
) -> Claim:
    """Prove whether the word meets minimum weight threshold."""
    count = weight_analysis.weight_unit_count
    verdict = "مثبت" if count >= threshold else "منفي"
    return Claim(
        claim_id="weight_threshold",
        text=f"الكلمة حاملة للوزن (عدد الوحدات الحاملة ≥ {threshold})",
        verdict=verdict,
        confidence=1.0,
        premises=[f"عدد_وحدات_وزنية_فاعلة={count}", f"العتبة={threshold}"],
        reasoning_steps=[
            f"حُسب عدد الوحدات الحاملة للوزن (حامل_وزن) = {count}",
            f"العتبة الدنيا = {threshold}",
            f"النتيجة: {'حاملة وزن' if count >= threshold else 'دون الوزن'}",
        ],
        trace_ids=[wu.node_id for wu in weight_analysis.weight_units
                   if wu.weight_role == "حامل_وزن"],
    )


def prove_below_weight_category(
    weight_analysis: WeightAnalysis,
) -> Claim:
    """Prove whether word falls in 'below weight' category (دون الوزن)."""
    is_below = weight_analysis.below_weight
    return Claim(
        claim_id="below_weight",
        text="الكلمة دون الوزن (أقل من ثلاث وحدات حاملة)",
        verdict="مثبت" if is_below else "منفي",
        confidence=1.0,
        premises=[f"weight_unit_count={weight_analysis.weight_unit_count}"],
        reasoning_steps=[
            f"وحدات_حاملة_للوزن (حامل_وزن) = {weight_analysis.weight_unit_count}",
            "قاعدة: أقل الميزان ثلاث وحدات حاملة (حامل_وزن)",
            f"الحكم: {'دون الوزن' if is_below else 'ضمن الوزن'}",
        ],
        trace_ids=[],
    )


def prove_mabni_vs_mu3rab(
    builtin_analysis: BuiltinAnalysis,
    morph_analysis: MorphAnalysis,
) -> Claim:
    """Prove مبني vs معرب status."""
    if builtin_analysis.is_mabni:
        verdict = "مثبت"
        text = f"الكلمة مبنية ({builtin_analysis.mabni_type})"
        premises = [
            f"وُجدت_في_معجم_المبنيات",
            f"النوع:{builtin_analysis.mabni_type}",
            f"الوظيفة:{builtin_analysis.function}",
        ]
        steps = [
            "بُحث عن الكلمة في معجم المبنيات",
            f"النتيجة: مبني من نوع {builtin_analysis.mabni_type}",
            f"وظيفتها: {builtin_analysis.function}",
        ]
    else:
        verdict = "منفي"
        text = "الكلمة معربة (لم تُوجد في معجم المبنيات)"
        premises = ["لم_تُوجد_في_معجم_المبنيات"]
        steps = [
            "بُحث عن الكلمة في معجم المبنيات",
            "لم توجد → تُعامَل كمعربة",
            "تحتاج تحليلًا نحويًا إضافيًا",
        ]
    return Claim(
        claim_id="mabni_vs_mu3rab",
        text=text,
        verdict=verdict,
        confidence=0.9,
        premises=premises,
        reasoning_steps=steps,
        trace_ids=builtin_analysis.trace,
    )


def prove_tri_quad(morph_analysis: MorphAnalysis) -> Claim:
    """Prove ثلاثي vs رباعي classification."""
    tri_quad = morph_analysis.tri_or_quad
    verdict = "مثبت" if tri_quad in ("ثلاثي", "رباعي") else "غير_محدد"
    return Claim(
        claim_id="tri_quad",
        text=f"الكلمة {tri_quad} (بنية الجذر)",
        verdict=verdict,
        confidence=0.85,
        premises=[
            f"الجذر_المرشح={morph_analysis.root_candidate}",
            f"طول_الجذر={len(morph_analysis.root_candidate)}",
        ],
        reasoning_steps=[
            f"تم استخراج الجذر: {morph_analysis.root_candidate}",
            f"طول الجذر = {len(morph_analysis.root_candidate)}",
            f"التصنيف: {tri_quad}",
        ],
        trace_ids=morph_analysis.evidence_trace[:5],
    )


def prove_mujarrad_mazid(morph_analysis: MorphAnalysis) -> Claim:
    """Prove مجرد vs مزيد classification."""
    mm = morph_analysis.mujarrad_or_mazid
    pattern = morph_analysis.pattern_candidate
    verdict = "مثبت" if mm in ("مجرد", "مزيد") else "غير_محدد"
    return Claim(
        claim_id="mujarrad_vs_mazid",
        text=f"الكلمة {mm}" + (f" على وزن {pattern}" if pattern else ""),
        verdict=verdict,
        confidence=0.8,
        premises=[
            f"الوزن_المطابق={pattern or 'غير_محدد'}",
            f"الحروف_الزائدة={'موجودة' if mm == 'مزيد' else 'غير_موجودة'}",
        ],
        reasoning_steps=[
            f"تم فحص حروف الكلمة بحثًا عن الزوائد",
            f"الوزن المطابق: {pattern or 'لم يُطابق'}",
            f"الحكم: {mm}",
        ],
        trace_ids=morph_analysis.evidence_trace[:5],
    )


def build_proof_report(
    word: str,
    normalized: NormalizedText,
    syllable_analysis: SyllableAnalysis,
    weight_analysis: WeightAnalysis,
    builtin_analysis: BuiltinAnalysis,
    morph_analysis: MorphAnalysis,
    sline_graph: Optional[SLineGraph] = None,
) -> ProofReport:
    """
    Collect all analysis results and produce a unified ProofReport.
    """
    claims: List[Claim] = []

    # Claim 1: Weight
    claims.append(prove_min_weight(weight_analysis))

    # Claim 2: Below weight
    claims.append(prove_below_weight_category(weight_analysis))

    # Claim 3: مبني vs معرب
    claims.append(prove_mabni_vs_mu3rab(builtin_analysis, morph_analysis))

    # Claim 4: ثلاثي vs رباعي
    if morph_analysis.tri_or_quad:
        claims.append(prove_tri_quad(morph_analysis))

    # Claim 5: مجرد vs مزيد
    if morph_analysis.mujarrad_or_mazid:
        claims.append(prove_mujarrad_mazid(morph_analysis))

    # Collect all traces
    trace = (
        normalized.normalization_log
        + syllable_analysis.trace
        + weight_analysis.trace
        + builtin_analysis.trace
        + morph_analysis.evidence_trace
    )

    # Overall confidence
    confidences = [c.confidence for c in claims]
    overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0

    return ProofReport(
        word=word,
        claims=claims,
        overall_confidence=overall_confidence,
        trace=trace,
    )
