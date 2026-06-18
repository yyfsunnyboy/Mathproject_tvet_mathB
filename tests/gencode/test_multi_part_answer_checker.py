from __future__ import annotations

from core.checkers.multi_part_answer_checker import check_multi_part_answer
from core.gencode.answer_payload import is_valid_answer_payload, validate_generated_answer_shape
from core.gencode.checker_registry import validate_answer_contract_capability
from core.gencode.runtime_skill_wrapper import check_answer


def _equation_area_contract() -> dict:
    return {
        "answer_type": "multi_part",
        "answer_shape": "multi_part",
        "answer_equivalence": "multi_part_answer",
        "equivalence_type": "multi_part_answer",
        "checker": "multi_part_answer_checker",
        "checker_key": "multi_part_answer_checker",
        "parts": [
            {
                "key": "equation",
                "label": "equation",
                "checker": "linear_equation_equivalent_checker",
                "equivalence_type": "linear_equation_equivalent",
                "expected_answer": "x + y - 6 = 0",
            },
            {
                "key": "area",
                "label": "area",
                "checker": "numeric_checker",
                "equivalence_type": "numeric_exact",
                "expected_answer": "12",
            },
        ],
    }


def test_multi_part_equation_and_area_all_correct() -> None:
    ac = _equation_area_contract()
    result = check_multi_part_answer(
        {"equation": "y = -x + 6", "area": "12"},
        {"equation": "x + y - 6 = 0", "area": "12"},
        answer_contract=ac,
    )

    assert result["overall_correct"] is True
    assert result["failed_parts"] == []
    assert [row["key"] for row in result["per_part_results"]] == ["equation", "area"]
    assert result["normalized_student_answer"] == {"equation": "y = -x + 6", "area": "12"}
    assert result["normalized_correct_answer"] == {"equation": "x + y - 6 = 0", "area": "12"}
    assert check_answer({"equation": "y = -x + 6", "area": "12"}, {}, answer_contract=ac)


def test_multi_part_equation_correct_area_wrong_reports_area() -> None:
    ac = _equation_area_contract()
    result = check_multi_part_answer(
        {"equation": "y = -x + 6", "area": "10"},
        {},
        answer_contract=ac,
    )

    assert result["overall_correct"] is False
    assert result["failed_parts"] == ["area"]
    assert result["per_part_results"][1]["reason"] == "incorrect"


def test_multi_part_equation_wrong_area_correct_reports_equation() -> None:
    ac = _equation_area_contract()
    result = check_multi_part_answer(
        {"equation": "y = x + 6", "area": "12"},
        {},
        answer_contract=ac,
    )

    assert result["overall_correct"] is False
    assert result["failed_parts"] == ["equation"]
    assert result["per_part_results"][0]["reason"] == "incorrect"


def test_multi_part_missing_part_reports_missing_key() -> None:
    ac = _equation_area_contract()
    result = check_multi_part_answer(
        {"equation": "y = -x + 6"},
        {},
        answer_contract=ac,
    )

    assert result["overall_correct"] is False
    assert result["failed_parts"] == ["area"]
    assert result["per_part_results"][1]["reason"] == "missing_part"


def test_multi_part_contract_registry_and_payload_shape() -> None:
    ac = _equation_area_contract()

    assert validate_answer_contract_capability(ac)["checker_capability_status"] == "ok"
    ok, reason = is_valid_answer_payload({"equation": "x + y = 6", "area": "12"}, ac)
    assert ok, reason
    ok2, blockers, _ = validate_generated_answer_shape(
        {
            "answer": {"equation": "x + y = 6", "area": "12"},
            "correct_answer": {"equation": "x + y = 6", "area": "12"},
        },
        answer_contract=ac,
    )
    assert ok2, blockers


def test_existing_single_answer_checkers_are_unchanged() -> None:
    linear_ac = {
        "answer_type": "equation",
        "answer_shape": "linear_equation",
        "equivalence_type": "linear_equation_equivalent",
        "checker": "linear_equation_equivalent_checker",
    }
    numeric_ac = {
        "answer_type": "numeric",
        "equivalence_type": "numeric_exact",
        "checker": "numeric_checker",
    }
    rational_ac = {
        "answer_type": "rational",
        "equivalence_type": "rational_equivalent",
        "checker": "rational_checker",
    }
    choice_ac = {
        "answer_type": "single_choice",
        "equivalence_type": "choice_label",
        "checker": "choice_label_checker",
        "presentation_mode": "single_choice",
    }

    assert check_answer("y=-x+6", "x + y - 6 = 0", answer_contract=linear_ac)
    assert check_answer("12", "12", answer_contract=numeric_ac)
    assert check_answer("2/4", "1/2", answer_contract=rational_ac)
    assert check_answer("A", "A", payload={"choices": ["one", "two"]}, answer_contract=choice_ac)
