from __future__ import annotations

import pytest

from core.checkers.choice_label_checker import check_choice_label
from core.domain.coordinate_geometry.line_equation_domain import (
    build_graph_based_linear_model_equation_matrix,
)
from core.gencode.answer_schema_registry import (
    resolve_answer_schema_key,
    validate_answer_schema,
)
from core.gencode.domain_matrix_adapter import (
    convert_domain_matrix_to_question_payload,
)
from core.gencode.services.v3_question_integrity_validator import (
    validate_component_payload,
)
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority
from core.registry.domain_operation_registry import get_domain_spec


@pytest.mark.parametrize("seed", [7, 42, 101])
def test_graph_based_linear_model_contract(seed: int) -> None:
    matrix = build_graph_based_linear_model_equation_matrix(seed=seed)
    facts = matrix["validation_facts"]
    assert facts["intercept"] > 0
    assert facts["x_end"] > 0
    assert all(
        y == 0 if x == facts["x_end"] else y == facts["intercept"]
        for x, y in facts["graph_points"]
    )
    assert matrix["visual_spec"]["points"] == facts["graph_points"]
    assert matrix["visual_spec"]["line"]["intercept"] == facts["intercept"]
    assert matrix["semantic_answer"] == facts["equation"]
    assert len(matrix["choices"]) == 4
    assert len({choice["value"] for choice in matrix["choices"]}) == 4
    assert facts["unique_choices"] is True
    assert facts["unique_correct_choice"] is True

    schema_key = resolve_answer_schema_key(
        domain_operation="graph_based_linear_model_equation"
    )
    assert schema_key == "choice_label"
    assert validate_answer_schema(matrix["answer"], answer_schema_key=schema_key)
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="graph_single_choice",
        answer_type="single_choice",
        problem_type_id="graph_based_linear_model_equation",
        domain_operation="graph_based_linear_model_equation",
    )
    assert payload["validation_facts"] == facts
    assert payload["metadata"]["givens"]["graph_points"] == facts["graph_points"]
    assert payload["answer_type"] == "single_choice"
    assert payload["presentation_mode"] == "graph_single_choice"
    assert payload["answer_contract"]["checker"] == "choice_label_checker"
    assert len(payload["choices"]) == 4
    assert payload["correct_answer"] == facts["correct_label"]
    assert payload["semantic_answer"] == facts["equation"]
    assert check_choice_label(
        payload["correct_answer"],
        payload["correct_answer"],
        payload["choices"],
    )
    wrong_label = next(
        choice["label"]
        for choice in payload["choices"]
        if choice["label"] != payload["correct_answer"]
    )
    assert not check_choice_label(
        wrong_label,
        payload["correct_answer"],
        payload["choices"],
    )
    assert validate_component_payload(payload)["passed"] is True


def test_textbook_intercept_pair_produces_expected_equation() -> None:
    matrix = build_graph_based_linear_model_equation_matrix(
        seed=1,
        constraints={"intercept": 40, "x_end": 400},
    )
    assert matrix["semantic_answer"] == "y=-1/10x+40"
    assert matrix["validation_facts"]["graph_points"] == [[0, 40], [400, 0]]
    assert matrix["visual_spec"]["axis_range"]["x_max"] >= 400
    assert matrix["visual_spec"]["axis_range"]["y_max"] >= 40


def test_registry_exposes_graph_model_operation() -> None:
    spec = get_domain_spec("coordinate_geometry.line_equation")
    operation = spec.operations["graph_based_linear_model_equation"]
    assert operation.handler == "build_graph_based_linear_model_equation_matrix"
    assert operation.supported_answer_types == ("single_choice",)
    assert operation.supported_presentation_modes == ("graph_single_choice",)


def test_exact_capability_ignores_distance_word_fallback() -> None:
    resolution = resolve_domain_authority(
        skill_id="unregistered_test_skill",
        problem_type_id="graph_based_linear_model_equation",
        extra={"required_capabilities": ["graph_based_linear_model_equation"]},
        textbook_example={"problem_text": "行駛距離與剩餘油量的線型函數圖"},
    )
    assert resolution.fixed_domain_key == "coordinate_geometry.line_equation"
