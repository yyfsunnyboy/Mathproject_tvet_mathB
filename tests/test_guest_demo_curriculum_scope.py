"""Guest Demo is confined to the vocational curriculum; real accounts keep every curriculum.

Runs on a throwaway SQLite DB; nothing touches the shared or production database.
"""
from __future__ import annotations

import re
import uuid
from datetime import datetime, timedelta

import pytest

DENIED = {"success": False, "error": "review_demo_read_only", "message": "此為展示頁面，請登入後再行操作。"}

# skill_id -> (stored curriculum code, grade, volume, chinese name)
SKILLS = {
    "jh_數學1上_ScopeJunior": ("junior_high", 7, "數學1上", "國中範圍技能甲"),
    "jh_數學1上_ScopeJuniorAlias": ("國中", 7, "數學1上", "國中別名技能戊"),
    "gh_數學1_ScopeGeneral": ("general", 11, "數學1", "普高範圍技能乙"),
    "vh_數學B1_ScopeVocational": ("vocational", 10, "數學B1", "技高範圍技能丙"),
    "vh_數學B1_ScopeVocAlias": ("vocational_high", 10, "數學B1", "技高別名技能丁"),
}
HIDDEN_NAMES = ("國中範圍技能甲", "國中別名技能戊", "普高範圍技能乙")
VOC_NAMES = ("技高範圍技能丙", "技高別名技能丁")
JUNIOR, GENERAL, VOC = "jh_數學1上_ScopeJunior", "gh_數學1_ScopeGeneral", "vh_數學B1_ScopeVocational"
# Skills without any skill_curriculum row fall back to the vh_ (vocational) id convention.
VOC_ORPHAN, JUNIOR_ORPHAN = "vh_數學B9_ScopeOrphan", "jh_數學1上_ScopeOrphan"


@pytest.fixture()
def scope_app(tmp_path):
    import config as config_module
    from app import create_app
    from models import (AdaptiveLearningLog, Class, ClassStudent, PracticeAttempt, SkillCurriculum,
                        SkillFamilyBridge, SkillInfo, TextbookExample, User, db)

    previous = config_module.Config.SQLALCHEMY_DATABASE_URI
    db_path = tmp_path / f"guest_scope_{uuid.uuid4().hex[:8]}.db"
    config_module.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            db.session.add_all([
                User(id=901, username="admin", password_hash="x", role="teacher"),
                User(id=902, username="root_admin", password_hash="x", role="admin"),
                User(id=903, username="plain_teacher", password_hash="x", role="teacher"),
                User(id=904, username="scope_student", password_hash="x", role="student", real_name="王小明"),
                Class(id=91, name="範圍班", teacher_id=901, class_code="SCOPE091"),
            ])
            db.session.flush()
            db.session.add(ClassStudent(class_id=91, student_id=904))
            for index, (skill_id, (curriculum, grade, volume, name)) in enumerate(SKILLS.items()):
                db.session.add(SkillInfo(skill_id=skill_id, skill_en_name=skill_id, skill_ch_name=name,
                                         description="d", gemini_prompt="p"))
                db.session.flush()
                db.session.add(SkillCurriculum(skill_id=skill_id, curriculum=curriculum, grade=grade, volume=volume,
                                               chapter="第一章", section="1-1", display_order=index))
                db.session.add(TextbookExample(id=100 + index, skill_id=skill_id, source_curriculum=curriculum,
                                               source_volume=volume, source_chapter="第一章", source_section="1-1",
                                               source_description="例題", problem_text=f"{name} 例題"))
            for skill_id in (VOC_ORPHAN, JUNIOR_ORPHAN):
                db.session.add(SkillInfo(skill_id=skill_id, skill_en_name=skill_id, skill_ch_name=skill_id,
                                         description="d", gemini_prompt="p"))
            db.session.flush()
            now = datetime.utcnow()
            for minutes, skill_id in enumerate([VOC, VOC, VOC, JUNIOR, JUNIOR, VOC_ORPHAN, JUNIOR_ORPHAN]):
                db.session.add(PracticeAttempt(
                    student_id=904, skill_id=skill_id, question_text="q", user_answer="1", expected_answer="1",
                    is_correct=True, source="general_practice", problem_type_id="t",
                    created_at=now - timedelta(minutes=minutes),
                ))
            db.session.add(SkillFamilyBridge(skill_id=JUNIOR, family_id="JH_SCOPE_FAM", skill_name=JUNIOR,
                                             family_name="jh", subskill_nodes="[]", curriculum="junior_high"))
            for step, family in enumerate(["JH_SCOPE_FAM"] * 4 + ["B4_UNBRIDGED"] * 5):
                db.session.add(AdaptiveLearningLog(
                    student_id=904, session_id="s", step_number=step, target_family_id=family,
                    target_subskills="[]", is_correct=True, current_apr=0.5, ppo_strategy=0,
                ))
            db.session.commit()
        yield app
    finally:
        config_module.Config.SQLALCHEMY_DATABASE_URI = previous


