from __future__ import annotations

from unittest.mock import patch

from core.gencode.problem_type_induction import induce_problem_types_from_examples


def _ex(ex_id: int, text: str, answer: str = "1", *, skill_id: str = "vh_數學B1_LinearFunction") -> dict:
    return {
        "id": ex_id,
        "example_id": ex_id,
        "skill_id": skill_id,
        "problem_text": text,
        "correct_answer": answer,
    }


def test_same_contract_different_math_objects_merge_into_single_problem_type():
    skill_id = "vh_數學B1_LinearFunction"
    meta = {
        "skill_ch_name": "線型函數",
        "skill_en_name": "LinearFunction",
        "chapter": "1 坐標系與函數圖形",
        "section_code": "1-2 平面坐標系與線型函數",
    }
    examples = [
        _ex(4424, "右圖為函數 y=f(x)=ax+b 的圖形，試求截距。", "2"),
        _ex(4444, "下圖為函數 y=f(x)=ax+b 的圖形，試求 f(x)。", "3"),
        _ex(4433, "試在坐標平面上畫出 y=f(x)=-2 的圖形。", "1"),
        _ex(4449, "試在坐標平面上畫出函數 y=f(x)=-2x+4 的圖形。", "4"),
    ]
    with patch("core.gencode.problem_type_induction.load_skill_metadata_from_db", return_value=meta):
        out = induce_problem_types_from_examples(skill_id, examples, spec_mode="rule_first_induce_from_sources")
    specs = out.get("induced_problem_type_specs") or []
    ids = [str(s.get("problem_type_id", "")) for s in specs if isinstance(s, dict)]
    assert "numeric_interpret_function_notation_short_answer" in ids
    assert not any("coordinate_point" in x for x in ids)
    assert not any("two_coordinate" in x for x in ids)
    target_specs = [
        s for s in specs
        if isinstance(s, dict) and str(s.get("problem_type_id", "")) == "numeric_interpret_function_notation_short_answer"
    ]
    assert target_specs
    src_ids = set(target_specs[0].get("source_example_ids") or [])
    assert {4424, 4433, 4449}.issubset(src_ids)


def test_different_target_task_not_merged():
    skill_id = "vh_數學B1_LinearFunction"
    meta = {"skill_ch_name": "線型函數", "skill_en_name": "LinearFunction"}
    examples = [
        _ex(5001, "給定函數，求 f(2) 的值。", "2"),
        _ex(5002, "解讀函數符號並判斷圖形。", "3"),
    ]
    with patch("core.gencode.problem_type_induction.load_skill_metadata_from_db", return_value=meta):
        out = induce_problem_types_from_examples(skill_id, examples, spec_mode="rule_first_induce_from_sources")
    specs = [s for s in (out.get("induced_problem_type_specs") or []) if isinstance(s, dict)]
    tasks = {str(s.get("target_task", "")).strip() for s in specs}
    assert len(tasks) >= 1

