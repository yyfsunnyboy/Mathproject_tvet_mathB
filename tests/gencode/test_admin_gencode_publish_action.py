# -*- coding: utf-8 -*-
"""Tests for admin skill-level V3 production publish action."""

from __future__ import annotations

import json
import shutil
import sqlite3
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest

from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.services.admin_gencode_action_service import run_admin_v3_publish_for_skill
from core.gencode.skill_wrapper_compiler import rollback_v3_to_v2_facade
from core.gencode.v3_production_publish_service import ALLOWED_PRODUCTION_SKILL_ID

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
SKILL_ID = ALLOWED_PRODUCTION_SKILL_ID
COMPONENT_ID = "src_1"
V2_LEGACY_CODE = "V2_LEGACY_CODE"
PAYLOAD = {
    "source_kind": "ex_1",
    "presentation_mode": "short_answer",
    "line_type": "point_slope",
    "integrity_gate_passed": True,
    "integrity_gate_version": "v1",
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
    base = SANDBOX_ROOT / f"pytest_admin_publish_{uuid.uuid4().hex}"
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


def _setup_mock_project_root(project_root: Path) -> None:
    (project_root / "skills").mkdir(parents=True, exist_ok=True)
    (project_root / "agent_skills_v3").mkdir(parents=True, exist_ok=True)
    facade_path = project_root / "skills" / f"{SKILL_ID}.py"
    facade_path.write_text(V2_LEGACY_CODE, encoding="utf-8")


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

    result = run_admin_v3_publish_for_skill(
        conn=memory_conn,
        skill_id=SKILL_ID,
        project_root=str(project_root),
        staging_root=str(staging_root),
        force_publish=True,
    )

    assert result["status"] == "production_published"
    assert result["component_count"] == 1
    assert result["verified_component_count"] == 1

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


def test_publish_requires_force_publish(
    memory_conn: sqlite3.Connection,
    isolated_publish_roots: tuple[Path, Path],
):
    _insert_verified_component(memory_conn)
    project_root, staging_root = isolated_publish_roots
    _setup_mock_project_root(project_root)

    with pytest.raises(ValueError, match="production_publish_requires_force_publish"):
        run_admin_v3_publish_for_skill(
            conn=memory_conn,
            skill_id=SKILL_ID,
            project_root=str(project_root),
            staging_root=str(staging_root),
            force_publish=False,
        )


def test_publish_rejects_non_benchmark_skill(
    memory_conn: sqlite3.Connection,
    isolated_publish_roots: tuple[Path, Path],
):
    _insert_verified_component(memory_conn)
    project_root, staging_root = isolated_publish_roots
    _setup_mock_project_root(project_root)

    # jh_* skills are not in the vh_* taxonomy scope → taxonomy_not_registered
    with pytest.raises(ValueError, match="taxonomy_not_registered"):
        run_admin_v3_publish_for_skill(
            conn=memory_conn,
            skill_id="jh_數學1上_FourArithmeticOperationsOfIntegers",
            project_root=str(project_root),
            staging_root=str(staging_root),
            force_publish=True,
        )


def test_publish_rejects_missing_verified_components(
    memory_conn: sqlite3.Connection,
    isolated_publish_roots: tuple[Path, Path],
):
    from unittest import mock
    project_root, staging_root = isolated_publish_roots
    _setup_mock_project_root(project_root)

    with mock.patch("core.gencode.services.admin_gencode_action_service.evaluate_v3_publish_eligibility", return_value={"allowed": True}):
        with pytest.raises(ValueError, match="no_verified_components"):
            run_admin_v3_publish_for_skill(
                conn=memory_conn,
                skill_id=SKILL_ID,
                project_root=str(project_root),
                staging_root=str(staging_root),
                force_publish=True,
            )


def test_publish_rejects_when_verified_rows_cleared(
    memory_conn: sqlite3.Connection,
    isolated_publish_roots: tuple[Path, Path],
):
    from unittest import mock
    _insert_verified_component(memory_conn)
    project_root, staging_root = isolated_publish_roots
    _setup_mock_project_root(project_root)
    memory_conn.execute("DELETE FROM gencode_component_tracker")
    memory_conn.commit()

    with mock.patch("core.gencode.services.admin_gencode_action_service.evaluate_v3_publish_eligibility", return_value={"allowed": True}):
        with pytest.raises(ValueError, match="no_verified_components"):
            run_admin_v3_publish_for_skill(
                conn=memory_conn,
                skill_id=SKILL_ID,
                project_root=str(project_root),
                staging_root=str(staging_root),
                force_publish=True,
            )


def test_template_has_publish_button_contract():
    content = (PROJECT_ROOT / "templates" / "admin_skills.html").read_text(encoding="utf-8")
    assert "admin_run_skill_v3_repackage" in content
    assert "admin_run_skill_v3_dryrun" in content
    assert "V3 重新包裝" in content
    assert "V3 重新生成" in content
    assert "publish_eligible" in content
    assert "verified_count" in content
    assert "repackageSkillV3" in content
