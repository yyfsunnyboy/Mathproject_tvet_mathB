# -*- coding: utf-8 -*-
"""Phase 6J: teacher/admin read-only visibility for Chap2 visibility audit logs."""

from __future__ import annotations

import uuid

import pytest

from app import create_app
from models import (
    AdaptiveLearningLog,
    B4Chap2VisibilityAuditLog,
    Progress,
    User,
    db,
)
from core.vocational_math_b4.services.b4_chap2_visibility_audit import (
    B4_CHAP2_VISIBILITY_SOURCE_PHASE,
)


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


@pytest.fixture()
def app_with_teacher(tmp_path):
    """Isolated DB file so pytest does not block on a running dev server's SQLite lock."""
    import config as _cfg

    db_path = tmp_path / "phase6j_teacher_audit.db"
    prev_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        tag = uuid.uuid4().hex[:12]
        with app.app_context():
            teacher = User(
                username=f"b4_6j_t_{tag}",
                password_hash="x",
                role="teacher",
            )
            student = User(
                username=f"b4_6j_s_{tag}",
                password_hash="x",
                role="student",
            )
            db.session.add_all([teacher, student])
            db.session.commit()
            tid, sid = teacher.id, student.id
        yield app, tid, sid, tag
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri


def _insert_seed(tag: str, student_pk: int) -> None:
    skill_det = f"vh_數學B4_6j_det_{tag}"
    skill_g1 = f"vh_數學B4_6j_g1_{tag}"
    db.session.add_all(
        [
            B4Chap2VisibilityAuditLog(
                record_kind="deterministic_answer",
                gated_event_type=None,
                student_id=student_pk,
                session_id=f"sess_det_{tag}",
                skill_id=skill_det,
                problem_type_id="classical_probability_fraction",
                generator_key="gen_k",
                answer_type="rational_fraction",
                expected_answer="1/2",
                user_answer="1/2",
                is_correct=True,
                checker_name="check_rational_answer",
                difficulty=1,
                diagnosis_tags='["ok"]',
                public_message=None,
                source_phase=B4_CHAP2_VISIBILITY_SOURCE_PHASE,
            ),
            B4Chap2VisibilityAuditLog(
                record_kind="gated",
                gated_event_type="not_enabled_skill",
                student_id=student_pk,
                session_id=f"sess_ne_{tag}",
                skill_id=skill_g1,
                problem_type_id=None,
                public_message="skill not enabled (test)",
                source_phase=B4_CHAP2_VISIBILITY_SOURCE_PHASE,
            ),
            B4Chap2VisibilityAuditLog(
                record_kind="gated",
                gated_event_type="reserved_problem_type",
                student_id=student_pk,
                session_id=f"sess_r_{tag}",
                skill_id="vh_數學B4_SampleSpaceAndEvents",
                problem_type_id="sample_space_listing",
                public_message="reserved (test)",
                source_phase=B4_CHAP2_VISIBILITY_SOURCE_PHASE,
            ),
        ]
    )
    db.session.commit()


class TestTeacherAuditHtml:
    def test_deterministic_row_visible_on_html(self, app_with_teacher) -> None:
        app, tid, sid, tag = app_with_teacher
        with app.app_context():
            _insert_seed(tag, sid)

        client = app.test_client()
        _login(client, tid)
        skill_det = f"vh_數學B4_6j_det_{tag}"
        r = client.get("/teacher/b4-chap2-audit")
        assert r.status_code == 200
        body = r.get_data(as_text=True)
        assert skill_det in body
        assert "deterministic_answer" in body
        assert "check_rational_answer" in body

    def test_gated_not_enabled_visible(self, app_with_teacher) -> None:
        app, tid, sid, tag = app_with_teacher
        with app.app_context():
            _insert_seed(tag, sid)
        client = app.test_client()
        _login(client, tid)
        skill_g1 = f"vh_數學B4_6j_g1_{tag}"
        r = client.get("/teacher/b4-chap2-audit")
        assert r.status_code == 200
        assert skill_g1 in r.get_data(as_text=True)
        assert "not_enabled_skill" in r.get_data(as_text=True)

    def test_gated_reserved_visible(self, app_with_teacher) -> None:
        app, tid, sid, tag = app_with_teacher
        with app.app_context():
            _insert_seed(tag, sid)
        client = app.test_client()
        _login(client, tid)
        r = client.get("/teacher/b4-chap2-audit")
        assert r.status_code == 200
        t = r.get_data(as_text=True)
        assert "reserved_problem_type" in t
        assert "sample_space_listing" in t

    def test_empty_unfiltered_still_ok_when_only_impossible_filter(self, app_with_teacher) -> None:
        app, tid, _, tag = app_with_teacher
        client = app.test_client()
        _login(client, tid)
        r = client.get(f"/teacher/b4-chap2-audit?skill_id=__no_such_skill_{tag}")
        assert r.status_code == 200
        assert "目前尚無 Chap2 audit logs。" in r.get_data(as_text=True)

    def test_student_redirect_no_crash(self, app_with_teacher) -> None:
        app, _, sid, tag = app_with_teacher
        with app.app_context():
            _insert_seed(tag, sid)
        client = app.test_client()
        _login(client, sid)
        r = client.get("/teacher/b4-chap2-audit", follow_redirects=False)
        assert r.status_code in (302, 303)
        assert "/dashboard" in (r.location or "")


