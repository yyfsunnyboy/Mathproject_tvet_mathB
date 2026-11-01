# -*- coding: utf-8 -*-
"""The V3 shadow bridge builds deterministic system scaffolds, not AI Python: no healer runs there."""

from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest

import core.gencode.pipeline_orchestrator as orchestrator
from core.gencode.pipeline_orchestrator import run_gencode_phase2_v3_shadow_bridge
from core.gencode.research_healer.adapter import HEALER_MODE_ENV
from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.schema.gencode_v3_healer_telemetry_inspection import healer_telemetry_table_exists

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
SKILL_ID = "vh_數學B1_PointSlopeForm"
CONSTRAINTS = {"line_type": "point_slope", "problem_type_id": "point_slope", "domain_operation": "point_slope"}
EXAMPLE_ROW = ("已知點 (1,2) 與斜率 3，求直線方程式。", "y-2=3(x-1)", "point_slope")
DELIMITER_FAULT = ('constraints["skill_id"] =', 'constraints["skill_id" =')


def _snapshot_paths(root: Path) -> dict[str, str]:
    if not root.exists():
        return {}
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


@pytest.fixture
def memory_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT NOT NULL,
            problem_text TEXT,
            correct_answer TEXT,
            source_description TEXT,
            problem_type TEXT
        )
        """
    )
    conn.execute(
        "INSERT INTO textbook_examples (id, skill_id, problem_text, correct_answer, problem_type) VALUES (?, ?, ?, ?, ?)",
        (1, SKILL_ID, *EXAMPLE_ROW),
    )
    apply_tracker_ddl(conn)
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def dryrun_base_dir() -> Iterator[Path]:
    base = SANDBOX_ROOT / f"pytest_v3_healer_{uuid.uuid4().hex}"
    base.mkdir(parents=True, exist_ok=True)
    try:
        yield base
    finally:
        shutil.rmtree(base, ignore_errors=True)


@pytest.fixture
def production_guard() -> Iterator[None]:
    skills = _snapshot_paths(PROJECT_ROOT / "skills")
    v3 = _snapshot_paths(PROJECT_ROOT / "agent_skills_v3")
    yield
    assert _snapshot_paths(PROJECT_ROOT / "skills") == skills
    assert _snapshot_paths(PROJECT_ROOT / "agent_skills_v3") == v3


@pytest.fixture
def forbid_all_healers(monkeypatch: pytest.MonkeyPatch) -> None:
    def _forbidden(*args, **kwargs):
        raise AssertionError("no healer may run inside the V3 shadow bridge")

    for target in (
        "core.gencode.research_healer.adapter.heal_ai_python_source",
        "core.gencode.research_healer.adapter.heal_coder_files",
        "core.gencode.v3_healer_adapter.heal_v3_component",
        "core.gencode.v3_healer_adapter.heal_v3_component_after_exec_failure",
    ):
        monkeypatch.setattr(target, _forbidden)


def test_shadow_bridge_source_has_no_healer_hook():
    source = Path(orchestrator.__file__).read_text(encoding="utf-8")
    assert "healer" not in source.lower()


@pytest.mark.parametrize("mode", [None, "shadow", "repair"])
def test_shadow_bridge_never_heals_scaffold_in_any_mode(
    memory_conn, dryrun_base_dir, production_guard, forbid_all_healers, monkeypatch, mode
):
    if mode is None:
        monkeypatch.delenv(HEALER_MODE_ENV, raising=False)
    else:
        monkeypatch.setenv(HEALER_MODE_ENV, mode)
    real_builder = orchestrator.build_v3_component_draft_from_skill

    def _builder(**kwargs):
        draft = real_builder(**kwargs)
        code = draft["files"]["generate.py"]
        assert code.count(DELIMITER_FAULT[0]) == 1
        draft["files"]["generate.py"] = code.replace(*DELIMITER_FAULT)
        return draft

    monkeypatch.setattr(orchestrator, "build_v3_component_draft_from_skill", _builder)
    with pytest.raises(ValueError, match="source_fidelity_failed: integrity_gate_blocker:execution_error:SyntaxError"):
        run_gencode_phase2_v3_shadow_bridge(
            conn=memory_conn,
            skill_id=SKILL_ID,
            textbook_example_id=1,
            source_kind="ex_1",
            seed=42,
            dryrun_base_dir=str(dryrun_base_dir),
            constraints=dict(CONSTRAINTS),
        )
    row = memory_conn.execute(
        "SELECT gencode_status, induced_spec_payload FROM gencode_component_tracker WHERE textbook_example_id = 1"
    ).fetchone()
    assert row["gencode_status"] == "failed"
    assert "v3_healer" not in json.loads(row["induced_spec_payload"] or "{}")
    assert not (dryrun_base_dir / SKILL_ID / "components" / "src_1").exists()
    assert not healer_telemetry_table_exists(memory_conn)
