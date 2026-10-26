"""gh_MathematicalInduction is served from its textbook examples (no generator).  Regression for the legacy textbook-example route:

* "next question" walks all 7 examples in order and never repeats the one just served, even when cookie pruning drops ``te_seq_*``;
* an example without a reference answer (proofs, figure patterns) is ungraded: no verdict, no attempt / progress record;
* an example WITH a reference answer keeps the old graded behaviour.

Runs through the Flask test client on the suite's isolated database; the formal DB is only opened read-only to copy the rows.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "instance" / "kumon_math.db"
pytestmark = pytest.mark.skipif(not PROD.exists(), reason="formal database not present")

SKILL = "gh_MathematicalInduction"
EXAMPLES = [12700, 12701, 12702, 12703, 12704, 12705, 12706]


def _copy_rows(src, dst, table: str, where: str, args: tuple) -> None:
    cols = [r[1] for r in src.execute(f"pragma table_info({table})")]
    marks = ",".join("?" * len(cols))
    for row in src.execute(f"select {','.join(cols)} from {table} where {where}", args).fetchall():
        dst.execute(f"insert or replace into {table} ({','.join(cols)}) values ({marks})", row)


@pytest.fixture(scope="module")
def client_and_db():
    """The suite's isolated database (tests/conftest.py) gets read-only copies of the rows these routes need."""
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
    for skill in (SKILL, "gh_Sequence", "gh_SineRule"):
        _copy_rows(src, dst, "skills_info", "skill_id=?", (skill,))
        _copy_rows(src, dst, "skill_curriculum", "skill_id=?", (skill,))
    _copy_rows(src, dst, "textbook_examples", "skill_id=?", (SKILL,))
    _copy_rows(src, dst, "textbook_examples", "skill_id=?", ("gh_SineRule",))
    dst.commit()
    dst.close()
    src.close()
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = "1"
            sess["_fresh"] = True
        yield client, target


def _next(client, **extra):
    query = "&".join(f"{k}={v}" for k, v in {"skill": SKILL, "level": 1, "mode": "type_rotation", **extra}.items())
    return client.get(f"/get_next_question?{query}").get_json()


def _counts(copy: Path) -> dict:
    con = sqlite3.connect(copy)
    try:
        return {t: con.execute(f"select count(*) from {t}").fetchone()[0]
                for t in ("practice_attempts", "adaptive_learning_logs", "progress", "mistake_notebook_entries", "student_abilities")}
    finally:
        con.close()


def test_next_question_walks_all_seven_examples_even_when_the_counter_is_pruned(client_and_db):
    client, _ = client_and_db
    served = []
    for _ in range(15):
        with client.session_transaction() as sess:  # what cookie pruning does: te_seq_* is not a kept practice key
            for key in [k for k in sess.keys() if str(k).startswith("te_seq_")]:
                sess.pop(key)
        served.append(_next(client)["textbook_example_id"])
    assert sorted(set(served)) == EXAMPLES
    assert all(a != b for a, b in zip(served, served[1:]))  # never the same question twice in a row
    assert served[:7] == served[7:14]  # a stable cycle through the seven


def test_rotation_restarts_cleanly_for_another_skill(client_and_db):
    client, _ = client_and_db
    first = _next(client)["textbook_example_id"]
    other = client.get("/get_next_question?skill=gh_Sequence&level=1&mode=type_rotation").get_json()
    assert other["skill_id"] == "gh_Sequence" and other.get("check_mode") != "ungraded_self_study"  # generator-backed skill untouched
    assert _next(client)["textbook_example_id"] in EXAMPLES and first in EXAMPLES


def test_examples_without_reference_answer_are_ungraded_and_leave_no_record(client_and_db):
    client, copy = client_and_db
    before = _counts(copy)
    for _ in range(7):
        question = _next(client)
        assert question["check_mode"] == "ungraded_self_study" and question["graded"] is False
        assert question["question_source"] == "db_textbook_example" and not str(question["correct_answer"]).strip()
        for answer in ("證明：略", "a_n = 4^n + 2", "6"):
            res = client.post("/check_answer", json={"skill_id": SKILL, "question_uid": question["question_uid"], "answer": answer})
            body = res.get_json()
            assert res.status_code == 200 and body["correct"] is None and body["graded"] is False
            assert "不自動判定" in body["result"]
    assert _counts(copy) == before  # no attempt, mastery or progress bookkeeping


def test_example_with_a_reference_answer_keeps_graded_behaviour(client_and_db):
    client, copy = client_and_db
    con = sqlite3.connect(copy)
    con.execute("update textbook_examples set correct_answer='5' where id=12701")
    con.commit()
    con.close()
    question = client.get(f"/get_next_question?skill={SKILL}&level=1&textbook_example_id=12701").get_json()
    assert question["textbook_example_id"] == 12701 and question.get("check_mode") != "ungraded_self_study"
    body = client.post("/check_answer", json={"skill_id": SKILL, "question_uid": question["question_uid"], "answer": "7"}).get_json()
    assert body["correct"] is False  # a real verdict, not the self-study notice


def test_practice_page_keeps_the_handwriting_canvas(client_and_db):
    client, _ = client_and_db
    html = client.get(f"/practice/{SKILL}").get_data(as_text=True)
    assert 'id="handwriting-canvas"' in html and 'id="drawing-background-canvas"' in html


def test_other_legacy_skills_are_not_switched_to_ungraded(client_and_db):
    client, _ = client_and_db  # gh_SineRule also has blank reference answers but is not opted in
    question = client.get("/get_next_question?skill=gh_SineRule&level=1&mode=type_rotation").get_json()
    assert question["question_source"] == "db_textbook_example" and question.get("check_mode") != "ungraded_self_study"
    body = client.post("/check_answer", json={"skill_id": "gh_SineRule", "question_uid": question["question_uid"], "answer": "1"}).get_json()
    assert body.get("graded") is not False
