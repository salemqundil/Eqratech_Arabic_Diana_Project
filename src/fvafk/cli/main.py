"""
Minimal CLI for FVAFK pipeline.

Usage:
    python -m fvafk.cli "كِتَابٌ" --json
    python -m fvafk.cli "كَاتِبٌ" --morphology --json
    python -m fvafk.cli "text" --verbose
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any, Dict, List, Optional

from fvafk.c1 import C1Encoder
from fvafk.c1.cv_pattern import analyze_text_for_cv_after_phonology
from fvafk.c1.unit import Unit, UnitCategory
from fvafk.c2a import (
    GateDeletion,
    GateEpenthesis,
    GateFramework,
    GateHamza,
    GateIdgham,
    GateMadd,
    GateShadda,
    GateSukun,
    GateWasl,
    GateWaqf,
        GateAssimilation,
        GateTanwin,
)
from fvafk.c2a.gate_framework import GateOrchestrator, GateResult, PhonologicalGate
from fvafk.c2a.syllable import Segment
from fvafk.c2b import PatternMatcher, RootExtractor
from fvafk.c2b.morpheme import Pattern, PatternType, Root, RootType


class MinimalCLI:
    """
    Minimal command-line interface for FVAFK.

    Runs the full pipeline: C1 (encoding) → C2a (phonology) → C2b (morphology)
    """

    def __init__(self, verbose: bool = False, json_output: bool = False) -> None:
        """Initialize CLI with encoder and gate orchestrator."""
        self.c1_encoder = C1Encoder()
        self._verbose_default = verbose
        self._json_output_default = json_output

        gates = [
            GateSukun(),
            GateIdgham(),
            GateShadda(),
            GateWasl(),
            GateHamza(),
            GateWaqf(),
            GateMadd(),
                GateAssimilation(),
                GateTanwin(),
            GateDeletion(),
            GateEpenthesis(),
        ]

        self.orchestrator = GateOrchestrator(gates=gates)

    def run(
        self,
        text: str,
        verbose: bool = False,
        morphology: bool = False,
        multi_word: bool = False,
        phonology_v2: bool = False,
        phonology_v2_details: bool = False,
        phonology_v2_witnesses: bool = False,
    ) -> Dict[str, Any]:
        """Run full FVAFK pipeline."""
        start = time.perf_counter()

        c1_start = time.perf_counter()
        segments = self.c1_encoder.encode(text)
        c1_time = (time.perf_counter() - c1_start) * 1000

        c2a_start = time.perf_counter()
        final_segments, gate_results = self.orchestrator.run(segments)
        paired_gate_results = list(
            zip(self.orchestrator.gates[: len(gate_results)], gate_results)
        )

        syllable_count = self._count_syllables(final_segments)
        c2a_time = (time.perf_counter() - c2a_start) * 1000

        morphology_result: Optional[Dict[str, Any]] = None
        c2b_time = 0.0

        if morphology:
            c2b_start = time.perf_counter()
            # If input contains multiple Arabic tokens, force multi-word analysis.
            if multi_word:
                morphology_result = self._analyze_morphology_multi_word(text)
            else:
                from fvafk.c2b.word_boundary import WordBoundaryDetector

                tokens = WordBoundaryDetector().detect(text)
                if len(tokens) > 1:
                    morphology_result = self._analyze_morphology_multi_word(text)
                else:
                    morphology_result = self._analyze_morphology(text)
            c2b_time = (time.perf_counter() - c2b_start) * 1000

        # ========================================================================
        # SYNTAX LAYER (Sprint 1, Task #1.7 — PR-A: CLI Syntax Wiring)
        # Output only when --morphology; no separate --syntax flag (conservative).
        # Schema: syntax.word_forms + syntax.links.isnadi
        # ========================================================================
        syntax_result = None
        if morphology and morphology_result:
            try:
                from fvafk.c2b.word_form import WordFormBuilder
                from fvafk.syntax.linkers import find_isnadi_links

                c2b_words = (
                    morphology_result["words"]
                    if isinstance(morphology_result.get("words"), list)
                    else [morphology_result]
                )
                if not c2b_words:
                    syntax_result = {"word_forms": [], "links": {"isnadi": []}}
                else:
                    builder = WordFormBuilder()
                    word_forms = [builder.from_multi_word_item(item) for item in c2b_words]
                    word_forms_out = [
                        _word_form_to_syntax_dict(wf, i) for i, wf in enumerate(word_forms)
                    ]
                    links = find_isnadi_links(word_forms)

                    CASE_ARABIC = {
                        "nominative": "مرفوع",
                        "accusative": "منصوب",
                        "genitive": "مجرور",
                        "accusative_or_genitive": "منصوب أو مجرور",
                        "unknown": "غير معروف",
                    }

                    isnadi_links = []
                    for link in links:
                        head_word = word_forms[link.head_id]
                        dep_word = word_forms[link.dependent_id]
                        head_case = (
                            CASE_ARABIC.get(head_word.case.value, "غير معروف")
                            if head_word.case else "غير معروف"
                        )
                        dep_case = (
                            CASE_ARABIC.get(dep_word.case.value, "غير معروف")
                            if dep_word.case else "غير معروف"
                        )
                        isnadi_links.append({
                            "type": getattr(link.link_type, "arabic", str(link.link_type)),
                            "type_en": link.link_type.name,
                            "head": {
                                "id": link.head_id,
                                "surface": head_word.surface,
                                "pos": head_word.pos.value,
                                "case": head_case,
                            },
                            "dependent": {
                                "id": link.dependent_id,
                                "surface": dep_word.surface,
                                "pos": dep_word.pos.value,
                                "case": dep_case,
                            },
                            "confidence": round(link.confidence, 3),
                            "reason": link.reason or "",
                        })

                    syntax_result = {
                        "word_forms": word_forms_out,
                        "links": {"isnadi": isnadi_links},
                    }
            except Exception as e:
                syntax_result = {
                    "error": str(e),
                    "word_forms": [],
                    "links": {"isnadi": []},
                }

        total_time = (time.perf_counter() - start) * 1000

        unit_rows = [self._segment_to_unit(s) for s in segments]
        cv_analysis = analyze_text_for_cv_after_phonology(
            text, engine="phonology_v2" if phonology_v2 else "c2a"
        )

        result: Dict[str, Any] = {
            "input": text,
            "success": True,
            "c1": {
                "num_units": len(unit_rows),
                "units": [self._unit_to_dict(u) for u in unit_rows] if verbose else None,
                "cv_analysis": cv_analysis,
            },
            "c2a": {
                "gates": [
                    self._gate_result_to_dict(gate, gr)
                    for gate, gr in paired_gate_results
                ],
                "syllables": {
                    "count": syllable_count,
                    "syllables": None,
                },
            },
            "stats": {
                "c1_time_ms": c1_time,
                "c2a_time_ms": c2a_time,
                "c2b_time_ms": c2b_time if morphology else None,
                "total_time_ms": total_time,
                "gates_count": len(paired_gate_results),
            },
        }

        # Optional Phonology V2 detailed trace (separate from cv_analysis.words)
        if phonology_v2 and phonology_v2_details:
            result["c2a"]["phonology_v2"] = self._phonology_v2_details_for_text(
                text, include_witnesses=phonology_v2_witnesses
            )

        if morphology_result:
            result["c2b"] = morphology_result

        if syntax_result is not None:
            result["syntax"] = syntax_result

        return result

    def _phonology_v2_details_for_text(self, text: str, *, include_witnesses: bool) -> Dict[str, Any]:
        from fvafk.c1.cv_pattern import should_exclude
        from fvafk.c2b.special_words_catalog import get_special_words_catalog
        from fvafk.c2b.word_boundary import WordBoundaryDetector
        from fvafk.phonology_v2.phonology_adapter import PhonologyV2Adapter

        spans = WordBoundaryDetector().detect(text)
        catalog = get_special_words_catalog()
        adapter = PhonologyV2Adapter()

        excluded_names = 0
        analyzed = []
        for sp in spans:
            tok = sp.token
            if should_exclude(tok):
                continue
            special = catalog.classify(tok)
            if special and special.get("kind") == "excluded_name":
                excluded_names += 1
                continue
            r = adapter.analyze_word(tok)
            item = {
                "word": tok,
                "span": {"start": sp.start, "end": sp.end},
                "success": bool(r.get("success")),
                "cv": r.get("cv_pattern") or "",
                "syllabification": r.get("syllabification") or "",
                "syllable_count": r.get("syllable_count") or 0,
                "version": r.get("version") or None,
            }
            if not r.get("success"):
                item["error"] = r.get("error") or "unknown_error"
            if include_witnesses:
                item["witnesses"] = r.get("witnesses") or []
            analyzed.append(item)

        return {
            "total_words_input": len(spans),
            "total_words_analyzed": len(analyzed),
            "excluded_names": excluded_names,
            "include_witnesses": include_witnesses,
            "words": analyzed,
        }

    def process(self, text: str) -> Dict[str, Any]:
        """Backward-compatible `process` entry point from legacy CLI."""
        return self.run(text=text, verbose=self._verbose_default)

    def _segment_to_unit(self, segment: Segment) -> Unit:
        from fvafk.c2a.syllable import SegmentKind

        category = UnitCategory.LETTER
        if segment.kind == SegmentKind.VOWEL:
            category = UnitCategory.DIAC
        return Unit(text=segment.text, category=category)

    def _analyze_morphology(self, text: str) -> Dict[str, Any]:
        from fvafk.c2b.features import extract_features
        from fvafk.c2b.mabni_rules import classify_mabni
        from fvafk.c2b.root_extractor import RootExtractionResult
        from fvafk.c2b.pattern_analyzer import PatternAnalyzer
        from fvafk.c2b.word_classifier import WordClassifier, WordKind

        mabni_result = classify_mabni(text)
        if mabni_result.is_mabni:
            bare = "".join(c for c in text if not (ord(c) in range(0x064B, 0x0653) or c == "\u0670"))
            dummy = RootExtractionResult(
                root=None,
                normalized_word=bare or text,
                stripped_word=bare or text,
                prefix="",
                suffix="",
            )
            return {
                "kind": "mabni",
                "mabni": mabni_result.to_dict(),
                "root": None,
                "pattern": None,
                "features": extract_features(text, dummy, None, WordKind.PARTICLE, mabni_result=mabni_result),
            }

        classifier = WordClassifier()
        classification = classifier.classify(text)
        if classification.kind == WordKind.OPERATOR and classification.operator:
            return {
                "kind": "operator",
                "operator": classification.operator,
                "root": None,
                "pattern": None,
            }
        if classification.kind in {WordKind.DEMONSTRATIVE, WordKind.NAME, WordKind.PARTICLE}:
            bare = (classification.special or {}).get("token_bare") if classification.special else None
            bare = bare or text
            dummy_suffix = None
            if classification.kind == WordKind.PARTICLE:
                dummy_suffix = ((classification.special or {}).get("attached_pronoun") or {}).get("suffix")
            dummy = RootExtractionResult(
                root=None,
                normalized_word=bare,
                stripped_word=bare,
                prefix="",
                suffix=dummy_suffix or "",
            )
            payload_key = "special"
            kind_value = classification.kind.value
            if classification.kind == WordKind.NAME:
                payload_key = "name"
            elif classification.kind == WordKind.DEMONSTRATIVE:
                payload_key = "demonstrative"
            elif classification.kind == WordKind.PARTICLE:
                payload_key = "particle"
            return {
                "kind": kind_value,
                payload_key: classification.special,
                "root": None,
                "pattern": None,
                "features": extract_features(text, dummy, None, classification.kind, mabni_result=mabni_result),
            }

        # Detached pronouns: do not attempt root/pattern.
        if classification.kind == WordKind.PRONOUN:
            bare = (classification.pronoun or {}).get("bare") if classification.pronoun else None
            bare = bare or text
            dummy = RootExtractionResult(
                root=None,
                normalized_word=bare,
                stripped_word=bare,
                prefix="",
                suffix="",
            )
            return {
                "kind": "pronoun",
                "pronoun": classification.pronoun,
                "root": None,
                "pattern": None,
                "features": extract_features(text, dummy, None, WordKind.PRONOUN, mabni_result=mabni_result),
            }

        root_extractor = RootExtractor()
        extraction = root_extractor.extract_with_affixes(text)
        root = extraction.root

        if not root:
            return {
                "kind": "unknown",
                "root": None,
                "pattern": None,
                "error": "Could not extract root from input text",
                "features": extract_features(text, extraction, None, WordKind.UNKNOWN, mabni_result=mabni_result),
            }

        # ------------------------------------------------------------------
        # Patch 2: protect roots from plural (…اء) hamza like: أَشِدَّاءُ
        # If stripped stem ends with "اء" and the extracted last radical is hamza (ء),
        # treat that hamza as a plural marker and restore the last radical.
        # ------------------------------------------------------------------
        def _is_plural_aa_form(stem: str) -> bool:
            s = (stem or "").strip()
            return s.endswith("اء") or s.endswith("آء")

        letters = list(root.letters)
        root_type = root.root_type
        aa_root_patch_applied = False

        kind_hint = classifier.classify(
            text,
            pattern_type=None,
            prefix=extraction.prefix or None,
            suffix=extraction.suffix or None,
        ).kind

        if (
            kind_hint == WordKind.NOUN
            and _is_plural_aa_form(extraction.stripped_word or "")
            and len(letters) == 3
            and letters[-1] == "ء"
        ):
            # Example: ش-د-ء should become ش-د-د for أَشِدَّاءُ
            letters[-1] = letters[1]
            aa_root_patch_applied = True

        if len(letters) == 4 and letters[1] == letters[2]:
            letters = [letters[0], letters[1], letters[3]]
            root_type = RootType.TRILATERAL

        analysis_root = Root(letters=tuple(letters), root_type=root_type)

        # ------------------------------------------------------------------
        # Heuristic pattern overrides (BEFORE PatternMatcher fallback).
        # هدفها إصلاح حالات قرآنية شائعة حيث الـCV fallback قد يختار وزنًا خاطئًا.
        # ------------------------------------------------------------------
        SHADDA = "\u0651"
        TANWIN_FATHA = "\u064b"
        prefix_parts = [p for p in (extraction.prefix or "").split("+") if p]
        suffix_parts = [s for s in (extraction.suffix or "").split("+") if s]

        kind_guess = classifier.classify(
            text,
            pattern_type=None,
            prefix=extraction.prefix or None,
            suffix=extraction.suffix or None,
        ).kind
        # Keep existing high-signal POS heuristics on the guess, so overrides can depend on them.
        if "است" in prefix_parts and len(extraction.stripped_word or "") <= 3:
            kind_guess = WordKind.VERB
        if (extraction.stripped_word or "") == "ازر" and (extraction.suffix or "") == "ه":
            kind_guess = WordKind.VERB

        pattern: Optional[Pattern] = None
        # If we applied the (…اء) root patch, force a broken-plural template marker.
        if aa_root_patch_applied and kind_guess == WordKind.NOUN:
            pattern = Pattern(
                name=PatternType.BROKEN_PLURAL_FU3ALAA.value,
                template="فُعَلَاءُ",
                pattern_type=PatternType.BROKEN_PLURAL_FU3ALAA,
                stem=text,
                features={
                    "pattern_type": PatternType.BROKEN_PLURAL_FU3ALAA.name,
                    "category": "noun",
                    "confidence": "0.80",
                    "rule": "plural_aa_hamza_root_patch->fu3alaa",
                },
            )
        # Special-case: تَرَاهُمْ is a defective verb from رأى (root ر-أ-ي).
        # CV fallback may pick a nominal template; override to reduce UNKNOWN.
        if (
            not pattern
            and kind_guess == WordKind.VERB
            and (extraction.stripped_word or "") == "ترا"
            and tuple(letters) in {("ر", "أ", "ي"), ("ر", "ا", "ي")}
        ):
            pattern = Pattern(
                name=PatternType.FORM_I.value,
                template="تَفْعَلُ",
                pattern_type=PatternType.FORM_I,
                stem=text,
                features={
                    "pattern_type": PatternType.FORM_I.name,
                    "category": "verb",
                    "confidence": "0.82",
                    "rule": "taraahum_raaa_defective->form_i",
                },
            )
        # (1) noun + shadda + fathatan غالبًا جمع تكسير على فُعَّل: رُكَّعًا/سُجَّدًا
        if not pattern and kind_guess == WordKind.NOUN and (SHADDA in text) and (TANWIN_FATHA in text):
            pattern = Pattern(
                name=PatternType.BROKEN_PLURAL_FU33AL.value,
                template="فُعَّل",
                pattern_type=PatternType.BROKEN_PLURAL_FU33AL,
                stem=text,
                features={
                    "pattern_type": PatternType.BROKEN_PLURAL_FU33AL.name,
                    "category": "noun",
                    "confidence": "0.88",
                    "rule": "noun_shadda_tanwin_fatha->fu33al",
                },
            )
        # (2) يَبْتَغُونَ (after segmentation: ي + بتغ + ون) => Form VIII (افتعل)
        elif not pattern and (
            kind_guess == WordKind.VERB
            and ("ي" in prefix_parts)
            and ("ون" in suffix_parts)
            and (extraction.stripped_word or "") == "بتغ"
        ):
            pattern = Pattern(
                name=PatternType.FORM_VIII.value,
                template="يَفْتَعِلُونَ",
                pattern_type=PatternType.FORM_VIII,
                stem=text,
                features={
                    "pattern_type": PatternType.FORM_VIII.name,
                    "category": "verb",
                    "confidence": "0.86",
                    "rule": "y_prefix+on_suffix+btg->form_viii",
                },
            )
        # (3) فَآزَرَهُ behaves like Form III (فَاعَلَ) – keep type consistent
        elif not pattern and kind_guess == WordKind.VERB and (extraction.stripped_word or "") == "ازر":
            pattern = Pattern(
                name=PatternType.FORM_III.value,
                template="فَاعَلَ",
                pattern_type=PatternType.FORM_III,
                stem=text,
                features={
                    "pattern_type": PatternType.FORM_III.name,
                    "category": "verb",
                    "confidence": "0.84",
                    "rule": "azr->form_iii",
                },
            )

        if not pattern:
            analyzer = PatternAnalyzer()
            analysis = analyzer.analyze(text, analysis_root)
            pattern = analysis.pattern if analysis else None

        # Classify (verb vs noun) using pattern_type when available.
        final_kind = classifier.classify(
            text,
            pattern_type=pattern.pattern_type if pattern else None,
            prefix=extraction.prefix or None,
            suffix=extraction.suffix or None,
        ).kind

        # Heuristic: Form X (استفعل) is overwhelmingly a verb when the remaining core
        # is triliteral (3 letters). This fixes cases like: فاستغلظ / فاستوى.
        if (extraction.prefix or "").split("+") and "است" in (extraction.prefix or "").split("+"):
            if len(extraction.stripped_word or "") <= 3:
                final_kind = WordKind.VERB

        # Quran-focused heuristic: فَ + آزر + هُ (Form III with hamza) behaves like a verb.
        if (extraction.stripped_word or "") == "ازر" and (extraction.suffix or "") == "ه":
            final_kind = WordKind.VERB

        result: Dict[str, Any] = {
            "kind": final_kind.value,
            "root": {
                "letters": letters,
                "formatted": "-".join(letters),
                "type": root_type.name.lower(),
                "length": len(letters),
            }
        }

        if pattern:
            pat_features = pattern.features.copy()
            pat_features.setdefault("pattern_type", pattern.pattern_type.name)
            if final_kind in {WordKind.VERB, WordKind.NOUN}:
                pat_features["category"] = final_kind.value
            result["pattern"] = {
                "template": pattern.template,
                "type": pattern.pattern_type.value,
                "category": final_kind.value if final_kind in {WordKind.VERB, WordKind.NOUN} else self._get_pattern_category(pattern.pattern_type),
                "stem": pattern.stem,
                "features": pat_features,
            }
        else:
            cat = "unknown"
            if final_kind in {WordKind.VERB, WordKind.NOUN}:
                cat = final_kind.value
            result["pattern"] = {
                "template": None,
                "type": "unknown",
                "category": cat,
                "error": "Could not match pattern"
            }

        features = extract_features(text, extraction, pattern, final_kind, mabni_result=mabni_result)
        result["affixes"] = {
            "prefix": extraction.prefix or None,
            "suffix": extraction.suffix or None,
        }
        result["features"] = features

        return result

    def _analyze_morphology_multi_word(self, text: str) -> Dict[str, Any]:
        """تحليل نص متعدد الكلمات - يستخرج الجذر لكل كلمة."""
        from fvafk.c2b.word_boundary import WordBoundaryDetector
        from fvafk.c2b.features import extract_features
        from fvafk.c2b.mabni_rules import classify_mabni
        from fvafk.c2b.root_extractor import RootExtractionResult
        from fvafk.c2b.pattern_analyzer import PatternAnalyzer
        from fvafk.c2b.word_classifier import WordClassifier, WordKind
        
        # Plan A: تقسيم النص إلى كلمات مع spans (وتصفية الرموز غير الحرفية)
        spans = WordBoundaryDetector().detect(text)
        
        root_extractor = RootExtractor()
        analyzer = PatternAnalyzer()
        classifier = WordClassifier()
        
        words_analysis: List[Dict[str, Any]] = []
        prev_governs_genitive = False
        genitive_governors = {"من", "في", "على", "إلى", "عن", "ب", "ل", "ك", "مع", "حتى"}
        
        for sp in spans:
            word = sp.token
            if not word or len(word) < 2:
                continue

            mabni_result = classify_mabni(word)
            if mabni_result.is_mabni:
                bare = "".join(c for c in word if not (ord(c) in range(0x064B, 0x0653) or c == "\u0670"))
                dummy = RootExtractionResult(
                    root=None,
                    normalized_word=bare or word,
                    stripped_word=bare or word,
                    prefix="",
                    suffix="",
                )
                words_analysis.append({
                    "word": word,
                    "span": {"start": sp.start, "end": sp.end},
                    "kind": "mabni",
                    "mabni": mabni_result.to_dict(),
                    "root": None,
                    "pattern": None,
                    "features": extract_features(word, dummy, None, WordKind.PARTICLE, mabni_result=mabni_result),
                })
                continue

            classification = classifier.classify(word)
            # Simple context: after a preposition/operator that governs genitive,
            # force the next content word to be treated as noun (not verb).
            force_noun_genitive = prev_governs_genitive
            prev_governs_genitive = False
            if classification.kind == WordKind.OPERATOR and classification.operator:
                op_base = (classification.operator.get("operator") or "").strip()
                if op_base in genitive_governors:
                    prev_governs_genitive = True
                words_analysis.append(
                    {
                        "word": word,
                        "span": {"start": sp.start, "end": sp.end},
                        "kind": "operator",
                        "operator": classification.operator,
                        "root": None,
                        "pattern": None,
                    }
                )
                continue
            if classification.kind in {WordKind.DEMONSTRATIVE, WordKind.NAME, WordKind.PARTICLE}:
                if classification.kind == WordKind.PARTICLE:
                    base = ((classification.special or {}).get("base") or "").strip()
                    if base in genitive_governors:
                        prev_governs_genitive = True
                bare = (classification.special or {}).get("token_bare") if classification.special else None
                bare = bare or word
                dummy_suffix = None
                if classification.kind == WordKind.PARTICLE:
                    dummy_suffix = ((classification.special or {}).get("attached_pronoun") or {}).get("suffix")
                dummy = RootExtractionResult(
                    root=None,
                    normalized_word=bare,
                    stripped_word=bare,
                    prefix="",
                    suffix=dummy_suffix or "",
                )
                payload_key = "special"
                kind_value = classification.kind.value
                if classification.kind == WordKind.NAME:
                    payload_key = "name"
                elif classification.kind == WordKind.DEMONSTRATIVE:
                    payload_key = "demonstrative"
                elif classification.kind == WordKind.PARTICLE:
                    payload_key = "particle"
                words_analysis.append(
                    {
                        "word": word,
                        "span": {"start": sp.start, "end": sp.end},
                        "kind": kind_value,
                        payload_key: classification.special,
                        "root": None,
                        "pattern": None,
                        "features": extract_features(word, dummy, None, classification.kind, mabni_result=mabni_result),
                    }
                )
                continue

            if classification.kind == WordKind.PRONOUN:
                bare = (classification.pronoun or {}).get("bare") if classification.pronoun else None
                bare = bare or word
                dummy = RootExtractionResult(
                    root=None,
                    normalized_word=bare,
                    stripped_word=bare,
                    prefix="",
                    suffix="",
                )
                words_analysis.append(
                    {
                        "word": word,
                        "span": {"start": sp.start, "end": sp.end},
                        "kind": "pronoun",
                        "pronoun": classification.pronoun,
                        "root": None,
                        "pattern": None,
                        "features": extract_features(word, dummy, None, WordKind.PRONOUN, mabni_result=mabni_result),
                    }
                )
                continue
                
            extraction = root_extractor.extract_with_affixes(word)
            root = extraction.root
            
            if not root:
                words_analysis.append({
                    "word": word,
                    "span": {"start": sp.start, "end": sp.end},
                    "kind": "unknown",
                    "root": None,
                    "pattern": None,
                    "error": "Could not extract root",
                    "features": extract_features(word, extraction, None, WordKind.UNKNOWN, mabni_result=mabni_result),
                })
                continue
            
            letters = list(root.letters)
            root_type = root.root_type

            def _is_plural_aa_form(stem: str) -> bool:
                s = (stem or "").strip()
                return s.endswith("اء") or s.endswith("آء")

            aa_root_patch_applied = False
            kind_hint = classifier.classify(
                word,
                pattern_type=None,
                prefix=extraction.prefix or None,
                suffix=extraction.suffix or None,
            ).kind
            if (
                kind_hint == WordKind.NOUN
                and _is_plural_aa_form(extraction.stripped_word or "")
                and len(letters) == 3
                and letters[-1] == "ء"
            ):
                letters[-1] = letters[1]
                aa_root_patch_applied = True
            
            # معالجة الجذور الرباعية المضعفة
            if len(letters) == 4 and letters[1] == letters[2]:
                letters = [letters[0], letters[1], letters[3]]
                root_type = RootType.TRILATERAL
            
            analysis_root = Root(letters=tuple(letters), root_type=root_type)
            # ------------------------------------------------------------------
            # Heuristic pattern overrides (BEFORE PatternMatcher fallback).
            # ------------------------------------------------------------------
            SHADDA = "\u0651"
            TANWIN_FATHA = "\u064b"
            prefix_parts = [p for p in (extraction.prefix or "").split("+") if p]
            suffix_parts = [s for s in (extraction.suffix or "").split("+") if s]

            kind_guess = classifier.classify(
                word,
                pattern_type=None,
                prefix=extraction.prefix or None,
                suffix=extraction.suffix or None,
            ).kind
            if "است" in prefix_parts and len(extraction.stripped_word or "") <= 3:
                kind_guess = WordKind.VERB
            if (extraction.stripped_word or "") == "ازر" and (extraction.suffix or "") == "ه":
                kind_guess = WordKind.VERB

            pattern: Optional[Pattern] = None
            if aa_root_patch_applied and kind_guess == WordKind.NOUN:
                pattern = Pattern(
                    name=PatternType.BROKEN_PLURAL_FU3ALAA.value,
                    template="فُعَلَاءُ",
                    pattern_type=PatternType.BROKEN_PLURAL_FU3ALAA,
                    stem=word,
                    features={
                        "pattern_type": PatternType.BROKEN_PLURAL_FU3ALAA.name,
                        "category": "noun",
                        "confidence": "0.80",
                        "rule": "plural_aa_hamza_root_patch->fu3alaa",
                    },
                )
            if (
                not pattern
                and kind_guess == WordKind.VERB
                and (extraction.stripped_word or "") == "ترا"
                and tuple(letters) in {("ر", "أ", "ي"), ("ر", "ا", "ي")}
            ):
                pattern = Pattern(
                    name=PatternType.FORM_I.value,
                    template="تَفْعَلُ",
                    pattern_type=PatternType.FORM_I,
                    stem=word,
                    features={
                        "pattern_type": PatternType.FORM_I.name,
                        "category": "verb",
                        "confidence": "0.82",
                        "rule": "taraahum_raaa_defective->form_i",
                    },
                )
            if kind_guess == WordKind.NOUN and (SHADDA in word) and (TANWIN_FATHA in word):
                if not pattern:
                    pattern = Pattern(
                    name=PatternType.BROKEN_PLURAL_FU33AL.value,
                    template="فُعَّل",
                    pattern_type=PatternType.BROKEN_PLURAL_FU33AL,
                    stem=word,
                    features={
                        "pattern_type": PatternType.BROKEN_PLURAL_FU33AL.name,
                        "category": "noun",
                        "confidence": "0.88",
                        "rule": "noun_shadda_tanwin_fatha->fu33al",
                    },
                    )
            elif (
                kind_guess == WordKind.VERB
                and ("ي" in prefix_parts)
                and ("ون" in suffix_parts)
                and (extraction.stripped_word or "") == "بتغ"
            ):
                if not pattern:
                    pattern = Pattern(
                    name=PatternType.FORM_VIII.value,
                    template="يَفْتَعِلُونَ",
                    pattern_type=PatternType.FORM_VIII,
                    stem=word,
                    features={
                        "pattern_type": PatternType.FORM_VIII.name,
                        "category": "verb",
                        "confidence": "0.86",
                        "rule": "y_prefix+on_suffix+btg->form_viii",
                    },
                    )
            elif kind_guess == WordKind.VERB and (extraction.stripped_word or "") == "ازر":
                if not pattern:
                    pattern = Pattern(
                    name=PatternType.FORM_III.value,
                    template="فَاعَلَ",
                    pattern_type=PatternType.FORM_III,
                    stem=word,
                    features={
                        "pattern_type": PatternType.FORM_III.name,
                        "category": "verb",
                        "confidence": "0.84",
                        "rule": "azr->form_iii",
                    },
                    )

            # If context forces noun (e.g., after a genitive governor), suppress verb-like
            # pattern matching to avoid confusing outputs such as: kind=noun but pattern=verb.
            if not pattern and not force_noun_genitive:
                analysis = analyzer.analyze(word, analysis_root)
                pattern = analysis.pattern if analysis else None

            final_kind = classifier.classify(
                word,
                pattern_type=pattern.pattern_type if pattern else None,
                prefix=extraction.prefix or None,
                suffix=extraction.suffix or None,
            ).kind

            if (extraction.prefix or "").split("+") and "است" in (extraction.prefix or "").split("+"):
                if len(extraction.stripped_word or "") <= 3:
                    final_kind = WordKind.VERB

            if (extraction.stripped_word or "") == "ازر" and (extraction.suffix or "") == "ه":
                final_kind = WordKind.VERB

            if force_noun_genitive and final_kind == WordKind.VERB:
                final_kind = WordKind.NOUN

            if force_noun_genitive and final_kind == WordKind.VERB:
                final_kind = WordKind.NOUN
            
            word_result: Dict[str, Any] = {
                "word": word,
                "span": {"start": sp.start, "end": sp.end},
                "kind": final_kind.value,
                "root": {
                    "letters": letters,
                    "formatted": "-".join(letters),
                    "type": root_type.name.lower(),
                    "length": len(letters),
                }
            }
            word_result["affixes"] = {
                "prefix": extraction.prefix or None,
                "suffix": extraction.suffix or None,
                "normalized": extraction.normalized_word,
                "stripped": extraction.stripped_word,
            }

            features = extract_features(word, extraction, pattern, final_kind, mabni_result=mabni_result)
            if force_noun_genitive:
                # best-effort: mark likely genitive after preposition
                features["case"] = features.get("case") or "genitive"
            if pattern:
                pat_features = pattern.features.copy()
                pat_features.setdefault("pattern_type", pattern.pattern_type.name)
                if final_kind in {WordKind.VERB, WordKind.NOUN}:
                    pat_features["category"] = final_kind.value
                word_result["pattern"] = {
                    "template": pattern.template,
                    "type": pattern.pattern_type.value,
                    "category": final_kind.value if final_kind in {WordKind.VERB, WordKind.NOUN} else self._get_pattern_category(pattern.pattern_type),
                    "features": pat_features,
                }
            else:
                cat = "unknown"
                if final_kind in {WordKind.VERB, WordKind.NOUN}:
                    cat = final_kind.value
                word_result["pattern"] = {
                    "template": None,
                    "type": "unknown",
                    "category": cat,
                }
            word_result["features"] = features
            
            words_analysis.append(word_result)
        
        return {
            "words_count": len(words_analysis),
            "words": words_analysis
        }

    def _get_pattern_category(self, pattern_type: PatternType) -> str:
        verb_forms = {
            PatternType.FORM_I,
            PatternType.FORM_II,
            PatternType.FORM_III,
            PatternType.FORM_IV,
            PatternType.FORM_V,
            PatternType.FORM_VI,
            PatternType.FORM_VII,
            PatternType.FORM_VIII,
            PatternType.FORM_IX,
            PatternType.FORM_X,
        }

        if pattern_type in verb_forms:
            return "verb"

        if "PLURAL" in pattern_type.value.upper():
            return "plural"

        return "noun"

    def _count_syllables(self, segments: List[Segment]) -> int:
        from fvafk.c2a.syllable import SegmentKind

        count = 0
        for seg in segments:
            if seg.kind == SegmentKind.VOWEL:
                count += 1
        return count

    def _unit_to_dict(self, unit: Unit) -> Dict[str, Any]:
        return {
            "text": unit.text,
            "category": unit.category.name if unit.category else None,
        }

    def _gate_result_to_dict(self, gate: PhonologicalGate, gate_result: GateResult) -> Dict[str, Any]:
        return {
            "gate_id": gate.gate_id,
            "status": gate_result.status.name,
            "time_ms": gate_result.latency_ms,
            "deltas": len(gate_result.deltas),
            "reason": gate_result.reason,
        }


def _print_human_readable(result: Dict[str, Any]) -> None:
    print(f"\n{'='*70}")
    print(f"  FVAFK Analysis: {result['input']}")
    print(f"{'='*70}\n")

    print(f"📝 Phase C1 (Encoding):")
    print(f"   Units: {result['c1']['num_units']}")
    print(f"   Time:  {result['stats']['c1_time_ms']:.3f}ms\n")

    print(f"🔊 Phase C2a (Phonology):")
    print(f"   Syllables: {result['c2a']['syllables']['count']}")
    print(f"   Gates:     {result['stats']['gates_count']}")

    modified_gates = [
        g for g in result['c2a']['gates']
        if g['status'] == 'REPAIR' and g['deltas'] > 0
    ]

    if modified_gates:
        print(f"   Modified by:")
        for gate in modified_gates:
            print(f"      • {gate['gate_id']}: {gate['deltas']} change(s)")

    print(f"   Time:  {result['stats']['c2a_time_ms']:.3f}ms\n")

    if 'c2b' in result:
        print(f"📖 Phase C2b (Morphology):")
        morph = result['c2b']

        if morph.get('root'):
            root = morph['root']
            print(f"   Root:    {root['formatted']} ({root['type']}, {root['length']} letters)")
        else:
            print(f"   Root:    Could not extract")

        if morph.get('pattern') and morph['pattern'].get('template'):
            pat = morph['pattern']
            print(f"   Pattern: {pat['template']}")
            print(f"   Type:    {pat['type']} ({pat['category']})")
        else:
            print(f"   Pattern: Could not match")

        if result['stats']['c2b_time_ms']:
            print(f"   Time:    {result['stats']['c2b_time_ms']:.3f}ms\n")

    print(f"⏱️  Performance Summary:")
    print(f"   Total:  {result['stats']['total_time_ms']:.3f}ms")

    breakdown = [
        f"C1: {result['stats']['c1_time_ms']:.1f}ms",
        f"C2a: {result['stats']['c2a_time_ms']:.1f}ms",
    ]
    if result['stats'].get('c2b_time_ms'):
        breakdown.append(f"C2b: {result['stats']['c2b_time_ms']:.1f}ms")

    print(f"   Breakdown: {' + '.join(breakdown)}")
    print(f"\n{'='*70}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="FVAFK: Arabic phonological and morphological analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m fvafk.cli "كِتَابٌ" --json
  python -m fvafk.cli "كَاتِبٌ" --morphology --json
  python -m fvafk.cli "text" --verbose --json
  python -m fvafk.cli "مُحَمَّدٌ رَسُولُ اللَّهِ" --morphology --multi-word --json
        """
    )

    parser.add_argument("text", help="Arabic text to analyze")
    parser.add_argument("--verbose", action="store_true", help="Include detailed unit and segment information")
    parser.add_argument("--json", action="store_true", help="Output results as JSON (default: human-readable)")
    parser.add_argument("--morphology", action="store_true", help="Include morphological analysis (root extraction + pattern matching)")
    parser.add_argument("--multi-word", action="store_true", help="Analyze each word separately in multi-word text (requires --morphology)")
    parser.add_argument("--phonology-v2", action="store_true", help="Use Phonology V2 engine for CV analysis (Assumption A)")
    parser.add_argument("--phonology-v2-details", action="store_true", help="Include Phonology V2 syllabification details in output JSON")
    parser.add_argument("--phonology-v2-witnesses", action="store_true", help="Include Phonology V2 witnesses (large output; requires --phonology-v2-details)")

    args = parser.parse_args()

    # Guard against unreasonably large inputs (protects against accidental
    # large-file pastes and potential DoS; 10 000 characters ≈ ~4 pages of text)
    _MAX_INPUT_CHARS = 10_000
    if len(args.text) > _MAX_INPUT_CHARS:
        error_msg = (
            f"Input too long: {len(args.text)} characters "
            f"(maximum {_MAX_INPUT_CHARS}). Truncate your text and try again."
        )
        if args.json:
            print(json.dumps({"success": False, "error": error_msg}, ensure_ascii=False))
        else:
            print(f"Error: {error_msg}", file=sys.stderr)
        sys.exit(1)

    try:
        cli = MinimalCLI()
        result = cli.run(
            text=args.text,
            verbose=args.verbose,
            morphology=args.morphology,
            multi_word=getattr(args, 'multi_word', False),
            phonology_v2=getattr(args, "phonology_v2", False),
            phonology_v2_details=getattr(args, "phonology_v2_details", False),
            phonology_v2_witnesses=getattr(args, "phonology_v2_witnesses", False),
        )

        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            _print_human_readable(result)

        sys.exit(0)

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "input": args.text
        }

        if args.json:
            print(json.dumps(error_result, ensure_ascii=False, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)

        sys.exit(1)


if __name__ == "__main__":
    main()
