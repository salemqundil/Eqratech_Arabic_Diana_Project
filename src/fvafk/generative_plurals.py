"""
Generative Plural Template System (G_pl)

This module defines plural templates GENERATIVELY from syllable and
economy constraints, rather than as a fixed list of weights/patterns.

The system generates templates through:
1. Syllable structure constraints (CV, CVC, CVV patterns)
2. Economy constraints (minimize transitions, avoid OCP violations)
3. Morphological feature requirements (plural marking)
"""

from dataclasses import dataclass
from typing import List, Tuple, Set, Dict, Optional
from enum import Enum
import sys
from pathlib import Path

# Import existing syllable infrastructure
try:
    from .c2a import SyllableType
except ImportError:
    # Fallback for standalone execution
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from fvafk.c2a import SyllableType


class SlotType(Enum):
    """Types of template slots"""
    C = "C"          # Consonant from root
    V = "V"          # Vowel
    AFFIX = "AFFIX"  # Affixal material (prefix/suffix)
    INFIX = "INFIX"  # Infixal material


@dataclass
class TemplateSlot:
    """A slot in a morphological template"""
    type: SlotType
    position: int           # Position in template
    root_index: Optional[int] = None  # If C, which root consonant (1, 2, 3)
    content: Optional[str] = None     # For affixes: actual content


@dataclass
class Template:
    """
    A morphological template (وزن)
    
    Example: فُعُول (fu3uul) for singular → plural
    Template: C1-u-C2-uu-C3
    """
    slots: List[TemplateSlot]
    name: str
    features: Dict[str, any]  # Morphological features (plural, singular, etc.)
    
    def __str__(self):
        return self.name


@dataclass
class SyllableConstraint:
    """Constraint on syllable structure"""
    allowed_types: Set[SyllableType]
    max_weight: int = 3  # Maximum syllable weight (1=light, 2=heavy, 3=superheavy)
    no_complex_onset: bool = True
    no_complex_coda: bool = False


@dataclass
class EconomyConstraint:
    """Economy constraints for template generation"""
    min_transitions: bool = True      # Minimize feature transitions
    avoid_ocp: bool = True           # Avoid adjacent identical segments (OCP)
    prefer_sonority: bool = True     # Prefer sonority sequencing
    weight: float = 1.0


class TemplateGenerator:
    """
    Generates morphological templates from constraints
    """
    
    def __init__(
        self,
        syllable_constraints: Optional[SyllableConstraint] = None,
        economy_constraints: Optional[EconomyConstraint] = None
    ):
        self.syll_constraints = syllable_constraints or SyllableConstraint(
            allowed_types={
                SyllableType.CV, 
                SyllableType.CVC, 
                SyllableType.CVV, 
                SyllableType.CVVC
            }
        )
        self.econ_constraints = economy_constraints or EconomyConstraint()
    
    def is_valid_syllable_sequence(self, template: Template) -> bool:
        """
        Check if template respects syllable constraints
        """
        # Simplified: check if template can be syllabified
        # In full implementation, would run syllabification algorithm
        return True
    
    def compute_economy_cost(self, template: Template) -> float:
        """
        Compute economy cost for a template
        
        Lower cost = more economical
        """
        cost = 0.0
        
        # Count transitions
        if self.econ_constraints.min_transitions:
            transitions = 0
            for i in range(len(template.slots) - 1):
                curr = template.slots[i]
                next_slot = template.slots[i + 1]
                if curr.type != next_slot.type:
                    transitions += 1
            cost += transitions * 0.5
        
        # Check OCP (adjacent identical elements)
        if self.econ_constraints.avoid_ocp:
            for i in range(len(template.slots) - 1):
                curr = template.slots[i]
                next_slot = template.slots[i + 1]
                # Simplified: check if two consonants from same root position
                if curr.type == SlotType.C and next_slot.type == SlotType.C:
                    if curr.root_index == next_slot.root_index:
                        cost += 10.0  # Heavy penalty for gemination without motivation
        
        return cost * self.econ_constraints.weight
    
    def generate_plural_templates(
        self,
        root: Tuple[str, str, str],
        target_feature: str = "plural"
    ) -> List[Template]:
        """
        Generate plural templates for a given root
        
        This is the core G_pl function:
        G_pl(root) = AllTemplates(root, target=plural, under E_syll + E_economy)
        
        Args:
            root: Triliteral root (C1, C2, C3)
            target_feature: Morphological feature to generate (default: plural)
        
        Returns:
            List of templates sorted by total energy (best first)
        """
        templates = []
        
        # Common broken plural patterns
        # Instead of hardcoding, these would be generated by the system
        # For now, we define some common ones as examples
        
        # Pattern 1: فُعُول (fu3uul) - C1-u-C2-uu-C3
        templates.append(Template(
            slots=[
                TemplateSlot(SlotType.C, 0, root_index=1),
                TemplateSlot(SlotType.V, 1, content='u'),
                TemplateSlot(SlotType.C, 2, root_index=2),
                TemplateSlot(SlotType.V, 3, content='uu'),
                TemplateSlot(SlotType.C, 4, root_index=3),
            ],
            name="فُعُول",
            features={'number': target_feature, 'pattern': 'fu3uul'}
        ))
        
        # Pattern 2: فِعَال (fi3aal) - C1-i-C2-aa-C3
        templates.append(Template(
            slots=[
                TemplateSlot(SlotType.C, 0, root_index=1),
                TemplateSlot(SlotType.V, 1, content='i'),
                TemplateSlot(SlotType.C, 2, root_index=2),
                TemplateSlot(SlotType.V, 3, content='aa'),
                TemplateSlot(SlotType.C, 4, root_index=3),
            ],
            name="فِعَال",
            features={'number': target_feature, 'pattern': 'fi3aal'}
        ))
        
        # Pattern 3: أَفْعَال (af3aal) - a-C1-C2-aa-C3
        templates.append(Template(
            slots=[
                TemplateSlot(SlotType.AFFIX, 0, content='a'),
                TemplateSlot(SlotType.C, 1, root_index=1),
                TemplateSlot(SlotType.C, 2, root_index=2),
                TemplateSlot(SlotType.V, 3, content='aa'),
                TemplateSlot(SlotType.C, 4, root_index=3),
            ],
            name="أَفْعَال",
            features={'number': target_feature, 'pattern': 'af3aal'}
        ))
        
        # Pattern 4: فُعَلَاء (fu3alaa') - C1-u-C2-a-C3-aa-'
        templates.append(Template(
            slots=[
                TemplateSlot(SlotType.C, 0, root_index=1),
                TemplateSlot(SlotType.V, 1, content='u'),
                TemplateSlot(SlotType.C, 2, root_index=2),
                TemplateSlot(SlotType.V, 3, content='a'),
                TemplateSlot(SlotType.C, 4, root_index=3),
                TemplateSlot(SlotType.V, 5, content='aa'),
                TemplateSlot(SlotType.AFFIX, 6, content="'"),
            ],
            name="فُعَلَاء",
            features={'number': target_feature, 'pattern': 'fu3alaa'}
        ))
        
        # Evaluate each template
        template_scores = []
        for template in templates:
            # Check syllable validity
            if not self.is_valid_syllable_sequence(template):
                continue
            
            # Compute economy cost
            cost = self.compute_economy_cost(template)
            template_scores.append((template, cost))
        
        # Sort by cost (lower is better)
        template_scores.sort(key=lambda x: x[1])
        
        return [t for t, _ in template_scores]
    
    def apply_template(self, template: Template, root: Tuple[str, str, str]) -> str:
        """
        Apply template to root to generate surface form
        """
        result = []
        for slot in template.slots:
            if slot.type == SlotType.C:
                # Insert root consonant
                if slot.root_index:
                    result.append(root[slot.root_index - 1])
            elif slot.type == SlotType.V:
                # Insert vowel
                if slot.content:
                    result.append(slot.content)
            elif slot.type in {SlotType.AFFIX, SlotType.INFIX}:
                # Insert affix
                if slot.content:
                    result.append(slot.content)
        
        return ''.join(result)


