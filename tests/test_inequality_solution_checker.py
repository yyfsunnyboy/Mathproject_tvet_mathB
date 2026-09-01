from __future__ import annotations

import importlib

import pytest

from core.checkers.inequality_solution_checker import check_inequality_solution_answer
from core.checkers.interval_checker import check_interval_answer
from core.gencode.answer_grading import grade_answer_for_current_question
from core.gencode.inequality_solution_routing import (
    is_inequality_solution_context,
    looks_like_relational_solution_text,
)
from core.gencode.runtime_skill_wrapper import check_answer

LINEAR_SKILL = "jh_數學1下_SolutionsAndGraphicalRepresentationOfOneVariableLinearInequalities"
ABS_SKILL = "vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning"
ABS_INEQ_SKILL = "vh_數學B1_AbsoluteValueInequality"
QUAD_SKILL = "vh_數學B1_QuadraticInequalitySolution"
COORD_SKILL = "vh_數學B1_DistanceBetweenTwoPointsInPlane"


def test_open_interval_matrix() -> None:
    correct = "2 < x < 7"
    true_cases = ["2<x<7", "x>2 且 x<7", "x<7 且 x>2", "x>2 and x<7", "(2,7)", "x∈(2,7)", "7>x>2"]
    false_cases = ["2<=x<7", "2<x<=7", "x<2 或 x>7", "[2,7]", "(2,7]"]
    for user in true_cases:
        assert check_inequality_solution_answer(user, correct) is True, user
        assert check_interval_answer(user, correct) is True, user
    for user in false_cases:
        assert check_inequality_solution_answer(user, correct) is False, user


def test_half_open_and_closed_and_or() -> None:
    assert check_inequality_solution_answer("2<=x<7", "2 <= x < 7") is True
    assert check_inequality_solution_answer("x>=2 且 x<7", "2 <= x < 7") is True
    assert check_inequality_solution_answer("x<7 and x>=2", "2 <= x < 7") is True
    assert check_inequality_solution_answer("[2,7)", "2 <= x < 7") is True
    assert check_inequality_solution_answer("x∈[2,7)", "2 <= x < 7") is True
    assert check_inequality_solution_answer("7>x>=2", "2 <= x < 7") is True
    assert check_inequality_solution_answer("2<x<7", "2 <= x < 7") is False
    assert check_inequality_solution_answer("2<=x<=7", "2 <= x < 7") is False
    assert check_inequality_solution_answer("(2,7)", "2 <= x < 7") is False
    assert check_inequality_solution_answer("[2,7]", "2 <= x < 7") is False

    assert check_inequality_solution_answer("2<=x<=7", "2 <= x <= 7") is True
    assert check_inequality_solution_answer("x>=2 且 x<=7", "2 <= x <= 7") is True
    assert check_inequality_solution_answer("[2,7]", "2 <= x <= 7") is True

    assert check_inequality_solution_answer("x>2", "x > 2") is True
    assert check_inequality_solution_answer("2<x", "x > 2") is True
    assert check_inequality_solution_answer("(2,∞)", "x > 2") is True
    assert check_inequality_solution_answer("x∈(2,∞)", "x > 2") is True
    assert check_inequality_solution_answer("x<=7", "x <= 7") is True
    assert check_inequality_solution_answer("7>=x", "x <= 7") is True
    assert check_inequality_solution_answer("(-∞,7]", "x <= 7") is True

    assert check_inequality_solution_answer("x<2 或 x>7", "x < 2 或 x > 7") is True
    assert check_inequality_solution_answer("x>7 or x<2", "x < 2 或 x > 7") is True
    assert check_inequality_solution_answer("(-∞,2) ∪ (7,∞)", "x < 2 或 x > 7") is True
    assert check_inequality_solution_answer("(7,∞) U (-∞,2)", "x < 2 或 x > 7") is True

    assert check_inequality_solution_answer("x>7 且 x<2", "x > 2 且 x < 7") is False
    assert check_inequality_solution_answer("x>1 且 x>2", "x>2") is True
    assert check_inequality_solution_answer("x<7 且 x<5", "x<5") is True
    assert check_inequality_solution_answer("x>2 或 x>5", "x>2") is True

    assert check_inequality_solution_answer("0.5 < x < 1.5", "1/2 < x < 3/2") is True
    assert check_inequality_solution_answer("(0.5,1.5)", "1/2 < x < 3/2") is True

    assert check_inequality_solution_answer("x<=-7/8 或 x>=27/8", "(-∞,-7/8]∪[27/8,∞)") is True
    assert check_inequality_solution_answer("x>=27/8 or x<=-0.875", "(-∞,-7/8]∪[27/8,∞)") is True
    assert check_inequality_solution_answer("x<-7/8 或 x>27/8", "(-∞,-7/8]∪[27/8,∞)") is False

    assert check_inequality_solution_answer("ℝ", "(-∞,∞)") is True
    assert check_inequality_solution_answer("所有實數", "R") is True
    assert check_inequality_solution_answer("∅", "無解") is True
    assert check_inequality_solution_answer("empty set", "無解") is True


