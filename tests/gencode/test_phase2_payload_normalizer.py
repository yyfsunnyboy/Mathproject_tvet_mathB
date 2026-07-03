# -*- coding: utf-8 -*-
from __future__ import annotations

import pytest
from core.gencode.domain_matrix_adapter import (
    normalize_domain_payload_to_v3_matrix,
    validate_domain_matrix,
)


def test_v3_matrix_preserved() -> None:
    # A complete V3 matrix should be returned unchanged
    v3_matrix = {
        "givens": {"x1": 1, "y1": 2},
        "answer": {
            "point": "(3, 4)",
        },
        "distractors": ["(1, 2)"],
        "explanation_steps": ["Step 1", "Step 2"],
        "validation_facts": {
            "domain_operation": "compute_midpoint_coordinates",
            "curriculum_profile": "voc1",
            "difficulty_profile": "easy",
        },
        "visual_spec": {
            "kind": "coordinate_plane_spec",
            "points": [],
            "lines": [],
            "x_range": [-10, 10],
            "y_range": [-10, 10],
        },
        "custom_extra_key": "some_extra_value",
    }
    context = {"presentation_mode": "short_answer", "problem_type_id": "compute_midpoint_coordinates"}
    res = normalize_domain_payload_to_v3_matrix(v3_matrix, context)
    assert res == v3_matrix
    assert res["custom_extra_key"] == "some_extra_value"


def test_legacy_short_answer_coordinate_pair() -> None:
    legacy_payload = {
        "skill_id": "vh_數學B1_MidpointCoordinates",
        "problem_type_id": "compute_midpoint_coordinates",
        "question_text": "已知 A(1, 2) 和 B(5, 6)，求中點 M 的座標。",
        "answer": "(3, 4)",
        "correct_answer": "(3, 4)",
        "explanation": "M = (3, 4)",
        "metadata": {
            "x1": 1,
            "y1": 2,
            "x2": 5,
            "y2": 6,
        },
    }
    context = {
        "presentation_mode": "short_answer",
        "problem_type_id": "compute_midpoint_coordinates",
        "fixed_domain_key": "coordinate_geometry.division_point_coordinates",
    }
    normalized = normalize_domain_payload_to_v3_matrix(legacy_payload, context)
    
    # Check that it passes validate_domain_matrix
    assert validate_domain_matrix(normalized, domain_operation="compute_midpoint_coordinates")

    # Check strict answer fields
    assert "point" in normalized["answer"]
    assert len(normalized["answer"]) == 1  # ONLY "point" field is allowed for coordinate_pair!
    assert normalized["answer"]["point"] == "(3, 4)"
    
    # Check visual_spec
    assert normalized["visual_spec"]["kind"] == "coordinate_plane_spec"


def test_legacy_short_answer_numeric_scalar() -> None:
    # A numeric scalar operation (e.g. distance from origin)
    legacy_payload = {
        "question_text": "已知點 P(3, 4)，求點 P 到原點的距離。",
        "answer": "5",
        "correct_answer": "5",
        "explanation": "OP = sqrt(3^2 + 4^2) = 5",
        "metadata": {"x": 3, "y": 4},
        "answer_type": "numeric",
    }
    context = {
        "presentation_mode": "short_answer",
        "problem_type_id": "compute_section_point_distance_from_origin",
        "fixed_domain_key": "coordinate_geometry.division_point_coordinates",
    }
    normalized = normalize_domain_payload_to_v3_matrix(legacy_payload, context)
    assert validate_domain_matrix(normalized, domain_operation="compute_section_point_distance_from_origin")

    # For distance_scalar / numeric_scalar, only "distance" (or "canonical_form") is allowed
    # Our registration maps compute_section_point_distance_from_origin to distance_scalar
    assert "distance" in normalized["answer"]
    assert len(normalized["answer"]) == 1
    assert normalized["answer"]["distance"] == "5"


def test_legacy_single_choice_choice_label() -> None:
    legacy_payload = {
        "question_text": "若 A(1, 2) 且 B(5, 6)，求中點。",
        "answer": "A",
        "correct_answer": "A",
        "choices": [
            {"text": "(3, 4)", "label": "A"},
            {"text": "(1, 2)", "label": "B"},
            {"text": "(5, 6)", "label": "C"},
        ],
        "explanation": "M = (3, 4)",
        "answer_type": "single_choice",
    }
    context = {
        "presentation_mode": "single_choice",
        "problem_type_id": "compute_midpoint_coordinates",
        "fixed_domain_key": "coordinate_geometry.division_point_coordinates",
    }
    normalized = normalize_domain_payload_to_v3_matrix(legacy_payload, context)
    # The registration mapped operation + presentation to choice_label
    assert validate_domain_matrix(normalized, domain_operation="compute_midpoint_coordinates", answer_schema_key="choice_label")
    assert "correct_label" in normalized["answer"]
    assert len(normalized["answer"]) == 1
    assert normalized["answer"]["correct_label"] == "A"
    assert normalized["distractors"] == ["(1, 2)", "(5, 6)"]


def test_no_visual_algebra_domain() -> None:
    # A legacy algebra absolute value engine payload (non-coordinate, no visual)
    algebra_payload = {
        "question_text": "數線上，若|x|=8，試求x之值。",
        "answer": "-8, 8",
        "correct_answer": "-8, 8",
        "explanation": "x = 8 或 x = -8。",
        "metadata": {"rhs": 8},
        "answer_type": "solution_set",
    }
    context = {
        "presentation_mode": "short_answer",
        "problem_type_id": "solve_basic_absolute_value_equation",
        "fixed_domain_key": "algebra.absolute_value",
    }
    normalized = normalize_domain_payload_to_v3_matrix(algebra_payload, context)
    assert validate_domain_matrix(normalized, domain_operation="solve_basic_absolute_value_equation")
    
    # Check visual_spec is no_visual!
    assert normalized["visual_spec"] == {"kind": "no_visual"}
    # Check parameter_solution_set schema mapping
    assert "solutions" in normalized["answer"]
    assert len(normalized["answer"]) == 1
    assert normalized["answer"]["solutions"] == ["-8", "8"]


def test_unresolved_answer_schema_raises_error() -> None:
    payload = {
        "question_text": "Some question",
        "answer": "abc",
    }
    context = {
        "presentation_mode": "short_answer",
        "problem_type_id": "unknown_random_op_without_registration",
    }
    with pytest.raises(ValueError) as excinfo:
        normalize_domain_payload_to_v3_matrix(payload, context)
    assert "domain_payload_answer_schema_unresolved" in str(excinfo.value)