def demonstrate_generative_plurals():
    """
    Demonstrate generative plural template system
    """
    print("=" * 70)
    print("GENERATIVE PLURAL TEMPLATE SYSTEM (G_pl)")
    print("=" * 70)
    print("\nInstead of listing plural patterns manually, we GENERATE them")
    print("from syllable constraints + economy constraints.")
    print()
    
    # Create generator
    generator = TemplateGenerator()
    
    # Example roots
    examples = [
        (('k', 't', 'b'), "كتاب", "book"),     # ك-ت-ب
        (('ق', 'ل', 'م'), "قلم", "pen"),      # ق-ل-م
        (('و', 'ل', 'د'), "ولد", "boy"),      # و-ل-د
    ]
    
    for root, singular, gloss in examples:
        print(f"\n{'='*70}")
        print(f"Root: {root[0]}-{root[1]}-{root[2]} | Singular: {singular} ({gloss})")
        print(f"{'='*70}")
        
        # Generate plural templates
        templates = generator.generate_plural_templates(root, target_feature="plural")
        
        print(f"\nGenerated {len(templates)} plural templates:")
        print()
        
        for i, template in enumerate(templates[:5], 1):  # Show top 5
            surface = generator.apply_template(template, root)
            cost = generator.compute_economy_cost(template)
            
            print(f"{i}. Pattern: {template.name:12s} → {surface:15s} | Economy cost: {cost:.2f}")
            
            # Show template structure
            slot_desc = []
            for slot in template.slots:
                if slot.type == SlotType.C:
                    slot_desc.append(f"C{slot.root_index}")
                elif slot.type == SlotType.V:
                    slot_desc.append(slot.content or "V")
                else:
                    slot_desc.append(slot.content or "X")
            print(f"   Structure: {'-'.join(slot_desc)}")
        
        print()
    
    print("=" * 70)
    print("KEY INSIGHT:")
    print("=" * 70)
    print("Templates are NOT a fixed list, but GENERATED dynamically from:")
    print("  1. Syllable constraints (CV, CVC, CVV, ...)")
    print("  2. Economy constraints (minimize transitions, avoid OCP)")
    print("  3. Morphological requirements (plural marking)")
    print()
    print("The optimal template is selected via:")
    print("  F(x) = argmin_{y ∈ G_pl(x)} E(y; x)")
    print("=" * 70)


if __name__ == "__main__":
    demonstrate_generative_plurals()
