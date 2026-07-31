# -*- coding: utf-8 -*-
"""DELETE_CORE wipes ALL curriculum data (junior_high + general + vocational)."""
from __future__ import annotations

import shutil
import uuid
from pathlib import Path

import pytest
from sqlalchemy import text

from app import create_app
from core.backup.backup_registry import CORE_TEXTBOOK_FULL_CLEAR_TABLES
from core.models.prompt_template import PromptTemplate
from core.routes.admin import (
    CORE_CLEAR_CONFIRM_TOKEN,
    _core_textbook_remaining_check,
    _hard_clear_core_data,
)
from models import (
    Class,
    ClassStudent,
    Progress,
    SkillCurriculum,
    SkillFamilyBridge,
    SkillInfo,
    SkillPrerequisites,
    SystemSetting,
    TextbookExample,
    User,
    db,
    init_db,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_ROOT = PROJECT_ROOT / "reports" / "pytest_delete_core_all_curriculum"


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
    db_path = run_dir / "delete_core_all.db"
    prev_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            admin = User(username=f"admin_{uuid.uuid4().hex[:6]}", password_hash="x", role="admin")
            db.session.add(admin)
            db.session.commit()
            yield app, admin.id, run_dir, db_path
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri
        shutil.rmtree(run_dir, ignore_errors=True)


def _add_skill(sid: str, en: str, ch: str) -> None:
    db.session.add(
        SkillInfo(
            skill_id=sid,
            skill_en_name=en,
            skill_ch_name=ch,
            description="d",
            gemini_prompt="p",
        )
    )


def _seed_all_curricula() -> dict:
    jh = "jh_數學1上_FourArithmeticOperationsOfIntegers"
    gh = "gh_BinomialTheorem"
    vh = "vh_數學B1_SlopeOfALine"

    _add_skill(jh, "Integers", "整數")
    _add_skill(gh, "Binomial", "二項")
    _add_skill(vh, "Slope", "斜率")
    db.session.flush()

    db.session.add_all(
        [
            SkillCurriculum(
                skill_id=jh, curriculum="junior_high", grade=7, volume="數學1上",
                chapter="1", section="1-1", paragraph="",
            ),
            SkillCurriculum(
                skill_id=gh, curriculum="general", grade=10, volume="數學1",
                chapter="1", section="1-1", paragraph="",
            ),
            SkillCurriculum(
                skill_id=vh, curriculum="vocational", grade=10, volume="數學B1",
                chapter="1", section="1-1", paragraph="",
            ),
        ]
    )
    jh_ex = TextbookExample(
        skill_id=jh, source_curriculum="junior_high", source_volume="數學1上",
        source_chapter="1", source_section="1-1", source_description="jh",
        problem_text="1+1", problem_type="short_answer", correct_answer="2", detailed_solution="s",
    )
    gh_ex = TextbookExample(
        skill_id=gh, source_curriculum="general", source_volume="數學1",
        source_chapter="1", source_section="1-1", source_description="gh",
        problem_text="C", problem_type="short_answer", correct_answer="1", detailed_solution="s",
    )
    vh_ex = TextbookExample(
        skill_id=vh, source_curriculum="vocational", source_volume="數學B1",
        source_chapter="1", source_section="1-1", source_description="vh",
        problem_text="m", problem_type="short_answer", correct_answer="1", detailed_solution="s",
    )
    db.session.add_all([jh_ex, gh_ex, vh_ex])
    db.session.flush()

    db.session.add(SkillPrerequisites(skill_id=vh, prerequisite_id=jh))
    db.session.add(
        SkillFamilyBridge(
            skill_id=jh, family_id="I1", skill_name="整數", skill_ch_name="整數",
            skill_en_name="Integers", family_name="int_ops", theme="t",
            subskill_nodes='["a"]', notes="jh", curriculum="junior_high", grade=7,
            volume="數學1上", chapter="1", section="1-1", paragraph="",
            hint_scope="a", version=1, source="test_seed",
        )
    )
    db.session.add(
        SkillFamilyBridge(
            skill_id=gh, family_id="G1", skill_name="二項", skill_ch_name="二項",
            skill_en_name="Binomial", family_name="bin", theme="t",
            subskill_nodes='["a"]', notes="gh", curriculum="general", grade=10,
            volume="數學1", chapter="1", section="1-1", paragraph="",
            hint_scope="a", version=1, source="test_seed",
        )
    )

    teacher = User(id=501, username="teacher_keep", password_hash="h", role="teacher")
    student = User(id=502, username="student_drop", password_hash="h", role="student")
    db.session.add_all([teacher, student])
    db.session.flush()
    db.session.add(Progress(user_id=501, skill_id=jh, consecutive_correct=1, questions_solved=1))
    db.session.add(Progress(user_id=502, skill_id=vh, consecutive_correct=2, questions_solved=2))
    db.session.add(Class(id=701, name="甲班", teacher_id=501, class_code="ALLCLR01"))
    db.session.flush()
    db.session.add(ClassStudent(id=801, class_id=701, student_id=502))

    setting = SystemSetting(key=f"keep_sys_{uuid.uuid4().hex[:6]}", value="keep")
    prompt = PromptTemplate(
        prompt_key=f"keep_p_{uuid.uuid4().hex[:6]}",
        title="t", category="c", content="x", default_content="x",
    )
    db.session.add_all([setting, prompt])
    db.session.commit()

    # questions row (if table exists)
    if "questions" in set(db.inspect(db.engine).get_table_names()):
        db.session.execute(
            text("INSERT INTO questions (skill_id, content) VALUES (:sid, 'q')"),
            {"sid": vh},
        )
        db.session.commit()

    db.session.execute(
        text(
            """
            INSERT INTO gencode_component_tracker
                (textbook_example_id, skill_id, component_id, gencode_status, induced_spec_payload)
            VALUES
                (:jh_ex, :jh, 'c_jh', 'usable', '{}'),
                (:vh_ex, :vh, 'c_vh', 'usable', '{}')
            """
        ),
        {"jh_ex": jh_ex.id, "vh_ex": vh_ex.id, "jh": jh, "vh": vh},
    )
    db.session.commit()

    return {
        "jh": jh,
        "gh": gh,
        "vh": vh,
        "setting_key": setting.key,
        "prompt_key": prompt.prompt_key,
        "before_curriculum": {
            "junior_high": SkillCurriculum.query.filter_by(curriculum="junior_high").count(),
            "general": SkillCurriculum.query.filter_by(curriculum="general").count(),
            "vocational": SkillCurriculum.query.filter_by(curriculum="vocational").count(),
        },
    }


def _textbook_totals() -> dict[str, int]:
    out = {}
    for name in CORE_TEXTBOOK_FULL_CLEAR_TABLES:
        out[name] = int(
            db.session.execute(text(f'SELECT COUNT(*) FROM "{name}"')).scalar() or 0
        )
    return out


def test_wrong_token_does_not_execute(app_ctx):
    app, admin_id, _, _ = app_ctx
    with app.app_context():
        seeded = _seed_all_curricula()
        before = _textbook_totals()
        client = app.test_client()
        _login(client, admin_id)
        r = client.post(
            "/db_maintenance",
            data={
                "action": "clear_all_data",
                "mode": "core",
                "core_scope_mode": "all",
                "core_clear_confirm": "WRONG",
            },
            follow_redirects=True,
        )
        assert r.status_code == 200
        assert _textbook_totals() == before
        assert User.query.filter_by(role="student").count() == 1
        assert seeded["before_curriculum"]["junior_high"] >= 1


def test_delete_core_wipes_all_curricula_keeps_admin_teacher(app_ctx):
    app, admin_id, _, db_path = app_ctx
    with app.app_context():
        seeded = _seed_all_curricula()
        assert seeded["before_curriculum"]["junior_high"] >= 1
        assert seeded["before_curriculum"]["general"] >= 1
        assert seeded["before_curriculum"]["vocational"] >= 1

        preview = _hard_clear_core_data(execute=False)
        plan = preview["plan"]
        assert plan.index("gencode_component_tracker") < plan.index("textbook_examples")
        assert plan.index("skill_family_bridge") < plan.index("skills_info")
        assert plan.index("skill_prerequisites") < plan.index("skills_info")
        assert plan.index("textbook_examples") < plan.index("skills_info")
        assert plan.index("quiz_attempts") < plan.index("questions")
        for name in CORE_TEXTBOOK_FULL_CLEAR_TABLES:
            assert name in plan
            assert any(t["table"] == name and t["where"] == "1=1" for t in preview["textbook_clear"])

        client = app.test_client()
        _login(client, admin_id)
        r = client.post(
            "/db_maintenance",
            data={
                "action": "clear_all_data",
                "mode": "core",
                "core_scope_mode": "all",
                "core_clear_confirm": CORE_CLEAR_CONFIRM_TOKEN,
            },
            follow_redirects=True,
        )
        body = r.get_data(as_text=True)
        assert r.status_code == 200
        assert "DELETE_CORE 完成" in body
        for name in CORE_TEXTBOOK_FULL_CLEAR_TABLES:
            assert f"{name}=" in body

        remaining = _core_textbook_remaining_check()
        assert remaining == {k: 0 for k in remaining}
        assert _textbook_totals() == {k: 0 for k in CORE_TEXTBOOK_FULL_CLEAR_TABLES}

        assert SkillCurriculum.query.filter_by(curriculum="junior_high").count() == 0
        assert SkillCurriculum.query.filter_by(curriculum="general").count() == 0
        assert SkillCurriculum.query.filter_by(curriculum="vocational").count() == 0
        assert SkillInfo.query.count() == 0
        assert SkillFamilyBridge.query.count() == 0

        assert User.query.filter_by(role="student").count() == 0
        assert User.query.filter_by(role="admin").count() >= 1
        assert User.query.filter_by(role="teacher").count() == 1
        assert Class.query.count() == 0
        assert ClassStudent.query.count() == 0
        assert Progress.query.filter_by(user_id=502).count() == 0
        assert Progress.query.filter_by(user_id=501).count() == 1
        assert SystemSetting.query.filter_by(key=seeded["setting_key"]).count() == 1
        assert PromptTemplate.query.filter_by(prompt_key=seeded["prompt_key"]).count() == 1

        db.session.execute(text("PRAGMA foreign_keys = ON"))
        assert db.session.execute(text("PRAGMA foreign_key_check")).fetchall() == []

        # Restart / re-init must NOT auto-seed curriculum from catalog.
        init_db(db.engine, seed_bridges=False)
        assert SkillInfo.query.count() == 0
        assert SkillCurriculum.query.count() == 0
        assert SkillFamilyBridge.query.count() == 0
        assert TextbookExample.query.count() == 0
