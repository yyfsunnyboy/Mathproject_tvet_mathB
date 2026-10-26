"""Fixed textbook practice for the four Unit 2 rows without a Generator (12719, 12727 graded; 12731, 12735 self-check).

Runs through the Flask test client on the suite's isolated database; the formal DB is only opened read-only to copy rows.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "instance" / "kumon_math.db"
pytestmark = pytest.mark.skipif(not PROD.exists(), reason="formal database not present")
sys.path.insert(0, str(ROOT))

from core import fixed_textbook_practice as F  # noqa: E402

SKILLS = ("gh_Series", "gh_CommonSeriesSummationFormulas")
GRADED = {12719: ("gh_Series", "341/128", ["341/128", "2.6640625", "682/256"], ["341/127", "2", "5"]),
          12727: ("gh_Series", "31/2", ["31/2", "15.5", "62/4"], ["15", "16", "31"])}
UNGRADED = {12731: "gh_CommonSeriesSummationFormulas", 12735: "gh_CommonSeriesSummationFormulas"}


def _copy_rows(src, dst, table, where, args):
    cols = [r[1] for r in src.execute(f"pragma table_info({table})")]
    for row in src.execute(f"select {','.join(cols)} from {table} where {where}", args).fetchall():
        dst.execute(f"insert or replace into {table} ({','.join(cols)}) values ({','.join('?' * len(cols))})", row)


@pytest.fixture(scope="module")
def client_and_db():
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
    for skill in SKILLS + ("gh_Sequence",):
        _copy_rows(src, dst, "skills_info", "skill_id=?", (skill,))
        _copy_rows(src, dst, "skill_curriculum", "skill_id=?", (skill,))
        _copy_rows(src, dst, "textbook_examples", "skill_id=?", (skill,))
    dst.commit()
    dst.close()
    src.close()
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = "1"
            sess["_fresh"] = True
        yield client, target


def _counts(db: Path) -> dict:
    con = sqlite3.connect(db)
    try:
        return {t: con.execute(f"select count(*) from {t}").fetchone()[0]
                for t in ("practice_attempts", "adaptive_learning_logs", "progress", "mistake_notebook_entries", "student_abilities")}
    finally:
        con.close()


def _serve(client, skill, rid):
    return client.get(f"/get_next_question?skill={skill}&level=1&mode=type_rotation&textbook_example_id={rid}").get_json()


def _check(client, skill, question, answer):
    return client.post("/check_answer", json={"skill_id": skill, "question_uid": question["question_uid"], "answer": answer}).get_json()


def test_config_is_bound_to_the_stage1_stems_and_the_derived_oracles():
    con = sqlite3.connect(f"file:{PROD.as_posix()}?mode=ro", uri=True)
    try:
        rows = {r[0]: SimpleNamespace(id=r[0], skill_id=r[1], problem_text=r[2]) for r in con.execute("select id, skill_id, problem_text from textbook_examples where id in (12719,12727,12731,12735)")}
    finally:
        con.close()
    assert sorted(F.load_entries()) == [12719, 12727, 12731, 12735]
    oracles = json.loads((ROOT / "reports/gh_math2_unit2_fixed/fixed_oracles.json").read_text(encoding="utf-8"))
    for rid, row in rows.items():
        entry = F.entry_for_row(row)
        assert entry is not None and entry["skill_id"] == row.skill_id, rid
        if rid in GRADED:
            assert entry["mode"] == "graded" and entry["answer"] == oracles[str(rid)]["answer"] == GRADED[rid][1]
        else:
            assert entry["mode"] == "ungraded" and len(entry["practice_scaffold"]) == 3 and len(entry["reference_solution"]) >= 5
    # the entry never applies to a changed stem or another skill
    changed = SimpleNamespace(id=12719, skill_id="gh_Series", problem_text=rows[12719].problem_text + "（改）")
    assert F.entry_for_row(changed) is None
    assert F.entry_for_row(SimpleNamespace(id=12719, skill_id="gh_Other", problem_text=rows[12719].problem_text)) is None


def test_practice_page_has_no_fixed_question_selector(client_and_db):
    client, _ = client_and_db
    for skill in SKILLS:
        html = client.get(f"/practice/{skill}").get_data(as_text=True)
        assert "fixed-example-select" not in html and "固定教材題" not in html  # no second mode, no dropdown: 下一題 follows the textbook


@pytest.mark.parametrize("rid", sorted(GRADED))
def test_figure_rows_are_served_with_their_image_and_graded_by_the_shared_checker(client_and_db, rid):
    client, db = client_and_db
    skill, canonical, good, bad = GRADED[rid]
    question = _serve(client, skill, rid)
    assert question["textbook_example_id"] == rid and question["question_source"] == "db_textbook_example"
    assert question["fixed_textbook_practice"] == "graded" and question.get("graded") is not False and question.get("check_mode") != "ungraded_self_study"
    assert question["answer_contract"]["checker_key"] == "rational_checker"
    assert len(question["image_assets"]) == 1 and (ROOT / question["image_assets"][0]["path"]).is_file()  # the reviewed crop, never redrawn
    for answer in good:  # a correct answer closes the question, so every answer is tried on a freshly served one
        assert _check(client, skill, _serve(client, skill, rid), answer)["correct"] is True, (rid, answer)
    for answer in bad:
        assert _check(client, skill, _serve(client, skill, rid), answer)["correct"] is False, (rid, answer)


@pytest.mark.parametrize("rid", sorted(UNGRADED))
def test_induction_rows_are_self_check_practice_with_a_verified_reference_proof(client_and_db, rid):
    client, db = client_and_db
    skill = UNGRADED[rid]
    question = _serve(client, skill, rid)
    assert question["check_mode"] == "ungraded_self_study" and question["graded"] is False and len(question["practice_scaffold"]) == 3
    assert "數學歸納法" in question["question_text"] and not question["image_assets"]
    before = _counts(db)
    for answer in ("", "證明：略", "n=1 成立"):
        res = client.post("/check_answer", json={"skill_id": skill, "question_uid": question["question_uid"], "answer": answer})
        body = res.get_json()
        assert res.status_code == 200 and body["correct"] is None and body["graded"] is False
        steps = body["reference_solution"]
        assert len(steps) == 5 and "n=1" in steps[0] and "n=k" in steps[1] and "n=k+1" in steps[2]
        assert all(s.count("$") % 2 == 0 and "None" not in s for s in steps)
    assert _counts(db) == before  # no attempt, streak, mastery or mistake record


def test_dynamic_rows_of_the_same_skills_are_still_served_by_their_generators(client_and_db):
    client, _ = client_and_db
    for skill in SKILLS:
        kinds = set()
        for _ in range(8):
            q = client.get(f"/get_next_question?skill={skill}&level=1&mode=type_rotation").get_json()
            if q.get("fixed_textbook_practice"):
                continue
            kinds.add("dynamic")
            assert q.get("graded") is not False and q["question_source"] != "db_textbook_example" and q["component_id"] == f"src_{q['textbook_example_id']}"
        assert kinds == {"dynamic"}


# --- safety: no answer leak before submitting, no credit inflation by repeating a fixed row, normal flow still recorded ------------------------

def test_graded_fixed_rows_do_not_send_the_answer_or_any_reference_before_submitting(client_and_db):
    client, _ = client_and_db
    secrets = {12719: ("341/128", "2.6640625"), 12727: ("31/2", "15.5")}
    for rid, skill in ((12719, "gh_Series"), (12727, "gh_Series"), (12731, "gh_CommonSeriesSummationFormulas"), (12735, "gh_CommonSeriesSummationFormulas")):
        question = _serve(client, skill, rid)
        blob = json.dumps(question, ensure_ascii=False)
        assert question["correct_answer"] == "" and question["answer"] == "", rid
        for secret in secrets.get(rid, ()):
            assert secret not in blob, (rid, secret)
        assert not question.get("reference_solution") and "【驗證" not in blob and "【推導" not in blob, rid  # the reference proof / steps arrive only after a submit
        assert question["answer_contract"].get("expected_answer") is None
        page = client.get(f"/practice/{skill}").get_data(as_text=True)
        assert all(s not in page for s in ("341/128", "31/2", "【推導"))  # nor does the page shell or the selector


def test_repeating_a_fixed_row_credits_streak_and_attempts_only_once(client_and_db):
    client, db = client_and_db
    con = sqlite3.connect(db)  # the suite's isolated database: start from a student who has solved neither figure row yet
    con.execute("delete from practice_attempts where skill_id='gh_Series'")
    con.execute("delete from progress where skill_id='gh_Series'")
    con.commit()
    con.close()
    first = _check(client, "gh_Series", _serve(client, "gh_Series", 12727), "31/2")
    assert first["correct"] is True and _counts(db)["practice_attempts"] == 1
    after_first = _counts(db)
    streak_after_first = first.get("consecutive_correct")
    for _ in range(4):
        again = _check(client, "gh_Series", _serve(client, "gh_Series", 12727), "15.5")
        assert again["correct"] is True  # the verdict is still shown
        assert again.get("consecutive_correct") == streak_after_first
    assert _counts(db) == after_first  # no new attempt, progress or ability record
    other = _check(client, "gh_Series", _serve(client, "gh_Series", 12719), "341/128")  # a different fixed row still earns its own credit
    assert other["correct"] is True and _counts(db)["practice_attempts"] == after_first["practice_attempts"] + 1


def test_dynamic_flow_next_question_and_submit_are_still_recorded(client_and_db):
    client, db = client_and_db
    before = _counts(db)
    question = client.get("/get_next_question?skill=gh_Series&level=1&mode=type_rotation").get_json()
    assert question["question_source"] != "db_textbook_example" and question.get("graded") is not False and question.get("fixed_textbook_practice") is None
    parts = (question.get("answer_contract") or {}).get("parts")
    wrong = {p["key"]: "999999" for p in parts} if parts else "999999"
    body = client.post("/check_answer", json={"skill_id": "gh_Series", "question_uid": question["question_uid"], "answer": wrong, "answers": wrong}).get_json()
    assert body["correct"] is False
    assert _counts(db)["practice_attempts"] == before["practice_attempts"] + 1  # the normal verdict path still writes its attempt


def test_admin_examples_page_shows_fixed_practice_without_posing_as_gencode(client_and_db):
    import re

    client, _ = client_and_db
    html = ""
    for page in (1, 2, 3):
        res = client.get(f"/examples?skill_id=gh_Series&page={page}")
        assert res.status_code == 200, res.status_code
        html += res.get_data(as_text=True)
    badges = dict(re.findall(r'data-v3-badge-example-id="(\d+)".*?<span class="v3-badge-label">([^<]+)</span>', html, flags=re.S))
    assert badges, "no status badge rendered"
    for rid in ("12719", "12727"):
        assert badges[rid] == "固定教材可練習（可自動判分）", (rid, badges[rid])
    assert "固定教材" not in badges.get("12707", "")  # a generated row of the same skill keeps its GenCode badge
    assert 'teacher-v3-fixed-graded' in html


# --- "下一題" walks the textbook order; dynamic and fixed rows are one sequence ---------------------------------------------------------

def _expected_sequence(db: Path, skill: str, generator_keys: set[str]) -> list[int]:
    """Practisable rows of the skill in Stage 1 reading order (anchor source_order), computed straight from the stored notes."""
    con = sqlite3.connect(db)
    try:
        rows = con.execute("select id, notes from textbook_examples where skill_id=?", (skill,)).fetchall()
    finally:
        con.close()
    fixed = set(F.load_entries())
    order = sorted(rows, key=lambda r: (int(((json.loads(r[1] or "{}").get("question_anchor") or {}).get("source_order")) or 10 ** 9), r[0]))
    return [r[0] for r in order if f"src_{r[0]}" in generator_keys or r[0] in fixed]


@pytest.mark.parametrize(("skill", "fixed_ids"), [("gh_Series", {12719, 12727}), ("gh_CommonSeriesSummationFormulas", {12731, 12735})])
def test_next_question_follows_the_textbook_order_across_dynamic_and_fixed_rows(client_and_db, skill, fixed_ids):
    import importlib

    client, db = client_and_db
    generator_keys = set(importlib.import_module(f"skills.{skill}").GENERATOR_KEYS)
    expected = _expected_sequence(db, skill, generator_keys)
    assert fixed_ids <= set(expected) and len(expected) == len(generator_keys) + len(fixed_ids)
    assert expected != sorted(expected)  # reading order interleaves 例題 / 隨堂練習 / 習題; it is not id order
    client.get("/get_next_question?skill=gh_Sequence&level=1&mode=type_rotation")  # leaving a skill forgets the position: a fresh visit starts at the first row
    first = client.get(f"/get_next_question?skill={skill}&level=1&mode=type_rotation").get_json()
    assert int(first["textbook_example_id"]) == expected[0]
    served, kinds = [int(first["textbook_example_id"])], {int(first["textbook_example_id"]): ("fixed" if first.get("fixed_textbook_practice") else "dynamic")}
    for _ in range(len(expected) * 2 + 3):  # two full passes and a bit more: the sequence wraps around
        q = client.get(f"/get_next_question?skill={skill}&level=1&mode=type_rotation").get_json()
        rid = int(q["textbook_example_id"])
        served.append(rid)
        kinds[rid] = ("fixed" if q.get("fixed_textbook_practice") else "dynamic")
        if rid in fixed_ids:
            assert q["question_source"] == "db_textbook_example" and q["fixed_textbook_practice"] in ("graded", "ungraded")
        else:
            assert not q.get("fixed_textbook_practice") and q.get("graded") is not False and q["question_source"] != "db_textbook_example"
    start = expected.index(served[0])  # the position carries over from whatever the student saw last; from there the order is strict and cyclic
    assert served == (expected * 4)[start: start + len(served)], served
    assert {rid for rid, k in kinds.items() if k == "fixed"} == fixed_ids  # no fixed row is skipped, none shows up elsewhere


def test_skills_without_fixed_rows_keep_their_existing_selection(client_and_db):
    from core.textbook_order_practice import pick_next_in_textbook_order
    from models import TextbookExample

    client, _ = client_and_db
    rows = TextbookExample.query.filter_by(skill_id="gh_Sequence").all()
    assert rows and pick_next_in_textbook_order(rows, last_served_id=None, generator_keys={f"src_{r.id}" for r in rows}) is None
    q = client.get("/get_next_question?skill=gh_Sequence&level=1&mode=type_rotation").get_json()
    assert q.get("fixed_textbook_practice") is None and q["question_source"] != "db_textbook_example"


def test_explicit_requests_still_bypass_the_sequence(client_and_db):
    client, _ = client_and_db
    q = client.get("/get_next_question?skill=gh_Series&level=1&mode=type_rotation&component_id=src_12707").get_json()
    assert int(q["textbook_example_id"]) == 12707 and not q.get("fixed_textbook_practice")
    q = client.get("/get_next_question?skill=gh_Series&level=1&mode=type_rotation&textbook_example_id=12727").get_json()
    assert int(q["textbook_example_id"]) == 12727 and q["fixed_textbook_practice"] == "graded"


# --- last acceptance round: refresh / pruning / re-login, all 37 rows, streak contract, mixed-practice streak text -------------------------------

def _next(client, skill, **extra):
    query = "&".join(f"{k}={v}" for k, v in {"skill": skill, "level": 1, "mode": "type_rotation", **extra}.items())
    return client.get(f"/get_next_question?{query}").get_json()


def _walk_to(client, skill, rid, limit=60):
    for _ in range(limit):
        q = _next(client, skill)
        if int(q["textbook_example_id"]) == rid:
            return q
    raise AssertionError(f"{rid} never served")


def test_refresh_returns_to_the_open_row_and_moves_on_once_it_is_answered(client_and_db):
    client, _ = client_and_db
    q = _walk_to(client, "gh_Series", 12719)
    again = _next(client, "gh_Series", resume=1)  # page refresh while the row is still open: the same row, not a skip and not a jump back
    assert int(again["textbook_example_id"]) == 12719 and again["fixed_textbook_practice"] == "graded"
    assert _check(client, "gh_Series", again, "341/128")["correct"] is True  # answered ...
    after = _next(client, "gh_Series", resume=1)  # ... so a refresh now continues with the next row
    assert int(after["textbook_example_id"]) == 12713
    assert int(_next(client, "gh_Series")["textbook_example_id"]) == 12720  # and plain 下一題 always advances


def test_session_pruning_keeps_the_textbook_position(client_and_db):
    client, _ = client_and_db
    _walk_to(client, "gh_Series", 12712)
    with client.session_transaction() as sess:  # push the cookie over its size target: pruning drops every practice key outside its keep list
        sess["bulky_practice_cache"] = "x" * 6000
        sess["te_seq_gh_Series"] = 5
    nxt = _next(client, "gh_Series")
    assert int(nxt["textbook_example_id"]) == 12719  # 例題6 -> 隨堂練習6 even though the extra state was pruned
    with client.session_transaction() as sess:
        assert "bulky_practice_cache" not in sess and sess.get("current_textbook_example_id") == "12719"


def test_a_new_login_starts_again_at_the_first_row_but_fixed_credit_is_kept(client_and_db):
    from app import app

    client, db = client_and_db
    con = sqlite3.connect(db)
    con.execute("delete from practice_attempts where skill_id='gh_Series'")
    con.execute("delete from progress where skill_id='gh_Series'")
    con.commit()
    con.close()
    _walk_to(client, "gh_Series", 12727)
    assert _check(client, "gh_Series", _serve(client, "gh_Series", 12727), "31/2")["correct"] is True
    credited = _counts(db)["practice_attempts"]
    assert credited == 1
    with app.test_client() as fresh:  # same student, new session (re-login): the position lives in the session, there is no stored position
        with fresh.session_transaction() as sess:
            sess["_user_id"] = "1"
            sess["_fresh"] = True
        assert int(_next(fresh, "gh_Series")["textbook_example_id"]) == 12707  # LIMITATION: the place in the book is not kept across sessions
        assert _check(fresh, "gh_Series", _serve(fresh, "gh_Series", 12727), "31/2")["correct"] is True  # the verdict is still shown ...
    assert _counts(db)["practice_attempts"] == credited  # ... but the credit is database-backed: not given twice


def test_all_37_rows_are_reachable_in_stage1_reading_order(client_and_db):
    import importlib

    client, db = client_and_db
    reached: dict[int, int] = {}
    for skill in SKILLS:
        keys = set(importlib.import_module(f"skills.{skill}").GENERATOR_KEYS)
        expected = _expected_sequence(db, skill, keys)
        client.get("/get_next_question?skill=gh_Sequence&level=1&mode=type_rotation")  # forget any position
        served = [int(_next(client, skill)["textbook_example_id"]) for _ in expected]
        assert served == expected, skill
        reached.update({rid: i for i, rid in enumerate(served)})
    assert sorted(reached) == list(range(12707, 12744))  # 33 generated + 4 fixed = every row of the unit
    con = sqlite3.connect(db)
    try:
        order = {rid: int(json.loads(notes)["question_anchor"]["source_order"]) for rid, notes in con.execute(
            "select id, notes from textbook_examples where id between 12707 and 12743")}
    finally:
        con.close()
    assert sorted(order.values()) == list(range(1, 38))  # the Stage 1 reading order of the whole unit is 1..37, each used once
    for skill in SKILLS:  # within a skill the served order is strictly increasing in reading order (one wrap per pass)
        keys = set(importlib.import_module(f"skills.{skill}").GENERATOR_KEYS)
        seq = _expected_sequence(db, skill, keys)
        assert [order[r] for r in seq] == sorted(order[r] for r in seq)


def test_selfcheck_rows_never_move_the_streak_or_the_records(client_and_db):
    from core import practice_question_store as QS

    client, db = client_and_db
    skill = "gh_CommonSeriesSummationFormulas"
    con = sqlite3.connect(db)
    con.execute("delete from practice_attempts where skill_id=?", (skill,))
    con.execute("delete from progress where skill_id=?", (skill,))
    con.commit()
    con.close()

    def streak():
        con = sqlite3.connect(db)
        try:
            row = con.execute("select consecutive_correct from progress where skill_id=? and user_id=1", (skill,)).fetchone()
        finally:
            con.close()
        return row[0] if row else 0

    def typed(value):
        if isinstance(value, list):
            return ", ".join(str(v) for v in value)
        return {k: typed(v) for k, v in value.items()} if isinstance(value, dict) else value

    dynamic = next(q for q in (_next(client, skill) for _ in range(12)) if not q.get("fixed_textbook_practice"))
    expected = next(b[dynamic["question_uid"]] for b in QS._STORE.values() if dynamic["question_uid"] in b)["correct_answer"]
    answer = typed(expected)
    assert client.post("/check_answer", json={"skill_id": skill, "question_uid": dynamic["question_uid"], "answer": answer, "answers": answer}).get_json()["correct"] is True
    def attempts():
        con = sqlite3.connect(db)
        try:
            return con.execute("select count(*) from practice_attempts where skill_id=?", (skill,)).fetchone()[0]
        finally:
            con.close()

    assert streak() == 1 and attempts() == 1  # a graded generated question builds the streak as always
    snapshot = (streak(), attempts(), _counts(db))
    for rid in (12731, 12735):  # proofs, answered or not: nothing moves
        q = _serve(client, skill, rid)
        for answer in ("", "n=1 成立", "亂寫"):
            assert client.post("/check_answer", json={"skill_id": skill, "question_uid": q["question_uid"], "answer": answer}).get_json()["graded"] is False
    assert (streak(), attempts(), _counts(db)) == snapshot


def test_mixed_practice_pages_show_only_n_and_other_pages_keep_n_over_m(client_and_db):
    client, _ = client_and_db
    common = client.get("/practice/gh_CommonSeriesSummationFormulas").get_data(as_text=True)
    import re

    assert "PRACTICE_STREAK_WITHOUT_TARGET = true" in common
    assert re.search(r"id=\"streak-counter\"[^>]*>🔥 連續答對 \d+ 題<", common) and not re.search(r"連續答對 \d+ / 11 題", common)
    series = client.get("/practice/gh_Series").get_data(as_text=True)  # graded fixed rows only: the target is reachable, so the usual N / M stays
    assert "PRACTICE_STREAK_WITHOUT_TARGET = false" in series and re.search(r"連續答對 \d+ / 26 題", series)
    other = client.get("/practice/gh_Sequence").get_data(as_text=True)
    assert "PRACTICE_STREAK_WITHOUT_TARGET = false" in other and "題" in other
