"""Focused review window tests; no test writes to the database."""
from __future__ import annotations

import pytest
from flask_login import UserMixin
from sqlalchemy import text
from types import SimpleNamespace

from app import app, login_manager
from models import Class, User, ClassStudent, PracticeAttempt, Progress, db

MESSAGE = "此為展示頁面，請登入後再行操作。"
DENIED = {"success": False, "error": "review_demo_read_only", "message": MESSAGE}


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.delenv("REVIEW_DEMO_ENABLED", raising=False)
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def _enter(client):
    response = client.get("/review-demo")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/teacher_dashboard")


def test_review_entry_opens_existing_teacher_dashboard_without_login(client):
    _enter(client)
    assert client.get("/teacher_dashboard").status_code == 200
    with client.session_transaction() as sess:
        assert sess["guest_demo"] is True
        assert "_user_id" not in sess
        assert "teacher_id" not in sess


@pytest.mark.parametrize("path", [
    "/curriculum", "/skills", "/teacher/analysis", "/api/teacher/classes",
])
def test_existing_teacher_get_pages_remain_browsable(client, path):
    _enter(client)
    assert client.get(path).status_code == 200


def test_class_student_details_use_admin_read_context(client):
    import core.guest_demo as guest_demo

    with app.app_context():
        teacher_id = guest_demo._admin_teacher_id(db)
        admin = db.session.query(User).filter(User.username == "admin").first()
        assert teacher_id == admin.id
        assert admin.role == "teacher"
        class_id = db.session.query(Class.id).filter(Class.teacher_id == teacher_id).first()[0]
    _enter(client)
    response = client.get(f"/api/classes/{class_id}/students")
    assert response.status_code == 200
    assert response.get_json()["success"] is True
    assert isinstance(response.get_json()["students"], list)
    with client.session_transaction() as sess:
        assert "_user_id" not in sess
        assert "teacher_id" not in sess
    principal = guest_demo.GuestDemoPrincipal(teacher_id)
    assert principal.id == teacher_id
    assert principal.is_authenticated is False
    assert principal.get_id() is None


def _admin_student_sample():
    with app.app_context():
        admin = db.session.query(User).filter(User.username == "admin").first()
        row = (
            db.session.query(Class.id, User.id, User.username, User.real_name)
            .join(ClassStudent, ClassStudent.class_id == Class.id)
            .join(User, User.id == ClassStudent.student_id)
            .filter(Class.teacher_id == admin.id, User.real_name.isnot(None))
            .first()
        )
        assert row is not None
        return row


def test_guest_masks_api_username_without_changing_user_row(client):
    import core.guest_demo as guest_demo

    class_id, student_id, username, real_name = _admin_student_sample()
    _enter(client)
    response = client.get(f"/api/classes/{class_id}/students")
    assert response.status_code == 200
    students = response.get_json()["students"]
    shown = next(row for row in students if row["id"] == student_id)
    assert shown["username"] == username[:3] + "*" * (len(username) - 3)
    assert username not in response.get_data(as_text=True)
    with app.app_context():
        db.session.expire_all()
        student = db.session.get(User, student_id)
        assert student.username == username
        assert student.real_name == real_name
    with app.test_request_context("/teacher/analysis"):
        from flask import session

        session["guest_demo"] = True
        assert guest_demo.mask_student_username("312001") == "312***"
        assert guest_demo.mask_student_name("王小明") == "王○明"
        assert guest_demo.mask_student_name("李明") == "李○"
        assert guest_demo.mask_student_name("王") == "○"


def test_guest_masks_teacher_analysis_names_and_identifiers(client):
    import core.guest_demo as guest_demo

    class_id, student_id, username, real_name = _admin_student_sample()
    before = _learning_counts()
    _enter(client)
    class_page = client.get("/teacher/analysis", query_string={"class_id": class_id})
    assert class_page.status_code == 200
    class_html = class_page.get_data(as_text=True)
    assert real_name not in class_html
    assert username not in class_html
    assert guest_demo.mask_student_name(real_name) in class_html
    assert guest_demo.mask_student_username(username) in class_html
    student_page = client.get("/teacher/analysis", query_string={
        "class_id": class_id, "student_id": student_id,
    })
    assert student_page.status_code == 200
    student_html = student_page.get_data(as_text=True)
    assert real_name not in student_html
    assert guest_demo.mask_student_name(real_name) in student_html
    assert _learning_counts() == before


def test_normal_admin_still_sees_complete_student_identity(client):
    class_id, student_id, username, real_name = _admin_student_sample()
    with app.app_context():
        admin_id = db.session.query(User.id).filter(User.username == "admin").scalar()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(admin_id)
        sess["_fresh"] = True
    api_response = client.get(f"/api/classes/{class_id}/students")
    assert api_response.status_code == 200
    shown = next(row for row in api_response.get_json()["students"] if row["id"] == student_id)
    assert shown["username"] == username
    analysis_response = client.get("/teacher/analysis", query_string={"class_id": class_id})
    assert analysis_response.status_code == 200
    html = analysis_response.get_data(as_text=True)
    assert real_name in html
    assert username in html