def test_bare_pair_is_not_a_relational_hint() -> None:
    assert looks_like_relational_solution_text("(2,7)") is False
    assert looks_like_relational_solution_text("2<x<7") is True
    assert looks_like_relational_solution_text("[2,7)") is True


def test_coordinate_pair_not_hijacked() -> None:
    payload = {
        "skill_id": COORD_SKILL,
        "problem_type_id": "ordered_pair_point",
        "answer_type": "ordered_pair",
        "checker": "coordinate_pair_checker",
        "answer_contract": {
            "answer_type": "ordered_pair",
            "checker": "coordinate_pair_checker",
            "answer_equivalence": "coordinate_pair_equivalence",
        },
    }
    assert is_inequality_solution_context(payload, payload["answer_contract"], "(2,7)") is False
    assert check_answer("(2,7)", "(2,7)", payload=payload, skill_id=COORD_SKILL) is True
    assert check_answer("2<x<7", "(2,7)", payload=payload, skill_id=COORD_SKILL) is False


def _interval_payload(skill_id: str, problem_type_id: str, correct: str) -> dict:
    return {
        "skill": skill_id,
        "skill_id": skill_id,
        "problem_type_id": problem_type_id,
        "answer_type": "interval",
        "checker": "interval_checker",
        "correct_answer": correct,
        "answer": correct,
        "answer_contract": {
            "answer_type": "interval",
            "checker": "interval_checker",
            "answer_equivalence": "interval_equivalence",
        },
    }


@pytest.mark.parametrize(
    "skill_id,problem_type_id",
    [
        (LINEAR_SKILL, "solve_inequality"),
        (ABS_SKILL, "absolute_value_inequality_linear_expression_basic"),
        (QUAD_SKILL, "integer_solve_quadratic_inequality"),
    ],
)
def test_shared_checker_cross_skill_matrix(skill_id: str, problem_type_id: str) -> None:
    current = _interval_payload(skill_id, problem_type_id, "2<x<7")
    assert is_inequality_solution_context(current, current["answer_contract"], "2<x<7")
    for user in ["2<x<7", "x>2且x<7", "x<7且x>2", "(2,7)", "7>x>2"]:
        result = grade_answer_for_current_question(user, current, skill_id)
        assert result is not None
        assert result["correct"] is True, (skill_id, user, result)
        assert check_answer(user, "2<x<7", payload=current, skill_id=skill_id) is True
    for user in ["2<=x<7", "2<x<=7", "x<2或x>7"]:
        result = grade_answer_for_current_question(user, current, skill_id)
        assert result is not None
        assert result["correct"] is False, (skill_id, user, result)


def test_expression_contract_still_routes_abs_inequality() -> None:
    payload = {
        "skill_id": ABS_SKILL,
        "problem_type_id": "absolute_value_inequality_linear_expression_basic",
        "answer_type": "expression",
        "checker": "linear_equation_equivalent_checker",
        "correct_answer": "(2,7)",
        "answer_contract": {
            "answer_type": "expression",
            "checker": "linear_equation_equivalent_checker",
            "answer_equivalence": "linear_equation_equivalent",
        },
    }
    assert is_inequality_solution_context(payload, payload["answer_contract"], "(2,7)")
    assert check_answer("2<x<7", "(2,7)", payload=payload, skill_id=ABS_SKILL) is True
    assert check_answer("[2,7]", "(2,7)", payload=payload, skill_id=ABS_SKILL) is False


