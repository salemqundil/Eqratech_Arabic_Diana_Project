"""
Augmentation Letter Operators

This module implements augmentation letters (حروف الزيادة) as
INSERTION OPERATORS around the triliteral root, with C_2 as the
economy center.

Augmentation letters: س، ل، ت، ن، م، ه، ء + ال

These are not simple "letters" but operators that:
1. Insert material at specific positions (prefix, infix, suffix)
2. Must satisfy morphological feature requirements
3. Must respect syllable structure (E_syll)
4. Must minimize economy violations (E_economy)
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Set
from enum import Enum


class InsertionPosition(Enum):
    """Position for insertion"""
    PRE = "prefix"       # Before root
    IN1 = "infix1"       # After C1
    IN2 = "infix2"       # After C2 (economy center)
    IN3 = "infix3"       # After C3
    POST = "suffix"      # After root


class AugmentationType(Enum):
    """Type of augmentation"""
    DERIVATIONAL = "derivational"  # اشتقاقي (changes word class/meaning)
    INFLECTIONAL = "inflectional"  # تصريفي (grammatical marking)
    DEFINITENESS = "definiteness"  # تعريف (ال)


@dataclass
class MorphFeature:
    """Morphological feature requirement"""
    name: str
    value: any


@dataclass
class AugmentationOperator:
    """
    An augmentation operator OP_ins(pos, feature_goal, segment)
    
    Inserts segment at position to achieve feature_goal
    """
    segment: str                           # The letter(s) to insert
    position: InsertionPosition            # Where to insert
    feature_goal: MorphFeature             # What feature it encodes
    aug_type: AugmentationType             # Type of augmentation
    
    # Constraints
    syllable_cost: float = 0.0             # Cost to syllable structure
    economy_cost: float = 0.0              # Cost to economy
    
    def __str__(self):
        return f"OP[{self.segment} @ {self.position.value} → {self.feature_goal.name}]"


@dataclass
class Root:
    """Triliteral root"""
    C1: str
    C2: str
    C3: str
    
    def __str__(self):
        return f"{self.C1}-{self.C2}-{self.C3}"


@dataclass
class DerivedForm:
    """Result of applying operators to root"""
    root: Root
    operators: List[AugmentationOperator]
    surface: str
    features: List[MorphFeature]
    
    def __str__(self):
        ops = " + ".join(str(op) for op in self.operators)
        return f"{self.root} + {ops} → {self.surface}"


class AugmentationSystem:
    """
    System for applying augmentation operators to roots
    """
    
    # Standard augmentation letters (سَألتمونيها)
    STANDARD_AUGMENTATIONS = {
        'س': 'causative/future',
        'أ': 'causative/plural',
        'ل': 'dative',
        'ت': 'reflexive/passive',
        'م': 'place/instrument',
        'و': 'conjunction/plural',
        'ن': 'passive/intensive',
        'ي': 'nisba/plural',
        'ه': 'pronoun',
        'ء': 'various',
    }
    
    # Definite article
    DEFINITE_ARTICLE = 'ال'
    
    def __init__(self):
        """Initialize augmentation system"""
        self.operators = self._create_standard_operators()
    
    def _create_standard_operators(self) -> List[AugmentationOperator]:
        """Create standard set of augmentation operators"""
        operators = []
        
        # 1. Causative prefix (أ) - Form IV
        operators.append(AugmentationOperator(
            segment='أ',
            position=InsertionPosition.PRE,
            feature_goal=MorphFeature('voice', 'causative'),
            aug_type=AugmentationType.DERIVATIONAL,
            syllable_cost=0.5,
            economy_cost=1.0
        ))
        
        # 2. Reflexive/passive prefix (ت) - Forms V, VI
        operators.append(AugmentationOperator(
            segment='ت',
            position=InsertionPosition.PRE,
            feature_goal=MorphFeature('voice', 'reflexive'),
            aug_type=AugmentationType.DERIVATIONAL,
            syllable_cost=0.5,
            economy_cost=1.0
        ))
        
        # 3. Gemination on C2 (تشديد) - Form II
        operators.append(AugmentationOperator(
            segment='shadda',
            position=InsertionPosition.IN2,
            feature_goal=MorphFeature('intensity', 'intensive'),
            aug_type=AugmentationType.DERIVATIONAL,
            syllable_cost=1.0,  # Changes syllable weight
            economy_cost=0.5    # C2 is economy center - lower cost here
        ))
        
        # 4. Long vowel after C2 - Form III
        operators.append(AugmentationOperator(
            segment='aa',
            position=InsertionPosition.IN2,
            feature_goal=MorphFeature('valency', 'reciprocal'),
            aug_type=AugmentationType.DERIVATIONAL,
            syllable_cost=0.5,
            economy_cost=0.5    # C2 is economy center
        ))
        
        # 5. Infix (ت) after C1 - Form VIII
        operators.append(AugmentationOperator(
            segment='ت',
            position=InsertionPosition.IN1,
            feature_goal=MorphFeature('voice', 'middle'),
            aug_type=AugmentationType.DERIVATIONAL,
            syllable_cost=1.0,
            economy_cost=1.5    # Not at C2 - higher cost
        ))
        
        # 6. Definite article (ال)
        operators.append(AugmentationOperator(
            segment='ال',
            position=InsertionPosition.PRE,
            feature_goal=MorphFeature('definiteness', 'definite'),
            aug_type=AugmentationType.DEFINITENESS,
            syllable_cost=0.5,
            economy_cost=0.5
        ))
        
        # 7. Feminine marker (ة/ت)
        operators.append(AugmentationOperator(
            segment='ة',
            position=InsertionPosition.POST,
            feature_goal=MorphFeature('gender', 'feminine'),
            aug_type=AugmentationType.INFLECTIONAL,
            syllable_cost=0.5,
            economy_cost=1.0
        ))
        
        return operators
    
    def compute_total_cost(self, operators: List[AugmentationOperator]) -> float:
        """
        Compute total cost of applying operators
        
        E_total = E_syll + E_economy
        """
        E_syll = sum(op.syllable_cost for op in operators)
        E_economy = sum(op.economy_cost for op in operators)
        return E_syll + E_economy
    
    def apply_operators(
        self,
        root: Root,
        operators: List[AugmentationOperator]
    ) -> DerivedForm:
        """
        Apply operators to root to derive surface form
        
        This is a simplified version - full implementation would
        handle vowel patterns, assimilation, etc.
        """
        # Sort operators by position
        sorted_ops = sorted(operators, key=lambda op: op.position.value)
        
        # Build surface form
        parts = []
        root_parts = {
            InsertionPosition.PRE: [],
            InsertionPosition.IN1: [root.C1],
            InsertionPosition.IN2: [root.C2],
            InsertionPosition.IN3: [root.C3],
            InsertionPosition.POST: []
        }
        
        # Insert augmentations
        for op in sorted_ops:
            if op.segment != 'shadda':  # Shadda is special
                root_parts[op.position].append(op.segment)
        
        # Assemble
        surface = (
            ''.join(root_parts[InsertionPosition.PRE]) +
            ''.join(root_parts[InsertionPosition.IN1]) +
            ''.join(root_parts[InsertionPosition.IN2]) +
            ''.join(root_parts[InsertionPosition.IN3]) +
            ''.join(root_parts[InsertionPosition.POST])
        )
        
        # Collect features
        features = [op.feature_goal for op in operators]
        
        return DerivedForm(
            root=root,
            operators=operators,
            surface=surface,
            features=features
        )
    
    def why_c2_is_center(self) -> str:
        """
        Explain why C_2 is the economy center
        """
        return """
        C_2 (the middle consonant) is the ECONOMY CENTER because:
        
        1. Symmetry: It's equidistant from C_1 and C_3
        2. Maximum impact: Changes to C_2 affect both transitions
           (C_1→C_2 and C_2→C_3)
        3. Derivational patterns: Many verb forms modify C_2:
           - Form II: C_2 gemination (كَتَّبَ)
           - Form III: Long vowel after C_2 (كَاتَبَ)
           - Form V: ت + C_2 gemination (تَكَتَّبَ)
        4. Feature transitions: Σ|Δfeatures| is maximized at C_2
        5. Cognitive salience: C_2 is perceptually central
        
        Therefore, insertions at C_2 have LOWER economy cost than
        insertions elsewhere.
        """


def demonstrate_augmentation_operators():
    """
    Demonstrate augmentation operators with examples
    """
    print("=" * 70)
    print("AUGMENTATION LETTER OPERATORS")
    print("=" * 70)
    print("\nAugmentation letters are not just letters, but OPERATORS")
    print("that insert material around the root with specific functions.")
    print()
    
    system = AugmentationSystem()
    
    # Example root: ك-ت-ب (k-t-b, "write")
    root = Root(C1='ك', C2='ت', C3='ب')
    
    print(f"Root: {root} (k-t-b, 'write')")
    print()
    
    # Show standard operators
    print("Standard Augmentation Operators:")
    print()
    for i, op in enumerate(system.operators, 1):
        print(f"{i}. {op}")
        print(f"   Type: {op.aug_type.value}")
        print(f"   Costs: E_syll={op.syllable_cost}, E_economy={op.economy_cost}")
        print()
    
    # Example derivations
    print("=" * 70)
    print("EXAMPLE DERIVATIONS")
    print("=" * 70)
    print()
    
    examples = [
        # Form I (base)
        ([], "كَتَبَ", "he wrote (basic)"),
        
        # Form II (gemination on C2)
        ([system.operators[2]], "كَتَّبَ", "he made write (causative/intensive)"),
        
        # Form III (long vowel after C2)
        ([system.operators[3]], "كَاتَبَ", "he corresponded (reciprocal)"),
        
        # Form IV (causative prefix)
        ([system.operators[0]], "أَكْتَبَ", "he dictated (causative)"),
        
        # With definite article
        ([system.operators[5]], "الكِتَاب", "the book (definite)"),
    ]
    
    for ops, surface_expected, gloss in examples:
        if ops:
            derived = system.apply_operators(root, ops)
            cost = system.compute_total_cost(ops)
            
            print(f"Surface: {surface_expected}")
            print(f"Gloss:   {gloss}")
            print(f"Operators: {', '.join(str(op.segment) for op in ops)}")
            print(f"Total cost: E = {cost:.2f}")
            
            # Show which position
            positions = [op.position.value for op in ops]
            print(f"Positions: {', '.join(positions)}")
        else:
            print(f"Surface: {surface_expected}")
            print(f"Gloss:   {gloss}")
            print(f"Operators: (none - base form)")
            print(f"Total cost: E = 0.00")
        
        print()
    
    # Explain C_2 as center
    print("=" * 70)
    print("WHY C_2 IS THE ECONOMY CENTER")
    print("=" * 70)
    explanation = system.why_c2_is_center()
    print(explanation)
    print("=" * 70)


if __name__ == "__main__":
    demonstrate_augmentation_operators()
