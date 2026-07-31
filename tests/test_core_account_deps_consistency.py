# -*- coding: utf-8 -*-
from __future__ import annotations

import io
import json
import shutil
import uuid
from pathlib import Path

import pandas as pd
import pytest
from sqlalchemy import text

from app import create_app
from core.backup.backup_registry import get_core_full_clear_table_names, get_core_table_names
from core.data_importer import FULL_CONFIRM_TOKEN, import_excel_to_db
from core.models.prompt_template import PromptTemplate
from core.routes.admin import CORE_CLEAR_CONFIRM_TOKEN, _hard_clear_vocational_math_b_core
from core.secret_policy import REDACTED_SECRET_VALUE
from models import (
    AdaptiveLearningLog,
    Class,
    ClassStudent,
    ExamAnalysis,
    LearningDiagnosis,
    MistakeLog,
    MistakeNotebookEntry,
    NodeCompetency,
    Progress,
    Question,
    QuizAttempt,
    SkillCurriculum,
    SkillInfo,
    StudentAbility,
    StudentUploadedQuestion,
    SystemSetting,
    TextbookExample,
    User,
    db,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_ROOT = PROJECT_ROOT / "reports" / "pytest_core_account_deps"


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


@pytest.fixture()
def app_ctx():
    import config as _cfg

    TEST_ROOT.mkdir(parents=True, exist_ok=True)
    run_dir = TEST_ROOT / uuid.uuid4().hex[:10]
    run_dir.mkdir(parents=True, exist_ok=True)
    db_path = run_dir / "account_deps.db"
    prev_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            admin = User(username=f"admin_{uuid.uuid4().hex[:6]}", password_hash="keep-hash-admin", role="admin")
            db.session.add(admin)
            db.session.commit()
            yield app, admin.id, run_dir
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri
        shutil.rmtree(run_dir, ignore_errors=True)


def _seed_full_account_graph() -> dict:
    teacher = User(id=501, username="teacher_ad", password_hash="hash-teacher-501", role="teacher")
    student = User(id=502, username="student_ad", password_hash="hash-student-502", role="student")
    db.session.add_all([teacher, student])
    db.session.flush()
    clazz = Class(id=701, name="甲班", teacher_id=501, class_code="ACCDEP01")
    db.session.add(clazz)
    db.session.flush()
    db.session.add(ClassStudent(id=801, class_id=701, student_id=502))

    sid = "vh_數學B1_AccountDepsSkill"
    db.session.add(
        SkillInfo(skill_id=sid, skill_en_name="e", skill_ch_name="c", description="d", gemini_prompt="p")
    )
    db.session.add(
        SkillCurriculum(
            skill_id=sid,
            curriculum="vocational",
            grade=10,
            volume="數學B1",
            chapter="1",
            section="1-1",
            paragraph="",
        )
    )
    db.session.add(
        TextbookExample(
            id=901,
            skill_id=sid,
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
    )
    q = Question(id=401, skill_id=sid, content={"prompt": "1+1?", "answer": "2"}, difficulty_level=1)
    db.session.add(q)
    db.session.flush()

    db.session.add(Progress(user_id=502, skill_id=sid, consecutive_correct=2, current_level=1, questions_solved=3))
    db.session.add(StudentAbility(user_id=502, skill_id=sid, ability_a=1.1, concept_u=1.0, calculation_c=0.9))
    db.session.add(QuizAttempt(id=601, user_id=502, question_id=401, user_answer="2", is_correct=True))
    db.session.add(
        AdaptiveLearningLog(
            log_id=701,
            student_id=502,
            session_id="s1",
            step_number=1,
            target_family_id="F1",
            target_subskills=json.dumps(["a"]),
            is_correct=True,
            current_apr=0.5,
            ppo_strategy=1,
        )
    )
    db.session.add(
        MistakeLog(
            user_id=502,
            skill_id=sid,
            question_content="q",
            user_answer="x",
            correct_answer="y",
        )
    )
    db.session.add(MistakeNotebookEntry(student_id=502, notes="n", skill_id=sid))
    db.session.add(
        ExamAnalysis(
            user_id=502,
            skill_id=sid,
            is_correct=True,
            image_path="p.png",
            student_answer_latex="1",
        )
    )
    db.session.add(StudentUploadedQuestion(student_id=502, ocr_content="ocr", status="pending"))
    db.session.add(NodeCompetency(user_id=502, node_id="n1", competency_score=50.0))
    db.session.add(
        LearningDiagnosis(
            student_id=502,
            radar_chart_data=json.dumps({"a": 1}),
            ai_comment="ok",
        )
    )
    setting = SystemSetting(key=f"keep_sys_{uuid.uuid4().hex[:6]}", value="keep")
    prompt = PromptTemplate(
        prompt_key=f"keep_p_{uuid.uuid4().hex[:6]}",
        title="t",
        category="c",
        content="x",
        default_content="x",
    )
    db.session.add_all([setting, prompt])
    db.session.commit()

    counts = {
        "users": User.query.count(),
        "classes": Class.query.count(),
        "class_students": ClassStudent.query.count(),
        "progress": Progress.query.count(),
        "student_abilities": StudentAbility.query.count(),
        "questions": Question.query.count(),
        "quiz_attempts": QuizAttempt.query.count(),
        "adaptive_learning_logs": AdaptiveLearningLog.query.count(),
        "mistake_logs": MistakeLog.query.count(),
        "mistake_notebook_entries": MistakeNotebookEntry.query.count(),
        "exam_analysis": ExamAnalysis.query.count(),
        "student_uploaded_questions": StudentUploadedQuestion.query.count(),
        "node_competency": NodeCompetency.query.count(),
        "learning_diagnosis": LearningDiagnosis.query.count(),
        "skills_info": SkillInfo.query.filter_by(skill_id=sid).count(),
    }
    return {
        "skill_id": sid,
        "counts": counts,
        "setting_key": setting.key,
        "prompt_key": prompt.prompt_key,
        "settings_before": SystemSetting.query.count(),
        "prompts_before": PromptTemplate.query.count(),
    }


def _legacy_core_workbook(path: Path) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        pd.DataFrame(
            [{"skill_id": "vh_數學B1_LegacyOnly", "skill_en_name": "e", "skill_ch_name": "c", "description": "d", "gemini_prompt": "p"}]
        ).to_excel(writer, sheet_name="skills_info", index=False)
        pd.DataFrame(
            [{"skill_id": "vh_數學B1_LegacyOnly", "curriculum": "vocational", "grade": 10, "volume": "數學B1", "chapter": "1", "section": "1-1"}]
        ).to_excel(writer, sheet_name="skill_curriculum", index=False)
        pd.DataFrame(
            [{
                "id": 911,
                "skill_id": "vh_數學B1_LegacyOnly",
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


def test_core_export_contains_all_account_dependent_sheets(app_ctx):
    app, admin_id, _ = app_ctx
    with app.app_context():
        _seed_full_account_graph()
        client = app.test_client()
        _login(client, admin_id)
        response = client.post("/db_maintenance", data={"action": "export_db", "mode": "core"})
        assert response.status_code == 200
        sheets = pd.read_excel(io.BytesIO(response.data), sheet_name=None, engine="openpyxl")
        for name in get_core_table_names(include="export"):
            assert name in sheets, name
        assert list(sheets.keys()) == get_core_table_names(include="export")
        hashes = set(sheets["users"]["password_hash"].astype(str).tolist())
        assert "hash-teacher-501" in hashes
        assert REDACTED_SECRET_VALUE not in hashes


def test_core_round_trip_counts_and_fk_clean(app_ctx):
    app, admin_id, run_dir = app_ctx
    with app.app_context():
        seeded = _seed_full_account_graph()
        client = app.test_client()
        _login(client, admin_id)
        response = client.post("/db_maintenance", data={"action": "export_db", "mode": "core"})
        path = run_dir / "roundtrip.xlsx"
        path.write_bytes(response.data)

        # Wipe learning + roster then restore from workbook.
        for table in get_core_full_clear_table_names():
            db.session.execute(text(f'DELETE FROM "{table}"'))
        db.session.commit()
        assert User.query.count() == 0

        ok, message = import_excel_to_db(str(path), mode="core")
        assert ok, message
        assert "PRAGMA foreign_key_check violations: 0" in message
        assert "account_orphan_total: 0" in message
        for table, before in seeded["counts"].items():
            if table == "users":
                # admin was wiped; restored workbook has teacher+student (+maybe admin from export)
                assert User.query.count() >= 2
            elif table == "skills_info":
                assert SkillInfo.query.filter_by(skill_id=seeded["skill_id"]).count() == before
            else:
                model_count = {
                    "classes": Class,
                    "class_students": ClassStudent,
                    "progress": Progress,
                    "student_abilities": StudentAbility,
                    "questions": Question,
                    "quiz_attempts": QuizAttempt,
                    "adaptive_learning_logs": AdaptiveLearningLog,
                    "mistake_logs": MistakeLog,
                    "mistake_notebook_entries": MistakeNotebookEntry,
                    "exam_analysis": ExamAnalysis,
                    "student_uploaded_questions": StudentUploadedQuestion,
                    "node_competency": NodeCompetency,
                    "learning_diagnosis": LearningDiagnosis,
                }[table].query.count()
                assert model_count == before, (table, model_count, before)
        teacher = User.query.filter_by(id=501).first()
        assert teacher is not None
        assert teacher.password_hash == "hash-teacher-501"


def test_delete_core_student_scoped_keeps_admin_teacher_and_settings(app_ctx):
    app, admin_id, _ = app_ctx
    with app.app_context():
        seeded = _seed_full_account_graph()
        preview = _hard_clear_vocational_math_b_core(execute=False)
        plan = preview["plan"]
        account_names = get_core_full_clear_table_names()
        for name in account_names:
            assert name in plan
        assert plan.index("class_students") < plan.index("classes") < plan.index("users")
        wheres = {item["table"]: item["where"] for item in preview["account_clear"]}
        assert wheres["users"] == "role = 'student'"

        before_admin = User.query.filter_by(role="admin").count()
        before_teacher = User.query.filter_by(role="teacher").count()
        _hard_clear_vocational_math_b_core(execute=True)
        assert User.query.filter_by(role="student").count() == 0
        assert User.query.filter_by(role="admin").count() == before_admin
        assert User.query.filter_by(role="teacher").count() == before_teacher
        assert Class.query.count() == 0
        assert ClassStudent.query.count() == 0
        assert Progress.query.count() == 0
        assert QuizAttempt.query.count() == 0
        assert SystemSetting.query.count() == seeded["settings_before"]
        assert PromptTemplate.query.count() == seeded["prompts_before"]
        assert SystemSetting.query.filter_by(key=seeded["setting_key"]).count() == 1
        db.session.execute(text("PRAGMA foreign_keys = ON"))
        fk_rows = db.session.execute(text("PRAGMA foreign_key_check")).fetchall()
        assert fk_rows == []


def test_legacy_core_workbook_still_imports(app_ctx):
    app, _, run_dir = app_ctx
    with app.app_context():
        path = run_dir / "legacy.xlsx"
        _legacy_core_workbook(path)
        ok, message = import_excel_to_db(str(path), mode="core")
        assert ok, message
        assert SkillInfo.query.filter_by(skill_id="vh_數學B1_LegacyOnly").count() == 1
        assert "optional core sheet missing" in message


def test_full_mode_confirm_and_secret_redact(app_ctx):
    app, admin_id, run_dir = app_ctx
    with app.app_context():
        _seed_full_account_graph()
        db.session.add(SystemSetting(key="ai_gemini_api_key", value="AIzaShouldNeverExportPlain"))
        db.session.commit()
        path = run_dir / "full.xlsx"
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            pd.DataFrame([{"skill_id": "vh_數學B1_Full", "skill_en_name": "e", "skill_ch_name": "c", "description": "d", "gemini_prompt": "p"}]).to_excel(
                writer, sheet_name="skills_info", index=False
            )
        ok, message = import_excel_to_db(str(path), mode="full", confirm_full_clear="")
        assert not ok
        assert "YES_DELETE_ALL" in message
        ok2, message2 = import_excel_to_db(str(path), mode="full", confirm_full_clear=FULL_CONFIRM_TOKEN)
        assert ok2, message2

        client = app.test_client()
        _login(client, admin_id)
        response = client.post("/db_maintenance", data={"action": "export_db", "mode": "full"})
        assert response.status_code == 200
        sheets = pd.read_excel(io.BytesIO(response.data), sheet_name=None, engine="openpyxl")
        assert "system_settings" in sheets
        assert len(sheets) > len(get_core_table_names())
        secret_row = sheets["system_settings"][sheets["system_settings"]["key"].astype(str) == "ai_gemini_api_key"].iloc[0]
        assert secret_row["value"] == REDACTED_SECRET_VALUE


def test_template_mentions_learning_records():
    text_out = (PROJECT_ROOT / "templates" / "db_maintenance.html").read_text(encoding="utf-8")
    assert "學習紀錄" in text_out
    assert "全部國中、普通高中及高職教材資料" in text_out
    assert "管理員、教師帳號、system_settings、prompt_templates 將保留" in text_out
    assert "system_settings" in text_out
    assert "prompt_templates" in text_out