def _learning_counts():
    with app.app_context():
        return (
            db.session.query(ClassStudent).count(),
            db.session.query(PracticeAttempt).count(),
            db.session.query(Progress).count(),
        )


def test_guest_student_mode_uses_existing_vocational_home_with_blank_personal_context(client):
    before = _learning_counts()
    _enter(client)
    response = client.get("/dashboard")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "歡迎回來，展示學生" in html
    assert "開始你的第一次練習" in html
    assert "尚未加入班級" in html
    assert "我的課程" in html
    assert "七年級" not in html
    assert "八年級" not in html
    assert "九年級" not in html
    with client.session_transaction() as sess:
        assert sess["current_curriculum"] == "vocational"
        assert "_user_id" not in sess
        assert "student_id" not in sess
    assert _learning_counts() == before


def test_guest_absolute_value_first_and_next_question_use_local_generator(client):
    before = _learning_counts()
    _enter(client)
    assert client.get("/practice/vh_數學B1_AbsoluteValue").status_code == 200
    previous_uid = None
    for _ in range(2):
        response = client.get("/get_next_question", query_string={
            "skill": "vh_數學B1_AbsoluteValue", "level": 1,
        })
        assert response.status_code == 200
        question = response.get_json()
        assert question["skill_id"] == "vh_數學B1_AbsoluteValue"
        assert question["question_text"]
        assert question["question_uid"] != previous_uid
        assert question["route_source"] == "gencode_wrapper"
        assert question["consecutive_correct"] == 0
        previous_uid = question["question_uid"]
    with client.session_transaction() as sess:
        assert sess["current_curriculum"] == "vocational"
        assert "_user_id" not in sess
    assert _learning_counts() == before


def test_practice_cookie_prune_preserves_guest_identity_under_size_pressure(client):
    from core.practice_question_store import prune_practice_session
    from flask import session

    _enter(client)
    with app.test_request_context("/practice/vh_數學B1_AbsoluteValue"):
        session["guest_demo"] = True
        result = prune_practice_session(max_cookie_bytes=1)
        assert session["guest_demo"] is True
        assert "guest_demo" in result["kept_keys"]
        assert "guest_demo" not in result["removed_keys"]


def test_practice_cookie_prune_keeps_normal_auth_without_adding_guest(client):
    from core.practice_question_store import prune_practice_session
    from flask import session

    with app.test_request_context("/practice/vh_數學B1_AbsoluteValue"):
        session["_user_id"] = "123"
        prune_practice_session(max_cookie_bytes=1)
        assert session["_user_id"] == "123"
        assert "guest_demo" not in session


def test_normal_student_absolute_value_generation_stays_available(client, monkeypatch):
    class Student(UserMixin):
        id = -2
        username = "existing_student"
        role = "student"
        is_admin = False

    monkeypatch.setattr(login_manager, "_user_callback", lambda _id: Student())
    with client.session_transaction() as sess:
        sess["_user_id"] = str(Student.id)
        sess["_fresh"] = True
        sess["current_curriculum"] = "vocational"
    response = client.get("/get_next_question", query_string={
        "skill": "vh_數學B1_AbsoluteValue", "level": 1,
    })
    assert response.status_code == 200
    assert response.get_json()["question_text"]
    with client.session_transaction() as sess:
        assert "guest_demo" not in sess


def test_guest_curriculum_is_fixed_on_deep_dashboard_and_selector(client):
    _enter(client)
    response = client.get("/dashboard", query_string={
        "view": "curriculum", "curriculum": "vocational", "volume": "數學B1",
    })
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'aria-label="固定課綱">技術型高中</span>' in html
    assert ">國中</a>" not in html
    assert ">普高</a>" not in html
    with client.session_transaction() as sess:
        assert sess["current_curriculum"] == "vocational"


@pytest.mark.parametrize("query", [
    {"curriculum": "junior_high"},
    {"curriculum": "general", "volume": "數學1上"},
    {"view": "all", "curriculum": "general"},
])
def test_guest_cannot_switch_curriculum_using_query_or_session(client, query):
    _enter(client)
    with client.session_transaction() as sess:
        sess["current_curriculum"] = "junior_high"
    response = client.get("/dashboard", query_string=query, follow_redirects=True)
    assert response.status_code == 200
    assert "歡迎回來，展示學生" in response.get_data(as_text=True)
    with client.session_transaction() as sess:
        assert sess["current_curriculum"] == "vocational"


