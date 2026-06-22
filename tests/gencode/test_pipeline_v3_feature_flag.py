# -*- coding: utf-8 -*-
"""Feature flag controlled production publish hook tests."""

from __future__ import annotations

import json
import shutil
import sqlite3
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest

from core.gencode.pipeline_orchestrator import run_gencode_phase2_raw
from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.skill_wrapper_compiler import rollback_v3_to_v2_facade

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
BENCHMARK_SKILL_ID = "vh_數學B1_PointSlopeForm"
COMPONENT_ID = "src_1"
V2_LEGACY_CODE = "V2_LEGACY_CODE"
PAYLOAD = {
    "source_kind": "ex_1",
    "presentation_mode": "short_answer",
    "line_type": "point_slope",
    "fixed_domain_key": "coordinate_geometry.line_equation",
    "domain_operation": "point_slope",
    "problem_type_id": "point_slope",
    "integrity_gate_passed": True,
    "integrity_gate_version": "v1",
}

STUB_METADATA_PY = 'COMPONENT_ID = "src_1"\n'
STUB_GENERATE_PY = """
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
"""
STUB_GET_HINT_PY = """
def get_hint(step: int, question_payload: dict[str, object] | None = None) -> str:
    return f"hint step {step}"
"""


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
def isolated_roots() -> Iterator[dict[str, Path]]:
    base = SANDBOX_ROOT / f"pytest_v3_feature_flag_{uuid.uuid4().hex}"
    dryrun_root = base / "dryrun"
    project_root = base / "project"
    staging_root = base / "staging"
    for root in (dryrun_root, project_root, staging_root):
        root.mkdir(parents=True, exist_ok=True)
    (project_root / "skills").mkdir(parents=True, exist_ok=True)
    (project_root / "agent_skills_v3").mkdir(parents=True, exist_ok=True)
    (project_root / "skills" / f"{BENCHMARK_SKILL_ID}.py").write_text(V2_LEGACY_CODE, encoding="utf-8")
    try:
        yield {
            "base": base,
            "dryrun_root": dryrun_root,
            "project_root": project_root,
            "staging_root": staging_root,
        }
    finally:
        shutil.rmtree(base, ignore_errors=True)


def _insert_verified_component(conn: sqlite3.Connection, *, skill_id: str = BENCHMARK_SKILL_ID) -> None:
    conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (1, skill_id),
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
        (1, skill_id, COMPONENT_ID, json.dumps(PAYLOAD, ensure_ascii=False)),
    )
    conn.commit()


def _seed_staging_component_stubs(staging_root: Path, *, skill_id: str = BENCHMARK_SKILL_ID) -> None:
    component_dir = staging_root / skill_id / "components" / COMPONENT_ID
    component_dir.mkdir(parents=True, exist_ok=True)
    (component_dir / "metadata.py").write_text(STUB_METADATA_PY, encoding="utf-8")
    (component_dir / "generate.py").write_text(STUB_GENERATE_PY, encoding="utf-8")
    (component_dir / "get_hint.py").write_text(STUB_GET_HINT_PY, encoding="utf-8")


def _fake_shadow_bridge_factory(dryrun_root: Path):
    def _fake_shadow_bridge(**kwargs: object) -> dict[str, object]:
        skill_id = str(kwargs["skill_id"])
        component_dir = dryrun_root / skill_id / "components" / COMPONENT_ID
        component_dir.mkdir(parents=True, exist_ok=True)
        for filename in ("metadata.py", "generate.py", "get_hint.py"):
            (component_dir / filename).write_text("# dryrun shadow stub\n", encoding="utf-8")
        return {
            "route": "v3_shadow_bridge",
            "skill_id": skill_id,
            "v3_activated": True,
            "tracker_status": "draft_written",
            "textbook_example_id": int(kwargs["textbook_example_id"]),
        }

    return _fake_shadow_bridge


