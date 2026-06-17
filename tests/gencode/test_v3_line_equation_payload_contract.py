# -*- coding: utf-8 -*-
"""Contract tests for line-equation domain payload adapter."""

from __future__ import annotations

from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.domain_matrix_adapter import convert_line_equation_matrix_to_question_payload


def _matrix(**kwargs: object) -> dict[str, object]:
    defaults: dict[str, object] = {
        "seed": 11,
        "line_type": "vertical_line",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy",
    }
    defaults.update(kwargs)
    return build_line_equation_matrix(**defaults)  # type: ignore[arg-type]


def test_short_answer_payload_contract():
    matrix = _matrix()
    payload = convert_line_equation_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        answer_type="expression",
        problem_type_id="write_line_equation_from_point_slope",
        component_id="src_4544",
        textbook_example_id=4544,
    )
    canonical = matrix["answer"]["canonical_form"]
    assert payload["choices"] == []
    assert payload["answer"] == canonical
    assert payload["correct_answer"] == canonical
    assert payload["semantic_answer"] == canonical
    assert payload["answer"] not in {"A", "B", "C", "D"}
    assert payload["metadata"]["presentation_mode"] == "short_answer"
    assert payload["metadata"]["semantic_answer"] == canonical
    assert payload["answer_contract"]["answer_type"] == "expression"
    assert payload["answer_contract"]["checker"] == "linear_equation_equivalent_checker"


def test_single_choice_payload_contract():
    matrix = _matrix()
    payload = convert_line_equation_matrix_to_question_payload(
        matrix,
        presentation_mode="single_choice",
        answer_type="single_choice",
        problem_type_id="write_line_equation_from_point_slope",
        component_id="src_4591",
        textbook_example_id=4591,
    )
    canonical = matrix["answer"]["canonical_form"]
    assert len(payload["choices"]) >= 4
    assert payload["answer"] == payload["correct_answer"]
    assert payload["answer"] in {"A", "B", "C", "D"}
    assert payload["semantic_answer"] == canonical
    assert payload["display_answer"] == canonical
    assert payload["metadata"]["presentation_mode"] == "single_choice"
    assert payload["answer_contract"]["answer_type"] == "single_choice"
    assert payload["answer_contract"]["semantic_answer"] == canonical
