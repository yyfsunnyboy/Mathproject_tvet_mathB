# -*- coding: utf-8 -*-
"""Legacy mistake_notebook_entries must migrate resolved_at before index creation."""

from __future__ import annotations

import sqlite3

from sqlalchemy import create_engine

import models


def _legacy_mistake_notebook_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE mistake_notebook_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            exam_image_path TEXT,
            question_data JSON,
            notes TEXT,
            skill_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        INSERT INTO mistake_notebook_entries
            (student_id, exam_image_path, question_data, notes, skill_id)
        VALUES (1, NULL, NULL, 'legacy', NULL)
        """
    )
    conn.commit()


def test_init_db_upgrades_legacy_mistake_notebook_before_indexes(tmp_path):
    path = tmp_path / "legacy_mistake.db"
    conn = sqlite3.connect(str(path))
    try:
        _legacy_mistake_notebook_schema(conn)
        cols_before = {row[1] for row in conn.execute("PRAGMA table_info(mistake_notebook_entries)")}
        assert "resolved_at" not in cols_before
    finally:
        conn.close()

    engine = create_engine(f"sqlite:///{path.as_posix()}")
    try:
        models.init_db(engine)
    finally:
        engine.dispose()

    conn = sqlite3.connect(str(path))
    try:
        cols = {row[1] for row in conn.execute("PRAGMA table_info(mistake_notebook_entries)")}
        assert "resolved_at" in cols
        assert "resolved_attempt_id" in cols
        assert "resolution_method" in cols
        indexes = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='mistake_notebook_entries'"
            )
        }
        assert "idx_mistake_notebook_active_student_created" in indexes
        count = conn.execute("SELECT COUNT(*) FROM mistake_notebook_entries").fetchone()[0]
        assert count == 1
        # Second startup must remain idempotent and not drop legacy rows.
        engine = create_engine(f"sqlite:///{path.as_posix()}")
        try:
            models.init_db(engine)
        finally:
            engine.dispose()
        assert conn.execute("SELECT COUNT(*) FROM mistake_notebook_entries").fetchone()[0] == 1
    finally:
        conn.close()
