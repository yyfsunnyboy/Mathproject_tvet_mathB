# -*- coding: utf-8 -*-
"""Exact Capability Readiness tests for B2 1-2 Batch 1."""

from __future__ import annotations

import importlib
from fractions import Fraction

import pytest
import sympy as sp

from core.domain.geometry_similarity_domain import (
    build_geometry_similarity_matrix,
    solve_proportion,
    validate_similarity_matrix,
)
from core.domain.trigonometry_acute_domain import (
    build_trigonometry_acute_matrix,
    complete_cofunction,
    compute_right_triangle_ratios,
    evaluate_special_angle_terms,
    exact_special_angle_value,
    validate_acute_trigonometry_matrix,
)
from core.gencode.b2_12_capability_adapter import adapt_b2_12_batch1_matrix
from core.gencode.checker_registry import validate_answer_contract_capability
from core.gencode.services.failed_component_recovery_service import _has_executable_adapter_route
from core.registry.domain_consistency_validator import validate_domain_operation_registry
from core.registry.domain_operation_registry import get_domain_spec, get_operation_spec
from core.registry.taxonomy_registry import get_fixed_domain_key, resolve_domain_for_skill


SIMILARITY_OP = "solve_similar_triangle_proportion"
RIGHT_TRIANGLE_OP = "compute_right_triangle_trig_ratios"
SPECIAL_ANGLE_OP = "evaluate_exact_special_angle_expression"
COFUNCTION_OP = "complete_cofunction_identity"


class TestSimilarityOperation:
    def test_exact_proportion_solution(self) -> None:
        assert solve_proportion([3, 4, 6, None]) == Fraction(8)
        assert solve_proportion([None, 10, 6, 15]) == Fraction(4)

    def test_similarity_ratio_invariance(self) -> None:
        base = solve_proportion([3, 5, 9, None])
        scaled = solve_proportion([6, 10, 18, None])
        assert base == 15
        assert scaled == 2 * base
        assert Fraction(3, 5) == Fraction(9, base) == Fraction(18, scaled)

    def test_positive_triangle_side_domain(self) -> None:
        with pytest.raises(ValueError, match="must_be_positive"):
            solve_proportion([3, -4, 6, None])

    def test_matrix_validator_and_determinism(self) -> None:
        first = build_geometry_similarity_matrix(seed=17, domain_operation=SIMILARITY_OP)
        second = build_geometry_similarity_matrix(seed=17, domain_operation=SIMILARITY_OP)
        assert first["answer"] == second["answer"]
        assert validate_similarity_matrix(first)

    def test_registry_and_taxonomy(self) -> None:
        spec = get_operation_spec("geometry.similarity", SIMILARITY_OP)
        assert spec is not None and spec.validator == "validate_similarity_matrix"
        binding = resolve_domain_for_skill("vh_數學B2_RatioAndRatioValue")
        assert binding["fixed_domain_key"] == "geometry.similarity"
        assert binding["allowed_operations"] == [SIMILARITY_OP]

    def test_adapter_and_canonical_answer_contract(self) -> None:
        matrix = build_geometry_similarity_matrix(seed=5, domain_operation=SIMILARITY_OP)
        payload = adapt_b2_12_batch1_matrix(matrix, domain_operation=SIMILARITY_OP)
        contract = payload["answer_contract"]
        assert contract["checker"] == "expression_checker"
        assert contract["answer_equivalence"] == "algebraic_equivalent"
        assert validate_answer_contract_capability(contract)["checker_capability_status"] == "ok"


