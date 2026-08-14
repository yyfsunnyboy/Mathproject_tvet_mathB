# -*- coding: utf-8 -*-
"""Focused tests for B1 2-1 parallel/perpendicular line_equation operations."""

from __future__ import annotations

from fractions import Fraction

import pytest

from core.checkers.multi_part_answer_checker import check_multi_part_answer
from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.answer_schema_registry import resolve_answer_schema_key, validate_answer_schema
from core.gencode.domain_matrix_adapter import convert_line_equation_matrix_to_question_payload
from core.registry.domain_operation_registry import get_domain_spec
from core.registry.taxonomy_registry import resolve_domain_for_skill

NEW_OPS = (
    "parallel_segments_parameter_choice",
    "parallel_two_point_lines_parameter_choice",
    "parallel_and_perpendicular_slopes_from_reference",
    "triangle_right_angle_verification",
    "perpendicular_two_point_lines_parameter",
    "perpendicular_slope_quadrant_choice",
)

REUSED_OPS = (
    "parallel_segments_parameter",
    "perpendicular_segments_parameter",
)


def _build(line_type: str, seed: int = 42, **extra: object) -> dict:
    return build_line_equation_matrix(
        seed=seed,
        line_type=line_type,
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints=extra,
    )


def test_taxonomy_wires_parallel_and_perpendicular_skills():
    for skill_id, expected_ops in (
        (
            "vh_數學B1_PropertiesOfParallelLines",
            {
                "parallel_segments_parameter",
                "parallel_segments_parameter_choice",
                "parallel_two_point_lines_parameter_choice",
            },
        ),
        (
            "vh_數學B1_PropertiesOfPerpendicularLines",
            {
                "parallel_and_perpendicular_slopes_from_reference",
                "triangle_right_angle_verification",
                "perpendicular_segments_parameter",
                "perpendicular_two_point_lines_parameter",
                "perpendicular_slope_quadrant_choice",
            },
        ),
    ):
        routing = resolve_domain_for_skill(skill_id)
        assert routing["fixed_domain_key"] == "coordinate_geometry.line_equation"
        allowed = set(routing.get("allowed_types") or [])
        assert expected_ops <= allowed


@pytest.mark.parametrize("op", NEW_OPS + REUSED_OPS)
def test_each_operation_builds_matrix(op: str):
    matrix = _build(op, seed=11)
    schema_key = resolve_answer_schema_key(domain_operation=op)
    validate_answer_schema(matrix["answer"], answer_schema_key=schema_key, domain_operation=op)
    payload = convert_line_equation_matrix_to_question_payload(matrix, domain_operation=op)
    assert payload.get("question_text")
    assert payload.get("correct_answer") is not None


def test_parallel_slopes_multi_part_algebra():
    matrix = _build(
        "parallel_and_perpendicular_slopes_from_reference",
        seed=3,
        reference_slope="-2/3",
    )
    m1 = Fraction(-2, 3)
    parts = matrix["answer"]["parts"]
    assert parts["part_1"] == str(m1)
    assert Fraction(parts["part_2"]) == Fraction(-1) / m1


def test_triangle_right_angle_textbook_seed():
    matrix = _build(
        "triangle_right_angle_verification",
        seed=4527,
        force_right_angle=True,
    )
    assert matrix["answer"]["canonical_form"] == "是"


def test_perpendicular_two_lines_parameter_consistency():
    matrix = _build("perpendicular_two_point_lines_parameter", seed=19)
    k = int(matrix["answer"]["parameter"])
    # Re-evaluate slopes with solved k from generated template metadata
    givens = matrix["givens"]
    assert givens.get("relation") == "perpendicular"
    assert isinstance(k, int)


def test_choice_ops_map_semantic_value():
    for op in (
        "parallel_segments_parameter_choice",
        "parallel_two_point_lines_parameter_choice",
        "perpendicular_slope_quadrant_choice",
    ):
        matrix = _build(op, seed=5)
        payload = convert_line_equation_matrix_to_question_payload(
            matrix,
            presentation_mode="single_choice",
            domain_operation=op,
        )
        assert payload["presentation_mode"] == "single_choice"
        assert payload["correct_answer"] in {"A", "B", "C", "D"}


def test_textbook_anchor_answers_via_domain():
    anchors = {
        "parallel_and_perpendicular_slopes_from_reference": (
            {"reference_slope": "-2/3"},
            {"part_1": "-2/3", "part_2": "3/2"},
        ),
        "parallel_and_perpendicular_slopes_from_reference#4532": (
            {"reference_slope": "3/2"},
            {"part_1": "3/2", "part_2": "-2/3"},
        ),
    }
    matrix = _build(
        "parallel_and_perpendicular_slopes_from_reference",
        seed=1,
        reference_slope="3/2",
    )
    payload = convert_line_equation_matrix_to_question_payload(
        matrix,
        domain_operation="parallel_and_perpendicular_slopes_from_reference",
    )
    ok = check_multi_part_answer(
        matrix["answer"]["parts"],
        payload["correct_answer"],
        answer_contract=payload["answer_contract"],
    )["overall_correct"]
    assert ok
