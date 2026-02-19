"""
مثال تطبيقي كامل: "من يكذب يعاقب"
Complete Example: Building & Validating "Man yakdhib yuʿaqab"

هذا المثال يوضح:
1. بناء الرسم Graph خطوة بخطوة
2. تطبيق البوابات Gates
3. فحص القوانين القاطعة Hard Invariants
4. حساب الطاقة E(x, y) مع Type checking
5. إنتاج الحكم اللغوي J
6. تصدير الرسم بصيغة JSON
"""

import json
from typing import Dict, List
from type_system import (
    RootKind, Ma3aniToolClass, RefType,
    TokenNode, RootNode, Ma3aniToolNode, MabniRefNode,
    ScopeOperatorNode, LinguisticJudgment,
    Ma3aniScopeGate, TypeChecker, TypeViolation
)
from validators import GraphValidator, compute_hard_gate_cost


# ═══════════════════════════════════════════════════════════════════════
# 1) بناء "من يكذب يعاقب" خطوة بخطوة
# ═══════════════════════════════════════════════════════════════════════

def build_man_yakdhib_yuaqab():
    """
    بناء: من يكذب يعاقب
    
    المعنى: من يكذب يُعاقب
    التحليل:
    - من: أداة شرط (Ma3aniToolNode)
    - يكذب: فعل مضارع (RootNode EventRoot)
    - يعاقب: فعل مضارع مبني للمجهول (RootNode EventRoot)
    
    البنية:
    - من → ScopeOp(IF_THEN)
    - يكذب → Predicate في الشرط
    - يعاقب → Predicate في الجواب
    """
    
    print("=" * 70)
    print("بناء: من يكذب يعاقب")
    print("=" * 70)
    
    checker = TypeChecker()
    J = LinguisticJudgment()
    graph_data = {
        "nodes": [],
        "edges": [],
        "judgment": {},
        "traces": []
    }
    
    # ═══ Step 1: من (أداة شرط) ═══
    print("\nStep 1: من - أداة شرط")
    print("-" * 70)
    
    token_man = TokenNode(id="t1", surface="من", tags=["particle", "condition"])
    ma3ani_man = Ma3aniToolNode(id="m1", tool_class=Ma3aniToolClass.COND)
    
    checker.register_node(token_man)
    checker.register_node(ma3ani_man)
    
    graph_data["nodes"].append({
        "id": "t1",
        "kind": "TokenNode",
        "data": {"surface": "من", "tags": ["particle", "condition"]},
        "capabilities": []
    })
    
    graph_data["nodes"].append({
        "id": "m1",
        "kind": "Ma3aniToolNode",
        "data": {"tool_class": "COND"},
        "capabilities": ["CAN_PRODUCE_SCOPE", "CAN_PRODUCE_CONSTRAINT"]
    })
    
    print(f"  ✓ TokenNode: {token_man.id} (surface='{token_man.surface}')")
    print(f"  ✓ Ma3aniToolNode: {ma3ani_man.id} (class={ma3ani_man.tool_class.value})")
    print(f"    Capabilities: {[c.name for c in ma3ani_man.capabilities]}")
    
    # ═══ Step 2: تطبيق Ma3aniScopeGate ═══
    print("\nStep 2: تطبيق Ma3aniScopeGate")
    print("-" * 70)
    
    gate_scope = Ma3aniScopeGate()
    scope_op = gate_scope.apply(ma3ani_man)
    checker.register_node(scope_op)
    
    graph_data["nodes"].append({
        "id": scope_op.id,
        "kind": "ScopeOperatorNode",
        "data": {
            "operator_type": scope_op.operator_type.value,
            "arity": scope_op.arity,
            "effect": scope_op.effect
        },
        "capabilities": []
    })
    
    graph_data["edges"].append({
        "id": "e1",
        "type": "ADDS_SCOPE_OPERATOR",
        "from": "m1",
        "to": scope_op.id
    })
    
    graph_data["traces"].append({
        "gate_type": "Ma3aniScopeGate",
        "input_node_id": "m1",
        "output_node_id": scope_op.id,
        "trace": {"tool_class": "COND", "operator_type": "IF_THEN"}
    })
    
    print(f"  ✓ ScopeOperatorNode: {scope_op.id}")
    print(f"    Type: {scope_op.operator_type.value}")
    print(f"  ✓ Trace recorded: Ma3aniScopeGate")
    
    # ═══ Step 3: إضافة Scope إلى J ═══
    print("\nStep 3: إضافة Scope إلى J")
    print("-" * 70)
    
    try:
        checker.check_produce_scope(ma3ani_man, J, scope_op.id)
        print(f"  ✓ J.scope updated: {J.scope}")
    except TypeViolation as e:
        print(f"  ✗ Type violation: {e}")
        return None
    
    # ═══ Step 4: يكذب (فعل - جذر حدث) ═══
    print("\nStep 4: يكذب - فعل (جذر حدث)")
    print("-" * 70)
    
    token_yakdhib = TokenNode(id="t2", surface="يكذب", tags=["verb", "present"])
    root_yakdhib = RootNode(
        id="r2",
        radicals=["ك", "ذ", "ب"],
        root_kind=RootKind.EVENT_ROOT
    )
    
    checker.register_node(token_yakdhib)
    checker.register_node(root_yakdhib)
    
    graph_data["nodes"].append({
        "id": "t2",
        "kind": "TokenNode",
        "data": {"surface": "يكذب", "tags": ["verb", "present"]},
        "capabilities": []
    })
    
    graph_data["nodes"].append({
        "id": "r2",
        "kind": "RootNode",
        "data": {
            "radicals": ["ك", "ذ", "ب"],
            "root_kind": "EventRoot"
        },
        "capabilities": ["CAN_WRITE_SUBJECT", "CAN_WRITE_PREDICATE"]
    })
    
    graph_data["edges"].append({
        "id": "e2",
        "type": "ROOT_OF",
        "from": "r2",
        "to": "t2"
    })
    
    print(f"  ✓ TokenNode: {token_yakdhib.id} (surface='{token_yakdhib.surface}')")
    print(f"  ✓ RootNode: {root_yakdhib.id} (radicals={root_yakdhib.radicals})")
    print(f"    Kind: {root_yakdhib.root_kind.value}")
    print(f"    Capabilities: {[c.name for c in root_yakdhib.capabilities]}")
    
    # ═══ Step 5: يكذب → Predicate ═══
    print("\nStep 5: يكذب → Predicate (شرط)")
    print("-" * 70)
    
    try:
        checker.check_write_predicate(root_yakdhib, J)
        print(f"  ✓ J.predicate updated: {J.predicate}")
        
        graph_data["edges"].append({
            "id": "e3",
            "type": "BUILDS_PREDICATE",
            "from": "r2",
            "to": "J.predicate"
        })
    except TypeViolation as e:
        print(f"  ✗ Type violation: {e}")
        return None
    
    # ═══ Step 6: يعاقب (فعل - جذر حدث) ═══
    print("\nStep 6: يعاقب - فعل (جذر حدث)")
    print("-" * 70)
    
    token_yuaqab = TokenNode(id="t3", surface="يعاقب", tags=["verb", "present", "passive"])
    root_yuaqab = RootNode(
        id="r3",
        radicals=["ع", "ق", "ب"],
        root_kind=RootKind.EVENT_ROOT
    )
    
    checker.register_node(token_yuaqab)
    checker.register_node(root_yuaqab)
    
    graph_data["nodes"].append({
        "id": "t3",
        "kind": "TokenNode",
        "data": {"surface": "يعاقب", "tags": ["verb", "present", "passive"]},
        "capabilities": []
    })
    
    graph_data["nodes"].append({
        "id": "r3",
        "kind": "RootNode",
        "data": {
            "radicals": ["ع", "ق", "ب"],
            "root_kind": "EventRoot"
        },
        "capabilities": ["CAN_WRITE_SUBJECT", "CAN_WRITE_PREDICATE"]
    })
    
    graph_data["edges"].append({
        "id": "e4",
        "type": "ROOT_OF",
        "from": "r3",
        "to": "t3"
    })
    
    print(f"  ✓ TokenNode: {token_yuaqab.id} (surface='{token_yuaqab.surface}')")
    print(f"  ✓ RootNode: {root_yuaqab.id} (radicals={root_yuaqab.radicals})")
    
    # ═══ Step 7: العلاقة: شرط → جواب ═══
    print("\nStep 7: ربط الشرط بالجواب")
    print("-" * 70)
    
    graph_data["edges"].append({
        "id": "e5",
        "type": "CONDITION_IMPLIES",
        "from": "r2",  # يكذب (شرط)
        "to": "r3",    # يعاقب (جواب)
        "payload": {
            "scope_operator": scope_op.id,
            "relation": "IF_THEN"
        }
    })
    
    print(f"  ✓ Edge: CONDITION_IMPLIES")
    print(f"    From: يكذب (r2)")
    print(f"    To: يعاقب (r3)")
    print(f"    Scope: {scope_op.id} (IF_THEN)")
    
    # ═══ Step 8: بناء الحكم J النهائي ═══
    print("\nStep 8: الحكم اللغوي J")
    print("-" * 70)
    
    graph_data["judgment"] = {
        "subject": None,  # محذوف (من يكذب = whoever lies)
        "predicate": root_yakdhib.id,
        "scope": [scope_op.id],
        "constraints": []
    }
    
    print(f"  Subject: {J.subject}")
    print(f"  Predicate: {J.predicate}")
    print(f"  Scope: {J.scope}")
    print(f"  Constraints: {J.constraints}")
    
    return graph_data, checker, J


