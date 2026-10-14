# -*- coding: utf-8 -*-
"""Exact-readiness coverage for the remaining Math B2 1-2 capabilities."""

from __future__ import annotations

import importlib
from decimal import Decimal

import pytest
import sympy as sp

from core.checkers.expression_equivalence_checker import check_expression_equivalence_debug
from core.domain.trigonometry_acute_domain import (
    build_trigonometry_acute_matrix,
    compute_chord_and_arc_length,
    evaluate_trig_decimal,
    simplify_fundamental_trig_expression,
    solve_acute_trig_constraints,
    solve_right_triangle_projection,
    validate_acute_trigonometry_matrix,
)
from core.gencode.b2_12_capability_adapter import (
    B2_12_EXAMPLE_OPERATION_MAP,
    adapt_b2_12_batch1_matrix,
    audit_b2_12_example_mapping,
)
from core.gencode.checker_registry import validate_answer_contract_capability
from core.gencode.services.failed_component_recovery_service import _has_executable_adapter_route
from core.registry.domain_consistency_validator import validate_domain_operation_registry
from core.registry.domain_operation_registry import get_domain_spec, get_operation_spec
from core.registry.taxonomy_registry import resolve_domain_for_skill


REMAINING_OPERATIONS = (
    "solve_acute_trig_constraints",
    "solve_right_triangle_projection",
    "evaluate_trig_decimal",
    "simplify_fundamental_trig_expression",
    "collinear_three_points_parameter",
    "sector_arc_and_area",
    "compute_chord_and_arc_length",
)


def test_acute_constraints_positive_branch_and_exact_targets() -> None:
    result = solve_acute_trig_constraints(
        known={"tan": sp.Rational(3, 4)},
        targets={"sin": "sin_theta", "cos": "cos_theta"},
    )
    assert result["targets"]["sin"]["canonical"] == "3/5"
    assert result["targets"]["cos"]["canonical"] == "4/5"
    assert all(value.is_positive is True for value in result["solutions"][0].values())


def test_acute_constraints_preserve_genuine_plus_minus_solution_set() -> None:
    result = solve_acute_trig_constraints(
        relations=["sin_theta+cos_theta=sqrt(7)/2"],
        targets={"product": "sin_theta*cos_theta", "difference": "sin_theta-cos_theta"},
    )
    assert result["targets"]["product"]["canonical"] == "3/8"
    assert result["targets"]["difference"]["canonical"] == "{-1/2,1/2}"
    assert result["targets"]["difference"]["unique"] is False


def test_acute_constraints_reject_nonacute_branch() -> None:
    with pytest.raises(ValueError, match="no_positive_solution"):
        solve_acute_trig_constraints(known={"sin": -sp.Rational(3, 5)}, targets=["cos_theta"])


def _choice_constraints() -> dict[str, object]:
    return {
        "known": {"tan": sp.Rational(7, 25)},
        "targets": {"a": "sin_theta*cos_theta"},
        "choice_options": [
            {"label": "A", "semantic": "1/2<a<1", "lower": "1/2", "upper": "1"},
            {"label": "B", "semantic": "0<a<1/2", "lower": "0", "upper": "1/2"},
            {"label": "C", "semantic": "-1/2<a<0", "lower": "-1/2", "upper": "0"},
            {"label": "D", "semantic": "-1<a<-1/2", "lower": "-1", "upper": "-1/2"},
        ],
    }


def test_single_choice_uses_semantic_answer_and_unique_option() -> None:
    matrix = build_trigonometry_acute_matrix(
        seed=1, domain_operation="solve_acute_trig_constraints", constraints=_choice_constraints()
    )
    assert matrix["answer"]["canonical_form"] == "0<a<1/2"
    assert matrix["answer"]["canonical_form"] not in {"A", "B", "C", "D"}
    assert validate_acute_trigonometry_matrix(matrix)
    payload = adapt_b2_12_batch1_matrix(
        matrix,
        domain_operation="solve_acute_trig_constraints",
        presentation_mode="single_choice",
        answer_type="single_choice",
        seed=3,
    )
    assert payload["answer_contract"]["semantic_canonical_answer"] == "0<a<1/2"
    assert payload["answer_contract"]["semantic_choice_unique"] is True
    assert len({choice["text"] for choice in payload["choices"]}) == 4


def test_projection_exact_values_elevation_and_pythagorean_invariant() -> None:
    result = solve_right_triangle_projection(hypotenuse=900, angle=45, base_elevation=500)
    assert result["horizontal_projection"] == 450 * sp.sqrt(2)
    assert result["vertical_projection"] == 450 * sp.sqrt(2)
    assert result["elevation"] == 500 + 450 * sp.sqrt(2)
    assert sp.simplify(result["horizontal_projection"]**2 + result["vertical_projection"]**2 - 900**2) == 0


