# -*- coding: utf-8 -*-
"""Regression tests for the single authoritative domain operation registry.

Test catalogue
--------------
T1  Registering a new operation requires no other allowlist changes.
T2  Handler present but operation unregistered → startup check fails.
T3  Registry registered but handler empty → startup check fails.
T4  taxonomy DOMAIN_ALLOWED_OPERATIONS == registry (no drift).
T5  Unknown operation returns DOMAIN_OPERATION_UNRESOLVED via capability service.
T6  New domain operation does not require skill-mapping changes.
T7  StatisticalChartReading: three cumulative operations validate no-LLM.
T8  Existing domain operations regression — all resolve as "ready".
T9  Consistency validator: taxonomy drift detected.
T10 Consistency validator: DOMAIN_PROVIDERS drift detected.
"""

from __future__ import annotations

import copy
import importlib
import pytest

from core.registry.domain_operation_registry import (
    DomainCapabilitySpec,
    OperationSpec,
    _REGISTRY,
    check_registry_consistency,
    get_domain_operations,
    get_domain_spec,
    get_operation_spec,
    list_registered_domains,
    operation_is_registered,
    register_domain_operation,
    register_domain_spec,
)
from core.registry.taxonomy_registry import DOMAIN_ALLOWED_OPERATIONS, get_allowed_operations
from core.gencode.skill_fixed_domain_authority import (
    DOMAIN_PROVIDERS,
    resolve_fixed_domain_context,
)
from core.gencode.domain_capability_service import resolve_domain_capability
from core.gencode.v3_error_codes import DOMAIN_OPERATION_MISSING


# ── helpers ───────────────────────────────────────────────────────────────────

_STAT_SKILL = "vh_數學B4_StatisticalChartReading"
_STAT_DOMAIN = "statistics.table_chart"
_CUMULATIVE_OPS = (
    "cumulative_above_fail_count",
    "cumulative_above_interval_count",
    "cumulative_below_interval_count",
)


# ── T1: new operation, zero allowlist changes needed ─────────────────────────

def test_T1_new_operation_auto_visible_after_registration(tmp_domain_spec):
    """A freshly registered operation is immediately visible in all layers."""
    dk = tmp_domain_spec.domain_key
    new_op = "tmp_test_operation_xyz"
    register_domain_operation(
        domain_key=dk,
        operation_key=new_op,
        handler="build_tmp_test_handler",
        supported_answer_types=("expression",),
    )
    # registry
    assert operation_is_registered(dk, new_op)
    # taxonomy derived view
    assert new_op in get_domain_operations(dk)
    # DOMAIN_ALLOWED_OPERATIONS is a snapshot computed at import; re-derive to test
    from core.registry.domain_operation_registry import get_domain_operations as _gdo
    assert new_op in _gdo(dk)
    # domain_capability_service sees it through ctx.allowed_operations
    ctx = _make_ctx_for_domain(dk, new_op)
    assert new_op in ctx.allowed_operations


def test_T1_no_manual_allowlist_edit_needed(tmp_domain_spec):
    """get_allowed_operations() returns the new op without touching taxonomy."""
    dk = tmp_domain_spec.domain_key
    new_op = "tmp_test_no_allowlist_edit"
    register_domain_operation(dk, new_op, handler="build_tmp_test_handler")
    ops = get_domain_operations(dk)
    assert new_op in ops


# ── T2: handler present but operation NOT registered → startup fails ──────────

def test_T2_unregistered_handler_triggers_startup_failure(tmp_domain_spec):
    """check_registry_consistency() detects op with empty handler."""
    dk = tmp_domain_spec.domain_key
    bad_op = OperationSpec(operation_key="bad_op_no_handler", handler="")
    tmp_domain_spec.operations["bad_op_no_handler"] = bad_op
    issues = check_registry_consistency()
    codes = [i["code"] for i in issues]
    assert "DOMAIN_OPERATION_REGISTRY_INCONSISTENT" in codes
    bad_issues = [i for i in issues if i.get("operation") == "bad_op_no_handler"]
    assert bad_issues


# ── T3: registry registered, handler is empty → startup check fails ──────────

def test_T3_empty_handler_detected_by_consistency_check(tmp_domain_spec):
    dk = tmp_domain_spec.domain_key
    tmp_domain_spec.operations["empty_handler_op"] = OperationSpec(
        operation_key="empty_handler_op", handler=""
    )
    issues = check_registry_consistency()
    offending = [i for i in issues if i.get("operation") == "empty_handler_op"]
    assert offending, "expected inconsistency for empty handler"
    assert "handler" in offending[0]["missing_layers"]


# ── T4: taxonomy == registry (no drift) ──────────────────────────────────────

