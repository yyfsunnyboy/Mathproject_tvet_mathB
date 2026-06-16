# -*- coding: utf-8 -*-
"""Unit tests for read-only Gencode status query service."""

from __future__ import annotations

import json
import shutil
import sqlite3
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest

from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.services.gencode_status_query_service import (
    build_admin_example_gencode_status_view,
    get_gencode_status_for_examples,
    inspect_gencode_files,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
SKILL_ID = "vh_數學B1_PointSlopeForm"
COMPONENT_ID = "src_1"


@pytest.fixture
def sandbox_root() -> Iterator[Path]:
    base = SANDBOX_ROOT / f"pytest_status_query_{uuid.uuid4().hex}"
    base.mkdir(parents=True, exist_ok=True)
    try:
        yield base
    finally:
        shutil.rmtree(base, ignore_errors=True)


@pytest.fixture
def memory_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT NOT NULL
        )
        """
    )
    apply_tracker_ddl(conn)
    yield conn
    conn.close()


def _insert_tracker_row(
    conn: sqlite3.Connection,
    *,
    textbook_example_id: int,
    status: str,
    payload: dict | None,
    error_log: str | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO gencode_component_tracker (
            textbook_example_id,
            skill_id,
            component_id,
            gencode_status,
            induced_spec_payload,
            gencode_error_log,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            textbook_example_id,
            SKILL_ID,
            f"src_{textbook_example_id}",
            status,
            json.dumps(payload, ensure_ascii=False) if payload is not None else None,
            error_log,
            "2026-06-16 10:00:00",
        ),
    )
    conn.commit()


def test_missing_tracker_row_returns_not_created_fallback(memory_conn: sqlite3.Connection):
    result = get_gencode_status_for_examples(memory_conn, [1, 2])

    assert result[1]["status"] == "not_created"
    assert result[1]["component_id"] is None
    assert result[1]["has_payload"] is False
    assert result[2]["status"] == "not_created"


def test_tracker_statuses_are_decoded(memory_conn: sqlite3.Connection):
    _insert_tracker_row(
        memory_conn,
        textbook_example_id=1,
        status="draft_written",
        payload={"line_type": "point_slope"},
    )
    _insert_tracker_row(
        memory_conn,
        textbook_example_id=2,
        status="verified",
        payload={"line_type": "point_slope"},
    )
    _insert_tracker_row(
        memory_conn,
        textbook_example_id=3,
        status="failed",
        payload=None,
        error_log="smoke failed",
    )

    result = get_gencode_status_for_examples(memory_conn, [1, 2, 3, 99])

    assert result[1]["status"] == "draft_written"
    assert result[2]["status"] == "verified"
    assert result[3]["status"] == "failed"
    assert result[3]["error_log"] == "smoke failed"
    assert result[99]["status"] == "not_created"


def test_has_payload_matches_induced_spec_payload(memory_conn: sqlite3.Connection):
    _insert_tracker_row(
        memory_conn,
        textbook_example_id=10,
        status="draft_written",
        payload={"presentation_mode": "short_answer"},
    )
    _insert_tracker_row(
        memory_conn,
        textbook_example_id=11,
        status="failed",
        payload=None,
    )

    result = get_gencode_status_for_examples(memory_conn, [10, 11])

    assert result[10]["has_payload"] is True
    assert result[11]["has_payload"] is False


def test_inspect_gencode_files_is_read_only_and_reports_existing_paths(sandbox_root: Path):
    dryrun_root = sandbox_root / "dryrun"
    production_root = sandbox_root / "agent_skills_v3"
    component_dir = dryrun_root / SKILL_ID / "components" / COMPONENT_ID
    component_dir.mkdir(parents=True)
    (component_dir / "generate.py").write_text("# stub\n", encoding="utf-8")
    (dryrun_root / SKILL_ID / "component_manifest.json").write_text("{}", encoding="utf-8")

    before_dirs = {p for p in sandbox_root.rglob("*")}
    result = inspect_gencode_files(
        skill_id=SKILL_ID,
        component_id=COMPONENT_ID,
        dryrun_base_dir=str(dryrun_root),
        production_base_dir=str(production_root),
        project_root=str(sandbox_root),
    )
    after_dirs = {p for p in sandbox_root.rglob("*")}

    assert before_dirs == after_dirs
    assert result["dryrun_component_exists"] is True
    assert result["dryrun_generate_exists"] is True
    assert result["dryrun_manifest_exists"] is True
    assert result["production_component_exists"] is False
    assert result["production_generate_exists"] is False
    assert result["production_manifest_exists"] is False


def test_build_admin_example_view_combines_tracker_and_files(
    memory_conn: sqlite3.Connection,
    sandbox_root: Path,
):
    _insert_tracker_row(
        memory_conn,
        textbook_example_id=1,
        status="verified",
        payload={"line_type": "point_slope"},
    )
    dryrun_root = sandbox_root / "dryrun"
    component_dir = dryrun_root / SKILL_ID / "components" / COMPONENT_ID
    component_dir.mkdir(parents=True)
    (component_dir / "generate.py").write_text("# stub\n", encoding="utf-8")

    view = build_admin_example_gencode_status_view(
        memory_conn,
        textbook_example_id=1,
        skill_id=SKILL_ID,
        project_root=sandbox_root,
        dryrun_base_dir=str(dryrun_root),
        production_base_dir=str(sandbox_root / "agent_skills_v3"),
    )

    assert view["status"] == "verified"
    assert view["status_label"] == "已驗證"
    assert view["component_id"] == COMPONENT_ID
    assert view["has_payload_label"] == "有"
    assert view["dryrun_generate_label"] == "是"
    assert view["production_generate_label"] == "否"
