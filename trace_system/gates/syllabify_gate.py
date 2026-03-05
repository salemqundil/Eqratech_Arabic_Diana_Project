"""
SyllabifyGate - Syllable Segmentation with Weight Assignment

Implements T-01 to T-06 rules for Arabic syllabification:
- T-01: CV (Light)
- T-02: CVC (Heavy)
- T-03: CVV (Heavy)
- T-04: CVVC/CVCC (Superheavy)
- T-05: Forbidden patterns (VV, VVC, *CCC)
- T-06: Transition balance (HEAVY-LIGHT-HEAVY preferred)

Reference: gates_schema.json
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum


class PhonemeType(Enum):
    """Phoneme type: Consonant or Vowel"""
    C = "C"
    V = "V"


class SyllableType(Enum):
    """Canonical Arabic syllable types"""
    CV = "CV"           # Light: ma, bi
    CVC = "CVC"         # Heavy: man, bil
    CVV = "CVV"         # Heavy: maa, bii
    CVVC = "CVVC"       # Superheavy: maan, biil
    CVCC = "CVCC"       # Superheavy: bint, qalb
    CVVCV = "CVVCV"     # Extended (word-final): maalu
    CVVCCV = "CVVCCV"   # Extended (word-final): maalkum


class SyllableWeight(Enum):
    """Syllable weight for prosodic analysis"""
    LIGHT = "LIGHT"           # CV
    HEAVY = "HEAVY"           # CVC, CVV
    SUPERHEAVY = "SUPERHEAVY" # CVVC, CVCC


class TransitionDecision(Enum):
    """Syllable boundary transition decision"""
    KEEP = "keep"       # Transition accepted
    REPAIR = "repair"   # Needs phonological repair
    REJECT = "reject"   # Invalid transition


class GateStatus(Enum):
    """Gate execution status"""
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class Phoneme:
    """Single phoneme with type and features"""
    type: PhonemeType
    sym: str
    features: List[str]
    
    @property
    def is_consonant(self) -> bool:
        return self.type == PhonemeType.C
    
    @property
    def is_vowel(self) -> bool:
        return self.type == PhonemeType.V
    
    @property
    def is_long_vowel(self) -> bool:
        """Check if vowel is long (VF_LN_002)"""
        return self.is_vowel and "VF_LN_002" in self.features


@dataclass
class Syllable:
    """Syllable structure with onset, nucleus, coda"""
    type: SyllableType
    onset: Optional[str]      # Can be empty in rare cases
    nucleus: str              # Always present
    coda: Optional[str]       # Optional
    weight: SyllableWeight
    feature_id: str           # Reference to feature_enums.json
    
    def __str__(self) -> str:
        parts = []
        if self.onset:
            parts.append(f"C({self.onset})")
        parts.append(f"V({self.nucleus})")
        if self.coda:
            parts.append(f"C({self.coda})")
        return "".join(parts)


@dataclass
class TokenSyllabification:
    """Syllabification result for one token"""
    token_id: int
    syllables: List[Syllable]
    
    @property
    def syllable_count(self) -> int:
        return len(self.syllables)
    
    @property
    def total_weight(self) -> int:
        """Compute total weight (L=1, H=2, SH=3)"""
        weight_map = {
            SyllableWeight.LIGHT: 1,
            SyllableWeight.HEAVY: 2,
            SyllableWeight.SUPERHEAVY: 3
        }
        return sum(weight_map[s.weight] for s in self.syllables)


@dataclass
class Transition:
    """Syllable boundary transition between tokens"""
    between: Dict[str, int]  # {"from_token": 0, "to_token": 1}
    pattern: Dict[str, str]  # {"left": "CVC", "right": "CV"}
    decision: TransitionDecision
    notes: List[str] = field(default_factory=list)


@dataclass
class SyllabifyInput:
    """Input to SyllabifyGate"""
    phoneme_stream: List[Dict[str, Any]]  # List of token phoneme data


@dataclass
class SyllabifyOutput:
    """Output from SyllabifyGate"""
    syllabification: List[TokenSyllabification]
    transitions: List[Transition]
    status: GateStatus
    warnings: List[str] = field(default_factory=list)


class SyllabifyGate:
    """
    Syllabification Gate - Converts phoneme stream to syllable structures
    
    Rules:
    - T-01: CV → LIGHT (single consonant + short vowel)
    - T-02: CVC → HEAVY (consonant + vowel + consonant)
    - T-03: CVV → HEAVY (consonant + long vowel)
    - T-04: CVVC/CVCC → SUPERHEAVY (double coda or long+coda)
    - T-05: Forbidden patterns (VV onset, VVC onset, CCC coda)
    - T-06: Transition balance (prefer alternating weights)
    """
    
    # Feature IDs from feature_enums.json
    SYLLABLE_TYPE_IDS = {
        SyllableType.CV: "SY_TP_001",
        SyllableType.CVC: "SY_TP_002",
        SyllableType.CVV: "SY_TP_003",
        SyllableType.CVVC: "SY_TP_004",
        SyllableType.CVCC: "SY_TP_005",
        SyllableType.CVVCV: "SY_TP_006",
        SyllableType.CVVCCV: "SY_TP_007"
    }
    
    def __init__(self):
        self.rule_id = "SYLLABIFY-GATE-01"
        self.version = "1.0.0"
    
    def apply(self, input_data: SyllabifyInput) -> SyllabifyOutput:
        """
        Main entry point - syllabify all tokens in phoneme stream
        
        Args:
            input_data: SyllabifyInput with phoneme_stream
            
        Returns:
            SyllabifyOutput with syllabification + transitions + status
        """
        syllabification = []
        warnings = []
        
        # Process each token
        for token_data in input_data.phoneme_stream:
            token_id = token_data['token_id']
            phonemes_raw = token_data['phonemes']
            
            # Convert to Phoneme objects
            phonemes = [
                Phoneme(
                    type=PhonemeType(p['type']),
                    sym=p['sym'],
                    features=p['features']
                )
                for p in phonemes_raw
            ]
            
            # Syllabify this token
            try:
                syllables = self._syllabify_token(phonemes)
                syllabification.append(TokenSyllabification(
                    token_id=token_id,
                    syllables=syllables
                ))
            except ValueError as e:
                warnings.append(f"Token {token_id}: {str(e)}")
                syllabification.append(TokenSyllabification(
                    token_id=token_id,
                    syllables=[]
                ))
        
        # Compute transitions between tokens
        transitions = self._compute_transitions(syllabification)
        
        # Determine status
        status = GateStatus.OK if not warnings else GateStatus.WARNING
        
        return SyllabifyOutput(
            syllabification=syllabification,
            transitions=transitions,
            status=status,
            warnings=warnings
        )
    
    def _syllabify_token(self, phonemes: List[Phoneme]) -> List[Syllable]:
        """
        Syllabify a single token's phoneme sequence
        
        Strategy:
        1. Scan left-to-right
        2. Greedy onset maximization (attach consonants to following vowel)
        3. Coda attachment (post-nucleus consonants)
        4. Weight assignment based on structure
        
        Args:
            phonemes: List of Phoneme objects
            
        Returns:
            List of Syllable objects
            
        Raises:
            ValueError: If phoneme sequence is invalid
        """
        if not phonemes:
            raise ValueError("Empty phoneme sequence")
        
        syllables = []
        i = 0
        n = len(phonemes)
        
        while i < n:
            # Rule T-05: Cannot start with vowel in non-initial position
            if i > 0 and phonemes[i].is_vowel:
                raise ValueError(f"Invalid: vowel at position {i} without onset")
            
            # Extract onset (consonants before nucleus)
            onset_consonants = []
            while i < n and phonemes[i].is_consonant:
                onset_consonants.append(phonemes[i].sym)
                i += 1
            
            if i >= n:
                raise ValueError("Syllable ended without nucleus")
            
            # Extract nucleus (vowel sequence)
            nucleus_vowels = []
            while i < n and phonemes[i].is_vowel:
                nucleus_vowels.append(phonemes[i])
                i += 1
            
            if not nucleus_vowels:
                raise ValueError(f"No nucleus at position {i}")
            
            # Determine nucleus type (short vs long)
            is_long_nucleus = any(v.is_long_vowel for v in nucleus_vowels) or len(nucleus_vowels) > 1
            nucleus_str = " ".join(v.sym for v in nucleus_vowels)
            
            # Extract coda (post-nucleus consonants)
            coda_consonants = []
            
            # Lookahead: how many consonants until next vowel?
            j = i
            consonant_cluster = []
            while j < n and phonemes[j].is_consonant:
                consonant_cluster.append(phonemes[j].sym)
                j += 1
            
            # Coda attachment rules:
            # - If at end: take all remaining consonants (up to 2 for CVCC)
            # - If followed by vowel: take 1 consonant if heavy nucleus, else 0
            # - Rule T-05: No more than 2 consonants in coda
            
            if j >= n:  # End of word
                max_coda = 2 if is_long_nucleus else 2
                coda_consonants = consonant_cluster[:max_coda]
                i += len(coda_consonants)
            else:  # Followed by another syllable
                if is_long_nucleus:
                    # Heavy nucleus: can take 1 coda (CVVC)
                    if len(consonant_cluster) >= 2:
                        coda_consonants = [consonant_cluster[0]]
                        i += 1
                    elif len(consonant_cluster) == 1:
                        # Ambiguous: prefer onset of next syllable (no coda)
                        pass
                else:
                    # Short nucleus: can take 1 coda (CVC)
                    if len(consonant_cluster) >= 2:
                        coda_consonants = [consonant_cluster[0]]
                        i += 1
                    else:
                        # Single consonant: prefer onset of next syllable
                        pass
            
            # Build syllable
            syllable = self._build_syllable(
                onset="".join(onset_consonants) if onset_consonants else None,
                nucleus=nucleus_str,
                coda="".join(coda_consonants) if coda_consonants else None,
                is_long_nucleus=is_long_nucleus
            )
            
            syllables.append(syllable)
        
        return syllables
    
    def _build_syllable(
        self,
        onset: Optional[str],
        nucleus: str,
        coda: Optional[str],
        is_long_nucleus: bool
    ) -> Syllable:
        """
        Build Syllable object with type and weight classification
        
        Rules:
        - T-01: CV → LIGHT
        - T-02: CVC → HEAVY
        - T-03: CVV → HEAVY
        - T-04: CVVC/CVCC → SUPERHEAVY
        
        Args:
            onset: Consonant string or None
            nucleus: Vowel string
            coda: Consonant string or None
            is_long_nucleus: Whether nucleus is long vowel
            
        Returns:
            Syllable object with type and weight
        """
        # Determine type
        has_onset = onset is not None
        has_coda = coda is not None
        coda_length = len(coda) if coda else 0
        
        if not has_coda:
            if is_long_nucleus:
                syll_type = SyllableType.CVV      # T-03
                weight = SyllableWeight.HEAVY
            else:
                syll_type = SyllableType.CV       # T-01
                weight = SyllableWeight.LIGHT
        elif coda_length == 1:
            if is_long_nucleus:
                syll_type = SyllableType.CVVC     # T-04
                weight = SyllableWeight.SUPERHEAVY
            else:
                syll_type = SyllableType.CVC      # T-02
                weight = SyllableWeight.HEAVY
        elif coda_length == 2:
            syll_type = SyllableType.CVCC         # T-04
            weight = SyllableWeight.SUPERHEAVY
        else:
            raise ValueError(f"Invalid coda length: {coda_length}")
        
        return Syllable(
            type=syll_type,
            onset=onset,
            nucleus=nucleus,
            coda=coda,
            weight=weight,
            feature_id=self.SYLLABLE_TYPE_IDS[syll_type]
        )
    
    def _compute_transitions(
        self,
        syllabification: List[TokenSyllabification]
    ) -> List[Transition]:
        """
        Compute transitions between token boundaries
        
        Rule T-06: Prefer alternating weight (HEAVY-LIGHT-HEAVY)
        
        Args:
            syllabification: List of TokenSyllabification
            
        Returns:
            List of Transition objects
        """
        transitions = []
        
        for i in range(len(syllabification) - 1):
            left_token = syllabification[i]
            right_token = syllabification[i + 1]
            
            if not left_token.syllables or not right_token.syllables:
                continue
            
            # Get rightmost syllable of left token
            left_syll = left_token.syllables[-1]
            # Get leftmost syllable of right token
            right_syll = right_token.syllables[0]
            
            # T-06: Check weight balance
            decision, notes = self._evaluate_transition(left_syll, right_syll)
            
            transitions.append(Transition(
                between={
                    "from_token": left_token.token_id,
                    "to_token": right_token.token_id
                },
                pattern={
                    "left": left_syll.type.value,
                    "right": right_syll.type.value
                },
                decision=decision,
                notes=notes
            ))
        
        return transitions
    
    def _evaluate_transition(
        self,
        left: Syllable,
        right: Syllable
    ) -> Tuple[TransitionDecision, List[str]]:
        """
        Evaluate transition quality between two syllables
        
        T-06: Balanced transitions preferred (HEAVY-LIGHT or LIGHT-HEAVY)
        
        Args:
            left: Left syllable
            right: Right syllable
            
        Returns:
            (decision, notes)
        """
        notes = []
        
        # Simple heuristic: check for problematic patterns
        # - SUPERHEAVY-SUPERHEAVY: warning (heavy clustering)
        # - Otherwise: keep
        
        if (left.weight == SyllableWeight.SUPERHEAVY and
            right.weight == SyllableWeight.SUPERHEAVY):
            notes.append("heavy_clustering")
            decision = TransitionDecision.KEEP  # Still valid, just marked
        else:
            notes.append("boundary_ok")
            decision = TransitionDecision.KEEP
        
        # Additional check: LIGHT-LIGHT sequences are fine in Arabic
        if (left.weight == SyllableWeight.LIGHT and
            right.weight == SyllableWeight.LIGHT):
            notes.append("light_sequence")
        
        return decision, notes


# Convenience function for direct usage
def syllabify_phoneme_stream(phoneme_stream: List[Dict[str, Any]]) -> SyllabifyOutput:
    """
    Convenience function to syllabify phoneme stream directly
    
    Args:
        phoneme_stream: List of token phoneme dictionaries
        
    Returns:
        SyllabifyOutput
        
    Example:
        >>> phoneme_stream = [
        ...     {
        ...         "token_id": 0,
        ...         "surface": "من",
        ...         "phonemes": [
        ...             {"type": "C", "sym": "m", "features": ["CF_PL_001"]},
        ...             {"type": "V", "sym": "a", "features": ["VF_LN_001"]},
        ...             {"type": "C", "sym": "n", "features": ["CF_PL_004"]}
        ...         ]
        ...     }
        ... ]
        >>> result = syllabify_phoneme_stream(phoneme_stream)
        >>> print(result.syllabification[0].syllables[0].type)
        SyllableType.CVC
    """
    gate = SyllabifyGate()
    input_data = SyllabifyInput(phoneme_stream=phoneme_stream)
    return gate.apply(input_data)