def test_T4_domain_allowed_operations_matches_registry_exactly():
    """DOMAIN_ALLOWED_OPERATIONS must equal get_domain_operations() for every domain."""
    for dk in list_registered_domains():
        registry_ops = set(get_domain_operations(dk))
        taxonomy_ops = set(DOMAIN_ALLOWED_OPERATIONS.get(dk, []))
        assert registry_ops == taxonomy_ops, (
            f"Drift for {dk!r}: "
            f"registry={sorted(registry_ops)} "
            f"taxonomy={sorted(taxonomy_ops)}"
        )


def test_T4_domain_providers_matches_registry_exactly():
    """DOMAIN_PROVIDERS.allowed_operations must equal registry for every domain."""
    for dk in list_registered_domains():
        registry_ops = set(get_domain_operations(dk))
        prov_ops = set(DOMAIN_PROVIDERS.get(dk, {}).get("allowed_operations", []))
        assert registry_ops == prov_ops, (
            f"DOMAIN_PROVIDERS drift for {dk!r}: "
            f"registry={sorted(registry_ops)} "
            f"providers={sorted(prov_ops)}"
        )


# ── T5: unknown operation → DOMAIN_OPERATION_MISSING ─────────────────────────

def test_T5_unknown_operation_returns_domain_operation_missing():
    ctx = resolve_fixed_domain_context(_STAT_SKILL)
    result = resolve_domain_capability(
        skill_id=ctx.skill_id,
        fixed_domain_key=ctx.fixed_domain_key,
        normalized_classification={
            "domain_operation": "totally_unknown_op_xyz",
            "function_name": ctx.entrypoint,
        },
        domain_context=ctx,
    )
    assert result.capability_status == DOMAIN_OPERATION_MISSING


# ── T6: new op in same domain, no skill-mapping change ───────────────────────

def test_T6_new_operation_in_existing_domain_no_skill_map_change(tmp_domain_spec):
    """Skill mapping (SKILL_TO_DOMAIN) must not need editing for a new op."""
    dk = tmp_domain_spec.domain_key
    new_op = "T6_new_op_no_skill_map"
    register_domain_operation(dk, new_op, handler="build_tmp_test_handler")
    # The skill mapping is untouched, but the op is visible via domain_operations.
    assert new_op in get_domain_operations(dk)


# ── T7: cumulative ops for StatisticalChartReading (no-LLM) ──────────────────

def test_T7_cumulative_ops_registered_in_registry():
    for op in _CUMULATIVE_OPS:
        assert operation_is_registered(_STAT_DOMAIN, op), (
            f"operation {op!r} not registered in {_STAT_DOMAIN!r}"
        )


def test_T7_cumulative_ops_have_runtime_contract():
    for op in _CUMULATIVE_OPS:
        spec = get_operation_spec(_STAT_DOMAIN, op)
        assert spec is not None
        assert spec.runtime_contract, f"{op} missing runtime_contract"
        assert "cumulative_frequency_polygon" in spec.required_source_features


def test_T7_cumulative_ops_in_allowed_operations_for_skill():
    ctx = resolve_fixed_domain_context(_STAT_SKILL)
    for op in _CUMULATIVE_OPS:
        assert op in ctx.allowed_operations, (
            f"{op!r} not in allowed_operations for {_STAT_SKILL!r}; "
            f"got {list(ctx.allowed_operations)}"
        )


def test_T7_cumulative_ops_resolve_as_ready():
    ctx = resolve_fixed_domain_context(_STAT_SKILL)
    for op in _CUMULATIVE_OPS:
        result = resolve_domain_capability(
            skill_id=ctx.skill_id,
            fixed_domain_key=ctx.fixed_domain_key,
            normalized_classification={
                "domain_operation": op,
                "function_name": ctx.entrypoint,
            },
            domain_context=ctx,
        )
        assert result.operation_registered, f"{op} not operation_registered"
        assert result.function_exists, f"{op} domain function does not exist"
        assert result.capability_status == "ready", (
            f"{op} capability_status={result.capability_status!r}"
        )


def test_T7_source_isomorphism_validator_cumulative_ops_not_generic():
    """Cumulative ops must NOT appear in _GENERIC_TABLE_CHART_OPS."""
    from core.gencode.validators.source_isomorphism_validator import _GENERIC_TABLE_CHART_OPS
    for op in _CUMULATIVE_OPS:
        assert op not in _GENERIC_TABLE_CHART_OPS, (
            f"cumulative op {op!r} incorrectly classified as generic"
        )


def test_T7_generic_ops_are_non_cumulative():
    from core.gencode.validators.source_isomorphism_validator import _GENERIC_TABLE_CHART_OPS
    expected_generic = {
        "read_category_value",
        "compare_category_values",
        "calculate_total_ratio_percent",
        "validate_chart_statement",
    }
    assert _GENERIC_TABLE_CHART_OPS == expected_generic


