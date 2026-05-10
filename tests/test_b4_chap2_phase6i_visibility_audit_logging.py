# -*- coding: utf-8 -*-
"""Phase 6I: Chap2 deterministic visibility audit logging (DB, no extra mastery hooks)."""

from __future__ import annotations

import uuid

import pytest

from app import create_app
from models import (
    User,
    db,
    B4Chap2VisibilityAuditLog,
    Progress,
    AdaptiveLearningLog,
)
from core.routes.practice import (
    B4_CHAP2_RESERVED_PROBLEM_TYPE_PUBLIC_ERROR,
)
from core.vocational_math_b4.services.b4_chap2_visibility_audit import (
    B4_CHAP2_VISIBILITY_SOURCE_PHASE,
)


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


@pytest.fixture()
def logged_client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"b4_6i_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    _login(client, uid)
    return client, uid


def _latest_audit() -> B4Chap2VisibilityAuditLog | None:
    return (
        db.session.query(B4Chap2VisibilityAuditLog)
        .order_by(B4Chap2VisibilityAuditLog.id.desc())
        .first()
    )


class TestChap2AnswerAuditRows:
    def test_deterministic_correct_and_incorrect_logged(self, logged_client) -> None:
        from core.vocational_math_b4.services.question_router import generate_for_chap2_skill

        client, uid = logged_client
        seed = 42
        p = generate_for_chap2_skill(
            skill_id="vh_數學B4_ProbabilityDefinition",
            problem_type_id="classical_probability_fraction",
            level=1,
            seed=seed,
        )
        ca = str(p["correct_answer"])

        rq = client.get(
            "/get_next_question?skill=vh_數學B4_ProbabilityDefinition"
            f"&problem_type=classical_probability_fraction&gen_seed={seed}&level=1"
        )
        assert rq.status_code == 200

        with client.application.app_context():
            n_before = db.session.query(B4Chap2VisibilityAuditLog).count()

        ok = client.post("/check_answer", json={"answer": ca})
        assert ok.get_json().get("correct") is True
        with client.application.app_context():
            assert db.session.query(B4Chap2VisibilityAuditLog).count() == n_before + 1
            row = _latest_audit()
            assert row is not None
            assert row.record_kind == "deterministic_answer"
            assert row.student_id == uid
            assert row.skill_id == "vh_數學B4_ProbabilityDefinition"
            assert row.problem_type_id == "classical_probability_fraction"
            assert row.answer_type == "rational_fraction"
            assert row.checker_name == "check_rational_answer"
            assert row.is_correct is True
            assert row.source_phase == B4_CHAP2_VISIBILITY_SOURCE_PHASE
            assert row.gated_event_type is None

        client.get(
            "/get_next_question?skill=vh_數學B4_ProbabilityDefinition"
            f"&problem_type=classical_probability_fraction&gen_seed={seed}&level=1"
        )
        bad = client.post("/check_answer", json={"answer": "999/999"})
        assert bad.get_json().get("correct") is False
        with client.application.app_context():
            row2 = _latest_audit()
            assert row2.is_correct is False


class TestGatedAuditRows:
    def test_not_enabled_skill_logged(self, logged_client) -> None:
        # Phase 6K closure: BasicConceptsOfSets is now enabled via deterministic
        # generator; the not-enabled gated audit path is no longer triggered for
        # this skill. Assert the inverted state: route returns 200 with NO new
        # gated `not_enabled_skill` row, and progress / APR remain untouched
        # (visibility-only mode preserved).
        client, uid = logged_client
        with client.application.app_context():
            gated_n0 = (
                db.session.query(B4Chap2VisibilityAuditLog)
                .filter_by(record_kind="gated", gated_event_type="not_enabled_skill")
                .count()
            )
            prog_n0 = db.session.query(Progress).filter_by(user_id=uid).count()
            apr_n0 = db.session.query(AdaptiveLearningLog).filter_by(student_id=uid).count()

        r = client.get(
            "/get_next_question?skill=vh_數學B4_BasicConceptsOfSets&gen_seed=29&level=1"
        )
        assert r.status_code == 200, r.get_data(as_text=True)
        body = r.get_json() or {}
        assert body.get("new_question_text")

        with client.application.app_context():
            assert (
                db.session.query(B4Chap2VisibilityAuditLog)
                .filter_by(record_kind="gated", gated_event_type="not_enabled_skill")
                .count()
                == gated_n0
            )
            assert db.session.query(Progress).filter_by(user_id=uid).count() == prog_n0
            assert (
                db.session.query(AdaptiveLearningLog)
                .filter_by(student_id=uid)
                .count()
                == apr_n0
            )

    def test_reserved_listing_logged(self, logged_client) -> None:
        client, uid = logged_client
        with client.application.app_context():
            n0 = db.session.query(B4Chap2VisibilityAuditLog).count()
        r = client.get(
            "/get_next_question?skill=vh_數學B4_SampleSpaceAndEvents"
            "&problem_type=sample_space_listing&level=1"
        )
        assert r.status_code == 422
        assert r.get_json().get("error") == B4_CHAP2_RESERVED_PROBLEM_TYPE_PUBLIC_ERROR
        with client.application.app_context():
            assert db.session.query(B4Chap2VisibilityAuditLog).count() == n0 + 1
            row = _latest_audit()
            assert row.record_kind == "gated"
            assert row.gated_event_type == "reserved_problem_type"
            assert row.problem_type_id == "sample_space_listing"
            assert row.is_correct is None


class TestRegression:
    def test_chap1_allowlist_size(self) -> None:
        from core.vocational_math_b4.adaptive.b4_chapter1_deterministic_allowlist import (
            B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST,
        )

        assert len(B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST) == 13
