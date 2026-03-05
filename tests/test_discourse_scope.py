"""
Tests for FractalHub Graph Engine - Discourse/Scope Features

These tests verify:
1. Iltizam requires bridge with sufficient strength
2. Scope specialization operators work correctly
3. Gate authorization is enforced
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from graph_engine import GraphEngine, OperationStatus


class TestIltizamRequiresBridge:
    """Test that iltizam denotation requires a bridge with sufficient strength"""
    
    def test_iltizam_fails_without_bridge(self):
        """Iltizam should fail when no bridge exists"""
        engine = GraphEngine()
        
        # Create word and concept
        word = engine.create_node('word', {
            'surface_form': 'test_word',
            'syntactic_role': 'mubtada',
            'case_ending': 'marfou3',
            'gender': 'mudhakkar',
            'number': 'mufrad'
        })
        
        concept = engine.create_node('concept', {
            'meaning_id': 'test_concept',
            'semantic_features': {}
        })
        
        # Authorize gate
        engine.authorize_gate('denotation_gate')
        
        # Try to apply iltizam without bridge - should fail
        success, audit = engine.apply_operator(
            'denotation_iltizam',
            word.node_id,
            concept.node_id,
            gate_id='denotation_gate'
        )
        
        assert not success
        assert audit.status == OperationStatus.FAILURE
        assert 'bridge' in audit.error_message.lower() or any(
            'bridge' in c['message'].lower() 
            for c in audit.constraints_checked if not c['passed']
        )
    
    def test_iltizam_fails_with_weak_bridge(self):
        """Iltizam should fail when bridge strength is below threshold"""
        engine = GraphEngine()
        
        # Create word and concept
        word = engine.create_node('word', {
            'surface_form': 'test_word',
            'syntactic_role': 'mubtada',
            'case_ending': 'marfou3',
            'gender': 'mudhakkar',
            'number': 'mufrad'
        })
        
        concept = engine.create_node('concept', {
            'meaning_id': 'test_concept',
            'semantic_features': {}
        })
        
        # Create weak bridge (below threshold of 0.7)
        bridge = engine.create_node('bridge', {
            'bridge_type': 'presupposition',
            'bridge_strength': 0.5,
            'source_id': word.node_id,
            'target_id': concept.node_id
        })
        
        # Authorize gate
        engine.authorize_gate('denotation_gate')
        
        # Try to apply iltizam with weak bridge - should fail
        success, audit = engine.apply_operator(
            'denotation_iltizam',
            word.node_id,
            concept.node_id,
            gate_id='denotation_gate'
        )
        
        assert not success
        assert audit.status == OperationStatus.FAILURE
    
    def test_iltizam_succeeds_with_strong_bridge(self):
        """Iltizam should succeed when bridge has sufficient strength"""
        engine = GraphEngine()
        
        # Create word and concept
        word = engine.create_node('word', {
            'surface_form': 'test_word',
            'syntactic_role': 'mubtada',
            'case_ending': 'marfou3',
            'gender': 'mudhakkar',
            'number': 'mufrad'
        })
        
        concept = engine.create_node('concept', {
            'meaning_id': 'test_concept',
            'semantic_features': {}
        })
        
        # Create strong bridge (above threshold of 0.7)
        bridge = engine.create_node('bridge', {
            'bridge_type': 'entailment',
            'bridge_strength': 0.85,
            'source_id': word.node_id,
            'target_id': concept.node_id
        })
        
        # Authorize gate
        engine.authorize_gate('denotation_gate')
        
        # Apply iltizam with strong bridge - should succeed
        success, audit = engine.apply_operator(
            'denotation_iltizam',
            word.node_id,
            concept.node_id,
            gate_id='denotation_gate'
        )
        
        assert success
        assert audit.status == OperationStatus.SUCCESS


class TestScopeSpecialization:
    """Test scope specialization operators"""
    
    def test_scope_specialization_by_condition(self):
        """Test scope specialization with condition operator"""
        engine = GraphEngine()
        
        # Create scope and condition nodes
        scope = engine.create_node('scope', {
            'scope_type': 'general',
            'truth_apt': True
        })
        
        condition = engine.create_node('condition', {
            'cond_type': 'if_then',
            'condition_content': 'إذا توفر الشرط'
        })
        
        # Authorize gate
        engine.authorize_gate('scope_gate')
        
        # Apply condition operator
        success, audit = engine.apply_operator(
            'scope_if_then',
            condition.node_id,
            scope.node_id,
            gate_id='scope_gate'
        )
        
        assert success
        assert audit.status == OperationStatus.SUCCESS
        assert audit.operator_name == 'scope_if_then'
        assert len(audit.effects_applied) > 0
    
    def test_scope_specialization_by_goal_boundary(self):
        """Test scope specialization with goal boundary operator"""
        engine = GraphEngine()
        
        # Create scope and goal nodes
        scope = engine.create_node('scope', {
            'scope_type': 'general',
            'truth_apt': True
        })
        
        goal = engine.create_node('goal', {
            'goal_type': 'boundary',
            'goal_content': 'حتى النهاية'
        })
        
        # Authorize gate
        engine.authorize_gate('scope_gate')
        
        # Apply goal boundary operator
        success, audit = engine.apply_operator(
            'scope_goal_boundary',
            goal.node_id,
            scope.node_id,
            gate_id='scope_gate'
        )
        
        assert success
        assert audit.status == OperationStatus.SUCCESS
        assert audit.operator_name == 'scope_goal_boundary'
    
    def test_scope_specialization_by_goal_purpose(self):
        """Test scope specialization with goal purpose operator"""
        engine = GraphEngine()
        
        # Create scope and goal nodes
        scope = engine.create_node('scope', {
            'scope_type': 'general',
            'truth_apt': True
        })
        
        goal = engine.create_node('goal', {
            'goal_type': 'purpose',
            'goal_content': 'لكي نحقق الهدف'
        })
        
        # Authorize gate
        engine.authorize_gate('scope_gate')
        
        # Apply goal purpose operator
        success, audit = engine.apply_operator(
            'scope_goal_purpose',
            goal.node_id,
            scope.node_id,
            gate_id='scope_gate'
        )
        
        assert success
        assert audit.status == OperationStatus.SUCCESS
        assert audit.operator_name == 'scope_goal_purpose'
    
    def test_scope_specialization_by_number(self):
        """Test scope specialization with number operator"""
        engine = GraphEngine()
        
        # Create scope and number nodes
        scope = engine.create_node('scope', {
            'scope_type': 'general',
            'truth_apt': True
        })
        
        number = engine.create_node('number', {
            'number_value': 5,
            'number_type': 'exact'
        })
        
        # Authorize gate
        engine.authorize_gate('scope_gate')
        
        # Apply number operator
        success, audit = engine.apply_operator(
            'scope_counts',
            number.node_id,
            scope.node_id,
            gate_id='scope_gate'
        )
        
        assert success
        assert audit.status == OperationStatus.SUCCESS
        assert audit.operator_name == 'scope_counts'
    
    def test_scope_specialization_by_exception(self):
        """Test scope specialization with exception operator"""
        engine = GraphEngine()
        
        # Create scope and exception nodes
        scope = engine.create_node('scope', {
            'scope_type': 'general',
            'truth_apt': True
        })
        
        exception = engine.create_node('exception', {
            'exception_type': 'illa',
            'exception_content': 'إلا واحداً'
        })
        
        # Authorize gate
        engine.authorize_gate('scope_gate')
        
        # Apply exception operator
        success, audit = engine.apply_operator(
            'scope_except',
            exception.node_id,
            scope.node_id,
            gate_id='scope_gate'
        )
        
        assert success
        assert audit.status == OperationStatus.SUCCESS
        assert audit.operator_name == 'scope_except'
    
    def test_all_specializations_in_sequence(self):
        """Test applying all specialization operators to the same scope"""
        engine = GraphEngine()
        
        # Create scope node
        scope = engine.create_node('scope', {
            'scope_type': 'general',
            'truth_apt': True
        })
        
        # Create all specialization nodes
        quantifier = engine.create_node('quantifier', {'quant_type': 'specific', 'domain': 'test'})
        restrictor = engine.create_node('restrictor', {'restrict_type': 'adjective', 'restriction_content': 'test'})
        condition = engine.create_node('condition', {'cond_type': 'if_then', 'condition_content': 'test'})
        goal = engine.create_node('goal', {'goal_type': 'purpose', 'goal_content': 'test'})
        number = engine.create_node('number', {'number_value': 3, 'number_type': 'exact'})
        exception = engine.create_node('exception', {'exception_type': 'illa', 'exception_content': 'test'})
        
        # Authorize gate
        engine.authorize_gate('scope_gate')
        
        # Apply all operators
        ops = [
            ('scope_quantify', quantifier.node_id),
            ('scope_restrict', restrictor.node_id),
            ('scope_if_then', condition.node_id),
            ('scope_goal_purpose', goal.node_id),
            ('scope_counts', number.node_id),
            ('scope_except', exception.node_id)
        ]
        
        for op_name, source_id in ops:
            success, audit = engine.apply_operator(op_name, source_id, scope.node_id, gate_id='scope_gate')
            assert success, f"{op_name} failed"
            assert audit.operator_name == op_name
        
        # Check audit trail
        scope_audits = [e for e in engine.audit_trail if e.operator_name.startswith('scope_')]
        assert len(scope_audits) == 6


class TestNoMutationWithoutGate:
    """Test that gate authorization is enforced for new operators"""
    
    def test_scope_operator_requires_gate(self):
        """Scope operators should require gate authorization"""
        engine = GraphEngine()
        
        scope = engine.create_node('scope', {'scope_type': 'general', 'truth_apt': True})
        quantifier = engine.create_node('quantifier', {'quant_type': 'specific', 'domain': 'test'})
        
        # Try without gate - should fail
        success, audit = engine.apply_operator('scope_quantify', quantifier.node_id, scope.node_id)
        
        assert not success
        assert audit.status == OperationStatus.FAILURE
        assert 'gate' in audit.error_message.lower() or any(
            'gate' in c['message'].lower()
            for c in audit.constraints_checked if not c['passed']
        )
    
    def test_denotation_operator_requires_gate(self):
        """Denotation operators should require gate authorization"""
        engine = GraphEngine()
        
        word = engine.create_node('word', {
            'surface_form': 'test',
            'syntactic_role': 'mubtada',
            'case_ending': 'marfou3',
            'gender': 'mudhakkar',
            'number': 'mufrad'
        })
        concept = engine.create_node('concept', {'meaning_id': 'test', 'semantic_features': {}})
        
        # Try without gate - should fail
        success, audit = engine.apply_operator('denotation_mutabaqa', word.node_id, concept.node_id)
        
        assert not success
        assert audit.status == OperationStatus.FAILURE
        assert 'gate' in audit.error_message.lower() or any(
            'gate' in c['message'].lower()
            for c in audit.constraints_checked if not c['passed']
        )


class TestPropositionExport:
    """Test proposition export functionality"""
    
    def test_proposition_export_structure(self):
        """Test that proposition export has correct structure"""
        engine = GraphEngine()
        
        # Create some scope elements
        scope = engine.create_node('scope', {'scope_type': 'specific', 'truth_apt': True})
        quantifier = engine.create_node('quantifier', {'quant_type': 'specific', 'domain': 'test'})
        number = engine.create_node('number', {'number_value': 2, 'number_type': 'exact'})
        
        # Export proposition
        proposition = engine.export_proposition('/tmp/test_proposition.json')
        
        # Verify structure
        assert 'truth_apt' in proposition
        assert 'quantifiers' in proposition
        assert 'restrictors' in proposition
        assert 'conditions' in proposition
        assert 'goals' in proposition
        assert 'numbers' in proposition
        assert 'exceptions' in proposition
        assert 'denotation_modes_used' in proposition
        
        # Verify counts
        assert proposition['scope_count'] == 1
        assert len(proposition['quantifiers']) == 1
        assert len(proposition['numbers']) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