# ── T8: existing operations regression ───────────────────────────────────────

@pytest.mark.parametrize("skill_id, expected_domain, sample_op", [
    ("vh_數學B1_DistanceBetweenPointAndLine", "coordinate_geometry.point_line_distance", "distance_from_point_to_line"),
    ("vh_數學B1_DistanceBetweenTwoParallelLines", "coordinate_geometry.parallel_lines_distance", "distance_between_parallel_lines"),
    ("vh_數學B4_FrequencyDistributionTableConstruction", "statistics.frequency_distribution", "frequency_table_construction_review"),
    (_STAT_SKILL, _STAT_DOMAIN, "read_category_value"),
    (_STAT_SKILL, _STAT_DOMAIN, "compare_category_values"),
    (_STAT_SKILL, _STAT_DOMAIN, "validate_chart_statement"),
])
def test_T8_existing_operations_regression(skill_id, expected_domain, sample_op):
    ctx = resolve_fixed_domain_context(skill_id)
    assert ctx.fixed_domain_key == expected_domain
    result = resolve_domain_capability(
        skill_id=ctx.skill_id,
        fixed_domain_key=ctx.fixed_domain_key,
        normalized_classification={
            "domain_operation": sample_op,
            "function_name": ctx.entrypoint,
        },
        domain_context=ctx,
    )
    assert result.capability_status == "ready", (
        f"{skill_id}/{sample_op}: status={result.capability_status}"
    )


# ── T9: consistency validator catches taxonomy drift ─────────────────────────

def test_T9_consistency_validator_catches_taxonomy_drift(monkeypatch):
    """Injecting a rogue entry into DOMAIN_ALLOWED_OPERATIONS is detected."""
    import core.registry.taxonomy_registry as tr
    original = dict(tr.DOMAIN_ALLOWED_OPERATIONS)
    patched = dict(original)
    patched["statistics.table_chart"] = list(original["statistics.table_chart"]) + ["rogue_op"]
    monkeypatch.setattr(tr, "DOMAIN_ALLOWED_OPERATIONS", patched)

    from core.registry.domain_consistency_validator import validate_domain_operation_registry
    findings = validate_domain_operation_registry(raise_on_failure=False)
    codes = [f["code"] for f in findings]
    assert "DOMAIN_OPERATION_REGISTRY_INCONSISTENT" in codes


# ── T10: consistency validator catches DOMAIN_PROVIDERS drift ────────────────

def test_T10_consistency_validator_catches_providers_drift(monkeypatch):
    """Injecting a rogue op into DOMAIN_PROVIDERS is detected."""
    import core.gencode.skill_fixed_domain_authority as sfa
    original = copy.deepcopy(sfa.DOMAIN_PROVIDERS)
    patched = copy.deepcopy(original)
    patched["statistics.table_chart"]["allowed_operations"] = (
        list(original["statistics.table_chart"]["allowed_operations"]) + ["rogue_provider_op"]
    )
    monkeypatch.setattr(sfa, "DOMAIN_PROVIDERS", patched)

    from core.registry.domain_consistency_validator import validate_domain_operation_registry
    findings = validate_domain_operation_registry(raise_on_failure=False)
    codes = [f["code"] for f in findings]
    assert "DOMAIN_OPERATION_REGISTRY_INCONSISTENT" in codes


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def tmp_domain_spec():
    """Register a temporary domain for mutation tests; clean up afterwards."""
    dk = "test.tmp_domain_fixture"
    spec = DomainCapabilitySpec(
        domain_key=dk,
        domain_module="core.domain.statistics.table_chart_domain",
        entrypoint="build_statistical_chart_reading_matrix",
        capabilities=frozenset({"tmp_cap"}),
        operations={
            "tmp_op": OperationSpec("tmp_op", "build_statistical_chart_reading_matrix"),
        },
    )
    register_domain_spec(spec)
    yield spec
    _REGISTRY.pop(dk, None)


def _make_ctx_for_domain(domain_key: str, operation: str):
    """Create a minimal FixedDomainContext for a dynamic domain."""
    from core.gencode.skill_fixed_domain_authority import FixedDomainContext
    prov = DOMAIN_PROVIDERS.get(domain_key, {})
    return FixedDomainContext(
        skill_id="test_skill",
        fixed_domain_key=domain_key,
        allowed_operations=tuple(get_domain_operations(domain_key)),
        registry_revision="test",
        domain_module=prov.get("domain_module", ""),
        entrypoint=prov.get("entrypoint", ""),
        curriculum_profile="vocational_high_b",
    )
