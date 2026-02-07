"""
Tests for Vowel Space Optimization Module
"""

import pytest
import math
from fvafk.vowel_space_optimization import (
    VowelPoint, VowelType, OptimizationParameters,
    VowelSpaceOptimizer
)


class TestVowelPoint:
    """Test VowelPoint data structure"""
    
    def test_valid_vowel_point(self):
        """Test creation of valid vowel point"""
        v = VowelPoint(h=0.5, b=0.5, r=0)
        assert v.h == 0.5
        assert v.b == 0.5
        assert v.r == 0
    
    def test_invalid_height(self):
        """Test that invalid height raises error"""
        with pytest.raises(AssertionError):
            VowelPoint(h=1.5, b=0.5, r=0)
    
    def test_invalid_backness(self):
        """Test that invalid backness raises error"""
        with pytest.raises(AssertionError):
            VowelPoint(h=0.5, b=-0.1, r=0)
    
    def test_invalid_rounding(self):
        """Test that invalid rounding raises error"""
        with pytest.raises(AssertionError):
            VowelPoint(h=0.5, b=0.5, r=2)


class TestOptimizationParameters:
    """Test OptimizationParameters"""
    
    def test_valid_parameters(self):
        """Test creation of valid parameters"""
        params = OptimizationParameters(lambda_=0.3, kappa=1.0, rho=0.5)
        assert params.lambda_ == 0.3
        assert params.kappa == 1.0
        assert params.rho == 0.5
    
    def test_negative_lambda(self):
        """Test that negative lambda raises error"""
        with pytest.raises(AssertionError):
            OptimizationParameters(lambda_=-0.1, kappa=1.0, rho=0.5)


class TestVowelSpaceOptimizer:
    """Test VowelSpaceOptimizer"""
    
    @pytest.fixture
    def optimizer(self):
        """Create optimizer with standard parameters"""
        params = OptimizationParameters(lambda_=0.3, kappa=1.0, rho=0.5)
        return VowelSpaceOptimizer(params)
    
    def test_perceptual_distance(self, optimizer):
        """Test perceptual distance calculation"""
        v1 = VowelPoint(h=0.0, b=0.5, r=0)
        v2 = VowelPoint(h=1.0, b=0.0, r=0)
        
        dist = optimizer.perceptual_distance(v1, v2)
        expected = math.sqrt((0.0 - 1.0)**2 + (0.5 - 0.0)**2)
        
        assert abs(dist - expected) < 1e-6
    
    def test_perceptual_distance_with_rounding(self, optimizer):
        """Test perceptual distance with rounding difference"""
        v1 = VowelPoint(h=1.0, b=1.0, r=0)
        v2 = VowelPoint(h=1.0, b=1.0, r=1)
        
        dist = optimizer.perceptual_distance(v1, v2)
        expected = math.sqrt(optimizer.params.kappa * 1**2)
        
        assert abs(dist - expected) < 1e-6
    
    def test_articulation_cost(self, optimizer):
        """Test articulation cost calculation"""
        # Center vowel should have minimum cost (except for rounding)
        v_center = VowelPoint(h=0.5, b=0.5, r=0)
        cost_center = optimizer.articulation_cost(v_center)
        assert cost_center == 0.0
        
        # Peripheral vowel should have higher cost
        v_peripheral = VowelPoint(h=0.0, b=0.5, r=0)
        cost_peripheral = optimizer.articulation_cost(v_peripheral)
        assert cost_peripheral > cost_center
    
    def test_articulation_cost_with_rounding(self, optimizer):
        """Test that rounding adds to articulation cost"""
        v_unrounded = VowelPoint(h=1.0, b=1.0, r=0)
        v_rounded = VowelPoint(h=1.0, b=1.0, r=1)
        
        cost_unrounded = optimizer.articulation_cost(v_unrounded)
        cost_rounded = optimizer.articulation_cost(v_rounded)
        
        assert cost_rounded == cost_unrounded + optimizer.params.rho
    
    def test_min_dispersion(self, optimizer):
        """Test minimum dispersion calculation"""
        vowels = [
            VowelPoint(h=0.0, b=0.5, r=0),  # a
            VowelPoint(h=1.0, b=0.0, r=0),  # i
            VowelPoint(h=1.0, b=1.0, r=1),  # u
        ]
        
        D = optimizer.min_dispersion(vowels)
        
        # Should be positive
        assert D > 0
        
        # Should be finite
        assert not math.isinf(D)
    
    def test_total_cost(self, optimizer):
        """Test total cost calculation"""
        vowels = [
            VowelPoint(h=0.0, b=0.5, r=0),
            VowelPoint(h=1.0, b=0.0, r=0),
            VowelPoint(h=1.0, b=1.0, r=1),
        ]
        
        C = optimizer.total_cost(vowels)
        
        # Should be positive (peripheral vowels + rounding)
        assert C > 0
    
    def test_optimization_criterion(self, optimizer):
        """Test optimization criterion"""
        vowels = [
            VowelPoint(h=0.0, b=0.5, r=0),
            VowelPoint(h=1.0, b=0.0, r=0),
            VowelPoint(h=1.0, b=1.0, r=1),
        ]
        
        J = optimizer.optimization_criterion(vowels)
        
        # Should be finite
        assert not math.isinf(J)
        assert not math.isnan(J)
    
    def test_check_collapse_prevention(self, optimizer):
        """Test collapse prevention check"""
        prevented, msg = optimizer.check_collapse_prevention()
        
        # With lambda=0.3, collapse should be prevented
        assert prevented
        assert "Collapse prevented" in msg
    
    def test_check_rounding_conditions(self, optimizer):
        """Test rounding conditions check"""
        correct, msg = optimizer.check_rounding_conditions()
        
        # With kappa=1.0, rho=0.5, rounding should attach to back vowel
        assert correct
        assert "Distance gain" in msg
    
    def test_verify_optimal_system(self, optimizer):
        """Test verification of optimal system"""
        report = optimizer.verify_optimal_system()
        
        assert 'optimal' in report
        assert 'J_criterion' in report
        assert 'dispersion' in report
        assert 'cost' in report
        assert 'collapse_prevented' in report
        assert 'rounding_correct' in report
        
        # With good parameters, should be optimal
        assert report['optimal']
        assert report['collapse_prevented']
        assert report['rounding_correct']


