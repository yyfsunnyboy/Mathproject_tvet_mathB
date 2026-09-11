import pytest
import sympy as sp

from core.domain.trigonometry_acute_domain import evaluate_trig_decimal
from core.domain.trigonometry_function_graph_domain import (
    OPS, analyze_affine_transformed_trig_graph, analyze_tangent_absolute_graph_period,
    build_trigonometry_function_graph_matrix, calculate_trig_period_from_argument_scale,
    classify_trig_equation_feasibility, classify_trig_expression_sign_change,
    compare_trig_values_by_monotonicity, count_sine_cosine_intersections,
    solve_trig_value_quadratic_constraint, validate_trigonometry_function_graph_matrix,
)
from core.gencode.b2_14_capability_adapter import OPERATION_PAYLOAD_CONTRACTS, adapt_b2_14_function_graph_matrix
from core.registry.domain_operation_registry import get_domain_spec, get_operation_spec
from core.registry.taxonomy_registry import resolve_domain_for_skill


def test_compare_exact_degree_and_radian_with_complementary_values():
    result = compare_trig_values_by_monotonicity([
        {"key":"a", "function":"sin", "angle":30},
        {"key":"b", "function":"cos", "angle":sp.pi/3, "unit":"radian"},
        {"key":"c", "function":"sin", "angle":60},
    ])
    assert result["ordered_keys"][:2] == ["a", "b"]
    assert all(row["value"].is_Float is False for row in result["normalized_terms"])


@pytest.mark.parametrize("function,coefficients,expected", [
    ("sin", [1,0,-4], []), ("cos", [2,-1,-1], [sp.Rational(-1,2),1]),
    ("tan", [1,0,-4], [-2,2]),
])
def test_quadratic_root_range_filtering(function, coefficients, expected):
    assert solve_trig_value_quadratic_constraint(function, coefficients)["valid_roots"] == expected


def test_affine_graph_exact_properties_and_negative_scale():
    result = analyze_affine_transformed_trig_graph("sin", -3, -2, sp.pi, 4)
    assert result["amplitude"] == 3 and result["period"] == sp.pi
    assert result["phase_shift"] == sp.pi/2 and result["minimum"] == 1 and result["maximum"] == 7
    assert result["drawing_reference"]["preserve_source_visual"] is True


@pytest.mark.parametrize("function,B,period", [("sin",-3,2*sp.pi/3),("cos",2,sp.pi),("tan",-2,sp.pi/2)])
def test_period_uses_absolute_argument_scale(function, B, period):
    assert calculate_trig_period_from_argument_scale(function,B,7)["period"] == period


def test_period_rejects_zero_scale():
    with pytest.raises(ValueError): calculate_trig_period_from_argument_scale("sin",0)


def test_sign_change_exact_quadrant_boundaries():
    result = classify_trig_expression_sign_change("sin",2,-360,[50,100],"degree")
    assert result["classification"] == "positive_to_negative"
    assert result["endpoint_signs"] == [1,-1]
    assert result["monotonic_direction"] == "decreasing"


def test_feasibility_sin_cos_boundaries_and_tan_range_semantic_choice():
    result = classify_trig_equation_feasibility([
        {"key":"A","function":"sin","value":1}, {"key":"B","function":"cos","value":-1},
        {"key":"C","function":"tan","value":100}, {"key":"D","function":"sin","value":sp.Rational(3,2)},
    ], target="infeasible")
    assert result["canonical_option"] == "D"


def test_absolute_tangent_period_domain_and_range():
    result = analyze_tangent_absolute_graph_period(A=-2,B=-3,C=sp.pi/6,D=5)
    assert result["period"] == sp.pi/3 and result["range"] == "(-oo,5]"
    assert "k" in result["domain_exclusion"]


def test_decimal_arbitrary_degree_minute_and_acute_regression():
    assert evaluate_trig_decimal("sin",390,minutes=0,precision=6)["canonical"] == "0.500000"
    assert evaluate_trig_decimal("cos",38,minutes=49,precision=8)["canonical"]
    assert evaluate_trig_decimal("sin",39,minutes=60,precision=9)["canonical"] == evaluate_trig_decimal("sin",40,precision=9)["canonical"]
    with pytest.raises(ValueError): evaluate_trig_decimal("tan",90,precision=6)


def test_intersection_closed_endpoints_and_duplicate_removal():
    result = count_sine_cosine_intersections(1,0,[sp.pi/4,9*sp.pi/4])
    assert result["solutions"] == [sp.pi/4,5*sp.pi/4,9*sp.pi/4]
    assert result["count"] == 3
    reversed_result = count_sine_cosine_intersections(-1,0,[-9*sp.pi/4,-sp.pi/4])
    assert len(reversed_result["solutions"]) == len(set(reversed_result["solutions"]))


def test_registry_taxonomy_adapter_and_deterministic_matrix_contract():
    spec = get_domain_spec("trigonometry.function_graph")
    assert spec and set(spec.operations) == set(OPS)
    for operation in OPS:
        op = get_operation_spec("trigonometry.function_graph",operation)
        assert op and op.payload_adapter and op.validator and op.runtime_contract
        assert operation in OPERATION_PAYLOAD_CONTRACTS
        assert OPERATION_PAYLOAD_CONTRACTS[operation]["input_schema"]["fields"]
        assert OPERATION_PAYLOAD_CONTRACTS[operation]["output_schema"]["answer"] == "canonical_exact"
    for index in range(1,5):
        route = resolve_domain_for_skill(f"vh_數學B2_SubSection_1_4_{index}")
        assert route["fixed_domain_key"] == "trigonometry.function_graph"
        assert set(route["allowed_operations"]) == set(OPS)
    matrix = build_trigonometry_function_graph_matrix(operation="calculate_trig_period_from_argument_scale", function="cos", B=-2, C=3)
    assert validate_trigonometry_function_graph_matrix(matrix)
    payload = adapt_b2_14_function_graph_matrix(matrix, domain_operation="calculate_trig_period_from_argument_scale")
    assert payload["answer_contract"]["fixed_domain_key"] == "trigonometry.function_graph"


def test_no_example_specific_domain_functions():
    import core.domain.trigonometry_function_graph_domain as module
    assert not [name for name in vars(module) if name.startswith("src_116")]
