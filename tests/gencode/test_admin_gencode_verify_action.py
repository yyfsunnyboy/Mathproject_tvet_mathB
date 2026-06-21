# -*- coding: utf-8 -*-
"""Tests for admin single-example verify action."""

from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

import pytest

from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.services.admin_gencode_action_service import mark_admin_v3_example_verified
from core.gencode.services.component_tracker_service import update_status

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILL_ID = "vh_數學B1_PointSlopeForm"
COMPONENT_ID = "src_1"


def _snapshot_paths(root: Path) -> dict[str, str]:
    if not root.exists():
        return {}
    snapshot: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            snapshot[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return snapshot


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
    conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (1, SKILL_ID),
    )
    conn.execute(
        """
        INSERT INTO gencode_component_tracker (
            textbook_example_id, skill_id, component_id, gencode_status, induced_spec_payload
        ) VALUES (?, ?, ?, 'smoke_passed', ?)
        """,
        (1, SKILL_ID, COMPONENT_ID, '{"source_kind":"ex_1"}'),
    )
    conn.commit()
    yield conn
    conn.close()


def test_verify_success_updates_tracker_and_keeps_production_clean(
    memory_conn: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
):
    skills_snapshot = _snapshot_paths(PROJECT_ROOT / "skills")
    v3_snapshot = _snapshot_paths(PROJECT_ROOT / "agent_skills_v3")

    monkeypatch.setattr(
        "core.gencode.v3_production_publish_service.publish_single_v3_skill_to_production",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("publish should never be called")),
    )
    monkeypatch.setattr(
        "core.gencode.skill_wrapper_compiler.compile_and_double_write_skill",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("compile_and_double_write_skill should never be called")),
    )

    result = mark_admin_v3_example_verified(
        conn=memory_conn,
        textbook_example_id=1,
        skill_id=SKILL_ID,
    )
    assert result["status"] == "verified"

    row = memory_conn.execute(
        "SELECT gencode_status, component_id FROM gencode_component_tracker WHERE textbook_example_id = 1"
    ).fetchone()
    assert row["gencode_status"] == "verified"
    assert row["component_id"] == COMPONENT_ID
    assert _snapshot_paths(PROJECT_ROOT / "skills") == skills_snapshot
    assert _snapshot_paths(PROJECT_ROOT / "agent_skills_v3") == v3_snapshot


@pytest.mark.parametrize("bad_status", ["draft_written", "failed", "verified", "generating"])
def test_verify_rejects_invalid_status(
    memory_conn: sqlite3.Connection,
    bad_status: str,
):
    update_status(
        memory_conn,
        textbook_example_id=1,
        skill_id=SKILL_ID,
        gencode_status=bad_status,
        gencode_error_log=None,
    )
    with pytest.raises(ValueError, match="invalid_status_for_verify"):
        mark_admin_v3_example_verified(
            conn=memory_conn,
            textbook_example_id=1,
            skill_id=SKILL_ID,
        )


def test_verify_rejects_missing_tracker_record(memory_conn: sqlite3.Connection):
    memory_conn.execute("DELETE FROM gencode_component_tracker")
    memory_conn.commit()
    with pytest.raises(ValueError, match="tracker_record_not_found"):
        mark_admin_v3_example_verified(
            conn=memory_conn,
            textbook_example_id=1,
            skill_id=SKILL_ID,
        )


def test_verify_rejects_skill_mismatch(memory_conn: sqlite3.Connection):
    with pytest.raises(ValueError, match="skill_id_mismatch"):
        mark_admin_v3_example_verified(
            conn=memory_conn,
            textbook_example_id=1,
            skill_id="vh_fake_mismatch",
        )


def test_template_has_verify_button_contract():
    content = (PROJECT_ROOT / "templates" / "admin_examples.html").read_text(encoding="utf-8")
    assert "v3Drawer" in content
