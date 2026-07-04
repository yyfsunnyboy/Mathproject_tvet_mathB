from __future__ import annotations

import pytest

from core.domain.coordinate_geometry.line_equation_domain import (
    build_graph_based_linear_application_inverse_matrix,
)
from core.gencode.answer_payload import grade_numeric_contract_answer
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


@pytest.mark.parametrize("seed", [7, 42, 101])
def test_graph_based_linear_inverse_contract(seed: int) -> None:
    matrix = build_graph_based_linear_application_inverse_matrix(seed=seed)
    facts = matrix["validation_facts"]
    assert facts["slope"] != 0
    assert facts["input_min"] <= facts["target_input"] <= facts["input_max"]
    assert facts["forward_output"] == facts["known_output"]
    assert facts["inverse_solution"] == facts["target_input"]
    assert facts["unique_solution"] is True
    assert matrix["answer"]["canonical_form"] == facts["target_input"]
    assert str(facts["known_output"]) in matrix["question"]

    schema_key = resolve_answer_schema_key(
        domain_operation="graph_based_linear_application_inverse"
    )
    assert schema_key == "numeric_scalar"
    assert validate_answer_schema(matrix["answer"], answer_schema_key=schema_key)
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="graph_short_answer",
        answer_type="numeric",
        problem_type_id="graph_based_linear_application_inverse",
        domain_operation="graph_based_linear_application_inverse",
    )
    assert payload["validation_facts"] == facts
    assert payload["metadata"]["givens"] == matrix["givens"]
    assert payload["answer_contract"]["checker"] == "numeric_checker"
    assert grade_numeric_contract_answer(
        payload["correct_answer"],
        payload["correct_answer"],
        payload["answer_contract"],
    )["correct"]
    assert not grade_numeric_contract_answer(
        facts["target_input"] + 1,
        payload["correct_answer"],
        payload["answer_contract"],
    )["correct"]
    assert validate_component_payload(payload)["passed"] is True


def test_registry_exposes_graph_inverse_operation() -> None:
    spec = get_domain_spec("coordinate_geometry.line_equation")
    operation = spec.operations["graph_based_linear_application_inverse"]
    assert operation.handler == "build_graph_based_linear_application_inverse_matrix"