class TestTeacherAuditJson:
    def test_limit_param(self, app_with_teacher) -> None:
        app, tid, sid, tag = app_with_teacher
        with app.app_context():
            _insert_seed(tag, sid)

        client = app.test_client()
        _login(client, tid)
        j = client.get("/api/teacher/b4-chap2-audit?limit=2").get_json()
        assert j.get("ok") is True
        assert len(j.get("items", [])) == 2

    def test_record_kind_filter(self, app_with_teacher) -> None:
        app, tid, sid, tag = app_with_teacher
        with app.app_context():
            _insert_seed(tag, sid)

        client = app.test_client()
        _login(client, tid)
        j = client.get("/api/teacher/b4-chap2-audit?record_kind=deterministic_answer").get_json()
        kinds = {x.get("record_kind") for x in j["items"]}
        assert kinds == {"deterministic_answer"}

    def test_skill_id_filter(self, app_with_teacher) -> None:
        app, tid, sid, tag = app_with_teacher
        with app.app_context():
            _insert_seed(tag, sid)

        skill_g1 = f"vh_數學B4_6j_g1_{tag}"
        client = app.test_client()
        _login(client, tid)
        j = client.get(f"/api/teacher/b4-chap2-audit?skill_id={skill_g1}").get_json()
        assert len(j["items"]) == 1
        assert j["items"][0]["gated_event_type"] == "not_enabled_skill"

    def test_problem_type_id_filter(self, app_with_teacher) -> None:
        app, tid, sid, tag = app_with_teacher
        with app.app_context():
            _insert_seed(tag, sid)

        client = app.test_client()
        _login(client, tid)
        j = client.get(
            "/api/teacher/b4-chap2-audit?problem_type_id=sample_space_listing"
        ).get_json()
        assert len(j["items"]) == 1
        assert j["items"][0]["gated_event_type"] == "reserved_problem_type"

    def test_empty_items_no_crash(self, app_with_teacher) -> None:
        app, tid, _, tag = app_with_teacher
        client = app.test_client()
        _login(client, tid)
        j = client.get(f"/api/teacher/b4-chap2-audit?skill_id=__none_{tag}").get_json()
        assert j["ok"] is True
        assert j["items"] == []

    def test_student_api_forbidden(self, app_with_teacher) -> None:
        app, _, sid, tag = app_with_teacher
        with app.app_context():
            _insert_seed(tag, sid)
        client = app.test_client()
        _login(client, sid)
        r = client.get("/api/teacher/b4-chap2-audit")
        assert r.status_code == 403


class TestVisibilityOnlySideEffects:
    def test_get_audit_does_not_touch_progress_or_adaptive_logs(self, app_with_teacher) -> None:
        app, tid, sid, tag = app_with_teacher
        with app.app_context():
            _insert_seed(tag, sid)
            p0 = db.session.query(Progress).count()
            a0 = db.session.query(AdaptiveLearningLog).count()

        client = app.test_client()
        _login(client, tid)
        client.get("/teacher/b4-chap2-audit?limit=10")
        client.get("/api/teacher/b4-chap2-audit?limit=10")

        with app.app_context():
            assert db.session.query(Progress).count() == p0
            assert db.session.query(AdaptiveLearningLog).count() == a0


class TestAdminMayAccess:
    def test_admin_html_ok(self, app_with_teacher) -> None:
        app, _, sid, tag = app_with_teacher
        with app.app_context():
            admin_u = User(
                username=f"b4_6j_a_{tag}",
                password_hash="x",
                role="admin",
            )
            db.session.add(admin_u)
            db.session.commit()
            aid = admin_u.id
            _insert_seed(tag, sid)

        client = app.test_client()
        _login(client, aid)
        r = client.get("/teacher/b4-chap2-audit")
        assert r.status_code == 200
        assert f"vh_數學B4_6j_det_{tag}" in r.get_data(as_text=True)
