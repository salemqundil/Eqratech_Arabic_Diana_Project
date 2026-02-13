"""
Hard Invariants Validators
فاحصات القوانين القاطعة

هذا الملف يوفر validators مستقلة لكل قانون قاطع
تُستخدم في:
1. مرحلة البناء (construction time)
2. مرحلة Minimization (لتعيين ∞ cost)
3. مرحلة Audit (للتحقق من صحة traces)
"""

from dataclasses import dataclass
from typing import List, Dict, Set, Optional
from enum import Enum, auto


# ═══════════════════════════════════════════════════════════════════════
# 1) نتائج الفحص
# ═══════════════════════════════════════════════════════════════════════

class ValidationResult(Enum):
    """نتيجة فحص"""
    PASS = auto()       # نجح الفحص
    FAIL = auto()       # فشل الفحص
    WARNING = auto()    # تحذير (ليس خطأ قاطع)


@dataclass
class InvariantViolation:
    """انتهاك قانون قاطع"""
    rule_id: str
    node_id: Optional[str]
    edge_id: Optional[str]
    message: str
    severity: str  # "FATAL" (∞ cost) | "ERROR" | "WARNING"
    
    def __repr__(self):
        return f"[{self.rule_id}] {self.severity}: {self.message}"


@dataclass
class ValidationReport:
    """تقرير شامل لفحص الرسم"""
    result: ValidationResult
    violations: List[InvariantViolation]
    warnings: List[str]
    passed_checks: List[str]
    
    def is_valid(self) -> bool:
        """هل الرسم صحيح؟"""
        return self.result == ValidationResult.PASS
    
    def has_fatal_violations(self) -> bool:
        """هل يوجد انتهاكات قاطعة (∞ cost)؟"""
        return any(v.severity == "FATAL" for v in self.violations)
    
    def get_cost(self) -> float:
        """حساب الكلفة (للاستخدام في E(x,y))"""
        if self.has_fatal_violations():
            return float('inf')
        return len(self.violations) * 10.0  # soft penalties


# ═══════════════════════════════════════════════════════════════════════
# 2) القانون 5.1: أدوات المعاني
# ═══════════════════════════════════════════════════════════════════════