def _guest(app):
    client = app.test_client()
    response = client.get("/review-demo")
    assert response.status_code == 302
    return client


def _login(app, user_id):
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True
    return client


def _curriculum_options(page: str) -> list[str]:
    select = re.search(r'<select id="f_curriculum".*?</select>', page, re.S).group(0)
    return re.findall(r'<option value="([^"]+)"', select)


def _table_rows(page: str) -> str:
    return page[page.index("<tbody"):page.index("</tbody>")]


def _counts(app):
    from models import SkillCurriculum, SkillInfo, TextbookExample

    with app.app_context():
        return SkillInfo.query.count(), SkillCurriculum.query.count(), TextbookExample.query.count()


# --- Guest Demo: vocational only ------------------------------------------------

@pytest.mark.parametrize("path", ["/curriculum", "/skills", "/examples", "/admin/prerequisites"])
def test_guest_first_load_lists_only_vocational(scope_app, path):
    page = _guest(scope_app).get(path).get_data(as_text=True)
    assert _curriculum_options(page) == ["vocational"]
    assert "data-curriculum-locked" in page and "（展示固定）" in page
    assert "data-guest-demo-warning" in page
    for name in HIDDEN_NAMES:
        assert name not in page
    if path != "/examples":
        for name in VOC_NAMES:
            assert name in page


@pytest.mark.parametrize("forced", ["junior_high", "general", "all", "國中", "general_high", "JUNIOR_HIGH"])
@pytest.mark.parametrize("path", ["/curriculum", "/skills", "/examples", "/admin/prerequisites"])
def test_guest_cannot_force_another_curriculum_by_url(scope_app, path, forced):
    client = _guest(scope_app)
    response = client.get(path, query_string={"f_curriculum": forced, "f_grade": "7"})
    assert response.status_code == 302
    assert "f_curriculum=vocational" in response.headers["Location"]
    page = client.get(path, query_string={"f_curriculum": forced}, follow_redirects=True).get_data(as_text=True)
    assert _curriculum_options(page) == ["vocational"]
    for name in HIDDEN_NAMES:
        assert name not in page


def test_guest_clear_and_reload_ignore_admin_filter_memory(scope_app):
    client = _guest(scope_app)
    with client.session_transaction() as sess:
        sess.update(last_f_curr="junior_high", last_f_grade="7", last_f_vol="數學1上")
    for _ in range(2):
        page = client.get("/curriculum").get_data(as_text=True)
        assert all(name in page for name in VOC_NAMES)
        assert not any(name in page for name in HIDDEN_NAMES)
    with client.session_transaction() as sess:
        assert sess["last_f_curr"] == "junior_high"


def test_guest_empty_filter_shows_empty_state_not_other_curricula(scope_app):
    page = _guest(scope_app).get("/curriculum", query_string={"f_volume": "數學1上"}).get_data(as_text=True)
    assert "目前的篩選條件下沒有結果" in page
    assert not any(name in page for name in HIDDEN_NAMES)


