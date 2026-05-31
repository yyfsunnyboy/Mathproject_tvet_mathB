# -*- coding: utf-8 -*-
"""Practice runtime session sync: coordinate_pair vs solution_set feedback."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path

from core.gencode.answer_grading import grade_answer_for_current_question
from core.gencode.answer_payload import refresh_runtime_question_session
from core.gencode.division_point_slot_engine import _internal_point
from core.gencode.runtime_skill_wrapper import check_answer
from core.routes.practice import get_skill, _normalize_gencode_runtime_payload


def test_fixed_case_p_q_ratio_2_1():
    px, py = _internal_point(-1, -3, 5, 0, 2, 1)
    assert px == Fraction(3, 1)
    assert py == Fraction(-1, 1)


def test_stale_list_with_checker_only_not_or_join():
    cur = {
        "skill": "vh_數學B1_DivisionPointCoordinates",
        "correct_answer": [3, -1],
        "checker": "coordinate_pair_checker",
        "equivalence": "coordinate_pair_equivalence",
        "problem_type_id": "ordered_pair_compute_internal_division_point_coordinates_short_answer_two_coordi",
        "question_text": "test",
    }
    refreshed = refresh_runtime_question_session(cur, skill_id=cur["skill"])
    assert refreshed["correct_answer"] == "(3,-1)"
    assert refreshed["display_answer"] == "(3,-1)"
    g = grade_answer_for_current_question("3,-1", refreshed, cur["skill"])
    assert g is not None and g["correct"] is True
    g2 = grade_answer_for_current_question("2,1", refreshed, cur["skill"])
    assert g2 is not None and g2["correct"] is False
    assert " 或 " not in g2["result"]
    assert "(3,-1)" in g2["result"]
    assert "4 或 10" not in g2["result"]


def test_stale_4_10_without_contract_gets_fixed_via_problem_type():
    cur = {
        "skill": "vh_數學B1_DivisionPointCoordinates",
        "correct_answer": [4, 10],
        "problem_type_id": "ordered_pair_compute_internal_division_point_coordinates_short_answer_two_coordi",
        "question_text": "division",
    }
    refreshed = refresh_runtime_question_session(cur, skill_id=cur["skill"])
    assert refreshed["correct_answer"] == "(4,10)"
    g = grade_answer_for_current_question("5", refreshed, cur["skill"])
    assert g is not None
    assert " 或 " not in g["result"]


def test_solution_set_regression_still_or_join():
    cur = {
        "skill": "mock_skill",
        "correct_answer": [2, 14],
        "answer_contract": {
            "answer_type": "solution_set",
            "answer_shape": "unordered_set",
            "checker": "solution_set_checker",
            "answer_equivalence": "unordered_solution_set",
        },
    }
    g = grade_answer_for_current_question("99", cur, "mock_skill")
    assert g is not None
    assert " 或 " in g["result"]


def test_check_answer_route_coordinate_pair_checker():
    ac = {
        "answer_type": "ordered_pair",
        "answer_shape": "coordinate_pair",
        "checker": "coordinate_pair_checker",
    }
    payload = {
        "skill_id": "vh_數學B1_DivisionPointCoordinates",
        "correct_answer": [3, -1],
        "answer_contract": ac,
        "checker": "coordinate_pair_checker",
    }
    assert check_answer("3,-1", "(3,-1)", payload=payload, answer_contract=ac) is True
    assert check_answer("4", "(3,-1)", payload=payload, answer_contract=ac) is False


def test_formal_skill_module_path():
    mod = get_skill("vh_數學B1_DivisionPointCoordinates")
    assert mod is not None
    mod_file = str(getattr(mod, "__file__", ""))
    assert "skills" in mod_file.replace("\\", "/")
    assert "DivisionPointCoordinates" in mod_file
    assert "drafts" not in mod_file.replace("\\", "/").lower() or Path(mod_file).name.startswith("vh_")