def test_projection_matrix_contract_has_units() -> None:
    matrix = build_trigonometry_acute_matrix(
        seed=1,
        domain_operation="solve_right_triangle_projection",
        constraints={"hypotenuse": 500, "angle": 30, "length_unit": "m"},
    )
    assert validate_acute_trigonometry_matrix(matrix)
    payload = adapt_b2_12_batch1_matrix(matrix, domain_operation="solve_right_triangle_projection")
    assert payload["answer_contract"]["unit"] == "m"


def test_decimal_degree_minute_normalization_and_rounding() -> None:
    normalized = evaluate_trig_decimal("cos", 38, minutes=49, precision=8)
    carried = evaluate_trig_decimal("sin", 39, minutes=60, precision=9)
    direct = evaluate_trig_decimal("sin", 40, precision=9)
    assert normalized["canonical"] == "0.77915566"
    assert normalized["normalized_degrees"] == sp.Rational(2329, 60)
    assert carried["canonical"] == direct["canonical"] == "0.642787610"
    assert normalized["tolerance"] == Decimal("5E-9")


def test_decimal_matrix_contract_is_explicit_per_part() -> None:
    matrix = build_trigonometry_acute_matrix(
        seed=1,
        domain_operation="evaluate_trig_decimal",
        constraints={"requests": [
            {"function": "sin", "degrees": 40, "precision": 9},
            {"function": "cos", "degrees": 38, "minutes": 49, "precision": 8},
        ]},
    )
    assert validate_acute_trigonometry_matrix(matrix)
    payload = adapt_b2_12_batch1_matrix(matrix, domain_operation="evaluate_trig_decimal")
    parts = payload["answer_contract"]["parts"]
    assert [part["checker"] for part in parts] == ["decimal_tolerance_checker"] * 2
    assert [part["precision"] for part in parts] == [9, 8]
    assert all(part["rounding_policy"] == "ROUND_HALF_UP" for part in parts)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("sin_theta/cos_theta", "tan(theta)"),
        ("tan_theta*cos_theta", "sin(theta)"),
        ("sin_theta**2+cos_theta**2", "1"),
        ("(sin_theta+cos_theta)**2+(sin_theta-cos_theta)**2", "2"),
    ],
)
def test_shared_symbolic_trig_simplification(expression: str, expected: str) -> None:
    theta = sp.symbols("theta", real=True)
    assert sp.trigsimp(simplify_fundamental_trig_expression(expression) - sp.sympify(expected, locals={"theta": theta})) == 0


def test_simplified_required_form_is_ast_based() -> None:
    contract = {"required_form": "simplified_trig"}
    accepted = check_expression_equivalence_debug("sin(theta)", "sin(theta)", answer_contract=contract)
    rejected = check_expression_equivalence_debug("tan(theta)*cos(theta)", "sin(theta)", answer_contract=contract)
    assert accepted["correct"] is True
    assert rejected["correct"] is False and rejected["required_form_failed"] is True


def test_collinear_cross_domain_delegation_and_determinant_invariant() -> None:
    matrix = build_trigonometry_acute_matrix(seed=19, domain_operation="collinear_three_points_parameter")
    assert matrix["validation_facts"]["domain_operation"] == "collinear_three_points_parameter"
    assert validate_acute_trigonometry_matrix(matrix)
    assert "core.domain.coordinate_geometry" in type(matrix).__module__ or matrix["givens"]["parameter_name"]


def test_sector_cross_domain_primitive_delegation() -> None:
    acute = build_trigonometry_acute_matrix(
        seed=1,
        domain_operation="sector_arc_and_area",
        constraints={"variant": "given_angle", "radius": 2, "theta_degrees": 60, "include_convert": False},
    )
    assert acute["answer"]["parts"]["part_1"] == "2*pi/3"
    assert validate_acute_trigonometry_matrix(acute)


def test_chord_and_arc_exact_geometry_and_sector_delegate() -> None:
    result = compute_chord_and_arc_length(radius=2, central_angle=60)
    assert result["chord_length"] == 2
    assert result["arc_length"] == 2 * sp.pi / 3
    assert result["sector_delegate"]["validation_facts"]["domain_operation"] == "sector_arc_and_area"
    assert result["chord_length"] > 0
    assert result["chord_length"] <= 2 * result["radius"]
    matrix = build_trigonometry_acute_matrix(seed=1, domain_operation="compute_chord_and_arc_length")
    assert validate_acute_trigonometry_matrix(matrix)