def test_guest_dropdown_and_search_apis_stay_vocational(scope_app):
    client = _guest(scope_app)
    redirect = client.get("/api/get_grades", query_string={"curriculum": "junior_high"})
    assert redirect.status_code == 302 and "curriculum=vocational" in redirect.headers["Location"]
    assert client.get("/api/get_grades", query_string={"curriculum": "junior_high"}, follow_redirects=True).get_json() == [10]
    assert client.get("/api/get_grades").get_json() == [10]
    assert client.get("/api/get_volumes", query_string={"grade": 7}).get_json() == []
    assert client.get("/api/get_volumes", query_string={"grade": 10}).get_json() == ["數學B1"]
    found = client.get("/api/skills/search", query_string={"term": "Scope"}).get_json()["results"]
    assert sorted(row["id"] for row in found) == sorted([VOC, "vh_數學B1_ScopeVocAlias", VOC_ORPHAN])
    options = client.get("/db_maintenance/core_scope_options", query_string={"curriculum": "general"},
                         follow_redirects=True).get_json()
    assert options["curricula"] == ["vocational"]
    assert 7 not in options["grades"] and 11 not in options["grades"]


@pytest.mark.parametrize("path", [
    f"/skills/{JUNIOR}/details", f"/skills/{GENERAL}/details", f"/api/skills/{JUNIOR}/prerequisites",
    f"/api/skills/{JUNIOR}/prerequisites", f"/api/skills/{GENERAL}/prompts",
    "/examples/100/details", "/examples/102/details", "/admin/textbook-examples/100/v3-details",
    f"/get_next_question?skill={JUNIOR}", f"/get_suggested_prompts/{GENERAL}",
    f"/skills/{JUNIOR_ORPHAN}/details", f"/get_next_question?skill={VOC},{JUNIOR}",
])
def test_guest_direct_api_calls_outside_scope_are_refused(scope_app, path):
    response = _guest(scope_app).get(path)
    assert response.status_code == 404
    assert response.get_json()["error"] == "review_demo_out_of_scope"


def test_guest_html_navigation_outside_scope_returns_to_vocational_home(scope_app):
    response = _guest(scope_app).get(f"/practice/{JUNIOR}", headers={"Accept": "text/html"})
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")


def test_guest_vocational_details_remain_readable(scope_app):
    client = _guest(scope_app)
    assert client.get(f"/skills/{VOC}/details").get_json()["data"]["skill_ch_name"] == "技高範圍技能丙"
    assert client.get("/examples/103/details").get_json()["data"]["skill_id"] == VOC
    assert client.get(f"/api/skills/{VOC}/prerequisites").get_json() == {"success": True, "data": []}
    assert client.get(f"/skills/{VOC_ORPHAN}/details").get_json()["success"] is True
    found = client.get("/api/skills/search", query_string={"term": "ScopeOrphan"}).get_json()["results"]
    assert [row["id"] for row in found] == [VOC_ORPHAN]


def test_guest_student_analysis_counts_only_vocational_records(scope_app):
    from flask import session

    from core.teacher_analysis_service import (_aggregate_adaptive_by_student, _aggregate_practice_by_student,
                                               parse_time_range)

    everything = parse_time_range("all")
    with scope_app.test_request_context("/teacher/analysis"):
        assert _aggregate_practice_by_student([904], everything)[904].total == 7
        assert _aggregate_adaptive_by_student([904], everything)[904].total == 9
        session["guest_demo"] = True
        assert _aggregate_practice_by_student([904], everything)[904].total == 4
        assert _aggregate_adaptive_by_student([904], everything)[904].total == 5
    page = _guest(scope_app).get("/teacher/analysis", query_string={"class_id": 91, "student_id": 904})
    assert page.status_code == 200
    html = page.get_data(as_text=True)
    assert "數學B1" in html and "數學1上" not in html


