"""
Tests for Pydantic models (Sprint 1, Task 1.3)

Tests all 7 Pydantic models for type safety, validation, and serialization.
"""

import pytest
from app.models import (
    Unit, Syllable, WordForm, Link, Evidence,
    ProofArtifact, AnalysisResult,
    PartOfSpeech, Case, Number, Gender, Span,
    LinkType, ProofStatus,
    C1Result, C2aResult, Stats
)


class TestUnit:
    def test_unit_creation(self):
        unit = Unit(text="ك", category="LETTER", index=0)
        assert unit.text == "ك"
        assert unit.category == "LETTER"
        assert unit.index == 0
    
    def test_unit_with_metadata(self):
        unit = Unit(text="َ", category="DIACRITIC", index=1, metadata={"type": "fatha"})
        assert unit.metadata["type"] == "fatha"
    
    def test_unit_json_serialization(self):
        unit = Unit(text="ك", category="LETTER", index=0)
        json_data = unit.model_dump_json()
        assert "ك" in json_data


class TestSyllable:
    def test_syllable_creation(self):
        syll = Syllable(pattern="CVC", units=[0, 1, 2], start=0, end=3)
        assert syll.pattern == "CVC"
        assert len(syll.units) == 3
    
    def test_syllable_with_weight(self):
        syll = Syllable(pattern="CVV", units=[0, 1], start=0, end=2, weight="superheavy")
        assert syll.weight == "superheavy"


class TestWordForm:
    def test_word_form_creation(self):
        wf = WordForm(
            word_id=0,
            surface="كِتَابٌ",
            bare="كتاب",
            pos=PartOfSpeech.NOUN,
            span=Span(start=0, end=6)
        )
        assert wf.word_id == 0
        assert wf.surface == "كِتَابٌ"
        assert wf.pos == PartOfSpeech.NOUN
    
    def test_word_form_with_case(self):
        wf = WordForm(
            word_id=0,
            surface="الْكِتَابُ",
            bare="الكتاب",
            pos=PartOfSpeech.NOUN,
            span=Span(start=0, end=10),
            case=Case.NOMINATIVE,
            number=Number.SINGULAR,
            gender=Gender.MASCULINE,
            definiteness=True
        )
        assert wf.case == Case.NOMINATIVE
        assert wf.number == Number.SINGULAR
        assert wf.definiteness is True


class TestLink:
    def test_link_creation(self):
        link = Link(
            link_type=LinkType.ISNADI,
            head_id=0,
            dependent_id=1,
            confidence=1.0
        )
        assert link.link_type == LinkType.ISNADI
        assert link.confidence == 1.0
    
    def test_link_with_reason(self):
        link = Link(
            link_type=LinkType.ISNADI,
            head_id=0,
            dependent_id=1,
            confidence=0.95,
            reason="Case agreement, number agreement"
        )
        assert "agreement" in link.reason


class TestEvidence:
    def test_evidence_creation(self):
        evidence = Evidence(
            score=0.85,
            scope_ok=True,
            truth_ok=True,
            reference_ok=True
        )
        assert evidence.score == 0.85
    
    def test_evidence_is_acceptable(self):
        evidence = Evidence(score=0.85, scope_ok=True, truth_ok=True, reference_ok=True)
        assert evidence.is_acceptable() is True
        
        evidence_low = Evidence(score=0.4, scope_ok=True, truth_ok=True, reference_ok=True)
        assert evidence_low.is_acceptable() is False


class TestProofArtifact:
    def test_proof_artifact_creation(self):
        proof = ProofArtifact(
            theorem_name="test_theorem",
            status=ProofStatus.PROVEN,
            coq_file="test.v"
        )
        assert proof.theorem_name == "test_theorem"
        assert proof.status == ProofStatus.PROVEN
    
    def test_proof_is_safe(self):
        proven = ProofArtifact(
            theorem_name="test",
            status=ProofStatus.PROVEN,
            coq_file="test.v"
        )
        assert proven.is_safe() is True
        
        admitted = ProofArtifact(
            theorem_name="test",
            status=ProofStatus.ADMITTED,
            coq_file="test.v"
        )
        assert admitted.is_safe() is False


class TestAnalysisResult:
    def test_analysis_result_creation(self):
        result = AnalysisResult(
            input="test",
            c1=C1Result(num_units=5),
            c2a=C2aResult(syllables=[], gates=[]),
            stats=Stats(
                c1_time_ms=1.0,
                c2a_time_ms=2.0,
                total_time_ms=3.0,
                gates_count=10
            )
        )
        assert result.input == "test"
        assert result.c1.num_units == 5
        assert result.stats.total_time_ms == 3.0
    
    def test_analysis_result_json_serialization(self):
        result = AnalysisResult(
            input="كِتَابٌ",
            c1=C1Result(num_units=5),
            c2a=C2aResult(syllables=[], gates=[]),
            stats=Stats(
                c1_time_ms=1.2,
                c2a_time_ms=10.5,
                total_time_ms=11.7,
                gates_count=11
            )
        )
        json_data = result.model_dump_json()
        assert "كِتَابٌ" in json_data
        assert "11.7" in json_data
