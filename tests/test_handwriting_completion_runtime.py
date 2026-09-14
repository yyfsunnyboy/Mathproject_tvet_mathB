from __future__ import annotations

from pathlib import Path
import uuid

import pytest

from app import create_app
from core.handwriting_ai_check import handwriting_completion_state, normalize_ai_handwriting_result
from models import PracticeAttempt, SkillInfo, User, db


ROOT = Path(__file__).resolve().parents[1]
SKILL = "test_handwriting_completion_runtime"


@pytest.mark.parametrize(
    "field",
    ["recognized_answer", "answer", "final_answer", "recognized_text", "expression"],
)
def test_normalize_accepts_legacy_and_modern_answer_fields(field):
    normalized = normalize_ai_handwriting_result(
        {field: "x=±13", "mode": "final_answer_only", "confidence": 0.99}
    )
    assert normalized["normalized_answer"] == "x=±13"
    assert handwriting_completion_state(normalized) == "completed"


def test_runtime_question_contract_uses_session_get_current(runtime_app, monkeypatch):
    import core.routes.adaptive_api as adaptive_api
    import core.session as session_mod

    app, user_id = runtime_app
    client = app.test_client()
    uid = "runtime-contract-lookup"
    contract = {
        "answer_type": "solution_set",
        "checker": "solution_set_checker",
        "answer_equivalence": "unordered_set",
    }
    current = _set_question(
        client, user_id, uid=uid, question="|x| = 13", answer="-13, 13", contract=contract
    )
    calls = {"n": 0}
    real_get_current = session_mod.get_current

    def _tracking_get_current():
        calls["n"] += 1
        loaded = real_get_current()
        assert loaded.get("question_uid") == uid
        assert loaded.get("correct_answer") == "-13, 13"
        return loaded

    monkeypatch.setattr(session_mod, "get_current", _tracking_get_current)
    monkeypatch.setattr(
        adaptive_api,
        "_call_ai_handwriting_checker",
        lambda *_a, **_k: {"expression": "x=±13", "mode": "final_answer_only", "confidence": 0.99},
    )

    with client:
        # Ensure Flask request/session context is active for get_current.
        response = client.post(
            "/api/practice/ai-check-handwriting",
            json={"image_data_url": "data:image/png;base64,ink", "question_uid": uid},
        ).get_json()

    assert response["completion_state"] == "completed"
    assert calls["n"] >= 1
    assert current["question_uid"] == uid


@pytest.fixture()
def runtime_app(tmp_path):
    import config as cfg

    previous_uri = cfg.Config.SQLALCHEMY_DATABASE_URI
    cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + (tmp_path / "handwriting-runtime.db").as_posix()
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            user = User(username=f"hw_{uuid.uuid4().hex[:10]}", password_hash="x", role="student")
            db.session.add(user)
            db.session.add(
                SkillInfo(
                    skill_id=SKILL,
                    skill_en_name="Handwriting runtime",
                    skill_ch_name="手寫執行期",
                    description="test",
                    gemini_prompt="test",
                    is_active=True,
                )
            )
            db.session.commit()
            yield app, user.id
    finally:
        cfg.Config.SQLALCHEMY_DATABASE_URI = previous_uri


def _set_question(client, user_id, *, uid, question, answer, contract):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True
        current = {
            "skill": SKILL,
            "skill_id": SKILL,
            "question_uid": uid,
            "question_text": question,
            "correct_answer": answer,
            "answer": answer,
            "answer_type": contract["answer_type"],
            "checker": contract["checker"],
            "equivalence": contract["answer_equivalence"],
            "answer_contract": contract,
        }
        sess["current_data"] = current
        sess["current_question_uid"] = uid
        sess["current_skill_id"] = SKILL
    return current


