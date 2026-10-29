"""Student-side checks for 普高數學2 Unit 5 (組合) 習題進階題12 that run BEFORE the formal release.

The row, its figure crop and the isolated import come from the rehearsal (``reports/gh_math2_unit5_fixed/rehearse_unit5_fixed.py``,
sandbox DB + sandbox uploads); the entry is a TEMP merge of ``reports/gh_math2_unit5_fixed/staged_fixed_entries.json``.  The live fixed config,
the formal DB and the real uploads folder are never touched.

* 進階題12 (FIXED_GRADED multi_part): the textbook stem with the reviewed semicircle crop; (1) single choice ③ (40 lines), (2) 116 triangles,
  graded by the shared multi_part / choice_label / integer checkers; nothing of the answer reaches the browser before submitting.
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "reports" / "gh_math2_unit5_fixed"
SANDBOX_DB = HERE / "sandbox" / "unit5.db"
STAGED = HERE / "staged_fixed_entries.json"
pytestmark = pytest.mark.skipif(not (SANDBOX_DB.exists() and STAGED.exists()), reason="Unit 5 rehearsal output not present")
sys.path.insert(0, str(ROOT))

from core import fixed_textbook_practice as F  # noqa: E402

SKILL = "gh_Combination"
ANCHOR = "general_2_section_advanced_exercise_012_037"
RID = int(next(iter(json.loads(STAGED.read_text(encoding="utf-8"))["entries"]))) if STAGED.exists() else 0
SECRETS = ("116", "③", "40")


def _copy_rows(src, dst, table, where, args):
    cols = [r[1] for r in src.execute(f"pragma table_info({table})")]
    dst_cols = {r[1] for r in dst.execute(f"pragma table_info({table})")}
    cols = [c for c in cols if c in dst_cols]
    for row in src.execute(f"select {','.join(cols)} from {table} where {where}", args).fetchall():
        dst.execute(f"insert or replace into {table} ({','.join(cols)}) values ({','.join('?' * len(cols))})", row)


@pytest.fixture(scope="module")
def merged_config(tmp_path_factory):
    live_before = F.CONFIG_PATH.read_bytes()
    tmp = tmp_path_factory.mktemp("unit5cfg") / "fixed_textbook_practice.json"
    shutil.copyfile(F.CONFIG_PATH, tmp)
    data = json.loads(tmp.read_text(encoding="utf-8"))
    for key, value in json.loads(STAGED.read_text(encoding="utf-8"))["entries"].items():
        data["entries"].setdefault(key, value)  # once released, the live entry (teacher-approved figure) is authoritative
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
    from core import question_image_assets as Q
    from models import db

    app.config["WTF_CSRF_ENABLED"] = False
    uri = app.config["SQLALCHEMY_DATABASE_URI"]
    assert "pytest_isolated.db" in uri
    target = Path(uri[len("sqlite:///"):])
    with app.app_context():
        db.create_all()
    src = sqlite3.connect(f"file:{SANDBOX_DB.as_posix()}?mode=ro", uri=True)
    dst = sqlite3.connect(target)
    _copy_rows(src, dst, "skills_info", "skill_id=?", (SKILL,))
    _copy_rows(src, dst, "skill_curriculum", "skill_id=?", (SKILL,))
    _copy_rows(src, dst, "textbook_examples", "skill_id=?", (SKILL,))
    dst.commit()
    dst.close()
    src.close()
    real_url = Q.question_asset_public_url
    Q.question_asset_public_url = lambda path, *, root_path=None: real_url(path, root_path=str(HERE / "sandbox"))  # rehearsal crops only
    try:
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess["_user_id"] = "1"
                sess["_fresh"] = True
            yield client, target
    finally:
        Q.question_asset_public_url = real_url


def _counts(db: Path) -> dict:
    con = sqlite3.connect(db)
    try:
        return {t: con.execute(f"select count(*) from {t}").fetchone()[0]
                for t in ("practice_attempts", "adaptive_learning_logs", "progress", "mistake_notebook_entries", "student_abilities")}
    finally:
        con.close()


def _serve(client, rid=RID):
    return client.get(f"/get_next_question?skill={SKILL}&level=1&mode=type_rotation&textbook_example_id={rid}").get_json()


def _check(client, question, answer):
    res = client.post("/check_answer", json={"skill_id": SKILL, "question_uid": question["question_uid"], "answer": answer})
    assert res.status_code == 200
    return res.get_json()


def _row(rid=RID):
    con = sqlite3.connect(f"file:{SANDBOX_DB.as_posix()}?mode=ro", uri=True)
    try:
        return con.execute("select id, skill_id, problem_text, notes from textbook_examples where id=?", (rid,)).fetchone()
    finally:
        con.close()


def test_entry_is_bound_to_the_anchor_stem_and_keeps_existing_entries(merged_config):
    from types import SimpleNamespace

    live = json.loads(ROOT.joinpath("configs/fixed_textbook_practice.json").read_text(encoding="utf-8"))["entries"]
    entries = F.load_entries()
    for key, value in live.items():
        assert entries[int(key)] == value
    rid, skill, text, notes = _row()
    assert json.loads(notes)["question_anchor"]["anchor_id"] == ANCHOR
    entry = F.entry_for_row(SimpleNamespace(id=rid, skill_id=skill, problem_text=text))
    assert entry and entry["mode"] == "graded" and entry["skill_id"] == SKILL and entry["question_anchor"] == ANCHOR
    assert entry["answer"] == {"part_1": "③", "part_2": "116"}
    assert all("expected_answer" not in p for p in entry["answer_contract"]["parts"])
    prov = entry["provenance"]
    assert (prov["curriculum"], prov["volume"], prov["chapter"], prov["pdf_page"]) == ("general", "數學2", "單元5 組合", 16)
    assert F.entry_for_row(SimpleNamespace(id=rid, skill_id=skill, problem_text=text + "（改）")) is None
    assert F.entry_for_row(SimpleNamespace(id=rid, skill_id="gh_Other", problem_text=text)) is None


def test_served_as_the_textbook_original_with_the_semicircle_and_no_answer(client_and_db):
    client, _ = client_and_db
    q = _serve(client)
    assert int(q["textbook_example_id"]) == RID and q["question_source"] == "db_textbook_example"
    assert q["route_reason"] == "no_generator_serve_textbook_example" and q["wrapper_loaded"] is False
    assert q["fixed_textbook_practice"] == "graded" and q.get("graded") is not False and q.get("check_mode") != "ungraded_self_study"
    _rid, _skill, text, _notes = _row()
    assert q["question_text"] == text and "半圓" in text and "(1)" in text and "(2)" in text
    ac = q["answer_contract"]
    assert ac["answer_type"] == "multi_part" and [p["key"] for p in ac["parts"]] == ["part_1", "part_2"]
    assert len(q["image_assets"]) == 1
    asset = q["image_assets"][0]
    assert (HERE / "sandbox" / asset["path"]).is_file() and "進階題12" in asset["path"]
    assert q["correct_answer"] == "" and q["answer"] == "" and not q.get("reference_solution")
    blob = json.dumps({k: v for k, v in q.items() if k not in ("question_uid", "image_assets", "question_text", "new_question_text",
                                                                 "question_text_hash")}, ensure_ascii=False)
    for secret in ("116", "expected_answer", "canonical_answer"):
        assert secret not in blob, secret
    assert "③" not in json.dumps([{k: v for k, v in p.items() if k != "choices"} for p in ac["parts"]], ensure_ascii=False)


@pytest.mark.parametrize("answer", [{"part_1": "③", "part_2": "116"}, {"part_1": "3", "part_2": "116"}, {"part_1": "40", "part_2": " 116 "},
                                    {"part_1": "③", "part_2": "116.0"}])
def test_correct_answers_are_graded_correct(client_and_db, answer):
    client, _ = client_and_db
    body = _check(client, _serve(client), answer)
    assert body["correct"] is True, body


@pytest.mark.parametrize("answer", [{"part_1": "④", "part_2": "116"}, {"part_1": "③", "part_2": "120"}, {"part_1": "45", "part_2": "116"},
                                    {"part_1": "③", "part_2": ""}, {"part_1": "", "part_2": "116"}, {"part_1": "①", "part_2": "abc"}])
def test_wrong_or_incomplete_answers_are_graded_wrong(client_and_db, answer):
    client, _ = client_and_db
    body = _check(client, _serve(client), answer)
    assert body["correct"] is False, body


def test_attempts_are_recorded_like_other_graded_rows(client_and_db):
    # The row's question_uid is stable, so an identical re-submission of an already-correct answer is a duplicate (existing policy).
    client, db = client_and_db
    before = _counts(db)
    wrong = _check(client, _serve(client), {"part_1": "⑤", "part_2": "120"})
    mid = _counts(db)
    assert wrong["correct"] is False and wrong.get("graded") is not False
    assert mid["practice_attempts"] == before["practice_attempts"] + 1 and mid["mistake_notebook_entries"] >= before["mistake_notebook_entries"] + 1
    assert _check(client, _serve(client), {"part_1": "C", "part_2": "116"})["correct"] is True


def test_other_unit5_rows_are_not_fixed_entries(client_and_db):
    from types import SimpleNamespace

    con = sqlite3.connect(f"file:{SANDBOX_DB.as_posix()}?mode=ro", uri=True)
    try:
        rows = con.execute("select id, skill_id, problem_text from textbook_examples where source_curriculum='general' and source_chapter='單元5 組合'").fetchall()
    finally:
        con.close()
    assert len(rows) == 37
    fixed = sorted(rid for rid, skill, text in rows if F.entry_for_row(SimpleNamespace(id=rid, skill_id=skill, problem_text=text)))
    assert fixed == [RID, 12838, 12845]  # 進階題12 (graded) + the two proof self-check rows released with the Unit 5 GenCode


def test_only_the_figure_dependent_row_carries_an_image():
    con = sqlite3.connect(f"file:{SANDBOX_DB.as_posix()}?mode=ro", uri=True)
    try:
        rows = con.execute("select id, notes from textbook_examples where source_curriculum='general' and source_chapter='單元5 組合'").fetchall()
    finally:
        con.close()
    assert len(rows) == 37
    with_images = {rid: json.loads(notes or "{}").get("image_assets") or [] for rid, notes in rows}
    with_images = {rid: assets for rid, assets in with_images.items() if assets}
    assert list(with_images) == [RID] and len(with_images[RID]) == 1
    asset = with_images[RID][0]
    path = HERE / "sandbox" / asset["path"]
    assert path.is_file() and path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    notes = json.loads(dict(rows)[RID])
    assert notes["question_anchor"]["anchor_id"] == ANCHOR
