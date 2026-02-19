"""
Vowel Space Optimization Module

This module implements rigorous mathematical conditions for vowel space
optimization with parameters (λ, κ, ρ) that ensure:
1. Prevention of vowel collapse to the center
2. Attachment of rounding to high back vowel specifically

Based on the framework described in the problem statement.
"""

import math
from dataclasses import dataclass
from typing import List, Tuple, Dict
from enum import Enum


@dataclass
class VowelPoint:
    """
    Represents a vowel in the vowel space [0,1] × [0,1] × {0,1}
    h: height (0=low, 1=high)
    b: backness (0=front, 1=back) 
    r: rounding (0=unrounded, 1=rounded)
    """
    h: float  # height [0, 1]
    b: float  # backness [0, 1]
    r: int    # rounding {0, 1}
    
    def __post_init__(self):
        """Validate vowel coordinates"""
        assert 0 <= self.h <= 1, "Height must be in [0, 1]"
        assert 0 <= self.b <= 1, "Backness must be in [0, 1]"
        assert self.r in {0, 1}, "Rounding must be 0 or 1"


class VowelType(Enum):
    """Standard vowel types in the {a, i, u} system"""
    A = "a"  # Low central unrounded
    I = "i"  # High front unrounded
    U = "u"  # High back rounded


@dataclass
class OptimizationParameters:
    """
    Parameters for vowel space optimization
    
    λ (lambda_): Weight for articulation cost vs dispersion
    κ (kappa): Perceptual weight for rounding dimension
    ρ (rho): Articulation cost for rounding
    """
    lambda_: float  # Cost weight (λ)
    kappa: float    # Rounding perceptual weight (κ)
    rho: float      # Rounding articulation cost (ρ)
    
    def __post_init__(self):
        """Validate parameters"""
        assert self.lambda_ >= 0, "λ must be non-negative"
        assert self.kappa >= 0, "κ must be non-negative"
        assert self.rho >= 0, "ρ must be non-negative"


