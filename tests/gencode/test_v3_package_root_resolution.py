# -*- coding: utf-8 -*-
"""Tests for dynamic V3_PACKAGE_ROOT resolution in thin facades."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sqlite3
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest

from core.gencode.skill_wrapper_compiler import (
    compile_and_double_write_skill,
    resolve_v3_package_root_from_facade,
)
from core.gencode.v3_production_publish_service import publish_single_v3_skill_to_production

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DDL_PATH = PROJECT_ROOT / "core" / "gencode" / "schema" / "gencode_component_tracker.sql"
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
SKILL_ID = "vh_數學B1_PointSlopeForm"
COMPONENT_ID = "src_1"
PAYLOAD = {
    "source_kind": "ex_1",
    "presentation_mode": "short_answer",
    "line_type": "point_slope",
}

STUB_GENERATE_PY = '''from __future__ import annotations
from typing import Any
def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    return {"question_text": "q", "correct_answer": "a", "component_id": "src_1"}
def check(user_answer, correct_answer, question_payload=None):
    return True
'''

STUB_GET_HINT_PY = '''from __future__ import annotations
def get_hint(step, question_payload=None):
    return "hint"
'''

STUB_METADATA_PY = "COMPONENT_ID = 'src_1'\n"


@pytest.fixture
def isolated_roots() -> Iterator[tuple[Path, Path]]:
    base = SANDBOX_ROOT / f"pytest_v3_root_{uuid.uuid4().hex}"
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
        "CREATE TABLE textbook_examples (id INTEGER PRIMARY KEY, skill_id TEXT NOT NULL)"
    )
    conn.executescript(DDL_PATH.read_text(encoding="utf-8"))
    conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (1, SKILL_ID),
    )
    conn.execute(
        """
        INSERT INTO gencode_component_tracker (
            textbook_example_id, skill_id, component_id, gencode_status, induced_spec_payload
        ) VALUES (?, ?, ?, 'verified', ?)
        """,
        (1, SKILL_ID, COMPONENT_ID, json.dumps(PAYLOAD, ensure_ascii=False)),
    )
    conn.commit()
    yield conn
    conn.close()


def _load_facade(facade_path: Path):
    spec = importlib.util.spec_from_file_location(f"facade_{uuid.uuid4().hex}", facade_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _seed_staging_components(staging_root: Path) -> None:
    component_dir = staging_root / SKILL_ID / "components" / COMPONENT_ID
    component_dir.mkdir(parents=True, exist_ok=True)
    (component_dir / "metadata.py").write_text(STUB_METADATA_PY, encoding="utf-8")
    (component_dir / "generate.py").write_text(STUB_GENERATE_PY, encoding="utf-8")
    (component_dir / "get_hint.py").write_text(STUB_GET_HINT_PY, encoding="utf-8")


def test_staging_facade_resolves_staging_agent_skills_v3(
    memory_conn: sqlite3.Connection,
    isolated_roots: tuple[Path, Path],
):
    _project_root, staging_root = isolated_roots
    (staging_root / "skills").mkdir(parents=True, exist_ok=True)
    compile_and_double_write_skill(memory_conn, SKILL_ID, str(staging_root))

    facade_path = staging_root / "skills" / f"{SKILL_ID}.py"
    source = facade_path.read_text(encoding="utf-8")
    assert "gencode_v3_publish_staging" not in source
    assert "V3_PACKAGE_ROOT =" not in source
    assert "_resolve_v3_package_root" in source

    module = _load_facade(facade_path)
    resolved = Path(module._resolve_v3_package_root()).resolve()
    expected = (staging_root / "agent_skills_v3").resolve()
    assert resolved == expected


def test_production_facade_resolves_production_agent_skills_v3(
    memory_conn: sqlite3.Connection,
    isolated_roots: tuple[Path, Path],
):
    project_root, staging_root = isolated_roots
    (project_root / "skills").mkdir(parents=True, exist_ok=True)
    (project_root / "agent_skills_v3").mkdir(parents=True, exist_ok=True)
    (project_root / "skills" / f"{SKILL_ID}.py").write_text("LEGACY", encoding="utf-8")
    _seed_staging_components(staging_root)

    result = publish_single_v3_skill_to_production(
        conn=memory_conn,
        skill_id=SKILL_ID,
        project_root=str(project_root),
        staging_root=str(staging_root),
    )
    assert result["status"] == "production_published"

    facade_path = project_root / "skills" / f"{SKILL_ID}.py"
    source = facade_path.read_text(encoding="utf-8")
    assert "gencode_v3_publish_staging" not in source
    assert "reports/" not in source
    assert "V3_PACKAGE_ROOT =" not in source

    module = _load_facade(facade_path)
    resolved = Path(module._resolve_v3_package_root()).resolve()
    expected = (project_root / "agent_skills_v3").resolve()
    assert resolved == expected
    assert resolve_v3_package_root_from_facade(facade_path) == expected