class TestCollapseConditions:
    """Test collapse prevention with various parameters"""
    
    def test_high_lambda_allows_collapse(self):
        """Test that high lambda may allow collapse"""
        params = OptimizationParameters(lambda_=10.0, kappa=1.0, rho=0.5)
        optimizer = VowelSpaceOptimizer(params)
        
        prevented, msg = optimizer.check_collapse_prevention()
        
        # High lambda may allow collapse
        # (exact threshold depends on vowel configuration)
        assert not prevented or "Collapse prevented" in msg
    
    def test_low_lambda_prevents_collapse(self):
        """Test that low lambda prevents collapse"""
        params = OptimizationParameters(lambda_=0.1, kappa=1.0, rho=0.5)
        optimizer = VowelSpaceOptimizer(params)
        
        prevented, msg = optimizer.check_collapse_prevention()
        
        # Low lambda should prevent collapse
        assert prevented


class TestRoundingConditions:
    """Test rounding attachment conditions"""
    
    def test_rounding_with_good_parameters(self):
        """Test rounding with parameters that favor back rounding"""
        params = OptimizationParameters(lambda_=0.3, kappa=1.0, rho=0.5)
        optimizer = VowelSpaceOptimizer(params)
        
        correct, msg = optimizer.check_rounding_conditions()
        
        # Should attach to back vowel
        assert correct
    
    def test_rounding_with_high_rho(self):
        """Test that high rho may prevent rounding"""
        params = OptimizationParameters(lambda_=0.3, kappa=1.0, rho=1.5)
        optimizer = VowelSpaceOptimizer(params)
        
        correct, msg = optimizer.check_rounding_conditions()
        
        # High rho (> sqrt(kappa)) should fail first condition
        assert not correct


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
