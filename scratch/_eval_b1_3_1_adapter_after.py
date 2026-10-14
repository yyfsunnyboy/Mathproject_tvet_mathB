# -*- coding: utf-8 -*-
"""Re-evaluate 3-1 adapter_route only after readiness fix."""
from __future__ import annotations

import inspect
import sys

sys.stdout.reconfigure(encoding="utf-8")

import core.gencode.domain_matrix_adapter as am
from core.gencode.services.failed_component_recovery_service import (
    _has_executable_adapter_route,
)

OPS = [
    "polynomial_descending_power_properties",
    "polynomial_param_degree_constraint",
    "polynomial_descending_power_table",
    "zero_polynomial_find_coeffs",
    "polynomial_degree_product_sum",
    "polynomial_add_sub",
    "polynomial_multiply",
    "polynomial_product_term_coefficient",
    "polynomial_long_division",
    "polynomial_synthetic_division",
    "polynomial_remainder_param_solve",
    "polynomial_shifted_basis_eval",
    "polynomial_equality_identity",
]

src = inspect.getsource(am.convert_domain_matrix_to_question_payload)
print("op\tbefore_string_match\tafter_executable_probe")
for op in OPS:
    before = f'"{op}"' in src or f"'{op}'" in src
    after = _has_executable_adapter_route(
        selected_operation=op,
        domain_module="core.domain.polynomial_domain",
        impl_fn_name="build_polynomial_matrix",
        presentation_mode="short_answer",
        answer_type="expression",
    )
    print(f"{op}\t{before}\t{after}")
