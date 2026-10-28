"""Transaction-level isolation tests for Stage 1 auto review (Unit 3 pre-repair DB copy).

Only the AI/DOCX text parsing front half of ``process_textbook_file`` is replaced; the replacement
delete, source skill map, PDF visual enrichment, review/heal, Gate, commit/rollback and asset
publishing are the production functions. The formal DB is opened read-only and hash-checked.
"""
import hashlib
import json
import queue as queue_mod
import sqlite3
import uuid
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "reports/gh_math2_unit3_stage1/production_change_set.json"
SOURCE = ROOT / "textbook_import/uploaded_sources/general/數學2"
DOCX = SOURCE / "cd38c1890caf_單元03-計數原理.docx"
PDF = SOURCE / "fe5ce0b620d3_單元03-計數原理.pdf"
FORMAL = ROOT / "instance/kumon_math.db"
CHAPTER = "單元3 計數原理"
VOLUME = "數學2"


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _chapter_fingerprint(db_path, where="source_chapter=?", args=(CHAPTER,), exclude=False):
    con = sqlite3.connect(f"file:{Path(db_path).as_posix()}?mode=ro", uri=True)
    try:
        op = "not (" if exclude else "("
        rows = con.execute(
            f"select * from textbook_examples where {op}source_curriculum='general' and source_volume=? "
            f"and {where}) order by id", (VOLUME, *args)).fetchall()
        return hashlib.sha256(repr(rows).encode()).hexdigest()
    finally:
        con.close()


@pytest.fixture
def env(tmp_path, monkeypatch):
    if not (CASE.is_file() and DOCX.is_file() and PDF.is_file() and FORMAL.is_file()):
        pytest.skip("authoritative Unit 3 source/formal DB unavailable on this checkout")
    formal_before = _sha(FORMAL)
    db_path = tmp_path / "unit3_before.db"
    with sqlite3.connect(f"file:{FORMAL.as_posix()}?mode=ro", uri=True) as src, sqlite3.connect(db_path) as dst:
        src.backup(dst)
    changes = json.loads(CASE.read_text(encoding="utf-8"))
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    for op in changes["updates"]:
        b = op["before"]
        con.execute("update textbook_examples set problem_text=?,detailed_solution=?,skill_id=?,notes=? where id=?",
                    (b["problem_text"], b["detailed_solution"], b["skill_id"], b["notes"], op["id"]))
    for row in changes["old_rows"]:
        cols = list(row)
        con.execute(f"insert into textbook_examples ({','.join(cols)}) values ({','.join('?' for _ in cols)})",
                    [row[k] for k in cols])
    new_rows = [dict(r) for r in con.execute(
        "select * from textbook_examples where source_chapter=? and source_volume=? and id>=12744 order by id",
        (CHAPTER, VOLUME))]
    assert len(new_rows) == 30
    con.execute("delete from textbook_examples where source_chapter=? and source_volume=? and id>=12744",
                (CHAPTER, VOLUME))
    con.commit()
    con.close()

    import config as _cfg
    from app import create_app
    from models import TextbookExample, db

    prev_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + db_path.as_posix()
    try:
        app = create_app()
        app.config.update(TESTING=True)
        root = tmp_path / "project_root"
        root.mkdir()
        app.root_path = str(root)
        with app.app_context():
            old_rows = TextbookExample.query.filter_by(
                source_curriculum="general", source_volume=VOLUME, source_chapter=CHAPTER).order_by(
                TextbookExample.id).all()
            assert len(old_rows) == 20
            from core.general_textbook_replacement import scope_fingerprint
            backup = tmp_path / "pre_replace.db"
            backup.write_bytes(b"sqlite-backup-placeholder")
            policy = {
                "preview": {"volume": VOLUME, "chapter": CHAPTER, "question_count": 30,
                            "docx_sha256": _sha(DOCX)},
                "old_ids": [r.id for r in old_rows],
                "old_rows_fingerprint": scope_fingerprint(old_rows),
                "backup_path": str(backup),
            }
            yield {"app": app, "db": db, "root": root, "policy": policy, "new_rows": new_rows,
                   "db_path": db_path, "model": TextbookExample, "monkeypatch": monkeypatch}
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri
        assert _sha(FORMAL) == formal_before, "formal DB must never change"


