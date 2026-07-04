from __future__ import annotations

import pytest

from core.checkers.choice_label_checker import check_choice_label
from core.checkers.linear_equation_equivalent_checker import (
    check_linear_equation_equivalent_answer,
)
from core.domain.coordinate_geometry.line_equation_domain import (
    build_linear_equation_from_two_points_choice_matrix,
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


def _assert_points_on_line(facts: dict[str, object]) -> None:
    for point in (facts["point_1"], facts["point_2"]):
        x, y = point
        if facts["line_kind"] == "vertical":
            assert x == facts["x_constant"]
        else:
            assert y == facts["slope"] * x + facts["intercept"]


@pytest.mark.parametrize("seed", [7, 42, 101])
def test_two_points_choice_contract(seed: int) -> None:
    matrix = build_linear_equation_from_two_points_choice_matrix(seed=seed)
    facts = matrix["validation_facts"]
    _assert_points_on_line(facts)
    values = [choice["value"] for choice in matrix["choices"]]
    assert len(values) == len(set(values)) == 4
    equivalent = [
        value
        for value in values
        if check_linear_equation_equivalent_answer(value, facts["equation"])
    ]
    assert equivalent == [facts["equation"]]
    assert facts["choice_value_to_label"][facts["equation"]] == facts["correct_label"]
    assert matrix["semantic_answer"] == facts["equation"]

    schema_key = resolve_answer_schema_key(
        domain_operation="linear_equation_from_two_points_choice"
    )
    assert schema_key == "choice_label"
    assert validate_answer_schema(matrix["answer"], answer_schema_key=schema_key)
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="single_choice",
        answer_type="single_choice",
        problem_type_id="linear_equation_from_two_points_choice",
        domain_operation="linear_equation_from_two_points_choice",
    )
    option_texts = [choice["text"] for choice in payload["choices"]]
    assert payload["validation_facts"] == facts
    assert payload["semantic_answer"] == facts["equation"]
    assert payload["answer_contract"]["choice_value_to_label"][facts["equation"]] == payload["correct_answer"]
    assert check_choice_label(
        payload["correct_answer"],
        payload["correct_answer"],
        option_texts,
    )
    wrong_label = next(label for label in "ABCD" if label != payload["correct_answer"])
    assert not check_choice_label(
        wrong_label,
        payload["correct_answer"],
        option_texts,
    )
    assert validate_component_payload(payload)["passed"] is True


@pytest.mark.parametrize("line_kind", ["vertical", "horizontal", "oblique"])
def test_two_points_choice_boundaries(line_kind: str) -> None:
    matrix = build_linear_equation_from_two_points_choice_matrix(
        seed=7,
        constraints={"line_kind": line_kind, "offset": 2, "slope": -2},
    )
    _assert_points_on_line(matrix["validation_facts"])


def test_registry_exposes_two_points_choice_operation() -> None:
    spec = get_domain_spec("coordinate_geometry.line_equation")
    operation = spec.operations["linear_equation_from_two_points_choice"]
    assert operation.handler == "build_linear_equation_from_two_points_choice_matrix"