class Ma3aniInvariantValidator:
    """
    فاحص القانون 5.1: أدوات المعاني لا تكتب Subject/Predicate
    
    الصيغة الرياضية:
    ∀ node ∈ nodes:
      if node.type = Ma3aniToolNode
      then ∀ writes:
        writes ∉ {J.subject, J.predicate}
    """
    
    RULE_ID = "INV_MA3ANI_5.1"
    
    @staticmethod
    def validate_node_capabilities(node_data: Dict) -> Optional[InvariantViolation]:
        """
        فحص 1: قدرات العقدة
        
        إذا كانت Ma3aniToolNode، تأكد أنها لا تملك:
        - CAN_WRITE_SUBJECT
        - CAN_WRITE_PREDICATE
        """
        if node_data.get("kind") != "Ma3aniToolNode":
            return None  # لا يطبق
        
        forbidden_caps = {"CAN_WRITE_SUBJECT", "CAN_WRITE_PREDICATE"}
        node_caps = set(node_data.get("capabilities", []))
        
        violations = forbidden_caps & node_caps
        if violations:
            return InvariantViolation(
                rule_id=Ma3aniInvariantValidator.RULE_ID,
                node_id=node_data.get("id"),
                edge_id=None,
                message=f"Ma3aniToolNode has forbidden capabilities: {violations}",
                severity="FATAL"
            )
        
        return None
    
    @staticmethod
    def validate_subject_write(edge_data: Dict, nodes_index: Dict) -> Optional[InvariantViolation]:
        """
        فحص 2: كتابة Subject
        
        إذا كان edge من نوع BUILDS_SUBJECT، تأكد أن from ليس Ma3aniToolNode
        """
        if edge_data.get("type") != "BUILDS_SUBJECT":
            return None
        
        from_id = edge_data.get("from")
        from_node = nodes_index.get(from_id)
        
        if not from_node:
            return InvariantViolation(
                rule_id=Ma3aniInvariantValidator.RULE_ID,
                node_id=from_id,
                edge_id=edge_data.get("id"),
                message=f"BUILDS_SUBJECT from unknown node: {from_id}",
                severity="ERROR"
            )
        
        if from_node.get("kind") == "Ma3aniToolNode":
            return InvariantViolation(
                rule_id=Ma3aniInvariantValidator.RULE_ID,
                node_id=from_id,
                edge_id=edge_data.get("id"),
                message=f"Ma3aniToolNode ({from_id}) cannot write Subject",
                severity="FATAL"
            )
        
        return None
    
    @staticmethod
    def validate_predicate_write(edge_data: Dict, nodes_index: Dict) -> Optional[InvariantViolation]:
        """
        فحص 3: كتابة Predicate
        
        إذا كان edge من نوع BUILDS_PREDICATE، تأكد أن from ليس Ma3aniToolNode
        """
        if edge_data.get("type") != "BUILDS_PREDICATE":
            return None
        
        from_id = edge_data.get("from")
        from_node = nodes_index.get(from_id)
        
        if not from_node:
            return InvariantViolation(
                rule_id=Ma3aniInvariantValidator.RULE_ID,
                node_id=from_id,
                edge_id=edge_data.get("id"),
                message=f"BUILDS_PREDICATE from unknown node: {from_id}",
                severity="ERROR"
            )
        
        if from_node.get("kind") == "Ma3aniToolNode":
            return InvariantViolation(
                rule_id=Ma3aniInvariantValidator.RULE_ID,
                node_id=from_id,
                edge_id=edge_data.get("id"),
                message=f"Ma3aniToolNode ({from_id}) cannot write Predicate",
                severity="FATAL"
            )
        
        return None
    
    @staticmethod
    def validate_judgment(judgment: Dict, nodes_index: Dict) -> List[InvariantViolation]:
        """
        فحص 4: الحكم J نفسه
        
        تأكد أن subject/predicate ليسا من Ma3aniToolNode
        """
        violations = []
        
        # فحص subject
        subj_id = judgment.get("subject")
        if subj_id:
            subj_node = nodes_index.get(subj_id)
            if subj_node and subj_node.get("kind") == "Ma3aniToolNode":
                violations.append(InvariantViolation(
                    rule_id=Ma3aniInvariantValidator.RULE_ID,
                    node_id=subj_id,
                    edge_id=None,
                    message=f"J.subject is Ma3aniToolNode: {subj_id}",
                    severity="FATAL"
                ))
        
        # فحص predicate
        pred_id = judgment.get("predicate")
        if pred_id:
            pred_node = nodes_index.get(pred_id)
            if pred_node and pred_node.get("kind") == "Ma3aniToolNode":
                violations.append(InvariantViolation(
                    rule_id=Ma3aniInvariantValidator.RULE_ID,
                    node_id=pred_id,
                    edge_id=None,
                    message=f"J.predicate is Ma3aniToolNode: {pred_id}",
                    severity="FATAL"
                ))
        
        return violations


# ═══════════════════════════════════════════════════════════════════════
# 3) القانون 5.2: المبنيات
# ═══════════════════════════════════════════════════════════════════════

