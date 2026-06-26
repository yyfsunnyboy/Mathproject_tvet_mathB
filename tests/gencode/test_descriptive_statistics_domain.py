# -*- coding: utf-8 -*-
"""Descriptive statistics domain tests (abstract fixtures only)."""

from __future__ import annotations

import importlib
import re
from unittest import mock

import pytest

from core.domain.statistics.descriptive_statistics_core import (
    arithmetic_mean_from_raw,
    median_from_values,
    mode_from_values,
    population_variance,
)
from core.domain.statistics.descriptive_statistics_domain import (
    DOMAIN_KEY,
    ENTRYPOINT,
    build_descriptive_statistics_matrix,
)
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority
from core.gencode.validators.descriptive_statistics_validator import validate_descriptive_statistics_payload
from core.registry.domain_operation_registry import (
    check_registry_consistency,
    get_domain_operations,
    get_domain_spec,
    get_operation_spec,
)

DOMAIN_MODULE = "core.domain.statistics.descriptive_statistics_domain"
ABSTRACT_SKILL = "abstract_descriptive_statistics_skill"


OPERATIONS = [
    "compute_arithmetic_mean_from_raw_values",
    "compute_arithmetic_mean_from_frequency_table",
    "compute_weighted_mean",
    "compute_median_from_raw_values",
    "compute_mode_from_raw_values",
    "compute_mode_from_frequency_table",
    "compute_range",
    "compute_population_variance",
    "compute_population_standard_deviation",
    "complete_descriptive_statistics_table",
]


@pytest.mark.parametrize("operation", OPERATIONS)
def test_registry_consistency(operation: str) -> None:
    assert check_registry_consistency() == []
    spec = get_domain_spec(DOMAIN_KEY)
    assert spec is not None
    assert spec.entrypoint == ENTRYPOINT
    assert operation in get_domain_operations(DOMAIN_KEY)
    op_spec = get_operation_spec(DOMAIN_KEY, operation)
    assert op_spec is not None
    assert op_spec.handler == ENTRYPOINT
    assert op_spec.supported_answer_types
    module = importlib.import_module(DOMAIN_MODULE)
    assert callable(getattr(module, ENTRYPOINT))


@pytest.mark.parametrize("operation", OPERATIONS)
def test_operation_seed_reproducible_and_varies(operation: str) -> None:
    m1 = build_descriptive_statistics_matrix(seed=42, domain_operation=operation)
    m2 = build_descriptive_statistics_matrix(seed=42, domain_operation=operation)
    m3 = build_descriptive_statistics_matrix(seed=99, domain_operation=operation)
    assert m1["answer"]["canonical_form"] == m2["answer"]["canonical_form"]
    if operation not in {"compute_population_standard_deviation"}:
        assert m1["givens"] != m3["givens"] or m1["answer"]["canonical_form"] != m3["answer"]["canonical_form"]


def test_arithmetic_mean_math_correct() -> None:
    matrix = build_descriptive_statistics_matrix(
        seed=1,
        domain_operation="compute_arithmetic_mean_from_raw_values",
        constraints={"raw_values": [2, 4, 6, 8]},
    )
    assert matrix["validation_facts"]["mean"] == arithmetic_mean_from_raw([2, 4, 6, 8])


def test_median_even_count() -> None:
    matrix = build_descriptive_statistics_matrix(
        seed=2,
        domain_operation="compute_median_from_raw_values",
        constraints={"raw_values": [1, 2, 3, 4]},
    )
    assert matrix["validation_facts"]["median"] == median_from_values([1, 2, 3, 4])


def test_mode_multi_and_none() -> None:
    multi = build_descriptive_statistics_matrix(
        seed=3,
        domain_operation="compute_mode_from_raw_values",
        constraints={"force_multi_mode": True},
    )
    assert multi["answer_shape"] == "unordered_set"
    none = build_descriptive_statistics_matrix(
        seed=4,
        domain_operation="compute_mode_from_raw_values",
        constraints={"force_no_mode": True},
    )
    assert none["answer_shape"] == "text_short"
    assert mode_from_values([1, 2, 3, 4]) == []


