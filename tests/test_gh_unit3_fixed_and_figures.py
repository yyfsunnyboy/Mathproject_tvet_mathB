"""Student-side checks for 普高數學2 Unit 3 that can run BEFORE the formal release (isolated DB, temp fixed config, in-memory candidate).

* 12746 (FIXED_UNGRADED): served as self-check practice from a TEMP merge of the staged entry; no verdict, streak, mastery or mistake record;
  the Unit 2 fixed entries stay intact; the live config file is not touched.
* Figure rows 12756 / 12773: the candidate payload carries ``reuse_textbook_image`` and the practice route attaches the reviewed crop; a row
  without a figure never gets one.
The dynamic components of the unit are exercised through the published facades in the isolated rehearsal
(``reports/gh_math2_unit3_bundle/rehearse_unit3.py``), because they exist only after promotion.
"""

from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "instance" / "kumon_math.db"
pytestmark = pytest.mark.skipif(not PROD.exists(), reason="formal database not present")
sys.path.insert(0, str(ROOT))

from core import fixed_textbook_practice as F  # noqa: E402

STAGED = ROOT / "reports" / "gh_math2_unit3_fixed" / "staged_fixed_entries.json"
SKILLS = ("gh_LogicAndSets", "gh_CountingPrinciples")


def _copy_rows(src, dst, table, where, args):
    cols = [r[1] for r in src.execute(f"pragma table_info({table})")]
    for row in src.execute(f"select {','.join(cols)} from {table} where {where}", args).fetchall():
        dst.execute(f"insert or replace into {table} ({','.join(cols)}) values ({','.join('?' * len(cols))})", row)


@pytest.fixture(scope="module")
def merged_config(tmp_path_factory):
    live_before = F.CONFIG_PATH.read_bytes()
    tmp = tmp_path_factory.mktemp("unit3cfg") / "fixed_textbook_practice.json"
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
    src = sqlite3.connect(f"file:{PROD.as_posix()}?mode=ro", uri=True)
    dst = sqlite3.connect(target)
    for skill in SKILLS:
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


def test_merge_keeps_unit2_entries_and_binds_12746_to_its_stem(merged_config):
    entries = F.load_entries()
    assert {12719, 12727, 12731, 12735, 12746} <= set(entries)
    live = json.loads(PROD.parent.parent.joinpath("configs/fixed_textbook_practice.json").read_text(encoding="utf-8"))["entries"]
    for key, value in live.items():
        assert entries[int(key)] == value
    con = sqlite3.connect(f"file:{PROD.as_posix()}?mode=ro", uri=True)
    try:
        rid, skill, text = con.execute("select id, skill_id, problem_text from textbook_examples where id=12746").fetchone()
    finally:
        con.close()
    from types import SimpleNamespace

    row = SimpleNamespace(id=rid, skill_id=skill, problem_text=text)
    entry = F.entry_for_row(row)
    assert entry and entry["mode"] == "ungraded" and entry["skill_id"] == "gh_LogicAndSets"
    assert F.entry_for_row(SimpleNamespace(id=rid, skill_id=skill, problem_text=text + "（改）")) is None
    assert F.entry_for_row(SimpleNamespace(id=rid, skill_id="gh_Other", problem_text=text)) is None
    assert entry["oracle"]["verified"]["de_morgan_truth_table"] is True


def test_12746_is_self_check_practice_without_any_record(client_and_db):
    client, db = client_and_db
    q = client.get("/get_next_question?skill=gh_LogicAndSets&level=1&mode=type_rotation&textbook_example_id=12746").get_json()
    assert int(q["textbook_example_id"]) == 12746 and q["fixed_textbook_practice"] == "ungraded"
    assert q["check_mode"] == "ungraded_self_study" and q["graded"] is False and len(q["practice_scaffold"]) == 2
    assert "否定" in q["question_text"] and q["correct_answer"] == "" and not q.get("reference_solution")
    blob = json.dumps(q, ensure_ascii=False)
    assert "不是偶數或" not in blob and "不是正數" not in blob and "\\le" not in blob  # the reference arrives only after a submit
    before = _counts(db)
    for answer in ("", "2不是偶數或2不是質數", "亂寫"):
        res = client.post("/check_answer", json={"skill_id": "gh_LogicAndSets", "question_uid": q["question_uid"], "answer": answer})
        body = res.get_json()
        assert res.status_code == 200 and body["correct"] is None and body["graded"] is False
        steps = body["reference_solution"]
        assert len(steps) == 3 and "不是偶數或" in steps[1] and "pi" in steps[2] and "不是正數" in steps[2]
        assert all(s.count("$") % 2 == 0 and "None" not in s for s in steps)
    assert _counts(db) == before


def test_practice_page_has_no_fixed_question_selector(client_and_db):
    client, _ = client_and_db
    for skill in SKILLS:
        html = client.get(f"/practice/{skill}").get_data(as_text=True)
        assert "fixed-example-select" not in html and "固定教材題" not in html


def _candidate_payload(cid):
    from agent_domains_candidate.counting_sets import build_sandbox as B
    from agent_domains_candidate.counting_sets.counting_sets_specs import COMPONENTS
    from agent_domains_candidate.counting_sets.sandbox_harness import register_candidate_in_memory
    from core.gencode.registered_operation_dispatch import dispatch_registered_operation

    register_candidate_in_memory()
    _skill, op, source, sampler = COMPONENTS[cid]
    out = []
    for variant in B.collect_variants(cid, op, source, sampler):
        out.append(dispatch_registered_operation(B.DOMAIN_KEY, op, seed=0, constraints=dict(variant))[1])
    return out


@pytest.mark.parametrize("cid", [12756, 12773])
def test_figure_rows_reuse_the_reviewed_crop_for_every_variant(client_and_db, cid):
    from app import app
    from core.routes.practice import _finalize_practice_question_api_fields

    payloads = _candidate_payload(cid)
    assert len(payloads) >= 6
    crops = set()
    with app.app_context():
        for p in payloads:
            assert p["reuse_textbook_image"] is True and ("如圖" in p["question_text"] or "右圖" in p["question_text"])
            served = _finalize_practice_question_api_fields({**p, "textbook_example_id": cid}, skill_id=p.get("skill_id") or "gh_CountingPrinciples")
            assert len(served["image_assets"]) == 1 and (ROOT / served["image_assets"][0]["path"]).is_file(), cid
            crops.add(served["image_assets"][0]["path"])
    assert len(crops) == 1  # the one reviewed crop of the textbook figure, never a redrawn one


def test_a_row_without_a_figure_gets_no_image(client_and_db):
    from app import app
    from core.routes.practice import _finalize_practice_question_api_fields

    p = _candidate_payload(12750)[0]
    assert not p.get("reuse_textbook_image")
    with app.app_context():
        served = _finalize_practice_question_api_fields({**p, "textbook_example_id": 12750}, skill_id="gh_CountingPrinciples")
    assert served["image_assets"] == []
