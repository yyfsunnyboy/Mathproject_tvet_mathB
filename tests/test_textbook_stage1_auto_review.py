"""Unit 3 source-backed regression in an isolated SQLite copy."""
import json
import sqlite3
from pathlib import Path
from types import SimpleNamespace

import pytest

from core.textbook_stage1_auto_review import review_and_heal_rows, verified_visual_regions
from core.textbook_stage1_gate import evaluate_stage1_gate
from core.textbook_pdf_visual import enrich_textbook_examples_with_pdf_visuals
from core.textbook_processor import find_general_high_source_skill_map

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "reports/gh_math2_unit3_stage1/production_change_set.json"
SOURCE = ROOT / "textbook_import/uploaded_sources/general/數學2"
DOCX = SOURCE / "cd38c1890caf_單元03-計數原理.docx"
PDF = SOURCE / "fe5ce0b620d3_單元03-計數原理.pdf"


@pytest.fixture
def old_unit3_copy(tmp_path):
    if not (CASE.is_file() and DOCX.is_file() and PDF.is_file()):
        pytest.skip("authoritative Unit 3 source/record unavailable on this checkout")
    src = ROOT / "instance/kumon_math.db"
    if not src.is_file():
        pytest.skip("local formal DB unavailable; isolated source fixture required")
    target = tmp_path / "unit3_before.db"
    with sqlite3.connect(f"file:{src.as_posix()}?mode=ro", uri=True) as before:
        with sqlite3.connect(target) as copy:
            before.backup(copy)
    changes = json.loads(CASE.read_text(encoding="utf-8"))
    db = sqlite3.connect(target)
    db.row_factory = sqlite3.Row
    for op in changes["updates"]:
        before = op["before"]
        db.execute("update textbook_examples set problem_text=?,detailed_solution=?,skill_id=?,notes=? where id=?",
                   (before["problem_text"], before["detailed_solution"], before["skill_id"], before["notes"], op["id"]))
    for row in changes["old_rows"]:
        cols = list(row)
        db.execute(f"insert into textbook_examples ({','.join(cols)}) values ({','.join('?' for _ in cols)})",
                   [row[k] for k in cols])
    db.commit()
    yield db
    db.close()


def _rows(db):
    return [SimpleNamespace(**dict(row)) for row in db.execute(
        "select * from textbook_examples where source_curriculum='general' and source_volume='數學2' "
        "and source_chapter='單元3 計數原理' order by id"
    )]


def test_unit3_review_replay_in_db_copy(old_unit3_copy, tmp_path):
    rows = _rows(old_unit3_copy)
    assert len(rows) == 50  # old version must prevent READY
    source_map = find_general_high_source_skill_map("general", "數學2", "單元3 計數原理")
    assert source_map and len(source_map["titles"]) == 30
    rows = [r for r in rows if r.id >= 12744]
    for row in rows:
        label = row.source_description.split(" [", 1)[0]
        row.skill_id = source_map["titles"][label]
    regions = verified_visual_regions(PDF, curriculum="general", volume="數學2", chapter="單元3 計數原理")
    assert regions is not None
    enrich_textbook_examples_with_pdf_visuals(
        pdf_path=PDF, examples=rows,
        curriculum_info={"curriculum": "general", "volume": "數學2", "chapter": "單元3 計數原理",
                         "section": "3.計數原理", "publisher": "longteng"},
        project_root=tmp_path, write_notes=True, publish_assets=False,
        assemble_visual_groups=True, region_overrides=regions,
    )
    result = review_and_heal_rows(
        rows, docx_path=DOCX, pdf_path=PDF, expected_count=30,
        allowed_skills={"gh_LogicAndSets": "甲.邏輯與集合", "gh_CountingPrinciples": "乙.計數原理"},
        ai_review=lambda *_: pytest.fail("teacher-confirmed source map should avoid AI"),
        asset_roots=[tmp_path],
    )
    assert result["gate"]["status"] == "READY", (result["gate"]["blocked"], result["gate"]["needs_review"])
    assert result["heal_passes"] == 1
    assert sum(r.skill_id == "gh_LogicAndSets" for r in rows) == 9
    assert all("MATH_PARSE_FAILED" not in r.problem_text + (r.detailed_solution or "") for r in rows)
    assets = [r.id for r in rows if json.loads(r.notes).get("image_assets")]
    assert assets == [12756, 12773]
    assert evaluate_stage1_gate([vars(r) for r in rows])["status"] == "READY"


def _enriched_rows(db, tmp_path):
    source_map = find_general_high_source_skill_map("general", "數學2", "單元3 計數原理")
    rows = [r for r in _rows(db) if r.id >= 12744]
    for row in rows:
        row.skill_id = source_map["titles"][row.source_description.split(" [", 1)[0]]
    enrich_textbook_examples_with_pdf_visuals(
        pdf_path=PDF, examples=rows,
        curriculum_info={"curriculum": "general", "volume": "數學2", "chapter": "單元3 計數原理",
                         "section": "3.計數原理", "publisher": "longteng"},
        project_root=tmp_path, write_notes=True, publish_assets=False, assemble_visual_groups=True,
        region_overrides=verified_visual_regions(PDF, curriculum="general", volume="數學2",
                                                 chapter="單元3 計數原理"),
    )
    return rows