def test_feature_flag_disabled_keeps_production_locked(
    memory_conn: sqlite3.Connection,
    isolated_roots: dict[str, Path],
    monkeypatch: pytest.MonkeyPatch,
):
    _insert_verified_component(memory_conn)
    monkeypatch.setattr("core.gencode.pipeline_orchestrator.V3_PRODUCTION_PUBLISH_ENABLED", False)
    monkeypatch.setattr(
        "core.gencode.pipeline_orchestrator.run_gencode_phase2_v3_shadow_bridge",
        _fake_shadow_bridge_factory(isolated_roots["dryrun_root"]),
    )

    def _forbidden_publish(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("publish_single_v3_skill_to_production should not be called when flag is disabled")

    monkeypatch.setattr(
        "core.gencode.v3_production_publish_service.publish_single_v3_skill_to_production",
        _forbidden_publish,
    )

    result = run_gencode_phase2_raw(
        BENCHMARK_SKILL_ID,
        dry_run=True,
        v3_textbook_example_id=1,
        v3_conn=memory_conn,
        v3_dryrun_base_dir=str(isolated_roots["dryrun_root"]),
        v3_project_root=str(isolated_roots["project_root"]),
        v3_staging_root=str(isolated_roots["staging_root"]),
    )

    assert result["phase_status"] == "V3_SHADOW_BRIDGE"
    assert result["production_publish_enabled"] is False
    assert result["production_publish_status"] == "disabled"
    assert result["production_publish_report"] is None
    assert (isolated_roots["project_root"] / "skills" / f"{BENCHMARK_SKILL_ID}.py").read_text(encoding="utf-8") == V2_LEGACY_CODE
    assert not (isolated_roots["project_root"] / "skills" / f"{BENCHMARK_SKILL_ID}.py.bak").exists()
    assert not (isolated_roots["project_root"] / "agent_skills_v3" / BENCHMARK_SKILL_ID).exists()
    assert (isolated_roots["dryrun_root"] / BENCHMARK_SKILL_ID / "components" / COMPONENT_ID).exists()


def test_feature_flag_enabled_publishes_and_can_rollback(
    memory_conn: sqlite3.Connection,
    isolated_roots: dict[str, Path],
    monkeypatch: pytest.MonkeyPatch,
):
    _insert_verified_component(memory_conn)
    _seed_staging_component_stubs(isolated_roots["staging_root"])
    monkeypatch.setattr("core.gencode.pipeline_orchestrator.V3_PRODUCTION_PUBLISH_ENABLED", True)
    monkeypatch.setattr(
        "core.gencode.pipeline_orchestrator.run_gencode_phase2_v3_shadow_bridge",
        _fake_shadow_bridge_factory(isolated_roots["dryrun_root"]),
    )

    result = run_gencode_phase2_raw(
        BENCHMARK_SKILL_ID,
        dry_run=True,
        v3_textbook_example_id=1,
        v3_conn=memory_conn,
        v3_dryrun_base_dir=str(isolated_roots["dryrun_root"]),
        v3_project_root=str(isolated_roots["project_root"]),
        v3_staging_root=str(isolated_roots["staging_root"]),
    )

    assert result["production_publish_enabled"] is True
    assert result["production_publish_status"] == "production_published"
    facade_path = isolated_roots["project_root"] / "skills" / f"{BENCHMARK_SKILL_ID}.py"
    backup_path = isolated_roots["project_root"] / "skills" / f"{BENCHMARK_SKILL_ID}.py.bak"
    assert backup_path.exists()
    assert backup_path.read_text(encoding="utf-8") == V2_LEGACY_CODE
    assert "runtime_skill_wrapper" in facade_path.read_text(encoding="utf-8")
    assert (isolated_roots["project_root"] / "agent_skills_v3" / BENCHMARK_SKILL_ID / "__init__.py").exists()

    rollback_result = rollback_v3_to_v2_facade(
        BENCHMARK_SKILL_ID,
        str(isolated_roots["project_root"]),
        trusted_project_root=True,
    )
    assert rollback_result["status"] == "rolled_back"
    assert facade_path.read_text(encoding="utf-8") == V2_LEGACY_CODE


def test_feature_flag_enabled_requires_project_and_staging_root(
    memory_conn: sqlite3.Connection,
    isolated_roots: dict[str, Path],
    monkeypatch: pytest.MonkeyPatch,
):
    _insert_verified_component(memory_conn)
    monkeypatch.setattr("core.gencode.pipeline_orchestrator.V3_PRODUCTION_PUBLISH_ENABLED", True)
    monkeypatch.setattr(
        "core.gencode.pipeline_orchestrator.run_gencode_phase2_v3_shadow_bridge",
        _fake_shadow_bridge_factory(isolated_roots["dryrun_root"]),
    )

    with pytest.raises(ValueError, match="missing_v3_project_root"):
        run_gencode_phase2_raw(
            BENCHMARK_SKILL_ID,
            dry_run=True,
            v3_textbook_example_id=1,
            v3_conn=memory_conn,
            v3_dryrun_base_dir=str(isolated_roots["dryrun_root"]),
            v3_staging_root=str(isolated_roots["staging_root"]),
        )

    with pytest.raises(ValueError, match="missing_v3_staging_root"):
        run_gencode_phase2_raw(
            BENCHMARK_SKILL_ID,
            dry_run=True,
            v3_textbook_example_id=1,
            v3_conn=memory_conn,
            v3_dryrun_base_dir=str(isolated_roots["dryrun_root"]),
            v3_project_root=str(isolated_roots["project_root"]),
        )

    assert (isolated_roots["project_root"] / "skills" / f"{BENCHMARK_SKILL_ID}.py").read_text(encoding="utf-8") == V2_LEGACY_CODE
    assert not (isolated_roots["project_root"] / "skills" / f"{BENCHMARK_SKILL_ID}.py.bak").exists()


def test_non_mvp_skill_stays_v2_route_and_shape(
    memory_conn: sqlite3.Connection,
    isolated_roots: dict[str, Path],
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("core.gencode.pipeline_orchestrator.V3_PRODUCTION_PUBLISH_ENABLED", True)
    monkeypatch.setattr(
        "core.gencode.pipeline_orchestrator.run_gencode_phase2_v3_shadow_bridge",
        lambda **_kwargs: (_ for _ in ()).throw(AssertionError("shadow bridge should not run for non-MVP skill")),
    )
    monkeypatch.setattr(
        "core.gencode.v3_production_publish_service.publish_single_v3_skill_to_production",
        lambda **_kwargs: (_ for _ in ()).throw(AssertionError("publish should not run for non-MVP skill")),
    )
    monkeypatch.setattr(
        "core.gencode.sop_policy.validate_sop_preflight",
        lambda *_args, **_kwargs: {"sop_preflight_status": "FAIL", "errors": ["test_gate"]},
    )

    tracker_before = memory_conn.execute("SELECT COUNT(*) AS c FROM gencode_component_tracker").fetchone()["c"]
    result = run_gencode_phase2_raw("legacy_skill_not_in_mvp", dry_run=True, v3_conn=memory_conn, v3_textbook_example_id=1)
    tracker_after = memory_conn.execute("SELECT COUNT(*) AS c FROM gencode_component_tracker").fetchone()["c"]

    assert result.get("phase_status") == "SOP_PREFLIGHT_FAIL"
    assert "production_publish_enabled" not in result
    assert tracker_after == tracker_before
    assert list(isolated_roots["dryrun_root"].rglob("*")) == []


def test_mvp_but_non_benchmark_skill_rejected_when_flag_enabled(
    memory_conn: sqlite3.Connection,
    isolated_roots: dict[str, Path],
    monkeypatch: pytest.MonkeyPatch,
):
    memory_conn.execute("INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)", (1, "vh_fake_MVP"))
    memory_conn.commit()
    monkeypatch.setattr("core.gencode.pipeline_orchestrator.V3_PRODUCTION_PUBLISH_ENABLED", True)
    monkeypatch.setattr(
        "core.gencode.pipeline_orchestrator._load_v3_taxonomy_mvp_scope",
        lambda _path: {BENCHMARK_SKILL_ID, "vh_fake_MVP"},
    )
    monkeypatch.setattr(
        "core.gencode.pipeline_orchestrator.run_gencode_phase2_v3_shadow_bridge",
        _fake_shadow_bridge_factory(isolated_roots["dryrun_root"]),
    )

    with pytest.raises(ValueError, match="skill_domain_not_registered|v3_publish_not_eligible|no_eligible_components"):
        run_gencode_phase2_raw(
            "vh_fake_MVP",
            dry_run=True,
            v3_textbook_example_id=1,
            v3_conn=memory_conn,
            v3_dryrun_base_dir=str(isolated_roots["dryrun_root"]),
            v3_project_root=str(isolated_roots["project_root"]),
            v3_staging_root=str(isolated_roots["staging_root"]),
        )

    assert (isolated_roots["project_root"] / "skills" / f"{BENCHMARK_SKILL_ID}.py").read_text(encoding="utf-8") == V2_LEGACY_CODE
    assert not (isolated_roots["project_root"] / "skills" / f"{BENCHMARK_SKILL_ID}.py.bak").exists()
    assert not (isolated_roots["project_root"] / "agent_skills_v3" / "vh_fake_MVP").exists()
