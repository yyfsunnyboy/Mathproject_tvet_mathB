# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

adapter = Path("core/gencode/domain_matrix_adapter.py").read_text(encoding="utf-8")
ops = [
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
print("ADAPTER_NAMED_OPS")
for op in ops:
    hit = f"'{op}'" in adapter or f'"{op}"' in adapter
    print(op, "YES" if hit else "NO")

import core.domain.polynomial_domain as pd

print("has_build", hasattr(pd, "build_polynomial_matrix"))
print("supported_count", len(pd._SUPPORTED_OPS))

from core.gencode.checker_registry import CHECKER_REGISTRY

print("expression_checker", "expression_checker" in CHECKER_REGISTRY)
print("multi_part", "multi_part_answer_checker" in CHECKER_REGISTRY)
print("validators", [p.name for p in Path("core/gencode/validators").glob("*.py")])

# Simulate Exact Readiness adapter check used by recovery service
for op in ops:
    routed = f'"{op}"' in adapter or f"'{op}'" in adapter
    print("recovery_adapter_route", op, routed)

# manifests statuses
import json

for skill in [
    "vh_數學B1_PolynomialBasicConcepts",
    "vh_數學B1_PolynomialArithmeticOperations",
    "vh_數學B1_PolynomialEquality",
]:
    man = Path(f"agent_skills_v3/{skill}/component_manifest.json")
    if man.exists():
        data = json.loads(man.read_text(encoding="utf-8"))
        statuses = {}
        for c in data.get("components") or []:
            st = c.get("status")
            statuses[st] = statuses.get(st, 0) + 1
        print(skill, "manifest_status", statuses, "count", data.get("component_count"))
