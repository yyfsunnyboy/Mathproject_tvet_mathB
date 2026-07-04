from __future__ import annotations

import pytest

from core.domain.coordinate_geometry.line_equation_domain import (
    build_draw_constant_function_graph_matrix,
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
from core.registry.domain_operation_registry import get_domain_spec
from core.services.drawing_answer_analysis_service import evaluate_line_graph


@pytest.mark.parametrize("seed", [7, 42, 101])
def test_constant_function_graph_contract_and_checker(seed: int) -> None:
    matrix = build_draw_constant_function_graph_matrix(seed=seed)
    spec = matrix["expected_drawing_spec"]
    constant = matrix["givens"]["constant"]
    assert matrix["answer"] == matrix["semantic_answer"] == spec
    assert spec["slope"] == 0
    assert spec["y_intercept"] == constant
    assert all(point[1] == constant for point in spec["expected_line"]["points"])
    assert str(constant) in matrix["question"]
    assert matrix["visual_spec"]["axis_range"] == spec["axis_range"]

    schema_key = resolve_answer_schema_key(
        domain_operation="draw_constant_function_graph"
    )
    assert schema_key == "drawing_spec"
    assert validate_answer_schema(matrix["answer"], answer_schema_key=schema_key)

    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="canvas",
        answer_type="drawing",
        problem_type_id="draw_constant_function_graph",
        domain_operation="draw_constant_function_graph",
    )
    contract = payload["answer_contract"]
    ui_contract = contract["ui_contract"]
    assert contract["checker"] == "free_response_drawing_checker"
    assert contract["expected_drawing_spec"] == spec
    assert ui_contract == {
        "response_mode": "drawing",
        "drawing_required": True,
        "ai_check_required": True,
        "text_answer_enabled": False,
        "text_input_enabled": False,
        "submit_button_enabled": False,
        "normal_submit_enabled": False,
        "success_dialog_required": True,
        "canvas_required": True,
        "allow_image_upload": False,
        "allow_text_answer": False,
    }
    assert validate_component_payload(payload)["passed"] is True

    correct = {
        "required_elements": {
            "x_axis": True,
            "y_axis": True,
            "function_line": True,
        },
        "line": {
            "detected": True,
            "slope": 0.02,
            "y_intercept": constant + 0.1,
            "spans_graph_width": True,
        },
        "confidence": 0.95,
    }
    wrong = {
        **correct,
        "line": {
            **correct["line"],
            "slope": 1.0,
        },
    }
    assert evaluate_line_graph(correct, spec)["is_correct"] is True
    assert evaluate_line_graph(wrong, spec)["is_correct"] is False


def test_registry_exposes_constant_function_graph_operation() -> None:
    spec = get_domain_spec("coordinate_geometry.line_equation")
    operation = spec.operations["draw_constant_function_graph"]
    assert operation.handler == "build_draw_constant_function_graph_matrix"
    assert operation.provided_capabilities == ("draw_constant_function_graph",)
