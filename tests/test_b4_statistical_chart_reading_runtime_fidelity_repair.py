from __future__ import annotations

import uuid
from urllib.parse import quote

import pytest

from app import create_app
from models import User, db
from core.vocational_math_b4.services import question_router as chap3_router
from core.vocational_math_b4.services.question_router import generate_for_chap3_skill


SKILL_ID = next(k for k in chap3_router._CHAP3_PHASE7B_REGISTRY.keys() if str(k).endswith("StatisticalChartReading"))
PT_REVIEW = "statistical_chart_reading_visibility_review"
PTS_CHOICE = {
    "chart_type_by_purpose",
    "chart_interpretation_caution",
    "chart_match_data_type",
}


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
            username=f"b4_stat_chart_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    _login(client, uid)
    return client


def _contains_visual_trigger(text: str) -> bool:
    return any(token in text for token in ["??", "??", "???", "??"])


def _assert_choice_contract(payload: dict) -> None:
    assert payload.get("runtime_mode") == "deterministic_choice"
    assert payload.get("check_mode") == "deterministic_auto_checked"
    assert payload.get("grading_mode") == "deterministic"
    assert payload.get("answer_input_type") == "choice"
    choices = payload.get("choices") or []
    assert isinstance(choices, list) and len(choices) >= 4
    codes = {str(c).split(".", 1)[0].strip() for c in choices}
    assert str(payload.get("answer")) in codes


def test_no_missing_visual_for_visual_wording() -> None:
    payload = generate_for_chap3_skill(skill_id=SKILL_ID, problem_type_id=PT_REVIEW, seed=7, level=1)
    q = str(payload.get("question_text", ""))
    if _contains_visual_trigger(q):
        assert payload.get("image_base64") or payload.get("visual_aids") or payload.get("chart_spec")


def test_deterministic_choice_availability() -> None:
    seen_choice = []
    for seed in range(1, 25):
        payload = generate_for_chap3_skill(skill_id=SKILL_ID, seed=seed, level=1)
        if payload.get("runtime_mode") == "deterministic_choice":
            seen_choice.append(payload)
    assert seen_choice
    _assert_choice_contract(seen_choice[0])


def test_scenario_diversity() -> None:
    families = set()
    patterns = set()
    for seed in range(1, 35):
        p = generate_for_chap3_skill(skill_id=SKILL_ID, seed=seed, level=1)
        families.add(str(p.get("scenario_family") or p.get("scenario_id") or ""))
        patterns.add(str(p.get("problem_type_id") or ""))
        assert "??????????????????????????????????????????" != str(p.get("question_text", "")).strip() or p.get("problem_type_id") == PT_REVIEW
    assert len({x for x in families if x}) >= 2 or len({x for x in patterns if x}) >= 2


def test_choice_contract_and_check_answer(logged_client) -> None:
    payload = generate_for_chap3_skill(skill_id=SKILL_ID, problem_type_id="chart_type_by_purpose", seed=5, level=1)
    _assert_choice_contract(payload)

    q = logged_client.get(f"/get_next_question?skill={quote(SKILL_ID)}&problem_type=chart_type_by_purpose&gen_seed=5&level=1")
    assert q.status_code == 200
    d = q.get_json() or {}
    ans = str(payload.get("answer"))
    ok = logged_client.post("/check_answer", json={"answer": ans}).get_json() or {}
    assert ok.get("correct") is True

    alpha = chr(ord("A") + int(ans) - 1)
    ok_alpha = logged_client.post("/check_answer", json={"answer": alpha}).get_json() or {}
    assert ok_alpha.get("correct") is True

    wrong = "4" if ans != "4" else "3"
    bad = logged_client.post("/check_answer", json={"answer": wrong}).get_json() or {}
    assert bad.get("correct") is False


def test_review_path_safety_guard(logged_client) -> None:
    p = generate_for_chap3_skill(skill_id=SKILL_ID, problem_type_id=PT_REVIEW, seed=3, level=1)
    assert p.get("check_mode") in {"review_mode", "visual_ai_checked"}
    assert p.get("expected_answer_schema") or p.get("rubric")
    if _contains_visual_trigger(str(p.get("question_text", ""))):
        assert p.get("visual_aids") or p.get("image_base64") or p.get("chart_spec")

    q = logged_client.get(f"/get_next_question?skill={quote(SKILL_ID)}&problem_type={PT_REVIEW}&gen_seed=3&level=1")
    assert q.status_code == 200
    guard = logged_client.post("/check_answer", json={"answer": "????"}).get_json() or {}
    assert guard.get("correct") is False
    assert "AI/Review" in str(guard.get("result", ""))


def test_localization_chinese_payload() -> None:
    for pt in ["chart_type_by_purpose", "chart_interpretation_caution", "chart_match_data_type", PT_REVIEW]:
        p = generate_for_chap3_skill(skill_id=SKILL_ID, problem_type_id=pt, seed=9, level=1)
        blob = " ".join(
            [
                str(p.get("question_text", "")),
                str(p.get("explanation", "")),
                str(p.get("message", "")),
                " ".join(str(x) for x in (p.get("choices") or [])),
            ]
        )
        assert "Please" not in blob
        assert "Choose" not in blob
        assert "Question" not in blob
