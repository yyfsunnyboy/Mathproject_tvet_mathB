"""Student-side checks for the two Unit 5 proof rows (例題9 12838, 隨堂練習10 12845, gh_BinomialTheorem).

The released live entries must equal the reviewed ``reports/gh_math2_unit5_fixed/staged_proof_entries.json``; the checks run on a TEMP copy of
the live fixed config merged with the staged file (a no-op once released); the rows come
from the private snapshot of the formal DB (``tmp/gh_math2_unit5_isolated``) copied into the pytest-isolated DB.  The live config and the formal
DB are never touched.  A proof is self-check practice: question + reference proof, no verdict, no attempt / streak / mastery / mistake record.
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
STAGED = ROOT / "reports" / "gh_math2_unit5_fixed" / "staged_proof_entries.json"
pytestmark = pytest.mark.skipif(not STAGED.exists(), reason="Unit 5 staged proof entries not present")
sys.path.insert(0, str(ROOT))

from agent_domains_candidate.combinations.build_sandbox import isolated_db  # noqa: E402
from core import fixed_textbook_practice as F  # noqa: E402

SKILL = "gh_BinomialTheorem"
PROOFS = (12838, 12845)
SNAPSHOT = isolated_db()


def _copy_rows(src, dst, table, where, args):
    cols = [r[1] for r in src.execute(f"pragma table_info({table})")]
    dst_cols = {r[1] for r in dst.execute(f"pragma table_info({table})")}
    cols = [c for c in cols if c in dst_cols]
    for row in src.execute(f"select {','.join(cols)} from {table} where {where}", args).fetchall():
        dst.execute(f"insert or replace into {table} ({','.join(cols)}) values ({','.join('?' * len(cols))})", row)


@pytest.fixture(scope="module")
def merged_config(tmp_path_factory):
    live_before = F.CONFIG_PATH.read_bytes()
    tmp = tmp_path_factory.mktemp("unit5proofs") / "fixed_textbook_practice.json"
    shutil.copyfile(F.CONFIG_PATH, tmp)
    data = json.loads(tmp.read_text(encoding="utf-8"))
    data["entries"].update(json.loads(STAGED.read_text(encoding="utf-8"))["entries"])
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    original = F.CONFIG_PATH
    F.CONFIG_PATH = tmp
    F._cache.update(mtime=None, entries={})
    yield tmp
    F.CONFIG_PATH = original
    F._cache.update(mtime=None, entries={})
    assert original.read_bytes() == live_before, "the live fixed config must not change"


@pytest.fixture(scope="module")
def client_and_db(merged_config):
    from app import app
    from models import db

    app.config["WTF_CSRF_ENABLED"] = False
    uri = app.config["SQLALCHEMY_DATABASE_URI"]
    assert "pytest_isolated.db" in uri
    target = Path(uri[len("sqlite:///"):])
    with app.app_context():
        db.create_all()
    src = sqlite3.connect(f"file:{SNAPSHOT.as_posix()}?mode=ro", uri=True)
    dst = sqlite3.connect(target)
    for table in ("skills_info", "skill_curriculum", "textbook_examples"):
        _copy_rows(src, dst, table, "skill_id=?", (SKILL,))
    dst.commit()
    dst.close()
    src.close()
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = "1"
            sess["_fresh"] = True
        yield client, target


def _rows() -> dict:
    con = sqlite3.connect(f"file:{SNAPSHOT.as_posix()}?mode=ro", uri=True)
    try:
        return {r[0]: SimpleNamespace(id=r[0], skill_id=r[1], problem_text=r[2])
                for r in con.execute("select id, skill_id, problem_text from textbook_examples where id between 12812 and 12848")}
    finally:
        con.close()


def _counts(db: Path) -> dict:
    con = sqlite3.connect(db)
    try:
        return {t: con.execute(f"select count(*) from {t}").fetchone()[0]
                for t in ("practice_attempts", "adaptive_learning_logs", "progress", "mistake_notebook_entries", "student_abilities")}
    finally:
        con.close()


def test_staged_entries_are_bound_to_the_formal_stems_and_keep_the_live_entries(merged_config):
    live = json.loads((ROOT / "configs" / "fixed_textbook_practice.json").read_text(encoding="utf-8"))["entries"]
    staged = json.loads(STAGED.read_text(encoding="utf-8"))["entries"]
    assert all(live.get(str(rid)) == staged[str(rid)] for rid in PROOFS)  # released as reviewed (deploy_unit5.py fixed)
    entries = F.load_entries()
    for key, value in live.items():
        assert entries[int(key)] == value
    rows = _rows()
    for rid in PROOFS:
        entry = F.entry_for_row(rows[rid])
        assert entry and entry["mode"] == "ungraded" and entry["skill_id"] == SKILL and "證明" in rows[rid].problem_text
        assert len(entry["practice_scaffold"]) == 3 and len(entry["reference_solution"]) == 3
        assert all(s.count("$") % 2 == 0 and "None" not in s for s in entry["reference_solution"])
        assert F.entry_for_row(SimpleNamespace(id=rid, skill_id=SKILL, problem_text=rows[rid].problem_text + "（改）")) is None
    fixed = sorted(rid for rid, row in rows.items() if F.entry_for_row(row))
    assert fixed == [12834, 12838, 12845]  # 進階題12 (graded, live) + the two proofs; every other Unit 5 row is a GenCode component


@pytest.mark.parametrize("rid", PROOFS)
def test_proofs_are_self_check_practice_and_never_recorded(client_and_db, rid):
    client, db = client_and_db
    q = client.get(f"/get_next_question?skill={SKILL}&level=1&mode=type_rotation&textbook_example_id={rid}").get_json()
    assert int(q["textbook_example_id"]) == rid and q["fixed_textbook_practice"] == "ungraded"
    assert q["check_mode"] == "ungraded_self_study" and q["graded"] is False and len(q["practice_scaffold"]) == 3
    assert "證明" in q["question_text"] and not q["image_assets"]
    before = _counts(db)
    for answer in ("", "證明：略", "代入 x=y=1"):
        res = client.post("/check_answer", json={"skill_id": SKILL, "question_uid": q["question_uid"], "answer": answer})
        body = res.get_json()
        assert res.status_code == 200 and body["correct"] is None and body["graded"] is False  # self-assessment is never "答對"
        assert len(body["reference_solution"]) == 3 and "代入" in body["reference_solution"][1]
    assert _counts(db) == before  # no attempt, streak, mastery or mistake record
