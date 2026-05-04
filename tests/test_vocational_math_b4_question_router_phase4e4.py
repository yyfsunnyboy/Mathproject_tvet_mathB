from __future__ import annotations

import pytest

from core.vocational_math_b4.services.question_router import generate_for_skill


def test_factorial_notation_supported_and_payload() -> None:
    payload = generate_for_skill(skill_id="vh_數學B4_FactorialNotation", level=1, seed=1)
    assert payload["problem_type_id"] == "factorial_equation_solve_n"
    assert payload["generator_key"] == "b4.counting.factorial_equation_solve_n"
    assert len(payload["choices"]) == 4
    assert len(set(payload["choices"])) == 4
    assert payload["answer"] in payload["choices"]
    assert "$" in payload["question_text"]
    assert "\\frac" in payload["question_text"] or "\\frac" in payload["explanation"]
    assert "router_trace" in payload


def test_combination_group_selection_problem_type_override() -> None:
    payload = generate_for_skill(
        skill_id="vh_數學B4_CombinationApplications",
        level=1,
        seed=1,
        problem_type_id="combination_group_selection",
    )
    assert payload["problem_type_id"] == "combination_group_selection"
    assert payload["generator_key"] == "b4.combination.combination_group_selection"
    assert "router_trace" in payload


def test_combination_applications_supports_three_problem_types() -> None:
    expected = {
        "combination_polygon_count",
        "combination_required_excluded_person",
        "combination_group_selection",
    }
    for problem_type_id in expected:
        payload = generate_for_skill(
            skill_id="vh_數學B4_CombinationApplications",
            level=1,
            seed=2,
            problem_type_id=problem_type_id,
        )
        assert payload["problem_type_id"] == problem_type_id
        assert "router_trace" in payload


def test_invalid_problem_type_for_skill_raises_value_error() -> None:
    with pytest.raises(ValueError):
        generate_for_skill(
            skill_id="vh_數學B4_FactorialNotation",
            level=1,
            seed=1,
            problem_type_id="combination_group_selection",
        )


def test_router_factorial_generate_success() -> None:
    # 蝣箄????ａ?
    payload = generate_for_skill(skill_id="vh_數學B4_FactorialNotation", level=1, seed=1)
    assert payload is not None
    assert payload["skill_id"] == "vh_數學B4_FactorialNotation"


