"""
OrthographyAdapter: Enhanced integration with FormCodecV2

Handles orthographic normalization rules for Arabic text, with full reversibility support.
Integrated with FormCodecV2 for encoding/decoding pipeline (Sprint 1, Task 1.4).

Features:
- Hamzat al-wasl (ٱ → ا)
- Taa marbuta (ة → ت)
- Alef maqsurah (ى → ي)
- Tanwin in waqf (ً/ٌ/ٍ → ن)
- Reversible encode/decode
- Integration with FormCodecV2
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fvafk.c1.form_codec_v2 import FormCodecV2, FormStream


# Orthography normalization rules (written → canonical)
ORTHOGRAPHY_RULES: List[Tuple[str, str, str]] = [
    # (source, target, description)
    ("ٱ", "ا", "hamzat_al_wasl"),      # Hamzat al-wasl → alef
    ("أ", "ا", "hamza_above_alef"),    # Hamza above alef → alef
    ("إ", "ا", "hamza_below_alef"),    # Hamza below alef → alef
    ("آ", "ا", "alef_madd"),           # Alef with madd → alef
    ("ة", "ت", "taa_marbuta"),         # Taa marbuta → taa
    ("ى", "ي", "alef_maqsurah"),       # Alef maqsurah → yaa
    ("ء", "ء", "hamza_isolated"),      # Keep isolated hamza
]

# Tanwin mapping (for waqf context)
TANWIN_MAP: Dict[str, str] = {
    "ً": "ن",  # Tanwin fath → nun
    "ٌ": "ن",  # Tanwin damm → nun
    "ٍ": "ن",  # Tanwin kasr → nun
}

# Arabic diacritics (harakat)
HARAKAT = {
    "َ",   # Fatha
    "ُ",   # Damma
    "ِ",   # Kasra
    "ْ",   # Sukun
    "ً",   # Tanwin fath
    "ٌ",   # Tanwin damm
    "ٍ",   # Tanwin kasr
    "ّ",   # Shadda
    "ٓ",   # Madda
    "ٰ",   # Superscript alef
    "ٖ",   # Kasra below
    "ٗ",   # Damma above
}


@dataclass
class OrthographyAdapter:
    """
    Enhanced OrthographyAdapter integrated with FormCodecV2
    
    Provides:
    - Normalization (written → canonical form)
    - Integration with FormCodecV2 for reversibility
    - Rule-based orthography mapping
    - Optional diacritic stripping
    
    Examples:
        >>> adapter = OrthographyAdapter()
        >>> adapter.normalize("ٱلْكِتَابُ")
        'الكتاب'
        
        >>> # With FormCodecV2 integration
        >>> codec = FormCodecV2()
        >>> stream = adapter.encode_with_normalization("ٱلْكِتَابُ", codec)
        >>> adapter.decode(stream, codec)
        'الكتاب'
    """
    
    keep_diacritics: bool = False
    apply_tanwin_waqf: bool = True
    apply_hamza_normalization: bool = True
    apply_taa_normalization: bool = True
    apply_alef_normalization: bool = True
    
    def normalize(self, text: str, strip_diacritics: bool = True) -> str:
        """
        Normalize Arabic text according to orthography rules
        
        Args:
            text: Input Arabic text
            strip_diacritics: Whether to remove diacritics
        
        Returns:
            Normalized text
        """
        result = text
        
        # Apply orthography rules
        for source, target, rule_type in ORTHOGRAPHY_RULES:
            if rule_type == "hamzat_al_wasl" and self.apply_hamza_normalization:
                result = result.replace(source, target)
            elif rule_type in ("hamza_above_alef", "hamza_below_alef", "alef_madd") and self.apply_hamza_normalization:
                result = result.replace(source, target)
            elif rule_type == "taa_marbuta" and self.apply_taa_normalization:
                result = result.replace(source, target)
            elif rule_type == "alef_maqsurah" and self.apply_alef_normalization:
                result = result.replace(source, target)
            elif rule_type == "hamza_isolated":
                # Keep isolated hamza as is
                pass
        
        # Apply tanwin in waqf context
        if self.apply_tanwin_waqf:
            result = self._collapse_tanwin(result)
        
        # Strip diacritics if requested
        if strip_diacritics or not self.keep_diacritics:
            result = self._strip_diacritics(result)
        
        return result
    
    def encode_with_normalization(
        self,
        text: str,
        codec: "FormCodecV2",
        normalize: bool = True
    ) -> "FormStream":
        """
        Encode text using FormCodecV2 with optional normalization
        
        Args:
            text: Input text
            codec: "FormCodecV2" instance
            normalize: Whether to apply normalization before encoding
        
        Returns:
            FormStream with encoded tokens
        """
        if normalize:
            text = self.normalize(text, strip_diacritics=not self.keep_diacritics)
        return codec.encode(text)
    
    def decode(self, stream: "FormStream", codec: "FormCodecV2") -> str:
        """
        Decode FormStream back to text
        
        Args:
            stream: "FormStream" from encoding
            codec: "FormCodecV2" instance
        
        Returns:
            Decoded text
        """
        return codec.decode(stream)
    
    def roundtrip_test(self, text: str, codec: "FormCodecV2") -> bool:
        """
        Test reversibility: decode(encode(text)) should equal normalized(text)
        
        Args:
            text: Input text
            codec: "FormCodecV2" instance
        
        Returns:
            True if roundtrip succeeds
        """
        normalized = self.normalize(text, strip_diacritics=not self.keep_diacritics)
        stream = codec.encode(normalized)
        decoded = codec.decode(stream)
        return decoded == normalized
    
    def _strip_diacritics(self, text: str) -> str:
        """Remove Arabic diacritics (harakat)"""
        return "".join(ch for ch in text if ch not in HARAKAT)
    
    def _collapse_tanwin(self, text: str) -> str:
        """Convert tanwin to nun (for waqf context)"""
        for symbol, replacement in TANWIN_MAP.items():
            text = text.replace(symbol, replacement)
        return text
    
    def get_rules_summary(self) -> Dict[str, bool]:
        """Get summary of active normalization rules"""
        return {
            "hamza_normalization": self.apply_hamza_normalization,
            "taa_normalization": self.apply_taa_normalization,
            "alef_normalization": self.apply_alef_normalization,
            "tanwin_waqf": self.apply_tanwin_waqf,
            "keep_diacritics": self.keep_diacritics,
        }
