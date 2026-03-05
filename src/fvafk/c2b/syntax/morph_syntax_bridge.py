"""
Morph-Syntax Bridge - Infer syntax from morphology + context.

Author: Hussein Hiyassat
Date: 2026-02-21
Sprint: 4 - Task 4.3
"""

from typing import List, Optional, Tuple

from ..morphology_flags import MorphologyFlags
from .syntax_features import SyntaxFeatures
from .mappings import SYNTACTIC_ROLE_MAPPING, I3RAB_TYPE_MAPPING_REVERSE


class MorphSyntaxBridge:
    """
    Infer I3rab type and syntax features from morphology + context.

    Applies a small set of deterministic rules that cover the most
    frequent constructions in Arabic.  Each rule returns an (i3rab_type_en,
    confidence) pair; a confidence of 0.0 signals "no prediction".

    Examples:
        >>> from fvafk.c2b.morphology_flags import MorphologyFlags
        >>> bridge = MorphSyntaxBridge()
        >>> morph = MorphologyFlags(case="nominative", definiteness=True, confidence=0.9)
        >>> i3rab, conf = bridge.infer_i3rab_type(morph, [], 0)
        >>> i3rab
        "mubtada"
        >>> conf
        0.8
    """

    def infer_i3rab_type(
        self,
        morph: MorphologyFlags,
        context: List,
        position: int,
    ) -> Tuple[Optional[str], float]:
        """
        Infer I3rab type from morphology flags and sentence context.

        Args:
            morph: MorphologyFlags for the word being analysed.
            context: List of WordForm / MorphologyFlags for the full
                sentence (used for context-sensitive rules).
            position: Zero-based word index within the sentence.

        Returns:
            (i3rab_type_en, confidence) tuple.
            i3rab_type_en is None when no rule fires.

        Rules (in priority order):
            1. Definite nominative at position 0 → مبتدأ  (mubtada)
            2. Nominative after sentence start with verb → فاعل  (fa'il)
            3. Indefinite accusative after verb → مفعول به  (maf'ul_bihi)
            4. Genitive after preposition → مجرور  (majrur)
            5. Nominative (catch-all) → خبر  (khabar)
        """
        if morph is None:
            return None, 0.0

        # Rule 1: Definite noun in nominative at sentence start → mubtada
        if (
            morph.definiteness
            and morph.case == "nominative"
            and position == 0
        ):
            return "mubtada", 0.8

        # Rule 2: Nominative noun after a verb (position > 0) → fa'il
        if (
            morph.case == "nominative"
            and position > 0
            and self._after_verb(context, position)
        ):
            return "fa'il", 0.75

        # Rule 3: Accusative (indefinite) after a verb → maf'ul_bihi
        if (
            morph.case == "accusative"
            and not morph.definiteness
            and self._after_verb(context, position)
        ):
            return "maf'ul_bihi", 0.7

        # Rule 4: Genitive after preposition → majrur
        if morph.case == "genitive" and self._after_preposition(context, position):
            return "majrur", 0.9

        # Rule 5: Nominative (fallback) → khabar (predicate of nominal sentence)
        if morph.case == "nominative" and position > 0:
            return "khabar", 0.5

        return None, 0.0

    def predict_syntax(
        self,
        morph: MorphologyFlags,
        context: List,
        position: int,
    ) -> SyntaxFeatures:
        """
        Generate a SyntaxFeatures prediction for a word.

        Args:
            morph: MorphologyFlags for the word.
            context: Surrounding words (list of MorphologyFlags or similar).
            position: Position of the word in the sentence.

        Returns:
            SyntaxFeatures object with predicted fields.
        """
        i3rab_type_en, conf = self.infer_i3rab_type(morph, context, position)

        # Map to Arabic label
        i3rab_type_ar = (
            I3RAB_TYPE_MAPPING_REVERSE.get(i3rab_type_en, "غير معروف")
            if i3rab_type_en
            else "غير معروف"
        )

        # Derive syntactic role
        syntactic_role = SYNTACTIC_ROLE_MAPPING.get(i3rab_type_en, "unknown")

        # Case string (default to empty string if None)
        case_str = morph.case if morph and morph.case else "unknown"

        return SyntaxFeatures(
            syntactic_role=syntactic_role,
            case=case_str,
            i3rab_type_ar=i3rab_type_ar,
            i3rab_type_en=i3rab_type_en or "unknown",
            confidence=conf,
        )

    # ------------------------------------------------------------------
    # Context helpers
    # ------------------------------------------------------------------

    def _after_verb(self, context: List, position: int) -> bool:
        """Return True if there is a verb somewhere before *position*."""
        if not context:
            return False
        for i in range(min(position, len(context))):
            item = context[i]
            # Support both MorphologyFlags and objects with .pos attribute
            pos = getattr(item, "pos", None)
            if pos == "verb":
                return True
        return False

    def _after_preposition(self, context: List, position: int) -> bool:
        """Return True if the immediately preceding token is a preposition."""
        if not context or position == 0:
            return False
        prev_index = position - 1
        if prev_index >= len(context):
            return False
        item = context[prev_index]
        pos = getattr(item, "pos", None)
        return pos == "particle"
