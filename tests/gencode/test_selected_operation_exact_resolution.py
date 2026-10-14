# -*- coding: utf-8 -*-
"""Exact selected_operation resolution for confirmed skill bindings."""

from __future__ import annotations

import pytest

from core.gencode.skill_fixed_domain_authority import (
    _resolve_exact_selected_operation,
    resolve_domain_authority,
)
from core.registry.taxonomy_registry import get_allowed_operations, get_fixed_domain_key

ARITH = "vh_數學B1_PolynomialArithmeticOperations"
BASIC = "vh_數學B1_PolynomialBasicConcepts"
EQUAL = "vh_數學B1_PolynomialEquality"
PARALLEL = "vh_數學B1_DistanceBetweenTwoParallelLines"


@pytest.mark.parametrize(
    "skill_id,op",
    [
        (ARITH, "polynomial_long_division"),
        (ARITH, "polynomial_add_sub"),
        (ARITH, "polynomial_multiply"),
        (ARITH, "polynomial_synthetic_division"),
        (EQUAL, "polynomial_equality_identity"),
    ],
)
def test_confirmed_binding_selects_exact_required_operation(skill_id: str, op: str) -> None:
    before_empty = resolve_domain_authority(skill_id)  # no required → must stay empty
    assert before_empty.selected_operation == ""

    result = resolve_domain_authority(skill_id, problem_type_id=op)
    assert result.fixed_domain_key == get_fixed_domain_key(skill_id)
    assert result.selected_operation == op
    assert result.selected_operation == op  # required == selected


def test_induced_spec_problem_type_selects_exact_operation() -> None:
    result = resolve_domain_authority(
        ARITH,
        extra={
            "v3_induced_spec": {
                "classification_status": "resolved",
                "problem_type_id": "polynomial_long_division",
                "required_capabilities": ["polynomial_long_division"],
            }
        },
    )
    assert result.selected_operation == "polynomial_long_division"


def test_missing_op_does_not_fallback() -> None:
    result = resolve_domain_authority(
        ARITH,
        problem_type_id="totally_missing_polynomial_op_xyz",
    )
    assert result.selected_operation == ""
    assert result.fixed_domain_key == "algebra.polynomial"


def test_wrong_domain_op_does_not_cross_route() -> None:
    result = resolve_domain_authority(
        ARITH,
        problem_type_id="two_points",  # line_equation op, not polynomial
    )
    assert result.selected_operation == ""
    assert result.fixed_domain_key == "algebra.polynomial"


def test_empty_required_does_not_guess() -> None:
    result = resolve_domain_authority(ARITH)
    assert result.selected_operation == ""
    helper = _resolve_exact_selected_operation(
        preferred="",
        extra_data={},
        problem_type_id="",
        required_capabilities=[],
        allowed_operations=get_allowed_operations("algebra.polynomial", skill_id=ARITH),
        fixed_domain_key="algebra.polynomial",
    )
    assert helper == ""


def test_unrelated_confirmed_skill_still_selects_exact() -> None:
    op = "distance_between_parallel_lines"
    result = resolve_domain_authority(PARALLEL, problem_type_id=op)
    assert result.fixed_domain_key == "coordinate_geometry.parallel_lines_distance"
    assert result.selected_operation == op


def test_basic_concepts_ops() -> None:
    op = "polynomial_descending_power_properties"
    result = resolve_domain_authority(BASIC, problem_type_id=op)
    assert result.selected_operation == op
