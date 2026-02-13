"""
Comprehensive Integration Example

This module demonstrates how all components of the framework work together
in a complete analysis pipeline.
"""

from src.fvafk.vowel_space_optimization import (
    OptimizationParameters, VowelSpaceOptimizer
)
from src.fvafk.node_schema import (
    create_preposition, create_noun, create_attached_pronoun, create_definite_article
)
from src.fvafk.energy_evaluation import (
    EnergyEvaluator, Candidate, CandidateStatus
)
from src.fvafk.generative_plurals import TemplateGenerator
from src.fvafk.augmentation_operators import AugmentationSystem, Root


def demonstrate_complete_pipeline():
    """
    Demonstrate the complete framework with an integrated example
    """
    
    print("=" * 80)
    print("COMPREHENSIVE INTEGRATION EXAMPLE")
    print("=" * 80)
    print()
    
    # ========================================================================
    # Part 1: Vowel Space Optimization
    # ========================================================================
    print("PART 1: VOWEL SPACE OPTIMIZATION")
    print("─" * 80)
    print("Verifying that the Arabic vowel system {a, i, u} is optimal")
    print()
    
    params = OptimizationParameters(lambda_=0.3, kappa=1.0, rho=0.5)
    optimizer = VowelSpaceOptimizer(params)
    report = optimizer.verify_optimal_system()
    
    print(f"Parameters: λ={params.lambda_}, κ={params.kappa}, ρ={params.rho}")
    print(f"System optimal: {report['optimal']}")
    print(f"Dispersion: {report['dispersion']:.4f}")
    print(f"Cost: {report['cost']:.4f}")
    print(f"Collapse prevented: {report['collapse_prevented']}")
    print(f"Rounding correct: {report['rounding_correct']}")
    print()
    
    # ========================================================================
    # Part 2: Morphological Analysis with Energy Evaluation
    # ========================================================================
    print("PART 2: MORPHOLOGICAL ANALYSIS - في بيتِهِ")
    print("─" * 80)
    print("Analyzing: في بيتِهِ (fii bayti-hi, 'in his house')")
    print("Structure: preposition + inflected noun + attached pronoun")
    print()
    
    # Create correct structure
    prep = create_preposition("prep1", "في", slot=0)
    noun = create_noun("noun1", "بيتِ", case=prep.case_mood.case, slot=1)
    pron = create_attached_pronoun("pron1", "ـهِ", slot=2, head_slot=1)
    pron.join.value = 1  # Attached
    
    correct_candidate = Candidate([prep, noun, pron], "في بيتِهِ (correct)")
    
    # Evaluate
    evaluator = EnergyEvaluator()
    energies, status = evaluator.evaluate_candidate(correct_candidate)
    
    print(f"Candidate: {correct_candidate.description}")
    print(f"Status: {status.value}")
    print(f"Energy components:")
    print(f"  E_attach: {energies.E_attach:.4f}")
    print(f"  E_case:   {energies.E_case:.4f}")
    print(f"  E_join:   {energies.E_join:.4f}")
    print(f"  TOTAL:    {energies.total():.4f}")
    print()
    
    # ========================================================================
    # Part 3: Generative Plural Templates
    # ========================================================================
    print("PART 3: GENERATIVE PLURAL TEMPLATES")
    print("─" * 80)
    print("Generating plural templates for root ك-ت-ب (k-t-b, 'write')")
    print()
    
    generator = TemplateGenerator()
    root_ktb = ('ك', 'ت', 'ب')
    
    templates = generator.generate_plural_templates(root_ktb, target_feature="plural")
    
    print(f"Generated {len(templates)} templates (showing top 3):")
    print()
    
    for i, template in enumerate(templates[:3], 1):
        surface = generator.apply_template(template, root_ktb)
        cost = generator.compute_economy_cost(template)
        print(f"{i}. {template.name:12s} → {surface:12s} (economy cost: {cost:.2f})")
    
    print()
    
    # ========================================================================
    # Part 4: Augmentation Operators
    # ========================================================================
    print("PART 4: AUGMENTATION OPERATORS")
    print("─" * 80)
    print("Applying augmentation operators to root ك-ت-ب")
    print()
    
    aug_system = AugmentationSystem()
    root_obj = Root(C1='ك', C2='ت', C3='ب')
    
    # Show some derivations
    derivations = [
        ([], "كَتَبَ", "he wrote (Form I)"),
        ([aug_system.operators[2]], "كَتَّبَ", "he made write (Form II - C2 gemination)"),
        ([aug_system.operators[0]], "أَكْتَبَ", "he dictated (Form IV - causative prefix)"),
    ]
    
    print("Derivational forms:")
    print()
    
    for ops, surface, gloss in derivations:
        if ops:
            cost = aug_system.compute_total_cost(ops)
            positions = [op.position.value for op in ops]
            print(f"  {surface:12s} - {gloss}")
            print(f"    Operators: {', '.join(op.segment for op in ops)}")
            print(f"    Positions: {', '.join(positions)}")
            print(f"    Cost: {cost:.2f}")
        else:
            print(f"  {surface:12s} - {gloss}")
            print(f"    Base form (no operators)")
            print(f"    Cost: 0.00")
        print()
    
    # ========================================================================
    # Part 5: Complete Analysis Pipeline
    # ========================================================================
    print("PART 5: COMPLETE ANALYSIS EXAMPLE")
    print("─" * 80)
    print("Analyzing a complex phrase: في الكِتابِ (fii al-kitaab-i, 'in the book')")
    print("Structure: preposition + definite article + noun")
    print()
    
    # Create structure
    prep2 = create_preposition("prep2", "في", slot=0)
    article = create_definite_article("def1", slot=1)
    article.join.value = 1  # Attached to noun
    noun2 = create_noun("noun2", "كِتابِ", case=prep2.case_mood.case, slot=2)
    
    phrase = Candidate([prep2, article, noun2], "في الكِتابِ")
    
    # Evaluate
    energies2, status2 = evaluator.evaluate_candidate(phrase)
    
    print(f"Phrase: {phrase.description}")
    print(f"Components:")
    for i, node in enumerate(phrase.nodes, 1):
        print(f"  {i}. {node.surface:8s} ({node.type.value})")
    
    print(f"\nStatus: {status2.value}")
    print(f"Total energy: {energies2.total():.4f}")
    print()
    
    # ========================================================================
    # Summary
    # ========================================================================
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print("This framework provides:")
    print("  1. ✓ Rigorous vowel space optimization with mathematical guarantees")
    print("  2. ✓ Unified representation for inflected and built-in words")
    print("  3. ✓ Energy-based evaluation with infinity gates for hard constraints")
    print("  4. ✓ Generative template system (not manual lists)")
    print("  5. ✓ Augmentation operators with position-based economy costs")
    print()
    print("All components work together in a principled, theoretically-grounded way.")
    print("=" * 80)


if __name__ == "__main__":
    demonstrate_complete_pipeline()
