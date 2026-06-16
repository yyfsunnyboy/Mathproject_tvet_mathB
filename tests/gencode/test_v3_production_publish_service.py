# -*- coding: utf-8 -*-
"""Production publish lifecycle tests for gated V3 skill promotion."""

from __future__ import annotations

import json
import shutil
import sqlite3
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest

from core.gencode.skill_wrapper_compiler import rollback_v3_to_v2_facade
from core.gencode.v3_production_publish_service import (
    ALLOWED_PRODUCTION_SKILL_ID,
    publish_single_v3_skill_to_production,
    run_v3_smoke,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DDL_PATH = PROJECT_ROOT / "core" / "gencode" / "schema" / "gencode_component_tracker.sql"
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
SKILL_ID = ALLOWED_PRODUCTION_SKILL_ID
COMPONENT_ID = "src_1"
V2_LEGACY_CODE = "V2_LEGACY_CODE"
PAYLOAD = {
    "source_kind": "ex_1",
    "presentation_mode": "short_answer",
    "line_type": "point_slope",
}

STUB_METADATA_PY = '''from __future__ import annotations

COMPONENT_ID = "src_1"
'''

STUB_GENERATE_PY = '''from __future__ import annotations

from typing import Any


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    return {
        "question_text": "mock line equation question",
        "answer": "mock answer",
        "correct_answer": "mock answer",
        "component_id": "src_1",
        "metadata": {"component_id": "src_1"},
    }


def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None) -> bool:
    return str(user_answer) == str(correct_answer)
'''

STUB_GET_HINT_PY = '''from __future__ import annotations

from typing import Any


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    return f"hint step {step}"
'''


@pytest.fixture
def isolated_publish_roots() -> Iterator[tuple[Path, Path]]:
    """Simulate tmp_path/project and tmp_path/staging under dryrun sandbox."""
    base = SANDBOX_ROOT / f"pytest_production_publish_{uuid.uuid4().hex}"
    project_root = base / "project"
    staging_root = base / "staging"
    project_root.mkdir(parents=True, exist_ok=True)
    staging_root.mkdir(parents=True, exist_ok=True)
    try:
        yield project_root, staging_root
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


def _insert_verified_component(conn: sqlite3.Connection) -> None:
    conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (1, SKILL_ID),
    )
    conn.execute(
        """
        INSERT INTO gencode_component_tracker (
            textbook_example_id,
            skill_id,
            component_id,
            gencode_status,
            induced_spec_payload
        ) VALUES (?, ?, ?, 'verified', ?)
        """,
        (
            1,
            SKILL_ID,
            COMPONENT_ID,
            json.dumps(PAYLOAD, ensure_ascii=False),
        ),
    )
    conn.commit()


def _setup_mock_project_root(project_root: Path) -> Path:
    (project_root / "skills").mkdir(parents=True, exist_ok=True)
    (project_root / "agent_skills_v3").mkdir(parents=True, exist_ok=True)
    facade_path = project_root / "skills" / f"{SKILL_ID}.py"
    facade_path.write_text(V2_LEGACY_CODE, encoding="utf-8")
    return project_root


def _seed_staging_component_stubs(staging_root: Path) -> None:
    component_dir = staging_root / SKILL_ID / "components" / COMPONENT_ID
    component_dir.mkdir(parents=True, exist_ok=True)
    (component_dir / "metadata.py").write_text(STUB_METADATA_PY, encoding="utf-8")
    (component_dir / "generate.py").write_text(STUB_GENERATE_PY, encoding="utf-8")
    (component_dir / "get_hint.py").write_text(STUB_GET_HINT_PY, encoding="utf-8")


def _facade_paths(project_root: Path) -> tuple[Path, Path]:
    facade_path = project_root / "skills" / f"{SKILL_ID}.py"
    backup_path = project_root / "skills" / f"{SKILL_ID}.py.bak"
    return facade_path, backup_path


