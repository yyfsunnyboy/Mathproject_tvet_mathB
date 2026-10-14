"""Rebuild only the formal mistake-notebook table in a SQLite database.

This one-purpose migration intentionally drops all existing notebook rows. It
does not issue DDL or DML against any other application table.
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


CREATE_SQL = """
CREATE TABLE mistake_notebook_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'practice',
    source_attempt_id INTEGER,
    source_question_uid TEXT,
    source_session_id TEXT,
    curriculum TEXT,
    volume TEXT,
    chapter TEXT,
    section TEXT,
    skill_id TEXT,
    problem_type_id TEXT,
    component_id TEXT,
    generator_key TEXT,
    variant TEXT,
    template_variant TEXT,
    generator_metadata JSON,
    question_text TEXT,
    question_data JSON,
    user_answer TEXT,
    expected_answer TEXT,
    exam_image_path TEXT,
    notes TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    last_retry_at DATETIME,
    resolved_at DATETIME,
    resolved_attempt_id INTEGER,
    resolution_method TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills_info (skill_id),
    FOREIGN KEY (source_attempt_id) REFERENCES practice_attempts (id),
    FOREIGN KEY (resolved_attempt_id) REFERENCES practice_attempts (id)
)
"""

INDEX_SQL = (
    "CREATE INDEX idx_mistake_notebook_active_student_created ON mistake_notebook_entries (student_id, resolved_at, created_at)",
    "CREATE INDEX idx_mistake_notebook_source_attempt ON mistake_notebook_entries (source_attempt_id)",
    "CREATE INDEX idx_mistake_notebook_source_question_uid ON mistake_notebook_entries (source_question_uid)",
    "CREATE INDEX idx_mistake_notebook_skill_id ON mistake_notebook_entries (skill_id)",
    "CREATE INDEX idx_mistake_notebook_problem_type_id ON mistake_notebook_entries (problem_type_id)",
)


def rebuild(database: Path) -> None:
    connection = sqlite3.connect(database)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        with connection:
            connection.execute("DROP TABLE mistake_notebook_entries")
            connection.execute(CREATE_SQL)
            for statement in INDEX_SQL:
                connection.execute(statement)
    finally:
        connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    args = parser.parse_args()
    rebuild(args.database)