def test_guest_curriculum_is_normalized_on_other_get_pages(client):
    _enter(client)
    response = client.get("/curriculum", query_string={"curriculum": "general"})
    assert response.status_code == 302
    assert "curriculum=vocational" in response.headers["Location"]
    assert client.get(response.headers["Location"]).status_code == 200
    with client.session_transaction() as sess:
        assert sess["current_curriculum"] == "vocational"


@pytest.mark.parametrize("record", [None, SimpleNamespace(id=1, role="student")])
def test_missing_or_non_teacher_admin_fails_closed_at_entry(client, monkeypatch, record):
    import core.guest_demo as guest_demo

    monkeypatch.setattr(guest_demo, "_admin_record", lambda _db: record)
    assert client.get("/review-demo").status_code == 503
    with client.session_transaction() as sess:
        assert "guest_demo" not in sess


def test_existing_guest_fails_closed_if_admin_role_changes(client, monkeypatch):
    import core.guest_demo as guest_demo

    _enter(client)
    monkeypatch.setattr(guest_demo, "_admin_record", lambda _db: SimpleNamespace(id=1, role="student"))
    assert client.get("/teacher_dashboard").status_code == 503


@pytest.mark.parametrize("path", [
    "/chat_ai", "/api/rag_chat", "/api/adaptive/adv_rag_chat",
    "/api/rag_search", "/api/adaptive/adv_rag_search",
    "/api/practice/ai-check-handwriting", "/analyze_handwriting",
    "/api/adaptive-review/chat", "/api/adaptive-review/check-handwriting",
])
def test_guest_ai_and_rag_are_denied_before_handler(client, monkeypatch, path):
    endpoint = next((rule.endpoint for rule in app.url_map.iter_rules() if rule.rule == path), None)
    if endpoint is None:
        pytest.skip(f"optional endpoint {path} is not registered")
    monkeypatch.setitem(app.view_functions, endpoint, lambda **_kwargs: pytest.fail("AI provider called"))
    _enter(client)
    response = client.post(path, json={"query": "hint", "question": "hint"})
    assert response.status_code == 403
    assert response.get_json() == DENIED


@pytest.mark.parametrize("method,path", [
    ("post", "/classes/create"), ("post", "/skills/add"),
    ("delete", "/api/prompts/1"), ("post", "/check_answer"),
    ("post", "/api/adaptive/submit_and_get_next"),
    ("post", "/admin/textbook-examples/1/v3-preview/generate"),
])
def test_every_guest_mutation_is_denied(client, method, path):
    _enter(client)
    response = getattr(client, method)(path, json={})
    assert response.status_code == 403
    assert response.get_json() == DENIED


@pytest.mark.parametrize("sql", [
    "/* review */ UPDATE users SET username = 'bad'",
    "-- review\nDELETE FROM users",
    "WITH x AS (SELECT 1) DELETE FROM users",
    "SELECT 1; DELETE FROM users",
    "CREATE TABLE review_write_probe (id INTEGER)",
    "PRAGMA writable_schema = ON",
])
def test_sql_backstop_rejects_writes_without_executing_them(client, sql):
    _enter(client)
    with app.test_request_context("/teacher_dashboard"):
        from flask import session

        session["guest_demo"] = True
        assert db.session.execute(text("SELECT 1")).scalar() == 1
        with pytest.raises(PermissionError, match="guest_demo_persistence_denied"):
            db.session.execute(text(sql))
        db.session.rollback()


@pytest.mark.parametrize("path", [
    "/debug/session_key_status", "/admin/ai_prompt_settings/check_api_key",
    "/admin/ai_prompt_settings/check_api_key_masked",
    "/admin/ai_prompt_settings/list", "/admin/check_api_key",
    "/api/runtime_ai_status", "/api/adaptive/rag_settings",
])
def test_guest_cannot_read_key_or_provider_status(client, path):
    _enter(client)
    response = client.get(path)
    assert response.status_code == 403
    assert response.get_json() == DENIED


def test_guest_can_view_ai_settings_without_credentials_or_mutation(client, monkeypatch):
    secret = "review-secret-must-not-appear-7391"
    monkeypatch.setenv("GEMINI_API_KEY", secret)
    before = _learning_counts()
    _enter(client)
    page = client.get("/admin/ai_prompt_settings")
    assert page.status_code == 200
    assert page.content_type.startswith("text/html")
    html = page.get_data(as_text=True)
    assert "AI 後台設定" in html
    assert secret not in html
    assert 'id="gemini-api-key"' in html
    assert MESSAGE in html
    settings = client.get("/admin/ai_prompt_settings/get")
    assert settings.status_code == 200
    data = settings.get_json()
    assert data["success"] is True
    assert data["cloud_model"]
    assert data["masked_gemini_api_key"] == ""
    assert data["has_gemini_api_key"] is False
    assert secret not in settings.get_data(as_text=True)
    for path in ("/admin/ai_prompt_settings/update", "/admin/ai_prompt_settings/reset",
                 "/admin/ai_prompt_settings/clear_api_key", "/test_api_key"):
        response = client.post(path, json={})
        assert response.status_code == 403
        assert response.get_json() == DENIED
    assert _learning_counts() == before


