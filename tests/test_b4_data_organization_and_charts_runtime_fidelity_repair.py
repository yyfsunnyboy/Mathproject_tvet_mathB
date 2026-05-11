from __future__ import annotations

import uuid
from urllib.parse import quote

import pytest

from app import create_app
from models import User, db
from core.vocational_math_b4.services import question_router as chap3_router
from core.vocational_math_b4.services.question_router import generate_for_chap3_skill


SKILL_ID = next(
    k for k in chap3_router._CHAP3_PHASE7B_REGISTRY.keys() if str(k).endswith("DataOrganizationAndCharts")
)
PT_CHART = "chart_type_selection_by_purpose"
PT_ORG = "data_organization_first_step"
PT_REVIEW = "data_organization_chart_selection_review"
FORBIDDEN_OPEN_ENDED = "?????????????????????????????????"


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
            username=f"b4_data_org_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    _login(client, uid)
    return client


def _assert_choice_payload_contract(payload: dict) -> None:
    assert payload.get("runtime_mode") == "deterministic_choice"
    assert payload.get("check_mode") == "deterministic_auto_checked"
    assert payload.get("grading_mode") == "deterministic"
    assert payload.get("answer_input_type") == "choice"
    choices = payload.get("choices") or []
    assert isinstance(choices, list)
    assert len(choices) >= 4
    assert str(payload.get("answer")) in {str(c).split(".", 1)[0].strip() for c in choices}
    for key in [
        "skill_id",
        "problem_type_id",
        "runtime_mode",
        "check_mode",
        "grading_mode",
        "answer_input_type",
        "choices",
        "answer",
        "explanation",
    ]:
        assert payload.get(key) is not None
    assert payload.get("scenario_family") or payload.get("scenario_id")
    assert payload.get("textbook_alignment_note") or payload.get("source_style_summary")


def test_deterministic_choice_metadata() -> None:
    for pt in (PT_CHART, PT_ORG):
        payload = generate_for_chap3_skill(skill_id=SKILL_ID, problem_type_id=pt, seed=11, level=1)
        _assert_choice_payload_contract(payload)

    payload_review = generate_for_chap3_skill(skill_id=SKILL_ID, problem_type_id=PT_REVIEW, seed=11, level=1)
    assert payload_review.get("runtime_mode") == "teacher_review"


def test_choices_rendering_contract_from_route(logged_client) -> None:
    resp = logged_client.get(f"/get_next_question?skill={quote(SKILL_ID)}&problem_type={PT_CHART}&gen_seed=9&level=1")
    assert resp.status_code == 200
    data = resp.get_json() or {}
    assert data.get("choices") or data.get("choices_display")
    q = str(data.get("new_question_text", ""))
    if "????" in q:
        assert data.get("choices")


def test_chart_type_selection_fidelity_coverage() -> None:
    seen = set()
    for seed in range(1, 40):
        payload = generate_for_chap3_skill(skill_id=SKILL_ID, problem_type_id=PT_CHART, seed=seed, level=1)
        _assert_choice_payload_contract(payload)
        sid = str(payload.get("scenario_id", ""))
        if sid.startswith("trend_"):
            seen.add("trend")
        if sid.startswith("category_comparison_"):
            seen.add("compare")
        if sid.startswith("proportion_"):
            seen.add("ratio")
        if sid.startswith("distribution_"):
            seen.add("distribution")
    assert len(seen) >= 2


def test_check_answer_correct_and_wrong(logged_client) -> None:
    expected = generate_for_chap3_skill(skill_id=SKILL_ID, problem_type_id=PT_CHART, seed=5, level=1)
    ans = str(expected.get("answer", "1"))
    q = logged_client.get(f"/get_next_question?skill={quote(SKILL_ID)}&problem_type={PT_CHART}&gen_seed=5&level=1")
    assert q.status_code == 200
    ok = logged_client.post("/check_answer", json={"answer": ans}).get_json() or {}
    assert ok.get("correct") is True

    alias = chr(ord("A") + int(ans) - 1)
    ok_alias = logged_client.post("/check_answer", json={"answer": alias}).get_json() or {}
    assert ok_alias.get("correct") is True

    wrong = "4" if ans != "4" else "3"
    bad = logged_client.post("/check_answer", json={"answer": wrong}).get_json() or {}
    assert bad.get("correct") is False
    assert "AI/Review" not in str(bad.get("result", ""))


def test_no_open_ended_only_and_review_still_possible() -> None:
    payload_choice = generate_for_chap3_skill(skill_id=SKILL_ID, problem_type_id=PT_ORG, seed=3, level=1)
    assert FORBIDDEN_OPEN_ENDED not in str(payload_choice.get("question_text", ""))

    payload_review = generate_for_chap3_skill(skill_id=SKILL_ID, problem_type_id=PT_REVIEW, seed=3, level=1)
    assert payload_review.get("runtime_mode") == "teacher_review"


def test_router_can_emit_multiple_question_patterns_without_problem_type() -> None:
    families = set()
    pts = set()
    for seed in range(1, 30):
        payload = generate_for_chap3_skill(skill_id=SKILL_ID, seed=seed, level=1)
        families.add(str(payload.get("scenario_family") or payload.get("scenario_id") or ""))
        pts.add(str(payload.get("problem_type_id") or ""))
    assert len({x for x in families if x}) >= 2
    assert len({x for x in pts if x}) >= 2
