"""
Tests for Node Schema and Energy Evaluation
"""

import pytest
import math
from fvafk.node_schema import (
    Node, NodeType, Case, Mood, JoinPolicy, RelationType,
    create_preposition, create_noun, create_attached_pronoun
)
from fvafk.energy_evaluation import (
    EnergyEvaluator, Candidate, CandidateStatus
)


class TestNodeSchema:
    """Test Node schema"""
    
    def test_create_preposition(self):
        """Test preposition creation"""
        prep = create_preposition("prep1", "في", Case.GEN)
        
        assert prep.type == NodeType.FUNC
        assert prep.surface == "في"
        assert prep.sig.reqR == "Noun"
        assert prep.can_govern_case()
    
    def test_create_noun(self):
        """Test noun creation"""
        noun = create_noun("noun1", "بيت", Case.GEN)
        
        assert noun.type == NodeType.NOUN
        assert noun.surface == "بيت"
        assert noun.case_mood.case == Case.GEN
        assert noun.is_inflected()
        assert not noun.is_built_in()
    
    def test_create_attached_pronoun(self):
        """Test attached pronoun creation"""
        pron = create_attached_pronoun("pron1", "ه")
        
        assert pron.type == NodeType.MABNI
        assert pron.surface == "ه"
        assert pron.requires_attachment()
        assert pron.is_built_in()
        assert not pron.is_inflected()
    
    def test_noun_inflection_status(self):
        """Test that inflected nouns have correct status"""
        noun_inflected = create_noun("n1", "بيت", Case.GEN, locked=False)
        noun_built_in = create_noun("n2", "حيث", Case.NONE, locked=True)
        
        assert noun_inflected.is_inflected()
        assert not noun_built_in.is_inflected()
        assert noun_built_in.is_built_in()


class TestEnergyEvaluation:
    """Test energy evaluation system"""
    
    @pytest.fixture
    def evaluator(self):
        """Create evaluator"""
        return EnergyEvaluator()
    
    def test_correct_preposition_phrase(self, evaluator):
        """Test that correct prepositional phrase has finite energy"""
        # في بيتِهِ (correct)
        prep = create_preposition("prep1", "في", Case.GEN, slot=0)
        noun = create_noun("noun1", "بيتِ", Case.GEN, slot=1)
        pron = create_attached_pronoun("pron1", "ـهِ", slot=2, head_slot=1)
        pron.join.value = 1  # Attached
        
        candidate = Candidate([prep, noun, pron], "correct")
        energies, status = evaluator.evaluate_candidate(candidate)
        
        assert status == CandidateStatus.VALID
        assert energies.is_finite()
        assert energies.E_attach == 0.0
        assert energies.E_case == 0.0
        assert energies.E_join == 0.0
    
    def test_case_mismatch(self, evaluator):
        """Test that case mismatch gives infinite energy"""
        # في بيتُهِ (wrong case - nominative instead of genitive)
        prep = create_preposition("prep1", "في", Case.GEN, slot=0)
        noun = create_noun("noun1", "بيتُ", Case.NOM, slot=1)  # WRONG
        pron = create_attached_pronoun("pron1", "ـهِ", slot=2, head_slot=1)
        pron.join.value = 1
        
        candidate = Candidate([prep, noun, pron], "case_error")
        energies, status = evaluator.evaluate_candidate(candidate)
        
        assert status == CandidateStatus.INVALID
        assert not energies.is_finite()
        assert math.isinf(energies.E_case)
    
    def test_join_violation(self, evaluator):
        """Test that join violation gives infinite energy"""
        # في بيتِ هو (clitic not attached)
        prep = create_preposition("prep1", "في", Case.GEN, slot=0)
        noun = create_noun("noun1", "بيتِ", Case.GEN, slot=1)
        pron = create_attached_pronoun("pron1", "هو", slot=2, head_slot=1)
        pron.join.value = 0  # WRONG: not attached
        
        candidate = Candidate([prep, noun, pron], "join_error")
        energies, status = evaluator.evaluate_candidate(candidate)
        
        assert status == CandidateStatus.INVALID
        assert not energies.is_finite()
        assert math.isinf(energies.E_join)
    
    def test_attachment_requirement(self, evaluator):
        """Test attachment requirement violation"""
        # Preposition without noun to its right
        prep = create_preposition("prep1", "في", Case.GEN, slot=0)
        
        candidate = Candidate([prep], "missing_noun")
        energies, status = evaluator.evaluate_candidate(candidate)
        
        assert status == CandidateStatus.INVALID
        assert math.isinf(energies.E_attach)
    
    def test_multiple_violations(self, evaluator):
        """Test candidate with multiple violations"""
        # Wrong case + clitic not attached
        prep = create_preposition("prep1", "في", Case.GEN, slot=0)
        noun = create_noun("noun1", "بيتُ", Case.NOM, slot=1)  # WRONG case
        pron = create_attached_pronoun("pron1", "هو", slot=2, head_slot=1)
        pron.join.value = 0  # WRONG: not attached
        
        candidate = Candidate([prep, noun, pron], "multiple_errors")
        energies, status = evaluator.evaluate_candidate(candidate)
        
        assert status == CandidateStatus.INVALID
        assert not energies.is_finite()
        # At least one should be infinite
        assert math.isinf(energies.E_case) or math.isinf(energies.E_join)


