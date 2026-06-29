from __future__ import annotations

import pytest

from core.gencode.pipeline_orchestrator import run_v3_no_llm_phase1_for_example


def _classify(text: str, *, answer: str = "") -> dict:
    return run_v3_no_llm_phase1_for_example(
        "future_generic_math_skill",
        {
            "id": 1,
            "problem_text": text,
            "correct_answer": answer,
            "detailed_solution": "",
        },
        conn=None,
    )


@pytest.mark.parametrize(
    ("text", "answer"),
    [
        ("若 |x| = 8，求 x", "-8, 8"),
        ("若 |t| = 7，求 t 的值", "-7, 7"),
        ("已知 |y| = 0，試求 y", "0"),
        ("若  | x | = 8 ， 求 x。", "-8, 8"),
        (r"若 $\left| t \right|$ = 7，求 t 的值", "-7, 7"),
    ],
)
def test_basic_absolute_value_equation_uses_structural_rule(text: str, answer: str) -> None:
    result = _classify(text, answer=answer)

    assert result["classification_status"] == "resolved"
    assert result["problem_type_id"] == "solve_basic_absolute_value_equation"
    assert result["answer_contract"]["answer_type"] == "solution_set"
    assert result["answer_contract"]["checker_key"] == "solution_set_checker"
    assert result["answer_contract"]["equivalence_type"] == "unordered_solution_set"


def test_negative_rhs_is_classified_as_no_solution_variant() -> None:
    result = _classify("若 |z| = -2，求 z", answer="無解")

    assert result["classification_status"] == "resolved"
    assert result["problem_type_id"] == "solve_basic_absolute_value_equation_no_solution"
    assert result["problem_type_id"] != "solve_basic_absolute_value_equation"


@pytest.mark.parametrize(
    ("text", "answer"),
    [
        ("數線上兩點 A(-3)、B(7)，求兩點距離", "10"),
        ("數線上兩點 P(5)、Q(-2)，求 P、Q 兩點距離", "7"),
        ("數線上兩點 A 點坐標為 p，B 點坐標為 q，求 AB", "|p-q|"),
    ],
)
def test_number_line_distance_uses_structural_rule(text: str, answer: str) -> None:
    result = _classify(text, answer=answer)

    assert result["classification_status"] == "resolved"
    assert result["problem_type_id"] == "number_line_distance_between_two_points"
    assert result["answer_contract"]["answer_type"] == "integer"
    assert result["answer_contract"]["checker_key"] == "integer_checker"
    assert result["answer_contract"]["equivalence_type"] == "numeric_exact"


@pytest.mark.parametrize(
    "text",
    [
        "解方程 x + 8 = 0",
        "平面上兩點 A(-3, 2)、B(7, 4)，求兩點距離",
        "數線上 A(-3) 點的絕對值是多少",
    ],
)
def test_unrelated_structures_are_not_misclassified(text: str) -> None:
    result = _classify(text)

    assert result.get("problem_type_id") not in {
        "solve_basic_absolute_value_equation",
        "solve_basic_absolute_value_equation_no_solution",
        "number_line_distance_between_two_points",
    }