class MabniInvariantValidator:
    """
    فاحص القانون 5.2: المبنيات لا تُعامل كجذر/صفة
    
    الصيغة الرياضية:
    ∀ node ∈ nodes:
      if node.type = MabniRefNode
      then ∀ instantiations:
        instantiation.type ∉ {RootNode, QualityRoot}
    """
    
    RULE_ID = "INV_MABNI_5.2"
    
    @staticmethod
    def validate_node_capabilities(node_data: Dict) -> Optional[InvariantViolation]:
        """
        فحص 1: قدرات العقدة
        
        إذا كانت MabniRefNode، تأكد أنها لا تملك:
        - CAN_INSTANTIATE_ROOT
        - CAN_INSTANTIATE_QUALITY
        """
        if node_data.get("kind") != "MabniRefNode":
            return None
        
        forbidden_caps = {"CAN_INSTANTIATE_ROOT", "CAN_INSTANTIATE_QUALITY"}
        node_caps = set(node_data.get("capabilities", []))
        
        violations = forbidden_caps & node_caps
        if violations:
            return InvariantViolation(
                rule_id=MabniInvariantValidator.RULE_ID,
                node_id=node_data.get("id"),
                edge_id=None,
                message=f"MabniRefNode has forbidden capabilities: {violations}",
                severity="FATAL"
            )
        
        return None
    
    @staticmethod
    def validate_root_instantiation(edge_data: Dict, nodes_index: Dict) -> Optional[InvariantViolation]:
        """
        فحص 2: instantiation كجذر
        
        إذا كان edge من نوع ROOT_OF أو INSTANTIATES_PATTERN، تأكد أن from ليس MabniRefNode
        """
        if edge_data.get("type") not in ["ROOT_OF", "INSTANTIATES_PATTERN"]:
            return None
        
        from_id = edge_data.get("from")
        from_node = nodes_index.get(from_id)
        
        if not from_node:
            return None
        
        if from_node.get("kind") == "MabniRefNode":
            return InvariantViolation(
                rule_id=MabniInvariantValidator.RULE_ID,
                node_id=from_id,
                edge_id=edge_data.get("id"),
                message=f"MabniRefNode ({from_id}) cannot be instantiated as Root",
                severity="FATAL"
            )
        
        return None
    
    @staticmethod
    def validate_quality_instantiation(edge_data: Dict, nodes_index: Dict) -> Optional[InvariantViolation]:
        """
        فحص 3: instantiation كصفة
        
        إذا كان edge من نوع MODIFIES، تأكد أن from ليس MabniRefNode
        """
        if edge_data.get("type") != "MODIFIES":
            return None
        
        from_id = edge_data.get("from")
        from_node = nodes_index.get(from_id)
        
        if not from_node:
            return None
        
        if from_node.get("kind") == "MabniRefNode":
            return InvariantViolation(
                rule_id=MabniInvariantValidator.RULE_ID,
                node_id=from_id,
                edge_id=edge_data.get("id"),
                message=f"MabniRefNode ({from_id}) cannot act as adjective/quality",
                severity="FATAL"
            )
        
        return None
    
    @staticmethod
    def validate_ref_production(edge_data: Dict, nodes_index: Dict, traces: List[Dict]) -> Optional[InvariantViolation]:
        """
        فحص 4: إنتاج Ref يتطلب MabniRefGate
        
        إذا كان edge من نوع BINDS_REF، تأكد من وجود MabniRefGate trace
        """
        if edge_data.get("type") != "BINDS_REF":
            return None
        
        from_id = edge_data.get("from")
        to_id = edge_data.get("to")
        
        # البحث عن trace
        gate_found = False
        for trace in traces:
            if (trace.get("input_node_id") == from_id and 
                trace.get("output_node_id") == to_id and
                "MabniRefGate" in trace.get("gate_type", "")):
                gate_found = True
                break
        
        if not gate_found:
            return InvariantViolation(
                rule_id=MabniInvariantValidator.RULE_ID,
                node_id=from_id,
                edge_id=edge_data.get("id"),
                message=f"BINDS_REF without MabniRefGate trace: {from_id} → {to_id}",
                severity="FATAL"
            )
        
        return None


# ═══════════════════════════════════════════════════════════════════════
# 4) القانون 5.3: الاشتقاق
# ═══════════════════════════════════════════════════════════════════════

class DerivationInvariantValidator:
    """
    فاحص القانون 5.3: تغيير نوع الجذر يتطلب Gate + trace
    
    الصيغة الرياضية:
    ∀ step:
      if change(root.kind from K₁ to K₂)
      then ∃ gate: gate.type = DerivationGate ∧ trace recorded
    """
    
    RULE_ID = "INV_DERIVATION"
    
    @staticmethod
    def validate_root_kind_change(edge_data: Dict, nodes_index: Dict, traces: List[Dict]) -> Optional[InvariantViolation]:
        """
        فحص: تغيير root_kind
        
        إذا كان edge من نوع DERIVES_TO، تأكد من:
        1. from و to كلاهما RootNode
        2. root_kind مختلف
        3. يوجد DerivationGate trace
        """
        if edge_data.get("type") != "DERIVES_TO":
            return None
        
        from_id = edge_data.get("from")
        to_id = edge_data.get("to")
        
        from_node = nodes_index.get(from_id)
        to_node = nodes_index.get(to_id)
        
        if not from_node or not to_node:
            return InvariantViolation(
                rule_id=DerivationInvariantValidator.RULE_ID,
                node_id=from_id,
                edge_id=edge_data.get("id"),
                message=f"DERIVES_TO with missing nodes: {from_id} → {to_id}",
                severity="ERROR"
            )
        
        # تأكد أن كلاهما RootNode
        if from_node.get("kind") != "RootNode" or to_node.get("kind") != "RootNode":
            return InvariantViolation(
                rule_id=DerivationInvariantValidator.RULE_ID,
                node_id=from_id,
                edge_id=edge_data.get("id"),
                message=f"DERIVES_TO requires both nodes to be RootNode",
                severity="ERROR"
            )
        
        # استخراج root_kind
        from_kind = from_node.get("data", {}).get("root_kind")
        to_kind = to_node.get("data", {}).get("root_kind")
        
        if from_kind == to_kind:
            return None  # no kind change
        
        # البحث عن DerivationGate trace
        gate_found = False
        for trace in traces:
            if (trace.get("input_node_id") == from_id and
                trace.get("output_node_id") == to_id and
                "DerivationGate" in trace.get("gate_type", "")):
                # تأكد من تسجيل التغيير في trace
                trace_data = trace.get("trace", {})
                if (trace_data.get("from_kind") == from_kind and
                    trace_data.get("to_kind") == to_kind):
                    gate_found = True
                    break
        
        if not gate_found:
            return InvariantViolation(
                rule_id=DerivationInvariantValidator.RULE_ID,
                node_id=from_id,
                edge_id=edge_data.get("id"),
                message=f"Root kind change ({from_kind} → {to_kind}) without DerivationGate trace",
                severity="FATAL"
            )
        
        return None


