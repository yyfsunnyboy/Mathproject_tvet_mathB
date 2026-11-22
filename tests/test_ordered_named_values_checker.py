"""Ordered named multi-value answers (a=0,b=3) — student-friendly input forms."""

from __future__ import annotations

import pytest

from core.checkers.coordinate_pair_checker import check_coordinate_pair_answer
from core.checkers.expression_equivalence_checker import (
    check_expression_equivalence_answer,
    ordered_variable_names_from_expected,
)
from core.checkers.multi_part_answer_checker import check_multi_part_answer


@pytest.mark.parametrize(
    "student",
    [
        "0,3",
        "0，3",
        "0 3",
        "0\u30003",
        "(0,3)",
        "a=0,b=3",
        "a = 0, b = 3",
        "a=0 b=3",
        "b=3,a=0",
    ],
)
def test_ordered_named_values_accepts_friendly_forms(student: str) -> None:
    assert check_expression_equivalence_answer(student, "a=0,b=3") is True


@pytest.mark.parametrize(
    "student",
    [
        "3,0",
        "3 0",
        "a=3,b=0",
        "0",
        "0,3,4",
        "",
        "c=0,d=3",
        "a=0",
        "4x^2+4x-2",
        "x+1",
    ],
)
def test_ordered_named_values_rejects_wrong_or_unsafe(student: str) -> None:
    assert check_expression_equivalence_answer(student, "a=0,b=3") is False


@pytest.mark.parametrize(
    ("student", "canonical"),
    [
        ("-2 5", "a=-2,b=5"),
        ("1/2 -3/4", "a=1/2,b=-3/4"),
        ("0.5 -1.25", "a=0.5,b=-1.25"),
        ("a=-2,b=5", "a=-2,b=5"),
        ("2/4, -6/8", "a=1/2,b=-3/4"),
    ],
)
def test_ordered_named_values_negatives_fractions_decimals(student: str, canonical: str) -> None:
    assert check_expression_equivalence_answer(student, canonical) is True


def test_unordered_value_list_still_accepts_reordered_or() -> None:
    assert check_expression_equivalence_answer("21,1", "1 或 21") is True


def test_algebra_not_split_by_spaces_against_assignment() -> None:
    assert check_expression_equivalence_answer("4x^2 + 4x - 2", "a=0,b=3") is False


def test_variable_order_helper() -> None:
    assert ordered_variable_names_from_expected("a=0,b=3") == ["a", "b"]
    assert ordered_variable_names_from_expected("0,3") is None


def test_contract_variable_order_with_unlabeled_canonical() -> None:
    ac = {"variable_order": ["a", "b"], "answer_shape": "ordered_named_values"}
    assert check_expression_equivalence_answer("0 3", "0,3", answer_contract=ac) is True
    assert check_expression_equivalence_answer("3 0", "0,3", answer_contract=ac) is False


def test_coordinate_pair_accepts_whitespace_pair() -> None:
    assert check_coordinate_pair_answer("2 3", "(2,3)") is True
    assert check_coordinate_pair_answer("3 2", "(2,3)") is False


def test_adapter_annotates_ordered_named_values() -> None:
    from core.gencode.domain_matrix_adapter import _multi_part_contract_parts

    parts = _multi_part_contract_parts({"part_1": "a=0,b=3", "part_2": "4x^2+4x-2"})
    assert parts[0].get("variable_order") == ["a", "b"]
    assert parts[0].get("answer_shape") == "ordered_named_values"
    assert "variable_order" not in parts[1]


def test_polynomial_param_degree_multipart_runtime_path() -> None:
    import re

    from agent_skills_v3.vh_數學B1_PolynomialBasicConcepts.components.src_4610.generate import (
        generate,
    )

    payload = generate(seed=42)
    ac = payload["answer_contract"]
    part1 = ac["parts"][0]
    assert part1.get("variable_order") == ["a", "b"]
    assert part1.get("answer_shape") == "ordered_named_values"
    expected = str(part1["expected_answer"])
    vals = dict(re.findall(r"([ab])=(-?\d+(?:\.\d+)?)", expected))
    a, b = vals["a"], vals["b"]
    poly = ac["parts"][1]["expected_answer"]

    ok = check_multi_part_answer(
        {"part_1": f"{a} {b}", "part_2": poly},
        None,
        answer_contract=ac,
        payload=payload,
    )
    assert ok["overall_correct"] is True
    assert ok["failed_parts"] == []

    partial = check_multi_part_answer(
        {"part_1": f"{b} {a}", "part_2": poly},
        None,
        answer_contract=ac,
        payload=payload,
    )
    assert partial["overall_correct"] is False
    assert partial["failed_parts"] == ["part_1"]
    assert partial["per_part_results"][1]["correct"] is True

    partial2 = check_multi_part_answer(
        {"part_1": f"{a},{b}", "part_2": "x"},
        None,
        answer_contract=ac,
        payload=payload,
    )
    assert partial2["overall_correct"] is False
    assert "part_2" in partial2["failed_parts"]