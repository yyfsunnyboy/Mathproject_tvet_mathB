# -*- coding: utf-8 -*-
"""Tests for admin single-example V3 dryrun action."""

from __future__ import annotations

import hashlib
import shutil
import sqlite3
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest

from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.services.admin_gencode_action_service import run_admin_v3_dryrun_for_example

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
SKILL_ID = "vh_數學B1_PointSlopeForm"
NON_MVP_SKILL_ID = "legacy_skill_not_in_mvp"
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
def memory_conn() -> Iterator[sqlite3.Connection]:
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
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def dryrun_root() -> Iterator[Path]:
    base = SANDBOX_ROOT / f"pytest_admin_action_{uuid.uuid4().hex}"
    base.mkdir(parents=True, exist_ok=True)
    try:
        yield base
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_admin_single_example_dryrun_success(
    memory_conn: sqlite3.Connection,
    dryrun_root: Path,
):
    memory_conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (1, SKILL_ID),
    )
    memory_conn.commit()

    production_skills_snapshot = _snapshot_paths(PROJECT_ROOT / "skills")
    production_v3_snapshot = _snapshot_paths(PROJECT_ROOT / "agent_skills_v3")

    result = run_admin_v3_dryrun_for_example(
        conn=memory_conn,
        textbook_example_id=1,
        skill_id=SKILL_ID,
        dryrun_base_dir=str(dryrun_root),
        seed=42,
    )

    assert result["status"] == "draft_written"
    assert result["component_id"] == COMPONENT_ID
    tracker_row = memory_conn.execute(
        """
        SELECT gencode_status
        FROM gencode_component_tracker
        WHERE textbook_example_id = ?
        """,
        (1,),
    ).fetchone()
    assert tracker_row is not None
    assert tracker_row["gencode_status"] == "draft_written"

    component_dir = dryrun_root / SKILL_ID / "components" / COMPONENT_ID
    assert (component_dir / "metadata.py").exists()
    assert (component_dir / "generate.py").exists()
    assert (component_dir / "get_hint.py").exists()
    assert (dryrun_root / SKILL_ID / "component_manifest.json").exists()

    assert _snapshot_paths(PROJECT_ROOT / "skills") == production_skills_snapshot
    assert _snapshot_paths(PROJECT_ROOT / "agent_skills_v3") == production_v3_snapshot


def test_admin_action_rejects_skill_id_mismatch(
    memory_conn: sqlite3.Connection,
    dryrun_root: Path,
):
    memory_conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (1, SKILL_ID),
    )
    memory_conn.commit()

    with pytest.raises(ValueError, match="skill_id_mismatch"):
        run_admin_v3_dryrun_for_example(
            conn=memory_conn,
            textbook_example_id=1,
            skill_id="vh_fake_MVP",
            dryrun_base_dir=str(dryrun_root),
        )


def test_admin_action_rejects_non_mvp_skill_without_v2_fallback(
    memory_conn: sqlite3.Connection,
    dryrun_root: Path,
):
    memory_conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (1, NON_MVP_SKILL_ID),
    )
    memory_conn.commit()

    with pytest.raises(ValueError, match="skill_not_in_v3_mvp_scope"):
        run_admin_v3_dryrun_for_example(
            conn=memory_conn,
            textbook_example_id=1,
            skill_id=NON_MVP_SKILL_ID,
            dryrun_base_dir=str(dryrun_root),
        )

    tracker_count = memory_conn.execute(
        "SELECT COUNT(*) AS c FROM gencode_component_tracker"
    ).fetchone()["c"]
    assert tracker_count == 0
    assert list(dryrun_root.rglob("*")) == []


def test_admin_dryrun_never_calls_production_publish(
    memory_conn: sqlite3.Connection,
    dryrun_root: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    memory_conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (1, SKILL_ID),
    )
    memory_conn.commit()

    monkeypatch.setattr("core.gencode.pipeline_orchestrator.V3_PRODUCTION_PUBLISH_ENABLED", False)

    def _forbidden_publish(*_args: object, **_kwargs: object):
        raise AssertionError("production publish must not be called in admin dryrun action")

    monkeypatch.setattr(
        "core.gencode.v3_production_publish_service.publish_single_v3_skill_to_production",
        _forbidden_publish,
    )

    result = run_admin_v3_dryrun_for_example(
        conn=memory_conn,
        textbook_example_id=1,
        skill_id=SKILL_ID,
        dryrun_base_dir=str(dryrun_root),
    )
    assert result["status"] == "draft_written"


def test_admin_examples_template_has_post_only_dryrun_button_contract():
    template_path = PROJECT_ROOT / "templates" / "admin_examples.html"
    content = template_path.read_text(encoding="utf-8")

    assert "admin_run_example_v3_dryrun" in content
    assert "method=\"POST\"" in content
    assert "v3-badge" in content
    assert "v3Drawer" in content
    assert "v3-drawer-template" in content
    assert "openV3Drawer" in content
    assert "發布僅包含 verified components；未 verified 的教材題不會自動補齊" not in content
    assert "payload:" not in content
    assert "dryrun generate.py:" not in content
    assert "production generate.py:" not in content
    assert "gencode_status in ['not_created', 'failed', 'draft_written']" in content


def test_admin_examples_get_renders_flat_v3_table():
    from app import app

    app.config["TESTING"] = True
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = "1"
            sess["_fresh"] = True

        response = client.get("/examples")

    assert response.status_code == 200
    content = response.get_data(as_text=True)
    assert "v3-badge" in content
    assert "v3Drawer" in content
    assert "v3-drawer-template" in content
    assert "發布僅包含 verified components；未 verified 的教材題不會自動補齊" not in content
    assert "payload:" not in content
    assert "dryrun generate.py:" not in content
    assert "production generate.py:" not in content