@pytest.mark.parametrize(
    ("uid", "question", "recognized", "answer", "contract"),
    [
        (
            "runtime-pm-13",
            "|x| = 13",
            "x = ±13",
            "-13, 13",
            {
                "answer_type": "solution_set",
                "checker": "solution_set_checker",
                "answer_equivalence": "unordered_set",
            },
        ),
        (
            "runtime-chain-14",
            "|x| ≤ 14",
            "-14 ≤ x ≤ 14",
            "-14 <= x <= 14",
            {
                "answer_type": "inequality",
                "checker": "inequality_checker",
                "answer_equivalence": "inequality_solution_set",
            },
        ),
    ],
)
def test_browser_runtime_completed_answer_reaches_shared_checker(
    runtime_app, monkeypatch, uid, question, recognized, answer, contract
):
    import core.routes.adaptive_api as adaptive_api
    import core.routes.practice as practice

    app, user_id = runtime_app
    client = app.test_client()
    current = _set_question(client, user_id, uid=uid, question=question, answer=answer, contract=contract)
    monkeypatch.setattr(practice, "resolve_check_context", lambda _body: (current, None))
    # Exercise the legacy runtime response shape that caused the production bug.
    monkeypatch.setattr(
        adaptive_api,
        "_call_ai_handwriting_checker",
        lambda *_args, **_kwargs: {
            "expression": recognized,
            "mode": "final_answer_only",
            "confidence": 0.99,
        },
    )

    recognition = client.post(
        "/api/practice/ai-check-handwriting",
        json={"image_data_url": "data:image/png;base64,ink", "question_uid": uid},
    ).get_json()
    assert recognition["completion_state"] == "completed"
    assert recognition["normalized_answer"] == recognized

    grade = client.post(
        "/check_answer",
        json={"answer": recognition["normalized_answer"], "question_uid": uid, "skill_id": SKILL},
    ).get_json()
    assert grade["correct"] is True

    source = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    start = source.index("async function submitHandwritingAsAnswer")
    end = source.index("// === AI 分析 / 手寫正式答案提交 ===", start)
    body = source[start:end]
    assert body.index("completion_state === 'in_progress'") < body.index("/check_answer")
    assert body.index("if (grade.correct === true)") < body.index("await handleCorrectAnswer()")


@pytest.mark.parametrize(
    ("ai_result", "expected_state"),
    [
        ({"mode": "unrecognized", "expression": "", "confidence": 0.99}, "blank"),
        ({"mode": "final_answer_only", "expression": "x=", "confidence": 0.99}, "in_progress"),
        ({"mode": "final_answer_only", "expression": "x=13 or", "confidence": 0.99}, "in_progress"),
        ({"mode": "final_answer_only", "expression": "-13≤x", "confidence": 0.99}, "in_progress"),
    ],
)
def test_browser_runtime_non_completed_states_do_not_record_attempt(
    runtime_app, monkeypatch, ai_result, expected_state
):
    import core.routes.adaptive_api as adaptive_api

    app, user_id = runtime_app
    client = app.test_client()
    uid = f"runtime-{expected_state}-{uuid.uuid4().hex[:6]}"
    contract = {
        "answer_type": "solution_set",
        "checker": "solution_set_checker",
        "answer_equivalence": "unordered_set",
    }
    _set_question(client, user_id, uid=uid, question="|x| = 13", answer="-13, 13", contract=contract)
    monkeypatch.setattr(adaptive_api, "_call_ai_handwriting_checker", lambda *_a, **_k: ai_result)

    response = client.post(
        "/api/practice/ai-check-handwriting",
        json={"image_data_url": "data:image/png;base64,ink", "question_uid": uid},
    ).get_json()
    assert response["completion_state"] == expected_state
    with app.app_context():
        assert PracticeAttempt.query.count() == 0


def test_browser_runtime_completed_wrong_answer_records_incorrect(runtime_app, monkeypatch):
    import core.routes.adaptive_api as adaptive_api
    import core.routes.practice as practice

    app, user_id = runtime_app
    client = app.test_client()
    uid = "runtime-wrong-completed"
    contract = {
        "answer_type": "solution_set",
        "checker": "solution_set_checker",
        "answer_equivalence": "unordered_set",
    }
    current = _set_question(client, user_id, uid=uid, question="|x| = 13", answer="-13, 13", contract=contract)
    monkeypatch.setattr(practice, "resolve_check_context", lambda _body: (current, None))
    monkeypatch.setattr(
        adaptive_api,
        "_call_ai_handwriting_checker",
        lambda *_a, **_k: {
            "expression": "x=±12",
            "mode": "final_answer_only",
            "feedback": "把 12 代回原式後，絕對值會等於 13 嗎？",
            "confidence": 0.99,
        },
    )

    recognition = client.post(
        "/api/practice/ai-check-handwriting",
        json={"image_data_url": "data:image/png;base64,ink", "question_uid": uid},
    ).get_json()
    assert recognition["completion_state"] == "completed"
    assert recognition["feedback"].endswith("？")
    grade = client.post(
        "/check_answer",
        json={"answer": recognition["normalized_answer"], "question_uid": uid, "skill_id": SKILL},
    ).get_json()
    assert grade["correct"] is False
    with app.app_context():
        attempt = PracticeAttempt.query.one()
        assert attempt.is_correct is False