def test_variance_zero_and_stddev_integer() -> None:
    matrix = build_descriptive_statistics_matrix(
        seed=5,
        domain_operation="compute_population_variance",
        constraints={"raw_values": [5, 5, 5, 5]},
    )
    assert population_variance([5, 5, 5, 5]) == 0
    assert float(matrix["validation_facts"]["variance"]) == 0
    std_matrix = build_descriptive_statistics_matrix(
        seed=6,
        domain_operation="compute_population_standard_deviation",
        constraints={"raw_values": [60, 72, 72, 72, 78, 78]},
    )
    assert std_matrix["validation_facts"]["standard_deviation"] == 6


def test_answer_shapes() -> None:
    single = convert_domain_matrix_to_question_payload(
        build_descriptive_statistics_matrix(seed=1, domain_operation="compute_arithmetic_mean_from_raw_values"),
        domain_operation="compute_arithmetic_mean_from_raw_values",
    )
    assert single["answer_shape"] == "single_numeric"
    multi = convert_domain_matrix_to_question_payload(
        build_descriptive_statistics_matrix(seed=2, domain_operation="complete_descriptive_statistics_table"),
        domain_operation="complete_descriptive_statistics_table",
    )
    assert multi["answer_shape"] == "table_fill"
    modes = convert_domain_matrix_to_question_payload(
        build_descriptive_statistics_matrix(
            seed=3,
            domain_operation="compute_mode_from_raw_values",
            constraints={"force_multi_mode": True},
        ),
        domain_operation="compute_mode_from_raw_values",
    )
    assert modes["answer_contract"]["checker_key"] == "unordered_set_checker"


def test_validator_passes_for_generated_payload() -> None:
    for operation in OPERATIONS[:5]:
        matrix = build_descriptive_statistics_matrix(seed=7, domain_operation=operation)
        payload = convert_domain_matrix_to_question_payload(matrix, domain_operation=operation)
        payload["domain_operation"] = operation
        errors = validate_descriptive_statistics_payload(payload)
        assert errors == [], f"{operation}: {errors}"


def test_resolver_matches_descriptive_domain() -> None:
    extra = {
        "problem_type_id": "compute_arithmetic_mean_from_raw_values",
        "required_capabilities": ["arithmetic_mean"],
        "classification_source": "test_induced_spec",
    }
    result = resolve_domain_authority(ABSTRACT_SKILL, extra=extra)
    assert result.resolution_source == "derived_capability_match"
    assert result.fixed_domain_key == DOMAIN_KEY


def test_resolver_weighted_mean_capability() -> None:
    extra = {"required_capabilities": ["weighted_mean"], "classification_source": "test_induced_spec"}
    with mock.patch(
        "core.gencode.skill_fixed_domain_authority.get_confirmed_skill_binding",
        return_value=None,
    ):
        result = resolve_domain_authority(ABSTRACT_SKILL, extra=extra)
    assert result.fixed_domain_key == DOMAIN_KEY


def test_publish_evidence_fields_in_payload() -> None:
    matrix = build_descriptive_statistics_matrix(seed=8, domain_operation="compute_range")
    payload = convert_domain_matrix_to_question_payload(matrix, domain_operation="compute_range")
    meta = payload["metadata"]
    assert meta["fixed_domain_key"] == DOMAIN_KEY
    assert meta["domain_operation"] == "compute_range"
    assert meta.get("required_capabilities")
    assert payload.get("domain_resolution", {}).get("fixed_domain_key") == DOMAIN_KEY


def test_no_skill_or_example_literals_in_domain_production_code() -> None:
    from pathlib import Path

    repo = Path(__file__).resolve().parents[2]
    targets = [
        repo / "core/domain/statistics/descriptive_statistics_domain.py",
        repo / "core/domain/statistics/descriptive_statistics_core.py",
        repo / "core/gencode/validators/descriptive_statistics_validator.py",
        repo / "core/gencode/descriptive_statistics_answer_contract.py",
        repo / "core/gencode/domain_matrix_adapter.py",
    ]
    forbidden = (
        re.compile(r"vh_[\w\u4e00-\u9fff]+"),
        re.compile(r"src_\d+"),
        re.compile(r"textbook_example_id\s*=\s*\d+"),
    )
    for path in targets:
        text = path.read_text(encoding="utf-8")
        for pattern in forbidden:
            assert not pattern.search(text), f"forbidden literal in {path.name}"
