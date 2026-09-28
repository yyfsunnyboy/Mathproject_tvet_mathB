# -*- coding: utf-8 -*-
"""Phase4 gate for B3 3-2 source-authored plain headings. Writes only a DB copy."""

import hashlib
import json
import sqlite3
from pathlib import Path

import pytest

from core.mathb_plain_source_heading import (
    B3_SECTION_3_2_EXAMPLE_COUNTS,
    classify_question_visual_dependency,
    provenance_payload,
    stamp_plain_heading_question_bindings,
)

ROOT = Path(__file__).resolve().parents[1]
PRODUCTION_DB = ROOT / "instance" / "kumon_math.db"


def test_provenance_does_not_invent_a_printed_concept_code():
    payload = provenance_payload(
        {
            "source_heading_text": "1. 二元一次不等式的定義",
            "source_order": 6,
            "source_page_start": 1,
            "source_heading_number": 1,
            "internal_coordinate": "3-2#1",
            "formal_skill_id": "vh_數學B3_PlainHeading_3_2_1",
            "concept_name": "二元一次不等式的定義",
        }
    )
    encoded = json.dumps(payload, ensure_ascii=False)
    assert payload["printed_concept_code"] is None
    assert payload["source_concept_code"] is None
    assert payload["authority_source"] == "source_authored_plain_heading"
    assert payload["internal_coordinate"] == "3-2#1"
    assert "3-2.1" not in encoded
    assert "SubSection_3_2" not in encoded


def test_question_binding_stamp_keeps_the_assigned_skill():
    blocks = {"例1": {}}
    stamp_plain_heading_question_bindings(
        blocks,
        [
            {
                "title": "例1",
                "assigned": True,
                "formal_skill_id": "vh_數學B3_PlainHeading_3_2_3",
                "concept_name": "邊界、半平面",
                "source_heading_number": 3,
                "internal_coordinate": "3-2#3",
            }
        ],
    )
    assert blocks["例1"]["formal_skill_id"] == "vh_數學B3_PlainHeading_3_2_3"
    assert blocks["例1"]["concept_code"] == ""
    assert blocks["例1"]["internal_coordinate"] == "3-2#3"


def test_visual_dependency_inventory_classes():
    assert classify_question_visual_dependency("圖示下列二元一次不等式的解")["visual_dependency"] == "DETERMINISTIC_VISUAL"
    assert classify_question_visual_dependency("將不等式解的半平面塗上顏色或畫斜線")["visual_dependency"] == "DETERMINISTIC_VISUAL"
    assert classify_question_visual_dependency("寫出滿足下列圖示之不等式")["visual_dependency"] == "VISUAL_REQUIRED"
    assert classify_question_visual_dependency("試寫出滿足鋪色區域的不等式")["visual_dependency"] == "VISUAL_REQUIRED"
    assert classify_question_visual_dependency("如圖，寫出滿足圖示之不等式")["visual_dependency"] == "VISUAL_REQUIRED"
    assert classify_question_visual_dependency("如下圖所示，景點分別位在哪一區")["visual_dependency"] == "TEXT_RECOVERABLE"
    assert classify_question_visual_dependency("兩點位於直線的同側，試求實數k的範圍")["visual_dependency"] == "TEXT_ONLY"
    assert classify_question_visual_dependency("每餐攝取量不能超過")["visual_dependency"] == "TEXT_ONLY"


def _copy_database(destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    source = sqlite3.connect(f"file:{PRODUCTION_DB.as_posix()}?mode=ro", uri=True)
    target = sqlite3.connect(destination)
    try:
        source.backup(target)
    finally:
        target.close()
        source.close()


@pytest.mark.skipif(not PRODUCTION_DB.is_file(), reason="production database is not available to copy")
def test_b3_3_2_phase4_copy_creates_four_skills_and_is_idempotent(tmp_path):
    before = hashlib.sha256(PRODUCTION_DB.read_bytes()).hexdigest()
    project = tmp_path / "project"
    db_path = project / "instance" / "kumon_math.db"
    _copy_database(db_path)
    db_uri = "sqlite:///" + str(db_path.resolve()).replace("\\", "/")

    import config

    config.Config.SQLALCHEMY_DATABASE_URI = db_uri
    from app import create_app
    from core.textbook_importer_v3_pipeline import run_v3_pair_pipeline

    app = create_app()
    app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI=db_uri)
    source = ROOT / "textbook_import" / "source" / "vocational" / "math_B3"
    docx = next(path for path in source.glob("*.docx") if "3-2" in path.name and "_Latex" not in path.name)
    pdf = next(path for path in source.glob("*.pdf") if "3-2" in path.name)

    def run_once(*, insert_missing_only: bool):
        return run_v3_pair_pipeline(
            project_root=project,
            docx_path=docx,
            pdf_path=pdf,
            curriculum="vocational",
            volume="數學B3",
            allow_phase4=True,
            insert_missing_only=insert_missing_only,
            emit_stream_end=False,
            app=app,
        )

    with app.app_context():
        first = run_once(insert_missing_only=False)
        second = run_v3_pair_pipeline(
            project_root=project,
            docx_path=docx,
            pdf_path=pdf,
            curriculum="vocational",
            volume="數學B3",
            allow_phase4=True,
            insert_missing_only=True,
            target_source_types={
                "textbook_example",
                "in_class_practice",
                "textbook_exercise",
                "advanced_exercise",
                "exam_practice",
            },
            emit_stream_end=False,
            app=app,
        )
        _assert_copy_acceptance(app, first, second, project)
    after = hashlib.sha256(PRODUCTION_DB.read_bytes()).hexdigest()
    assert before == after


