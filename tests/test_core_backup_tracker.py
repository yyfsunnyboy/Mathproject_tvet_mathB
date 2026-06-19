from __future__ import annotations

import uuid
from pathlib import Path

import pandas as pd
import pytest
from sqlalchemy import text

from app import create_app
from core.data_importer import import_excel_to_db
from models import SkillCurriculum, SkillInfo, TextbookExample, User, db


@pytest.fixture()
def app_ctx(tmp_path):
    import config as _cfg

    db_path = tmp_path / f"core_backup_tracker_{uuid.uuid4().hex[:8]}.db"
    prev_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            admin = User(username=f"admin_{uuid.uuid4().hex[:6]}", password_hash="x", role="admin")
            db.session.add(admin)
            db.session.commit()
            yield app, admin.id
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _seed_skill_example(skill_id="vh_tracker_skill", example_id: int | None = None) -> int:
    db.session.add(
        SkillInfo(
            skill_id=skill_id,
            skill_en_name=skill_id,
            skill_ch_name=skill_id,
            description="d",
            gemini_prompt="p",
        )
    )
    db.session.add(
        SkillCurriculum(
            skill_id=skill_id,
            curriculum="vocational",
            grade=10,
            volume="數學B1",
            chapter="1",
            section="1-1",
            paragraph="",
        )
    )
    ex = TextbookExample(
        skill_id=skill_id,
        source_curriculum="vocational",
        source_volume="數學B1",
        source_chapter="1",
        source_section="1-1",
        source_description="ex",
        problem_text="q",
        problem_type="short_answer",
        correct_answer="1",
        detailed_solution="s",
    )
    if example_id is not None:
        ex.id = example_id
    db.session.add(ex)
    db.session.commit()
    return int(ex.id)


def _insert_tracker(example_id: int, skill_id="vh_tracker_skill", row_id: int = 77, payload='{"a":1}') -> None:
    db.session.execute(
        text(
            """
            INSERT INTO gencode_component_tracker (
                id, textbook_example_id, skill_id, component_id, gencode_status,
                induced_spec_payload, gencode_error_log, created_at, updated_at
            ) VALUES (
                :id, :textbook_example_id, :skill_id, :component_id, 'verified',
                :payload, 'none', '2026-01-01 00:00:00', '2026-01-02 00:00:00'
            )
            """
        ),
        {
            "id": row_id,
            "textbook_example_id": example_id,
            "skill_id": skill_id,
            "component_id": f"src_{example_id}",
            "payload": payload,
        },
    )
    db.session.commit()


def _core_workbook(path: Path, *, include_tracker: bool, tracker_rows: list[dict] | None = None) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        pd.DataFrame(
            [{"skill_id": "vh_tracker_skill", "skill_en_name": "e", "skill_ch_name": "c", "description": "d", "gemini_prompt": "p"}]
        ).to_excel(writer, sheet_name="skills_info", index=False)
        pd.DataFrame(
            [{"skill_id": "vh_tracker_skill", "curriculum": "vocational", "grade": 10, "volume": "數學B1", "chapter": "1", "section": "1-1"}]
        ).to_excel(writer, sheet_name="skill_curriculum", index=False)
        pd.DataFrame(
            [{
                "id": 901,
                "skill_id": "vh_tracker_skill",
                "source_curriculum": "vocational",
                "source_volume": "數學B1",
                "source_chapter": "1",
                "source_section": "1-1",
                "source_description": "ex",
                "problem_text": "q",
                "problem_type": "short_answer",
                "correct_answer": "1",
                "detailed_solution": "s",
                "difficulty_level": 1,
            }]
        ).to_excel(writer, sheet_name="textbook_examples", index=False)
        pd.DataFrame().to_excel(writer, sheet_name="skill_family_bridge", index=False)
        pd.DataFrame().to_excel(writer, sheet_name="skill_prerequisites", index=False)
        if include_tracker:
            pd.DataFrame(tracker_rows or [{
                "id": 88,
                "textbook_example_id": 901,
                "skill_id": "vh_tracker_skill",
                "component_id": "src_901",
                "gencode_status": "verified",
                "induced_spec_payload": '{"payload":true}',
                "gencode_error_log": "none",
                "created_at": "2026-01-01 00:00:00",
                "updated_at": "2026-01-02 00:00:00",
            }]).to_excel(writer, sheet_name="gencode_component_tracker", index=False)


def test_tracker_exports_to_core_excel(app_ctx):
    app, admin_id = app_ctx
    with app.app_context():
        example_id = _seed_skill_example()
        _insert_tracker(example_id)
        client = app.test_client()
        _login(client, admin_id)
        response = client.post("/db_maintenance", data={"action": "export_db", "mode": "core"})
        assert response.status_code == 200
        sheets = pd.read_excel(response.data, sheet_name=None, engine="openpyxl")
        assert "gencode_component_tracker" in sheets
        row = sheets["gencode_component_tracker"].iloc[0].to_dict()
        assert int(row["id"]) == 77
        assert row["component_id"] == f"src_{example_id}"
        assert row["induced_spec_payload"] == '{"a":1}'


def test_tracker_import_preserves_id_component_payload(app_ctx, tmp_path):
    app, _ = app_ctx
    with app.app_context():
        path = tmp_path / "core_with_tracker.xlsx"
        _core_workbook(path, include_tracker=True)
        ok, message = import_excel_to_db(str(path), mode="core")
        assert ok, message
        row = db.session.execute(text("SELECT * FROM gencode_component_tracker WHERE id=88")).mappings().first()
        assert row["textbook_example_id"] == 901
        assert row["component_id"] == "src_901"
        assert row["induced_spec_payload"] == '{"payload":true}'


def test_legacy_five_sheet_excel_imports_with_tracker_warning(app_ctx, tmp_path):
    app, _ = app_ctx
    with app.app_context():
        path = tmp_path / "legacy_core.xlsx"
        _core_workbook(path, include_tracker=False)
        ok, message = import_excel_to_db(str(path), mode="core")
        assert ok, message
        assert "legacy core workbook has no gencode_component_tracker sheet" in message
        assert "final_status: completed_with_warnings" in message


def test_tracker_orphan_validation_fails_when_strict(app_ctx, tmp_path):
    app, _ = app_ctx
    with app.app_context():
        path = tmp_path / "orphan_tracker.xlsx"
        _core_workbook(
            path,
            include_tracker=True,
            tracker_rows=[{
                "id": 89,
                "textbook_example_id": 999999,
                "skill_id": "vh_tracker_skill",
                "component_id": "src_999999",
                "gencode_status": "verified",
            }],
        )
        ok, message = import_excel_to_db(str(path), mode="core", strict_mode=True)
        assert not ok
        assert "orphan gencode_component_tracker rows" in message


def test_core_restore_rolls_back_when_tracker_import_fails(app_ctx, tmp_path):
    app, _ = app_ctx
    with app.app_context():
        path = tmp_path / "bad_tracker.xlsx"
        _core_workbook(
            path,
            include_tracker=True,
            tracker_rows=[{
                "id": 90,
                "textbook_example_id": 901,
                "skill_id": "vh_tracker_skill",
                "component_id": "src_901",
                "gencode_status": "not_a_status",
            }],
        )
        ok, message = import_excel_to_db(str(path), mode="core")
        assert not ok
        assert "tracker_restore_failed" in message
        assert SkillInfo.query.filter_by(skill_id="vh_tracker_skill").count() == 0