def test_chord_arc_contract_has_pi_form_and_units() -> None:
    matrix = build_trigonometry_acute_matrix(
        seed=1, domain_operation="compute_chord_and_arc_length",
        constraints={"radius": 2, "central_angle": 60, "length_unit": "m"},
    )
    payload = adapt_b2_12_batch1_matrix(matrix, domain_operation="compute_chord_and_arc_length")
    parts = {part["key"]: part for part in payload["answer_contract"]["parts"]}
    assert parts["arc_length"]["required_form"] == "pi_expression"
    assert all(part["unit"] == "m" for part in parts.values())


def test_all_31_examples_have_one_exact_operation_mapping() -> None:
    audit = audit_b2_12_example_mapping()
    assert audit == {
        "expected_examples": 31,
        "mapped_examples": 31,
        "missing_examples": [],
        "unexpected_examples": [],
        "example_mapping_complete": True,
    }
    assert len(B2_12_EXAMPLE_OPERATION_MAP) == len(set(B2_12_EXAMPLE_OPERATION_MAP)) == 31


def test_taxonomy_routes_each_b2_12_skill_to_required_operations() -> None:
    expected = {
        "vh_數學B2_TrigonometricFunctionsOfAcuteAngles": {
            "compute_right_triangle_trig_ratios", "solve_acute_trig_constraints",
            "simplify_fundamental_trig_expression", "collinear_three_points_parameter",
            "compute_chord_and_arc_length",
        },
        "vh_數學B2_TrigonometricValuesOfSpecialAngles": {
            "evaluate_exact_special_angle_expression", "solve_right_triangle_projection",
        },
        "vh_數學B2_CalculatingFunctionValuesUsingCalculator": {"evaluate_trig_decimal"},
        "vh_數學B2_FundamentalTrigonometricIdentities": {
            "simplify_fundamental_trig_expression", "complete_cofunction_identity",
            "solve_acute_trig_constraints",
        },
    }
    for skill_id, operations in expected.items():
        route = resolve_domain_for_skill(skill_id)
        assert route["fixed_domain_key"] == "trigonometry.acute"
        assert set(route["allowed_operations"]) == operations


@pytest.mark.parametrize("operation", REMAINING_OPERATIONS)
def test_remaining_operation_exact_readiness(operation: str) -> None:
    spec = get_operation_spec("trigonometry.acute", operation)
    domain = get_domain_spec("trigonometry.acute")
    assert spec is not None and domain is not None
    module = importlib.import_module(domain.domain_module)
    assert callable(getattr(module, spec.handler))
    assert callable(getattr(module, spec.validator))
    adapter_module, adapter_name = spec.payload_adapter.rsplit(".", 1)
    assert callable(getattr(importlib.import_module(adapter_module), adapter_name))
    assert spec.runtime_contract and spec.provided_capabilities == (operation,)
    assert _has_executable_adapter_route(
        selected_operation=operation,
        domain_module=domain.domain_module,
        impl_fn_name=spec.handler,
        presentation_mode=spec.supported_presentation_modes[0],
        answer_type=spec.supported_answer_types[0],
    )


def test_registry_and_generated_contracts_have_no_readiness_findings() -> None:
    findings = validate_domain_operation_registry(raise_on_failure=False)
    assert not [finding for finding in findings if finding.get("domain_key") in {"trigonometry.acute", "geometry.similarity"}]
    for operation in REMAINING_OPERATIONS:
        matrix = build_trigonometry_acute_matrix(seed=7, domain_operation=operation)
        assert validate_acute_trigonometry_matrix(matrix)
        payload = adapt_b2_12_batch1_matrix(matrix, domain_operation=operation)
        result = validate_answer_contract_capability(payload["answer_contract"])
        assert result["checker_capability_status"] == "ok", (operation, result)


def test_remaining_operations_are_deterministic_and_valid_for_20_seeds() -> None:
    for operation in REMAINING_OPERATIONS:
        for seed in range(20):
            first = build_trigonometry_acute_matrix(seed=seed, domain_operation=operation)
            second = build_trigonometry_acute_matrix(seed=seed, domain_operation=operation)
            assert first["answer"] == second["answer"], (operation, seed)
            assert validate_acute_trigonometry_matrix(first), (operation, seed)
            payload = adapt_b2_12_batch1_matrix(first, domain_operation=operation, seed=seed)
            assert str(payload.get("question_text") or "").strip(), (operation, seed)
