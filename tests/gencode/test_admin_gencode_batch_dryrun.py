# -*- coding: utf-8 -*-
"""Tests for skill-level V3 batch dryrun service."""

from __future__ import annotations

import shutil
import sqlite3
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest

from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.services.admin_gencode_action_service import (
    run_admin_v3_dryrun_for_example,
    run_admin_v3_dryrun_for_skill,
)

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
            skill_id TEXT NOT NULL
        )
        """
    )
    apply_tracker_ddl(conn)
    for example_id in (4544, 4553):
        conn.execute(
            "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
            (example_id, SKILL_ID),
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
    assert any(row["status"] == "skipped_verified" for row in skipped["results"])

    forced = run_admin_v3_dryrun_for_skill(
        memory_conn,
        SKILL_ID,
        dryrun_base_dir=str(dryrun_root),
        seed=42,
        force=True,
    )
    assert forced["skipped_verified_count"] == 0


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
