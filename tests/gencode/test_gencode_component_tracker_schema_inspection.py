# -*- coding: utf-8 -*-
"""Schema inspection tests for gencode_component_tracker contracts."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from core.gencode.schema.gencode_component_tracker_inspection import (
    ALLOWED_GENCODE_STATUSES,
    MIGRATION_PATH,
    REQUIRED_COLUMNS,
    apply_tracker_ddl,
    assert_tracker_schema_contract,
    inspect_gencode_component_tracker_schema,
    load_tracker_ddl,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def memory_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    apply_tracker_ddl(conn)
    yield conn
    conn.close()


def test_migration_file_exists_without_running_alembic_upgrade():
    assert MIGRATION_PATH.is_file()
    assert not (PROJECT_ROOT / "alembic.ini").is_file()


def test_ddl_and_migration_share_required_contract_elements():
    ddl = load_tracker_ddl()
    migration_source = MIGRATION_PATH.read_text(encoding="utf-8")

    for column in REQUIRED_COLUMNS:
        assert column in ddl
        assert column in migration_source

    assert "component_path" not in ddl
    assert "component_path" not in migration_source
    assert "CREATE TRIGGER" not in ddl.upper()
    assert "CREATE TRIGGER" not in migration_source.upper()
    assert "uq_gencode_tracker_example_id" in ddl
    assert "uq_gencode_tracker_namespace_pool" in ddl
    assert "ck_gencode_status_values" in ddl

    for status in ALLOWED_GENCODE_STATUSES:
        assert status in ddl
        assert status in migration_source


def test_tracker_schema_inspection_on_memory_sqlite(memory_conn: sqlite3.Connection):
    report = inspect_gencode_component_tracker_schema(memory_conn)

    assert set(REQUIRED_COLUMNS).issubset(set(report["columns"]))
    assert report["forbidden_columns_present"] == []
    assert report["trigger_count"] == 0
    assert report["unique_constraints"]["textbook_example_id_unique"] is True
    assert report["unique_constraints"]["skill_component_unique"] is True
    assert report["gencode_status_check"]["enforced"] is True

    assert_tracker_schema_contract(memory_conn)
