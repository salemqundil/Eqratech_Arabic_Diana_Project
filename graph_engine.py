#!/usr/bin/env python3
"""
Graph Engine for FractalHub Linguistic Analysis

This engine implements a graph-based system for Arabic linguistic analysis
following the spaces_edges_operators_v01.yaml specification. It provides:
- Node creation in different linguistic spaces
- Operator application with constraint checking
- Gate-based authorization for critical operations
- Comprehensive audit trail for all operations
"""

import yaml
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json


class OperationStatus(Enum):
    """Status of an operation"""
    SUCCESS = "success"
    FAILURE = "failure"
    WARNING = "warning"


@dataclass
class Node:
    """Represents a node in the linguistic graph"""
    node_id: str
    node_type: str
    space: str
    attributes: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_attribute(self, name: str, default=None):
        """Get node attribute with default value"""
        return self.attributes.get(name, default)
    
    def set_attribute(self, name: str, value: Any):
        """Set node attribute"""
        self.attributes[name] = value
    
    def to_dict(self):
        """Convert node to dictionary"""
        return {
            'node_id': self.node_id,
            'node_type': self.node_type,
            'space': self.space,
            'attributes': self.attributes,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class Edge:
    """Represents an edge (operator application) in the graph"""
    edge_id: str
    operator_name: str
    source_node_id: Optional[str]
    target_node_id: str
    space: str
    status: OperationStatus
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self):
        """Convert edge to dictionary"""
        return {
            'edge_id': self.edge_id,
            'operator_name': self.operator_name,
            'source_node_id': self.source_node_id,
            'target_node_id': self.target_node_id,
            'space': self.space,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class AuditEntry:
    """Represents an audit trail entry"""
    operation_id: str
    timestamp: datetime
    operator_name: str
    source_node_id: Optional[str]
    target_node_id: str
    space: str
    status: OperationStatus
    preconditions_met: List[str] = field(default_factory=list)
    constraints_checked: List[Dict[str, Any]] = field(default_factory=list)
    effects_applied: List[str] = field(default_factory=list)
    gate_authorization: Optional[str] = None
    exception_declared: Optional[str] = None
    validation_result: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self):
        """Convert audit entry to dictionary"""
        return {
            'operation_id': self.operation_id,
            'timestamp': self.timestamp.isoformat(),
            'operator_name': self.operator_name,
            'source_node_id': self.source_node_id,
            'target_node_id': self.target_node_id,
            'space': self.space,
            'status': self.status.value,
            'preconditions_met': self.preconditions_met,
            'constraints_checked': self.constraints_checked,
            'effects_applied': self.effects_applied,
            'gate_authorization': self.gate_authorization,
            'exception_declared': self.exception_declared,
            'validation_result': self.validation_result,
            'error_message': self.error_message,
            'metadata': self.metadata
        }


