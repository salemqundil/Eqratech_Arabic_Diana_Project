"""
Unified Node Schema DSL

This module defines a unified schema for linguistic nodes that handles
both inflected (معرب mu'rab) and built-in (مبني mabnī) words within
the same framework.

Node types include: consonants, vowels, functional words, built-in words,
augmentation letters, nouns, and verbs.
"""

from dataclasses import dataclass, field
from typing import Optional, Set, List
from enum import Enum, auto


class NodeType(Enum):
    """Types of linguistic nodes"""
    C = "consonant"           # صامت
    V = "vowel"              # صائت
    FUNC = "function_word"   # حرف وظيفي
    MABNI = "built_in"       # مبني
    ZAID = "augmentation"    # حرف زائد
    NOUN = "noun"            # اسم
    VERB = "verb"            # فعل


class Case(Enum):
    """Grammatical case (حالات الإعراب)"""
    NOM = "nominative"       # رفع (marfuu3)
    ACC = "accusative"       # نصب (manSuub)
    GEN = "genitive"         # جر (majruur)
    NONE = "none"            # لا إعراب (no case marking)


class Mood(Enum):
    """Verbal mood (أوجه الفعل)"""
    IND = "indicative"       # مرفوع (marfuu3)
    JUS = "jussive"          # مجزوم (majzuum)
    SUBJ = "subjunctive"     # منصوب (manSuub)
    NONE = "none"            # لا مود


class JoinPolicy(Enum):
    """Attachment policy for clitics"""
    MUST = "must_attach"     # يجب الاتصال
    PREFER = "prefer_attach" # يفضل الاتصال
    FREE = "free"            # حر
    FORBID = "forbid_attach" # يمنع الاتصال


class RelationType(Enum):
    """Types of syntactic relations"""
    ISNADI = "predicative"      # إسنادي (verb-subject, subject-predicate)
    TADMINI = "transitive"      # تضميني (transitive verb-object)
    TAQYIDI = "attributive"     # تقييدي (adjective-noun with agreement)
    TAQYID_PP = "pp_attachment" # تقييد حرف الجر
    TAQYID_IDAFA = "possessive" # تقييد إضافة
    NONE = "none"


class ThetaRole(Enum):
    """Theta (semantic) roles"""
    AGENT = "agent"          # فاعل دلالي
    THEME = "theme"          # موضوع
    POSS = "possessor"       # مالك
    REF = "referent"         # مرجع
    NONE = "none"


class SyntacticRole(Enum):
    """Syntactic roles"""
    HEAD = "head"            # رأس
    DEP = "dependent"        # تابع
    CLITIC = "clitic"        # متصل
    NONE = "none"


@dataclass
class Anchor:
    """Position information for a node in template/sentence"""
    slot: int                    # Position in template
    span: tuple[int, int]        # Character span in string
    head: Optional[int] = None   # Index of syntactic head (if dependent)


@dataclass
class Signature:
    """
    Attachment signature - defines what the node requires and provides
    """
    reqL: Optional[str] = None          # Required left context
    reqR: Optional[str] = None          # Required right context
    relType: RelationType = RelationType.NONE  # Type of relation
    scope: str = "local"                # Scope: local, clause, sentence


@dataclass
class CaseMood:
    """Case and mood information with locking status"""
    case: Case = Case.NONE
    mood: Mood = Mood.NONE
    locked: bool = False  # True for مبني (built-in), False for معرب (inflected)


@dataclass
class Join:
    """Join/attachment policy and status"""
    policy: JoinPolicy = JoinPolicy.FREE
    value: int = 0  # 0=separate, 1=attached


@dataclass
class Roles:
    """Semantic and syntactic roles"""
    theta: ThetaRole = ThetaRole.NONE
    syntactic: SyntacticRole = SyntacticRole.NONE


@dataclass
class Node:
    """
    Unified node schema for morphological and syntactic analysis
    
    This schema handles both:
    - معرب (mu'rab): inflected words with variable Case/Mood
    - مبني (mabnī): built-in words with locked Case/Mood
    
    The distinction is captured through CaseMood.locked and Join.policy
    """
    # Identity
    id: str
    type: NodeType
    
    # Position
    anchor: Anchor
    
    # Attachment signature
    sig: Signature
    
    # Case and mood
    case_mood: CaseMood
    
    # Join/attachment
    join: Join
    
    # Roles
    roles: Roles
    
    # Surface form
    surface: str = ""
    
    # Features
    features: dict = field(default_factory=dict)
    
    def is_inflected(self) -> bool:
        """Check if node is inflected (معرب)"""
        return not self.case_mood.locked
    
    def is_built_in(self) -> bool:
        """Check if node is built-in (مبني)"""
        return self.case_mood.locked
    
    def requires_attachment(self) -> bool:
        """Check if node must attach (e.g., clitic pronouns)"""
        return self.join.policy == JoinPolicy.MUST
    
    def is_attached(self) -> bool:
        """Check if node is currently attached"""
        return self.join.value == 1
    
    def can_govern_case(self) -> bool:
        """Check if node can govern case (e.g., prepositions, transitive verbs)"""
        return self.type in {NodeType.FUNC, NodeType.VERB} and \
               self.sig.relType in {RelationType.TAQYID_PP, RelationType.TADMINI}


