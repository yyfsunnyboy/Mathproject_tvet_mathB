# -*- coding: utf-8 -*-
"""Tests for skill-level V3 batch dryrun service."""

from __future__ import annotations

import shutil
import sqlite3
import time
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest

from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.services.admin_gencode_action_service import (
    run_admin_v3_dryrun_for_example,
    run_admin_v3_dryrun_for_skill,
)
from core.gencode.services.component_tracker_service import save_tracker_record

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
SKILL_ID = "vh_數學B1_HorizontalAndVerticalLineEquations"


@pytest.fixture
def memory_conn() -> Iterator[sqlite3.Connection]:
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
    # 4544 is vertical line, 4553 is horizontal line
    conn.execute(
        "INSERT INTO textbook_examples (id, skill_id, problem_type_id, line_type, problem_text) VALUES (?, ?, ?, ?, ?)",
        (4544, SKILL_ID, "vertical_line", "vertical_line", "垂直線"),
    )
    conn.execute(
        "INSERT INTO textbook_examples (id, skill_id, problem_type_id, line_type, problem_text) VALUES (?, ?, ?, ?, ?)",
        (4553, SKILL_ID, "horizontal_line", "horizontal_line", "水平線"),
    )
    conn.commit()
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def dryrun_root() -> Iterator[Path]:
    base = SANDBOX_ROOT / f"pytest_batch_{uuid.uuid4().hex}"
    base.mkdir(parents=True, exist_ok=True)
    try:
        yield base
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_batch_dryrun_processes_all_examples(memory_conn, dryrun_root):
    result = run_admin_v3_dryrun_for_skill(
        memory_conn,
        SKILL_ID,
        dryrun_base_dir=str(dryrun_root),
        seed=42,
    )

    assert result["total_examples"] == 2
    assert result["processed_count"] == 2
    assert result["success_count"] == 2
    assert result["failed_count"] == 0
    statuses = {row["textbook_example_id"]: row["status"] for row in result["results"]}
    assert statuses[4544] == "processed"
    assert statuses[4553] == "processed"


def test_batch_dryrun_skips_verified_unless_force(memory_conn, dryrun_root):
    run_admin_v3_dryrun_for_example(
        conn=memory_conn,
        textbook_example_id=4544,
        skill_id=SKILL_ID,
        dryrun_base_dir=str(dryrun_root),
        seed=42,
    )
    memory_conn.execute(
        """
        UPDATE gencode_component_tracker
        SET gencode_status = 'verified'
        WHERE textbook_example_id = 4544
        """
    )
    memory_conn.commit()

    skipped = run_admin_v3_dryrun_for_skill(
        memory_conn,
        SKILL_ID,
        dryrun_base_dir=str(dryrun_root),
        seed=42,
    )
    assert skipped["skipped_verified_count"] == 1
    skipped_rows = [row for row in skipped["results"] if row["status"] == "reused_verified"]
    assert skipped_rows
    assert skipped_rows[0]["cache_hit"] is True
    assert skipped_rows[0]["skip_reason"] == "verified_tracker_reused"
    assert skipped_rows[0]["model_generation_invoked"] is False

    forced = run_admin_v3_dryrun_for_skill(
        memory_conn,
        SKILL_ID,
        dryrun_base_dir=str(dryrun_root),
        seed=42,
        mode="regenerate",
        force=True,
    )
    assert forced["skipped_verified_count"] == 0
    assert all(row["cache_hit"] is False for row in forced["results"])
    assert all(row["generation_run_id"] for row in forced["results"])
    assert all(row["model_generation_invoked"] is True for row in forced["results"])


def test_force_regenerate_verified_component_updates_run_id_and_overwrites_generate(
    memory_conn,
    dryrun_root,
):
    first = run_admin_v3_dryrun_for_example(
        conn=memory_conn,
        textbook_example_id=4544,
        skill_id=SKILL_ID,
        dryrun_base_dir=str(dryrun_root),
        seed=42,
    )
    generate_py = Path(first["dryrun_component_dir"]) / "generate.py"
    old_mtime = generate_py.stat().st_mtime
    old_hash = first["new_artifact_hash"]
    old_run_id = first["generation_run_id"]
    memory_conn.execute(
        """
        UPDATE gencode_component_tracker
        SET gencode_status = 'verified'
        WHERE textbook_example_id = 4544
        """
    )
    memory_conn.commit()
    time.sleep(1.05)

    forced = run_admin_v3_dryrun_for_example(
        conn=memory_conn,
        textbook_example_id=4544,
        skill_id=SKILL_ID,
        dryrun_base_dir=str(dryrun_root),
        seed=42,
        force_regenerate=True,
    )

    assert forced["cache_hit"] is False
    assert forced["model_generation_invoked"] is True
    assert forced["generation_run_id"] != old_run_id
    assert forced["old_artifact_hash"] == old_hash
    assert generate_py.stat().st_mtime > old_mtime
    assert forced["new_generate_mtime"] > old_mtime


