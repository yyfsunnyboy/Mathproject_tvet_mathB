from __future__ import annotations

from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.domain_matrix_adapter import convert_line_equation_matrix_to_question_payload
from core.gencode.question_semantic_validators import validate_source_completeness
from core.gencode.services.v3_question_integrity_validator import validate_component_payload


def _payload(line_type: str, *, mode: str = "short_answer", answer_type: str = "text_short", constraints=None):
    schema = {
        "distance_from_point_to_line": "distance_scalar",
        "distance_from_point_to_line_parameter": "parameter_scalar",
        "distance_from_point_to_line_parameter_single_choice_scalar": "parameter_scalar",
        "compare_point_to_line_distances": "comparison_label",
    }[line_type]
    matrix = build_line_equation_matrix(
        seed=42,
        line_type=line_type,
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints=constraints or {},
    )
    return convert_line_equation_matrix_to_question_payload(
        matrix,
        presentation_mode=mode,
        answer_type=answer_type,
        problem_type_id=line_type,
        answer_schema_key=schema,
        domain_operation=line_type,
    )


def test_distance_equation_serialization_has_single_equals_zero() -> None:
    for line_type in ("distance_from_point_to_line", "distance_from_point_to_line_parameter"):
        payload = _payload(
            line_type,
            answer_type="rational" if line_type == "distance_from_point_to_line" else "text_short",
        )
        text = payload["question_text"].replace(" ", "")
        assert "=0=0" not in text
        assert "=0+" not in text


def test_comparison_contract_respects_farther_intent() -> None:
    payload = _payload(
        "compare_point_to_line_distances",
        mode="single_choice",
        answer_type="single_choice",
        constraints={"target_direction": "farther"},
    )
    contract = payload["answer_contract"]
    assert contract["target_direction"] == "farther"
    assert contract["comparison_result"] == contract["farther_line"]
    assert validate_component_payload(payload)["passed"]


def test_parameter_single_choice_scalar_topology() -> None:
    payload = _payload(
        "distance_from_point_to_line_parameter_single_choice_scalar",
        mode="single_choice",
        answer_type="single_choice",
    )
    contract = payload["answer_contract"]
    assert contract["choice_value_shape"] == "scalar"
    assert contract["solution_cardinality"] == "single"
    assert all("或" not in choice["text"] for choice in payload["choices"])
    assert validate_component_payload(payload)["passed"]


def test_incomplete_parameter_source_requires_human_review() -> None:
    result = validate_source_completeness(
        "若到直線L : 5x - 12y + k = 0的距離為3，試求k值。",
        "distance_from_point_to_line_parameter",
    )
    assert not result["passed"]
    assert "source_incomplete:missing_point_coordinates" in result["blockers"]