# Factory functions for common node types

def create_preposition(
    id: str,
    surface: str,
    governs_case: Case = Case.GEN,
    slot: int = 0
) -> Node:
    """Create a preposition node (حرف جر)"""
    return Node(
        id=id,
        type=NodeType.FUNC,
        anchor=Anchor(slot=slot, span=(0, len(surface))),
        sig=Signature(
            reqL="head(any)",
            reqR="Noun",
            relType=RelationType.TAQYID_PP,
            scope="local"
        ),
        case_mood=CaseMood(case=governs_case, locked=True),
        join=Join(policy=JoinPolicy.PREFER, value=0),
        roles=Roles(theta=ThetaRole.NONE, syntactic=SyntacticRole.HEAD),
        surface=surface,
        features={'governs': governs_case.value}
    )


def create_noun(
    id: str,
    surface: str,
    case: Case = Case.NOM,
    slot: int = 1,
    locked: bool = False
) -> Node:
    """Create a noun node (اسم)"""
    return Node(
        id=id,
        type=NodeType.NOUN,
        anchor=Anchor(slot=slot, span=(0, len(surface))),
        sig=Signature(relType=RelationType.NONE),
        case_mood=CaseMood(case=case, locked=locked),
        join=Join(policy=JoinPolicy.FREE, value=0),
        roles=Roles(theta=ThetaRole.THEME, syntactic=SyntacticRole.HEAD),
        surface=surface
    )


def create_attached_pronoun(
    id: str,
    surface: str,
    slot: int = 2,
    head_slot: Optional[int] = None
) -> Node:
    """Create an attached pronoun node (ضمير متصل)"""
    return Node(
        id=id,
        type=NodeType.MABNI,
        anchor=Anchor(slot=slot, span=(0, len(surface)), head=head_slot),
        sig=Signature(
            reqL="Noun",
            reqR=None,
            relType=RelationType.TAQYID_IDAFA,
            scope="local"
        ),
        case_mood=CaseMood(locked=True),  # Pronouns are مبني
        join=Join(policy=JoinPolicy.MUST, value=1),  # Must attach
        roles=Roles(theta=ThetaRole.POSS, syntactic=SyntacticRole.CLITIC),
        surface=surface,
        features={'person': 3, 'gender': 'masculine', 'number': 'singular'}
    )


def create_definite_article(
    id: str,
    slot: int = 0
) -> Node:
    """Create definite article (ال) node"""
    return Node(
        id=id,
        type=NodeType.ZAID,
        anchor=Anchor(slot=slot, span=(0, 2)),
        sig=Signature(reqR="Noun", relType=RelationType.NONE),
        case_mood=CaseMood(locked=True),
        join=Join(policy=JoinPolicy.MUST, value=1),
        roles=Roles(syntactic=SyntacticRole.CLITIC),
        surface="ال",
        features={'definiteness': 'definite'}
    )


if __name__ == "__main__":
    # Example: Create nodes for "في بيتِهِ" (in his house)
    
    # في (preposition)
    prep = create_preposition("prep1", "في", Case.GEN, slot=0)
    
    # بيت (noun in genitive)
    noun = create_noun("noun1", "بيت", Case.GEN, slot=1)
    
    # ـه (attached pronoun)
    pronoun = create_attached_pronoun("pron1", "ه", slot=2, head_slot=1)
    
    print("=" * 60)
    print("Example: في بيتِهِ (in his house)")
    print("=" * 60)
    print(f"\n1. Preposition: {prep.surface}")
    print(f"   Type: {prep.type.value}")
    print(f"   Governs: {prep.features.get('governs')}")
    print(f"   Requires right: {prep.sig.reqR}")
    
    print(f"\n2. Noun: {noun.surface}")
    print(f"   Type: {noun.type.value}")
    print(f"   Case: {noun.case_mood.case.value}")
    print(f"   Inflected: {noun.is_inflected()}")
    
    print(f"\n3. Pronoun: {pronoun.surface}")
    print(f"   Type: {pronoun.type.value}")
    print(f"   Built-in: {pronoun.is_built_in()}")
    print(f"   Must attach: {pronoun.requires_attachment()}")
    print(f"   Attached: {pronoun.is_attached()}")
    print("=" * 60)
