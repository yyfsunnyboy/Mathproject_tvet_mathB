# -*- coding: utf-8 -*-
"""Idempotent migration: create student_problem_type_mastery if missing."""
from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "instance" / "kumon_math.db"

DDL = """
CREATE TABLE IF NOT EXISTS student_problem_type_mastery (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    skill_id TEXT NOT NULL,
    problem_type_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'NOT_STARTED',
    consecutive_wrong INTEGER NOT NULL DEFAULT 0,
    needs_independent_verify BOOLEAN NOT NULL DEFAULT 0,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    last_attempt_at DATETIME,
    last_attempt_id INTEGER,
    last_question_uid TEXT,
    mastered_at DATETIME,
    mastery_attempt_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE(user_id, skill_id, problem_type_id)
)
"""


def main() -> None:
    con = sqlite3.connect(str(DB))
    try:
        con.execute(DDL)
        con.execute(
            "CREATE INDEX IF NOT EXISTS idx_sptm_user_skill "
            "ON student_problem_type_mastery (user_id, skill_id)"
        )
        con.execute(
            "CREATE INDEX IF NOT EXISTS idx_sptm_user_skill_status "
            "ON student_problem_type_mastery (user_id, skill_id, status)"
        )
        con.commit()
        exists = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='student_problem_type_mastery'"
        ).fetchone()
        print({"ok": bool(exists), "db": str(DB)})
    finally:
        con.close()


if __name__ == "__main__":
    main()
