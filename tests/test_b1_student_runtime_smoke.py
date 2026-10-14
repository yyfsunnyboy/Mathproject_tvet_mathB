from __future__ import annotations

import uuid
import json
from pathlib import Path
from urllib.parse import quote

import pytest
from werkzeug.security import generate_password_hash


SKILL_ID = "vh_數學B1_PolynomialArithmeticOperations"


def _published_skill_ids() -> list[str]:
    root = Path(__file__).resolve().parents[1]
    result: list[str] = []
    for manifest_path in sorted((root / "agent_skills_v3").glob("vh_數學B1_*/component_manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        if manifest.get("publish_status") == "production_manifest_compiled":
            result.append(str(manifest["skill_id"]))
    return result


PUBLISHED_SKILLS = _published_skill_ids()


@pytest.fixture()
def b1_student_app():
    import config as _cfg

    db_path = Path("reports") / f"pytest_b1_student_smoke_{uuid.uuid4().hex[:8]}.db"
    previous_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + db_path.resolve().as_posix()
    try:
        from app import create_app
        from models import SkillCurriculum, SkillInfo, User, db

        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            for index, skill_id in enumerate(PUBLISHED_SKILLS, start=1):
                db.session.add(
                    SkillInfo(
                        skill_id=skill_id,
                        skill_en_name=skill_id.removeprefix("vh_數學B1_"),
                        skill_ch_name="B1 已上線技能",
                        description="B1 full production runtime smoke",
                        gemini_prompt="published runtime",
                        is_active=True,
                    )
                )
                db.session.add(
                    SkillCurriculum(
                        skill_id=skill_id,
                        curriculum="vocational",
                        grade=10,
                        volume="數學B1",
                        chapter="B1 production",
                        section=f"online-{index}",
                        display_order=index,
                    )
                )
            username = f"b1_smoke_{uuid.uuid4().hex[:8]}"
            password = "test-password"
            db.session.add(
                User(
                    username=username,
                    password_hash=generate_password_hash(password, method="pbkdf2:sha256"),
                    role="student",
                    curriculum_code="vocational",
                )
            )
            db.session.commit()
        yield app, username, password
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = previous_uri
        for candidate in (db_path, Path(str(db_path) + "-wal"), Path(str(db_path) + "-shm")):
            try:
                candidate.unlink(missing_ok=True)
            except OSError:
                pass


def test_b1_student_login_generate_submit_feedback_and_next_question(b1_student_app) -> None:
    app, username, password = b1_student_app
    client = app.test_client()

    login = client.post(
        "/login",
        data={"username": username, "password": password, "role": "student"},
    )
    assert login.status_code == 302
    assert login.headers["Location"].endswith("/dashboard")
    assert client.get("/dashboard").status_code == 200

    practice = client.get(f"/practice/{quote(SKILL_ID)}")
    assert practice.status_code == 200
    practice_html = practice.get_data(as_text=True)
    assert "MathJax-script" in practice_html
    assert "math_display_normalizer.js" in practice_html

    first_response = client.get(
        f"/get_next_question?skill={quote(SKILL_ID)}&level=1&gen_seed=7"
    )
    assert first_response.status_code == 200
    first = first_response.get_json() or {}
    assert first.get("wrapper_loaded") is True
    assert first.get("legacy_fallback_used") is False
    assert first.get("question_uid")
    assert first.get("correct_answer") not in (None, "")

    correct = client.post(
        "/check_answer",
        json={
            "skill_id": SKILL_ID,
            "question_uid": first["question_uid"],
            "answer": first["correct_answer"],
        },
    ).get_json() or {}
    assert correct.get("correct") is True
    assert correct.get("result")

    second = client.get(
        f"/get_next_question?skill={quote(SKILL_ID)}&level=1&gen_seed=8"
    ).get_json() or {}
    assert second.get("question_uid")
    assert second["question_uid"] != first["question_uid"]
    wrong = client.post(
        "/check_answer",
        json={
            "skill_id": SKILL_ID,
            "question_uid": second["question_uid"],
            "answer": "__definitely_wrong__",
        },
    ).get_json() or {}
    assert wrong.get("correct") is False
    assert wrong.get("result")
    assert wrong.get("correct_answer_display")

    third = client.get(
        f"/get_next_question?skill={quote(SKILL_ID)}&level=1&gen_seed=9"
    ).get_json() or {}
    assert third.get("question_uid")
    assert third["question_uid"] != second["question_uid"]
    assert third.get("legacy_fallback_used") is False


def _wrong_answer(question: dict):
    contract = question.get("answer_contract") or {}
    answer_type = str(contract.get("answer_type") or question.get("answer_type") or "")
    correct = question.get("correct_answer", question.get("answer"))
    if "choice" in answer_type:
        return "A" if str(correct) != "A" else "B"
    if answer_type == "multi_part" or contract.get("parts"):
        return {str(part.get("key")): "__wrong__" for part in contract.get("parts") or []}
    if str(correct).strip() == "0":
        return "1"
    if str(correct).strip() == "否":
        return "是"
    return "0"


def test_every_b1_online_skill_http_checker_feedback_and_next_question(b1_student_app) -> None:
    app, username, password = b1_student_app
    client = app.test_client()
    login = client.post(
        "/login",
        data={"username": username, "password": password, "role": "student"},
    )
    assert login.status_code == 302

    for index, skill_id in enumerate(PUBLISHED_SKILLS, start=1):
        assert client.get(f"/practice/{quote(skill_id)}").status_code == 200
        first_response = client.get(
            f"/get_next_question?skill={quote(skill_id)}&level=1&gen_seed={index * 101}"
        )
        assert first_response.status_code == 200
        first = first_response.get_json() or {}
        assert first.get("wrapper_loaded") is True
        assert first.get("legacy_fallback_used") is False
        assert first.get("answer_contract")
        assert str((first.get("answer_contract") or {}).get("answer_type")) != "drawing"

        wrong_response = client.post(
            "/check_answer",
            json={
                "skill_id": skill_id,
                "question_uid": first["question_uid"],
                "answer": _wrong_answer(first),
            },
        )
        assert wrong_response.status_code == 200
        wrong = wrong_response.get_json() or {}
        assert wrong.get("correct") is False
        assert wrong.get("correct_answer_display")

        second = client.get(
            f"/get_next_question?skill={quote(skill_id)}&level=1&gen_seed={index * 101 + 1}"
        ).get_json() or {}
        assert second.get("question_uid") != first.get("question_uid")
        correct_response = client.post(
            "/check_answer",
            json={
                "skill_id": skill_id,
                "question_uid": second["question_uid"],
                "answer": second.get("correct_answer", second.get("answer")),
            },
        )
        assert correct_response.status_code == 200
        assert (correct_response.get_json() or {}).get("correct") is True

        third = client.get(
            f"/get_next_question?skill={quote(skill_id)}&level=1&gen_seed={index * 101 + 2}"
        ).get_json() or {}
        assert third.get("question_uid") != second.get("question_uid")
        assert third.get("legacy_fallback_used") is False

    from models import Progress

    with app.app_context():
        progress = {row.skill_id: row.questions_solved for row in Progress.query.all()}
    assert all(progress.get(skill_id, 0) >= 1 for skill_id in PUBLISHED_SKILLS)
