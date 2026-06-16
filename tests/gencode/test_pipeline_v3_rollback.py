# -*- coding: utf-8 -*-
"""Backup and rollback integration tests for sandbox thin facade."""

from __future__ import annotations

import json
import shutil
import sqlite3
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest

from core.gencode.skill_wrapper_compiler import (
    assert_safe_sandbox_root,
    compile_and_double_write_skill,
    rollback_v3_to_v2_facade,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DDL_PATH = PROJECT_ROOT / "core" / "gencode" / "schema" / "gencode_component_tracker.sql"
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
SKILL_ID = "vh_數學B1_PointSlopeForm"
PAYLOAD = {
    "source_kind": "ex_1",
    "presentation_mode": "short_answer",
    "line_type": "point_slope",
}
V2_LEGACY_CODE = "V2_LEGACY_CODE"


@pytest.fixture
def sandbox_root() -> Iterator[Path]:
    base = SANDBOX_ROOT / f"pytest_rollback_{uuid.uuid4().hex}"
    base.mkdir(parents=True, exist_ok=True)
    try:
        yield base
    finally:
        shutil.rmtree(base, ignore_errors=True)


@pytest.fixture
def memory_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT NOT NULL
        )
        """
    )
    conn.executescript(DDL_PATH.read_text(encoding="utf-8"))
    yield conn
    conn.close()


def _insert_verified_component(conn: sqlite3.Connection, textbook_example_id: int = 1) -> None:
    conn.execute(
        """
        INSERT INTO textbook_examples (id, skill_id)
        VALUES (?, ?)
        """,
        (textbook_example_id, SKILL_ID),
    )
    conn.execute(
        """
        INSERT INTO gencode_component_tracker (
            textbook_example_id, skill_id, component_id, gencode_status, induced_spec_payload
        ) VALUES (?, ?, ?, 'verified', ?)
        """,
        (
            textbook_example_id,
            SKILL_ID,
            f"src_{textbook_example_id}",
            json.dumps(PAYLOAD, ensure_ascii=False),
        ),
    )
    conn.commit()


def _facade_paths(sandbox_root: Path) -> tuple[Path, Path]:
    facade_path = sandbox_root / "skills" / f"{SKILL_ID}.py"
    backup_path = sandbox_root / "skills" / f"{SKILL_ID}.py.bak"
    return facade_path, backup_path


def test_backup_no_overwrite_and_rollback_restore(memory_conn: sqlite3.Connection, sandbox_root: Path):
    _insert_verified_component(memory_conn, 1)
    facade_path, backup_path = _facade_paths(sandbox_root)
    facade_path.parent.mkdir(parents=True, exist_ok=True)
    facade_path.write_text(V2_LEGACY_CODE, encoding="utf-8")

    compile_and_double_write_skill(memory_conn, SKILL_ID, str(sandbox_root))
    assert backup_path.exists()
    assert backup_path.read_text(encoding="utf-8") == V2_LEGACY_CODE
    first_v3_facade = facade_path.read_text(encoding="utf-8")
    assert "runtime_skill_wrapper" in first_v3_facade or "dispatch_generate" in first_v3_facade

    compile_and_double_write_skill(memory_conn, SKILL_ID, str(sandbox_root))
    assert backup_path.read_text(encoding="utf-8") == V2_LEGACY_CODE

    result = rollback_v3_to_v2_facade(SKILL_ID, str(sandbox_root))
    assert result["status"] == "rolled_back"
    assert result["facade_restored"] is True
    assert facade_path.read_text(encoding="utf-8") == V2_LEGACY_CODE
    assert not backup_path.exists()
    assert not (sandbox_root / "agent_skills_v3" / SKILL_ID).exists()
    assert (sandbox_root / "agent_skills_v3").exists()


def test_rollback_without_backup_removes_v3_facade_only(sandbox_root: Path):
    facade_path, backup_path = _facade_paths(sandbox_root)
    facade_path.parent.mkdir(parents=True, exist_ok=True)
    facade_path.write_text("from core.gencode.runtime_skill_wrapper import dispatch_generate\n", encoding="utf-8")
    assert not backup_path.exists()

    result = rollback_v3_to_v2_facade(SKILL_ID, str(sandbox_root))
    assert result["status"] == "rolled_back"
    assert not facade_path.exists()


def test_rollback_without_backup_keeps_non_v3_file(sandbox_root: Path):
    facade_path, backup_path = _facade_paths(sandbox_root)
    facade_path.parent.mkdir(parents=True, exist_ok=True)
    facade_path.write_text("REAL_LEGACY_SKILL_CODE", encoding="utf-8")
    assert not backup_path.exists()

    result = rollback_v3_to_v2_facade(SKILL_ID, str(sandbox_root))
    assert result["status"] == "skipped_no_backup_non_v3_file"
    assert facade_path.read_text(encoding="utf-8") == "REAL_LEGACY_SKILL_CODE"


def test_rollback_rejects_unsafe_sandbox_root():
    for unsafe_root in ("", ".", "skills", "agent_skills_v3"):
        with pytest.raises(ValueError, match="unsafe_sandbox_root"):
            rollback_v3_to_v2_facade(SKILL_ID, unsafe_root)

    for unsafe_root in ("", ".", "skills", "agent_skills_v3"):
        with pytest.raises(ValueError, match="unsafe_sandbox_root"):
            assert_safe_sandbox_root(unsafe_root)
