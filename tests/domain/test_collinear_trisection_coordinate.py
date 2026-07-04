from __future__ import annotations

import pytest

from core.checkers.coordinate_pair_checker import check_coordinate_pair_answer
from core.gencode.answer_schema_registry import (
    resolve_answer_schema_key,
    validate_answer_schema,
)
from core.gencode.division_point_slot_engine import (
    build_collinear_trisection_coordinate_matrix,
    generate_division_point_payload,
)
from core.gencode.domain_matrix_adapter import (
    convert_domain_matrix_to_question_payload,
)
from core.gencode.services.v3_question_integrity_validator import (
    validate_component_payload,
)
from core.registry.domain_operation_registry import get_domain_spec


@pytest.mark.parametrize("seed", [7, 42, 101])
def test_collinear_trisection_coordinate_contract(seed: int) -> None:
    matrix = build_collinear_trisection_coordinate_matrix(seed=seed)
    facts = matrix["validation_facts"]
    point_a, point_b = facts["point_a"], facts["point_b"]
    point_c, point_d = facts["point_c"], facts["point_d"]

    assert point_b == (
        (2 * point_a[0] + point_d[0]) // 3,
        (2 * point_a[1] + point_d[1]) // 3,
    )
    assert point_c == (
        (point_a[0] + 2 * point_d[0]) // 3,
        (point_a[1] + 2 * point_d[1]) // 3,
    )
    vector_ad = (point_d[0] - point_a[0], point_d[1] - point_a[1])
    for point in (point_b, point_c):
        vector_ap = (point[0] - point_a[0], point[1] - point_a[1])
        assert vector_ad[0] * vector_ap[1] == vector_ad[1] * vector_ap[0]
    assert facts["ratios"] == {"AB:BD": "1:2", "AC:CD": "2:1"}
    midpoint = (
        (point_a[0] + point_d[0]) / 2,
        (point_a[1] + point_d[1]) / 2,
    )
    assert point_b != midpoint
    assert point_c != midpoint

    schema_key = resolve_answer_schema_key(
        domain_operation="collinear_trisection_coordinate"
    )
    assert schema_key == "coordinate_pair"
    assert validate_answer_schema(matrix["answer"], answer_schema_key=schema_key)
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        answer_type="coordinate_pair",
        problem_type_id="collinear_trisection_coordinate",
        domain_operation="collinear_trisection_coordinate",
    )
    contract = payload["answer_contract"]
    assert contract["checker"] == "coordinate_pair_checker"
    assert contract["answer_equivalence"] == "coordinate_pair_equivalence"
    assert check_coordinate_pair_answer(
        payload["correct_answer"],
        payload["correct_answer"],
    )
    assert not check_coordinate_pair_answer(
        f"({point_b[0]}, {point_b[1]})",
        payload["correct_answer"],
    )
    assert str(point_a) in payload["question_text"]
    assert str(point_d) in payload["question_text"]
    assert validate_component_payload(payload)["passed"] is True


def test_registry_exposes_collinear_trisection_operation() -> None:
    spec = get_domain_spec("coordinate_geometry.division_point_coordinates")
    operation = spec.operations["collinear_trisection_coordinate"]
    assert operation.handler == "build_collinear_trisection_coordinate_matrix"


def test_generic_entrypoint_preserves_trisection_semantic_facts() -> None:
    matrix = generate_division_point_payload(
        skill_id="test_skill",
        problem_type_id="collinear_trisection_coordinate",
        spec={},
        seed=7,
    )
    assert set(matrix["validation_facts"]) >= {
        "point_a",
        "point_b",
        "point_c",
        "point_d",
        "ratios",
    }
