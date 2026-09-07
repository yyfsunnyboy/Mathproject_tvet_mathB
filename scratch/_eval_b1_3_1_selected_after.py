# -*- coding: utf-8 -*-
"""Re-evaluate 3-1 selected_operation_match after exact resolution fix."""
from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8")

from core.gencode.skill_fixed_domain_authority import resolve_domain_authority
from core.gencode.services.failed_component_recovery_service import (
    _has_executable_adapter_route,
)

OPS = [
    ("vh_數學B1_PolynomialBasicConcepts", "polynomial_descending_power_properties"),
    ("vh_數學B1_PolynomialBasicConcepts", "polynomial_param_degree_constraint"),
    ("vh_數學B1_PolynomialBasicConcepts", "polynomial_descending_power_table"),
    ("vh_數學B1_PolynomialBasicConcepts", "zero_polynomial_find_coeffs"),
    ("vh_數學B1_PolynomialBasicConcepts", "polynomial_degree_product_sum"),
    ("vh_數學B1_PolynomialArithmeticOperations", "polynomial_add_sub"),
    ("vh_數學B1_PolynomialArithmeticOperations", "polynomial_multiply"),
    ("vh_數學B1_PolynomialArithmeticOperations", "polynomial_product_term_coefficient"),
    ("vh_數學B1_PolynomialArithmeticOperations", "polynomial_long_division"),
    ("vh_數學B1_PolynomialArithmeticOperations", "polynomial_synthetic_division"),
    ("vh_數學B1_PolynomialArithmeticOperations", "polynomial_remainder_param_solve"),
    ("vh_數學B1_PolynomialArithmeticOperations", "polynomial_shifted_basis_eval"),
    ("vh_數學B1_PolynomialEquality", "polynomial_equality_identity"),
]

print("op\trequired\tselected\tmatch\tadapter")
all_match = True
for skill, op in OPS:
    # before behavior was empty on confirmed path without this fix; we report after
    res = resolve_domain_authority(skill, problem_type_id=op)
    match = res.selected_operation == op
    adapter = _has_executable_adapter_route(
        selected_operation=op,
        domain_module="core.domain.polynomial_domain",
        impl_fn_name="build_polynomial_matrix",
    )
    all_match = all_match and match
    print(f"{op}\t{op}\t{res.selected_operation!r}\t{match}\t{adapter}")

print("all_selected_match", all_match)
print("overall_note", "PARTIAL — answer_contract/validator/choice not fixed this round")
