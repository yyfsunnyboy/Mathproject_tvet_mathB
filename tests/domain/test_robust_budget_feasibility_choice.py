from __future__ import annotations

import pytest

from core.checkers.choice_label_checker import check_choice_label
from core.domain.coordinate_geometry.line_equation_domain import (
    build_robust_budget_feasibility_choice_matrix,
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
def test_robust_budget_feasibility_contract(seed: int) -> None:
    matrix = build_robust_budget_feasibility_choice_matrix(seed=seed)
    facts = matrix["validation_facts"]
    budget = facts["budget_condition"]["limit"]
    candidates = facts["candidate_plans"]
    assert len({candidate["value"] for candidate in candidates}) == 4
    for candidate in candidates:
        assert candidate["worst_case_cost"] == max(
            candidate["assignment_costs"]
        )
        assert candidate["robust_feasible"] is (
            candidate["worst_case_cost"] <= budget
        )
    feasible = [
        candidate for candidate in candidates if candidate["robust_feasible"]
    ]
    assert len(feasible) == 1
    assert feasible[0]["value"] == matrix["semantic_answer"]
    assert (
        facts["choice_value_to_label"][matrix["semantic_answer"]]
        == facts["correct_label"]
    )

    schema_key = resolve_answer_schema_key(
        domain_operation="robust_budget_feasibility_choice"
    )
    assert schema_key == "choice_label"
    assert validate_answer_schema(matrix["answer"], answer_schema_key=schema_key)
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="single_choice",
        answer_type="single_choice",
        problem_type_id="robust_budget_feasibility_choice",
        domain_operation="robust_budget_feasibility_choice",
    )
    assert payload["validation_facts"] == facts
    assert payload["metadata"]["givens"] == matrix["givens"]
    assert (
        payload["answer_contract"]["choice_value_to_label"][
            payload["semantic_answer"]
        ]
        == payload["correct_answer"]
    )
    texts = [choice["text"] for choice in payload["choices"]]
    assert check_choice_label(
        payload["correct_answer"], payload["correct_answer"], texts
    )
    wrong = next(
        label for label in "ABCD" if label != payload["correct_answer"]
    )
    assert not check_choice_label(wrong, payload["correct_answer"], texts)
    assert str(budget) in payload["question_text"]
    assert validate_component_payload(payload)["passed"] is True


def test_registry_exposes_robust_budget_operation() -> None:
    spec = get_domain_spec("coordinate_geometry.line_equation")
    operation = spec.operations["robust_budget_feasibility_choice"]
    assert operation.handler == "build_robust_budget_feasibility_choice_matrix"
