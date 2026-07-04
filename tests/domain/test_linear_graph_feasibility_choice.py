from __future__ import annotations

import pytest

from core.checkers.choice_label_checker import check_choice_label
from core.domain.coordinate_geometry.line_equation_domain import (
    build_linear_graph_feasibility_choice_matrix,
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


@pytest.mark.parametrize("seed", [7, 42, 101])
def test_linear_graph_feasibility_contract(seed: int) -> None:
    matrix = build_linear_graph_feasibility_choice_matrix(seed=seed)
    facts = matrix["validation_facts"]
    condition = facts["graph_condition"]
    candidates = facts["candidate_lines"]
    assert len(candidates) == 4
    assert len({candidate["equation"] for candidate in candidates}) == 4
    for candidate in candidates:
        expected = (
            candidate["slope"] != 0
            and candidate["y_intercept"]
            == condition["required_y_intercept"]
        )
        assert candidate["feasible"] is expected
    impossible = [candidate for candidate in candidates if not candidate["feasible"]]
    assert len(impossible) == 1
    assert impossible[0]["equation"] == matrix["semantic_answer"]
    assert facts["choice_value_to_label"][matrix["semantic_answer"]] == facts["correct_label"]

    schema_key = resolve_answer_schema_key(
        domain_operation="linear_graph_feasibility_choice"
    )
    assert schema_key == "choice_label"
    assert validate_answer_schema(matrix["answer"], answer_schema_key=schema_key)
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="graph_single_choice",
        answer_type="single_choice",
        problem_type_id="linear_graph_feasibility_choice",
        domain_operation="linear_graph_feasibility_choice",
    )
    assert payload["validation_facts"] == facts
    assert payload["visual_spec"]["candidates"] == candidates
    assert payload["answer_contract"]["choice_value_to_label"][payload["semantic_answer"]] == payload["correct_answer"]
    texts = [choice["text"] for choice in payload["choices"]]
    assert check_choice_label(payload["correct_answer"], payload["correct_answer"], texts)
    wrong = next(label for label in "ABCD" if label != payload["correct_answer"])
    assert not check_choice_label(wrong, payload["correct_answer"], texts)
    assert str(condition["required_y_intercept"]) in payload["question_text"]
    assert validate_component_payload(payload)["passed"] is True


def test_registry_exposes_graph_feasibility_operation() -> None:
    spec = get_domain_spec("coordinate_geometry.line_equation")
    operation = spec.operations["linear_graph_feasibility_choice"]
    assert operation.handler == "build_linear_graph_feasibility_choice_matrix"