@pytest.mark.parametrize("method,path,payload", [
    ("post", "/curriculum", {"skill_id": VOC, "curriculum": "vocational", "grade": "10"}),
    ("post", "/curriculum/edit/1", {"curriculum": "junior_high"}),
    ("post", "/curriculum/delete/1", None),
    ("post", "/skills/add", {"skill_id": "x"}),
    ("post", f"/skills/edit/{VOC}", {"skill_ch_name": "x"}),
    ("post", f"/skills/delete/{VOC}", None),
    ("post", f"/skills/toggle/{VOC}", None),
    ("post", "/examples/add", {"skill_id": VOC}),
    ("post", "/examples/edit/103", {"skill_id": VOC}),
    ("post", "/examples/delete/103", None),
    ("post", f"/api/skills/{VOC}/prerequisites", {"prereq_id": JUNIOR}),
    ("delete", f"/api/skills/{VOC}/prerequisites/{JUNIOR}", None),
    ("post", "/curriculum?f_curriculum=vocational", {"skill_id": VOC}),
])
def test_guest_cannot_write_by_any_http_request(scope_app, method, path, payload):
    before = _counts(scope_app)
    response = getattr(_guest(scope_app), method)(path, data=payload)
    assert response.status_code == 403
    assert response.get_json() == DENIED
    assert _counts(scope_app) == before


# --- Real accounts keep every curriculum --------------------------------------

@pytest.mark.parametrize("user_id", [901, 902, 903])
def test_real_admin_and_teacher_see_every_curriculum(scope_app, user_id):
    client = _login(scope_app, user_id)
    page = client.get("/curriculum", query_string={"f_curriculum": "all"}).get_data(as_text=True)
    assert _curriculum_options(page) == ["all", "junior_high", "general", "vocational"]
    assert "data-curriculum-locked" not in page and "data-guest-demo-warning" not in page
    for name in HIDDEN_NAMES + VOC_NAMES:
        assert name in page
    junior = client.get("/curriculum", query_string={"f_curriculum": "junior_high"})
    assert junior.status_code == 200
    junior_rows = _table_rows(junior.get_data(as_text=True))
    assert "國中範圍技能甲" in junior_rows and "國中別名技能戊" in junior_rows and "技高範圍技能丙" not in junior_rows
    general = _table_rows(client.get("/skills", query_string={"f_curriculum": "general"}).get_data(as_text=True))
    assert "普高範圍技能乙" in general and "技高範圍技能丙" not in general
    with client.session_transaction() as sess:
        assert sess["last_f_curr"] == "general"
    assert client.get("/api/get_grades", query_string={"curriculum": "junior_high"}).get_json() == [7]
    assert client.get(f"/skills/{JUNIOR}/details").status_code == 200
    assert client.get("/examples/100/details").status_code == 200
    found = client.get("/api/skills/search", query_string={"term": "Scope"}).get_json()["results"]
    assert len(found) == len(SKILLS) + 2
    assert set(client.get("/db_maintenance/core_scope_options").get_json()["curricula"]) == {
        "junior_high", "general", "vocational", "國中", "vocational_high"}


def test_real_admin_keeps_write_access(scope_app):
    from models import SkillCurriculum

    with scope_app.app_context():
        row_id = SkillCurriculum.query.filter_by(skill_id=GENERAL).one().id
    client = _login(scope_app, 902)
    response = client.post(f"/curriculum/delete/{row_id}")
    assert response.status_code == 200 and response.get_json() == {"success": True}
    with scope_app.app_context():
        assert SkillCurriculum.query.filter_by(skill_id=GENERAL).count() == 0


def test_real_admin_student_analysis_is_unscoped(scope_app):
    html = _login(scope_app, 901).get(
        "/teacher/analysis", query_string={"class_id": 91, "student_id": 904}).get_data(as_text=True)
    assert "數學B1" in html and "數學1上" in html
