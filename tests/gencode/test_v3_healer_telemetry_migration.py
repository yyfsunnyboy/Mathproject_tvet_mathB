# -*- coding: utf-8 -*-
"""Add-only migration of gencode_v3_healer_telemetry_events; legacy healer_events is preserved."""

from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path

import pytest
from sqlalchemy import create_engine

import models
import scripts.migrate_v3_healer_telemetry_add_table as mig
from core.gencode.schema.gencode_v3_healer_telemetry_inspection import TABLE_NAME as TELEMETRY_TABLE

LEGACY_TABLES = (
    "healer_events",
    "experiment_runs",
    "ablation_settings",
    "ablation_summary",
    "execution_samples",
    "evaluation_items",
    "experiment_log",
)


def _startup_schema(path: Path) -> None:
    from core.models.prompt_template import PromptTemplate  # noqa: F401  (registered like app startup)

    engine = create_engine(f"sqlite:///{path.as_posix()}")
    try:
        models.init_db(engine)
        models.db.metadata.create_all(engine)
    finally:
        engine.dispose()


@pytest.fixture
def legacy_db(tmp_path, monkeypatch):
    """Pre-telemetry DB shape: legacy tables with data, no telemetry table."""
    monkeypatch.setattr(mig, "ROOT", tmp_path / "project_root_sentinel")
    db_path = tmp_path / "target.db"
    _startup_schema(db_path)
    conn = sqlite3.connect(str(db_path))
    conn.execute(f"DROP TABLE {TELEMETRY_TABLE}")
    conn.execute("INSERT INTO users (username, password_hash) VALUES ('keep_me', 'x')")
    run_cols = {
        r[1]: (1 if "INT" in str(r[2]).upper() or "FLOAT" in str(r[2]).upper() else "x")
        for r in conn.execute("PRAGMA table_info(experiment_runs)")
        if r[3] and r[4] is None
    }
    run_cols["run_id"] = "r1"
    conn.execute(
        f"INSERT INTO experiment_runs ({', '.join(run_cols)}) VALUES ({', '.join('?' for _ in run_cols)})",
        list(run_cols.values()),
    )
    conn.execute(
        "INSERT INTO healer_events VALUES ('e1', 'r1', 'Regex_Healer', 'fix_latex', 'a$', 'a', 1, 3, '2026-01-02 03:04:05')"
    )
    conn.commit()
    conn.close()
    return db_path


def test_orm_keeps_legacy_healer_events_model():
    assert hasattr(models, "HealerEvent")
    for table in LEGACY_TABLES[:2] + ("evaluation_items",):
        assert table in models.db.metadata.tables


def test_migration_statements_are_add_only():
    statements = mig.migration_statements()
    assert len(statements) == 4
    sql = "\n".join(statements).upper()
    for token in ("DROP ", "ALTER ", "DELETE ", "INSERT ", "HEALER_EVENTS"):
        assert token not in sql.replace("HEALER_TELEMETRY_EVENTS", "")


def test_guard_rejects_non_add_only_ddl(monkeypatch):
    monkeypatch.setattr(
        mig, "load_healer_telemetry_ddl",
        lambda: "CREATE TABLE IF NOT EXISTS gencode_v3_healer_telemetry_events (id INTEGER);\nDROP TABLE healer_events;\n",
    )
    with pytest.raises(RuntimeError):
        mig.migration_statements()


def test_backup_migrate_compare_preserves_everything(legacy_db, tmp_path):
    manifest = mig.backup_db(legacy_db, tmp_path / "archive")
    assert manifest["backup_integrity_check"] == "ok"
    assert manifest["snapshot_matches_source_content"] is True
    for meta in manifest["files"].values():
        assert mig._sha256_file(Path(meta["path"])) == meta["sha256"]

    before = mig.audit_db(legacy_db)
    dry = mig.migrate_db(legacy_db, apply=False)
    assert dry["telemetry_table_present"] is False
    assert mig.audit_db(legacy_db)["tables"] == before["tables"]

    result = mig.migrate_db(legacy_db, apply=True)
    assert result["integrity_check"] == "ok"
    assert result["foreign_key_check_violations"] == 0
    assert result["telemetry_schema"]["ok"] is True

    after_first = mig.audit_db(legacy_db)
    diff = mig.compare_audits(before, after_first)
    assert diff["added_tables"] == [TELEMETRY_TABLE]
    assert diff["removed_tables"] == []
    assert diff["changed_retained_tables"] == []
    assert diff["schema_objects_removed"] == [] and diff["schema_objects_changed"] == []
    assert diff["sqlite_sequence_identical"] is True
    assert diff["only_expected_changes"] is True
    assert after_first["tables"]["healer_events"] == before["tables"]["healer_events"]

    again = mig.migrate_db(legacy_db, apply=True)
    assert again["telemetry_table_existed_before"] is True
    rerun = mig.compare_audits(after_first, mig.audit_db(legacy_db))
    assert rerun["added_tables"] == [] and rerun["changed_retained_tables"] == []
    assert rerun["schema_objects_added"] == [] and rerun["only_expected_changes"] is True


