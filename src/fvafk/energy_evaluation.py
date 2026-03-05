"""
Energy-Based Candidate Evaluation

This module implements the energy function framework for evaluating
morphological and syntactic candidates. It uses "infinity gates" to
enforce hard constraints and energy functions for soft preferences.

Example: "في بيتِهِ" (fii bayti-hi, "in his house")
- Preposition + inflected noun + attached pronoun
"""

import math
from dataclasses import dataclass
from typing import List, Tuple, Dict
from enum import Enum

try:
    from .node_schema import (
        Node, Case, JoinPolicy, RelationType,
        create_preposition, create_noun, create_attached_pronoun
    )
except ImportError:
    from node_schema import (
        Node, Case, JoinPolicy, RelationType,
        create_preposition, create_noun, create_attached_pronoun
    )


class CandidateStatus(Enum):
    """Status of candidate evaluation"""
    VALID = "valid"
    INVALID = "invalid"


@dataclass
class EnergyComponents:
    """Components of total energy"""
    E_attach: float = 0.0    # Attachment violation energy
    E_case: float = 0.0      # Case mismatch energy
    E_join: float = 0.0      # Join policy violation energy
    E_dist: float = 0.0      # Distance/economy energy (for phonology)
    E_morph: float = 0.0     # Morphological constraint energy
    
    def total(self) -> float:
        """Compute total energy"""
        return self.E_attach + self.E_case + self.E_join + self.E_dist + self.E_morph
    
    def is_finite(self) -> bool:
        """Check if all energies are finite (no hard constraint violations)"""
        return all(
            not math.isinf(e) 
            for e in [self.E_attach, self.E_case, self.E_join, self.E_dist, self.E_morph]
        )


@dataclass
class Candidate:
    """A candidate structure (sequence of nodes)"""
    nodes: List[Node]
    description: str = ""
    
    def __str__(self):
        return self.description or " ".join(n.surface for n in self.nodes)


