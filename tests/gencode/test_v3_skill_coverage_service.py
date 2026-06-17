# -*- coding: utf-8 -*-
"""Tests for V3 skill component coverage reporting."""

from __future__ import annotations

import sqlite3

from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.services.v3_skill_coverage_service import (
    build_coverage_warnings,
    get_v3_skill_component_coverage,
)

SKILL_ID = "vh_數學B1_HorizontalAndVerticalLineEquations"


def _memory_conn() -> sqlite3.Connection:
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
    for example_id in (4544, 4553, 4562, 4591):
        conn.execute(
            "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
            (example_id, SKILL_ID),
        )
    conn.commit()
    return conn


def test_coverage_marks_missing_tracker_examples():
    conn = _memory_conn()
    try:
        coverage = get_v3_skill_component_coverage(conn, SKILL_ID)
        assert coverage["total_examples"] == 4
        assert coverage["verified_count"] == 0
        assert coverage["missing_tracker_count"] == 4
        assert coverage["publish_ready"] is False
    finally:
        conn.close()


def test_publish_ready_requires_all_verified():
    conn = _memory_conn()
    try:
        for example_id in (4544, 4553, 4562):
            conn.execute(
                """
                INSERT INTO gencode_component_tracker (
                    textbook_example_id, skill_id, component_id, gencode_status
                ) VALUES (?, ?, ?, 'verified')
                """,
                (example_id, SKILL_ID, f"src_{example_id}"),
            )
        conn.execute(
            """
            INSERT INTO gencode_component_tracker (
                textbook_example_id, skill_id, component_id, gencode_status
            ) VALUES (?, ?, ?, 'draft_written')
            """,
            (4591, SKILL_ID, "src_4591"),
        )
        conn.commit()

        coverage = get_v3_skill_component_coverage(conn, SKILL_ID)
        assert coverage["verified_count"] == 3
        assert coverage["publish_ready"] is False
        warnings = build_coverage_warnings(coverage)
        assert any("3/4 verified" in item for item in warnings)
    finally:
        conn.close()
