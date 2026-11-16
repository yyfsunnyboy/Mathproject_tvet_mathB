"""Math 2 Unit 8 (一維數據分析) textbook-original fallback: no published generator, no verified reference answers.

* all 35 rows are served from the textbook (route ``textbook_example``) with their LaTeX tables intact;
* 隨堂練習10 (12930) shows the 例題9 (12926) bar-chart crop after the P0-A link, and no other Unit 8 row gets a picture;
* a submit is ungraded self-study: no verdict, no "模組載入錯誤", no attempt / progress / mistake record;
* the unpublished revision_0004 is not loaded, and a published V3 skill (Unit 7) keeps its graded flow.

Runs through the Flask test client on the suite's isolated database; the formal DB is only opened read-only to copy the rows.
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "instance" / "kumon_math.db"
pytestmark = pytest.mark.skipif(not PROD.exists(), reason="formal database not present")

UNIT8 = {
    "gh_Mean": [12912, 12913, 12914, 12915, 12916, 12917, 12931, 12936, 12937],
    "gh_MedianAndPercentiles": [12918, 12919, 12920, 12921, 12922, 12923, 12934, 12935, 12946],
    "gh_VarianceAndStandardDeviation": [12924, 12925, 12926, 12927, 12928, 12929, 12930, 12932, 12938, 12940],
    "gh_DataScalingAndShifting": [12933, 12939, 12941, 12942, 12943, 12944, 12945],
}
TABLE_ROWS = {12913, 12916, 12919, 12920, 12922, 12936, 12943, 12944}
CHART_ROWS = {12926, 12930}
PUBLISHED_V3 = "gh_MathematicalExpectation"
NO_ANSWER_NOTICE = "本題目前沒有經驗證的標準答案"


def _copy_rows(src, dst, table: str, where: str, args: tuple) -> None:
    cols = [r[1] for r in src.execute(f"pragma table_info({table})")]
    marks = ",".join("?" * len(cols))
    for row in src.execute(f"select {','.join(cols)} from {table} where {where}", args).fetchall():
        dst.execute(f"insert or replace into {table} ({','.join(cols)}) values ({marks})", row)


def _load_repair():
    path = ROOT / "reports" / "gh_math2_unit8_fallback_repair" / "link_12930_visual.py"
    spec = importlib.util.spec_from_file_location("u8_link_12930_visual", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
    for skill in [*UNIT8, PUBLISHED_V3]:
        _copy_rows(src, dst, "skills_info", "skill_id=?", (skill,))
        _copy_rows(src, dst, "skill_curriculum", "skill_id=?", (skill,))
        _copy_rows(src, dst, "textbook_examples", "skill_id=?", (skill,))
    dst.commit()
    src.close()
    _load_repair().apply(dst)
    dst.close()
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = "1"
            sess["_fresh"] = True
        yield client, target


def _next(client, skill: str, **extra):
    query = "&".join(f"{k}={v}" for k, v in {"skill": skill, "level": 1, **extra}.items())
    return client.get(f"/get_next_question?{query}").get_json()


def _counts(copy: Path) -> dict:
    con = sqlite3.connect(copy)
    try:
        return {t: con.execute(f"select count(*) from {t}").fetchone()[0]
                for t in ("practice_attempts", "adaptive_learning_logs", "progress", "mistake_notebook_entries", "student_abilities")}
    finally:
        con.close()


def _stems(copy: Path) -> dict[int, str]:
    con = sqlite3.connect(copy)
    try:
        return dict(con.execute("select id, problem_text from textbook_examples where id between 12912 and 12946").fetchall())
    finally:
        con.close()


def test_all_35_rows_are_served_from_the_textbook_with_tables_and_charts(client_and_db):
    client, copy = client_and_db
    stems, seen = _stems(copy), {}
    for skill, ids in UNIT8.items():
        for _ in range(len(ids) + 2):
            question = _next(client, skill)
            assert question["route_mode"] == "textbook_example" and question["question_source"] == "db_textbook_example"
            seen[question["textbook_example_id"]] = question
        assert set(ids) <= set(seen)
    assert sorted(seen) == list(range(12912, 12947))
    for qid, question in seen.items():
        assert question["question_text"] == stems[qid]  # stem, formulas and tables untouched
        assert ("\\begin{array}" in question["question_text"]) == (qid in TABLE_ROWS)
        assets = question.get("image_assets") or []
        if qid in CHART_ROWS:
            assert len(assets) == 1 and assets[0]["url"].endswith("_fig1.png") and question["visual_backed"] is True
        else:
            assert assets == []
    assert seen[12926]["image_assets"][0]["url"] == seen[12930]["image_assets"][0]["url"]


def test_submit_is_ungraded_self_study_and_leaves_no_record(client_and_db):
    client, copy = client_and_db
    before = _counts(copy)
    for skill in UNIT8:
        question = _next(client, skill)
        assert question["check_mode"] == "ungraded_self_study" and question["graded"] is False
        assert not str(question.get("correct_answer") or "").strip()
        for answer in ("12", "國文科", ""):
            res = client.post("/check_answer", json={"skill_id": skill, "question_uid": question["question_uid"], "answer": answer})
            body = res.get_json()
            assert res.status_code == 200 and body["correct"] is None and body["graded"] is False
            assert "模組載入錯誤" not in body["result"] and NO_ANSWER_NOTICE in body["result"]
            assert "證明" not in body["result"] and body["reference_solution"] == []
    assert _counts(copy) == before


def test_a_row_that_gets_a_reference_answer_is_graded_again(client_and_db):
    client, copy = client_and_db
    con = sqlite3.connect(copy)
    con.execute("update textbook_examples set correct_answer='5' where id=12924")
    con.commit()
    con.close()
    try:
        question = _next(client, "gh_VarianceAndStandardDeviation", textbook_example_id=12924)
        assert question["textbook_example_id"] == 12924 and question.get("check_mode") != "ungraded_self_study"
        body = client.post("/check_answer", json={"skill_id": "gh_VarianceAndStandardDeviation",
                                                  "question_uid": question["question_uid"], "answer": "7"}).get_json()
        assert body.get("graded") is not False
    finally:
        con = sqlite3.connect(copy)
        con.execute("update textbook_examples set correct_answer='' where id=12924")
        con.commit()
        con.close()


def test_unpublished_revision_0004_is_not_loaded():
    from core.registry.domain_operation_registry import get_domain_spec

    assert get_domain_spec("statistics.univariate_descriptive") is None
    for skill in UNIT8:
        assert not (ROOT / "skills" / f"{skill}.py").exists()
        assert not (ROOT / "agent_skills_v3" / skill).exists()
    store = json.loads((ROOT / "configs" / "gencode_promoted_capabilities.json").read_text(encoding="utf-8"))
    assert "statistics.univariate_descriptive" not in json.dumps(store)


@pytest.mark.skipif(not (ROOT / "skills" / f"{PUBLISHED_V3}.py").exists(), reason="Unit 7 facade not published")
def test_published_v3_skill_keeps_its_graded_flow(client_and_db):
    client, _ = client_and_db
    question = _next(client, PUBLISHED_V3)
    assert question.get("question_source") != "db_textbook_example" and question.get("check_mode") != "ungraded_self_study"
    body = client.post("/check_answer", json={"skill_id": PUBLISHED_V3, "question_uid": question["question_uid"],
                                              "answer": "-987654"}).get_json()
    assert body.get("graded") is not False and body.get("correct") is False
