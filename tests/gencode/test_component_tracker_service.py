# -*- coding: utf-8 -*-
"""Contract tests for gencode_component_tracker shadow-table service."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from core.gencode.services.component_tracker_service import (
    ALLOWED_GENCODE_STATUSES,
    assert_textbook_example_skill,
    derive_component_id,
    derive_component_path,
    save_tracker_record,
    update_status,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DDL_PATH = PROJECT_ROOT / "core" / "gencode" / "schema" / "gencode_component_tracker.sql"
SERVICE_PATH = PROJECT_ROOT / "core" / "gencode" / "services" / "component_tracker_service.py"
SKILL_ID = "vh_數學B1_PointSlopeForm"


@pytest.fixture
def memory_conn() -> sqlite3.Connection:
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
    ddl = DDL_PATH.read_text(encoding="utf-8")
    conn.executescript(ddl)
    yield conn
    conn.close()


def _tracker_column_names(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("PRAGMA table_info(gencode_component_tracker)").fetchall()
    return {str(row["name"]) for row in rows}


def test_save_tracker_record_success(memory_conn: sqlite3.Connection):
    memory_conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (1, SKILL_ID),
    )
    memory_conn.commit()

    record = save_tracker_record(
        memory_conn,
        textbook_example_id=1,
        skill_id=SKILL_ID,
        gencode_status="draft_written",
        induced_spec_payload={"line_type": "point_slope", "source_kind": "ex_1"},
    )

    assert record["component_id"] == "src_1"
    assert record["gencode_status"] == "draft_written"
    assert isinstance(record["induced_spec_payload"], str)
    payload = json.loads(str(record["induced_spec_payload"]))
    assert payload["line_type"] == "point_slope"
    assert "component_path" not in _tracker_column_names(memory_conn)


def test_save_tracker_record_raises_skill_id_mismatch(memory_conn: sqlite3.Connection):
    memory_conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (1, "A"),
    )
    memory_conn.commit()

    with pytest.raises(ValueError, match="skill_id_mismatch"):
        save_tracker_record(
            memory_conn,
            textbook_example_id=1,
            skill_id="B",
            gencode_status="pending",
        )


def test_save_tracker_record_raises_textbook_example_not_found(
    memory_conn: sqlite3.Connection,
):
    with pytest.raises(ValueError, match="textbook_example_not_found"):
        save_tracker_record(
            memory_conn,
            textbook_example_id=999,
            skill_id=SKILL_ID,
            gencode_status="pending",
        )


def test_save_tracker_record_rejects_invalid_gencode_status(
    memory_conn: sqlite3.Connection,
):
    memory_conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (1, SKILL_ID),
    )
    memory_conn.commit()

    with pytest.raises(ValueError, match="invalid_gencode_status"):
        save_tracker_record(
            memory_conn,
            textbook_example_id=1,
            skill_id=SKILL_ID,
            gencode_status="random_status",
        )


def test_update_status_updates_record_and_timestamp(memory_conn: sqlite3.Connection):
    memory_conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (1, SKILL_ID),
    )
    memory_conn.commit()

    saved = save_tracker_record(
        memory_conn,
        textbook_example_id=1,
        skill_id=SKILL_ID,
        gencode_status="draft_written",
    )
    updated = update_status(
        memory_conn,
        textbook_example_id=1,
        skill_id=SKILL_ID,
        gencode_status="smoke_passed",
    )

    assert updated["gencode_status"] == "smoke_passed"
    assert str(updated["updated_at"]).strip()
    assert updated["updated_at"] != saved["updated_at"] or updated["gencode_status"] != saved["gencode_status"]

    service_source = SERVICE_PATH.read_text(encoding="utf-8")
    ddl_source = DDL_PATH.read_text(encoding="utf-8")
    assert "updated_at = datetime('now', 'localtime')" in service_source
    assert "CREATE TRIGGER" not in ddl_source.upper()


def test_update_status_raises_when_tracker_missing(memory_conn: sqlite3.Connection):
    memory_conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (2, SKILL_ID),
    )
    memory_conn.commit()

    with pytest.raises(ValueError, match="tracker_record_not_found"):
        update_status(
            memory_conn,
            textbook_example_id=2,
            skill_id=SKILL_ID,
            gencode_status="smoke_passed",
        )


def test_derive_component_id_and_path_without_db_column():
    component_id = derive_component_id(1)
    assert component_id == "src_1"

    path = derive_component_path(SKILL_ID, component_id)
    assert path == f"agent_skills_v3/{SKILL_ID}/components/src_1/"


def test_allowed_statuses_match_contract():
    assert ALLOWED_GENCODE_STATUSES == {
        "pending",
        "usable",
        "generating",
        "draft_written",
        "smoke_passed",
        "verified",
        "failed",
    }


def test_assert_textbook_example_skill_is_reusable(memory_conn: sqlite3.Connection):
    memory_conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (1, SKILL_ID),
    )
    memory_conn.commit()

    assert_textbook_example_skill(
        memory_conn,
        textbook_example_id=1,
        skill_id=SKILL_ID,
    )

    with pytest.raises(ValueError, match="skill_id_mismatch"):
        assert_textbook_example_skill(
            memory_conn,
            textbook_example_id=1,
            skill_id="other_skill",
        )
