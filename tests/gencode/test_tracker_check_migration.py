# -*- coding: utf-8 -*-
"""
Tests for migration 20260629_0001:
  - needs_human_review is accepted after migration
  - illegal statuses remain rejected
  - migration is idempotent (safe to run twice)
  - existing data survives the rebuild
"""

from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MIGRATION_PATH = (
    PROJECT_ROOT
    / "migrations"
    / "versions"
    / "20260629_0001_add_needs_human_review_to_tracker_check.py"
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _load_migration():
    """Dynamically import the migration module without installing it."""
    spec = importlib.util.spec_from_file_location("migration_20260629", MIGRATION_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_db_with_old_check() -> sqlite3.Connection:
    """In-memory SQLite with the OLD CHECK (without needs_human_review)."""
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE gencode_component_tracker (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            textbook_example_id     INTEGER NOT NULL,
            skill_id                TEXT    NOT NULL,
            component_id            TEXT    NOT NULL,
            gencode_status          TEXT    NOT NULL DEFAULT 'pending',
            induced_spec_payload    TEXT,
            gencode_error_log       TEXT,
            created_at              TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
            updated_at              TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
            CONSTRAINT uq_gencode_tracker_example_id
                UNIQUE (textbook_example_id),
            CONSTRAINT uq_gencode_tracker_namespace_pool
                UNIQUE (skill_id, component_id),
            CONSTRAINT ck_gencode_status_values
                CHECK (gencode_status IN (
                    'pending','usable','generating','draft_written',
                    'smoke_passed','verified','failed'
                ))
        );
        """
    )
    return conn


def _make_db_with_new_check() -> sqlite3.Connection:
    """In-memory SQLite with the NEW CHECK (includes needs_human_review)."""
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE gencode_component_tracker (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            textbook_example_id     INTEGER NOT NULL,
            skill_id                TEXT    NOT NULL,
            component_id            TEXT    NOT NULL,
            gencode_status          TEXT    NOT NULL DEFAULT 'pending',
            induced_spec_payload    TEXT,
            gencode_error_log       TEXT,
            created_at              TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
            updated_at              TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
            CONSTRAINT uq_gencode_tracker_example_id
                UNIQUE (textbook_example_id),
            CONSTRAINT uq_gencode_tracker_namespace_pool
                UNIQUE (skill_id, component_id),
            CONSTRAINT ck_gencode_status_values
                CHECK (gencode_status IN (
                    'pending','usable','generating','draft_written',
                    'smoke_passed','verified','needs_human_review','failed'
                ))
        );
        """
    )
    return conn


def _insert_row(conn: sqlite3.Connection, ex_id: int, status: str) -> None:
    conn.execute(
        """
        INSERT INTO gencode_component_tracker
            (textbook_example_id, skill_id, component_id, gencode_status)
        VALUES (?, 'sk', ?, ?)
        """,
        (ex_id, f"src_{ex_id}", status),
    )
    conn.commit()


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestMigrationFilePresent:
    def test_migration_file_exists(self):
        assert MIGRATION_PATH.is_file(), f"migration file missing: {MIGRATION_PATH}"

    def test_migration_has_needs_human_review(self):
        text = MIGRATION_PATH.read_text(encoding="utf-8")
        assert "'needs_human_review'" in text

    def test_migration_revision_ids(self):
        mod = _load_migration()
        assert mod.revision == "20260629_0001"
        assert mod.down_revision == "20250616_0001"


class TestNeedsHumanReviewAllowed:
    """After migration, needs_human_review must be insertable."""

    def test_needs_human_review_allowed_after_migration(self):
        conn = _make_db_with_old_check()
        mod = _load_migration()
        mod.migrate(conn, verbose=False)

        # Must not raise
        _insert_row(conn, 1, "needs_human_review")
        row = conn.execute(
            "SELECT gencode_status FROM gencode_component_tracker WHERE textbook_example_id=1"
        ).fetchone()
        assert row is not None
        assert row[0] == "needs_human_review"
        conn.close()

    def test_needs_human_review_allowed_on_new_schema(self):
        """Sanity: DDL already has the status — direct insert must pass."""
        conn = _make_db_with_new_check()
        _insert_row(conn, 1, "needs_human_review")
        row = conn.execute(
            "SELECT gencode_status FROM gencode_component_tracker WHERE textbook_example_id=1"
        ).fetchone()
        assert row[0] == "needs_human_review"
        conn.close()

    def test_all_canonical_statuses_allowed_after_migration(self):
        conn = _make_db_with_old_check()
        mod = _load_migration()
        mod.migrate(conn, verbose=False)

        canonical = [
            "pending", "usable", "generating", "draft_written",
            "smoke_passed", "verified", "needs_human_review", "failed",
        ]
        for idx, status in enumerate(canonical, start=100):
            _insert_row(conn, idx, status)
        count = conn.execute(
            "SELECT COUNT(*) FROM gencode_component_tracker"
        ).fetchone()[0]
        assert count == len(canonical)
        conn.close()


class TestIllegalStatusesStillRejected:
    """Non-canonical statuses must still be rejected after migration."""

    @pytest.mark.parametrize("bad_status", [
        "random_status",
        "unsupported_domain_operation",
        "fixed_domain_violation",
        "needs_regeneration",
        "draft",        # common mis-spelling
        "human_review", # partial match
        "",             # empty string
    ])
    def test_illegal_status_rejected_after_migration(self, bad_status):
        conn = _make_db_with_old_check()
        mod = _load_migration()
        mod.migrate(conn, verbose=False)

        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO gencode_component_tracker
                    (textbook_example_id, skill_id, component_id, gencode_status)
                VALUES (99999, 'sk', 'src_99999', ?)
                """,
                (bad_status,),
            )
            conn.commit()
        conn.rollback()
        conn.close()


class TestMigrationIdempotency:
    """Running migration twice must produce identical results with no data loss."""

    def test_second_run_is_no_op(self):
        conn = _make_db_with_old_check()
        _insert_row(conn, 1, "verified")
        _insert_row(conn, 2, "failed")

        mod = _load_migration()
        result1 = mod.migrate(conn, verbose=False)
        result2 = mod.migrate(conn, verbose=False)

        assert result1["already_migrated"] is False
        assert result2["already_migrated"] is True
        # Row counts unchanged
        assert result2["rows_before"] == 2
        assert result2["rows_after"] == 2
        conn.close()

    def test_idempotent_on_already_migrated_schema(self):
        conn = _make_db_with_new_check()
        _insert_row(conn, 1, "verified")
        mod = _load_migration()
        result = mod.migrate(conn, verbose=False)

        assert result["already_migrated"] is True
        assert result["rows_before"] == 1
        conn.close()

    def test_idempotent_three_times(self):
        conn = _make_db_with_old_check()
        _insert_row(conn, 1, "verified")
        mod = _load_migration()
        for i in range(3):
            result = mod.migrate(conn, verbose=False)
            count = conn.execute(
                "SELECT COUNT(*) FROM gencode_component_tracker"
            ).fetchone()[0]
            assert count == 1, f"row lost on run {i+1}"
        conn.close()


class TestDataPreservation:
    """All existing rows must survive the table rebuild unchanged."""

    def test_all_rows_preserved_with_correct_values(self):
        conn = _make_db_with_old_check()
        seed_rows = [
            (1, "sk_a", "src_1", "verified",        '{"ok":true}', None),
            (2, "sk_a", "src_2", "failed",           '{"err":"x"}', "some error"),
            (3, "sk_b", "src_3", "draft_written",    None,          None),
            (4, "sk_b", "src_4", "smoke_passed",     None,          None),
            (5, "sk_c", "src_5", "pending",          None,          None),
        ]
        for row in seed_rows:
            conn.execute(
                """
                INSERT INTO gencode_component_tracker
                    (textbook_example_id, skill_id, component_id, gencode_status,
                     induced_spec_payload, gencode_error_log)
                VALUES (?,?,?,?,?,?)
                """,
                row,
            )
        conn.commit()

        mod = _load_migration()
        result = mod.migrate(conn, verbose=False)

        assert result["rows_before"] == len(seed_rows)
        assert result["rows_after"] == len(seed_rows)

        for ex_id, skill_id, comp_id, status, payload, error_log in seed_rows:
            row = conn.execute(
                "SELECT skill_id, component_id, gencode_status, induced_spec_payload, gencode_error_log "
                "FROM gencode_component_tracker WHERE textbook_example_id=?",
                (ex_id,),
            ).fetchone()
            assert row is not None, f"row {ex_id} missing after migration"
            assert row[0] == skill_id
            assert row[1] == comp_id
            assert row[2] == status
            assert row[3] == payload
            assert row[4] == error_log
        conn.close()

    def test_autoincrement_continues_after_migration(self):
        """New inserts after migration get higher ids than pre-migration rows."""
        conn = _make_db_with_old_check()
        _insert_row(conn, 1, "verified")
        _insert_row(conn, 2, "failed")
        max_before = conn.execute(
            "SELECT MAX(id) FROM gencode_component_tracker"
        ).fetchone()[0]

        mod = _load_migration()
        mod.migrate(conn, verbose=False)

        # Insert a new row (textbook_example_id must be unique)
        conn.execute(
            """
            INSERT INTO gencode_component_tracker
                (textbook_example_id, skill_id, component_id, gencode_status)
            VALUES (999, 'sk', 'src_999', 'needs_human_review')
            """
        )
        conn.commit()
        new_id = conn.execute(
            "SELECT id FROM gencode_component_tracker WHERE textbook_example_id=999"
        ).fetchone()[0]
        assert new_id > max_before, (
            f"AUTOINCREMENT regression: new id {new_id} <= pre-migration max {max_before}"
        )
        conn.close()

    def test_unique_constraints_preserved(self):
        """UNIQUE constraints must still be enforced after migration."""
        conn = _make_db_with_old_check()
        mod = _load_migration()
        mod.migrate(conn, verbose=False)

        _insert_row(conn, 1, "verified")
        # Duplicate textbook_example_id
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO gencode_component_tracker
                    (textbook_example_id, skill_id, component_id, gencode_status)
                VALUES (1, 'sk_other', 'src_different', 'pending')
                """
            )
            conn.commit()
        conn.rollback()
        conn.close()


class TestMigrationReturnContract:
    """The migrate() return dict must have the expected keys and values."""

    def test_return_keys_present(self):
        conn = _make_db_with_old_check()
        mod = _load_migration()
        result = mod.migrate(conn, verbose=False)
        for key in ("already_migrated", "rows_before", "rows_after",
                    "status_dist_before", "status_dist_after",
                    "create_sql_before", "create_sql_after"):
            assert key in result, f"missing key: {key}"
        conn.close()

    def test_create_sql_after_contains_needs_human_review(self):
        conn = _make_db_with_old_check()
        mod = _load_migration()
        result = mod.migrate(conn, verbose=False)
        assert "'needs_human_review'" in result["create_sql_after"]
        conn.close()

    def test_create_sql_before_lacks_needs_human_review(self):
        conn = _make_db_with_old_check()
        mod = _load_migration()
        result = mod.migrate(conn, verbose=False)
        assert "'needs_human_review'" not in result["create_sql_before"]
        conn.close()

    def test_already_migrated_true_when_skipped(self):
        conn = _make_db_with_new_check()
        mod = _load_migration()
        result = mod.migrate(conn, verbose=False)
        assert result["already_migrated"] is True
        conn.close()