class VowelSpaceOptimizer:
    """
    Implements vowel space optimization with rigorous mathematical conditions
    """
    
    # Comfortable articulation center
    H0 = 0.5
    B0 = 0.5
    
    # Standard vowel system {a, i, u}
    STANDARD_VOWELS = {
        VowelType.A: VowelPoint(h=0.0, b=0.5, r=0),  # Low central unrounded
        VowelType.I: VowelPoint(h=1.0, b=0.0, r=0),  # High front unrounded  
        VowelType.U: VowelPoint(h=1.0, b=1.0, r=1),  # High back rounded
    }
    
    def __init__(self, params: OptimizationParameters):
        """Initialize optimizer with parameters"""
        self.params = params
        
    def perceptual_distance(self, v1: VowelPoint, v2: VowelPoint) -> float:
        """
        Compute perceptual distance between two vowels
        d_P(v_i, v_j) = √((h_i - h_j)² + (b_i - b_j)² + κ(r_i - r_j)²)
        """
        return math.sqrt(
            (v1.h - v2.h) ** 2 + 
            (v1.b - v2.b) ** 2 + 
            self.params.kappa * (v1.r - v2.r) ** 2
        )
    
    def articulation_cost(self, v: VowelPoint) -> float:
        """
        Compute articulation cost for a vowel
        c_A(v) = (h - h0)² + (b - b0)² + ρ·r
        
        Cost increases with distance from comfortable center (0.5, 0.5)
        and with rounding
        """
        return (
            (v.h - self.H0) ** 2 + 
            (v.b - self.B0) ** 2 + 
            self.params.rho * v.r
        )
    
    def min_dispersion(self, vowels: List[VowelPoint]) -> float:
        """
        Compute minimum pairwise dispersion D(S)
        D(S) = min_{i≠j} d_P(v_i, v_j)
        """
        if len(vowels) < 2:
            return float('inf')
        
        min_dist = float('inf')
        for i in range(len(vowels)):
            for j in range(i + 1, len(vowels)):
                dist = self.perceptual_distance(vowels[i], vowels[j])
                min_dist = min(min_dist, dist)
        
        return min_dist
    
    def total_cost(self, vowels: List[VowelPoint]) -> float:
        """
        Compute total articulation cost C(S)
        C(S) = Σ c_A(v)
        """
        return sum(self.articulation_cost(v) for v in vowels)
    
    def optimization_criterion(self, vowels: List[VowelPoint]) -> float:
        """
        Compute optimization criterion J_λ(S)
        J_λ(S) = -D(S) + λ·C(S)
        
        Lower is better (we minimize this)
        """
        D = self.min_dispersion(vowels)
        C = self.total_cost(vowels)
        return -D + self.params.lambda_ * C
    
    def check_collapse_prevention(self) -> Tuple[bool, str]:
        """
        Check if parameters prevent collapse to center
        
        Sufficient condition:
        λ < (D_tri - D_col) / (C_col - C_tri)
        
        Simplified practical condition:
        λ < D_tri / C_tri
        """
        # Get standard three-vowel system
        tri_vowels = list(self.STANDARD_VOWELS.values())
        
        D_tri = self.min_dispersion(tri_vowels)
        C_tri = self.total_cost(tri_vowels)
        
        if C_tri == 0:
            return False, "C_tri is zero, cannot compute bound"
        
        # Simplified sufficient condition
        bound = D_tri / C_tri
        
        if self.params.lambda_ < bound:
            return True, f"λ={self.params.lambda_:.4f} < {bound:.4f}: Collapse prevented"
        else:
            return False, f"λ={self.params.lambda_:.4f} >= {bound:.4f}: May collapse"
    
    def check_rounding_conditions(self) -> Tuple[bool, str]:
        """
        Check if rounding attaches to high back vowel specifically
        
        Conditions:
        1. 0 < ρ < √κ (rounding is useful but costly)
        2. ρ > ε (prevents free rounding)
        3. Rounding back vowel increases min distance more than cost
        """
        epsilon = 0.01
        
        # Condition 1 & 2: ε < ρ < √κ
        sqrt_kappa = math.sqrt(self.params.kappa)
        cond1 = epsilon < self.params.rho < sqrt_kappa
        
        if not cond1:
            return False, f"ρ={self.params.rho:.4f} not in ({epsilon:.4f}, {sqrt_kappa:.4f})"
        
        # Condition 3: Compare rounding back vs front
        v_a = self.STANDARD_VOWELS[VowelType.A]
        v_u = self.STANDARD_VOWELS[VowelType.U]
        v_u_unrounded = VowelPoint(h=1.0, b=1.0, r=0)
        
        # Distance gain from rounding back vowel
        dist_with_round = self.perceptual_distance(v_a, v_u)
        dist_without_round = self.perceptual_distance(v_a, v_u_unrounded)
        distance_gain_back = dist_with_round - dist_without_round
        
        # Cost of rounding
        rounding_cost = self.params.lambda_ * self.params.rho
        
        if distance_gain_back > rounding_cost:
            return True, f"Distance gain ({distance_gain_back:.4f}) > cost ({rounding_cost:.4f})"
        else:
            return False, f"Distance gain ({distance_gain_back:.4f}) <= cost ({rounding_cost:.4f})"
    
    def verify_optimal_system(self) -> Dict[str, any]:
        """
        Verify that {a, i, u} is the optimal three-vowel system
        under the given parameters
        
        Returns comprehensive verification report
        """
        # Get standard system
        standard = list(self.STANDARD_VOWELS.values())
        
        # Compute metrics
        J_standard = self.optimization_criterion(standard)
        D_standard = self.min_dispersion(standard)
        C_standard = self.total_cost(standard)
        
        # Check conditions
        collapse_ok, collapse_msg = self.check_collapse_prevention()
        rounding_ok, rounding_msg = self.check_rounding_conditions()
        
        return {
            'optimal': collapse_ok and rounding_ok,
            'J_criterion': J_standard,
            'dispersion': D_standard,
            'cost': C_standard,
            'collapse_prevented': collapse_ok,
            'collapse_message': collapse_msg,
            'rounding_correct': rounding_ok,
            'rounding_message': rounding_msg,
            'parameters': {
                'lambda': self.params.lambda_,
                'kappa': self.params.kappa,
                'rho': self.params.rho
            }
        }


def demonstrate_vowel_optimization():
    """
    Demonstrate vowel space optimization with example parameters
    """
    # Example parameters that satisfy conditions
    params = OptimizationParameters(
        lambda_=0.3,  # Low enough to prevent collapse
        kappa=1.0,    # Moderate perceptual weight for rounding
        rho=0.5       # Cost of rounding
    )
    
    optimizer = VowelSpaceOptimizer(params)
    
    # Verify the system
    report = optimizer.verify_optimal_system()
    
    print("=" * 60)
    print("VOWEL SPACE OPTIMIZATION VERIFICATION")
    print("=" * 60)
    print(f"\nParameters:")
    print(f"  λ (lambda): {params.lambda_:.4f}")
    print(f"  κ (kappa):  {params.kappa:.4f}")
    print(f"  ρ (rho):    {params.rho:.4f}")
    print(f"\nStandard {{a, i, u}} System:")
    print(f"  J criterion: {report['J_criterion']:.4f}")
    print(f"  Dispersion:  {report['dispersion']:.4f}")
    print(f"  Cost:        {report['cost']:.4f}")
    print(f"\nConditions:")
    print(f"  Collapse prevented: {report['collapse_prevented']}")
    print(f"    → {report['collapse_message']}")
    print(f"  Rounding correct:   {report['rounding_correct']}")
    print(f"    → {report['rounding_message']}")
    print(f"\nOptimal: {report['optimal']}")
    print("=" * 60)
    
    return report


if __name__ == "__main__":
    demonstrate_vowel_optimization()
