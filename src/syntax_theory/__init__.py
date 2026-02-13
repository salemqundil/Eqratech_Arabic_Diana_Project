"""
نظرية التركيب (Syntax Theory)
============================

نظام تركيبي كامل على نفس مبدأ اللفظ المفرد:
x → y₀ → G(x) → arg min E

المكونات:
---------
1. structures: تعريف x (المدخل) و y (الرسم البياني)
2. relations: ISN, TADMN, TAQYID
3. operators: العوامل (إنّ، كان، لم، حروف جر...)
4. minimizers: دالة الكلفة E
5. generators: Canon(x) و G(x)
6. proofs: براهين الاختيار

البرهان المركزي:
---------------
arg min E يختار:
- ISN (الإسناد) لإثبات الحكم
- TADMN (التضمين) لإشباع الفتحات
- TAQYID (التقييد) لربط المقيدات
- ويُغلق المبني/المعرب كحصيلة بوابات ∞
- ويُثبت الفاعلية/المفعولية/السببية داخل نفس E
"""

__version__ = "1.0.0"
__author__ = "نظرية التركيب الرياضية"

# الاستيرادات الرئيسية
from .structures import (
    SyntacticInput, SyntacticGraph,
    LexicalAtom, LexicalType, VerbValency, SemanticRole,
    EdgeType, CaseMarking, MoodMarking,
    Node, Edge, NodeFeatures,
    make_simple_input, make_token_node, make_governor_node
)

from .relations import (
    RelationBuilder, RelationConstraints,
    make_simple_isn_graph
)

from .operators import (
    OperatorFactory, OperatorConstraints,
    OperatorSignature,
    INNA_SIGNATURE, KANA_SIGNATURE, LAM_SIGNATURE,
    make_inna_graph, make_lam_graph
)

from .generators import (
    CanonicalConstructor, CandidateGenerator, SimpleGenerator
)

from .minimizers import (
    SyntacticEnergy, SyntacticOptimizer, EnergyWeights
)

from .proofs import (
    TheoremResult, prove_all_theorems,
    StructuralSelectionTheorem,
    BuiltVsDeclensionTheorem,
    SemanticRolesTheorem
)

__all__ = [
    # structures
    'SyntacticInput', 'SyntacticGraph',
    'LexicalAtom', 'LexicalType', 'VerbValency', 'SemanticRole',
    'EdgeType', 'CaseMarking', 'MoodMarking',
    'Node', 'Edge', 'NodeFeatures',
    'make_simple_input', 'make_token_node', 'make_governor_node',
    
    # relations
    'RelationBuilder', 'RelationConstraints',
    'make_simple_isn_graph',
    
    # operators
    'OperatorFactory', 'OperatorConstraints',
    'OperatorSignature',
    'INNA_SIGNATURE', 'KANA_SIGNATURE', 'LAM_SIGNATURE',
    'make_inna_graph', 'make_lam_graph',
    
    # generators
    'CanonicalConstructor', 'CandidateGenerator', 'SimpleGenerator',
    
    # minimizers
    'SyntacticEnergy', 'SyntacticOptimizer', 'EnergyWeights',
    
    # proofs
    'TheoremResult', 'prove_all_theorems',
    'StructuralSelectionTheorem',
    'BuiltVsDeclensionTheorem',
    'SemanticRolesTheorem',
]