def test_unexpected_difference_rolls_back(legacy_db, monkeypatch, tmp_path):
    real_compare = mig.compare_audits
    monkeypatch.setattr(mig, "compare_audits", lambda a, b: {**real_compare(a, b), "only_expected_changes": False})
    before = mig.audit_db(legacy_db)
    result = mig.migrate_db(legacy_db, apply=True, evidence_dir=tmp_path / "evidence")
    assert result["applied"] is False and result["reason"] == "unexpected_difference_rolled_back"
    after = mig.audit_db(legacy_db)
    assert after["tables"] == before["tables"] and after["schema_objects"] == before["schema_objects"]
    assert (tmp_path / "evidence" / "migration_compare.json").exists()


def test_migration_does_not_touch_existing_telemetry_rows(legacy_db):
    mig.migrate_db(legacy_db, apply=True)
    conn = sqlite3.connect(str(legacy_db))
    conn.execute(
        f"INSERT INTO {TELEMETRY_TABLE} (event_key, event_type, attempt_id, generation_run_id, component_id, "
        "skill_id, mode, environment, data_origin, outcome, created_at, source_version) "
        "VALUES ('k1', 'attempt', 'a', 'r', 'c', 's', 'shadow', 'test', 'synthetic', 'UNCHANGED', 'now', 'v')"
    )
    conn.commit()
    conn.close()
    before = mig.audit_db(legacy_db)
    mig.migrate_db(legacy_db, apply=True)
    assert mig.compare_audits(before, mig.audit_db(legacy_db))["changed_retained_tables"] == []


def test_telemetry_works_on_migrated_db(legacy_db):
    import core.gencode.v3_healer_telemetry as telemetry
    from core.gencode.v3_healer_adapter import MODE_REPAIR

    spec = importlib.util.spec_from_file_location(
        "_healer_telemetry_helpers", Path(__file__).with_name("test_v3_healer_telemetry.py")
    )
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)

    mig.migrate_db(legacy_db, apply=True)
    conn = sqlite3.connect(str(legacy_db))
    try:
        result = helpers._heal(helpers.TIER_A_B_BROKEN, MODE_REPAIR)
        for _ in range(2):
            telemetry.record_attempt_safely(
                conn, result, generation_run_id="run-db", context={"environment": "test", "data_origin": "synthetic"}
            )
            telemetry.record_gate_safely(conn, result, passed=True)
        assert not result.telemetry.get("errors")
        totals = telemetry.build_dashboard_payload(conn)["metrics"]["totals"]
        assert totals["invocations"] == 1 and totals["verified_rescues"] == 1
        with pytest.raises(sqlite3.DatabaseError):
            conn.execute(f"UPDATE {TELEMETRY_TABLE} SET outcome='x'")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                f"INSERT INTO {TELEMETRY_TABLE} (event_key, event_type, attempt_id, generation_run_id, component_id, "
                "skill_id, mode, environment, data_origin, outcome, created_at, source_version) "
                "VALUES ('bad', 'attempt', 'a', 'r', 'c', 's', 'yolo', 'test', 'synthetic', 'x', 'now', 'v')"
            )
        assert conn.execute("SELECT COUNT(*) FROM healer_events").fetchone()[0] == 1
    finally:
        conn.close()


def test_startup_init_keeps_legacy_tables_and_adds_telemetry(legacy_db):
    for _ in range(2):
        _startup_schema(legacy_db)
    conn = sqlite3.connect(str(legacy_db))
    try:
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert set(LEGACY_TABLES) <= tables and TELEMETRY_TABLE in tables
        assert conn.execute("SELECT COUNT(*) FROM healer_events").fetchone()[0] == 1
    finally:
        conn.close()


def test_formal_db_refused_without_approval(legacy_db, monkeypatch):
    monkeypatch.setattr(mig, "FORMAL_DB", legacy_db.resolve())
    with pytest.raises(SystemExit):
        mig.migrate_db(legacy_db, apply=True)
    assert TELEMETRY_TABLE not in {
        r[0] for r in sqlite3.connect(str(legacy_db)).execute("SELECT name FROM sqlite_master WHERE type='table'")
    }


def test_backup_refuses_directory_inside_project(legacy_db, monkeypatch, tmp_path):
    monkeypatch.setattr(mig, "ROOT", tmp_path)
    with pytest.raises(SystemExit):
        mig.backup_db(legacy_db, tmp_path / "inside")