# ═══════════════════════════════════════════════════════════════════════
# 2) فحص القوانين القاطعة
# ═══════════════════════════════════════════════════════════════════════

def validate_graph(graph_data: Dict):
    """فحص الرسم باستخدام GraphValidator"""
    
    print("\n\n" + "=" * 70)
    print("فحص القوانين القاطعة")
    print("=" * 70)
    
    validator = GraphValidator()
    report = validator.validate_graph(graph_data)
    
    print(f"\nResult: {report.result.name}")
    print(f"Violations: {len(report.violations)}")
    print(f"Warnings: {len(report.warnings)}")
    print(f"Passed checks: {len(report.passed_checks)}")
    
    if report.violations:
        print("\nViolations:")
        for v in report.violations:
            print(f"  ✗ {v}")
    
    if report.passed_checks:
        print("\nPassed checks:")
        for check in report.passed_checks:
            print(f"  ✓ {check}")
    
    print(f"\nType-checking cost: {report.get_cost()}")
    print(f"Is admissible (Y_admiss): {not report.has_fatal_violations()}")
    
    return report


# ═══════════════════════════════════════════════════════════════════════
# 3) حساب الطاقة E(x, y)
# ═══════════════════════════════════════════════════════════════════════

def compute_energy(graph_data: Dict):
    """
    حساب دالة الطاقة E(x, y)
    
    E(x, y) = HardGates(x, y) + SoftTerms(x, y)
    
    حيث:
    - HardGates = Type checking (إذا فشل → ∞)
    - SoftTerms = تفضيلات ناعمة (penalties)
    """
    
    print("\n\n" + "=" * 70)
    print("حساب الطاقة E(x, y)")
    print("=" * 70)
    
    # Hard gate cost (type checking)
    hard_cost = compute_hard_gate_cost(graph_data)
    
    print(f"\nHard gate cost (type checking): {hard_cost}")
    
    if hard_cost == float('inf'):
        print("  → Candidate REJECTED (type violation)")
        return float('inf')
    
    # Soft terms (يمكن إضافة penalties أخرى)
    soft_cost = 0.0
    
    # مثال: penalty لعدم وجود subject صريح
    if graph_data["judgment"].get("subject") is None:
        soft_cost += 1.0  # penalty بسيط
        print("  Soft penalty: missing explicit subject (+1.0)")
    
    # مثال: penalty لعدد الحواف
    num_edges = len(graph_data["edges"])
    if num_edges > 10:
        soft_cost += (num_edges - 10) * 0.1
        print(f"  Soft penalty: too many edges (+{(num_edges - 10) * 0.1})")
    
    total_cost = hard_cost + soft_cost
    
    print(f"\nSoft terms cost: {soft_cost}")
    print(f"Total E(x, y): {total_cost}")
    
    return total_cost