class GraphEngine:
    """Main graph engine for linguistic analysis"""
    
    def __init__(self, config_path: str = "spaces_edges_operators_v01.yaml"):
        """Initialize the graph engine with configuration"""
        self.config = self._load_config(config_path)
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}
        self.audit_trail: List[AuditEntry] = []
        self.gates_authorized: Dict[str, bool] = {}
        self.exceptions_declared: Dict[str, bool] = {}
        
    def _load_config(self, path: str) -> Dict:
        """Load configuration from YAML file"""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def create_node(self, node_type: str, attributes: Dict[str, Any]) -> Optional[Node]:
        """
        Create a new node in the graph
        
        Args:
            node_type: Type of node (must be defined in config)
            attributes: Node attributes
            
        Returns:
            Created node or None if validation fails
        """
        # Validate node type
        if node_type not in self.config['node_types']:
            print(f"Error: Unknown node type '{node_type}'")
            return None
        
        node_spec = self.config['node_types'][node_type]
        space = node_spec['space']
        
        # Validate required attributes
        for attr_spec in node_spec['attributes']:
            if attr_spec.get('required', False) and attr_spec['name'] not in attributes:
                print(f"Error: Missing required attribute '{attr_spec['name']}'")
                return None
        
        # Create node
        node_id = str(uuid.uuid4())
        node = Node(
            node_id=node_id,
            node_type=node_type,
            space=space,
            attributes=attributes
        )
        self.nodes[node_id] = node
        
        print(f"✓ Created {node_type} node {node_id[:8]} in {space} space")
        return node
    
    def apply_operator(
        self,
        operator_name: str,
        source_node_id: Optional[str],
        target_node_id: str,
        gate_id: Optional[str] = None,
        exception_id: Optional[str] = None
    ) -> Tuple[bool, AuditEntry]:
        """
        Apply an operator (create an edge) between nodes
        
        Args:
            operator_name: Name of operator to apply
            source_node_id: Source node ID (None for creation operators)
            target_node_id: Target node ID
            gate_id: Gate authorization ID if required
            exception_id: Exception ID if exception applies
            
        Returns:
            Tuple of (success, audit_entry)
        """
        operation_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        # Validate operator exists
        if operator_name not in self.config['operators']:
            error_msg = f"Unknown operator '{operator_name}'"
            print(f"✗ {error_msg}")
            audit = AuditEntry(
                operation_id=operation_id,
                timestamp=timestamp,
                operator_name=operator_name,
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                space="unknown",
                status=OperationStatus.FAILURE,
                error_message=error_msg
            )
            self.audit_trail.append(audit)
            return False, audit
        
        operator = self.config['operators'][operator_name]
        space = operator['space']
        
        # Get nodes
        source_node = self.nodes.get(source_node_id) if source_node_id else None
        target_node = self.nodes.get(target_node_id)
        
        if not target_node:
            error_msg = f"Target node {target_node_id} not found"
            print(f"✗ {error_msg}")
            audit = AuditEntry(
                operation_id=operation_id,
                timestamp=timestamp,
                operator_name=operator_name,
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                space=space,
                status=OperationStatus.FAILURE,
                error_message=error_msg
            )
            self.audit_trail.append(audit)
            return False, audit
        
        # Use the new validation method
        can_apply, preconditions_met, constraints_checked = self.validate_operator_application(
            operator_name, operator, source_node, target_node, gate_id, exception_id
        )
        
        if not can_apply:
            # Find the failed constraint/precondition
            error_msg = "Validation failed"
            if constraints_checked:
                failed = [c for c in constraints_checked if not c['passed']]
                if failed:
                    error_msg = f"Constraint '{failed[0]['name']}' failed: {failed[0]['message']}"
            
            print(f"✗ {error_msg}")
            audit = AuditEntry(
                operation_id=operation_id,
                timestamp=timestamp,
                operator_name=operator_name,
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                space=space,
                status=OperationStatus.FAILURE,
                preconditions_met=preconditions_met,
                constraints_checked=constraints_checked,
                error_message=error_msg
            )
            self.audit_trail.append(audit)
            return False, audit
        
        # Apply effects
        effects_applied = []
        if 'effects' in operator:
            for effect in operator['effects']:
                effects_applied.append(effect)
                # Apply effect logic here (simplified)
        
        # Apply rules
        if 'rules' in operator:
            for rule in operator['rules']:
                # Simplified rule application
                if 'effect' in rule:
                    for key, value in rule['effect'].items():
                        target_node.set_attribute(key, value)
                        effects_applied.append(f"set_{key}={value}")
        
        # Create edge
        edge_id = str(uuid.uuid4())
        edge = Edge(
            edge_id=edge_id,
            operator_name=operator_name,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            space=space,
            status=OperationStatus.SUCCESS
        )
        self.edges[edge_id] = edge
        
        # Create audit entry
        audit = AuditEntry(
            operation_id=operation_id,
            timestamp=timestamp,
            operator_name=operator_name,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            space=space,
            status=OperationStatus.SUCCESS,
            preconditions_met=preconditions_met,
            constraints_checked=constraints_checked,
            effects_applied=effects_applied,
            gate_authorization=gate_id,
            exception_declared=exception_id,
            validation_result="passed"
        )
        self.audit_trail.append(audit)
        
        print(f"✓ Applied {operator_name} from {source_node_id[:8] if source_node_id else 'null'} to {target_node_id[:8]}")
        return True, audit
    
    def authorize_gate(self, gate_id: str):
        """Authorize a gate for operations"""
        self.gates_authorized[gate_id] = True
        print(f"✓ Gate {gate_id} authorized")
    
    def declare_exception(self, exception_id: str):
        """Declare an exception (e.g., for CC clusters in loanwords)"""
        self.exceptions_declared[exception_id] = True
        print(f"✓ Exception {exception_id} declared")
    
    def get_audit_trail(self, filters: Optional[Dict[str, Any]] = None) -> List[AuditEntry]:
        """Get audit trail with optional filters"""
        if not filters:
            return self.audit_trail
        
        filtered = self.audit_trail
        if 'operator_name' in filters:
            filtered = [e for e in filtered if e.operator_name == filters['operator_name']]
        if 'space' in filters:
            filtered = [e for e in filtered if e.space == filters['space']]
        if 'status' in filters:
            filtered = [e for e in filtered if e.status.value == filters['status']]
        
        return filtered
    
    def export_audit_trail(self, filename: str = "audit_trail.json"):
        """Export audit trail to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([e.to_dict() for e in self.audit_trail], f, indent=2, ensure_ascii=False)
        print(f"✓ Exported audit trail to {filename}")
    
    def export_graph(self, filename: str = "graph.json"):
        """Export graph structure to JSON file"""
        graph_data = {
            'nodes': [n.to_dict() for n in self.nodes.values()],
            'edges': [e.to_dict() for e in self.edges.values()]
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Exported graph to {filename}")
    
    def check_bridge_exists(self, source_id: str, target_id: str) -> Tuple[bool, float]:
        """
        Check if a bridge edge exists between source and target nodes
        
        Returns:
            Tuple of (exists, strength)
        """
        # Check if there's a bridge node connecting these nodes
        for node in self.nodes.values():
            if node.node_type == 'bridge':
                if (node.get_attribute('source_id') == source_id and 
                    node.get_attribute('target_id') == target_id):
                    strength = node.get_attribute('bridge_strength', 0.0)
                    return True, strength
        
        # Also check edges with bridge metadata
        for edge in self.edges.values():
            if (edge.source_node_id == source_id and 
                edge.target_node_id == target_id and
                'bridge_strength' in edge.metadata):
                return True, edge.metadata['bridge_strength']
        
        return False, 0.0
    
    def validate_operator_application(
        self,
        operator_name: str,
        operator: Dict,
        source_node: Optional[Node],
        target_node: Node,
        gate_id: Optional[str],
        exception_id: Optional[str]
    ) -> Tuple[bool, List[str], List[Dict]]:
        """
        Validate if an operator can be applied
        
        Returns:
            Tuple of (can_apply, preconditions_met, constraints_checked)
        """
        preconditions_met = []
        constraints_checked = []
        
        # Check gate requirements
        if operator.get('gate_required', False):
            gate_type = operator.get('gate_type', 'UNKNOWN')
            if gate_id and self.gates_authorized.get(gate_id, False):
                preconditions_met.append(f"gate_{gate_type}_authorized: {gate_id}")
            else:
                return False, preconditions_met, [{
                    'name': 'gate_required',
                    'passed': False,
                    'message': f"Gate {gate_type} authorization required but not provided"
                }]
        
        # Check preconditions
        if 'preconditions' in operator:
            for precond in operator['preconditions']:
                if precond == "gate_authorization_required":
                    continue  # Already handled above
                elif precond == "bridge_exists_and_strong":
                    # Special handling for iltizam
                    if source_node:
                        exists, strength = self.check_bridge_exists(source_node.node_id, target_node.node_id)
                        threshold = self.config['parameters'].get('bridge_threshold', 0.7)
                        if exists and strength >= threshold:
                            preconditions_met.append(f"bridge_exists_and_strong: {strength:.2f} >= {threshold}")
                        else:
                            return False, preconditions_met, [{
                                'name': 'bridge_exists_and_strong',
                                'passed': False,
                                'message': f"Bridge {'does not exist' if not exists else f'too weak ({strength:.2f} < {threshold})'}"
                            }]
                else:
                    preconditions_met.append(precond)
        
        # Check constraints
        if 'constraints' in operator:
            for constraint in operator['constraints']:
                constraint_result = {
                    'name': constraint['name'],
                    'passed': True,
                    'message': ''
                }
                
                # Handle different constraint types
                if constraint['name'] == 'iltizam_requires_bridge':
                    if source_node:
                        exists, strength = self.check_bridge_exists(source_node.node_id, target_node.node_id)
                        threshold = constraint.get('threshold', 0.7)
                        if not exists or strength < threshold:
                            constraint_result['passed'] = False
                            constraint_result['message'] = f"Bridge required for iltizam (exists={exists}, strength={strength:.2f}, threshold={threshold})"
                
                elif constraint['name'] == 'bridge_edge_exists':
                    if source_node:
                        exists, _ = self.check_bridge_exists(source_node.node_id, target_node.node_id)
                        if not exists:
                            constraint_result['passed'] = False
                            constraint_result['message'] = "Bridge edge does not exist"
                
                elif constraint['name'] == 'no_cc_cluster':
                    # Original CC cluster check
                    if source_node and target_node:
                        src_cons = source_node.get_attribute('consonant_code', 0)
                        tgt_cons = target_node.get_attribute('consonant_code', 0)
                        src_vowel = source_node.get_attribute('vowel_code', 0)
                        tgt_vowel = target_node.get_attribute('vowel_code', 0)
                        
                        is_cc_cluster = (
                            src_cons != 0 and tgt_cons != 0 and
                            src_vowel in [0, 1] and tgt_vowel in [0, 1]
                        )
                        
                        if is_cc_cluster:
                            if exception_id and self.exceptions_declared.get(exception_id, False):
                                constraint_result['passed'] = True
                                constraint_result['message'] = f"CC cluster allowed by exception {exception_id}"
                            else:
                                constraint_result['passed'] = False
                                constraint_result['message'] = "CC cluster detected without exception"
                
                constraints_checked.append(constraint_result)
                
                if not constraint_result['passed']:
                    return False, preconditions_met, constraints_checked
        
        return True, preconditions_met, constraints_checked
    
    def export_proposition(self, filename: str = "proposition.json"):
        """
        Export proposition/utterance content with denotation analysis
        """
        # Collect scope information
        scope_nodes = [n for n in self.nodes.values() if n.node_type == 'scope']
        quantifiers = [n for n in self.nodes.values() if n.node_type == 'quantifier']
        restrictors = [n for n in self.nodes.values() if n.node_type == 'restrictor']
        conditions = [n for n in self.nodes.values() if n.node_type == 'condition']
        goals = [n for n in self.nodes.values() if n.node_type == 'goal']
        numbers = [n for n in self.nodes.values() if n.node_type == 'number']
        exceptions = [n for n in self.nodes.values() if n.node_type == 'exception']
        claims = [n for n in self.nodes.values() if n.node_type == 'claim']
        
        # Collect denotation modes used
        denotation_modes = set()
        for entry in self.audit_trail:
            if entry.operator_name.startswith('denotation_'):
                mode = entry.operator_name.replace('denotation_', '')
                if entry.status == OperationStatus.SUCCESS:
                    denotation_modes.add(mode)
        
        # Determine truth_apt
        truth_apt = True
        if scope_nodes:
            truth_apt = scope_nodes[0].get_attribute('truth_apt', True)
        elif claims:
            truth_apt = claims[0].get_attribute('truth_apt', True)
        
        proposition = {
            'truth_apt': truth_apt,
            'quantifiers': [{'id': q.node_id, 'type': q.get_attribute('quant_type')} for q in quantifiers],
            'restrictors': [{'id': r.node_id, 'type': r.get_attribute('restrict_type')} for r in restrictors],
            'conditions': [{'id': c.node_id, 'type': c.get_attribute('cond_type')} for c in conditions],
            'goals': [{'id': g.node_id, 'type': g.get_attribute('goal_type')} for g in goals],
            'numbers': [{'id': n.node_id, 'value': n.get_attribute('number_value')} for n in numbers],
            'exceptions': [{'id': e.node_id, 'type': e.get_attribute('exception_type')} for e in exceptions],
            'denotation_modes_used': list(denotation_modes),
            'scope_count': len(scope_nodes),
            'claim_count': len(claims)
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(proposition, f, indent=2, ensure_ascii=False)
        print(f"✓ Exported proposition to {filename}")
        
        return proposition
    
    def print_summary(self):
        """Print summary of graph state"""
        print("\n" + "="*60)
        print("GRAPH ENGINE SUMMARY")
        print("="*60)
        print(f"Nodes: {len(self.nodes)}")
        for space in set(n.space for n in self.nodes.values()):
            count = sum(1 for n in self.nodes.values() if n.space == space)
            print(f"  - {space}: {count}")
        print(f"Edges: {len(self.edges)}")
        print(f"Audit entries: {len(self.audit_trail)}")
        
        success = sum(1 for e in self.audit_trail if e.status == OperationStatus.SUCCESS)
        failure = sum(1 for e in self.audit_trail if e.status == OperationStatus.FAILURE)
        print(f"  - Success: {success}")
        print(f"  - Failure: {failure}")
        print("="*60)


def example_phonological_analysis():
    """Example: Phonological analysis with CC onset checking"""
    print("\n" + "="*60)
    print("EXAMPLE: Phonological Analysis")
    print("="*60 + "\n")
    
    engine = GraphEngine()
    
    # Create position tokens
    token1 = engine.create_node('position_token', {
        'consonant_code': 10,  # Some consonant
        'vowel_code': 1,       # SUKUN
        'position_index': 0
    })
    
    token2 = engine.create_node('position_token', {
        'consonant_code': 15,  # Another consonant
        'vowel_code': 1,       # SUKUN
        'position_index': 1
    })
    
    token3 = engine.create_node('position_token', {
        'consonant_code': 20,  # Another consonant
        'vowel_code': 2,       # FATHA
        'position_index': 2
    })
    
    # Try to apply onset check between token1 and token2 (should fail - CC cluster)
    print("\n--- Testing CC onset constraint ---")
    success, _ = engine.apply_operator(
        'phono_onset_check',
        token1.node_id,
        token2.node_id
    )
    
    # Declare exception and try again
    if not success:
        print("\n--- Declaring exception for loanword ---")
        engine.declare_exception('loanword_exception_1')
        success, _ = engine.apply_operator(
            'phono_onset_check',
            token1.node_id,
            token2.node_id,
            exception_id='loanword_exception_1'
        )
    
    # Apply onset check between token2 and token3 (should succeed - has vowel)
    print("\n--- Testing valid onset ---")
    engine.apply_operator(
        'phono_onset_check',
        token2.node_id,
        token3.node_id
    )
    
    engine.print_summary()
    engine.export_audit_trail('phonology_audit.json')


def example_morphological_derivation():
    """Example: Morphological derivation with gate constraints"""
    print("\n" + "="*60)
    print("EXAMPLE: Morphological Derivation")
    print("="*60 + "\n")
    
    engine = GraphEngine()
    
    # Try to create morpheme without gate authorization (should fail)
    print("--- Attempting to create morpheme without gate ---")
    morpheme = engine.create_node('morpheme', {
        'root_consonants': [10, 15, 20],
        'pattern_id': 'fa3ala',
        'form_number': 1
    })
    
    # Authorize gate and create morpheme
    print("\n--- Authorizing root gate ---")
    engine.authorize_gate('root_gate_1')
    
    success, _ = engine.apply_operator(
        'morpho_root_gate',
        None,
        morpheme.node_id,
        gate_id='root_gate_1'
    )
    
    # Apply pattern
    if success:
        print("\n--- Applying pattern ---")
        engine.authorize_gate('pattern_gate_1')
        engine.apply_operator(
            'morpho_pattern_application',
            morpheme.node_id,
            morpheme.node_id,
            gate_id='pattern_gate_1'
        )
    
    engine.print_summary()
    engine.export_audit_trail('morphology_audit.json')


def demo_scope_and_denotation():
    """Example: Scope construction and denotation with bridge constraints"""
    print("\n" + "="*60)
    print("DEMO: Scope and Denotation Analysis")
    print("="*60 + "\n")
    
    engine = GraphEngine()
    
    # Create word and concept nodes
    word1 = engine.create_node('word', {
        'surface_form': 'كتاب',
        'syntactic_role': 'mubtada',
        'case_ending': 'marfou3',
        'gender': 'mudhakkar',
        'number': 'mufrad'
    })
    
    concept1 = engine.create_node('concept', {
        'meaning_id': 'book_concept',
        'semantic_features': {'category': 'object', 'type': 'reading_material'}
    })
    
    # Create scope node
    scope1 = engine.create_node('scope', {
        'scope_type': 'specific',
        'quant_scope': 'specific',
        'restrict_scope': 'restricted',
        'truth_apt': True
    })
    
    # Create quantifier
    quantifier1 = engine.create_node('quantifier', {
        'quant_type': 'specific',
        'domain': 'books'
    })
    
    # Create restrictor
    restrictor1 = engine.create_node('restrictor', {
        'restrict_type': 'adjective',
        'restriction_content': 'الكبير'
    })
    
    # Create condition
    condition1 = engine.create_node('condition', {
        'cond_type': 'if_then',
        'condition_content': 'إذا كان متاحاً'
    })
    
    # Create goal (purpose)
    goal1 = engine.create_node('goal', {
        'goal_type': 'purpose',
        'goal_content': 'لكي نقرأه'
    })
    
    # Create number
    number1 = engine.create_node('number', {
        'number_value': 3,
        'number_type': 'exact'
    })
    
    # Create exception
    exception1 = engine.create_node('exception', {
        'exception_type': 'illa',
        'exception_content': 'إلا القديم'
    })
    
    print("--- Building scope graph ---")
    
    # Authorize SCOPE_GATE
    engine.authorize_gate('scope_gate_1')
    
    # Apply scope operators
    engine.apply_operator('scope_quantify', quantifier1.node_id, scope1.node_id, gate_id='scope_gate_1')
    engine.apply_operator('scope_restrict', restrictor1.node_id, scope1.node_id, gate_id='scope_gate_1')
    engine.apply_operator('scope_if_then', condition1.node_id, scope1.node_id, gate_id='scope_gate_1')
    engine.apply_operator('scope_goal_purpose', goal1.node_id, scope1.node_id, gate_id='scope_gate_1')
    engine.apply_operator('scope_counts', number1.node_id, scope1.node_id, gate_id='scope_gate_1')
    engine.apply_operator('scope_except', exception1.node_id, scope1.node_id, gate_id='scope_gate_1')
    
    print("\n--- Testing denotation modes ---")
    
    # Authorize DENOTATION_GATE
    engine.authorize_gate('denotation_gate_1')
    
    # Test mutabaqa (direct matching) - should succeed
    print("\n1. Testing mutabaqa (direct matching):")
    engine.apply_operator('denotation_mutabaqa', word1.node_id, concept1.node_id, gate_id='denotation_gate_1')
    
    # Test tadammun (inclusion) - should succeed
    print("\n2. Testing tadammun (inclusion):")
    concept2 = engine.create_node('concept', {
        'meaning_id': 'literature_concept',
        'semantic_features': {'category': 'abstract', 'includes': 'books'}
    })
    engine.apply_operator('denotation_tadammun', word1.node_id, concept2.node_id, gate_id='denotation_gate_1')
    
    # Test iltizam without bridge - should fail
    print("\n3. Testing iltizam WITHOUT bridge (should fail):")
    concept3 = engine.create_node('concept', {
        'meaning_id': 'knowledge_concept',
        'semantic_features': {'category': 'abstract', 'related_to': 'books'}
    })
    success, audit = engine.apply_operator('denotation_iltizam', word1.node_id, concept3.node_id, gate_id='denotation_gate_1')
    
    # Create bridge and test iltizam again - should succeed
    print("\n4. Creating bridge and testing iltizam again:")
    bridge1 = engine.create_node('bridge', {
        'bridge_type': 'entailment',
        'bridge_strength': 0.85,
        'source_id': word1.node_id,
        'target_id': concept3.node_id
    })
    
    success, audit = engine.apply_operator('denotation_iltizam', word1.node_id, concept3.node_id, gate_id='denotation_gate_1')
    
    # Test iltizam with weak bridge - should fail
    print("\n5. Testing iltizam with WEAK bridge (should fail):")
    concept4 = engine.create_node('concept', {
        'meaning_id': 'wisdom_concept',
        'semantic_features': {'category': 'abstract'}
    })
    bridge2 = engine.create_node('bridge', {
        'bridge_type': 'presupposition',
        'bridge_strength': 0.5,  # Below threshold
        'source_id': word1.node_id,
        'target_id': concept4.node_id
    })
    success, audit = engine.apply_operator('denotation_iltizam', word1.node_id, concept4.node_id, gate_id='denotation_gate_1')
    
    # Export proposition
    print("\n--- Exporting proposition ---")
    proposition = engine.export_proposition('proposition.json')
    print(f"\nProposition summary:")
    print(f"  Truth-apt: {proposition['truth_apt']}")
    print(f"  Quantifiers: {len(proposition['quantifiers'])}")
    print(f"  Restrictors: {len(proposition['restrictors'])}")
    print(f"  Conditions: {len(proposition['conditions'])}")
    print(f"  Goals: {len(proposition['goals'])}")
    print(f"  Numbers: {len(proposition['numbers'])}")
    print(f"  Exceptions: {len(proposition['exceptions'])}")
    print(f"  Denotation modes used: {', '.join(proposition['denotation_modes_used'])}")
    
    engine.print_summary()
    engine.export_audit_trail('scope_denotation_audit.json')
    engine.export_graph('scope_denotation_graph.json')


if __name__ == "__main__":
    print("FractalHub Graph Engine")
    print("=" * 60)
    
    # Run examples
    example_phonological_analysis()
    example_morphological_derivation()
    demo_scope_and_denotation()
    
    print("\n✓ All examples completed")
    print("Check audit trail files for detailed operation logs:")
    print("  - phonology_audit.json")
    print("  - morphology_audit.json")
    print("  - scope_denotation_audit.json")
    print("  - proposition.json")
    print("  - scope_denotation_graph.json")