def _run(env, *, regions=True, fail_commit=False):
    import core.textbook_processor as tp
    import core.textbook_stage1_auto_review as review
    mp, db, Model = env["monkeypatch"], env["db"], env["model"]
    labels = [r["source_description"].split(" [", 1)[0].strip() for r in env["new_rows"]]
    by_order = sorted(env["new_rows"], key=lambda r: json.loads(r["notes"])["question_anchor"]["source_order"])
    items = [{"canonical_title": r["source_description"].split(" [", 1)[0].strip()} for r in by_order]
    scan = {"chapter": {"unit": "單元3", "title": "計數原理"}, "items": items,
            "blocks": {i["canonical_title"]: "" for i in items}, "solutions": {}}

    mp.setattr(tp, "_DOCX_IMPORT_CONTEXT", {"docx_formula_source_mode": "converted_docx_latex"})
    mp.setattr(tp, "extract_content_from_file", lambda *a, **k: {1: "x"})
    mp.setattr(tp, "_normalize_extracted_content_math", lambda content, *a, **k: content)
    mp.setattr(tp, "_normalize_parsed_textbook_math", lambda data, *a, **k: data)
    mp.setattr(tp, "call_gemini_for_analysis",
               lambda *a, **k: json.dumps({"chapters": [{"chapter_title": CHAPTER, "sections": []}]}))
    mp.setattr(tp, "scan_docx_title_inventory", lambda *a, **k: [dict(i) for i in items])
    mp.setattr(tp, "scan_general_high_layout", lambda *a, **k: scan)
    mp.setattr(tp, "scan_converted_docx_question_blocks", lambda *a, **k: {})
    mp.setattr(tp, "hydrate_converted_docx_latex_parsed_data", lambda data, **k: (data, 0, 0))
    mp.setattr(tp, "collect_returned_titles_from_parsed_data", lambda data: labels)
    mp.setattr(tp, "write_title_inventory_report", lambda *a, **k: None)
    if not regions:
        mp.setattr(review, "verified_visual_regions", lambda *a, **k: None)

    def fake_save(parsed_data, curriculum_info, q, import_policy=None, **kwargs):
        from core.general_textbook_replacement import replace_old_rows_in_session
        replacement = import_policy["general_replacement"]
        replace_old_rows_in_session(db.session, Model, replacement, curriculum_info, parsed_data)
        for row in env["new_rows"]:
            db.session.add(Model(**row))
        db.session.flush()
        return {"status": "success"}

    mp.setattr(tp, "save_to_database", fake_save)
    if fail_commit:
        real_commit = db.session.commit

        def boom():
            raise RuntimeError("simulated_commit_failure")
        mp.setattr(db.session, "commit", boom)
    q = queue_mod.Queue()
    result = tp.process_textbook_file(
        str(DOCX), {"curriculum": "general", "volume": VOLUME}, q, skip_code_gen=True,
        import_policy={"docx_primary": True, "pdf_optional_enrich": True,
                       "docx_formula_source_mode": "converted_docx_latex",
                       "general_replacement": env["policy"], "auto_stage1_review": True},
        optional_enrich_pdf_path=str(PDF),
    )
    return result, [str(m) for m in list(q.queue)]


def _chapter_rows(env):
    Model = env["model"]
    return Model.query.filter_by(source_curriculum="general", source_volume=VOLUME,
                                 source_chapter=CHAPTER).order_by(Model.id).all()


def _asset_files(root):
    return sorted(p for p in (root / "uploads").rglob("*") if p.is_file()) if (root / "uploads").exists() else []


def test_ready_branch_commits_verified_unit(env):
    other_before = _chapter_fingerprint(env["db_path"], where="source_chapter=?", args=(CHAPTER,), exclude=True)
    result, logs = _run(env)
    assert result["status"] == "success", result
    assert any("[STAGE1 GATE] status=READY rows=30 blocked=0 needs_review=0" in m for m in logs)
    env["db"].session.expire_all()
    rows = _chapter_rows(env)
    assert len(rows) == 30 and min(r.id for r in rows) >= 12744  # old printing replaced
    assert sum(r.skill_id == "gh_LogicAndSets" for r in rows) == 9
    assert sum(r.skill_id == "gh_CountingPrinciples" for r in rows) == 21
    assert all("MATH_PARSE_FAILED" not in (r.problem_text or "") + (r.detailed_solution or "") for r in rows)
    with_assets = [r for r in rows if json.loads(r.notes).get("image_assets")]
    assert [r.id for r in with_assets] == [12756, 12773]
    for r in with_assets:
        notes = json.loads(r.notes)
        assert notes["pdf_visual_status"] == "VISUAL_ATTACHED" and not notes.get("visual_required_missing")
        asset = notes["image_assets"][0]
        assert asset["source"] == "pdf" and asset["visual_classification"] == "required"
        published = env["root"] / asset["path"]
        assert published.is_file() and _sha(published) == asset["sha256"]
    assert len(_asset_files(env["root"])) == 2
    assert not any(json.loads(r.notes).get("pdf_visual_status") == "VISUAL_REQUIRED_MISSING" for r in rows)
    anchors = sorted(json.loads(r.notes)["question_anchor"]["source_order"] for r in rows)
    assert anchors == list(range(1, 31))
    assert any("[AUTO REVIEW] stage=stage1_gate status=ready" in m for m in logs)
    env["db"].session.commit()
    assert _chapter_fingerprint(env["db_path"], where="source_chapter=?", args=(CHAPTER,), exclude=True) == other_before


