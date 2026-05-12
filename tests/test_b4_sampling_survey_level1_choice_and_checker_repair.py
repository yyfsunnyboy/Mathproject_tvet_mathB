from __future__ import annotations

import uuid
from urllib.parse import quote

import pytest

from app import create_app
from core.vocational_math_b4.services import question_router as chap3_router
from core.vocational_math_b4.services.question_router import generate_for_chap3_skill
from models import User, db


FORBIDDEN_OPEN_ENDED = [
    "請說明",
    "請討論",
    "請簡述",
    "可能有哪些偏誤",
    "是否具有代表性",
    "提出改善方式",
]


def _resolve_skill_id(suffix: str) -> str:
    for key in chap3_router._CHAP3_PHASE7B_REGISTRY.keys():
        if str(key).endswith(suffix):
            return str(key)
    raise AssertionError(f"Missing skill with suffix={suffix}")


@pytest.fixture()
def logged_client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"b4_sampling_survey_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid)
        sess["_fresh"] = True
    return client


def test_level1_no_open_ended_and_deterministic_choice_only() -> None:
    skill_id = _resolve_skill_id("SamplingSurvey")
    payloads = [generate_for_chap3_skill(skill_id=skill_id, level=1, seed=i + 1) for i in range(20)]

    for p in payloads:
        q = str(p.get("question_text", ""))
        for token in FORBIDDEN_OPEN_ENDED:
            assert token not in q
        assert p.get("runtime_mode") == "deterministic_choice"
        assert p.get("check_mode") == "deterministic_auto_checked"
        assert p.get("grading_mode") == "deterministic"
        assert p.get("answer_input_type") == "choice"
        choices = p.get("choices") or []
        assert isinstance(choices, list) and len(choices) >= 4
        codes = {str(c).split(".", 1)[0].strip() for c in choices}
        assert str(p.get("answer", "")).strip() in codes
        assert p.get("problem_type_id")
        assert p.get("scenario_id")


def test_screenshot_question_choice_checker_regression(logged_client) -> None:
    skill_id = _resolve_skill_id("SamplingSurvey")
    found_seed = None
    for s in range(1, 300):
        p = generate_for_chap3_skill(skill_id=skill_id, level=1, seed=s)
        q = str(p.get("question_text", ""))
        if "5000 位機車族" in q and "250 位" in q and "樣本" in q:
            found_seed = s
            break
    assert found_seed is not None, "did not find screenshot-aligned scenario within seed range"

    resp = logged_client.get(
        f"/get_next_question?skill={quote(skill_id)}&problem_type=sampling_survey_foundation_identification&gen_seed={found_seed}&level=1"
    )
    assert resp.status_code == 200
    payload = resp.get_json() or {}
    q = str(payload.get("question", ""))
    assert "5000 位機車族" in q
    assert "250 位" in q
    assert payload.get("answer_input_type") == "choice"
    assert payload.get("check_mode") == "deterministic_auto_checked"

    ok3 = (logged_client.post("/check_answer", json={"answer": "3"}).get_json() or {})
    okC = (logged_client.post("/check_answer", json={"answer": "C"}).get_json() or {})
    okc = (logged_client.post("/check_answer", json={"answer": "c"}).get_json() or {})
    bad1 = (logged_client.post("/check_answer", json={"answer": "1"}).get_json() or {})

    assert ok3.get("correct") is True
    assert okC.get("correct") is True
    assert okc.get("correct") is True
    assert bad1.get("correct") is False

    for item in (ok3, okC, okc, bad1):
        msg = str(item.get("result", ""))
        assert "模組載入錯誤" not in msg
        assert "AI/Review" not in msg


def test_sampling_survey_textbook_boundary_and_diversity() -> None:
    skill_id = _resolve_skill_id("SamplingSurvey")
    payloads = [generate_for_chap3_skill(skill_id=skill_id, level=1, seed=i + 1) for i in range(20)]
    question_texts = [str(p.get("question_text", "")) for p in payloads]
    scenario_ids = [str(p.get("scenario_id", "")) for p in payloads]

    allowed_keywords = ["母群體", "樣本", "母群體數", "樣本數", "普查", "抽查"]
    for q in question_texts:
        assert any(k in q for k in allowed_keywords)

    open_ended_count = sum(1 for q in question_texts if any(t in q for t in FORBIDDEN_OPEN_ENDED))
    deterministic_count = sum(1 for p in payloads if p.get("runtime_mode") == "deterministic_choice")
    consecutive_dup = sum(1 for i in range(1, len(question_texts)) if question_texts[i] == question_texts[i - 1])

    assert open_ended_count == 0
    assert deterministic_count == 20
    assert len(set(question_texts)) >= 8
    assert len(set(scenario_ids)) >= 8
    assert consecutive_dup == 0


def test_review_gating_only_when_explicit_problem_type() -> None:
    skill_id = _resolve_skill_id("SamplingSurvey")
    p = generate_for_chap3_skill(
        skill_id=skill_id,
        level=1,
        seed=1,
        problem_type_id="sampling_survey_bias_review",
    )
    assert p.get("problem_type_id") == "sampling_survey_bias_review"
    assert p.get("check_mode") == "review_mode"
    assert p.get("grading_mode") in {"teacher_review", "ai_assisted_review"}
    assert p.get("expected_answer_schema") or p.get("rubric")
