"""Math 2 Unit 9 original-question practice with a cross-question dependency (隨堂練習7 承例題6).

* 隨堂練習7 is served with 例題6's ten data points prepended, its own stem verbatim, and none of 例題6's option figures;
* it has no verified answer, so the submit is ungraded self-study and leaves no record;
* without 例題6 the row is never served (rotation skips it, a direct request is refused);
* rows without a dependency are served exactly as stored.

Runs on the suite's isolated database; the formal DB is only opened read-only to copy the rows.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "instance" / "kumon_math.db"
pytestmark = pytest.mark.skipif(not PROD.exists(), reason="formal database not present")

CHAPTER = ("general", "數學2", "單元9 二維數據分析")
SKILLS = ("gh_ScatterPlot", "gh_CorrelationCoefficient", "gh_LeastSquaresMethodAndRegressionLine")
CORR = "gh_CorrelationCoefficient"
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
    _copy_rows(src, dst, "textbook_examples", "source_curriculum=? and source_volume=? and source_chapter=?", CHAPTER)
    dst.commit()
    ids = {desc.split(" [")[0]: (rid, text) for rid, desc, text in dst.execute(
        "select id, source_description, problem_text from textbook_examples where source_curriculum=? and source_volume=? "
        "and source_chapter=?", CHAPTER)}
    src.close()
    dst.close()
    if "隨堂練習7" not in ids:
        pytest.skip("Unit 9 not imported")
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = "1"
            sess["_fresh"] = True
        yield client, target, ids


def _next(client, skill: str, **extra):
    query = "&".join(f"{k}={v}" for k, v in {"skill": skill, "level": 1, **extra}.items())
    res = client.get(f"/get_next_question?{query}")
    return res.status_code, res.get_json()


def _stored(uid: str) -> dict:
    from core.practice_question_store import _STORE

    return next(rows[uid] for rows in _STORE.values() if uid in rows)


def _counts(copy: Path) -> dict:
    con = sqlite3.connect(copy)
    try:
        return {t: con.execute(f"select count(*) from {t}").fetchone()[0]
                for t in ("practice_attempts", "adaptive_learning_logs", "progress", "mistake_notebook_entries")}
    finally:
        con.close()


def test_practice7_is_served_with_example6_data_and_its_own_stem(client_and_db):
    client, _, ids = client_and_db
    rid, stem = ids["隨堂練習7"]
    status, q = _next(client, CORR, textbook_example_id=rid)
    assert status == 200 and q["textbook_example_id"] == rid and q["route_mode"] == "textbook_example"
    text = q["question_text"]
    assert text.startswith("【例題6的資料】") and text.endswith(stem)
    assert "\\begin{array}" in text and "24.5" in text and "173" in text
    assert "迴歸" not in text and "①" not in text  # 例題6's sub-questions and option figures stay out
    assert q.get("image_assets") == [] and "source_dependency" not in q["metadata"]  # provenance stays server-side
    dep = _stored(q["question_uid"])["metadata"]["source_dependency"]
    assert dep["example_title"] == "例題6" and dep["example_id"] == ids["例題6"][0] and "example_table" in dep["needs"]
    assert dep["provenance"]["dependent_row_id"] == rid and len(dep["provenance"]["example_problem_text_sha256"]) == 64


def test_practice7_without_a_verified_answer_is_never_auto_graded(client_and_db):
    client, copy, ids = client_and_db
    before = _counts(copy)
    _, q = _next(client, CORR, textbook_example_id=ids["隨堂練習7"][0])
    assert q["check_mode"] == "ungraded_self_study" and q["graded"] is False
    for answer in ("變小", "變大", ""):
        body = client.post("/check_answer", json={"skill_id": CORR, "question_uid": q["question_uid"], "answer": answer}).get_json()
        assert body["correct"] is None and body["graded"] is False and NO_ANSWER_NOTICE in body["result"]
    assert _counts(copy) == before


def test_rows_without_a_dependency_are_served_as_stored(client_and_db):
    client, _, ids = client_and_db
    for title in ("例題2", "隨堂練習2", "9習題 基礎題3"):
        rid, stem = ids[title]
        status, q = _next(client, CORR, textbook_example_id=rid)
        assert status == 200 and q["question_text"] == stem
        assert "source_dependency" not in _stored(q["question_uid"])["metadata"]


def test_without_example6_the_continuing_row_is_not_served(client_and_db):
    client, copy, ids = client_and_db
    ex_id = ids["例題6"][0]
    con = sqlite3.connect(copy)
    original = con.execute("select source_description from textbook_examples where id=?", (ex_id,)).fetchone()[0]
    con.execute("update textbook_examples set source_description='例題6_moved [x]' where id=?", (ex_id,))
    con.commit()
    con.close()
    try:
        status, body = _next(client, CORR, textbook_example_id=ids["隨堂練習7"][0])
        assert status == 409 and body["error_code"] == "TEXTBOOK_EXAMPLE_NOT_STANDALONE" and body["reason"] == "example_not_found"
        served = {_next(client, CORR)[1]["textbook_example_id"] for _ in range(20)}
        assert ids["隨堂練習7"][0] not in served and len(served) > 1
    finally:
        con = sqlite3.connect(copy)
        con.execute("update textbook_examples set source_description=? where id=?", (original, ex_id))
        con.commit()
        con.close()