class TestRightTriangleRatiosOperation:
    def test_exact_three_four_five_ratios(self) -> None:
        result = compute_right_triangle_ratios(opposite=3, adjacent=4, hypotenuse=5)
        assert result == {"sin": sp.Rational(3, 5), "cos": sp.Rational(4, 5), "tan": sp.Rational(3, 4), "hypotenuse": sp.Integer(5)}

    def test_pythagorean_consistency(self) -> None:
        result = compute_right_triangle_ratios(opposite=5, adjacent=12)
        assert sp.simplify(result["hypotenuse"] ** 2 - 5**2 - 12**2) == 0

    def test_trigonometric_invariants(self) -> None:
        result = compute_right_triangle_ratios(opposite=8, adjacent=15)
        assert sp.simplify(result["sin"] ** 2 + result["cos"] ** 2 - 1) == 0
        assert sp.simplify(result["tan"] - result["sin"] / result["cos"]) == 0

    def test_rejects_invalid_right_triangle(self) -> None:
        with pytest.raises(ValueError, match="pythagorean_inconsistent"):
            compute_right_triangle_ratios(opposite=3, adjacent=4, hypotenuse=6)
        with pytest.raises(ValueError, match="must_be_positive"):
            compute_right_triangle_ratios(opposite=0, adjacent=4)

    def test_matrix_validator_and_determinism(self) -> None:
        first = build_trigonometry_acute_matrix(seed=21, domain_operation=RIGHT_TRIANGLE_OP)
        second = build_trigonometry_acute_matrix(seed=21, domain_operation=RIGHT_TRIANGLE_OP)
        assert first["answer"] == second["answer"]
        assert validate_acute_trigonometry_matrix(first)

    def test_adapter_multi_part_math_equivalence(self) -> None:
        matrix = build_trigonometry_acute_matrix(seed=3, domain_operation=RIGHT_TRIANGLE_OP)
        payload = adapt_b2_12_batch1_matrix(matrix, domain_operation=RIGHT_TRIANGLE_OP)
        contract = payload["answer_contract"]
        assert contract["checker"] == "multi_part_answer_checker"
        assert all(part["checker"] in {"integer_checker", "expression_checker"} for part in contract["parts"])
        assert validate_answer_contract_capability(contract)["checker_capability_status"] == "ok"


class TestSpecialAngleOperation:
    def test_exact_special_angle_values(self) -> None:
        assert exact_special_angle_value("sin", 30) == sp.Rational(1, 2)
        assert exact_special_angle_value("cos", 45) == sp.sqrt(2) / 2
        assert exact_special_angle_value("tan", 60) == sp.sqrt(3)

    def test_exact_expression_evaluation(self) -> None:
        terms = [
            {"function": "sin", "angle": 30, "power": 2},
            {"function": "cos", "angle": 30, "power": 2},
        ]
        assert evaluate_special_angle_terms(terms) == 1

    def test_degree_radian_equivalence(self) -> None:
        degree_value = exact_special_angle_value("sin", 30, unit="degree")
        radian_value = exact_special_angle_value("sin", Fraction(1, 6), unit="pi_coefficient")
        assert degree_value == radian_value

    def test_positive_acute_special_angle_domain(self) -> None:
        for angle in (0, 90, -30):
            with pytest.raises(ValueError, match="positive_acute"):
                exact_special_angle_value("sin", angle)
        with pytest.raises(ValueError, match="special_angle_unsupported"):
            exact_special_angle_value("sin", 20)

    def test_matrix_validator_and_determinism(self) -> None:
        first = build_trigonometry_acute_matrix(seed=29, domain_operation=SPECIAL_ANGLE_OP)
        second = build_trigonometry_acute_matrix(seed=29, domain_operation=SPECIAL_ANGLE_OP)
        assert first["answer"] == second["answer"]
        assert validate_acute_trigonometry_matrix(first)

    def test_adapter_uses_symbolic_equivalence(self) -> None:
        matrix = build_trigonometry_acute_matrix(seed=8, domain_operation=SPECIAL_ANGLE_OP)
        payload = adapt_b2_12_batch1_matrix(matrix, domain_operation=SPECIAL_ANGLE_OP)
        contract = payload["answer_contract"]
        assert contract["checker"] == "expression_checker"
        assert contract["answer_equivalence"] == "algebraic_equivalent"
        assert validate_answer_contract_capability(contract)["checker_capability_status"] == "ok"