def test_force_regenerate_processes_all_three_components(memory_conn, dryrun_root, monkeypatch):
    memory_conn.execute(
        "INSERT INTO textbook_examples (id, skill_id, problem_type_id, line_type, problem_text) VALUES (?, ?, ?, ?, ?)",
        (4666, SKILL_ID, "vertical_line", "vertical_line", "third example"),
    )
    memory_conn.commit()
    calls: list[int] = []

    def _fake_example(**kwargs):
        example_id = int(kwargs["textbook_example_id"])
        calls.append(example_id)
        component_id = f"src_{example_id}"
        run_id = uuid.uuid4().hex
        save_tracker_record(
            kwargs["conn"],
            textbook_example_id=example_id,
            skill_id=kwargs["skill_id"],
            gencode_status="verified",
            induced_spec_payload={
                "generation_run_id": run_id,
                "force_regenerate": bool(kwargs.get("force_regenerate")),
                "cache_hit": False,
                "model_generation_invoked": True,
            },
        )
        return {
            "status": "verified",
            "textbook_example_id": example_id,
            "component_id": component_id,
            "dryrun_component_dir": str(dryrun_root / kwargs["skill_id"] / "components" / component_id),
            "force_regenerate": bool(kwargs.get("force_regenerate")),
            "cache_hit": False,
            "skip_reason": None,
            "generation_run_id": run_id,
            "generation_started_at": "2026-06-25T00:00:00",
            "generation_finished_at": "2026-06-25T00:00:01",
            "old_artifact_hash": None,
            "new_artifact_hash": run_id,
            "old_generate_mtime": None,
            "new_generate_mtime": 1.0,
            "model_generation_invoked": True,
        }

    monkeypatch.setattr(
        "core.gencode.services.admin_gencode_action_service.run_admin_v3_dryrun_for_example",
        _fake_example,
    )

    result = run_admin_v3_dryrun_for_skill(
        memory_conn,
        SKILL_ID,
        dryrun_base_dir=str(dryrun_root),
        mode="regenerate",
        force=True,
    )

    assert result["total_examples"] == 3
    assert result["processed_count"] == 3
    assert result["success_count"] == 3
    assert result["failed_count"] == 0
    assert set(calls) == {4544, 4553, 4666}
    assert all(row["force_regenerate"] is True for row in result["results"])
    assert all(row["cache_hit"] is False for row in result["results"])
    assert all(row["model_generation_invoked"] is True for row in result["results"])


def test_force_regenerate_single_failure_does_not_reuse_old_verified_success(
    memory_conn,
    dryrun_root,
    monkeypatch,
):
    for example_id in (4544, 4553):
        save_tracker_record(
            memory_conn,
            textbook_example_id=example_id,
            skill_id=SKILL_ID,
            gencode_status="verified",
            induced_spec_payload={
                "generation_run_id": f"old-{example_id}",
                "new_artifact_hash": f"old-hash-{example_id}",
            },
        )

    def _fake_example(**kwargs):
        example_id = int(kwargs["textbook_example_id"])
        if example_id == 4544:
            return {
                "status": "failed",
                "textbook_example_id": example_id,
                "component_id": f"src_{example_id}",
                "force_regenerate": True,
                "cache_hit": False,
                "skip_reason": None,
                "generation_run_id": "new-failed-run",
                "generation_started_at": "2026-06-25T00:00:00",
                "generation_finished_at": "2026-06-25T00:00:01",
                "old_artifact_hash": "old-hash-4544",
                "new_artifact_hash": "old-hash-4544",
                "model_generation_invoked": True,
                "error_code": "COMPONENT_GENERATION_FAILED",
            }
        save_tracker_record(
            kwargs["conn"],
            textbook_example_id=example_id,
            skill_id=kwargs["skill_id"],
            gencode_status="verified",
            induced_spec_payload={"generation_run_id": "new-success-run"},
        )
        return {
            "status": "verified",
            "textbook_example_id": example_id,
            "component_id": f"src_{example_id}",
            "force_regenerate": True,
            "cache_hit": False,
            "skip_reason": None,
            "generation_run_id": "new-success-run",
            "generation_started_at": "2026-06-25T00:00:00",
            "generation_finished_at": "2026-06-25T00:00:01",
            "old_artifact_hash": "old-hash-4553",
            "new_artifact_hash": "new-hash-4553",
            "model_generation_invoked": True,
        }

    monkeypatch.setattr(
        "core.gencode.services.admin_gencode_action_service.run_admin_v3_dryrun_for_example",
        _fake_example,
    )

    result = run_admin_v3_dryrun_for_skill(
        memory_conn,
        SKILL_ID,
        dryrun_base_dir=str(dryrun_root),
        mode="regenerate",
        force=True,
    )

    assert result["success"] is False
    assert result["failed_count"] == 1
    assert result["success_count"] == 1
    failed = [row for row in result["results"] if row["status"] == "failed"]
    assert failed[0]["generation_run_id"] == "new-failed-run"
    assert failed[0]["cache_hit"] is False
    assert failed[0]["model_generation_invoked"] is True


def test_batch_dryrun_continues_after_single_failure(memory_conn, dryrun_root, monkeypatch):
    original = run_admin_v3_dryrun_for_example

    def _flaky(**kwargs):
        if kwargs["textbook_example_id"] == 4544:
            raise RuntimeError("dryrun boom")
        return original(**kwargs)

    monkeypatch.setattr(
        "core.gencode.services.admin_gencode_action_service.run_admin_v3_dryrun_for_example",
        lambda **kwargs: _flaky(**kwargs),
    )

    result = run_admin_v3_dryrun_for_skill(
        memory_conn,
        SKILL_ID,
        dryrun_base_dir=str(dryrun_root),
        seed=42,
    )
    assert result["success"] is False
    assert result["failed_count"] == 1
    assert result["success_count"] == 1