def test_guest_can_view_database_maintenance_without_operations(client):
    before = _learning_counts()
    _enter(client)
    page = client.get("/db_maintenance")
    assert page.status_code == 200
    assert page.content_type.startswith("text/html")
    html = page.get_data(as_text=True)
    assert "資料庫維護" in html
    assert f'<div class="alert alert-error" role="alert" data-guest-demo-warning>' in html
    assert MESSAGE in html
    assert client.get("/db_maintenance/core_scope_options").status_code == 200
    for action in ("export_db", "restore", "import", "clear", "delete"):
        response = client.post("/db_maintenance", data={"action": action})
        assert response.status_code == 403
        assert response.get_json() == DENIED
    assert client.post("/upload_db", data={}).status_code == 403
    assert _learning_counts() == before


def test_normal_admin_management_pages_and_write_route_remain_available(client, monkeypatch):
    with app.app_context():
        admin_id = db.session.query(User.id).filter(User.username == "admin").scalar()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(admin_id)
        sess["_fresh"] = True
    assert client.get("/admin/ai_prompt_settings").status_code == 200
    maintenance = client.get("/db_maintenance")
    assert maintenance.status_code == 200
    assert "data-guest-demo-warning" not in maintenance.get_data(as_text=True)
    assert MESSAGE not in maintenance.get_data(as_text=True)
    endpoint = "core.update_ai_prompt_setting"
    assert endpoint in app.view_functions
    monkeypatch.setitem(app.view_functions, endpoint, lambda: ("normal admin reached handler", 200))
    response = client.post("/admin/ai_prompt_settings/update", json={})
    assert response.status_code == 200
    assert response.get_data(as_text=True) == "normal admin reached handler"


def test_review_entry_and_session_work_without_feature_flag(client, monkeypatch):
    _enter(client)
    monkeypatch.setenv("REVIEW_DEMO_ENABLED", "0")
    response = client.get("/teacher_dashboard")
    assert response.status_code == 200


@pytest.mark.parametrize("role", ["teacher", "admin", "student"])
def test_normal_accounts_outside_review_keep_their_login(client, monkeypatch, role):
    class Account(UserMixin):
        id = 123456789
        username = "existing_account"
        is_admin = role == "admin"

        def __init__(self):
            self.role = role

    monkeypatch.setattr(login_manager, "_user_callback", lambda _id: Account())
    with client.session_transaction() as sess:
        sess["_user_id"] = str(Account.id)
        sess["_fresh"] = True
    response = client.get("/dashboard")
    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert sess["_user_id"] == str(Account.id)
        assert "guest_demo" not in sess
    # The review gate must not reject an authenticated account's regular POST.
    response = client.post("/chat_ai", json={})
    assert response.get_json() != DENIED


def test_logged_in_admin_explicitly_entering_review_gets_guest_student_home(client):
    with app.app_context():
        admin_id = db.session.query(User.id).filter(User.username == "admin").scalar()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(admin_id)
        sess["_fresh"] = True
    before = client.get("/dashboard")
    assert before.status_code == 200
    assert "學習儀表板" in before.get_data(as_text=True)

    _enter(client)
    with client.session_transaction() as sess:
        assert sess["guest_demo"] is True
        assert "_user_id" not in sess
    after = client.get("/dashboard")
    assert after.status_code == 200
    html = after.get_data(as_text=True)
    assert "歡迎回來，展示學生" in html
    assert "七年級" not in html


@pytest.mark.parametrize("role,curriculum,expected", [
    ("admin", "general", "普高"),
    ("student", "vocational", "歡迎回來，existing_account"),
])
def test_normal_accounts_keep_curriculum_behavior(client, monkeypatch, role, curriculum, expected):
    class Account(UserMixin):
        id = -2
        username = "existing_account"
        real_name = ""
        is_admin = role == "admin"
        curriculum_code = curriculum

        def __init__(self):
            self.role = role

    monkeypatch.setattr(login_manager, "_user_callback", lambda _id: Account())
    with client.session_transaction() as sess:
        sess["_user_id"] = str(Account.id)
        sess["_fresh"] = True
    response = client.get("/dashboard", query_string={"curriculum": curriculum})
    assert response.status_code == 200
    assert expected in response.get_data(as_text=True)
    with client.session_transaction() as sess:
        assert "guest_demo" not in sess
        if role == "admin":
            assert sess["current_curriculum"] == "general"
