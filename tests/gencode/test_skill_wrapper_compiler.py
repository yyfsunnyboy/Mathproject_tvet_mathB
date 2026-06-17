# -*- coding: utf-8 -*-
"""Integration tests for sandbox V3 skill wrapper compiler."""

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

FORBIDDEN_NEW_HOUSE_TOKENS = (
    "import sympy",
    "import matplotlib",
    "db.session",
    "Flask",
    "textbook_examples",
)

FORBIDDEN_THIN_FACADE_TOKENS = (
    "import sympy",
    "import matplotlib",
    "Fraction",
    "gcd(",
    "_compute_slope",
    "_build_distractors",
    "db.session",
    "Flask",
    "textbook_examples",
    "SkillInfo",
)


@pytest.fixture
def sandbox_root() -> Iterator[Path]:
    base = SANDBOX_ROOT / f"pytest_compiler_{uuid.uuid4().hex}"
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
    ddl = DDL_PATH.read_text(encoding="utf-8")
    conn.executescript(ddl)
    yield conn
    conn.close()


def _insert_verified_component(
    conn: sqlite3.Connection,
    *,
    textbook_example_id: int,
) -> None:
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
            textbook_example_id,
            SKILL_ID,
            f"src_{textbook_example_id}",
            json.dumps(PAYLOAD, ensure_ascii=False),
        ),
    )


def test_compile_and_double_write_skill_deterministic_order(
    memory_conn: sqlite3.Connection,
    sandbox_root: Path,
):
    _insert_verified_component(memory_conn, textbook_example_id=4610)
    _insert_verified_component(memory_conn, textbook_example_id=4545)
    memory_conn.commit()

    result = compile_and_double_write_skill(
        memory_conn,
        SKILL_ID,
        str(sandbox_root),
    )

    assert result["status"] == "compiled"
    assert result["skill_id"] == SKILL_ID
    assert result["component_count"] == 2
    assert result["generator_keys"] == ["src_4545", "src_4610"]

    new_house_path = sandbox_root / "agent_skills_v3" / SKILL_ID / "__init__.py"
    thin_facade_path = sandbox_root / "skills" / f"{SKILL_ID}.py"
    assert new_house_path.exists()
    assert thin_facade_path.exists()

    new_house_source = new_house_path.read_text(encoding="utf-8")
    thin_facade_source = thin_facade_path.read_text(encoding="utf-8")

    first_index = new_house_source.index("src_4545")
    second_index = new_house_source.index("src_4610")
    assert first_index < second_index

    for token in (
        "GENERATOR_KEYS",
        "GENERATOR_SPECS",
        "_COMPONENT_DISPATCH",
        "def generate(",
        "def check(",
        "def get_hint(",
    ):
        assert token in new_house_source

    for token in FORBIDDEN_NEW_HOUSE_TOKENS:
        assert token not in new_house_source

    for token in ("def generate(", "def check(", "def get_hint("):
        assert token in thin_facade_source

    for token in FORBIDDEN_THIN_FACADE_TOKENS:
        assert token not in thin_facade_source

    assert "V3_PACKAGE_ROOT =" not in thin_facade_source
    assert "_resolve_v3_package_root" in thin_facade_source
    assert "gencode_v3_publish_staging" not in thin_facade_source

    assert str(new_house_path.resolve()) == result["new_house_path"]
    assert str(thin_facade_path.resolve()) == result["thin_facade_path"]


def test_assert_safe_sandbox_root_blocks_production_paths():
    blocked_roots = ["", ".", "skills", "agent_skills_v3"]
    for root in blocked_roots:
        with pytest.raises(ValueError, match="unsafe_sandbox_root"):
            assert_safe_sandbox_root(root)

    with pytest.raises(ValueError, match="unsafe_sandbox_root"):
        assert_safe_sandbox_root(str(PROJECT_ROOT))


def test_compile_raises_when_no_verified_components(
    memory_conn: sqlite3.Connection,
    sandbox_root: Path,
):
    with pytest.raises(ValueError, match="no_verified_components"):
        compile_and_double_write_skill(
            memory_conn,
            SKILL_ID,
            str(sandbox_root),
        )


def test_compile_does_not_touch_production_directories(
    memory_conn: sqlite3.Connection,
    sandbox_root: Path,
):
    production_skills = PROJECT_ROOT / "skills"
    production_v3 = PROJECT_ROOT / "agent_skills_v3"
    skills_existed = production_skills.exists()
    v3_existed = production_v3.exists()

    _insert_verified_component(memory_conn, textbook_example_id=4545)
    memory_conn.commit()

    compile_and_double_write_skill(memory_conn, SKILL_ID, str(sandbox_root))

    if not skills_existed:
        assert not production_skills.exists() or production_skills.is_dir()
    if not v3_existed:
        assert not production_v3.exists() or production_v3.is_dir()
