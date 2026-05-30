from __future__ import annotations

from core.gencode.problem_type_induction import induce_problem_types_from_examples


def _ex(ex_id: int, stem: str, answer: str = "", skill_id: str = "vh_mock_skill") -> dict:
    return {
        "id": ex_id,
        "example_id": ex_id,
        "skill_id": skill_id,
        "problem_text": stem,
        "correct_answer": answer,
    }


def test_composite_exercise_goes_to_same_as_main_skill_fallback():
    examples = [
        _ex(1, "章末綜合練習：請判斷下列敘述與函數關係，並簡述理由。", "", "vh_mock_Function"),
        _ex(2, "統測題：根據圖形與表格綜合判斷。", "", "vh_mock_Function"),
    ]
    out = induce_problem_types_from_examples("vh_mock_Function", examples, spec_mode="rule_first_induce_from_sources")
    assert out.get("fallback_subskill_used") is True
    subskills = set(out.get("subskills") or [])
    assert "same_as_main_skill" in subskills
    same_main_rows = out.get("same_as_main_skill_examples") or []
    assert len(same_main_rows) >= 1


def test_low_source_examples_not_semantic_mismatch():
    examples = [
        _ex(1, "求 A(1,2)、B(3,4) 的中點坐標。", "(2,3)", "vh_mock_Midpoint"),
        _ex(2, "求 △ABC 的重心坐標。", "(0,0)", "vh_mock_Midpoint"),
    ]
    out = induce_problem_types_from_examples("vh_mock_Midpoint", examples, spec_mode="rule_first_induce_from_sources")
    blockers = set(out.get("alignment_blockers") or [])
    assert "majority_needs_review" not in blockers
    assert isinstance(out.get("low_source_examples"), list)