class TestInfinityGates:
    """Test infinity gate behavior"""
    
    def test_infinity_filters_invalid_candidates(self):
        """Test that infinity gates filter out invalid candidates"""
        evaluator = EnergyEvaluator()
        
        # Create correct and incorrect candidates
        candidates = []
        
        # Correct
        prep = create_preposition("prep1", "في", Case.GEN, slot=0)
        noun = create_noun("noun1", "بيتِ", Case.GEN, slot=1)
        pron = create_attached_pronoun("pron1", "ـهِ", slot=2, head_slot=1)
        pron.join.value = 1
        candidates.append(Candidate([prep, noun, pron], "correct"))
        
        # Wrong case
        prep2 = create_preposition("prep2", "في", Case.GEN, slot=0)
        noun2 = create_noun("noun2", "بيتُ", Case.NOM, slot=1)
        pron2 = create_attached_pronoun("pron2", "ـهِ", slot=2, head_slot=1)
        pron2.join.value = 1
        candidates.append(Candidate([prep2, noun2, pron2], "wrong_case"))
        
        # Evaluate all
        results = [evaluator.evaluate_candidate(c) for c in candidates]
        
        # Only first should be valid
        valid_count = sum(1 for _, status in results if status == CandidateStatus.VALID)
        assert valid_count == 1
        
        # First should be valid
        assert results[0][1] == CandidateStatus.VALID
        
        # Others should be invalid
        for _, status in results[1:]:
            assert status == CandidateStatus.INVALID


class TestNodeFeatures:
    """Test node feature queries"""
    
    def test_inflected_vs_built_in(self):
        """Test distinction between inflected and built-in"""
        # Inflected noun
        noun = create_noun("n1", "بيت", Case.GEN, locked=False)
        assert noun.is_inflected()
        assert not noun.is_built_in()
        
        # Built-in pronoun
        pron = create_attached_pronoun("p1", "ه")
        assert pron.is_built_in()
        assert not pron.is_inflected()
    
    def test_attachment_requirements(self):
        """Test attachment requirement queries"""
        # Clitic must attach
        pron = create_attached_pronoun("p1", "ه")
        assert pron.requires_attachment()
        assert pron.join.policy == JoinPolicy.MUST
        
        # Regular noun is free
        noun = create_noun("n1", "بيت", Case.GEN)
        assert not noun.requires_attachment()
        assert noun.join.policy == JoinPolicy.FREE
    
    def test_case_governance(self):
        """Test case governance queries"""
        # Preposition can govern case
        prep = create_preposition("p1", "في", Case.GEN)
        assert prep.can_govern_case()
        
        # Regular noun cannot
        noun = create_noun("n1", "بيت", Case.GEN)
        assert not noun.can_govern_case()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
