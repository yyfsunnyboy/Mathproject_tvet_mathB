# -*- coding: utf-8 -*-
"""Admin read-only Gencode status view context tests."""

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
    build_admin_examples_gencode_status_map,
    build_admin_skill_gencode_status_view,
    format_gencode_status_label,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
SKILL_ID = "vh_數學B1_PointSlopeForm"


@pytest.fixture
def sandbox_root() -> Iterator[Path]:
    base = SANDBOX_ROOT / f"pytest_admin_status_view_{uuid.uuid4().hex}"
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


def _insert_row(
    conn: sqlite3.Connection,
    *,
    example_id: int,
    status: str,
    payload: dict | None = None,
    error_log: str | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO gencode_component_tracker (
            textbook_example_id, skill_id, component_id, gencode_status,
            induced_spec_payload, gencode_error_log, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            example_id,
            SKILL_ID,
            f"src_{example_id}",
            status,
            json.dumps(payload, ensure_ascii=False) if payload is not None else None,
            error_log,
            "2026-06-16 12:00:00",
        ),
    )
    conn.commit()


def test_status_label_mapping():
    assert format_gencode_status_label("not_created") == "未建立"
    assert format_gencode_status_label("draft_written") == "草稿已寫入"
    assert format_gencode_status_label("verified") == "已驗證"
    assert format_gencode_status_label("failed") == "失敗"


def test_examples_context_covers_not_created_draft_verified_failed(
    memory_conn: sqlite3.Connection,
    sandbox_root: Path,
):
    _insert_row(memory_conn, example_id=2, status="draft_written", payload={"line_type": "point_slope"})
    _insert_row(memory_conn, example_id=3, status="verified", payload={"line_type": "point_slope"})
    _insert_row(memory_conn, example_id=4, status="failed", payload=None, error_log="compile failed")

    dryrun_root = sandbox_root / "dryrun"
    for example_id in (2, 3):
        component_dir = dryrun_root / SKILL_ID / "components" / f"src_{example_id}"
        component_dir.mkdir(parents=True)
        (component_dir / "generate.py").write_text("# stub\n", encoding="utf-8")

    before_paths = {p for p in sandbox_root.rglob("*")}
    status_map = build_admin_examples_gencode_status_map(
        memory_conn,
        [(1, SKILL_ID), (2, SKILL_ID), (3, SKILL_ID), (4, SKILL_ID)],
        project_root=sandbox_root,
        dryrun_base_dir=str(dryrun_root),
        production_base_dir=str(sandbox_root / "agent_skills_v3"),
    )
    after_paths = {p for p in sandbox_root.rglob("*")}

    assert before_paths == after_paths
    assert status_map[1]["status_label"] == "未建立"
    assert status_map[2]["status_label"] == "草稿已寫入"
    assert status_map[2]["dryrun_generate_label"] == "是"
    assert status_map[3]["status_label"] == "已驗證"
    assert status_map[4]["status_label"] == "失敗"
    assert status_map[4]["error_log"] == "compile failed"


def test_skill_context_view_is_read_only_and_reports_tracker_summary(
    memory_conn: sqlite3.Connection,
    sandbox_root: Path,
):
    _insert_row(memory_conn, example_id=1, status="verified", payload={"line_type": "point_slope"})

    before_paths = {p for p in sandbox_root.rglob("*")}
    view = build_admin_skill_gencode_status_view(
        memory_conn,
        skill_id=SKILL_ID,
        project_root=sandbox_root,
        dryrun_base_dir=str(sandbox_root / "dryrun"),
        production_base_dir=str(sandbox_root / "agent_skills_v3"),
    )
    after_paths = {p for p in sandbox_root.rglob("*")}

    assert before_paths == after_paths
    assert view["status_label"] == "已驗證"
    assert view["component_id"] == "src_1"
    assert view["has_payload_label"] == "有"
    assert view["production_generate_label"] == "否"


def test_admin_loader_helpers_do_not_mutate_tracker(
    memory_conn: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
):
    from core.routes import admin as admin_routes

    _insert_row(memory_conn, example_id=1, status="draft_written", payload={"line_type": "point_slope"})
    tracker_before = memory_conn.execute(
        "SELECT gencode_status, induced_spec_payload FROM gencode_component_tracker WHERE textbook_example_id = 1"
    ).fetchone()

    class _Example:
        id = 1
        skill_id = SKILL_ID

    class _NonClosingConnection:
        def __init__(self, conn: sqlite3.Connection):
            self._conn = conn

        def __getattr__(self, name: str):
            return getattr(self._conn, name)

        def close(self) -> None:
            return None

    class _Engine:
        def raw_connection(self):
            return _NonClosingConnection(memory_conn)

    class _DB:
        engine = _Engine()

    monkeypatch.setattr(admin_routes, "db", _DB())
    monkeypatch.setattr(admin_routes, "_resolve_admin_project_root", lambda: Path("."))

    status_map = admin_routes._load_examples_gencode_status_map([_Example()])
    tracker_after = memory_conn.execute(
        "SELECT gencode_status, induced_spec_payload FROM gencode_component_tracker WHERE textbook_example_id = 1"
    ).fetchone()

    assert status_map[1]["status_label"] == "草稿已寫入"
    assert tracker_before["gencode_status"] == tracker_after["gencode_status"]
    assert tracker_before["induced_spec_payload"] == tracker_after["induced_spec_payload"]
