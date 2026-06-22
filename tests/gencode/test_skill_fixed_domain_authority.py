# -*- coding: utf-8 -*-
"""Tests for Skill-Fixed Domain Authority gates."""

from __future__ import annotations

import json
import sqlite3
from unittest import mock

import pytest

from core.gencode.skill_fixed_domain_authority import (
    DOMAIN_OPERATION_NOT_ALLOWED,
    FIXED_DOMAIN_VIOLATION,
    SkillFixedDomainError,
    assert_operation_allowed,
    assert_template_dispatch,
    build_classifier_taxonomy_entry,
    log_dispatch_event,
    normalize_ai_classification,
    resolve_fixed_domain_context,
    strip_ai_routing_fields,
    validate_publish_component_record,
)
from core.registry.taxonomy_registry import (
    SkillDomainNotRegisteredError,
    get_allowed_operations,
    get_fixed_domain_key,
)


def test_get_fixed_domain_key_parallel_lines_skill():
    key = get_fixed_domain_key("vh_數學B1_DistanceBetweenTwoParallelLines")
    assert key == "coordinate_geometry.parallel_lines_distance"


def test_unregistered_skill_raises():
    with pytest.raises(SkillDomainNotRegisteredError):
        get_fixed_domain_key("vh_數學B1_NotRegisteredSkill")


def test_ai_cannot_override_fixed_domain():
    ctx = resolve_fixed_domain_context("vh_數學B1_DistanceBetweenTwoParallelLines")
    classification = normalize_ai_classification(
        {
            "domain_key": "coordinate_geometry.line_equation",
            "recommended_skill": "vh_數學B1_PointSlopeForm",
            "selected_operation": "distance_between_parallel_lines",
            "problem_type_id": "distance_between_parallel_lines",
        },
        ctx,
    )
    assert classification["fixed_domain_key"] == ctx.fixed_domain_key
    assert "domain_key" not in classification
    assert classification["selected_operation"] == "distance_between_parallel_lines"


def test_illegal_cross_domain_operation_blocked():
    ctx = resolve_fixed_domain_context("vh_數學B1_DistanceBetweenTwoParallelLines")
    with pytest.raises(SkillFixedDomainError) as exc:
        assert_operation_allowed(
            skill_id=ctx.skill_id,
            fixed_domain_key=ctx.fixed_domain_key,
            selected_operation="perpendicular_bisector_application",
            allowed_operations=ctx.allowed_operations,
        )
    assert exc.value.code == DOMAIN_OPERATION_NOT_ALLOWED


def test_missing_operation_does_not_fallback():
    ctx = resolve_fixed_domain_context("vh_數學B1_DistanceBetweenTwoParallelLines")
    with pytest.raises(SkillFixedDomainError):
        normalize_ai_classification(
            {"selected_operation": "point_slope", "problem_type_id": "point_slope"},
            ctx,
        )


def test_template_domain_mismatch_blocked():
    with pytest.raises(SkillFixedDomainError) as exc:
        assert_template_dispatch(
            skill_id="vh_數學B1_DistanceBetweenTwoParallelLines",
            fixed_domain_key="coordinate_geometry.parallel_lines_distance",
            template_domain_key="coordinate_geometry.line_equation",
            template_operation_key="distance_between_parallel_lines",
        )
    assert exc.value.code == FIXED_DOMAIN_VIOLATION


def test_domain_mismatch_component_not_publishable():
    blockers = validate_publish_component_record(
        skill_id="vh_數學B1_DistanceBetweenTwoParallelLines",
        component_skill_id="vh_數學B1_DistanceBetweenTwoParallelLines",
        component_fixed_domain_key="coordinate_geometry.line_equation",
        component_operation="distance_between_parallel_lines",
        component_status="verified",
    )
    assert FIXED_DOMAIN_VIOLATION in blockers


def test_legal_operation_allowed_for_draft():
    ctx = resolve_fixed_domain_context("vh_數學B1_DistanceBetweenTwoParallelLines")
    op = assert_operation_allowed(
        skill_id=ctx.skill_id,
        fixed_domain_key=ctx.fixed_domain_key,
        selected_operation="solve_parameter_from_parallel_distance",
        allowed_operations=ctx.allowed_operations,
    )
    assert op == "solve_parameter_from_parallel_distance"


def test_classifier_taxonomy_entry_includes_allowed_operations():
    ctx = resolve_fixed_domain_context("vh_數學B1_DistanceBetweenTwoParallelLines")
    entry = build_classifier_taxonomy_entry(ctx)
    assert entry["fixed_domain_key"] == ctx.fixed_domain_key
    assert "distance_between_parallel_lines" in entry["allowed_operations"]


def test_strip_ai_routing_fields():
    cleaned = strip_ai_routing_fields(
        {"domain_key": "x", "recommended_skill": "y", "selected_operation": "distance_between_parallel_lines"}
    )
    assert "domain_key" not in cleaned
    assert cleaned["selected_operation"] == "distance_between_parallel_lines"


def test_global_preflight_log_does_not_require_tracker(caplog):
    import logging

    with caplog.at_level(logging.INFO):
        log_dispatch_event(
            phase="global_preflight",
            skill_id="vh_數學B1_DistanceBetweenTwoParallelLines",
            fixed_domain_key="coordinate_geometry.parallel_lines_distance",
            selected_operation="distance_between_parallel_lines",
        )
    assert "global_preflight" in caplog.text


def test_parallel_lines_allowed_operations_whitelist():
    ops = get_allowed_operations("coordinate_geometry.parallel_lines_distance")
    assert "perpendicular_bisector_application" not in ops
    assert "distance_between_parallel_lines" in ops
