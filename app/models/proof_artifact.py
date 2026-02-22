"""
Pydantic model for Coq proof artifacts

Represents formal verification artifacts from Coq proofs.
"""

from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum


class ProofStatus(str, Enum):
    """Status of a Coq proof"""
    PROVEN = "proven"        # Fully proven (Qed)
    ADMITTED = "admitted"    # Admitted temporarily
    FAILED = "failed"        # Proof failed
    UNKNOWN = "unknown"      # Status unknown


class ProofArtifact(BaseModel):
    """
    Coq proof artifact
    
    Attached to analysis results to provide formal verification evidence.
    
    Attributes:
        theorem_name: Name of the Coq theorem/lemma
        status: Proof status (proven, admitted, failed)
        coq_file: Path to .v file containing proof
        line_number: Line number in Coq file
        proof_term: Optional proof term (for proven theorems)
        dependencies: List of lemmas this proof depends on
        notes: Additional notes about the proof
    
    Examples:
        >>> artifact = ProofArtifact(
        ...     theorem_name="gate_sukun_preserves_length",
        ...     status=ProofStatus.PROVEN,
        ...     coq_file="coq/Gates/GateSukun.v",
        ...     line_number=42,
        ...     dependencies=["length_preservation"]
        ... )
        >>> artifact.status
        <ProofStatus.PROVEN: 'proven'>
    """
    
    theorem_name: str = Field(..., description="Coq theorem/lemma name")
    status: ProofStatus = Field(..., description="Proof status")
    coq_file: str = Field(..., description="Path to .v file")
    line_number: Optional[int] = Field(default=None, ge=1, description="Line number in file")
    proof_term: Optional[str] = Field(default=None, description="Proof term (if proven)")
    dependencies: List[str] = Field(default_factory=list, description="Dependent lemmas")
    notes: Optional[str] = Field(default=None, description="Additional notes")
    
    def is_safe(self) -> bool:
        """Check if proof is safe to rely on (proven, not admitted)"""
        return self.status == ProofStatus.PROVEN

    model_config = ConfigDict(
        use_enum_values=False,
        json_schema_extra={
            "example": {
                "theorem_name": "gate_sukun_preserves_length",
                "status": "proven",
                "coq_file": "coq/Gates/GateSukun.v",
                "line_number": 42,
                "proof_term": "exact (refl_equal _).",
                "dependencies": ["length_preservation"],
                "notes": "Verified 2026-02-15"
            }
        }
    )