# ═══════════════════════════════════════════════════════════════════════
# 5) الفاحص الشامل
# ═══════════════════════════════════════════════════════════════════════

class GraphValidator:
    """
    فاحص شامل يطبق كل القوانين القاطعة
    """
    
    def __init__(self):
        self.ma3ani_validator = Ma3aniInvariantValidator()
        self.mabni_validator = MabniInvariantValidator()
        self.derivation_validator = DerivationInvariantValidator()
    
    def validate_graph(self, graph_data: Dict) -> ValidationReport:
        """
        فحص شامل للرسم
        
        Args:
            graph_data: رسم بصيغة JSON (حسب graph_schema.json)
        
        Returns:
            ValidationReport مع كل الانتهاكات
        """
        violations = []
        warnings = []
        passed_checks = []
        
        # استخراج البيانات
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])
        judgment = graph_data.get("judgment", {})
        traces = graph_data.get("traces", [])
        
        # بناء index للعقد
        nodes_index = {node["id"]: node for node in nodes}
        
        # ═══ Stage 1: فحص العقد ═══
        for node in nodes:
            # قانون 5.1
            v = Ma3aniInvariantValidator.validate_node_capabilities(node)
            if v:
                violations.append(v)
            else:
                if node.get("kind") == "Ma3aniToolNode":
                    passed_checks.append(f"Ma3aniToolNode {node['id']}: capabilities OK")
            
            # قانون 5.2
            v = MabniInvariantValidator.validate_node_capabilities(node)
            if v:
                violations.append(v)
            else:
                if node.get("kind") == "MabniRefNode":
                    passed_checks.append(f"MabniRefNode {node['id']}: capabilities OK")
        
        # ═══ Stage 2: فحص الحواف ═══
        for edge in edges:
            # قانون 5.1
            v = Ma3aniInvariantValidator.validate_subject_write(edge, nodes_index)
            if v:
                violations.append(v)
            
            v = Ma3aniInvariantValidator.validate_predicate_write(edge, nodes_index)
            if v:
                violations.append(v)
            
            # قانون 5.2
            v = MabniInvariantValidator.validate_root_instantiation(edge, nodes_index)
            if v:
                violations.append(v)
            
            v = MabniInvariantValidator.validate_quality_instantiation(edge, nodes_index)
            if v:
                violations.append(v)
            
            v = MabniInvariantValidator.validate_ref_production(edge, nodes_index, traces)
            if v:
                violations.append(v)
            
            # قانون 5.3
            v = DerivationInvariantValidator.validate_root_kind_change(edge, nodes_index, traces)
            if v:
                violations.append(v)
        
        # ═══ Stage 3: فحص الحكم J ═══
        j_violations = Ma3aniInvariantValidator.validate_judgment(judgment, nodes_index)
        violations.extend(j_violations)
        
        if not j_violations:
            passed_checks.append("Judgment J: no Ma3aniToolNode in subject/predicate")
        
        # ═══ النتيجة النهائية ═══
        if violations:
            result = ValidationResult.FAIL
        else:
            result = ValidationResult.PASS
            passed_checks.append("All hard invariants satisfied")
        
        return ValidationReport(
            result=result,
            violations=violations,
            warnings=warnings,
            passed_checks=passed_checks
        )


