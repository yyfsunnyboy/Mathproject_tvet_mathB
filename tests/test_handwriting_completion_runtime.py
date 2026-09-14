from __future__ import annotations

from pathlib import Path
import uuid

import pytest

from app import create_app
from core.handwriting_ai_check import handwriting_completion_state, normalize_ai_handwriting_result
from models import PracticeAttempt, Progress, SkillInfo, User, db


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
    ("ai_result", "expected_state", "image"),
    [
        ({"mode": "unrecognized", "expression": "", "confidence": 0.99}, "blank", "blank"),
        ({"mode": "final_answer_only", "expression": "x=", "confidence": 0.99}, "in_progress", "data:image/png;base64,ink"),
        ({"mode": "final_answer_only", "expression": "x=13 or", "confidence": 0.99}, "in_progress", "data:image/png;base64,ink"),
        ({"mode": "final_answer_only", "expression": "-13≤x", "confidence": 0.99}, "in_progress", "data:image/png;base64,ink"),
    ],
)
def test_browser_runtime_non_completed_states_do_not_record_attempt(
    runtime_app, monkeypatch, ai_result, expected_state, image
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
        json={"image_data_url": image, "question_uid": uid},
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


def _install_multi_part_question(client, user_id, uid):
    import core.practice_question_store as question_store

    contract = {
        "answer_type": "multi_part",
        "checker": "multi_part_answer_checker",
        "answer_equivalence": "multi_part_answer",
        "parts": [
            {
                "key": "part_1",
                "checker": "expression_checker",
                "equivalence_type": "algebraic_equivalent",
                "expected_answer": "-pi",
                "required_form": "pi_expression",
            },
            {
                "key": "part_2",
                "checker": "integer_checker",
                "equivalence_type": "numeric_exact",
                "expected_answer": "300",
            },
        ],
    }
    payload = {
        "skill": SKILL,
        "skill_id": SKILL,
        "question_uid": uid,
        "question_text": "(1) -180° 化為弧度 (2) 5π/3 化為角度",
        "problem_type_id": "two_way_angle_conversion",
        "presentation_mode": "multi_part",
        "answer_type": "multi_part",
        "answer": {"part_1": "-pi", "part_2": "300"},
        "correct_answer": {"part_1": "-pi", "part_2": "300"},
        "checker": "multi_part_answer_checker",
        "equivalence": "multi_part_answer",
        "answer_contract": contract,
    }
    stored = question_store.slim_payload_for_store(payload, skill_id=SKILL, question_uid=uid)
    question_store._STORE[f"user:{user_id}"] = {uid: stored}
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True
        sess["current_question_uid"] = uid
        sess["current_skill_id"] = SKILL
        sess["practice_ref"] = {"question_uid": uid, "skill_id": SKILL}
    return question_store, contract


def _recognize_handwriting(client, uid, submission_id, image):
    return client.post(
        "/api/practice/ai-check-handwriting",
        json={
            "image_data_url": image,
            "image_base64": image,
            "question_uid": uid,
            "skill_id": SKILL,
            "handwriting_submission_id": submission_id,
            "capture_debug": {
                "captured_at": f"2026-09-14T00:00:0{submission_id[-1]}Z",
                "reused_cache": False,
            },
        },
    ).get_json()


def _install_integer_question(client, user_id, uid):
    import core.practice_question_store as question_store

    contract = {
        "answer_type": "integer",
        "checker": "integer_checker",
        "answer_equivalence": "numeric_exact",
    }
    payload = {
        "skill": SKILL,
        "skill_id": SKILL,
        "question_uid": uid,
        "question_text": "請計算答案。",
        "answer": "14",
        "correct_answer": "14",
        "answer_type": "integer",
        "checker": "integer_checker",
        "equivalence": "numeric_exact",
        "answer_contract": contract,
    }
    stored = question_store.slim_payload_for_store(payload, skill_id=SKILL, question_uid=uid)
    question_store._STORE[f"user:{user_id}"] = {uid: stored}
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True
        sess["current_question_uid"] = uid
        sess["current_skill_id"] = SKILL
        sess["practice_ref"] = {"question_uid": uid, "skill_id": SKILL}


def _grade_handwriting(client, uid, recognition):
    normalized = recognition["normalized_answer"]
    audit = recognition["submission_audit"]
    return client.post(
        "/check_answer",
        json={
            "answer": normalized,
            "answers": normalized,
            "user_answer": normalized,
            "question_uid": uid,
            "skill_id": SKILL,
            "handwriting_submission_id": recognition["handwriting_submission_id"],
            "handwriting_image_sha256": audit["image_sha256"],
        },
    ).get_json()


def test_wrong_37_then_new_submission_14_regrades_and_advances(runtime_app, monkeypatch):
    import core.routes.adaptive_api as adaptive_api

    app, user_id = runtime_app
    client = app.test_client()
    uid = "handwriting-37-then-14"
    _install_integer_question(client, user_id, uid)

    def _fake_vision(payload, _ctx):
        answer = "37" if payload["handwriting_submission_id"] == "submit-37" else "14"
        return {"mode": "final_answer_only", "recognized_answer": answer, "confidence": 0.99}

    monkeypatch.setattr(adaptive_api, "_call_ai_handwriting_checker", _fake_vision)
    wrong = _recognize_handwriting(
        client, uid, "submit-37", "data:image/png;base64,d3JvbmctMzc="
    )
    wrong_grade = _grade_handwriting(client, uid, wrong)
    correct = _recognize_handwriting(
        client, uid, "submit-14", "data:image/png;base64,Y29ycmVjdC0xNA=="
    )
    correct_grade = _grade_handwriting(client, uid, correct)

    assert wrong_grade["checker_input"] == "37"
    assert wrong_grade["correct"] is False
    assert correct_grade["checker_input"] == "14"
    assert correct_grade["correct"] is True
    assert correct_grade.get("duplicate_submission") is not True
    source = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    submit_body = source[
        source.index("async function submitHandwritingAsAnswer"):
        source.index("// === AI 分析 / 手寫正式答案提交 ===")
    ]
    assert "await handleCorrectAnswer()" in submit_body
    assert "showCustomAlert(message, resolve);" in source
    assert "setTimeout(loadQuestion, 500);" in source


def test_wrong_then_correct_handwriting_resubmit_is_fresh(runtime_app, monkeypatch):
    import core.routes.adaptive_api as adaptive_api

    app, user_id = runtime_app
    client = app.test_client()
    uid = "handwriting-resubmit-wrong-correct"
    question_store, _contract = _install_multi_part_question(client, user_id, uid)
    seen_images = []

    def _fake_vision(payload, _ctx):
        seen_images.append(payload["image_data_url"])
        if payload["handwriting_submission_id"] == "submit-1":
            return {
                "mode": "final_answer_only",
                "recognized_answer": "1. 0  2. 0°",
                "confidence": 0.99,
            }
        return {
            "mode": "final_answer_only",
            "recognized_answer": "1. -π  2. 300°",
            "confidence": 0.99,
        }

    monkeypatch.setattr(adaptive_api, "_call_ai_handwriting_checker", _fake_vision)

    first = _recognize_handwriting(client, uid, "submit-1", "data:image/png;base64,Zmlyc3Q=")
    first_grade = _grade_handwriting(client, uid, first)
    assert first["completion_state"] == "completed"
    assert first["recognized_answer"] == "1. 0  2. 0°"
    assert first_grade["checker_result"] == "incorrect"
    assert question_store._STORE[f"user:{user_id}"][uid]["status"] == "answered"
    with client.session_transaction() as sess:
        assert sess["chat_tutor_authoritative_result"]["status"] == "incorrect"

    second = _recognize_handwriting(client, uid, "submit-2", "data:image/png;base64,c2Vjb25k")
    second_grade = _grade_handwriting(client, uid, second)

    assert seen_images == ["data:image/png;base64,Zmlyc3Q=", "data:image/png;base64,c2Vjb25k"]
    assert first["submission_audit"]["image_sha256"] != second["submission_audit"]["image_sha256"]
    assert second["recognized_answer"] == "1. -π  2. 300°"
    assert second["normalized_answer"] == {"part_1": "-π", "part_2": "300°"}
    assert second["submission_audit"]["part_1"] == "-π"
    assert second["submission_audit"]["part_2"] == "300°"
    assert second["submission_audit"]["previous_handwriting_state_reused"] is False
    assert second["submission_audit"]["previous_authoritative_state_cleared"] is True
    assert second["submission_audit"]["structured_analysis_from_current_request"] is True
    assert second["submission_audit"]["tutor_authoritative_result"] is None
    assert second_grade["checker_input"] == {"part_1": "-π", "part_2": "300°"}
    assert second_grade["checker_result"] == "correct"
    assert second_grade["correct"] is True
    assert second_grade.get("duplicate_submission") is not True
    assert question_store._STORE[f"user:{user_id}"][uid]["status"] == "answered"
    with client.session_transaction() as sess:
        assert sess["chat_tutor_authoritative_result"]["status"] == "correct"


@pytest.mark.parametrize(
    ("first_image", "first_result", "expected_first_state"),
    [
        ("blank", None, "blank"),
        (
            "data:image/png;base64,cGFydGlhbA==",
            {"mode": "process_only", "recognized_steps": ["1. -π"], "confidence": 0.99},
            "in_progress",
        ),
    ],
)
def test_blank_or_inprogress_then_correct_handwriting_resubmit_is_fresh(
    runtime_app, monkeypatch, first_image, first_result, expected_first_state
):
    import core.routes.adaptive_api as adaptive_api

    _app, user_id = runtime_app
    client = _app.test_client()
    uid = "handwriting-resubmit-progress-correct"
    _install_multi_part_question(client, user_id, uid)

    def _fake_vision(payload, _ctx):
        if payload["handwriting_submission_id"] == "submit-1" and first_result is not None:
            return first_result
        return {
            "mode": "final_answer_only",
            "recognized_answer": "1. -π  2. 300°",
            "confidence": 0.99,
        }

    monkeypatch.setattr(adaptive_api, "_call_ai_handwriting_checker", _fake_vision)

    first = _recognize_handwriting(client, uid, "submit-1", first_image)
    assert first["completion_state"] == expected_first_state
    assert first["submission_audit"]["checker_result"] is None

    second = _recognize_handwriting(client, uid, "submit-2", "data:image/png;base64,Y29tcGxldGU=")
    second_grade = _grade_handwriting(client, uid, second)
    assert second["completion_state"] == "completed"
    assert second["normalized_answer"] == {"part_1": "-π", "part_2": "300°"}
    assert second["submission_audit"]["previous_handwriting_state_reused"] is False
    assert second_grade["correct"] is True


def test_wrong_then_different_wrong_handwriting_reenters_checker(runtime_app, monkeypatch):
    import core.routes.adaptive_api as adaptive_api

    app, user_id = runtime_app
    client = app.test_client()
    uid = "handwriting-resubmit-two-wrong"
    _install_multi_part_question(client, user_id, uid)
    recognized = {"submit-1": "1. 0  2. 0°", "submit-2": "1. π  2. 180°"}
    calls = []

    def _fake_vision(payload, _ctx):
        submission_id = payload["handwriting_submission_id"]
        calls.append(submission_id)
        return {
            "mode": "final_answer_only",
            "recognized_answer": recognized[submission_id],
            "confidence": 0.99,
        }

    monkeypatch.setattr(adaptive_api, "_call_ai_handwriting_checker", _fake_vision)
    first = _recognize_handwriting(client, uid, "submit-1", "data:image/png;base64,Zmlyc3Q=")
    first_grade = _grade_handwriting(client, uid, first)
    second = _recognize_handwriting(client, uid, "submit-2", "data:image/png;base64,c2Vjb25k")
    second_grade = _grade_handwriting(client, uid, second)

    assert calls == ["submit-1", "submit-2"]
    assert first_grade["correct"] is False
    assert second_grade["correct"] is False
    assert second_grade.get("duplicate_submission") is not True
    assert second_grade["checker_input"] != first_grade["checker_input"]
    with app.app_context():
        assert PracticeAttempt.query.count() == 2
        assert Progress.query.filter_by(user_id=user_id, skill_id=SKILL).one().questions_solved == 2


def test_same_handwriting_submission_double_check_is_safe_replay(runtime_app, monkeypatch):
    import core.routes.adaptive_api as adaptive_api

    app, user_id = runtime_app
    client = app.test_client()
    uid = "handwriting-double-check"
    _install_multi_part_question(client, user_id, uid)
    monkeypatch.setattr(
        adaptive_api,
        "_call_ai_handwriting_checker",
        lambda *_a, **_k: {
            "mode": "final_answer_only",
            "recognized_answer": "1. -π  2. 300°",
            "confidence": 0.99,
        },
    )

    recognition = _recognize_handwriting(
        client, uid, "submit-double", "data:image/png;base64,ZG91Ymxl"
    )
    first_grade = _grade_handwriting(client, uid, recognition)
    second_grade = _grade_handwriting(client, uid, recognition)

    assert first_grade["correct"] is True
    assert first_grade.get("duplicate_submission") is not True
    assert second_grade["correct"] is True
    assert second_grade["duplicate_submission"] is True
    assert second_grade["handwriting_submission_id"] == "submit-double"
    with app.app_context():
        assert PracticeAttempt.query.count() == 1
        assert Progress.query.filter_by(user_id=user_id, skill_id=SKILL).one().questions_solved == 1


def test_standard_frontend_resets_transient_handwriting_state_per_click():
    source = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    start = source.index("async function submitHandwritingAsAnswer")
    end = source.index("// === AI 分析 / 手寫正式答案提交 ===", start)
    body = source[start:end]

    assert "const submission = beginFreshHandwritingSubmission(cq);" in body
    assert body.index("beginFreshHandwritingSubmission(cq)") < body.index("captureHandwritingImageForRecognition()")
    assert "handwriting_submission_id: submission.submissionId" in body
    assert "handwritingPayload.handwriting_image_sha256 = submission.imageSha256" in body
    assert "feedback.handwriting_submission_id !== submission.submissionId" in body
    assert "await handleCorrectAnswer()" in body

    adaptive = (ROOT / "templates" / "adaptive_practice_v2.html").read_text(encoding="utf-8")
    assert "handwritingTransient: null" in adaptive
    assert "handwriting_submission_id: submission.submissionId" in adaptive
    assert "handwriting_image_sha256: submission.imageSha256" in adaptive
