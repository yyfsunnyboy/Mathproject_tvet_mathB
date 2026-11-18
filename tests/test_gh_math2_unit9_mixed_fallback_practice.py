"""Unit 9 mixed practice: DEFERRED originals stay reachable via fixed ungraded rows alongside V3 generators.

Isolation only (pytest_isolated.db). Does not publish facades or write the formal DB.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

from core import fixed_textbook_practice as FTP
from core.textbook_order_practice import pick_next_in_textbook_order, textbook_sequence

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "instance" / "kumon_math.db"
pytestmark = pytest.mark.skipif(not PROD.exists(), reason="formal database not present")

CHAPTER = ("general", "數學2", "單元9 二維數據分析")
SKILLS = (
    "gh_ScatterPlot",
    "gh_CorrelationCoefficient",
    "gh_LeastSquaresMethodAndRegressionLine",
)
DEFERRED = (12947, 12948, 12954, 12960, 12963)
VERIFIED = (
    12949, 12950, 12951, 12952, 12953, 12955, 12956, 12957, 12958, 12959,
    12961, 12962, 12964, 12965, 12966, 12967, 12968, 12969, 12970, 12971, 12972,
)
NO_ANSWER_NOTICE = "本題目前沒有經驗證的標準答案"


def _copy_rows(src, dst, table: str, where: str, args: tuple) -> None:
    cols = [r[1] for r in src.execute(f"pragma table_info({table})")]
    marks = ",".join("?" * len(cols))
    for row in src.execute(f"select {','.join(cols)} from {table} where {where}", args).fetchall():
        dst.execute(f"insert or replace into {table} ({','.join(cols)}) values ({marks})", row)


@pytest.fixture(scope="module")
def client_and_db():
    sys.path.insert(0, str(ROOT))
    from app import app
    from models import db

    app.config["WTF_CSRF_ENABLED"] = False
    uri = app.config["SQLALCHEMY_DATABASE_URI"]
    assert "pytest_isolated.db" in uri
    target = Path(uri[len("sqlite:///"):])
    with app.app_context():
        db.create_all()
    src = sqlite3.connect(f"file:{PROD.as_posix()}?mode=ro", uri=True)
    dst = sqlite3.connect(target)
    for skill in SKILLS:
        _copy_rows(src, dst, "skills_info", "skill_id=?", (skill,))
        _copy_rows(src, dst, "skill_curriculum", "skill_id=?", (skill,))
    _copy_rows(
        src, dst, "textbook_examples",
        "source_curriculum=? and source_volume=? and source_chapter=?", CHAPTER,
    )
    dst.commit()
    src.close()
    dst.close()
    FTP._cache.update(mtime=None, entries={})
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = "1"
            sess["_fresh"] = True
        yield client, target
    FTP._cache.update(mtime=None, entries={})


def _next(client, skill: str, **extra):
    query = "&".join(f"{k}={v}" for k, v in {"skill": skill, "level": 1, **extra}.items())
    res = client.get(f"/get_next_question?{query}")
    return res.status_code, res.get_json()


def _stem(db: Path, rid: int) -> tuple[str, str, list]:
    import json

    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    try:
        row = con.execute(
            "select skill_id, problem_text, notes from textbook_examples where id=?", (rid,)
        ).fetchone()
    finally:
        con.close()
    notes = json.loads(row["notes"] or "{}") if (row["notes"] or "").strip().startswith("{") else {}
    return row["skill_id"], row["problem_text"] or "", notes.get("image_assets") or []


def _counts(db: Path) -> dict[str, int]:
    con = sqlite3.connect(db)
    try:
        tables = ("practice_attempts", "adaptive_learning_logs", "progress", "mistake_notebook_entries")
        return {t: con.execute(f"select count(*) from {t}").fetchone()[0] for t in tables}
    finally:
        con.close()


def test_five_deferred_rows_are_registered_ungraded_with_matching_stem_hash():
    entries = FTP.load_entries()
    prod = sqlite3.connect(f"file:{PROD.as_posix()}?mode=ro", uri=True)
    try:
        for rid in DEFERRED:
            entry = entries[rid]
            stem = prod.execute("select problem_text from textbook_examples where id=?", (rid,)).fetchone()[0]
            assert entry["mode"] == "ungraded" and entry["skill_id"] in SKILLS
            assert entry["problem_text_sha256"] == FTP.stem_sha256(stem)
    finally:
        prod.close()


def test_mixed_sequence_interleaves_verified_generators_and_deferred_originals(client_and_db):
    client, _db = client_and_db
    from models import TextbookExample

    with client.application.app_context():
        for skill in SKILLS:
            rows = TextbookExample.query.filter_by(skill_id=skill).all()
            generator_keys = {f"src_{r.id}" for r in rows if r.id in VERIFIED}
            seq = textbook_sequence(rows, generator_keys)
            deferred_here = [r.id for r in rows if r.id in DEFERRED]
            verified_here = [r.id for r in rows if r.id in VERIFIED]
            assert {item["row"].id for item in seq} == set(deferred_here) | set(verified_here)
            assert {item["row"].id for item in seq if item["kind"] == "fixed"} == set(deferred_here)
            assert {item["row"].id for item in seq if item["kind"] == "dynamic"} == set(verified_here)
            if not deferred_here:
                continue
            first_deferred = next(item["row"].id for item in seq if item["kind"] == "fixed")
            last = None
            for _ in range(len(seq) + 2):
                pick = pick_next_in_textbook_order(rows, last_served_id=last, generator_keys=generator_keys)
                assert pick is not None
                last = pick["row"].id
                if last == first_deferred:
                    assert pick["kind"] == "fixed"
                    break
            else:
                raise AssertionError(f"{skill}: deferred row never selected")


@pytest.mark.parametrize("rid", DEFERRED)
def test_deferred_original_served_intact_ungraded_and_leaves_no_record(client_and_db, rid):
    client, db = client_and_db
    skill, stem, assets = _stem(db, rid)
    before = _counts(db)
    status, q = _next(client, skill, mode="type_rotation", textbook_example_id=rid)
    assert status == 200, q
    assert q["textbook_example_id"] == rid
    assert q["question_source"] == "db_textbook_example"
    assert q["fixed_textbook_practice"] == "ungraded"
    assert q["check_mode"] == "ungraded_self_study" and q["graded"] is False
    assert q["question_text"] == stem
    assert len(q.get("image_assets") or []) == len(assets) >= 1
    if rid == 12947:
        assert (q.get("answer_input_type") or q.get("answer_type")) == "handwriting"
    if rid == 12963:
        assert "散布圖" in stem and ("3.8" in stem and "66.4" in stem)
    if rid == 12960:
        assert any(token in stem for token in ("−1.1", "-1.1", "(1)", "(5)"))
    submit = client.post(
        "/check_answer",
        json={"skill_id": skill, "question_uid": q["question_uid"], "student_answer": "測試"},
    )
    body = submit.get_json()
    assert submit.status_code == 200
    assert body.get("graded") is False and body.get("correct") is None
    assert NO_ANSWER_NOTICE in (body.get("result") or "") or "不自動判定" in (body.get("result") or "")
    assert _counts(db) == before


def test_verified_ids_are_not_registered_as_fixed_originals():
    entries = FTP.load_entries()
    for rid in VERIFIED:
        assert rid not in entries


def test_practice7_dependency_still_resolves_under_mixed_registration(client_and_db):
    client, _db = client_and_db
    status, q = _next(client, "gh_CorrelationCoefficient", mode="type_rotation", textbook_example_id=12967)
    assert status == 200, q
    assert q["question_text"].startswith("【例題6的資料】")
    assert q["question_text"].endswith("試問x與y的相關係數會變大還是變小？")
    assert q["check_mode"] == "ungraded_self_study"
