# -*- coding: utf-8 -*-
"""Tests for idempotent gencode_component_tracker initialization."""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

from core.gencode.schema.gencode_component_tracker_inspection import (
    ensure_gencode_component_tracker_table,
    tracker_table_exists,
)


def test_ensure_tracker_table_creates_on_empty_db():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "empty.db"
        conn = sqlite3.connect(str(db_path))
        try:
            assert tracker_table_exists(conn) is False
            created = ensure_gencode_component_tracker_table(conn)
            assert created is True
            assert tracker_table_exists(conn) is True
        finally:
            conn.close()


def test_ensure_tracker_table_is_idempotent():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "repeat.db"
        conn = sqlite3.connect(str(db_path))
        try:
            ensure_gencode_component_tracker_table(conn)
            conn.execute(
                """
                INSERT INTO gencode_component_tracker (
                    textbook_example_id, skill_id, component_id, gencode_status
                ) VALUES (101, 'skill_a', 'src_101', 'verified')
                """
            )
            conn.commit()
            created_again = ensure_gencode_component_tracker_table(conn)
            assert created_again is False
            count = conn.execute(
                "SELECT COUNT(*) FROM gencode_component_tracker"
            ).fetchone()[0]
            assert count == 1
        finally:
            conn.close()