class TestCofunctionOperation:
    def test_cofunction_symmetry(self) -> None:
        sin_case = complete_cofunction("sin", 25)
        cos_case = complete_cofunction("cos", 65)
        assert sin_case["cofunction"] == "cos"
        assert cos_case["cofunction"] == "sin"
        assert sp.simplify(sin_case["left_value"] - sin_case["right_value"]) == 0
        assert sp.simplify(cos_case["left_value"] - cos_case["right_value"]) == 0

    def test_degree_radian_equivalence(self) -> None:
        degree_case = complete_cofunction("sin", 30, unit="degree")
        radian_case = complete_cofunction("sin", Fraction(1, 6), unit="pi_coefficient")
        assert degree_case == radian_case

    def test_positive_acute_angle_domain(self) -> None:
        with pytest.raises(ValueError, match="positive_acute"):
            complete_cofunction("sin", 90)
        with pytest.raises(ValueError, match="requires_sin_or_cos"):
            complete_cofunction("tan", 30)

    def test_matrix_validator_and_determinism(self) -> None:
        first = build_trigonometry_acute_matrix(seed=31, domain_operation=COFUNCTION_OP)
        second = build_trigonometry_acute_matrix(seed=31, domain_operation=COFUNCTION_OP)
        assert first["answer"] == second["answer"]
        assert validate_acute_trigonometry_matrix(first)

    def test_adapter_has_per_part_non_text_checkers(self) -> None:
        matrix = build_trigonometry_acute_matrix(seed=4, domain_operation=COFUNCTION_OP)
        payload = adapt_b2_12_batch1_matrix(matrix, domain_operation=COFUNCTION_OP)
        parts = payload["answer_contract"]["parts"]
        assert {part["key"]: part["checker"] for part in parts} == {"cofunction": "expression_checker", "complement_degrees": "integer_checker"}
        assert validate_answer_contract_capability(payload["answer_contract"])["checker_capability_status"] == "ok"

    def test_all_four_operations_are_exact_ready(self) -> None:
        targets = {
            "geometry.similarity": (SIMILARITY_OP,),
            "trigonometry.acute": (RIGHT_TRIANGLE_OP, SPECIAL_ANGLE_OP, COFUNCTION_OP),
        }
        findings = validate_domain_operation_registry(raise_on_failure=False)
        assert not [finding for finding in findings if finding.get("domain_key") in targets]
        for domain_key, operations in targets.items():
            domain = get_domain_spec(domain_key)
            assert domain is not None
            module = importlib.import_module(domain.domain_module)
            assert callable(getattr(module, domain.entrypoint))
            for operation in operations:
                spec = get_operation_spec(domain_key, operation)
                assert spec is not None
                assert spec.payload_adapter and spec.validator and spec.runtime_contract
                assert callable(getattr(module, spec.handler))
                assert callable(getattr(module, spec.validator))
                adapter_module_name, adapter_name = spec.payload_adapter.rsplit(".", 1)
                assert callable(getattr(importlib.import_module(adapter_module_name), adapter_name))
                assert _has_executable_adapter_route(
                    selected_operation=operation,
                    domain_module=domain.domain_module,
                    impl_fn_name=spec.handler,
                    presentation_mode=spec.supported_presentation_modes[0],
                    answer_type=spec.supported_answer_types[0],
                )


def test_fixed_domain_keys_are_not_skill_named_duplicates() -> None:
    assert get_fixed_domain_key("vh_數學B2_RatioAndRatioValue") == "geometry.similarity"
    for skill_id in (
        "vh_數學B2_TrigonometricFunctionsOfAcuteAngles",
        "vh_數學B2_TrigonometricValuesOfSpecialAngles",
        "vh_數學B2_FundamentalTrigonometricIdentities",
    ):
        assert get_fixed_domain_key(skill_id) == "trigonometry.acute"