class EnergyEvaluator:
    """
    Evaluates energy of morphological/syntactic candidates
    """
    
    # Infinity for hard constraint violations
    INF = float('inf')
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize evaluator with optional energy weights
        
        Default weights are 1.0 for all components
        """
        self.weights = weights or {
            'attach': 1.0,
            'case': 1.0,
            'join': 1.0,
            'dist': 1.0,
            'morph': 1.0
        }
    
    def eval_attachment(self, nodes: List[Node]) -> float:
        """
        Evaluate attachment requirements (E_attach)
        
        Returns INF if:
        - A node with reqL/reqR is not satisfied
        - A preposition doesn't have a noun to its right
        - A clitic doesn't have its required host
        """
        energy = 0.0
        
        for i, node in enumerate(nodes):
            # Check right requirement
            if node.sig.reqR:
                if i + 1 >= len(nodes):
                    # No right neighbor
                    return self.INF
                
                right = nodes[i + 1]
                # Simple check: if reqR="Noun", next must be NOUN
                if node.sig.reqR == "Noun" and right.type.value != "noun":
                    return self.INF
            
            # Check left requirement  
            if node.sig.reqL:
                # Allow "head(any)" to be satisfied by being at sentence start
                if "head(any)" in node.sig.reqL:
                    # Prepositions can start a phrase
                    continue
                
                if i - 1 < 0:
                    # No left neighbor
                    return self.INF
                
                left = nodes[i - 1]
                # Simple check for "Noun" requirement
                if node.sig.reqL == "Noun" and left.type.value != "noun":
                    return self.INF
        
        return energy * self.weights['attach']
    
    def eval_case(self, nodes: List[Node]) -> float:
        """
        Evaluate case agreement (E_case)
        
        Returns INF if:
        - A preposition is followed by a noun not in genitive
        - A verb doesn't properly govern its object
        - Case requirements are not met
        """
        energy = 0.0
        
        for i, node in enumerate(nodes):
            # If node governs case (e.g., preposition)
            if node.can_govern_case():
                governed_case = node.case_mood.case
                
                # Check right neighbor (the governed word)
                if i + 1 < len(nodes):
                    right = nodes[i + 1]
                    
                    # If right is inflected and in wrong case
                    if right.is_inflected() and right.case_mood.case != governed_case:
                        return self.INF
        
        return energy * self.weights['case']
    
    def eval_join(self, nodes: List[Node]) -> float:
        """
        Evaluate join policy (E_join)
        
        Returns INF if:
        - A MUST-attach clitic is not attached (join.value = 0)
        - A FORBID-attach is attached (join.value = 1)
        """
        energy = 0.0
        
        for node in nodes:
            if node.join.policy == JoinPolicy.MUST and node.join.value == 0:
                # Must attach but not attached
                return self.INF
            
            if node.join.policy == JoinPolicy.FORBID and node.join.value == 1:
                # Must not attach but is attached
                return self.INF
        
        return energy * self.weights['join']
    
    def evaluate_candidate(self, candidate: Candidate) -> Tuple[EnergyComponents, CandidateStatus]:
        """
        Evaluate a complete candidate and return energy breakdown
        """
        energies = EnergyComponents()
        
        # Compute each component
        energies.E_attach = self.eval_attachment(candidate.nodes)
        energies.E_case = self.eval_case(candidate.nodes)
        energies.E_join = self.eval_join(candidate.nodes)
        # E_dist and E_morph can be added based on phonological context
        
        # Determine status
        status = CandidateStatus.VALID if energies.is_finite() else CandidateStatus.INVALID
        
        return energies, status


def create_example_fii_baytihi():
    """
    Create numerical example: "في بيتِهِ" (fii bayti-hi, "in his house")
    
    We create three candidates:
    1. CORRECT: في + بيتِ(GEN) + ـهِ(attached)
    2. WRONG1: في + بيتُ(NOM) + ـهِ(attached) - wrong case
    3. WRONG2: في + بيتِ(GEN) + هو(separate) - clitic not attached
    """
    
    # Candidate 1: CORRECT
    prep1 = create_preposition("prep1", "في", Case.GEN, slot=0)
    noun1 = create_noun("noun1", "بيتِ", Case.GEN, slot=1)
    pron1 = create_attached_pronoun("pron1", "ـهِ", slot=2, head_slot=1)
    pron1.join.value = 1  # Mark as attached
    
    candidate1 = Candidate(
        nodes=[prep1, noun1, pron1],
        description="CORRECT: في بيتِهِ (prep + noun.GEN + clitic.attached)"
    )
    
    # Candidate 2: WRONG - Case mismatch (nominative instead of genitive)
    prep2 = create_preposition("prep2", "في", Case.GEN, slot=0)
    noun2 = create_noun("noun2", "بيتُ", Case.NOM, slot=1)  # WRONG: NOM instead of GEN
    pron2 = create_attached_pronoun("pron2", "ـهِ", slot=2, head_slot=1)
    pron2.join.value = 1
    
    candidate2 = Candidate(
        nodes=[prep2, noun2, pron2],
        description="WRONG1: في بيتُهِ (prep + noun.NOM + clitic) - case error"
    )
    
    # Candidate 3: WRONG - Clitic not attached (separate pronoun)
    prep3 = create_preposition("prep3", "في", Case.GEN, slot=0)
    noun3 = create_noun("noun3", "بيتِ", Case.GEN, slot=1)
    pron3 = create_attached_pronoun("pron3", "هو", slot=2, head_slot=1)
    pron3.join.value = 0  # WRONG: not attached but must be
    pron3.surface = "هو"  # Separate pronoun form
    
    candidate3 = Candidate(
        nodes=[prep3, noun3, pron3],
        description="WRONG2: في بيتِ هو (prep + noun.GEN + pron.separate) - join error"
    )
    
    return [candidate1, candidate2, candidate3]


def demonstrate_numerical_example():
    """
    Demonstrate energy-based evaluation with numerical example
    """
    print("=" * 70)
    print("NUMERICAL EXAMPLE: في بيتِهِ (fii bayti-hi, 'in his house')")
    print("=" * 70)
    print("\nThis example shows how infinity gates filter incorrect candidates:")
    print("- Preposition 'في' governs GENITIVE case")
    print("- Pronoun 'ـهِ' is a clitic that MUST attach")
    print()
    
    # Create candidates
    candidates = create_example_fii_baytihi()
    
    # Evaluate each
    evaluator = EnergyEvaluator()
    
    for i, candidate in enumerate(candidates, 1):
        print(f"\n{'='*70}")
        print(f"Candidate {i}: {candidate.description}")
        print(f"{'='*70}")
        
        # Show structure
        print("\nStructure:")
        for j, node in enumerate(candidate.nodes):
            print(f"  {j+1}. {node.surface:8s} | Type: {node.type.value:12s} | ", end="")
            if node.is_inflected():
                print(f"Case: {node.case_mood.case.value:10s} (معرب)", end="")
            else:
                print(f"مبني (built-in)        ", end="")
            if node.requires_attachment():
                status = "✓ attached" if node.is_attached() else "✗ NOT attached"
                print(f" | {status}")
            else:
                print()
        
        # Evaluate
        energies, status = evaluator.evaluate_candidate(candidate)
        
        print("\nEnergy Components:")
        print(f"  E_attach: {energies.E_attach:10.4f} {'(∞)' if math.isinf(energies.E_attach) else ''}")
        print(f"  E_case:   {energies.E_case:10.4f} {'(∞)' if math.isinf(energies.E_case) else ''}")
        print(f"  E_join:   {energies.E_join:10.4f} {'(∞)' if math.isinf(energies.E_join) else ''}")
        print(f"  E_dist:   {energies.E_dist:10.4f}")
        print(f"  E_morph:  {energies.E_morph:10.4f}")
        print(f"  {'─'*40}")
        total = energies.total()
        print(f"  TOTAL:    {total:10.4f} {'(∞)' if math.isinf(total) else ''}")
        
        print(f"\nStatus: {status.value.upper()}")
        
        if status == CandidateStatus.VALID:
            print("✓ This candidate satisfies all hard constraints")
        else:
            print("✗ This candidate violates hard constraints (infinity energy)")
            if math.isinf(energies.E_case):
                print("  → Reason: Case mismatch (preposition requires genitive)")
            if math.isinf(energies.E_join):
                print("  → Reason: Clitic attachment violation (must attach)")
    
    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print("Only Candidate 1 is VALID with finite energy.")
    print("Candidates 2 and 3 are filtered out by infinity gates:")
    print("  - Candidate 2: E_case = ∞ (wrong case)")
    print("  - Candidate 3: E_join = ∞ (clitic not attached)")
    print("=" * 70)


if __name__ == "__main__":
    demonstrate_numerical_example()
