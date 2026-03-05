"""
اختبارات بنية X-bar / C1–C2–C3
================================

يتحقق من أن ملف coq_proofs/XBar.v:
  1. موجود ويحتوي على التعريفات المطلوبة.
  2. يُعرّف الأنواع الاستقرائية المتوافقة مع C1/C2/C3.
  3. يُصرّح بالعلاقات c1_feeds_c2 و c2_feeds_c3 و c1_related_c3.
  4. يحتوي على المبرهنات المطلوبة.
  5. مضمَّن في _CoqProject.
  6. Theorems.v يستورد XBar ويحتوي على theorem11.
"""

import pathlib
import re

REPO_ROOT = pathlib.Path(__file__).parent.parent
COQ_PROOFS = REPO_ROOT / "coq_proofs"
XBAR_V = COQ_PROOFS / "XBar.v"
COQ_PROJECT = COQ_PROOFS / "_CoqProject"
THEOREMS_V = COQ_PROOFS / "Theorems.v"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def read_file(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

def test_xbar_v_exists():
    """XBar.v must exist in coq_proofs/"""
    assert XBAR_V.exists(), f"Missing file: {XBAR_V}"


def test_xbar_pipeline_stage_inductive():
    """PipelineStage inductive with C1/C2/C3 constructors must be present"""
    content = read_file(XBAR_V)
    assert "Inductive PipelineStage" in content, "PipelineStage inductive missing"
    for ctor in ("| C1", "| C2", "| C3"):
        assert ctor in content, f"Constructor '{ctor}' missing from PipelineStage"


def test_xbar_level_inductive():
    """XBarLevel inductive with Head/Bar/Phrase must be present"""
    content = read_file(XBAR_V)
    assert "Inductive XBarLevel" in content, "XBarLevel inductive missing"
    for ctor in ("| Head", "| Bar", "| Phrase"):
        assert ctor in content, f"Constructor '{ctor}' missing from XBarLevel"


def test_xbar_tree_inductive():
    """XBarTree inductive with XHead/XBarNode/XPhrase must be present"""
    content = read_file(XBAR_V)
    assert "Inductive XBarTree" in content, "XBarTree inductive missing"
    for ctor in ("| XHead", "| XBarNode", "| XPhrase"):
        assert ctor in content, f"Constructor '{ctor}' missing from XBarTree"


def test_level_to_stage_mapping():
    """level_to_stage must map Head→C1, Bar→C2, Phrase→C3"""
    content = read_file(XBAR_V)
    assert "level_to_stage" in content, "level_to_stage mapping missing"
    # Check each mapping appears
    assert re.search(r"Head\s*=>\s*C1", content), "Head => C1 mapping missing"
    assert re.search(r"Bar\s*=>\s*C2",  content), "Bar  => C2 mapping missing"
    assert re.search(r"Phrase\s*=>\s*C3", content), "Phrase => C3 mapping missing"


def test_c1_feeds_c2_definition():
    """c1_feeds_c2 relation must be defined"""
    content = read_file(XBAR_V)
    assert "c1_feeds_c2" in content, "c1_feeds_c2 definition missing"


def test_c2_feeds_c3_definition():
    """c2_feeds_c3 relation must be defined"""
    content = read_file(XBAR_V)
    assert "c2_feeds_c3" in content, "c2_feeds_c3 definition missing"


def test_c1_related_c3_definition():
    """c1_related_c3 indirect relation (via C2) must be defined"""
    content = read_file(XBAR_V)
    assert "c1_related_c3" in content, "c1_related_c3 definition missing"
    # Must use 'exists bar' to express the bridging
    assert "exists bar" in content, "c1_related_c3 must existentially quantify over the C2 bridge"
    # The definition body must conjoin c1_feeds_c2 and c2_feeds_c3 via the bridge
    idx = content.index("Definition c1_related_c3")
    block = content[idx:idx + 400]
    assert "c1_feeds_c2" in block, "c1_related_c3 must reference c1_feeds_c2"
    assert "c2_feeds_c3" in block, "c1_related_c3 must reference c2_feeds_c3"


def test_c2_bridges_c1_c3_theorem():
    """c2_bridges_c1_c3 theorem must be present and proved (no Admitted)"""
    content = read_file(XBAR_V)
    assert "Theorem c2_bridges_c1_c3" in content, "c2_bridges_c1_c3 theorem missing"
    # Extract the theorem block and verify it ends with Qed not Admitted
    idx = content.index("Theorem c2_bridges_c1_c3")
    block = content[idx:]
    first_end = re.search(r"\bQed\b|\bAdmitted\b", block)
    assert first_end is not None, "c2_bridges_c1_c3 proof block not closed"
    assert first_end.group() == "Qed", "c2_bridges_c1_c3 must be fully proved (Qed), not Admitted"


def test_xbar_wf_definition():
    """xbar_wf well-formedness predicate must be defined"""
    content = read_file(XBAR_V)
    assert "xbar_wf" in content, "xbar_wf predicate missing"


def test_xbar_from_token_lemmas():
    """xbar_from_token helper and its well-formedness lemma must be present"""
    content = read_file(XBAR_V)
    assert "xbar_from_token" in content, "xbar_from_token missing"
    assert "xbar_from_token_wf" in content, "xbar_from_token_wf lemma missing"
    assert "xbar_from_token_c1_related_c3" in content, (
        "xbar_from_token_c1_related_c3 lemma missing"
    )


def test_coq_project_includes_xbar():
    """_CoqProject must list XBar.v"""
    content = read_file(COQ_PROJECT)
    assert "XBar.v" in content, "XBar.v not listed in _CoqProject"


def test_theorems_imports_xbar():
    """Theorems.v must import XBar"""
    content = read_file(THEOREMS_V)
    assert "Require Import XBar" in content, "Theorems.v does not import XBar"


def test_theorem11_in_theorems():
    """Theorems.v must contain theorem11_xbar_c1_c2_c3"""
    content = read_file(THEOREMS_V)
    assert "theorem11_xbar_c1_c2_c3" in content, (
        "theorem11_xbar_c1_c2_c3 not found in Theorems.v"
    )
    # Must be fully proved
    idx = content.index("theorem11_xbar_c1_c2_c3")
    block = content[idx:]
    first_end = re.search(r"\bQed\b|\bAdmitted\b", block)
    assert first_end is not None, "theorem11 proof block not closed"
    assert first_end.group() == "Qed", (
        "theorem11_xbar_c1_c2_c3 must be fully proved (Qed), not Admitted"
    )