def _assert_copy_acceptance(app, first, second, project: Path) -> None:
    from models import SkillCurriculum, SkillInfo, SystemSetting, TextbookExample, User, db
    from core.adaptive_engine import recommend_question, select_review_skill
    from core.gencode.services.gencode_status_query_service import build_admin_skills_gencode_status_map
    from core.mathb_plain_source_heading import classify_question_visual_dependency, provenance_setting_key
    from core.routes.practice import _select_textbook_example_for_skill
    from core.textbook_importer_v3_pipeline import build_v3_ui_result_payload

    assert first.get("ok") is True, first.get("error")
    assert second.get("ok") is True, second.get("error")
    binding = first["metrics"]["curriculum_binding"]
    db_write = first["metrics"]["db_write"]
    assert binding["formal_skills_created"] == 4
    assert binding["formal_skills_reused"] == 0
    assert int(db_write["inserted"]) == 21
    assert int(db_write["updated"]) == 0
    assert first["metrics"]["ai_alignment"]["gemini_requests"] == 0

    second_binding = second["metrics"]["curriculum_binding"]
    second_write = second["metrics"]["db_write"]
    assert second_binding["formal_skills_created"] == 0
    assert second_binding["formal_skills_reused"] == 4
    assert int(second_write["inserted"]) == 0
    assert int(second_write.get("existing_skipped") or 0) == 21
    ui = build_v3_ui_result_payload({"pairs": [second]})
    assert ui["resultCode"] == "already_up_to_date"

    skill_ids = list(B3_SECTION_3_2_EXAMPLE_COUNTS)
    infos = SkillInfo.query.filter(SkillInfo.skill_id.in_(skill_ids)).all()
    curricula = SkillCurriculum.query.filter(SkillCurriculum.skill_id.in_(skill_ids)).all()
    assert len(infos) == 4
    assert len(curricula) == 4
    rows = TextbookExample.query.filter_by(
        source_curriculum="vocational",
        source_volume="數學B3",
        source_chapter="第3章 二元一次不等式及其應用",
        source_section="3-2 二元一次不等式",
    ).all()
    assert len(rows) == 21
    counts = {skill_id: 0 for skill_id in skill_ids}
    descriptions = []
    inventory = []
    for row in rows:
        assert row.skill_id in counts
        assert not str(row.skill_id).startswith("outline_")
        assert "SubSection_3_2" not in str(row.skill_id)
        counts[row.skill_id] += 1
        descriptions.append(row.source_description)
        notes = json.loads(row.notes or "{}")
        provenance = notes.get("plain_source_heading") or {}
        assert provenance.get("printed_concept_code") is None
        assert "3-2.1" not in json.dumps(provenance, ensure_ascii=False)
        visual = classify_question_visual_dependency(row.problem_text)
        inventory.append(
            {
                "source_id": row.id,
                "source_description": row.source_description,
                "skill_id": row.skill_id,
                "problem_text": row.problem_text,
                **visual,
            }
        )
    assert counts == B3_SECTION_3_2_EXAMPLE_COUNTS
    assert len(descriptions) == len(set(descriptions))
    assert all(str(row.problem_text or "").strip() for row in rows)

    for skill_id, info in zip(skill_ids, sorted(infos, key=lambda item: item.skill_id)):
        setting = SystemSetting.query.filter_by(key=provenance_setting_key(info.skill_id)).one()
        payload = json.loads(setting.value)
        assert payload["authority_source"] == "source_authored_plain_heading"
        assert payload["printed_concept_code"] is None
        assert payload["source_concept_code"] is None
        assert payload["internal_coordinate"].startswith("3-2#")
        assert "3-2.1" not in setting.value
        _ = skill_id

    empty_id = "vh_數學B3_PlainHeading_3_2_1"
    assert TextbookExample.query.filter_by(skill_id=empty_id).count() == 0
    listed = (
        db.session.query(SkillInfo, SkillCurriculum)
        .join(SkillCurriculum, SkillInfo.skill_id == SkillCurriculum.skill_id)
        .filter(SkillInfo.skill_id == empty_id)
        .all()
    )
    assert len(listed) == 1
    assert select_review_skill(
        [empty_id],
        {empty_id: {"attempts": 0, "correct": 0, "wrong": 0, "fail_streak": 0}},
        "",
    ) == empty_id
    user_id = User.query.order_by(User.id.asc()).first().id
    assert recommend_question(user_id, [empty_id]) is None
    with app.test_request_context():
        assert _select_textbook_example_for_skill(empty_id) is None
    raw = db.engine.raw_connection()
    try:
        status_map = build_admin_skills_gencode_status_map(raw, [empty_id], project_root=ROOT)
    finally:
        raw.close()
    encoded_status = json.dumps(status_map, ensure_ascii=False, default=str)
    assert "PACKAGE_READY" not in encoded_status

    report = {
        "first": {
            "created": binding["formal_skills_created"],
            "reused": binding["formal_skills_reused"],
            "db_write": {key: db_write.get(key) for key in ("inserted", "updated", "skipped", "existing_skipped", "parsed_questions")},
            "gemini_requests": first["metrics"]["ai_alignment"]["gemini_requests"],
        },
        "second": {
            "created": second_binding["formal_skills_created"],
            "reused": second_binding["formal_skills_reused"],
            "db_write": {key: second_write.get(key) for key in ("inserted", "updated", "skipped", "existing_skipped")},
            "result_code": ui["resultCode"],
        },
        "distribution": counts,
        "inventory": inventory,
        "empty_skill_status": encoded_status,
    }
    out = ROOT / "scratch" / "_b3_32_phase4_acceptance.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    _ = project
