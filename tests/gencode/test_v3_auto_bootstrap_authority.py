from __future__ import annotations

import sqlite3

import pytest

from core.gencode.domain_capability_service import resolve_domain_capability
from core.gencode.services.admin_gencode_action_service import _classify_dryrun_error
from core.gencode.services.component_tracker_service import save_tracker_record
from core.gencode.services.v3_skill_coverage_service import get_v3_skill_component_coverage
from core.gencode.skill_fixed_domain_authority import (
    DOMAIN_BINDING_MISSING,
    resolve_fixed_domain_context,
)
from core.gencode.v3_error_codes import (
    DOMAIN_FUNCTION_MISSING,
    SHADOW_BRIDGE_NOT_EXECUTED,
)


def test_b4_frequency_skill_has_fixed_statistics_domain() -> None:
    ctx = resolve_fixed_domain_context("vh_數學B4_FrequencyDistributionTableConstruction")

    assert ctx.fixed_domain_key == "statistics.frequency_distribution"
    assert "frequency_table_construction_review" in ctx.allowed_operations


def test_ai_cannot_make_unregistered_skill_guess_domain() -> None:
    from core.gencode.v3_error_codes import DOMAIN_CAPABILITY_UNRESOLVED
    with pytest.raises(Exception) as exc:
        resolve_fixed_domain_context("vh_數學B4_NotRegisteredForV3")

    assert getattr(exc.value, "code", "") == DOMAIN_CAPABILITY_UNRESOLVED


def test_domain_capability_ready_for_frequency_table() -> None:
    ctx = resolve_fixed_domain_context("vh_數學B4_FrequencyDistributionTableConstruction")

    result = resolve_domain_capability(
        skill_id=ctx.skill_id,
        fixed_domain_key=ctx.fixed_domain_key,
        normalized_classification={
            "domain_operation": "frequency_table_construction_review",
            "function_name": ctx.entrypoint,
        },
        source_example={"id": 3822},
        domain_context=ctx,
    )

    assert result.capability_status == "ready"
    assert result.function_exists is True
    assert result.operation_registered is True


def test_b4_statistical_chart_reading_has_table_chart_domain_capability() -> None:
    ctx = resolve_fixed_domain_context("vh_數學B4_StatisticalChartReading")

    assert ctx.fixed_domain_key == "statistics.table_chart"
    assert "read_category_value" in ctx.allowed_operations
    assert "compare_category_values" in ctx.allowed_operations
    assert "calculate_total_ratio_percent" in ctx.allowed_operations
    assert "validate_chart_statement" in ctx.allowed_operations

    result = resolve_domain_capability(
        skill_id=ctx.skill_id,
        fixed_domain_key=ctx.fixed_domain_key,
        normalized_classification={
            "domain_operation": "read_category_value",
            "requested_capability": "statistical_chart_reading",
            "function_name": ctx.entrypoint,
        },
        source_example={"id": 0},
        domain_context=ctx,
    )

    assert result.capability_status == "ready"
    assert result.function_exists is True
    assert result.operation_registered is True


def test_unknown_statistical_skill_does_not_use_broad_statistical_fallback() -> None:
    from core.gencode.skill_fixed_domain_authority import SkillFixedDomainError
    from core.gencode.v3_error_codes import DOMAIN_CAPABILITY_UNRESOLVED

    with pytest.raises(SkillFixedDomainError) as exc:
        resolve_fixed_domain_context("vh_數學B4_StatisticalMeasureUnknown")

    assert exc.value.code == DOMAIN_CAPABILITY_UNRESOLVED


def test_shadow_bridge_not_executed_is_not_unsupported() -> None:
    assert _classify_dryrun_error(ValueError("v3_shadow_bridge_not_executed")) == SHADOW_BRIDGE_NOT_EXECUTED


def test_domain_gap_not_counted_as_unsupported() -> None:
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE textbook_examples (id INTEGER PRIMARY KEY, skill_id TEXT NOT NULL)")
    conn.execute(
        """
        CREATE TABLE gencode_component_tracker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            textbook_example_id INTEGER NOT NULL UNIQUE,
            skill_id TEXT NOT NULL,
            component_id TEXT NOT NULL,
            gencode_status TEXT NOT NULL,
            induced_spec_payload TEXT,
            gencode_error_log TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )
    conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (3822, "vh_數學B4_FrequencyDistributionTableConstruction"),
    )
    save_tracker_record(
        conn,
        textbook_example_id=3822,
        skill_id="vh_數學B4_FrequencyDistributionTableConstruction",
        gencode_status="failed",
        induced_spec_payload={"error_code": DOMAIN_FUNCTION_MISSING},
        gencode_error_log=f"{DOMAIN_FUNCTION_MISSING}: missing reusable function",
    )

    coverage = get_v3_skill_component_coverage(conn, "vh_數學B4_FrequencyDistributionTableConstruction")

    assert coverage["failed_count"] == 1
    assert coverage["domain_gap_count"] == 1
    assert coverage["unsupported_count"] == 0


def test_pipeline_defect_not_counted_as_unsupported() -> None:
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE textbook_examples (id INTEGER PRIMARY KEY, skill_id TEXT NOT NULL)")
    conn.execute(
        """
        CREATE TABLE gencode_component_tracker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            textbook_example_id INTEGER NOT NULL UNIQUE,
            skill_id TEXT NOT NULL,
            component_id TEXT NOT NULL,
            gencode_status TEXT NOT NULL,
            induced_spec_payload TEXT,
            gencode_error_log TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )
    conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (3822, "vh_數學B4_FrequencyDistributionTableConstruction"),
    )
    save_tracker_record(
        conn,
        textbook_example_id=3822,
        skill_id="vh_數學B4_FrequencyDistributionTableConstruction",
        gencode_status="failed",
        induced_spec_payload={"error_code": SHADOW_BRIDGE_NOT_EXECUTED},
        gencode_error_log=f"{SHADOW_BRIDGE_NOT_EXECUTED}: bridge was not called",
    )

    coverage = get_v3_skill_component_coverage(conn, "vh_數學B4_FrequencyDistributionTableConstruction")

    assert coverage["failed_count"] == 1
    assert coverage["pipeline_failed_count"] == 1
    assert coverage["unsupported_count"] == 0
