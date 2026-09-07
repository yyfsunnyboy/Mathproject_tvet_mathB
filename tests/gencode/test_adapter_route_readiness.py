# -*- coding: utf-8 -*-
"""Adapter_route Exact Readiness: executable formal path, not operation-name string match."""

from __future__ import annotations

import inspect
from unittest.mock import MagicMock, patch

import pytest

import core.gencode.domain_matrix_adapter as adapter_module
from core.domain.polynomial_domain import build_polynomial_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload
from core.gencode.services.failed_component_recovery_service import (
    _has_executable_adapter_route,
)
from core.registry.domain_operation_registry import get_operation_spec


POLY_OPS = [
    "polynomial_long_division",
    "polynomial_add_sub",
    "polynomial_multiply",
]

B1_3_1_OPS = [
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


def _legacy_string_match(op: str) -> bool:
    src = inspect.getsource(adapter_module.convert_domain_matrix_to_question_payload)
    return f'"{op}"' in src or f"'{op}'" in src


@pytest.mark.parametrize("op", POLY_OPS)
def test_polynomial_generic_adapter_conversion_pass(op: str) -> None:
    matrix = build_polynomial_matrix(seed=7, domain_operation=op)
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        answer_type="expression",
        problem_type_id=op,
        domain_operation=op,
    )
    assert isinstance(payload, dict)
    assert payload.get("answer") is not None or str(
        payload.get("question_text") or ""
    ).strip()
    assert _legacy_string_match(op) is False


@pytest.mark.parametrize("op", POLY_OPS)
def test_polynomial_adapter_route_readiness_pass(op: str) -> None:
    spec = get_operation_spec("algebra.polynomial", op)
    assert spec is not None
    assert _has_executable_adapter_route(
        selected_operation=op,
        domain_module="core.domain.polynomial_domain",
        impl_fn_name=spec.handler,
        presentation_mode="short_answer",
        answer_type="expression",
    )


def test_fake_no_adapter_callable_fails_adapter_gate() -> None:
    """Negative control: domain/op resolvable inputs but adapter callable missing → NO."""
    with patch.object(adapter_module, "convert_domain_matrix_to_question_payload", None):
        ok = _has_executable_adapter_route(
            selected_operation="polynomial_long_division",
            domain_module="core.domain.polynomial_domain",
            impl_fn_name="build_polynomial_matrix",
        )
    assert ok is False


def test_fake_adapter_raises_fails_adapter_gate() -> None:
    """Negative control: adapter exists but cannot convert → NO."""

    def boom(*_a, **_k):
        raise RuntimeError("no formal adapter path")

    with patch.object(adapter_module, "convert_domain_matrix_to_question_payload", boom):
        ok = _has_executable_adapter_route(
            selected_operation="polynomial_add_sub",
            domain_module="core.domain.polynomial_domain",
            impl_fn_name="build_polynomial_matrix",
        )
    assert ok is False


def test_fixed_domain_only_does_not_auto_pass() -> None:
    """Having domain module alone must not pass without operation + handler probe."""
    assert (
        _has_executable_adapter_route(
            selected_operation="",
            domain_module="core.domain.polynomial_domain",
            impl_fn_name="build_polynomial_matrix",
        )
        is False
    )
    assert (
        _has_executable_adapter_route(
            selected_operation="polynomial_long_division",
            domain_module="core.domain.polynomial_domain",
            impl_fn_name="",
        )
        is False
    )
    assert (
        _has_executable_adapter_route(
            selected_operation="totally_fake_op_without_builder",
            domain_module="core.domain.polynomial_domain",
            impl_fn_name="build_polynomial_matrix",
        )
        is False
    )


def test_b1_3_1_all_ops_adapter_route_after_fix() -> None:
    for op in B1_3_1_OPS:
        before = _legacy_string_match(op)
        after = _has_executable_adapter_route(
            selected_operation=op,
            domain_module="core.domain.polynomial_domain",
            impl_fn_name="build_polynomial_matrix",
            presentation_mode="short_answer",
            answer_type="expression",
        )
        assert before is False, op
        assert after is True, op


def test_named_specialized_route_still_passes_via_probe() -> None:
    """Unrelated domain with working production adapter path must not regress."""
    from core.registry.domain_operation_registry import get_domain_spec

    domain_key = "coordinate_geometry.line_equation"
    op = "two_points"
    dspec = get_domain_spec(domain_key)
    ospec = get_operation_spec(domain_key, op)
    assert ospec is not None
    ok = _has_executable_adapter_route(
        selected_operation=op,
        domain_module=dspec.domain_module,
        impl_fn_name=ospec.handler,
        presentation_mode="short_answer",
        answer_type=(ospec.supported_answer_types[0] if ospec.supported_answer_types else "expression"),
    )
    assert ok is True