def test_needs_review_branch_rolls_back_and_leaves_no_assets(env):
    before = _chapter_fingerprint(env["db_path"])
    result, logs = _run(env, regions=False)
    assert result["status"] == "needs_review", result
    assert result["stage1_gate"]["status"] in ("NEEDS_REVIEW", "BLOCKED")
    assert result["stage1_auto_review"]["source"]["pdf_sha256"] == _sha(PDF)  # diagnostic retained for retry
    assert sorted(b["id"] for b in result["stage1_gate"]["blocked"]) == [12756, 12773]
    assert "required_figure_missing" in result["stage1_gate"]["reasons"]
    env["db"].session.expire_all()
    assert len(_chapter_rows(env)) == 20 and max(r.id for r in _chapter_rows(env)) < 12744
    assert _asset_files(env["root"]) == []
    assert _chapter_fingerprint(env["db_path"]) == before
    assert any("status=needs_review" in m for m in logs)
    assert DOCX.is_file() and PDF.is_file()


def test_commit_failure_rolls_back_rows_and_published_assets(env):
    before = _chapter_fingerprint(env["db_path"])
    result, _logs = _run(env, fail_commit=True)
    assert result["status"] == "error", result
    env["db"].session.expire_all()
    assert len(_chapter_rows(env)) == 20
    assert _asset_files(env["root"]) == []  # no orphan published crop
    assert _chapter_fingerprint(env["db_path"]) == before
    assert not [r for r in _chapter_rows(env) if r.id >= 12744]  # no orphan new rows


def test_retry_after_failed_run_does_not_duplicate(env):
    failed, _ = _run(env, regions=False)
    assert failed["status"] == "needs_review"
    env["monkeypatch"].undo()
    ok, _ = _run(env)
    assert ok["status"] == "success", ok
    env["db"].session.commit()
    env["db"].session.expire_all()
    rows = _chapter_rows(env)
    assert len(rows) == 30 and len({r.id for r in rows}) == 30
    assert len(_asset_files(env["root"])) == 2


# ------------------------------------------------------------------ job status: five distinguishable outcomes
def _job(lines, *, result=None, exc=None):
    from core.general_v1_import_status import GeneralV1ImportStatus
    st = GeneralV1ImportStatus("t")
    st.start([("u3.docx", "u3.pdf")])
    st.begin_pair("u3", 1)
    for line in lines:
        st.observe(line)
    st.finish_pair("u3", result, exc)
    st.finish()
    return st.snapshot()


_IMPORT = ["INFO: Import complete: skills=0, curriculums=0, examples=7, practices=23, in_class=12, "
           "chapter_exercises=11, self_assessment=0, exam=0, other=0, needs_review=0, skipped=0"]
_READY = ["INFO: [AUTO REVIEW] stage=auto_review status=running", "INFO: [AUTO REVIEW] stage=auto_review status=done changes=3",
          "INFO: [AUTO REVIEW] stage=ai_healing status=done items=0",
          'INFO: [STAGE1 GATE] status=READY rows=30 blocked=0 needs_review=0 reasons={}',
          "INFO: [AUTO REVIEW] stage=stage1_gate status=ready"]
_BLOCKED = _READY[:3] + ['INFO: [STAGE1 GATE] status=BLOCKED rows=30 blocked=2 needs_review=0 reasons={"required_figure_missing": 2}',
                         "WARN: [AUTO REVIEW] stage=stage1_gate status=needs_review; staged DB changes rolled back"]


def test_job_status_distinguishes_ready_review_and_failure():
    running = _job([], result=None, exc=None)  # no worker output at all is a failed job, never READY
    assert running["state"] == "failed" and running["result"]["stage1_ready"] is None

    ready = _job(_IMPORT + _READY, result={"status": "success"})
    assert ready["state"] == "completed" and ready["result"]["stage1_ready"] is True
    assert ready["stages"]["auto_review"] == ready["stages"]["ai_healing"] == ready["stages"]["stage1_gate"] == "done"
    assert ready["result"]["imported_questions"] == 30 and ready["result"]["staged_rolled_back"] is False

    review = _job(_IMPORT + _BLOCKED, result={"status": "needs_review"})
    assert review["state"] == "completed" and review["result"]["stage1_ready"] is False
    assert review["stages"]["stage1_gate"] == "failed"
    assert review["result"]["staged_rolled_back"] is True and not review["result"]["imported_questions"]
    assert review["result"]["pairs"][0]["status"] == "needs_review" and "待人工確認" in review["message"]

    failed = _job(_IMPORT + _READY[:2], exc=RuntimeError("boom\nTraceback"))
    assert failed["state"] == "failed" and failed["error"]["stage"] and failed["result"]["stage1_ready"] is None
