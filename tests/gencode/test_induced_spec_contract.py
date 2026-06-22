# -*- coding: utf-8 -*-
"""Tests for V3 induced spec contract enforcement."""

from __future__ import annotations

import pytest

from core.gencode.induced_spec_contract import (
    InducedSpecContractError,
    assert_induced_spec_contract,
    migrate_induced_spec_payload,
    validate_induced_spec_contract,
)
from core.gencode.failure_responsibility import (
    FAILURE_LAYER_SHARED,
    classify_batch_failures,
)


def _full_spec(**overrides: object) -> dict:
    base = {
        "component_id": "src_4568",
        "skill_id": "vh_數學B1_DistanceBetweenPointAndLine",
        "domain": "coordinate_geometry",
        "domain_operation": "distance_from_point_to_line",
        "problem_type_id": "distance_from_point_to_line",
        "answer_schema_key": "distance_scalar",
        "presentation_mode": "short_answer",
        "checker_key": "rational_checker",
    }
    base.update(overrides)
    return base


def test_missing_domain_operation_blocked():
    spec = _full_spec()
    del spec["domain_operation"]
    del spec["problem_type_id"]
    blockers = validate_induced_spec_contract(spec, allow_fallback_status=False)
    assert any("missing_induced_spec_field:domain_operation" in item for item in blockers)


def test_missing_answer_schema_key_blocked_without_mapping():
    spec = _full_spec(answer_schema_key="", domain_operation="", problem_type_id="")
    migrated = migrate_induced_spec_payload(spec)
    assert migrated.get("classification_status") == "needs_human_review"


def test_missing_checker_key_blocked():
    spec = _full_spec(checker_key="")
    blockers = validate_induced_spec_contract(spec, allow_fallback_status=False)
    assert any("missing_induced_spec_field:checker_key" in item for item in blockers)


def test_assert_induced_spec_contract_passes_complete_spec():
    assert assert_induced_spec_contract(_full_spec())["component_id"] == "src_4568"


def test_legacy_spec_migrates_answer_schema_from_problem_type():
    migrated = migrate_induced_spec_payload(
        {
            "component_id": "src_4607",
            "skill_id": "vh_數學B1_DistanceBetweenPointAndLine",
            "problem_type_id": "compare_point_to_line_distances",
            "presentation_mode": "short_answer",
            "checker_key": "text_short_checker",
        }
    )
    assert migrated["answer_schema_key"] == "comparison_label"
    assert migrated["domain_operation"] == "compare_point_to_line_distances"


def test_shared_failure_detection():
    failures = [
        {"message": "answer_schema_mismatch: expected=['distance'] actual=['slope']"},
        {"message": "answer_schema_mismatch: expected=['distance'] actual=['slope']"},
    ]
    batch = classify_batch_failures(failures)
    assert batch["shared_contract_failure"] is True
    assert batch["failure_layer"] == FAILURE_LAYER_SHARED
    assert batch["should_skip_component_repair"] is True


def test_component_id_fixed_to_src_prefix():
    migrated = migrate_induced_spec_payload({"textbook_example_id": 4545})
    assert migrated["component_id"] == "src_4545"
