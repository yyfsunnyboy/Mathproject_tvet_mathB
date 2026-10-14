from __future__ import annotations

import sympy as sp

from core.domain.trigonometry_arbitrary_domain import (
    SUPPORTED_OPERATIONS,
    build_trigonometry_arbitrary_matrix,
    classify_standard_position_angle,
    classify_trig_derived_point_quadrant,
    complete_reference_angle_conversion,
    compute_terminal_ray_trig_ratios,
    evaluate_exact_arbitrary_angle_trig_expression,
    exact_arbitrary_trig_value,
    solve_arbitrary_angle_vertical_projection,
    solve_signed_trig_constraints,
    validate_reference_angle_conversion_ast,
    validate_trigonometry_arbitrary_matrix,
)
from core.gencode.b2_13_capability_adapter import adapt_b2_13_arbitrary_matrix, audit_b2_13_example_mapping
from core.gencode.checker_registry import validate_answer_contract_capability
from core.registry.domain_operation_registry import get_domain_spec
from core.registry.taxonomy_registry import resolve_domain_for_skill


def test_coterminal_classification_and_quadrantal_tangent() -> None:
    assert classify_standard_position_angle(-420)["quadrant"] == 4
    assert classify_standard_position_angle(630)["axis"] == "negative_y"
    ratios = compute_terminal_ray_trig_ratios(x=0, y=-7)
    assert ratios["sin"] == -1 and ratios["cos"] == 0
    assert ratios["tan"] is None and ratios["tan_defined"] is False


def test_terminal_ratios_obey_exact_identities_in_all_quadrants() -> None:
    for x, y in ((3, 4), (-3, 4), (-3, -4), (3, -4)):
        row = compute_terminal_ray_trig_ratios(x=x, y=y)
        assert sp.simplify(row["sin"] ** 2 + row["cos"] ** 2 - 1) == 0
        assert sp.simplify(row["tan"] - row["sin"] / row["cos"]) == 0


def test_signed_constraint_unique_branch_and_identities() -> None:
    result = solve_signed_trig_constraints(known={"sin": sp.Rational(-5, 13)}, signs={"tan": 1})
    row = result["solutions"][0]
    assert result["quadrant"] == 3
    assert row == {"sin": sp.Rational(-5, 13), "cos": sp.Rational(-12, 13), "tan": sp.Rational(5, 12)}
    assert sp.simplify(row["sin"] ** 2 + row["cos"] ** 2 - 1) == 0


def test_exact_special_values_expression_and_reference_conversion() -> None:
    assert exact_arbitrary_trig_value("sin", -930) == sp.Rational(1, 2)
    assert exact_arbitrary_trig_value("cos", 225) == -sp.sqrt(2) / 2
    expression = {"op": "add", "args": [{"trig": "sin", "angle": 30}, {"trig": "cos", "angle": 120}]}
    assert evaluate_exact_arbitrary_angle_trig_expression(expression) == 0
    row = complete_reference_angle_conversion([{"function": "tan", "angle": 300}])[0]
    assert row["reference_degrees"] == 60 and row["sign"] == -1
    assert validate_reference_angle_conversion_ast(
        {"function": "tan", "reference_degrees": sp.Rational(120, 2), "sign": -1}, row
    )


def test_derived_quadrant_and_signed_vertical_projection() -> None:
    point = classify_trig_derived_point_quadrant(
        source={"kind": "angle", "angle": 120},
        x_expression={"trig": "sin", "angle": 120},
        y_expression={"trig": "cos", "angle": 120},
    )
    assert point["quadrant"] == 4
    projection = solve_arbitrary_angle_vertical_projection(radius=50, angle=120, base_elevation=100)
    assert projection["vertical_projection"] == 25 * sp.sqrt(3)
    assert projection["elevation"] == 100 + 25 * sp.sqrt(3)


def test_registry_taxonomy_adapter_contracts_and_matrix_validators() -> None:
    spec = get_domain_spec("trigonometry.arbitrary_angle")
    assert set(spec.operations) == set(SUPPORTED_OPERATIONS)
    for operation in SUPPORTED_OPERATIONS:
        matrix = build_trigonometry_arbitrary_matrix(seed=17, domain_operation=operation)
        assert validate_trigonometry_arbitrary_matrix(matrix)
        payload = adapt_b2_13_arbitrary_matrix(matrix, domain_operation=operation)
        assert payload["answer_contract"]["fixed_domain_key"] == "trigonometry.arbitrary_angle"
        assert payload["answer_contract"]["canonical_answer_contract"]
        assert validate_answer_contract_capability(payload["answer_contract"])["checker_capability_status"] == "ok"
    for suffix in ("1", "2", "4", "5", "6", "7"):
        config = resolve_domain_for_skill(f"vh_數學B2_SubSection_1_3_{suffix}")
        assert config["fixed_domain_key"] == "trigonometry.arbitrary_angle"


def test_all_29_sources_are_mapped_to_exact_ready_shared_operations() -> None:
    assert audit_b2_13_example_mapping() == {
        "expected_examples": 29,
        "mapped_examples": 29,
        "oracle_unavailable": [],
        "example_mapping_complete": True,
    }
    for operation in SUPPORTED_OPERATIONS:
        for seed in range(20):
            first = build_trigonometry_arbitrary_matrix(seed=seed, domain_operation=operation)
            second = build_trigonometry_arbitrary_matrix(seed=seed, domain_operation=operation)
            assert first == second
            assert validate_trigonometry_arbitrary_matrix(first)
