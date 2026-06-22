# -*- coding: utf-8 -*-
"""Tests for canonical answer schema registry and matrix validation."""

from __future__ import annotations

import pytest

from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.answer_schema_registry import (
    ANSWER_SCHEMAS,
    AnswerSchemaMismatchError,
    resolve_answer_schema_key,
    validate_answer_schema,
)
from core.gencode.domain_matrix_adapter import validate_domain_matrix, validate_full_matrix_shell


def _matrix(line_type: str) -> dict:
    return build_line_equation_matrix(
        seed=11,
        line_type=line_type,
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={},
    )


def test_distance_scalar_requires_only_distance():
    schema = ANSWER_SCHEMAS["distance_scalar"]["required_fields"]
    assert schema == frozenset({"distance"})
    validate_answer_schema({"distance": "3"}, answer_schema_key="distance_scalar")


def test_slope_intercept_requires_slope_and_intercept():
    validate_answer_schema(
        {"slope": 2, "intercept": 1},
        answer_schema_key="slope_intercept",
    )


def test_line_equation_requires_canonical_and_general_form():
    validate_answer_schema(
        {"canonical_form": "y = x", "general_form": "x - y = 0"},
        answer_schema_key="line_equation",
    )


def test_unknown_schema_fail_fast():
    with pytest.raises(AnswerSchemaMismatchError, match="answer_schema_unknown"):
        validate_answer_schema({"distance": 1}, answer_schema_key="missing_schema")


def test_no_fallback_to_slope_intercept_for_distance_task():
    matrix = _matrix("distance_from_point_to_line")
    with pytest.raises(AnswerSchemaMismatchError):
        validate_answer_schema(
            matrix["answer"],
            answer_schema_key="slope_intercept",
            component_id="src_1",
            problem_type_id="distance_from_point_to_line",
            domain_operation="distance_from_point_to_line",
        )


def test_point_to_line_distance_does_not_require_slope_intercept():
    matrix = _matrix("distance_from_point_to_line")
    assert validate_domain_matrix(
        matrix,
        component_id="src_1",
        problem_type_id="distance_from_point_to_line",
        domain_operation="distance_from_point_to_line",
    )


def test_slope_intercept_equation_still_validates():
    matrix = _matrix("slope_intercept_equation")
    assert validate_domain_matrix(
        matrix,
        domain_operation="slope_intercept_equation",
        problem_type_id="slope_intercept_equation",
    )


def test_resolve_answer_schema_key_from_domain_operation():
    assert resolve_answer_schema_key(domain_operation="distance_from_point_to_line") == "distance_scalar"


def test_validate_full_matrix_shell_does_not_require_answer_fields():
    matrix = _matrix("distance_from_point_to_line")
    broken = dict(matrix)
    broken["answer"] = {}
    with pytest.raises(AnswerSchemaMismatchError):
        validate_domain_matrix(
            broken,
            domain_operation="distance_from_point_to_line",
        )
    assert validate_full_matrix_shell({**matrix, "answer": {}}) is True
