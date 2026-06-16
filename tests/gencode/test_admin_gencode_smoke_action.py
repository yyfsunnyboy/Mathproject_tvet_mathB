# -*- coding: utf-8 -*-
"""Tests for admin single-example V3 smoke action."""

from __future__ import annotations

import hashlib
import shutil
import sqlite3
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest

from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.services.admin_gencode_action_service import run_admin_v3_smoke_for_example
from core.gencode.services.component_tracker_service import update_status

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
SKILL_ID = "vh_數學B1_PointSlopeForm"
COMPONENT_ID = "src_1"

STUB_METADATA = 'COMPONENT_ID = "src_1"\n'
STUB_GENERATE = """
from typing import Any

def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    return {"answer": "ok", "metadata": {"component_id": "src_1"}}
"""
STUB_HINT = """
def get_hint(step: int, question_payload: dict | None = None) -> str:
    return "hint"
"""


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
    conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (1, SKILL_ID),
    )
    conn.execute(
        """
        INSERT INTO gencode_component_tracker (
            textbook_example_id, skill_id, component_id, gencode_status, induced_spec_payload
        ) VALUES (?, ?, ?, 'draft_written', ?)
        """,
        (1, SKILL_ID, COMPONENT_ID, '{"source_kind":"ex_1"}'),
    )
    conn.commit()
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def sandbox_root() -> Iterator[Path]:
    base = SANDBOX_ROOT / f"pytest_smoke_action_{uuid.uuid4().hex}"
    base.mkdir(parents=True, exist_ok=True)
    try:
        yield base
    finally:
        shutil.rmtree(base, ignore_errors=True)


def _seed_component_files(sandbox_root: Path) -> Path:
    component_dir = sandbox_root / SKILL_ID / "components" / COMPONENT_ID
    component_dir.mkdir(parents=True, exist_ok=True)
    (component_dir / "metadata.py").write_text(STUB_METADATA, encoding="utf-8")
    (component_dir / "generate.py").write_text(STUB_GENERATE, encoding="utf-8")
    (component_dir / "get_hint.py").write_text(STUB_HINT, encoding="utf-8")
    return component_dir


def test_smoke_action_success_updates_tracker_and_keeps_production_clean(
    memory_conn: sqlite3.Connection,
    sandbox_root: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    _seed_component_files(sandbox_root)
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

    result = run_admin_v3_smoke_for_example(
        conn=memory_conn,
        textbook_example_id=1,
        skill_id=SKILL_ID,
        dryrun_base_dir=str(sandbox_root),
    )

    assert result["status"] == "smoke_passed"
    row = memory_conn.execute(
        "SELECT gencode_status, gencode_error_log FROM gencode_component_tracker WHERE textbook_example_id = 1"
    ).fetchone()
    assert row["gencode_status"] == "smoke_passed"
    assert row["gencode_error_log"] is None
    assert _snapshot_paths(PROJECT_ROOT / "skills") == skills_snapshot
    assert _snapshot_paths(PROJECT_ROOT / "agent_skills_v3") == v3_snapshot


def test_smoke_action_missing_files_sets_failed_and_raises(
    memory_conn: sqlite3.Connection,
    sandbox_root: Path,
):
    component_dir = _seed_component_files(sandbox_root)
    (component_dir / "generate.py").unlink()

    with pytest.raises(ValueError, match="dryrun_component_missing_files"):
        run_admin_v3_smoke_for_example(
            conn=memory_conn,
            textbook_example_id=1,
            skill_id=SKILL_ID,
            dryrun_base_dir=str(sandbox_root),
        )

    row = memory_conn.execute(
        "SELECT gencode_status, gencode_error_log FROM gencode_component_tracker WHERE textbook_example_id = 1"
    ).fetchone()
    assert row["gencode_status"] == "failed"
    assert row["gencode_error_log"]


def test_smoke_action_rejects_invalid_status(
    memory_conn: sqlite3.Connection,
    sandbox_root: Path,
):
    _seed_component_files(sandbox_root)
    update_status(
        memory_conn,
        textbook_example_id=1,
        skill_id=SKILL_ID,
        gencode_status="verified",
        gencode_error_log=None,
    )

    with pytest.raises(ValueError, match="invalid_status_for_smoke"):
        run_admin_v3_smoke_for_example(
            conn=memory_conn,
            textbook_example_id=1,
            skill_id=SKILL_ID,
            dryrun_base_dir=str(sandbox_root),
        )


def test_smoke_action_rejects_skill_mismatch(
    memory_conn: sqlite3.Connection,
    sandbox_root: Path,
):
    _seed_component_files(sandbox_root)
    with pytest.raises(ValueError, match="skill_id_mismatch"):
        run_admin_v3_smoke_for_example(
            conn=memory_conn,
            textbook_example_id=1,
            skill_id="vh_fake_mismatch",
            dryrun_base_dir=str(sandbox_root),
        )


def test_template_has_post_smoke_button_contract():
    content = (PROJECT_ROOT / "templates" / "admin_examples.html").read_text(encoding="utf-8")
    assert "admin_run_example_v3_smoke" in content
    assert "🧪 執行 Smoke 測試" in content
    assert "⚠️ 僅測試 dryrun 沙盒組件，不會正式發布" in content
    assert "gencode_status in ['draft_written', 'failed']" in content