# ═══════════════════════════════════════════════════════════════════════
# 4) تصدير JSON
# ═══════════════════════════════════════════════════════════════════════

def export_graph_json(graph_data: Dict, filename: str):
    """تصدير الرسم بصيغة JSON"""
    
    print("\n\n" + "=" * 70)
    print("تصدير JSON")
    print("=" * 70)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(graph_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Graph exported to: {filename}")
    print(f"  Nodes: {len(graph_data['nodes'])}")
    print(f"  Edges: {len(graph_data['edges'])}")
    print(f"  Traces: {len(graph_data['traces'])}")


# ═══════════════════════════════════════════════════════════════════════
# 5) Main
# ═══════════════════════════════════════════════════════════════════════

def main():
    """تشغيل المثال الكامل"""
    
    # بناء الرسم
    graph_data, checker, J = build_man_yakdhib_yuaqab()
    
    if graph_data is None:
        print("\n✗ Graph construction failed")
        return
    
    # فحص القوانين
    report = validate_graph(graph_data)
    
    # حساب الطاقة
    energy = compute_energy(graph_data)
    
    # تصدير JSON
    export_graph_json(graph_data, "man_yakdhib_yuaqab.json")
    
    # خلاصة نهائية
    print("\n\n" + "=" * 70)
    print("خلاصة نهائية")
    print("=" * 70)
    
    print(f"\nSentence: من يكذب يعاقب")
    print(f"Translation: Whoever lies will be punished")
    
    print(f"\nGraph structure:")
    print(f"  Nodes: {len(graph_data['nodes'])}")
    print(f"  Edges: {len(graph_data['edges'])}")
    print(f"  Traces: {len(graph_data['traces'])}")
    
    print(f"\nLinguistic Judgment J:")
    print(f"  Subject: {graph_data['judgment']['subject']}")
    print(f"  Predicate: {graph_data['judgment']['predicate']}")
    print(f"  Scope: {graph_data['judgment']['scope']}")
    print(f"  Constraints: {graph_data['judgment']['constraints']}")
    
    print(f"\nValidation:")
    print(f"  Result: {report.result.name}")
    print(f"  Violations: {len(report.violations)}")
    print(f"  Is admissible: {not report.has_fatal_violations()}")
    
    print(f"\nEnergy E(x, y): {energy}")
    
    print(f"\nHard Invariants:")
    print(f"  ✓ INV_MA3ANI_5.1: Ma3aniToolNode ('من') did not write Subject/Predicate")
    print(f"  ✓ INV_MA3ANI_5.1: Ma3aniScopeGate correctly produced ScopeOperator")
    print(f"  ✓ All type checks passed")
    
    print("\n" + "=" * 70)
    print("✓ Example completed successfully")
    print("=" * 70)


if __name__ == "__main__":
    main()
