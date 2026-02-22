"""
WordForm: Unified representation bridging C2B (morphology) and Syntax

This module provides a unified data structure that combines morphological
analysis from C2B with syntactic features needed for the Syntax Layer.

Author: Hussein Hiyassat
Date: 2025-02-12
Version: 1.0
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


# =============================================================================
# Enumerations
# =============================================================================

class PartOfSpeech(Enum):
    """Part of speech tags"""
    NOUN = "noun"
    VERB = "verb"
    PARTICLE = "particle"
    PRONOUN = "pronoun"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    UNKNOWN = "unknown"
    
    def __str__(self):
        return self.value


class Case(Enum):
    """Grammatical case (إعراب)"""
    NOMINATIVE = "nominative"  # مرفوع
    ACCUSATIVE = "accusative"  # منصوب
    GENITIVE = "genitive"      # مجرور
    UNKNOWN = "unknown"
    
    def __str__(self):
        return self.value
    
    @property
    def arabic(self) -> str:
        """Get Arabic name"""
        mapping = {
            Case.NOMINATIVE: "مرفوع",
            Case.ACCUSATIVE: "منصوب",
            Case.GENITIVE: "مجرور",
            Case.UNKNOWN: "غير معروف"
        }
        return mapping[self]


class Number(Enum):
    """Grammatical number (العدد)"""
    SINGULAR = "singular"  # مفرد
    DUAL = "dual"          # مثنى
    PLURAL = "plural"      # جمع
    UNKNOWN = "unknown"
    
    def __str__(self):
        return self.value
    
    @property
    def arabic(self) -> str:
        """Get Arabic name"""
        mapping = {
            Number.SINGULAR: "مفرد",
            Number.DUAL: "مثنى",
            Number.PLURAL: "جمع",
            Number.UNKNOWN: "غير معروف"
        }
        return mapping[self]


class Gender(Enum):
    """Grammatical gender (الجنس)"""
    MASCULINE = "masculine"  # مذكر
    FEMININE = "feminine"    # مؤنث
    UNKNOWN = "unknown"
    
    def __str__(self):
        return self.value
    
    @property
    def arabic(self) -> str:
        """Get Arabic name"""
        mapping = {
            Gender.MASCULINE: "مذكر",
            Gender.FEMININE: "مؤنث",
            Gender.UNKNOWN: "غير معروف"
        }
        return mapping[self]


class SyntaxRole(Enum):
    """Syntactic role in sentence (الوظيفة النحوية)"""
    MUBTADA = "mubtada"              # مبتدأ
    KHABAR = "khabar"                # خبر
    FAIL = "fail"                    # فاعل
    MAFOOL_BIH = "mafool_bih"        # مفعول به
    MUDAF = "mudaf"                  # مضاف
    MUDAF_ILAYH = "mudaf_ilayh"      # مضاف إليه
    SIFA = "sifa"                    # صفة
    MAWSOOF = "mawsoof"              # موصوف
    HAAL = "haal"                    # حال
    TAMYEEZ = "tamyeez"              # تمييز
    UNKNOWN = "unknown"
    
    def __str__(self):
        return self.value
    
    @property
    def arabic(self) -> str:
        """Get Arabic name"""
        mapping = {
            SyntaxRole.MUBTADA: "مبتدأ",
            SyntaxRole.KHABAR: "خبر",
            SyntaxRole.FAIL: "فاعل",
            SyntaxRole.MAFOOL_BIH: "مفعول به",
            SyntaxRole.MUDAF: "مضاف",
            SyntaxRole.MUDAF_ILAYH: "مضاف إليه",
            SyntaxRole.SIFA: "صفة",
            SyntaxRole.MAWSOOF: "موصوف",
            SyntaxRole.HAAL: "حال",
            SyntaxRole.TAMYEEZ: "تمييز",
            SyntaxRole.UNKNOWN: "غير معروف"
        }
        return mapping[self]


# =============================================================================
# Data Structures
# =============================================================================

@dataclass(frozen=True)
class Root:
    """Root letters (جذر)"""
    letters: tuple[str, ...]
    formatted: str
    type: str = "trilateral"  # trilateral, quadrilateral, etc.
    
    @property
    def length(self) -> int:
        return len(self.letters)
    
    def __str__(self):
        return self.formatted


@dataclass(frozen=True)
class Pattern:
    """Morphological pattern (وزن)"""
    template: str
    type: str
    category: str
    confidence: float = 1.0
    
    def __str__(self):
        return self.template


@dataclass(frozen=True)
class Span:
    """Text span (position in original text)"""
    start: int
    end: int
    
    def __len__(self):
        return self.end - self.start
    
    def overlaps(self, other: 'Span') -> bool:
        """Check if this span overlaps with another"""
        return not (self.end <= other.start or other.end <= self.start)
    
    def contains(self, other: 'Span') -> bool:
        """Check if this span contains another"""
        return self.start <= other.start and self.end >= other.end


@dataclass(frozen=True)
class Affixes:
    """Prefixes and suffixes"""
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    
    def has_prefix(self) -> bool:
        return self.prefix is not None
    
    def has_suffix(self) -> bool:
        return self.suffix is not None


# =============================================================================
# Main WordForm Class
# =============================================================================

@dataclass
class WordForm:
    """
    Unified word representation bridging morphology and syntax
    
    This class combines:
    - Surface form and position
    - Morphological analysis (from C2B)
    - Syntactic features (for Syntax Layer)
    
    Attributes:
        surface: Surface form of the word
        span: Position in original text
        root: Root letters (optional)
        pattern: Morphological pattern (optional)
        affixes: Prefixes and suffixes (optional)
        pos: Part of speech
        case: Grammatical case
        definiteness: Whether word is definite (معرفة)
        number: Grammatical number
        gender: Grammatical gender
        syntax_role: Syntactic role in sentence (filled by Syntax Layer)
        head_id: ID of syntactic head (filled by Syntax Layer)
        dependencies: IDs of syntactic dependents
        metadata: Additional metadata
    
    Examples:
        >>> # From C2B output
        >>> word = WordForm(
        ...     surface="الْكِتَابُ",
        ...     span=Span(0, 10),
        ...     pos=PartOfSpeech.NOUN,
        ...     case=Case.NOMINATIVE,
        ...     definiteness=True
        ... )
        >>> print(word.surface)
        الْكِتَابُ
        >>> print(word.case.arabic)
        مرفوع
    """
    
    # Surface form
    surface: str
    span: Span
    
    # Morphological analysis (from C2B)
    root: Optional[Root] = None
    pattern: Optional[Pattern] = None
    affixes: Optional[Affixes] = None
    
    # Part of speech
    pos: PartOfSpeech = PartOfSpeech.UNKNOWN
    
    # Morphological features
    case: Case = Case.UNKNOWN
    definiteness: bool = False
    number: Number = Number.UNKNOWN
    gender: Gender = Gender.UNKNOWN
    
    # Syntactic features (filled by Syntax Layer)
    syntax_role: Optional[SyntaxRole] = None
    head_id: Optional[int] = None
    dependencies: List[int] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Unique ID (assigned by builder)
    word_id: Optional[int] = None
    
    def __post_init__(self):
        """Validate and normalize after initialization"""
        # Ensure dependencies is a list
        if self.dependencies is None:
            object.__setattr__(self, 'dependencies', [])
    
    @property
    def is_noun(self) -> bool:
        """Check if word is a noun"""
        return self.pos == PartOfSpeech.NOUN
    
    @property
    def is_verb(self) -> bool:
        """Check if word is a verb"""
        return self.pos == PartOfSpeech.VERB
    
    @property
    def is_particle(self) -> bool:
        """Check if word is a particle"""
        return self.pos == PartOfSpeech.PARTICLE
    
    @property
    def is_definite(self) -> bool:
        """Check if word is definite"""
        return self.definiteness
    
    @property
    def has_root(self) -> bool:
        """Check if word has root"""
        return self.root is not None
    
    @property
    def has_pattern(self) -> bool:
        """Check if word has pattern"""
        return self.pattern is not None
    
    @property
    def has_syntax_role(self) -> bool:
        """Check if syntax role is assigned"""
        return self.syntax_role is not None and self.syntax_role != SyntaxRole.UNKNOWN
    
    def agrees_with(self, other: 'WordForm', features: List[str]) -> bool:
        """
        Check if this word agrees with another in specified features
        
        Args:
            other: Another WordForm
            features: List of features to check ('number', 'gender', 'case')
        
        Returns:
            True if all specified features agree
        
        Examples:
            >>> word1 = WordForm(surface="الكتاب", span=Span(0, 6),
            ...                  number=Number.SINGULAR, gender=Gender.MASCULINE)
            >>> word2 = WordForm(surface="الجديد", span=Span(7, 13),
            ...                  number=Number.SINGULAR, gender=Gender.MASCULINE)
            >>> word1.agrees_with(word2, ['number', 'gender'])
            True
        """
        for feature in features:
            if feature == 'number' and self.number != other.number:
                if self.number != Number.UNKNOWN and other.number != Number.UNKNOWN:
                    return False
            elif feature == 'gender' and self.gender != other.gender:
                if self.gender != Gender.UNKNOWN and other.gender != Gender.UNKNOWN:
                    return False
            elif feature == 'case' and self.case != other.case:
                if self.case != Case.UNKNOWN and other.case != Case.UNKNOWN:
                    return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation
        
        Returns:
            Dictionary with all fields
        """
        return {
            'word_id': self.word_id,
            'surface': self.surface,
            'span': {'start': self.span.start, 'end': self.span.end},
            'root': self.root.formatted if self.root else None,
            'pattern': str(self.pattern) if self.pattern else None,
            'affixes': {
                'prefix': self.affixes.prefix if self.affixes else None,
                'suffix': self.affixes.suffix if self.affixes else None
            } if self.affixes else None,
            'pos': str(self.pos),
            'case': str(self.case),
            'definiteness': self.definiteness,
            'number': str(self.number),
            'gender': str(self.gender),
            'syntax_role': str(self.syntax_role) if self.syntax_role else None,
            'head_id': self.head_id,
            'dependencies': self.dependencies,
            'metadata': self.metadata
        }
    
    def __str__(self):
        return f"WordForm('{self.surface}', {self.pos}, {self.case})"
    
    def __repr__(self):
        return (f"WordForm(surface='{self.surface}', pos={self.pos}, "
                f"case={self.case}, syntax_role={self.syntax_role})")
