from __future__ import annotations

import re
from pathlib import Path

import pytest

from app import create_app
from models import Class, ClassStudent, User, db


@pytest.fixture()
def teacher_dashboard_app(tmp_path: Path):
    import config as app_config

    db_path = tmp_path / "teacher_dashboard.db"
    previous_uri = app_config.Config.SQLALCHEMY_DATABASE_URI
    app_config.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path.resolve()).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        yield app
    finally:
        with app.app_context():
            db.session.remove()
        app_config.Config.SQLALCHEMY_DATABASE_URI = previous_uri


def _login(client, user_id: int) -> None:
    with client.session_transaction() as session:
        session["_user_id"] = str(user_id)
        session["_fresh"] = True


def test_teacher_dashboard_renders_two_class_rosters_and_total(teacher_dashboard_app):
    with teacher_dashboard_app.app_context():
        teacher = User(username="dashboard_teacher", password_hash="hash", role="teacher")
        students = [
            User(username=f"dashboard_student_{index:02d}", password_hash="hash", role="student")
            for index in range(50)
        ]
        db.session.add_all([teacher, *students])
        db.session.flush()

        class_a = Class(name="資一乙", teacher_id=teacher.id, class_code="L131HFEZ")
        class_b = Class(name="多三甲", teacher_id=teacher.id, class_code="XHP4YS43")
        db.session.add_all([class_a, class_b])
        db.session.flush()
        db.session.add_all(
            [ClassStudent(class_id=class_a.id, student_id=student.id) for student in students[:19]]
            + [ClassStudent(class_id=class_b.id, student_id=student.id) for student in students[19:]]
        )
        db.session.commit()
        teacher_id = teacher.id

    client = teacher_dashboard_app.test_client()
    _login(client, teacher_id)
    response = client.get("/teacher_dashboard")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert re.search(r'id="class-count" class="summary-value">\s*2\s*</div>', html)
    assert re.search(r'id="student-count" class="summary-value">\s*50\s*</div>', html)
    assert "資一乙" in html and "L131HFEZ" in html
    assert "多三甲" in html and "XHP4YS43" in html
    assert "<strong>19</strong><span>位學生</span>" in html
    assert "<strong>31</strong><span>位學生</span>" in html
    assert "待批改作業" not in html


def test_teacher_dashboard_counts_student_in_two_classes_once(teacher_dashboard_app):
    with teacher_dashboard_app.app_context():
        teacher = User(username="unique_count_teacher", password_hash="hash", role="teacher")
        student = User(username="shared_student", password_hash="hash", role="student")
        db.session.add_all([teacher, student])
        db.session.flush()
        classes = [
            Class(name="甲班", teacher_id=teacher.id, class_code="AAAA1111"),
            Class(name="乙班", teacher_id=teacher.id, class_code="BBBB2222"),
        ]
        db.session.add_all(classes)
        db.session.flush()
        db.session.add_all(
            [ClassStudent(class_id=class_obj.id, student_id=student.id) for class_obj in classes]
        )
        db.session.commit()
        teacher_id = teacher.id

    client = teacher_dashboard_app.test_client()
    _login(client, teacher_id)

    page_response = client.get("/teacher_dashboard")
    assert page_response.status_code == 200
    assert re.search(
        r'id="student-count" class="summary-value">\s*1\s*</div>',
        page_response.get_data(as_text=True),
    )

    api_response = client.get("/api/teacher/classes")
    assert api_response.status_code == 200
    payload = api_response.get_json()
    assert payload["student_count"] == 1
    assert sorted(class_row["student_count"] for class_row in payload["classes"]) == [1, 1]