# ═══════════════════════════════════════════════════════════════════════
# 6) دوال مساعدة للاستخدام في Maqam Theory
# ═══════════════════════════════════════════════════════════════════════

def compute_hard_gate_cost(graph_data: Dict) -> float:
    """
    حساب كلفة البوابات القاطعة (للاستخدام في E(x,y))
    
    إذا وجد انتهاك قاطع → ∞
    وإلا → 0
    """
    validator = GraphValidator()
    report = validator.validate_graph(graph_data)
    
    if report.has_fatal_violations():
        return float('inf')
    
    return 0.0


def is_admissible_candidate(graph_data: Dict) -> bool:
    """
    فحص: هل y ∈ Y_admiss؟
    
    Y_admiss = {y : all hard gates pass}
    """
    validator = GraphValidator()
    report = validator.validate_graph(graph_data)
    
    return not report.has_fatal_violations()


# ═══════════════════════════════════════════════════════════════════════
# 7) مثال: تطبيق على "من يكذب يعاقب"
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("Hard Invariants Validators - Test")
    print("=" * 70)
    
    # مثال 1: رسم صحيح
    valid_graph = {
        "nodes": [
            {
                "id": "m1",
                "kind": "Ma3aniToolNode",
                "data": {"tool_class": "COND"},
                "capabilities": ["CAN_PRODUCE_SCOPE", "CAN_PRODUCE_CONSTRAINT"]
            },
            {
                "id": "r2",
                "kind": "RootNode",
                "data": {"radicals": ["ك", "ذ", "ب"], "root_kind": "EventRoot"},
                "capabilities": ["CAN_WRITE_SUBJECT", "CAN_WRITE_PREDICATE"]
            },
            {
                "id": "scope1",
                "kind": "ScopeOperatorNode",
                "data": {"operator_type": "IF_THEN"},
                "capabilities": []
            }
        ],
        "edges": [
            {
                "id": "e1",
                "type": "ADDS_SCOPE_OPERATOR",
                "from": "m1",
                "to": "scope1"
            },
            {
                "id": "e2",
                "type": "BUILDS_PREDICATE",
                "from": "r2",
                "to": "J.predicate"
            }
        ],
        "judgment": {
            "subject": None,
            "predicate": "r2",
            "scope": ["scope1"],
            "constraints": []
        },
        "traces": [
            {
                "gate_type": "Ma3aniScopeGate",
                "input_node_id": "m1",
                "output_node_id": "scope1",
                "trace": {}
            }
        ]
    }
    
    print("\nTest 1: Valid Graph")
    print("-" * 70)
    validator = GraphValidator()
    report = validator.validate_graph(valid_graph)
    
    print(f"Result: {report.result.name}")
    print(f"Violations: {len(report.violations)}")
    print(f"Passed checks: {len(report.passed_checks)}")
    for check in report.passed_checks:
        print(f"  ✓ {check}")
    print(f"Cost: {report.get_cost()}")
    print(f"Is admissible: {is_admissible_candidate(valid_graph)}")
    
    # مثال 2: رسم خاطئ (Ma3aniTool يكتب Predicate)
    invalid_graph = {
        "nodes": [
            {
                "id": "m1",
                "kind": "Ma3aniToolNode",
                "data": {"tool_class": "NEG"},
                "capabilities": ["CAN_PRODUCE_SCOPE"]
            }
        ],
        "edges": [
            {
                "id": "e1",
                "type": "BUILDS_PREDICATE",
                "from": "m1",
                "to": "J.predicate"
            }
        ],
        "judgment": {
            "subject": None,
            "predicate": "m1",
            "scope": [],
            "constraints": []
        },
        "traces": []
    }
    
    print("\n\nTest 2: Invalid Graph (Ma3aniTool writes Predicate)")
    print("-" * 70)
    report = validator.validate_graph(invalid_graph)
    
    print(f"Result: {report.result.name}")
    print(f"Violations: {len(report.violations)}")
    for v in report.violations:
        print(f"  ✗ {v}")
    print(f"Cost: {report.get_cost()}")
    print(f"Is admissible: {is_admissible_candidate(invalid_graph)}")
    
    print("\n" + "=" * 70)
    print("✓ Validation tests completed")
    print("=" * 70)