def test_publish_success_backup_promote_and_manual_rollback(
    memory_conn: sqlite3.Connection,
    isolated_publish_roots: tuple[Path, Path],
):
    _insert_verified_component(memory_conn)
    project_root, staging_root = isolated_publish_roots
    _setup_mock_project_root(project_root)
    _seed_staging_component_stubs(staging_root)

    result = publish_single_v3_skill_to_production(
        conn=memory_conn,
        skill_id=SKILL_ID,
        project_root=str(project_root),
        staging_root=str(staging_root),
    )

    assert result["status"] == "production_published"
    assert result["smoke_status"] == "passed"
    assert result["component_count"] == 1

    facade_path, backup_path = _facade_paths(project_root)
    assert backup_path.exists()
    assert backup_path.read_text(encoding="utf-8") == V2_LEGACY_CODE

    promoted_facade = facade_path.read_text(encoding="utf-8")
    assert "runtime_skill_wrapper" in promoted_facade or "dispatch_generate" in promoted_facade
    assert promoted_facade != V2_LEGACY_CODE

    v3_skill_dir = project_root / "agent_skills_v3" / SKILL_ID
    assert v3_skill_dir.exists()
    assert (v3_skill_dir / "__init__.py").exists()
    assert (v3_skill_dir / "components" / COMPONENT_ID / "generate.py").exists()

    rollback_result = rollback_v3_to_v2_facade(SKILL_ID, str(project_root))
    assert rollback_result["status"] == "rolled_back"
    assert facade_path.read_text(encoding="utf-8") == V2_LEGACY_CODE
    assert not backup_path.exists()
    assert not v3_skill_dir.exists()
    assert (project_root / "agent_skills_v3").exists()


def test_publish_rejects_non_benchmark_skill(
    memory_conn: sqlite3.Connection,
    isolated_publish_roots: tuple[Path, Path],
):
    _insert_verified_component(memory_conn)
    project_root, staging_root = isolated_publish_roots
    _setup_mock_project_root(project_root)

    with pytest.raises(ValueError, match="production_publish_not_allowed_for_skill"):
        publish_single_v3_skill_to_production(
            conn=memory_conn,
            skill_id="jh_數學1上_FourArithmeticOperationsOfIntegers",
            project_root=str(project_root),
            staging_root=str(staging_root),
        )


def test_publish_rejects_missing_verified_components(
    memory_conn: sqlite3.Connection,
    isolated_publish_roots: tuple[Path, Path],
):
    project_root, staging_root = isolated_publish_roots
    _setup_mock_project_root(project_root)

    with pytest.raises(ValueError, match="no_verified_components"):
        publish_single_v3_skill_to_production(
            conn=memory_conn,
            skill_id=SKILL_ID,
            project_root=str(project_root),
            staging_root=str(staging_root),
        )


def test_staging_smoke_failure_does_not_touch_production(
    memory_conn: sqlite3.Connection,
    isolated_publish_roots: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
):
    _insert_verified_component(memory_conn)
    project_root, staging_root = isolated_publish_roots
    _setup_mock_project_root(project_root)
    facade_path, backup_path = _facade_paths(project_root)

    def _fail_staging_smoke(root: Path, skill_id: str) -> None:
        raise RuntimeError("forced staging smoke failure")

    monkeypatch.setattr(
        "core.gencode.v3_production_publish_service.run_v3_smoke",
        _fail_staging_smoke,
    )

    with pytest.raises(ValueError, match="staging_smoke_failed"):
        publish_single_v3_skill_to_production(
            conn=memory_conn,
            skill_id=SKILL_ID,
            project_root=str(project_root),
            staging_root=str(staging_root),
        )

    assert facade_path.read_text(encoding="utf-8") == V2_LEGACY_CODE
    assert not backup_path.exists()
    assert not (project_root / "agent_skills_v3" / SKILL_ID).exists()


def test_production_smoke_failure_auto_rollback(
    memory_conn: sqlite3.Connection,
    isolated_publish_roots: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
):
    _insert_verified_component(memory_conn)
    project_root, staging_root = isolated_publish_roots
    _setup_mock_project_root(project_root)
    _seed_staging_component_stubs(staging_root)
    facade_path, backup_path = _facade_paths(project_root)

    calls: list[str] = []

    def _smoke_with_production_failure(root: Path, skill_id: str) -> None:
        calls.append(str(root.resolve()))
        if root.resolve() == project_root.resolve():
            raise RuntimeError("forced production smoke failure")
        run_v3_smoke(root, skill_id)

    monkeypatch.setattr(
        "core.gencode.v3_production_publish_service.run_v3_smoke",
        _smoke_with_production_failure,
    )

    result = publish_single_v3_skill_to_production(
        conn=memory_conn,
        skill_id=SKILL_ID,
        project_root=str(project_root),
        staging_root=str(staging_root),
    )

    assert result["status"] == "rolled_back_after_failed_production_smoke"
    assert facade_path.read_text(encoding="utf-8") == V2_LEGACY_CODE
    assert not backup_path.exists()
    assert not (project_root / "agent_skills_v3" / SKILL_ID).exists()
    assert len(calls) == 2