def test_live_skills_share_inequality_checker() -> None:
    abs_mod = importlib.import_module(f"skills.{ABS_SKILL}")
    quad_mod = importlib.import_module(f"skills.{QUAD_SKILL}")
    linear_mod = importlib.import_module(f"skills.{LINEAR_SKILL}")

    abs_q = None
    for seed in range(40):
        q = abs_mod.generate(level=1, seed=seed)
        if str(q.get("presentation_mode") or "") == "single_choice":
            continue
        ca = str(q.get("correct_answer") or q.get("answer") or "")
        if check_inequality_solution_answer(ca, ca) is True:
            abs_q = q
            break
    assert abs_q is not None
    ca = str(abs_q.get("correct_answer") or abs_q.get("answer"))
    parsed_ok = check_answer(ca, ca, payload=abs_q, skill_id=ABS_SKILL)
    assert parsed_ok is True
    assert check_answer("x>99999", ca, payload=abs_q, skill_id=ABS_SKILL) is False

    quad_q = None
    for seed in range(40):
        q = quad_mod.generate(level=1, seed=seed)
        pt = str(q.get("problem_type_id") or "")
        if "solve_quadratic_inequality" not in pt or "special" in pt or "reverse" in pt:
            continue
        if str((q.get("answer_contract") or {}).get("checker") or q.get("checker")) != "interval_checker":
            if str((q.get("answer_contract") or {}).get("answer_type")) != "interval":
                continue
        ca = str(q.get("correct_answer") or q.get("answer") or "")
        if check_inequality_solution_answer(ca, ca) is True:
            quad_q = q
            break
    assert quad_q is not None
    qca = str(quad_q.get("correct_answer") or quad_q.get("answer"))
    assert check_answer(qca, qca, payload=quad_q, skill_id=QUAD_SKILL) is True

    linear_q = linear_mod.generate(level=1)
    lca = str(linear_q.get("correct_answer") or linear_q.get("answer") or "")
    current = {
        "skill": LINEAR_SKILL,
        "correct_answer": lca,
        "answer": lca,
        "problem_type_id": "solve_inequality",
    }
    result = grade_answer_for_current_question(lca.replace("$", "").replace(" ", ""), current, LINEAR_SKILL)
    assert result is not None
    assert result["correct"] is True


def _live_abs_zero_center_payload(correct: str) -> dict:
    return {
        "skill": ABS_INEQ_SKILL,
        "skill_id": ABS_INEQ_SKILL,
        "problem_type_id": "absolute_value_inequality_zero_center_basic",
        "answer_type": "expression",
        "checker": "interval_checker",
        "equivalence": "interval_set",
        "correct_answer": correct,
        "answer": correct,
        "answer_contract": {
            "presentation_mode": "short_answer",
            "answer_type": "expression",
            "checker": "interval_checker",
            "checker_key": "interval_checker",
            "answer_equivalence": "interval_set",
            "equivalence": "interval_set",
            "equivalence_type": "interval_set",
            "semantic_answer": correct,
        },
        "metadata": {
            "presentation_mode": "short_answer",
            "semantic_answer": correct,
            "problem_type_id": "absolute_value_inequality_zero_center_basic",
            "line_type": "absolute_value_inequality_zero_center_basic",
        },
    }


def test_nospace_or_equivalent_to_outer_union() -> None:
    correct = "(-∞,-1] U [1,∞)"
    assert check_inequality_solution_answer("x>=1或x<=-1", correct) is True
    assert check_inequality_solution_answer("x<=-1或x>=1", correct) is True
    assert check_inequality_solution_answer("x>=1 or x<=-1", correct) is True
    assert check_inequality_solution_answer("x>1或x<-1", correct) is False


def test_grade_answer_live_abs_payload_does_not_use_expression_checker() -> None:
    correct = "(-∞,-1] ∪ [1,∞)"
    current = _live_abs_zero_center_payload(correct)
    assert is_inequality_solution_context(current, current["answer_contract"], correct) is True
    ok = grade_answer_for_current_question("x>=1或x<=-1", current, ABS_INEQ_SKILL)
    assert ok is not None
    assert ok["correct"] is True, ok
    ok2 = grade_answer_for_current_question("x<=-1或x>=1", current, ABS_INEQ_SKILL)
    assert ok2 is not None and ok2["correct"] is True
    bad = grade_answer_for_current_question("x>1或x<-1", current, ABS_INEQ_SKILL)
    assert bad is not None and bad["correct"] is False


def test_grade_answer_live_expansion_fraction_union() -> None:
    correct = "(-∞,-7/8] U [27/8,∞)"
    current = {
        "skill": ABS_SKILL,
        "skill_id": ABS_SKILL,
        "problem_type_id": "absolute_value_inequality_linear_expression_basic",
        "answer_type": "expression",
        "checker": "interval_checker",
        "equivalence": "interval_set",
        "correct_answer": correct,
        "answer": correct,
        "answer_contract": {
            "presentation_mode": "short_answer",
            "answer_type": "expression",
            "checker": "interval_checker",
            "checker_key": "interval_checker",
            "answer_equivalence": "interval_set",
            "equivalence": "interval_set",
            "equivalence_type": "interval_set",
            "semantic_answer": correct,
        },
        "metadata": {
            "presentation_mode": "short_answer",
            "problem_type_id": "absolute_value_inequality_linear_expression_basic",
            "line_type": "absolute_value_inequality_linear_expression_basic",
        },
    }
    ok = grade_answer_for_current_question("x<=-7/8或x>=27/8", current, ABS_SKILL)
    assert ok is not None
    assert ok["correct"] is True, ok
    bad = grade_answer_for_current_question("x<-7/8或x>27/8", current, ABS_SKILL)
    assert bad is not None and bad["correct"] is False

