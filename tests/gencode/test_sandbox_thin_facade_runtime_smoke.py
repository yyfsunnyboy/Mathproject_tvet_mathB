# -*- coding: utf-8 -*-
"""Runtime smoke tests for sandbox thin facade and V3 route dispatch."""

from __future__ import annotations

import importlib.util
import json
import py_compile
import shutil
import sqlite3
import sys
import uuid
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType

import pytest

from core.gencode.skill_wrapper_compiler import compile_and_double_write_skill

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
def sandbox_root() -> Iterator[Path]:
    base = SANDBOX_ROOT / f"pytest_runtime_smoke_{uuid.uuid4().hex}"
    base.mkdir(parents=True, exist_ok=True)
    original_sys_path = list(sys.path)
    try:
        yield base
    finally:
        for module_name in list(sys.modules):
            if module_name.startswith("sandbox_thin_facade_"):
                sys.modules.pop(module_name, None)
        sys.path[:] = original_sys_path
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
    ddl = DDL_PATH.read_text(encoding="utf-8")
    conn.executescript(ddl)
    yield conn
    conn.close()


def _insert_verified_tracker_row(conn: sqlite3.Connection) -> None:
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


def _component_dir(sandbox_root: Path) -> Path:
    return (
        sandbox_root
        / "agent_skills_v3"
        / SKILL_ID
        / "components"
        / COMPONENT_ID
    )


def _write_stub_component(sandbox_root: Path) -> None:
    component_dir = _component_dir(sandbox_root)
    component_dir.mkdir(parents=True, exist_ok=True)
    (component_dir / "metadata.py").write_text(STUB_METADATA_PY, encoding="utf-8")
    (component_dir / "generate.py").write_text(STUB_GENERATE_PY, encoding="utf-8")
    (component_dir / "get_hint.py").write_text(STUB_GET_HINT_PY, encoding="utf-8")


def _load_module_from_path(module_name: str, file_path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load module from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sandbox_thin_facade_runtime_smoke(memory_conn: sqlite3.Connection, sandbox_root: Path):
    _insert_verified_tracker_row(memory_conn)

    compile_result = compile_and_double_write_skill(
        memory_conn,
        SKILL_ID,
        str(sandbox_root),
    )
    assert compile_result["status"] == "compiled"

    _write_stub_component(sandbox_root)

    thin_facade_path = sandbox_root / "skills" / f"{SKILL_ID}.py"
    new_house_path = sandbox_root / "agent_skills_v3" / SKILL_ID / "__init__.py"
    component_generate_path = _component_dir(sandbox_root) / "generate.py"
    component_hint_path = _component_dir(sandbox_root) / "get_hint.py"

    for target in (
        thin_facade_path,
        new_house_path,
        component_generate_path,
        component_hint_path,
        _component_dir(sandbox_root) / "metadata.py",
    ):
        py_compile.compile(str(target), doraise=True)

    module_name = f"sandbox_thin_facade_{uuid.uuid4().hex}"
    facade = _load_module_from_path(module_name, thin_facade_path)
    sys.modules[module_name] = facade

    payload = facade.generate(seed=42)
    assert isinstance(payload, dict)
    assert payload.get("question_text")
    assert payload.get("answer")
    metadata = payload.get("metadata")
    assert isinstance(metadata, dict)
    assert metadata.get("component_id") == COMPONENT_ID

    assert facade.check("mock answer", "mock answer", question_payload=payload) is True
    hint = facade.get_hint(step=1, question_payload=payload)
    assert isinstance(hint, str)
    assert hint.strip()

    production_skills = PROJECT_ROOT / "skills" / f"{SKILL_ID}.py"
    production_v3 = PROJECT_ROOT / "agent_skills_v3"
    assert thin_facade_path.resolve().is_relative_to(sandbox_root.resolve())
    if production_v3.exists():
        assert not new_house_path.resolve().is_relative_to(production_v3.resolve())
    assert thin_facade_path != production_skills
