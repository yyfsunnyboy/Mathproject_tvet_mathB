"""Student-side checks for 普高數學2 Unit 4 (排列) that can run BEFORE the formal release (isolated DB, temp fixed config, in-memory candidate).

* 12801 (FIXED_GRADED, street graph, answer 62): served from a TEMP merge of the staged entry as the textbook original with its reviewed
  figure crop, graded by the shared rational checker; no answer / reference before submitting; the live config file is not touched.
* Figure rows 12794 / 12797 / 12803: only the variant that restates the textbook figure's own structure carries ``reuse_textbook_image``
  (stem cue + reviewed crop); every other variant describes its data in words (no cue, no image).
The dynamic components themselves are exercised through the published facades in the isolated rehearsal
(``reports/gh_math2_unit4_bundle/rehearse_unit4.py``), because they exist only after promotion.
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

STAGED = ROOT / "reports" / "gh_math2_unit4_fixed" / "staged_fixed_entries.json"
SKILLS = ("gh_LinearPermutation", "gh_PermutationWithIdenticalItems", "gh_RepeatedPermutation")
FIGURE_SKILL = {12794: "gh_PermutationWithIdenticalItems", 12797: "gh_PermutationWithIdenticalItems", 12803: "gh_PermutationWithIdenticalItems"}


def _copy_rows(src, dst, table, where, args):
    cols = [r[1] for r in src.execute(f"pragma table_info({table})")]
    for row in src.execute(f"select {','.join(cols)} from {table} where {where}", args).fetchall():
        dst.execute(f"insert or replace into {table} ({','.join(cols)}) values ({','.join('?' * len(cols))})", row)


@pytest.fixture(scope="module")
def merged_config(tmp_path_factory):
    live_before = F.CONFIG_PATH.read_bytes()
    tmp = tmp_path_factory.mktemp("unit4cfg") / "fixed_textbook_practice.json"
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


def _serve(client, skill, rid):
    return client.get(f"/get_next_question?skill={skill}&level=1&mode=type_rotation&textbook_example_id={rid}").get_json()


def _check(client, skill, question, answer):
    res = client.post("/check_answer", json={"skill_id": skill, "question_uid": question["question_uid"], "answer": answer})
    assert res.status_code == 200
    return res.get_json()


def test_merge_binds_12801_to_its_stage1_stem_and_keeps_existing_entries(merged_config):
    from types import SimpleNamespace

    entries = F.load_entries()
    live = json.loads(ROOT.joinpath("configs/fixed_textbook_practice.json").read_text(encoding="utf-8"))["entries"]
    for key, value in live.items():
        assert entries[int(key)] == value
    con = sqlite3.connect(f"file:{PROD.as_posix()}?mode=ro", uri=True)
    try:
        rid, skill, text = con.execute("select id, skill_id, problem_text from textbook_examples where id=12801").fetchone()
    finally:
        con.close()
    entry = F.entry_for_row(SimpleNamespace(id=rid, skill_id=skill, problem_text=text))
    assert entry and entry["mode"] == "graded" and entry["answer"] == "62" and entry["skill_id"] == "gh_PermutationWithIdenticalItems"
    assert F.entry_for_row(SimpleNamespace(id=rid, skill_id=skill, problem_text=text + "（改）")) is None
    assert F.entry_for_row(SimpleNamespace(id=rid, skill_id="gh_Other", problem_text=text)) is None


def test_12801_is_the_textbook_original_graded_by_the_shared_checker(client_and_db):
    client, _ = client_and_db
    skill = "gh_PermutationWithIdenticalItems"
    q = _serve(client, skill, 12801)
    assert int(q["textbook_example_id"]) == 12801 and q["question_source"] == "db_textbook_example"
    assert q["fixed_textbook_practice"] == "graded" and q.get("graded") is not False and q.get("check_mode") != "ungraded_self_study"
    assert q["answer_contract"]["checker_key"] == "rational_checker"
    assert len(q["image_assets"]) == 1 and (ROOT / q["image_assets"][0]["path"]).is_file()  # the reviewed crop, never redrawn
    assert q["correct_answer"] == "" and q["answer"] == "" and not q.get("reference_solution")
    assert "62" not in json.dumps({k: v for k, v in q.items() if k not in ("question_uid", "image_assets")}, ensure_ascii=False)
    for good in ("62", " 62 "):
        assert _check(client, skill, _serve(client, skill, 12801), good)["correct"] is True, good
    for bad in ("61", "63", "", "31", "abc"):
        assert _check(client, skill, _serve(client, skill, 12801), bad)["correct"] is False, bad


def test_wrong_and_right_12801_answers_show_the_verified_reference_solution(client_and_db):
    client, _ = client_and_db
    skill = "gh_PermutationWithIdenticalItems"
    body = _check(client, skill, _serve(client, skill, 12801), "61")
    steps = body.get("reference_solution") or []
    blob = json.dumps(body, ensure_ascii=False)
    assert body["correct"] is False and "62" in blob and (len(steps) == 3 or "62" in blob)


def test_practice_page_has_no_fixed_question_selector(client_and_db):
    client, _ = client_and_db
    for skill in SKILLS:
        html = client.get(f"/practice/{skill}").get_data(as_text=True)
        assert "fixed-example-select" not in html and "固定教材題" not in html


def _candidate_payloads(cid):
    from agent_domains_candidate.permutations import build_sandbox as B
    from agent_domains_candidate.permutations.permutations_specs import COMPONENTS
    from agent_domains_candidate.permutations.sandbox_harness import register_candidate_in_memory
    from core.gencode.registered_operation_dispatch import dispatch_registered_operation

    register_candidate_in_memory()
    _skill, op, source, sampler = COMPONENTS[cid]
    return [dispatch_registered_operation(B.DOMAIN_KEY, op, seed=0, constraints=dict(v))[1]
            for v in B.collect_variants(cid, op, source, sampler)]


@pytest.mark.parametrize("cid", sorted(FIGURE_SKILL))
def test_figure_rows_reuse_the_reviewed_crop_only_for_the_figure_structure(client_and_db, cid):
    from app import app
    from core.routes.practice import _finalize_practice_question_api_fields

    payloads = _candidate_payloads(cid)
    assert len(payloads) >= 6
    crops, with_figure = set(), 0
    with app.app_context():
        for p in payloads:
            cue = any(w in p["question_text"] for w in ("如圖", "右圖", "下圖"))
            assert bool(p.get("reuse_textbook_image")) == cue, (cid, p["question_text"][:60])
            served = _finalize_practice_question_api_fields({**p, "textbook_example_id": cid}, skill_id=FIGURE_SKILL[cid])
            if cue:
                with_figure += 1
                assert len(served["image_assets"]) == 1 and (ROOT / served["image_assets"][0]["path"]).is_file(), cid
                crops.add(served["image_assets"][0]["path"])
            else:
                assert served["image_assets"] == [], (cid, "a word-only variant must not get the textbook figure")
    assert with_figure >= 1 and len(crops) == 1  # the one reviewed crop, never a redrawn one


def test_a_row_without_a_figure_gets_no_image(client_and_db):
    from app import app
    from core.routes.practice import _finalize_practice_question_api_fields

    p = _candidate_payloads(12774)[0]
    assert not p.get("reuse_textbook_image")
    with app.app_context():
        served = _finalize_practice_question_api_fields({**p, "textbook_example_id": 12774}, skill_id="gh_LinearPermutation")
    assert served["image_assets"] == []