def _stale_blocked_ids(db, tmp_path, mutate):
    rows = _enriched_rows(db, tmp_path)
    target = next(r for r in rows if r.id == 12756)
    notes = json.loads(target.notes)
    mutate(notes, tmp_path)
    notes["pdf_visual_status"] = "VISUAL_REQUIRED_MISSING"
    target.notes = json.dumps(notes, ensure_ascii=False)
    result = review_and_heal_rows(
        rows, docx_path=DOCX, pdf_path=PDF, expected_count=30,
        allowed_skills={"gh_LogicAndSets": "甲", "gh_CountingPrinciples": "乙"},
        ai_review=lambda *_: [], asset_roots=[tmp_path],
    )
    return result, json.loads(target.notes)


def _set(**values):
    return lambda notes, _root: notes["image_assets"][0].update(values)


def _delete_file(notes, root):
    (root / notes["image_assets"][0]["path"]).unlink()


def _corrupt_file(notes, root):
    (root / notes["image_assets"][0]["path"]).write_bytes(b"not the recorded crop")


@pytest.mark.parametrize("mutate", [
    _set(visual_classification="decorative"),
    _set(visual_classification="solution_only"),
    _set(source="docx"),
    _set(question_anchor="general_2_other_question"),
    _set(source_page=1),
    _set(needs_crop_review=True),
    _delete_file,
    _corrupt_file,
], ids=["decorative", "solution", "not_pdf", "foreign_anchor", "wrong_page", "crop_review", "missing_file", "bad_hash"])
def test_stale_missing_figure_is_never_cleared_without_proof(old_unit3_copy, tmp_path, mutate):
    result, notes = _stale_blocked_ids(old_unit3_copy, tmp_path, mutate)
    assert result["gate"]["status"] != "READY"
    assert notes["pdf_visual_status"] == "VISUAL_REQUIRED_MISSING"
    assert not any(c["kind"] == "verified_visual_attached" and c["id"] == 12756 for c in result["changes"])


def test_unauthorized_old_printing_is_reported_never_healed_or_ready(old_unit3_copy, tmp_path):
    rows = _enriched_rows(old_unit3_copy, tmp_path) + [r for r in _rows(old_unit3_copy) if r.id < 12744]
    old_before = [(r.id, r.problem_text, r.notes, r.skill_id) for r in rows if r.id < 12744]
    result = review_and_heal_rows(
        rows, docx_path=DOCX, pdf_path=PDF, expected_count=30,
        allowed_skills={"gh_LogicAndSets": "甲", "gh_CountingPrinciples": "乙"},
        ai_review=lambda *_: [], asset_roots=[tmp_path],
    )
    stale = next(i for i in result["issues"] if i["reason"] == "stale_rows_require_manual_cleanup")
    assert stale["ids"] == list(range(1362, 1382)) and result["gate"]["status"] == "BLOCKED"
    assert [(r.id, r.problem_text, r.notes, r.skill_id) for r in rows if r.id < 12744] == old_before


def test_review_history_is_idempotent_for_the_same_source():
    from core.textbook_stage1_auto_review import _record
    notes = {}
    for before in ("a", "b"):  # same transition re-detected on re-import with different incidental text
        _record(notes, kind="student_drawn_visual", before=before, after="c", source_hash="h", confidence=1.0)
    assert len(notes["stage1_auto_review"]) == 1
    for before in ("x", "y"):  # distinct original texts must both be kept
        _record(notes, kind="source_symbol", before=before, after="c", source_hash="h", confidence=1.0)
    assert len(notes["stage1_auto_review"]) == 3


def test_ai_advice_cannot_apply_unverified_skill(old_unit3_copy):
    rows = [r for r in _rows(old_unit3_copy) if r.id >= 12744]
    row = next(r for r in rows if r.id == 12766)
    notes = json.loads(row.notes)
    notes["skill_binding"] = {"source": "unmapped_in_source_skill_map"}
    row.notes = json.dumps(notes, ensure_ascii=False)
    result = review_and_heal_rows(
        rows, docx_path=DOCX, pdf_path=PDF, expected_count=30,
        allowed_skills={"gh_LogicAndSets": "甲.邏輯與集合"},
        ai_review=lambda *_: [{"id": 12766, "skill_id": "gh_LogicAndSets", "confidence": 1,
                               "evidence": "invented evidence"}],
    )
    assert row.skill_id == "gh_CountingPrinciples"
    assert any(x.get("reason") == "skill_binding_requires_human_review" for x in result["issues"])
    assert result["gate"]["status"] == "BLOCKED"
