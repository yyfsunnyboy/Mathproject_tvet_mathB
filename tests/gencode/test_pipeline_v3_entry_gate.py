# -*- coding: utf-8 -*-
"""Tests for formal Phase 2 entry taxonomy gate."""

from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest

from core.gencode.pipeline_orchestrator import run_gencode_phase2_raw
from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
SKILL_ID = "vh_數學B1_PointSlopeForm"
COMPONENT_FILES = ("metadata.py", "generate.py", "get_hint.py")


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
            skill_id TEXT NOT NULL,
            problem_type_id TEXT,
            line_type TEXT,
            problem_text TEXT
        )
        """
    )
    apply_tracker_ddl(conn)
    yield conn
    conn.close()


@pytest.fixture
def dryrun_base_dir() -> Iterator[Path]:
    base = SANDBOX_ROOT / f"pytest_entry_gate_{uuid.uuid4().hex}"
    base.mkdir(parents=True, exist_ok=True)
    try:
        yield base
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_mvp_skill_enters_v3_shadow_bridge_from_formal_entry(
    memory_conn: sqlite3.Connection,
    dryrun_base_dir: Path,
):
    production_skills_snapshot = _snapshot_paths(PROJECT_ROOT / "skills")
    production_v3_snapshot = _snapshot_paths(PROJECT_ROOT / "agent_skills_v3")

    memory_conn.execute(
        "INSERT INTO textbook_examples (id, skill_id, problem_type_id, line_type, problem_text) VALUES (?, ?, ?, ?, ?)",
        (1, SKILL_ID, "write_line_equation_from_point_slope", "point_slope", "已知一點與斜率，求直線方程式"),
    )
    memory_conn.commit()

    result = run_gencode_phase2_raw(
        SKILL_ID,
        dry_run=True,
        v3_textbook_example_id=1,
        v3_conn=memory_conn,
        v3_dryrun_base_dir=str(dryrun_base_dir),
    )

    assert result["phase_status"] == "V3_SHADOW_BRIDGE"
    assert result["v3_activated"] is True
    assert result["route"] == "v3_shadow_bridge"
    assert result["tracker_status"] == "verified"
    assert result["textbook_example_id"] == 1

    tracker_row = memory_conn.execute(
        """
        SELECT gencode_status, textbook_example_id
        FROM gencode_component_tracker
        WHERE textbook_example_id = ?
        """,
        (1,),
    ).fetchone()
    assert tracker_row is not None
    assert tracker_row["gencode_status"] == "verified"
    assert tracker_row["textbook_example_id"] == 1

    component_dir = dryrun_base_dir / SKILL_ID / "components" / "src_1"
    manifest_path = dryrun_base_dir / SKILL_ID / "component_manifest.json"
    assert component_dir.exists()
    assert manifest_path.exists()
    for filename in COMPONENT_FILES:
        assert (component_dir / filename).exists()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["publish_status"] == "dryrun_manifest_compiled"

    assert _snapshot_paths(PROJECT_ROOT / "skills") == production_skills_snapshot
    assert _snapshot_paths(PROJECT_ROOT / "agent_skills_v3") == production_v3_snapshot


def test_non_mvp_skill_with_v3_example_id_enters_v3_not_v2(
    memory_conn: sqlite3.Connection,
    dryrun_base_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Passing v3_textbook_example_id always routes to V3 shadow bridge; V2 is retired."""
    v3_called = {"value": False}

    def _shadow_bridge(*args: object, **kwargs: object) -> dict[str, object]:
        v3_called["value"] = True
        return {
            "route": "v3_shadow_bridge",
            "v3_activated": True,
            "tracker_status": "verified",
        }

    monkeypatch.setattr(
        "core.gencode.pipeline_orchestrator.run_gencode_phase2_v3_shadow_bridge",
        _shadow_bridge,
    )

    result = run_gencode_phase2_raw(
        "legacy_skill_not_in_mvp",
        dry_run=True,
        v3_conn=memory_conn,
        v3_textbook_example_id=1,
        v3_dryrun_base_dir=str(dryrun_base_dir),
    )

    assert v3_called["value"] is True
    assert result.get("route") == "v3_shadow_bridge"
    assert result.get("v3_activated") is True


def test_mvp_skill_missing_textbook_example_id_does_not_fallback_to_v2(
    memory_conn: sqlite3.Connection,
    dryrun_base_dir: Path,
):
    memory_conn.execute(
        "INSERT INTO textbook_examples (id, skill_id, problem_text) VALUES (?, ?, ?)",
        (1, SKILL_ID, "已知點與斜率求直線方程式"),
    )
    memory_conn.commit()

    # Without v3_textbook_example_id the call stays on the SOP/legacy Phase2 path,
    # but must never invoke auto_generate_skill_code / V2 generator.
    import core.gencode.pipeline_orchestrator as orchestrator

    assert not hasattr(orchestrator, "auto_generate_skill_code")
    result = run_gencode_phase2_raw(
        SKILL_ID,
        dry_run=True,
        v3_conn=memory_conn,
        v3_dryrun_base_dir=str(dryrun_base_dir),
    )
    assert "v2" not in str(result.get("route", "")).lower()
    assert result.get("phase_status") != "v2_legacy_passthrough"

def test_mvp_skill_missing_conn_does_not_fallback_to_v2(
    memory_conn: sqlite3.Connection,
    dryrun_base_dir: Path,
):
    memory_conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (1, SKILL_ID),
    )
    memory_conn.commit()

    with pytest.raises(ValueError, match="missing_v3_conn"):
        run_gencode_phase2_raw(
            SKILL_ID,
            dry_run=True,
            v3_textbook_example_id=1,
            v3_dryrun_base_dir=str(dryrun_base_dir),
        )

    tracker_count = memory_conn.execute(
        "SELECT COUNT(*) FROM gencode_component_tracker"
    ).fetchone()[0]
    assert tracker_count == 0
    assert list(dryrun_base_dir.rglob("*")) == []
