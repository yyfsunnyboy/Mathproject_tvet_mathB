# -*- coding: utf-8 -*-
"""Startup init must not rewrite skill_family_bridge (IDs, timestamps, sqlite_sequence)."""

from __future__ import annotations

import sqlite3

import pytest
from sqlalchemy import create_engine

import models

CATALOG = [
    {"skill_id": "s1", "family_id": "F1", "skill_name": "S1", "family_name": "Fam1", "theme": "t", "notes": "", "subskill_nodes": "a;b"},
    {"skill_id": "s1", "family_id": "F2", "skill_name": "S1", "family_name": "Fam2", "theme": "t", "notes": "", "subskill_nodes": "c"},
    {"skill_id": "s2", "family_id": "F1", "skill_name": "S2", "family_name": "Fam1", "theme": "t", "notes": "", "subskill_nodes": "d"},
    {"skill_id": "ghost", "family_id": "F9", "skill_name": "G", "family_name": "Fam9", "theme": "t", "notes": "", "subskill_nodes": "z"},
]


class _Db:
    def __init__(self, path, catalog):
        self.path = path
        self.catalog = catalog

    def as_posix(self):
        return self.path.as_posix()

    def __str__(self):
        return str(self.path)


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    catalog = [dict(r) for r in CATALOG]
    monkeypatch.setattr(models, "_read_bridge_catalog_rows", lambda: [dict(r) for r in catalog])
    path = tmp_path / "bridge.db"
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    models.init_db(engine)
    engine.dispose()
    conn = sqlite3.connect(str(path))
    for sid in ("s1", "s2"):
        conn.execute(
            "INSERT INTO skills_info (skill_id, skill_en_name, skill_ch_name, description, gemini_prompt) "
            "VALUES (?, ?, ?, 'd', 'p')",
            (sid, sid.upper(), f"技能{sid}"),
        )
    conn.commit()
    conn.close()
    return _Db(path, catalog)


def _startup(path):
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    try:
        models.init_db(engine)
        models.db.metadata.create_all(engine)
    finally:
        engine.dispose()


def _sync(path, *, force=False):
    conn = sqlite3.connect(str(path))
    try:
        return models._sync_skill_family_bridge(conn, force=force)
    finally:
        conn.close()


def _snapshot(path):
    conn = sqlite3.connect(str(path))
    try:
        rows = conn.execute("SELECT * FROM skill_family_bridge ORDER BY bridge_id").fetchall()
        seq = conn.execute("SELECT seq FROM sqlite_sequence WHERE name='skill_family_bridge'").fetchone()
        return rows, seq
    finally:
        conn.close()


def test_empty_table_is_seeded_then_repeated_startup_is_a_noop(db_path):
    _startup(db_path)
    rows, seq = _snapshot(db_path)
    assert {(r[1], r[2]) for r in rows} == {("s1", "F1"), ("s1", "F2"), ("s2", "F1")}

    for _ in range(3):
        _startup(db_path)
    assert _snapshot(db_path) == (rows, seq)
    assert _sync(db_path)["status"] == "unchanged"


def test_missing_catalog_row_is_inserted_without_touching_existing(db_path):
    _startup(db_path)
    rows, _seq = _snapshot(db_path)
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "INSERT INTO skills_info (skill_id, skill_en_name, skill_ch_name, description, gemini_prompt) "
        "VALUES ('ghost', 'G', 'g', 'd', 'p')"
    )
    conn.commit()
    conn.close()

    result = _sync(db_path)
    assert result["status"] == "inserted_missing" and result["missing"] == [("ghost", "F9")]
    after, _ = _snapshot(db_path)
    assert after[: len(rows)] == rows
    assert len(after) == len(rows) + 1


@pytest.mark.parametrize("mutation", ["changed", "stale"])
def test_mismatch_fails_closed_without_writes(db_path, mutation):
    _startup(db_path)
    if mutation == "changed":
        conn = sqlite3.connect(str(db_path))
        conn.execute("UPDATE skill_family_bridge SET notes='teacher edit' WHERE skill_id='s1' AND family_id='F1'")
        conn.commit()
        conn.close()
    else:
        db_path.catalog.pop(0)
    db_path.catalog.append(
        {"skill_id": "s2", "family_id": "F3", "skill_name": "S2", "family_name": "Fam3", "theme": "t", "notes": "", "subskill_nodes": "e"}
    )
    before = _snapshot(db_path)

    result = _sync(db_path)
    assert result["status"] == "fail_closed_mismatch"
    assert result["missing"] == [("s2", "F3")]
    assert result[mutation] == [("s1", "F1")]
    _startup(db_path)
    assert _snapshot(db_path) == before


def test_explicit_admin_seed_still_reseeds(db_path):
    _startup(db_path)
    conn = sqlite3.connect(str(db_path))
    conn.execute("UPDATE skill_family_bridge SET notes='teacher edit' WHERE skill_id='s1' AND family_id='F1'")
    conn.commit()
    conn.close()

    assert _sync(db_path, force=True)["status"] == "force_reseeded"
    rows, _ = _snapshot(db_path)
    assert len(rows) == 3
    assert all(r[9] == "" for r in rows)
